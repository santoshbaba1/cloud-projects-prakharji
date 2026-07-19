"""order-ingest — Eventarc (GCS finalize) → Cloud Function (2nd gen).

Fires whenever an order file is uploaded to the inbox bucket. It:
  1. reads the uploaded JSON object from Cloud Storage,
  2. validates it has the fields an order needs,
  3. writes a record to Firestore (collection "orders"),
  4. publishes an "order received" event to Pub/Sub for downstream consumers.

This is the fan-in half of the pipeline: one upload → one durable record → one event.
Everything after (notifications, analytics, ...) subscribes to the Pub/Sub topic and
scales independently — the ingest function doesn't know or care who listens.
"""
import json
import os

import functions_framework
from cloudevents.http import CloudEvent
from google.cloud import firestore, pubsub_v1, storage

PROJECT_ID = os.environ.get("GCP_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
TOPIC_ID = os.environ.get("ORDER_EVENTS_TOPIC", "order-events")

# Clients are created at import time so they're reused across warm invocations.
_storage = storage.Client()
_db = firestore.Client()
_publisher = pubsub_v1.PublisherClient()

REQUIRED_FIELDS = ("order_id", "customer", "item", "total")


def _log(severity, message, **fields):
    print(json.dumps({"severity": severity, "message": message, **fields}))


@functions_framework.cloud_event
def order_ingest(cloud_event: CloudEvent):
    """Handle a GCS object-finalized CloudEvent."""
    data = cloud_event.data
    bucket_name = data["bucket"]
    object_name = data["name"]

    # Only process .json files dropped at the top level; ignore anything else
    # (e.g. a folder placeholder or a processed/ marker) so retries stay clean.
    if not object_name.endswith(".json"):
        _log("INFO", "skipping non-json object", object=object_name)
        return

    blob = _storage.bucket(bucket_name).blob(object_name)
    raw = blob.download_as_text()

    try:
        order = json.loads(raw)
    except json.JSONDecodeError as exc:
        _log("ERROR", "invalid JSON in order file", object=object_name, error=str(exc))
        # Return (don't raise): a malformed file will never parse, so retrying is
        # pointless. Raising would make Eventarc redeliver forever.
        return

    missing = [f for f in REQUIRED_FIELDS if f not in order]
    if missing:
        _log("WARNING", "order missing fields", object=object_name, missing=missing)
        return

    order_id = str(order["order_id"])

    # Idempotency: the document ID is the order_id, so re-processing the same file
    # (Eventarc guarantees *at-least-once*, not exactly-once) overwrites rather than
    # duplicates.
    doc_ref = _db.collection("orders").document(order_id)
    doc_ref.set(
        {
            "order_id": order_id,
            "customer": order["customer"],
            "item": order["item"],
            "total": order["total"],
            "status": "received",
            "source_object": object_name,
            "received_at": firestore.SERVER_TIMESTAMP,
        }
    )
    _log("INFO", "order stored in Firestore", order_id=order_id)

    topic_path = _publisher.topic_path(PROJECT_ID, TOPIC_ID)
    payload = json.dumps({"order_id": order_id, "total": order["total"]}).encode("utf-8")
    future = _publisher.publish(topic_path, payload, event_type="order.received")
    future.result(timeout=30)
    _log("INFO", "order event published", order_id=order_id, topic=TOPIC_ID)
