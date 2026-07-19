# Step 5 — Run the Workflow

Before adding the API Gateway, drive the workflow **directly** with `gcloud`. You'll run all four
sample orders and watch the happy path, fast-fail validation, a hard decline, and a
transient-failure that triggers **compensation**.

---

## 5.1 The Happy Path

```bash
export REGION=us-east1

gcloud workflows run order-fulfillment --location "$REGION" \
  --data "$(cat ./src/sample-orders/order-good.json)"
```

`workflows run` blocks until the execution finishes and prints the result. Expect:

```
result: '{"order_id":"5001","status":"fulfillment_started","transaction_id":"txn_...","task":"projects/.../tasks/..."}'
state: SUCCEEDED
```

Confirm shipping actually ran (Cloud Tasks → worker, asynchronously):

```bash
gcloud functions logs read shipping-worker --gen2 --region "$REGION" --limit 5
# → "order shipped" order_id=5001
```

That log proves the full chain: workflow → Cloud Tasks → `shipping-worker`, each authenticated with a
different OIDC identity.

---

## 5.2 Fast-Fail at Validation

`order-invalid.json` orders a `Cashmere Scarf` — deliberately out of stock:

```bash
gcloud workflows run order-fulfillment --location "$REGION" \
  --data "$(cat ./src/sample-orders/order-invalid.json)"
```

Expect `state: FAILED` with a message like `order rejected at validation: insufficient stock…`. Note
`charge-payment` was **never called** — you never take money for an unfulfillable order.

---

## 5.3 A Hard Decline (no retry)

`order-decline.json` sets `"simulate": "decline"`, so charge returns **402**:

```bash
gcloud workflows run order-fulfillment --location "$REGION" \
  --data "$(cat ./src/sample-orders/order-decline.json)"
```

Expect `state: FAILED`, `payment failed…`. Crucially this fails **fast** — a 402 is not in the retry
predicate, so the workflow doesn't waste three attempts on a card that won't clear.

---

## 5.4 Transient Failure → Retry → Compensation

`order-transient.json` sets `"simulate": "transient"`, so charge returns **503 every time**. Watch the
retry policy exhaust, and — because this order's charge never succeeds — the workflow fails at charge
(no compensation needed, since nothing was charged):

```bash
gcloud workflows run order-fulfillment --location "$REGION" \
  --data "$(cat ./src/sample-orders/order-transient.json)"
```

Expect it to take ~15–30s (the backoff between 3 retries) then `state: FAILED`. Inspect the retries in
the execution history:

```bash
EXEC="$(gcloud workflows executions list order-fulfillment --location "$REGION" \
  --limit 1 --format='value(name)')"
gcloud workflows executions describe "$EXEC" --location "$REGION" \
  --format='value(state, error.payload)'
```

### Seeing compensation actually fire

To watch the **refund** compensation, force a failure *after* a successful charge. The quickest way:
temporarily break the shipping enqueue by pointing the queue name in the workflow at a non-existent
queue (edit `queue:` in the YAML, re-run Step 4.1–4.2), then run `order-good.json`. Charge succeeds,
enqueue fails, and the `except` block calls `refund-payment`:

```bash
gcloud functions logs read refund-payment --gen2 --region "$REGION" --limit 5
# → "payment refunded (compensation)" order_id=5001 transaction_id=txn_...
```

Restore the real queue name and redeploy when you're done. (Challenge 2 offers a cleaner
fault-injection switch.)

---

## 5.5 Read the Execution History

Every execution is recorded with its per-step progress:

```bash
gcloud workflows executions list order-fulfillment --location "$REGION" \
  --format='table(name.scope(executions), state, startTime)'
```

The **Console → Workflows → order-fulfillment → Executions** view renders each run as a visual graph
with the step that failed highlighted — the single best reason to use a workflow engine over glue
code.

---

## Checkpoint

- [ ] `order-good` → `SUCCEEDED`, and `shipping-worker` logged the shipment
- [ ] `order-invalid` → `FAILED` at validation, charge never called
- [ ] `order-decline` → `FAILED` at charge with **402**, no retries
- [ ] `order-transient` → retried 3× then `FAILED`
- [ ] (Optional) You forced a post-charge failure and saw `refund-payment` compensate

---

**Next:** [Step 6 — API Gateway Front Door](./06-api-gateway.md)
