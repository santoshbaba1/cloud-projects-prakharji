"""orders microservice — owns orders; validates books by CALLING catalog.

Single responsibility: place/read orders. To check a book_id is real it makes an
HTTP call to the catalog service via Kubernetes DNS (CATALOG_URL). That
service-to-service call is the microservices analog of the monolith's in-process
function call — now it crosses a network boundary, so it can fail, time out, and
must be handled.
"""

import os
import uuid

import requests
from flask import Flask, jsonify, request

APP_VERSION = os.environ.get("APP_VERSION", "orders-1.0")
CATALOG_URL = os.environ.get("CATALOG_URL", "http://catalog.shop.svc.cluster.local")
app = Flask(__name__)

ORDERS = {}


@app.get("/health")
def health():
    return jsonify(status="ok", service="orders", version=APP_VERSION)


@app.post("/orders")
def create_order():
    body = request.get_json(force=True)
    book_id = body.get("book_id", "")
    try:
        r = requests.get(f"{CATALOG_URL}/books/{book_id}", timeout=2)
    except requests.RequestException:
        return jsonify(error="catalog unavailable"), 503
    if r.status_code != 200:
        return jsonify(error="unknown book_id"), 400
    oid = str(uuid.uuid4())
    ORDERS[oid] = {"id": oid, "book_id": book_id,
                   "qty": int(body.get("qty", 1)), "status": "PLACED"}
    return jsonify(ORDERS[oid]), 201


@app.get("/orders/<order_id>")
def get_order(order_id):
    order = ORDERS.get(order_id)
    return (jsonify(order), 200) if order else (jsonify(error="not found"), 404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
