# Troubleshooting — GCP Serverless Orchestration

Error → Cause → Fix. Nearly every failure here is an **IAM link in the identity chain** or a
**placeholder left unsubstituted** in the workflow/API YAML.

---

## Workflow deploy fails: YAML/syntax or `unresolved value` error

**Cause:** A `__…__` placeholder wasn't substituted, or an expression is malformed.

**Fix:** Deploy the **substituted** file, not the source:
```bash
grep -n '__' /tmp/order-fulfillment.deployed.yaml   # must return nothing
```
Re-run the `sed` block in [Step 4.1](steps/04-deploy-workflow.md) if tokens remain.

---

## Execution fails at `validate`/`charge`/`refund` with `403` / `PermissionDenied`

**Cause:** `order-workflow-sa` lacks `run.invoker` on that function (the workflow can't call it).

**Fix:** Re-grant it on the specific function:
```bash
gcloud run services add-iam-policy-binding charge-payment --region us-east1 \
  --member "serviceAccount:order-workflow-sa@$(gcloud config get-value project).iam.gserviceaccount.com" \
  --role roles/run.invoker
```
Also confirm the workflow was deployed with `--service-account order-workflow-sa` (else it runs as the
default SA, which has no invoker rights).

---

## Execution fails at `enqueueShipping` with `iam.serviceAccounts.actAs` denied

**Cause:** `order-workflow-sa` can't act as `tasks-invoker-sa`, so it can't name it as the task's OIDC
identity. **This is the most common failure in the project.**

**Fix:**
```bash
gcloud iam service-accounts add-iam-policy-binding \
  "tasks-invoker-sa@$(gcloud config get-value project).iam.gserviceaccount.com" \
  --member "serviceAccount:order-workflow-sa@$(gcloud config get-value project).iam.gserviceaccount.com" \
  --role roles/iam.serviceAccountUser
```

---

## Execution fails at `enqueueShipping` with `queue does not exist` / `NOT_FOUND`

**Cause:** The queue name/location in the workflow doesn't match the created queue, or the workflow SA
lacks `cloudtasks.enqueuer`.

**Fix:** Confirm the queue and the grant:
```bash
gcloud tasks queues describe order-shipping-queue --location us-east1 --format='value(name,state)'
gcloud tasks queues add-iam-policy-binding order-shipping-queue --location us-east1 \
  --member "serviceAccount:order-workflow-sa@$(gcloud config get-value project).iam.gserviceaccount.com" \
  --role roles/cloudtasks.enqueuer
```

---

## Task is created but `shipping-worker` never runs / logs `403`

**Cause:** `tasks-invoker-sa` lacks `run.invoker` on `shipping-worker`.

**Fix:**
```bash
gcloud run services add-iam-policy-binding shipping-worker --region us-east1 \
  --member "serviceAccount:tasks-invoker-sa@$(gcloud config get-value project).iam.gserviceaccount.com" \
  --role roles/run.invoker
```
Check task delivery: `gcloud tasks list --queue order-shipping-queue --location us-east1`.

---

## `order-intake` returns `500` / `PermissionDenied ... workflows.executions.create`

**Cause:** `order-intake-sa` lacks `workflows.invoker`, or the function didn't deploy with that SA.

**Fix:**
```bash
gcloud projects add-iam-policy-binding "$(gcloud config get-value project)" \
  --member "serviceAccount:order-intake-sa@$(gcloud config get-value project).iam.gserviceaccount.com" \
  --role roles/workflows.invoker
gcloud functions describe order-intake --gen2 --region us-east1 \
  --format='value(serviceConfig.serviceAccountEmail)'   # must be order-intake-sa
```

---

## API Gateway `POST /orders` returns `403` or `Forbidden`

**Cause #1:** `gateway-invoker-sa` lacks `run.invoker` on `order-intake`.

**Fix:**
```bash
gcloud run services add-iam-policy-binding order-intake --region us-east1 \
  --member "serviceAccount:gateway-invoker-sa@$(gcloud config get-value project).iam.gserviceaccount.com" \
  --role roles/run.invoker
```

**Cause #2:** The config wasn't created with `--backend-auth-service-account`, so the gateway sends no
OIDC token to the backend.

**Fix:** Recreate the config with the flag (configs are immutable), then point the gateway at the new
config:
```bash
gcloud api-gateway api-configs create orders-config-v2 --api orders-api \
  --openapi-spec /tmp/openapi.deployed.yaml --backend-auth-service-account "$GW_SA"
gcloud api-gateway gateways update orders-gateway --location us-east1 \
  --api-config orders-config-v2 --api orders-api
```

---

## API Gateway `POST /orders` returns `404 Not Found`

**Cause:** The OpenAPI `address` still has the `__INTAKE_URL__` placeholder, or the path doesn't match
(`/orders`).

**Fix:** Confirm the substituted spec and that you POSTed the right path:
```bash
grep address /tmp/openapi.deployed.yaml   # must be the real function URL
```

---

## `gcloud workflows run` hangs for ~30 seconds on the transient order

**Cause:** Expected — the retry policy waits between the three attempts (2s → 4s → 8s backoff).

**Fix:** Nothing; it's the retry backoff. It ends in `FAILED` after the attempts exhaust.

---

## Gateway creation takes several minutes / seems stuck

**Cause:** Provisioning a managed gateway + its service config is genuinely slow (2–5 min).

**Fix:** Wait; check `gcloud api-gateway gateways describe orders-gateway --location us-east1
--format='value(state)'` — it moves `CREATING` → `ACTIVE`.
