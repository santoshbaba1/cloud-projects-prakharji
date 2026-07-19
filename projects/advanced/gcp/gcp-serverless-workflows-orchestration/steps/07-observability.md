# Step 7 — Observability

Orchestration's payoff is that the whole process is **inspectable**: which step ran, what it returned,
where it failed, and what's queued. This step shows you where to look across Workflows, the functions,
and Cloud Tasks.

---

## 7.1 Workflow Execution History

Every run is retained with its state and result:

```bash
export REGION=us-east1
gcloud workflows executions list order-fulfillment --location "$REGION" \
  --format='table(name.scope(executions), state, startTime, endTime)'
```

Drill into one execution to see the input, output, and (on failure) the error:

```bash
EXEC="$(gcloud workflows executions list order-fulfillment --location "$REGION" \
  --limit 1 --format='value(name)')"
gcloud workflows executions describe "$EXEC" --location "$REGION" \
  --format='yaml(state, argument, result, error)'
```

In the **Console → Workflows → order-fulfillment → Executions**, each run is a **visual graph** with
the failed step highlighted and each step's I/O expandable — the fastest way to debug a process.

---

## 7.2 Step-Level Function Logs

Each step function logs structured JSON (Step-1 habit). Correlate a run across all of them:

```bash
for NAME in validate-order charge-payment refund-payment shipping-worker order-intake; do
  echo "=== $NAME ==="
  gcloud functions logs read "$NAME" --gen2 --region "$REGION" --limit 3
done
```

Because every line carries `order_id`, you can filter the whole system by one order in Logs Explorer:

```
jsonPayload.order_id="5001"
```

That single query stitches together intake → validate → charge → ship for one order across five
functions — the reason structured logging was worth the discipline.

---

## 7.3 Cloud Tasks Queue State

Inspect the queue and any in-flight/backlogged tasks:

```bash
gcloud tasks queues describe order-shipping-queue --location "$REGION" \
  --format='value(name, state, rateLimits.maxDispatchesPerSecond, retryConfig.maxAttempts)'

gcloud tasks list --queue order-shipping-queue --location "$REGION" \
  --format='table(name, dispatchCount, responseCount)' 2>/dev/null \
  || echo "(no tasks in flight — they complete in seconds)"
```

A healthy queue drains almost immediately here. If `shipping-worker` were failing, you'd see tasks
accumulate with rising `dispatchCount` (retries) until they hit `maxAttempts`.

---

## 7.4 (Optional) Trace the Identity of Each Hop

Prove *who* called *what* by reading a step function's request auth. Add a temporary log of the
incoming `Authorization` audience in `shipping-worker`, redeploy, run an order, and confirm the token
was minted for `tasks-invoker-sa`. This makes the [architecture.md §2](../architecture.md) identity
chain concrete rather than theoretical. Remove the temporary log afterwards.

---

## Checkpoint

- [ ] You can list executions and describe one's `state`/`result`/`error`
- [ ] A single `jsonPayload.order_id` query returns entries from multiple functions
- [ ] `gcloud tasks queues describe` shows the queue's rate/retry config
- [ ] You've seen the visual execution graph in the Console

---

**Next:** [Step 8 — Cleanup](./08-cleanup.md)
