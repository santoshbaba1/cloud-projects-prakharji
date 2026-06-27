"""Shop monolith — the "before" architecture (one container, all domains).

A single Flask app that serves catalog, orders, and the storefront page from one
process and one image. On AWS this runs as one ECS/Fargate task (see
ecs-fargate-basics). You will split it into three Kubernetes microservices.

Run locally:
    cd src/monolith
    pip install flask==3.1.0
    python app.py      # http://localhost:8080/
"""

import os
import uuid

from flask import Flask, jsonify, request

APP_VERSION = os.environ.get("APP_VERSION", "monolith-1.0")
app = Flask(__name__)

BOOKS = {
    "b1": {"id": "b1", "title": "The Pragmatic Programmer", "price": 39.99},
    "b2": {"id": "b2", "title": "Designing Data-Intensive Applications", "price": 44.99},
    "b3": {"id": "b3", "title": "Release It!", "price": 34.99},
}
ORDERS = {}


@app.get("/health")
def health():
    return jsonify(status="ok", version=APP_VERSION)


# ---- Catalog domain (later: catalog microservice) ----
@app.get("/books")
def list_books():
    return jsonify(version=APP_VERSION, books=list(BOOKS.values()))


@app.get("/books/<book_id>")
def get_book(book_id):
    book = BOOKS.get(book_id)
    return (jsonify(book), 200) if book else (jsonify(error="not found"), 404)


# ---- Orders domain (later: orders microservice) ----
@app.post("/orders")
def create_order():
    body = request.get_json(force=True)
    if body.get("book_id") not in BOOKS:
        return jsonify(error="unknown book_id"), 400
    oid = str(uuid.uuid4())
    ORDERS[oid] = {"id": oid, "book_id": body["book_id"],
                   "qty": int(body.get("qty", 1)), "status": "PLACED"}
    return jsonify(ORDERS[oid]), 201


# ---- Storefront page (later: frontend microservice) ----
@app.get("/")
def home():
    rows = "".join(f"<li>{b['title']} — ${b['price']}</li>" for b in BOOKS.values())
    return f"<h1>Shop ({APP_VERSION})</h1><ul>{rows}</ul>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
