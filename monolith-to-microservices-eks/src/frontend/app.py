"""frontend microservice — the storefront / backend-for-frontend (BFF).

Owns no data. It aggregates the other services: renders the catalog by calling
catalog, and posts orders by calling orders. It's the only service exposed
outside the cluster (via a LoadBalancer Service), so it's the new front door.
"""

import os

import requests
from flask import Flask, jsonify, request

APP_VERSION = os.environ.get("APP_VERSION", "frontend-1.0")
CATALOG_URL = os.environ.get("CATALOG_URL", "http://catalog.shop.svc.cluster.local")
ORDERS_URL = os.environ.get("ORDERS_URL", "http://orders.shop.svc.cluster.local")
app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok", service="frontend", version=APP_VERSION)


@app.get("/")
def home():
    try:
        books = requests.get(f"{CATALOG_URL}/books", timeout=2).json().get("books", [])
    except requests.RequestException:
        return "<h1>Shop</h1><p>catalog unavailable</p>", 503
    rows = "".join(f"<li>{b['title']} — ${b['price']} (id={b['id']})</li>" for b in books)
    return f"<h1>Shop (frontend {APP_VERSION})</h1><ul>{rows}</ul>"


@app.post("/checkout")
def checkout():
    body = request.get_json(force=True)
    r = requests.post(f"{ORDERS_URL}/orders", json=body, timeout=2)
    return (r.json(), r.status_code)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
