"""charge-payment — the money step. Deliberately fallible to teach retries + saga.

Behaviour is driven by the order so the lab is deterministic (no randomness):
  order.simulate == "transient" → return 503 (a retryable error; the workflow's
                                   retry policy should recover on a later attempt
                                   ... but this function ALWAYS 503s, so it lets you
                                   watch retries exhaust and the saga compensate)
  order.simulate == "decline"   → return 402 (a hard decline; not retried)
  order.total > 5000            → return 402 (over limit)
  otherwise                     → 200 {"status": "charged", "transaction_id": ...}

The workflow retries 503s (transient) and treats a 402 as a terminal failure.
"""
import json
import uuid

import functions_framework


def _log(severity, message, **fields):
    print(json.dumps({"severity": severity, "message": message, **fields}))


@functions_framework.http
def charge_payment(request):
    order = request.get_json(silent=True) or {}
    order_id = order.get("order_id", "?")
    total = float(order.get("total", 0))
    simulate = order.get("simulate")

    if simulate == "transient":
        _log("ERROR", "payment processor unavailable (simulated)", order_id=order_id)
        return {"status": "error", "reason": "processor unavailable"}, 503

    if simulate == "decline" or total > 5000:
        _log("WARNING", "payment declined", order_id=order_id, total=total)
        return {"status": "declined", "reason": "card declined"}, 402

    transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
    _log("INFO", "payment charged", order_id=order_id, transaction_id=transaction_id, total=total)
    return {"status": "charged", "transaction_id": transaction_id}, 200
