# Step 6 — Reliability: Retries, Idempotency, Dead-Letters

Event systems fail *partially* — a downstream is briefly down, a message is a poison pill. This step
makes the pipeline **resilient** on purpose so you understand the levers before you need them.

Keep [architecture.md §2](../architecture.md) open for the delivery/retry diagram.

---

## 6.1 Success = Return, Failure = Raise

The Functions Framework acks an event only when your handler **returns normally**. If it **raises**,
the event is **redelivered** with exponential backoff. That's the whole retry contract:

| Situation | What to do | Why |
|-----------|-----------|-----|
| Bad/malformed input (won't ever succeed) | **return** (log a WARNING) | Retrying is pointless; you'd loop forever |
| Transient failure (Firestore/Pub/Sub blip) | **raise** | Let the platform retry after backoff |

`order-ingest` already does this: JSON errors and missing fields `return`; the Firestore/publish calls
are allowed to raise, so a transient outage triggers a redelivery.

---

## 6.2 Prove At-Least-Once + Idempotency

Enable retries explicitly (2nd-gen event functions can opt into retry-on-failure) and reason about the
consequence:

```bash
gcloud functions deploy order-ingest \
  --gen2 --region us-east1 --source ./src/order_ingest --entry-point order_ingest \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=meridian-orders-inbox-$(gcloud config get-value project)" \
  --trigger-location=us-east1 \
  --service-account "order-fns-sa@$(gcloud config get-value project).iam.gserviceaccount.com" \
  --retry
```

Because ingest keys the Firestore document on `order_id` and uses `.set()`, **a redelivery overwrites
the same document** — no duplicate order. This is why idempotency isn't optional in event systems:
the platform *will* occasionally deliver twice, and only your data model can make that harmless.

---

## 6.3 Add a Dead-Letter Topic for the Notifier

A message the notifier can *never* process (say, malformed JSON that slipped through) would otherwise
retry until it expires. Park such poison messages in a **dead-letter topic** after N attempts.

```bash
# 1. A place for the dead letters + a subscription so they don't expire unseen.
gcloud pubsub topics create order-events-dlq
gcloud pubsub subscriptions create order-events-dlq-sub --topic order-events-dlq

# 2. Find the auto-created subscription that feeds order-notifier.
SUB="$(gcloud pubsub subscriptions list \
  --filter="topic:order-events" --format='value(name)' | grep -v dlq | head -n1)"
echo "notifier subscription: $SUB"

# 3. Attach the dead-letter policy: after 5 failed deliveries, send to the DLQ.
gcloud pubsub subscriptions update "$SUB" \
  --dead-letter-topic order-events-dlq \
  --max-delivery-attempts 5
```

Pub/Sub also needs its service agent to publish to the DLQ and to ack on the source subscription:

```bash
PROJECT_NUMBER="$(gcloud projects describe "$(gcloud config get-value project)" --format='value(projectNumber)')"
PUBSUB_SA="service-${PROJECT_NUMBER}@gcp-sa-pubsub.iam.gserviceaccount.com"
gcloud pubsub topics add-iam-policy-binding order-events-dlq \
  --member "serviceAccount:${PUBSUB_SA}" --role roles/pubsub.publisher
gcloud pubsub subscriptions add-iam-policy-binding "$SUB" \
  --member "serviceAccount:${PUBSUB_SA}" --role roles/pubsub.subscriber
```

| Setting | Effect |
|---------|--------|
| `--max-delivery-attempts 5` | After 5 failed tries, stop retrying this message |
| `--dead-letter-topic` | Route the exhausted message to `order-events-dlq` instead |
| DLQ subscription | Retains dead letters so you can inspect/replay them |

---

## 6.4 (Optional) Watch a Poison Message Land in the DLQ

Publish something the notifier can't decode (not valid base64-wrapped JSON path), let it fail 5×, then
pull from the DLQ:

```bash
gcloud pubsub topics publish order-events --message 'not-json-at-all'
# wait ~1 min for the 5 attempts + backoff, then:
gcloud pubsub subscriptions pull order-events-dlq-sub --auto-ack --limit 5
```

The bad message ends up in the DLQ instead of blocking the pipeline forever — exactly the outcome you
want. Real orders keep flowing.

---

## Checkpoint

- [ ] You can state the return-vs-raise retry contract
- [ ] Re-uploading a file yields **one** order document (idempotent under retry)
- [ ] `order-events-dlq` topic + subscription exist and the notifier's subscription has a dead-letter policy
- [ ] (Optional) a poison message landed in the DLQ after max attempts

---

**Next:** [Step 7 — Cleanup](./07-cleanup.md)
