# Step 3 — Deploy `order-ingest` (Eventarc GCS Trigger)

This is the heart of the project: a function that fires **when a file is uploaded**. Getting the
Eventarc **trust chain** right is what makes it work — so you'll grant those roles first, then deploy.

Keep [architecture.md §1](../architecture.md) open; it diagrams every grant below.

---

## 3.1 Wire the Trust Chain

Event delivery needs three grants beyond what the runtime SA already has.

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
export FN_SA="order-fns-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# (a) The Cloud Storage service agent must be allowed to publish events to Pub/Sub.
export GCS_SA="$(gcloud storage service-agent --project="$PROJECT_ID")"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${GCS_SA}" --role roles/pubsub.publisher

# (b) The trigger's SA (our runtime SA) must be allowed to receive Eventarc events.
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${FN_SA}" --role roles/eventarc.eventReceiver

# (c) The Pub/Sub service agent must be able to mint tokens (create it if missing, then grant).
gcloud beta services identity create --service=pubsub.googleapis.com --project="$PROJECT_ID"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-pubsub.iam.gserviceaccount.com" \
  --role roles/iam.serviceAccountTokenCreator
```

| Grant | Principal | Why |
|-------|-----------|-----|
| `pubsub.publisher` | GCS service agent | GCS publishes `object.finalized` into Eventarc's Pub/Sub |
| `eventarc.eventReceiver` | `order-fns-sa` | The trigger identity may receive the event |
| `iam.serviceAccountTokenCreator` | Pub/Sub service agent | Pub/Sub signs the push request to your function |

> **Why this is fiddly:** GCS→function is not one hop. Missing any grant makes the trigger silently
> fail to deliver. If your pipeline "does nothing" later, re-check these three.

---

## 3.2 Deploy the Function with a GCS Trigger

```bash
export REGION=us-east1
export INBOX="meridian-orders-inbox-${PROJECT_ID}"

gcloud functions deploy order-ingest \
  --gen2 \
  --runtime python312 \
  --region "$REGION" \
  --source ./src/order_ingest \
  --entry-point order_ingest \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=${INBOX}" \
  --trigger-location="$REGION" \
  --service-account "$FN_SA" \
  --set-env-vars "ORDER_EVENTS_TOPIC=order-events,GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
  --memory 256Mi \
  --max-instances 5
```

| Flag | Why |
|------|-----|
| `--trigger-event-filters type=…object.v1.finalized` | Fire on new/overwritten objects |
| `--trigger-event-filters bucket=…` | Scope the trigger to the inbox bucket only |
| `--trigger-location us-east1` | Eventarc trigger region (matches the bucket) |
| `--service-account $FN_SA` | Run and receive events as the least-privilege SA |

The first deploy both builds the function **and** creates the Eventarc trigger. It can take 2–3
minutes. If it fails with a permissions/propagation error, wait ~60s (IAM is eventually consistent)
and re-run — see [troubleshooting.md](../troubleshooting.md).

### Console (Alternative)

1. **Cloud Functions → Create function**, 2nd gen, name `order-ingest`, region us-east1.
2. **Trigger → Add Eventarc trigger**: event provider **Cloud Storage**, event
   `google.cloud.storage.object.v1.finalized`, bucket = your inbox, region us-east1.
3. Trigger service account = `order-fns-sa`. Accept the prompt to grant missing roles if offered.
4. **Runtime** = Python 3.12, entry point `order_ingest`, add the two env vars, service account
   `order-fns-sa`, upload `src/order_ingest`. **Deploy**.

---

## 3.3 Confirm the Trigger Is Active

```bash
gcloud eventarc triggers list --location "$REGION" \
  --format='table(name, eventFilters.value.list(), destination.cloudRun.service)'

gcloud eventarc triggers describe \
  "$(gcloud eventarc triggers list --location "$REGION" --format='value(name)' | head -n1)" \
  --location "$REGION" --format='value(name, transport.pubsub.topic)'
```

You should see a trigger tied to `order-ingest` and an Eventarc-managed Pub/Sub topic behind it.

---

## Checkpoint

- [ ] The three trust-chain grants succeeded
- [ ] `order-ingest` deployed with `state: ACTIVE`
- [ ] `gcloud eventarc triggers list` shows a trigger targeting the function
- [ ] The trigger's event filter is `object.v1.finalized` on your inbox bucket

---

**Next:** [Step 4 — Deploy `order-notifier` (Pub/Sub)](./04-deploy-notifier.md)
