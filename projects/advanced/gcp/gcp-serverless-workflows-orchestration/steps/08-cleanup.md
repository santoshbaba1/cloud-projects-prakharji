# Step 8 — Cleanup

API Gateway is the one component here **without a free tier**, so this cleanup matters more than the
earlier projects'. Delete in dependency order: gateway → API config → API, then the workflow, queue,
functions, and service accounts.

---

## 8.1 Delete the Gateway, Config, and API

Order matters — you can't delete an API that still has a config, or a config still used by a gateway.

```bash
export REGION=us-east1
gcloud api-gateway gateways delete orders-gateway --location "$REGION" --quiet
gcloud api-gateway api-configs delete orders-config-v1 --api orders-api --quiet
gcloud api-gateway apis delete orders-api --quiet
```

---

## 8.2 Delete the Workflow

```bash
gcloud workflows delete order-fulfillment --location "$REGION" --quiet
```

(Executions are deleted with the workflow; there's nothing separate to clean up.)

---

## 8.3 Delete the Cloud Tasks Queue

```bash
gcloud tasks queues delete order-shipping-queue --location "$REGION" --quiet
```

---

## 8.4 Delete the Functions

```bash
for NAME in order-intake validate-order charge-payment refund-payment shipping-worker; do
  gcloud functions delete "$NAME" --gen2 --region "$REGION" --quiet
done

# Confirm none remain:
gcloud functions list --regions "$REGION"
gcloud run services list --region "$REGION"
```

---

## 8.5 Delete the Service Accounts (optional)

```bash
export PROJECT_ID="$(gcloud config get-value project)"
for SA in order-workflow-sa tasks-invoker-sa order-intake-sa gateway-invoker-sa; do
  gcloud iam service-accounts delete "${SA}@${PROJECT_ID}.iam.gserviceaccount.com" --quiet
done
```

Deleting the SAs removes the IAM bindings that referenced them.

---

## 8.6 (Optional) Disable APIs / Delete the Project

```bash
gcloud services disable apigateway.googleapis.com --force
gcloud services disable workflows.googleapis.com --force
# Surest zero-cost outcome if this was a throwaway project:
# gcloud projects delete "$PROJECT_ID"
```

---

## Checkpoint

- [ ] `gcloud api-gateway gateways list --location us-east1` is empty
- [ ] `gcloud workflows list --location us-east1` shows no `order-fulfillment`
- [ ] `gcloud tasks queues list --location us-east1` is empty
- [ ] `gcloud functions list --regions us-east1` shows none of the five functions
- [ ] (Optional) the four service accounts are deleted

---

**Done — and that completes the GCP Serverless track.** You built:

1. an HTTP function ([beginner](../../../../beginner/gcp/gcp-cloud-functions-basics/README.md)),
2. an event-driven pipeline ([intermediate](../../../../intermediate/gcp/gcp-event-driven-functions-pubsub/README.md)),
3. and a full orchestration with retries, a saga, async tasks, and a public API (this one).

You've now seen both **choreography** (events) and **orchestration** (workflows) — the two ways to
compose serverless systems, and when each fits.
