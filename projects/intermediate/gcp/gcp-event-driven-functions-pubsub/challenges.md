# Challenges — GCP Event-Driven Functions

Extend the pipeline. Each is a realistic next feature an event-driven system grows into.

---

### 1. Send a real notification

Replace the log line in `order_notifier` with an actual email via **SendGrid** or a Slack webhook
(store the API key in **Secret Manager**, mount it with `--set-secrets`). Now the "notification" is
real — and you've kept the credential out of code and env vars.

---

### 2. Add a second, independent consumer

Deploy `order-analytics` on the **same** `order-events` topic that writes a daily revenue rollup to a
separate Firestore doc. Prove the fan-out: one publish, two consumers, and `order-ingest` didn't
change at all. This is the payoff of publishing events instead of calling services.

---

### 3. Process images, not JSON

Point a second Eventarc trigger at an `images/` prefix. In the handler, use Pillow to generate a
thumbnail and write it to an `outbox` bucket — the GCP twin of
[`aws-lambda-s3-event-processing`](../../../beginner/aws/aws-lambda-s3-event-processing/README.md)'s
two-bucket pattern. Watch for the trigger loop (don't write thumbnails back into the trigger bucket!).

---

### 4. Enforce ordering with an ordering key

Pub/Sub can deliver messages **in order** per ordering key. Publish with
`--ordering-key="$order_id"` and enable message ordering on the subscription, then reason about the
throughput trade-off (ordered delivery serializes per key).

---

### 5. Move validation into a schema

Attach a **Pub/Sub schema** (Avro/Protobuf) to `order-events` so malformed events are rejected at
publish time, before a consumer ever sees them. Compare "validate in the consumer" vs. "validate at
the topic".

---

### 6. Exactly-once counting

The counter can slightly over-count under retries. Add a `processed_events` collection keyed by the
Pub/Sub `message_id` and skip already-seen IDs, turning at-least-once into effective exactly-once for
the counter.

---

### 7. Replay from the dead-letter queue

Write a small function or script that pulls from `order-events-dlq-sub`, fixes/inspects the payload,
and republishes to `order-events`. This is how real systems recover poison messages after a bug fix.
