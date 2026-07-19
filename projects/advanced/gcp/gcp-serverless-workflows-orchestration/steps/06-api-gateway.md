# Step 6 — API Gateway Front Door

Right now only someone with `gcloud` and IAM can start the workflow. Real clients need a public HTTPS
endpoint. You'll deploy the `order-intake` function (which starts an execution) and put **API
Gateway** in front of it.

---

## 6.1 Deploy `order-intake`

This function is called **by API Gateway** and, in turn, **starts a workflow execution** — so it runs
as `order-intake-sa`, which needs `workflows.invoker`.

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export REGION=us-east1
export INTAKE_SA="order-intake-sa@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud functions deploy order-intake \
  --gen2 --runtime python312 --region "$REGION" \
  --source ./src/order_intake --entry-point order_intake \
  --trigger-http --no-allow-unauthenticated \
  --service-account "$INTAKE_SA" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID},WORKFLOW_LOCATION=${REGION},WORKFLOW_NAME=order-fulfillment" \
  --memory 256Mi --max-instances 5

# Allow order-intake to create workflow executions.
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${INTAKE_SA}" --role roles/workflows.invoker

# Allow API Gateway (as gateway-invoker-sa) to invoke order-intake.
export GW_SA="gateway-invoker-sa@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud run services add-iam-policy-binding order-intake --region "$REGION" \
  --member "serviceAccount:${GW_SA}" --role roles/run.invoker
```

| Grant | Why |
|-------|-----|
| `workflows.invoker` for `order-intake-sa` | The function creates executions of `order-fulfillment` |
| `run.invoker` for `gateway-invoker-sa` on `order-intake` | API Gateway may call the backend |

---

## 6.2 Fill In and Create the API Config

Substitute the intake URL into the OpenAPI spec:

```bash
export INTAKE_URL="$(gcloud functions describe order-intake --gen2 --region "$REGION" \
  --format='value(serviceConfig.uri)')"

sed "s|__INTAKE_URL__|${INTAKE_URL}|g" api/openapi.yaml > /tmp/openapi.deployed.yaml
grep -n "address" /tmp/openapi.deployed.yaml   # should show the real URL, no token
```

Create the API and a config that runs as the gateway invoker SA:

```bash
gcloud api-gateway apis create orders-api

gcloud api-gateway api-configs create orders-config-v1 \
  --api orders-api \
  --openapi-spec /tmp/openapi.deployed.yaml \
  --backend-auth-service-account "$GW_SA"
```

| Flag | Why |
|------|-----|
| `--backend-auth-service-account $GW_SA` | The identity API Gateway uses to sign calls to the backend |

---

## 6.3 Create the Gateway

```bash
gcloud api-gateway gateways create orders-gateway \
  --api orders-api \
  --api-config orders-config-v1 \
  --location "$REGION"
```

Gateway creation takes a few minutes. Get its hostname:

```bash
export GW_HOST="$(gcloud api-gateway gateways describe orders-gateway \
  --location "$REGION" --format='value(defaultHostname)')"
echo "https://${GW_HOST}"
```

---

## 6.4 Call the Public API

```bash
curl -s -X POST "https://${GW_HOST}/orders" \
  -H 'Content-Type: application/json' \
  -d "$(cat ./src/sample-orders/order-good.json)" | python3 -m json.tool
```

Expect **202** with an `execution` name — the workflow is now running from a public HTTPS request,
with API Gateway → `order-intake` → Workflows → the step functions, each hop authenticated for you.

Confirm the execution:

```bash
gcloud workflows executions list order-fulfillment --location "$REGION" --limit 1 \
  --format='value(state)'
```

> **Note on public exposure:** the gateway is open to the internet here for simplicity. In production
> you'd require an **API key** or a **JWT** (Firebase/Auth0/IAM) in the OpenAPI `security` section —
> Challenge 4. Don't leave a truly open order endpoint running.

---

## Checkpoint

- [ ] `order-intake` deployed and has `workflows.invoker`
- [ ] `gateway-invoker-sa` has `run.invoker` on `order-intake`
- [ ] `orders-gateway` reports a `defaultHostname`
- [ ] `POST https://$GW_HOST/orders` returns **202** and starts an execution

---

**Next:** [Step 7 — Observability](./07-observability.md)
