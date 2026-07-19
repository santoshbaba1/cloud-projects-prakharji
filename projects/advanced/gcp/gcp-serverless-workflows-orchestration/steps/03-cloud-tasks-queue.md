# Step 3 — Cloud Tasks Queue

The workflow won't ship inline — it hands shipping to **Cloud Tasks**, which delivers the work to
`shipping-worker` with its own rate limits and retries. Create the queue and complete the
task→worker identity wiring.

---

## 3.1 Create the Queue

```bash
export REGION=us-east1

gcloud tasks queues create order-shipping-queue \
  --location "$REGION" \
  --max-dispatches-per-second=5 \
  --max-attempts=5 \
  --min-backoff=5s \
  --max-backoff=60s
```

| Flag | Why |
|------|-----|
| `--max-dispatches-per-second=5` | Rate-limit delivery to the worker (protect a slow downstream) |
| `--max-attempts=5` | Retry a failing task up to 5× before giving up |
| `--min/--max-backoff` | Exponential backoff between retries |

These retry semantics belong to the **queue**, independent of the workflow's retry policy — that
separation is the whole point of the async handoff.

---

## 3.2 Let the Workflow Enqueue and Delegate the Worker Identity

The workflow (as `order-workflow-sa`) must be able to (a) **create tasks** in the queue, and (b) set
`tasks-invoker-sa` as the task's OIDC identity — which requires **acting as** that SA.

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export WF_SA="order-workflow-sa@${PROJECT_ID}.iam.gserviceaccount.com"
export TASKS_SA="tasks-invoker-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# (a) Enqueue tasks into this specific queue.
gcloud tasks queues add-iam-policy-binding order-shipping-queue --location "$REGION" \
  --member "serviceAccount:${WF_SA}" --role roles/cloudtasks.enqueuer

# (b) Act as tasks-invoker-sa (so it can be named as the task's OIDC identity).
gcloud iam service-accounts add-iam-policy-binding "$TASKS_SA" \
  --member "serviceAccount:${WF_SA}" --role roles/iam.serviceAccountUser
```

| Grant | Why (see [architecture.md §2](../architecture.md)) |
|-------|-----|
| `cloudtasks.enqueuer` on the queue | `order-workflow-sa` may add tasks |
| `iam.serviceAccountUser` on `tasks-invoker-sa` | Required to name it as the task's `oidcToken` identity |

> **This `serviceAccountUser` grant is the #1 orchestration gotcha.** Without it, task creation fails
> with `PERMISSION_DENIED ... iam.serviceAccounts.actAs`. The rule: to tell one service to run *as*
> an identity, you must be allowed to act as that identity.

Recall from Step 2 that `tasks-invoker-sa` already has `run.invoker` on `shipping-worker`, so the
final hop (Cloud Tasks → worker) is authorized.

---

## Checkpoint

- [ ] `order-shipping-queue` exists in `us-east1` with the retry/rate settings
- [ ] `order-workflow-sa` has `cloudtasks.enqueuer` on the queue
- [ ] `order-workflow-sa` has `iam.serviceAccountUser` on `tasks-invoker-sa`
- [ ] You can explain why the `actAs` grant is needed

---

**Next:** [Step 4 — Deploy the Workflow](./04-deploy-workflow.md)
