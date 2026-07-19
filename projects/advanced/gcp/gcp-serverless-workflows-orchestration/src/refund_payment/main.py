"""refund-payment — the compensation step for the saga.

If a later step fails after payment succeeded, the workflow calls this to undo the
charge, keeping the order in a consistent state. Idempotent: refunding an already-
refunded transaction is a no-op success, because the workflow may retry compensation.
"""
import json

import functions_framework


def _log(severity, message, **fields):
    print(json.dumps({"severity": severity, "message": message, **fields}))


@functions_framework.http
def refund_payment(request):
    body = request.get_json(silent=True) or {}
    order_id = body.get("order_id", "?")
    transaction_id = body.get("transaction_id")

    if not transaction_id:
        # Nothing was charged (e.g. failure happened before charge) → nothing to undo.
        _log("INFO", "no transaction to refund", order_id=order_id)
        return {"status": "noop"}, 200

    _log("INFO", "payment refunded (compensation)", order_id=order_id, transaction_id=transaction_id)
    return {"status": "refunded", "transaction_id": transaction_id}, 200
