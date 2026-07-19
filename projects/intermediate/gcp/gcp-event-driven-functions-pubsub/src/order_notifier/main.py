"""order-notifier — Pub/Sub (order-events) → Cloud Function (2nd gen).

Subscribes to the topic that order-ingest publishes to. For each order event it
"sends a notification" (here: logs it — swap in email/SMS/Slack in a challenge) and
bumps a running counter document in Firestore so you can prove events flowed through.

This is the fan-out half: it is fully decoupled from ingest. You could add three more
subscribers (analytics, fraud check, warehouse) without touching order-ingest at all.
"""
import base64
import json
import os

import functions_framework
from cloudevents.http import CloudEvent
from google.cloud import firestore

_db = firestore.Client()
COUNTER_DOC = os.environ.get("COUNTER_DOC", "stats/orders")


def _log(severity, message, **fields):
    print(json.dumps({"severity": severity, "message": message, **fields}))


@functions_framework.cloud_event
def order_notifier(cloud_event: CloudEvent):
    """Handle a Pub/Sub messagePublished CloudEvent.

    The message payload lives base64-encoded at data.message.data.
    """
    message = cloud_event.data["message"]
    raw = base64.b64decode(message["data"]).decode("utf-8")
    event = json.loads(raw)

    order_id = event.get("order_id", "unknown")
    total = event.get("total", 0)

    # Pretend to notify the customer. In real life this is where you'd call an email
    # API; keep it a log line so the lab needs no third-party credentials.
    _log("INFO", "notification sent to customer", order_id=order_id, total=total)

    # Atomically increment a lifetime counter so repeated events are visible.
    coll, doc_id = COUNTER_DOC.split("/", 1)
    _db.collection(coll).document(doc_id).set(
        {
            "orders_notified": firestore.Increment(1),
            "revenue_total": firestore.Increment(float(total)),
            "last_order_id": order_id,
            "updated_at": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )
    _log("INFO", "counter updated", order_id=order_id)
