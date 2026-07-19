# Troubleshooting — GCP Event-Driven Functions

Error → Cause → Fix. In event pipelines the top failure is **"nothing happened"** — almost always a
broken Eventarc trust chain (Step 3) or a region mismatch.

---

## I upload a file but `order-ingest` never logs anything

**Cause #1:** A missing trust-chain grant — the GCS service agent can't publish, or the trigger SA
can't receive.

**Fix:** Re-apply the three grants from [Step 3.1](steps/03-deploy-ingest.md):
```bash
GCS_SA="$(gcloud storage service-agent)"
gcloud projects add-iam-policy-binding "$(gcloud config get-value project)" \
  --member "serviceAccount:${GCS_SA}" --role roles/pubsub.publisher
```
Then re-check `eventarc.eventReceiver` on `order-fns-sa` and `serviceAccountTokenCreator` on the
Pub/Sub service agent. IAM is eventually consistent — wait ~60s after granting.

**Cause #2:** Region mismatch. The bucket, trigger-location, and function region must be compatible
(all `us-east1` here).

**Fix:**
```bash
gcloud storage buckets describe "gs://meridian-orders-inbox-$(gcloud config get-value project)" \
  --format='value(location)'
gcloud eventarc triggers list --location us-east1
```

**Cause #3:** The object isn't a `.json` at the bucket root — `main.py` deliberately skips those.

---

## Deploy fails: `... does not have permission ... eventReceiver` / trigger creation error

**Cause:** The trigger's service account lacks `roles/eventarc.eventReceiver`, or IAM hasn't
propagated yet.

**Fix:** Grant it and retry the deploy after a minute:
```bash
gcloud projects add-iam-policy-binding "$(gcloud config get-value project)" \
  --member "serviceAccount:order-fns-sa@$(gcloud config get-value project).iam.gserviceaccount.com" \
  --role roles/eventarc.eventReceiver
```

---

## Deploy fails: `Eventarc API ... not enabled` or `service-...@gcp-sa-pubsub ... not found`

**Cause:** Eventarc/Pub/Sub service agents aren't provisioned yet.

**Fix:**
```bash
gcloud services enable eventarc.googleapis.com pubsub.googleapis.com
gcloud beta services identity create --service=pubsub.googleapis.com
gcloud beta services identity create --service=eventarc.googleapis.com
```

---

## `order-ingest` runs but errors: `403 ... firestore` / `permission denied` on publish

**Cause:** The runtime SA is missing `datastore.user` or `pubsub.publisher`, or you deployed without
`--service-account order-fns-sa` (so it ran as the default SA).

**Fix:** Confirm the SA and its roles, and that the function uses it:
```bash
gcloud functions describe order-ingest --gen2 --region us-east1 \
  --format='value(serviceConfig.serviceAccountEmail)'
```

---

## `order-notifier` never fires even though `order-ingest` published

**Cause #1:** The publish failed silently (check ingest logs for `order event published`).

**Cause #2:** The auto-created push subscription is missing or points at the wrong service.

**Fix:**
```bash
gcloud pubsub subscriptions list --filter="topic:order-events" \
  --format='table(name, pushConfig.pushEndpoint)'
# Isolate the consumer: publish directly
gcloud pubsub topics publish order-events --message '{"order_id":"test","total":1}'
gcloud functions logs read order-notifier --gen2 --region us-east1 --limit 5
```

---

## Firestore error: `The Cloud Firestore API is not available ... database does not exist`

**Cause:** No Firestore database in the project, or it's in Datastore mode.

**Fix:** Create it in Native mode (once per project):
```bash
gcloud firestore databases create --location=us-east1
```
If it exists in **Datastore** mode, you can't switch it — use a separate project for this lab.

---

## Duplicate order documents appear

**Cause:** You changed `main.py` to use `.add()` (auto-ID) instead of `.document(order_id).set()`.

**Fix:** Key the document on `order_id` and use `.set()` — that's what makes at-least-once delivery
idempotent. Revert to the provided `main.py`.

---

## The pipeline "double-processes" after enabling `--retry`

**Cause:** This is expected under at-least-once delivery — a slow success can still be retried.

**Fix:** Nothing to fix if your handler is idempotent (it is). The order doc is overwritten, not
duplicated; the counter uses `Increment`, so at worst it slightly over-counts — acceptable for a
demo. For exact-once counting you'd dedupe on a processed-event ID.
