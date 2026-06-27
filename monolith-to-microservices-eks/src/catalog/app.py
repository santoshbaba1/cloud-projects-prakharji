"""catalog microservice — owns the book catalog and nothing else.

Single responsibility: list/read books. Its own image, own Deployment, own data.
Other services reach it at http://catalog.shop.svc.cluster.local inside the cluster.
"""

import os

from flask import Flask, jsonify

APP_VERSION = os.environ.get("APP_VERSION", "catalog-1.0")
app = Flask(__name__)

BOOKS = {
    "b1": {"id": "b1", "title": "The Pragmatic Programmer", "price": 39.99},
    "b2": {"id": "b2", "title": "Designing Data-Intensive Applications", "price": 44.99},
    "b3": {"id": "b3", "title": "Release It!", "price": 34.99},
}


@app.get("/health")
def health():
    return jsonify(status="ok", service="catalog", version=APP_VERSION)


@app.get("/books")
def list_books():
    return jsonify(version=APP_VERSION, books=list(BOOKS.values()))


@app.get("/books/<book_id>")
def get_book(book_id):
    book = BOOKS.get(book_id)
    return (jsonify(book), 200) if book else (jsonify(error="not found"), 404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
