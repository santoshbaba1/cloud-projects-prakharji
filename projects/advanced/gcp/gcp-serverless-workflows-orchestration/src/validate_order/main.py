"""validate-order — a single step in the order-fulfillment workflow.

Given an order, decide whether it can proceed. Pure and fast: no side effects, so
the workflow can safely retry it. Returns HTTP 200 with {"status": "valid"} or
{"status": "invalid", "reason": ...} — the workflow branches on that field.
"""
import json

import functions_framework

# Tiny in-memory catalog with stock levels. In production this would be a Firestore
# or Cloud SQL lookup; kept in-memory so the lab needs no database.
CATALOG = {
    "Wool Overcoat": 12,
    "Leather Boots": 4,
    "Cashmere Scarf": 0,   # deliberately out of stock to exercise the invalid path
}


def _log(severity, message, **fields):
    print(json.dumps({"severity": severity, "message": message, **fields}))


@functions_framework.http
def validate_order(request):
    order = request.get_json(silent=True) or {}
    order_id = order.get("order_id", "?")
    item = order.get("item")
    quantity = int(order.get("quantity", 0))
    total = float(order.get("total", 0))

    def invalid(reason):
        _log("WARNING", "order invalid", order_id=order_id, reason=reason)
        return {"status": "invalid", "reason": reason}, 200

    if item not in CATALOG:
        return invalid(f"unknown item: {item}")
    if quantity <= 0:
        return invalid("quantity must be positive")
    if total <= 0:
        return invalid("total must be positive")
    if CATALOG[item] < quantity:
        return invalid(f"insufficient stock for {item} (have {CATALOG[item]})")

    _log("INFO", "order valid", order_id=order_id)
    return {"status": "valid", "order_id": order_id}, 200
