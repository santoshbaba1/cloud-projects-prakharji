"""edge service — the public gateway and the ONLY host-facing container.

It stores nothing. It sits on BOTH networks: `frontend` (published to your host)
and `backend` (so it can reach the api). Every request is proxied to the api by
name (http://api:5000). Because the api is only on the internal `backend`
network, this service is the single, deliberate front door — you cannot reach
the api from the host at all.
"""

import os

import requests
from flask import Flask, jsonify, request

API_URL = os.environ.get("API_URL", "http://api:5000")
app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok", service="edge", api_url=API_URL)


@app.get("/")
def home():
    try:
        cfg = requests.get(f"{API_URL}/config", timeout=3).json()
        notes = requests.get(f"{API_URL}/notes", timeout=3).json().get("notes", [])
    except requests.RequestException as exc:
        return jsonify(error="api unreachable", api_url=API_URL, detail=str(exc)), 503
    items = "".join(
        f"<li>#{n['id']} {n['body']} <small>{n['created_at']}</small></li>" for n in notes
    )
    return (
        f"<h1>{cfg.get('title', 'Notes')}</h1>"
        f"<p>{cfg.get('banner', '')}</p>"
        "<form method='post' action='/notes'>"
        "<input name='body' placeholder='new note'><button>add</button></form>"
        f"<ul>{items or '<li>(no notes yet)</li>'}</ul>"
    )


@app.post("/notes")
def add_note():
    body = request.form.get("body") if request.form else None
    payload = {"body": body} if body is not None else request.get_json(force=True)
    try:
        r = requests.post(f"{API_URL}/notes", json=payload, timeout=3)
    except requests.RequestException as exc:
        return jsonify(error="api unreachable", detail=str(exc)), 503
    if request.form:
        return "", 303, {"Location": "/"}
    return r.json(), r.status_code


@app.get("/notes")
def list_notes():
    try:
        r = requests.get(f"{API_URL}/notes", timeout=3)
    except requests.RequestException as exc:
        return jsonify(error="api unreachable", detail=str(exc)), 503
    return r.json(), r.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
