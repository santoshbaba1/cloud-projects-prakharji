"""api service — owns the notes data and all three kinds of Docker storage.

It lives ONLY on the internal `backend` network: never published to the host,
and (because that network is `internal`) it has no route to the internet. Its
storage is deliberately split three ways to show what each Docker mount type is
for:

  /data   named volume  -> the SQLite database; PERSISTS across container removal
  /config bind mount ro -> host-managed config; edit it on the host, not here
  /cache  tmpfs         -> scratch marker; EPHEMERAL, gone when the container stops
"""

import json
import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, jsonify, request

DATA_DIR = os.environ.get("DATA_DIR", "/data")
CONFIG_PATH = os.environ.get("CONFIG_PATH", "/config/app.json")
CACHE_DIR = os.environ.get("CACHE_DIR", "/cache")
DB_PATH = os.path.join(DATA_DIR, "notes.db")

app = Flask(__name__)


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = db()
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS notes ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "body TEXT NOT NULL, "
            "created_at TEXT NOT NULL)"
        )
        conn.commit()
    finally:
        conn.close()


def load_config():
    try:
        with open(CONFIG_PATH) as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {"title": "Notes", "banner": "(default config — no bind mount found)"}


@app.get("/health")
def health():
    return jsonify(status="ok", service="api", db=DB_PATH)


@app.get("/config")
def config():
    return jsonify(load_config())


@app.get("/notes")
def list_notes():
    conn = db()
    try:
        rows = conn.execute("SELECT id, body, created_at FROM notes ORDER BY id").fetchall()
    finally:
        conn.close()
    return jsonify(notes=[dict(r) for r in rows])


@app.post("/notes")
def add_note():
    body = (request.get_json(force=True) or {}).get("body", "").strip()
    if not body:
        return jsonify(error="body is required"), 400
    now = datetime.now(timezone.utc).isoformat()
    conn = db()
    try:
        cur = conn.execute(
            "INSERT INTO notes (body, created_at) VALUES (?, ?)", (body, now)
        )
        conn.commit()
        note_id = cur.lastrowid
    finally:
        conn.close()
    _touch_cache(now)
    return jsonify(id=note_id, body=body, created_at=now), 201


def _touch_cache(value):
    """Write a marker to the tmpfs so a later /cache read can prove it's ephemeral."""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(os.path.join(CACHE_DIR, "last_write.txt"), "w") as fh:
            fh.write(value)
    except OSError:
        pass


@app.get("/cache")
def cache():
    path = os.path.join(CACHE_DIR, "last_write.txt")
    try:
        with open(path) as fh:
            return jsonify(cache_dir=CACHE_DIR, last_write=fh.read())
    except OSError:
        return jsonify(cache_dir=CACHE_DIR, last_write=None)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
