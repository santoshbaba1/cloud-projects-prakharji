# Step 4 — Deploy `order-notifier` (Pub/Sub Trigger)

The consumer half. `order-notifier` subscribes to the `order-events` topic and reacts to each
published event — completely independently of `order-ingest`.

---

## 4.1 Deploy with a Pub/Sub Trigger

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export REGION=us-east1
export FN_SA="order-fns-sa@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud functions deploy order-notifier \
  --gen2 \
  --runtime python312 \
  --region "$REGION" \
  --source ./src/order_notifier \
  --entry-point order_notifier \
  --trigger-topic order-events \
  --service-account "$FN_SA" \
  --set-env-vars "COUNTER_DOC=stats/orders" \
  --memory 256Mi \
  --max-instances 5
```

| Flag | Why |
|------|-----|
| `--trigger-topic order-events` | Fire on every message published to that topic |
| `--service-account $FN_SA` | Same least-privilege SA (it only needs `datastore.user` here) |
| `COUNTER_DOC=stats/orders` | Which Firestore doc to increment |

`--trigger-topic` automatically creates a **push subscription** on `order-events` and wires the
Eventarc/Pub/Sub delivery for you — you don't manage the subscription by hand.

> **1st-gen note:** a classic Pub/Sub-triggered function receives the message differently. On 2nd gen
> the handler is a **CloudEvent** whose payload is at `data["message"]["data"]`, base64-encoded —
> which is exactly what `order_notifier/main.py` decodes.

### Console (Alternative)

1. **Create function**, 2nd gen, name `order-notifier`, region us-east1.
2. **Trigger → Cloud Pub/Sub**, topic `order-events`. Trigger SA `order-fns-sa`.
3. Runtime Python 3.12, entry point `order_notifier`, env var `COUNTER_DOC=stats/orders`, upload
   `src/order_notifier`. **Deploy.**

---

## 4.2 Confirm the Subscription Exists

```bash
gcloud pubsub subscriptions list \
  --format='table(name, topic, pushConfig.pushEndpoint)'
```

You'll see an auto-created subscription on `order-events` whose push endpoint is the
`order-notifier` Cloud Run URL.

---

## 4.3 Smoke-Test the Consumer Directly

Before uploading any files, prove the notifier works by publishing a message by hand:

```bash
gcloud pubsub topics publish order-events \
  --message '{"order_id":"9999","total":10.0}'

# Give it a few seconds, then check the notifier logged it:
gcloud functions logs read order-notifier --gen2 --region "$REGION" --limit 10
```

You should see `notification sent to customer` with `order_id: 9999`, and a `counter updated` line.
Check Firestore picked it up:

```bash
gcloud firestore documents get "stats/orders" 2>/dev/null || \
  echo "(use the Console → Firestore to view stats/orders if the CLI verb is unavailable)"
```

> This manual publish is the fastest way to isolate "is the consumer healthy?" from "is the trigger
> firing?" — a habit worth keeping for any event system.

---

## Checkpoint

- [ ] `order-notifier` deployed with `state: ACTIVE`
- [ ] A push subscription on `order-events` points at the notifier
- [ ] A manual `topics publish` produces `notification sent` in the notifier logs
- [ ] `stats/orders` in Firestore shows `orders_notified: 1`

---

**Next:** [Step 5 — Run the Whole Pipeline](./05-run-the-pipeline.md)
