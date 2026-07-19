# Step 2 — Deploy the Step Functions

Four small functions make up the process. All are deployed **private** (`--no-allow-unauthenticated`)
— only their authorized callers (the workflow, or Cloud Tasks) may invoke them. You'll grant those
invoker rights here.

---

## 2.1 Deploy validate / charge / refund

These three are called **by the workflow**, so `order-workflow-sa` must be able to invoke each. Deploy
them in a loop:

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export REGION=us-east1
export WF_SA="order-workflow-sa@${PROJECT_ID}.iam.gserviceaccount.com"

for fn in validate-order:validate_order charge-payment:charge_payment refund-payment:refund_payment; do
  NAME="${fn%%:*}"; DIR="${fn##*:}"
  gcloud functions deploy "$NAME" \
    --gen2 --runtime python312 --region "$REGION" \
    --source "./src/${DIR}" --entry-point "$DIR" \
    --trigger-http --no-allow-unauthenticated \
    --memory 256Mi --max-instances 5
  # Only the workflow SA may invoke it.
  gcloud run services add-iam-policy-binding "$NAME" --region "$REGION" \
    --member "serviceAccount:${WF_SA}" --role roles/run.invoker
done
```

| Choice | Why |
|--------|-----|
| `--no-allow-unauthenticated` | Private — no public caller; the workflow authenticates with OIDC |
| `run.invoker` for `$WF_SA` on each | Exactly one identity is allowed to call each step |
| entry point = folder name | e.g. `validate_order` — matches the Python function name |

---

## 2.2 Deploy shipping-worker

`shipping-worker` is invoked by **Cloud Tasks**, not the workflow — so its invoker is
`tasks-invoker-sa`:

```bash
export TASKS_SA="tasks-invoker-sa@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud functions deploy shipping-worker \
  --gen2 --runtime python312 --region "$REGION" \
  --source ./src/shipping_worker --entry-point shipping_worker \
  --trigger-http --no-allow-unauthenticated \
  --memory 256Mi --max-instances 5

gcloud run services add-iam-policy-binding shipping-worker --region "$REGION" \
  --member "serviceAccount:${TASKS_SA}" --role roles/run.invoker
```

---

## 2.3 Capture the Function URLs

Step 4 substitutes these into the workflow YAML. Grab them now:

```bash
for NAME in validate-order charge-payment refund-payment shipping-worker; do
  URL="$(gcloud functions describe "$NAME" --gen2 --region "$REGION" \
        --format='value(serviceConfig.uri)')"
  echo "${NAME} = ${URL}"
done
```

Copy these four URLs somewhere — you'll paste them (or `export` them) in Step 4.

> Because these are private, `curl`-ing them directly returns **403** — that's correct. You'll invoke
> them *through* the workflow (with its OIDC identity) in Step 5. To test one by hand:
> `curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$URL"` only works if *your*
> account has `run.invoker`; the point is that arbitrary callers can't.

---

## Checkpoint

- [ ] Four functions deployed, all `state: ACTIVE`, all private
- [ ] `order-workflow-sa` has `run.invoker` on validate/charge/refund
- [ ] `tasks-invoker-sa` has `run.invoker` on shipping-worker
- [ ] You've recorded all four `serviceConfig.uri` values

---

**Next:** [Step 3 — Cloud Tasks Queue](./03-cloud-tasks-queue.md)
