# Step 4 — Deploy the Workflow

Now the orchestrator itself. The definition in `workflow/order-fulfillment.yaml` has `__TOKEN__`
placeholders for the function URLs and project values — you'll fill them in, then deploy the workflow
to run as `order-workflow-sa`.

---

## 4.1 Fill in the Placeholders

Export the four function URLs (from Step 2.3) and the identity values, then substitute them into a
deployable copy of the YAML:

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export REGION=us-east1
export TASKS_SA="tasks-invoker-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Pull the URLs straight from the deployed functions:
export VALIDATE_URL="$(gcloud functions describe validate-order --gen2 --region "$REGION" --format='value(serviceConfig.uri)')"
export CHARGE_URL="$(gcloud functions describe charge-payment  --gen2 --region "$REGION" --format='value(serviceConfig.uri)')"
export REFUND_URL="$(gcloud functions describe refund-payment  --gen2 --region "$REGION" --format='value(serviceConfig.uri)')"
export SHIPPING_URL="$(gcloud functions describe shipping-worker --gen2 --region "$REGION" --format='value(serviceConfig.uri)')"

# Substitute tokens into a build copy (sed keeps the source YAML pristine).
sed \
  -e "s|__VALIDATE_URL__|${VALIDATE_URL}|g" \
  -e "s|__CHARGE_URL__|${CHARGE_URL}|g" \
  -e "s|__REFUND_URL__|${REFUND_URL}|g" \
  -e "s|__SHIPPING_URL__|${SHIPPING_URL}|g" \
  -e "s|__PROJECT_ID__|${PROJECT_ID}|g" \
  -e "s|__TASKS_SA__|${TASKS_SA}|g" \
  workflow/order-fulfillment.yaml > /tmp/order-fulfillment.deployed.yaml

grep -n "run.app\|${PROJECT_ID}" /tmp/order-fulfillment.deployed.yaml | head
```

The `grep` should show real URLs and your project ID — **no** remaining `__…__` tokens.

> Why placeholders + `sed`? The function URLs aren't known until the functions are deployed, and they
> differ per project. Templating keeps the checked-in workflow portable; this is the same reason the
> App Delivery track templates `image:` in its skaffold config.

---

## 4.2 Deploy the Workflow

```bash
export WF_SA="order-workflow-sa@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud workflows deploy order-fulfillment \
  --source /tmp/order-fulfillment.deployed.yaml \
  --location "$REGION" \
  --service-account "$WF_SA"
```

| Flag | Why |
|------|-----|
| `--source` | The filled-in YAML |
| `--service-account $WF_SA` | The workflow **runs as** this SA — which is why Steps 2–3 granted it invoker/enqueuer/actAs |

Deployment validates the YAML syntax. A syntax error points at the offending line — see
[troubleshooting.md](../troubleshooting.md).

### Console (Alternative)

1. **Workflows → Create**. Name `order-fulfillment`, region us-east1, service account
   `order-workflow-sa`.
2. Paste the **substituted** YAML (`/tmp/order-fulfillment.deployed.yaml`) into the editor.
3. **Deploy**.

---

## 4.3 Confirm

```bash
gcloud workflows describe order-fulfillment --location "$REGION" \
  --format='value(name, state, serviceAccount)'
# state: ACTIVE, serviceAccount: order-workflow-sa@...
```

---

## Checkpoint

- [ ] `/tmp/order-fulfillment.deployed.yaml` has no `__…__` placeholders left
- [ ] `gcloud workflows deploy` succeeded (`state: ACTIVE`)
- [ ] The workflow's service account is `order-workflow-sa`

---

**Next:** [Step 5 — Run the Workflow](./05-run-workflow.md)
