# Step 5 — Run the Whole Pipeline

Both functions are live and the topic connects them. Now trigger the real thing: **upload an order
file** and watch it flow bucket → ingest → Firestore → topic → notifier.

---

## 5.1 Upload a Good Order

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export INBOX="meridian-orders-inbox-${PROJECT_ID}"

gcloud storage cp ./src/sample-orders/order-1001.json "gs://${INBOX}/"
```

That single copy fires the whole chain. Watch it unfold:

```bash
# Ingest should log: order stored + order event published
gcloud functions logs read order-ingest --gen2 --region us-east1 --limit 10

# Notifier should log: notification sent + counter updated
gcloud functions logs read order-notifier --gen2 --region us-east1 --limit 10
```

Delivery isn't instant — give it 5–15 seconds end to end. If ingest logs nothing after ~30s, the
Eventarc trigger chain is the suspect ([troubleshooting.md](../troubleshooting.md)).

---

## 5.2 Verify Firestore

```bash
# The order document
gcloud firestore documents get "orders/1001" 2>/dev/null \
  || echo "Open Console → Firestore → orders/1001 to view it"
```

In the **Console → Firestore → Data**, you should see:

- `orders/1001` → `status: received`, `customer`, `item`, `total`, a `received_at` timestamp
- `stats/orders` → `orders_notified: N`, `revenue_total` accumulating

---

## 5.3 Upload the Rest and See the Counter Climb

```bash
gcloud storage cp ./src/sample-orders/order-1002.json "gs://${INBOX}/"
```

`stats/orders.orders_notified` should now be one higher and `revenue_total` should include 145.50.

---

## 5.4 Upload the Bad Order (validation)

```bash
gcloud storage cp ./src/sample-orders/bad-order.json "gs://${INBOX}/"
gcloud functions logs read order-ingest --gen2 --region us-east1 --limit 5
```

`bad-order.json` is missing `customer` and `total`. Ingest logs a **WARNING** `order missing fields`
and returns **without** writing Firestore or publishing — so the notifier never fires and no partial
order is stored. This is defensive validation at the edge of the pipeline.

> Note it returns rather than *raises*: a malformed file will never become valid, so retrying is
> pointless and would just spin. Compare with a *transient* failure (Firestore briefly unavailable),
> where raising to force a retry is correct — the subject of Step 6.

---

## 5.5 The Big Picture

You now have a system where **the producer and consumer never call each other**. Prove the decoupling:
open the Console side-by-side and re-upload `order-1001.json` — ingest overwrites `orders/1001`
(same doc ID = idempotent) and the notifier fires again, but there's still exactly **one** order
document. Delivery is at-least-once; your data model made it safe.

---

## Checkpoint

- [ ] Uploading `order-1001.json` creates `orders/1001` with `status: received`
- [ ] `order-notifier` fires and `stats/orders` increments
- [ ] `order-1002.json` bumps the counter and revenue
- [ ] `bad-order.json` logs a WARNING and creates **no** document
- [ ] Re-uploading a file does not create a duplicate order document

---

**Next:** [Step 6 — Reliability: Retries & Dead-Letters](./06-reliability.md)
