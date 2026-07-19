# Step 2 — Inbox Bucket and Pub/Sub Topic

Two resources hold the ends of the pipeline: a **bucket** partners upload to, and a **topic** that
fans out order events. You'll create both now.

---

## 2.1 The Inbox Bucket

Bucket names are **globally unique**, so suffix it with your project ID:

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export REGION=us-east1
export INBOX="meridian-orders-inbox-${PROJECT_ID}"

gcloud storage buckets create "gs://${INBOX}" \
  --location="$REGION" \
  --uniform-bucket-level-access \
  --public-access-prevention
```

| Flag | Why |
|------|-----|
| `--location=us-east1` | Must be compatible with the Eventarc trigger region |
| `--uniform-bucket-level-access` | IAM-only permissions (no legacy per-object ACLs) — the modern default |
| `--public-access-prevention` | Orders are private; block any accidental public exposure |

Confirm:

```bash
gcloud storage buckets describe "gs://${INBOX}" --format='value(name, location)'
```

---

## 2.2 The `order-events` Topic

```bash
gcloud pubsub topics create order-events
```

That's the fan-out point. `order-ingest` will publish to it; `order-notifier` (Step 4) subscribes.
You do **not** need to create a subscription by hand — deploying a Pub/Sub-triggered function creates
a push subscription automatically.

Verify:

```bash
gcloud pubsub topics list --format='table(name)'
```

---

## 2.3 (Concept) Why a Topic Instead of Calling the Next Function Directly?

`order-ingest` could just HTTP-call `order-notifier`. It publishes to a topic instead because:

- **Decoupling** — ingest doesn't know who consumes; add analytics/fraud/warehouse consumers later
  with zero changes to ingest.
- **Buffering** — a burst of uploads queues in Pub/Sub instead of overwhelming a downstream.
- **Retry isolation** — if a consumer is down, Pub/Sub retries *that* delivery without re-running
  ingest.

This is the single most important architectural idea in the project: **publish an event, don't call a
service.**

---

## Checkpoint

- [ ] `gs://meridian-orders-inbox-<PROJECT_ID>` exists in `us-east1` with uniform access
- [ ] Public access prevention is enforced on the bucket
- [ ] The `order-events` topic exists
- [ ] You can articulate why ingest publishes an event rather than calling the notifier

---

**Next:** [Step 3 — Deploy `order-ingest` (Eventarc)](./03-deploy-ingest.md)
