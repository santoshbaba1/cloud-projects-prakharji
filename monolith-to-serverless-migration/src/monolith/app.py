"""Bookstore monolith — the "before" architecture.

One Flask process serves the whole application: it lists books, accepts orders,
and keeps everything in a single SQLite file on the same box. This is the system
you will strangle, route by route, into serverless functions.

Run locally:
    cd src/monolith
    pip install flask==3.1.0
    python app.py
    # http://localhost:5000/books
"""

import os
import sqlite3
import uuid

from flask import Flask, jsonify, request

DB_PATH = os.environ.get("DB_PATH", "bookstore.db")
APP_VERSION = os.environ.get("APP_VERSION", "monolith-1.0")

app = Flask(__name__)


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS books (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            book_id TEXT NOT NULL,
            qty INTEGER NOT NULL,
            status TEXT NOT NULL
        );
        """
    )
    if conn.execute("SELECT COUNT(*) AS n FROM books").fetchone()["n"] == 0:
        seed = [
            (str(uuid.uuid4()), "The Pragmatic Programmer", "Hunt & Thomas", 39.99),
            (str(uuid.uuid4()), "Designing Data-Intensive Applications", "Kleppmann", 44.99),
            (str(uuid.uuid4()), "Release It!", "Nygard", 34.99),
        ]
        conn.executemany("INSERT INTO books VALUES (?,?,?,?)", seed)
    conn.commit()
    conn.close()


@app.get("/health")
def health():
    return jsonify(status="ok", version=APP_VERSION)


# ---- Catalog domain (later: bookstore-catalog Lambda) ----
@app.get("/books")
def list_books():
    rows = db().execute("SELECT * FROM books").fetchall()
    return jsonify(version=APP_VERSION, books=[dict(r) for r in rows])


@app.get("/books/<book_id>")
def get_book(book_id):
    row = db().execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
    if not row:
        return jsonify(error="not found"), 404
    return jsonify(dict(row))


# ---- Orders domain (later: bookstore-orders Lambda) ----
@app.post("/orders")
def create_order():
    body = request.get_json(force=True)
    book = db().execute("SELECT * FROM books WHERE id=?", (body["book_id"],)).fetchone()
    if not book:
        return jsonify(error="unknown book_id"), 400
    order_id = str(uuid.uuid4())
    conn = db()
    conn.execute(
        "INSERT INTO orders VALUES (?,?,?,?)",
        (order_id, body["book_id"], int(body.get("qty", 1)), "PLACED"),
    )
    conn.commit()
    conn.close()
    return jsonify(id=order_id, status="PLACED"), 201


@app.get("/orders/<order_id>")
def get_order(order_id):
    row = db().execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if not row:
        return jsonify(error="not found"), 404
    return jsonify(dict(row))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
