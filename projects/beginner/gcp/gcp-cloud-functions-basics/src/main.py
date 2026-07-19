"""Meridian Retail — order-status HTTP Cloud Function (2nd gen).

A single HTTP-triggered function that answers "what's the status of order N?".
It is deliberately stateless: the "orders" live in an in-memory dict so the whole
project stays free-tier and needs no database. The point is the *serverless plumbing*
— HTTP trigger, environment-variable config, and structured logging — not the data.

Environment variables (set at deploy time, no rebuild needed):
  STORE_NAME    → shown in every response so you can prove config is injected
  ENVIRONMENT   → e.g. "dev"/"prod"; included in logs and the response

Cloud Run functions inject the request as a Flask Request object. We read the
`order_id` from the query string (`?order_id=1001`) or a JSON body.
"""
import json
import logging
import os

import functions_framework

STORE_NAME = os.environ.get("STORE_NAME", "Meridian Retail")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")

# Stand-in "database". In the intermediate project this becomes Firestore.
ORDERS = {
    "1001": {"item": "Wool Overcoat", "status": "shipped", "total": 189.00},
    "1002": {"item": "Leather Boots", "status": "packing", "total": 145.50},
    "1003": {"item": "Cashmere Scarf", "status": "cancelled", "total": 79.99},
}


def _structured_log(severity, message, **fields):
    """Emit one JSON line so Cloud Logging parses severity + custom fields.

    Cloud Logging reads stdout/stderr; a JSON payload with a `severity` key is
    promoted to a real log level and the extra keys become queryable fields.
    """
    entry = {"severity": severity, "message": message, "environment": ENVIRONMENT}
    entry.update(fields)
    print(json.dumps(entry))


@functions_framework.http
def order_status(request):
    """Return the status of an order as JSON.

    GET  /?order_id=1001
    POST / {"order_id": "1001"}
    """
    order_id = request.args.get("order_id")
    if order_id is None and request.is_json:
        order_id = (request.get_json(silent=True) or {}).get("order_id")

    # A missing order_id means the scheduled "heartbeat" ping (Step 5) — treat it
    # as a health check, not an error, so the schedule doesn't log noise.
    if not order_id:
        _structured_log("INFO", "heartbeat ping (no order_id)")
        return {"store": STORE_NAME, "status": "ok", "orders_loaded": len(ORDERS)}, 200

    order = ORDERS.get(str(order_id))
    if order is None:
        _structured_log("WARNING", "order not found", order_id=order_id)
        return {"store": STORE_NAME, "error": f"order {order_id} not found"}, 404

    _structured_log("INFO", "order looked up", order_id=order_id, status=order["status"])
    return {
        "store": STORE_NAME,
        "environment": ENVIRONMENT,
        "order_id": order_id,
        "order": order,
    }, 200
