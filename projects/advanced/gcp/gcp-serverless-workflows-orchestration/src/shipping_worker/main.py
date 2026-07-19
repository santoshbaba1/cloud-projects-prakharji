"""shipping-worker — the async Cloud Tasks target.

The workflow enqueues a Cloud Task instead of shipping inline, because shipping is
slow, retryable, and shouldn't hold the workflow (or the customer's HTTP request)
open. Cloud Tasks delivers this HTTP POST with its own retry/backoff policy; the
worker just does the work and returns 200 to ack the task.
"""
import json

import functions_framework


def _log(severity, message, **fields):
    print(json.dumps({"severity": severity, "message": message, **fields}))


@functions_framework.http
def shipping_worker(request):
    order = request.get_json(silent=True) or {}
    order_id = order.get("order_id", "?")

    # Pretend to book a courier, print a label, etc. Returning 200 acks the task;
    # returning >=500 makes Cloud Tasks retry it later (its own retry config).
    _log("INFO", "order shipped", order_id=order_id, item=order.get("item"))
    return {"status": "shipped", "order_id": order_id}, 200
