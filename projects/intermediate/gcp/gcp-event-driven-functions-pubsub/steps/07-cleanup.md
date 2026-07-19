# Step 7 — Cleanup

Delete in dependency order: functions (which remove their Eventarc triggers and push subscriptions)
first, then the topics, bucket, Firestore data, and finally the service account and IAM grants.

---

## 7.1 Delete the Functions (removes triggers + subscriptions)

```bash
export REGION=us-east1
gcloud functions delete order-ingest --gen2 --region "$REGION" --quiet
gcloud functions delete order-notifier --gen2 --region "$REGION" --quiet
```

Deleting a function removes its Cloud Run service, its Eventarc trigger, and (for the notifier) its
auto-created push subscription.

Confirm no triggers remain:

```bash
gcloud eventarc triggers list --location "$REGION"
```

---

## 7.2 Delete the Topics and Any Leftover Subscriptions

```bash
# Any subscription not auto-removed:
for s in $(gcloud pubsub subscriptions list --format='value(name)' | grep -E 'order-events'); do
  gcloud pubsub subscriptions delete "$s" --quiet
done

gcloud pubsub topics delete order-events --quiet
gcloud pubsub topics delete order-events-dlq --quiet 2>/dev/null || true
```

---

## 7.3 Empty and Delete the Bucket

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export INBOX="meridian-orders-inbox-${PROJECT_ID}"
gcloud storage rm --recursive "gs://${INBOX}" --quiet
```

(`rm --recursive` on the bucket URL deletes the objects and the bucket itself.)

---

## 7.4 Delete the Firestore Documents

Firestore has no per-collection delete from the CLI in all setups; remove the demo documents:

```bash
gcloud firestore documents delete "orders/1001" --quiet 2>/dev/null || true
gcloud firestore documents delete "orders/1002" --quiet 2>/dev/null || true
gcloud firestore documents delete "stats/orders" --quiet 2>/dev/null || true
```

> Don't delete the **database** itself if you're keeping other GCP projects that use Firestore (e.g.
> the databases track's `carts`). Deleting individual documents is enough. To wipe everything, use
> **Console → Firestore → Delete collection** or `gcloud firestore databases delete`.

---

## 7.5 Remove the Service Account and Trust-Chain Grants (optional)

```bash
export FN_SA="order-fns-sa@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud iam service-accounts delete "$FN_SA" --quiet
```

Deleting the SA removes the bindings that referenced it. The GCS/Pub/Sub **service-agent** grants
(`pubsub.publisher`, `serviceAccountTokenCreator`) are harmless to leave, but to fully revert:

```bash
export GCS_SA="$(gcloud storage service-agent --project="$PROJECT_ID")"
gcloud projects remove-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${GCS_SA}" --role roles/pubsub.publisher --quiet
```

---

## 7.6 (Optional) Disable APIs / Delete the Project

```bash
gcloud services disable eventarc.googleapis.com --force
# Cleanest of all if this was a throwaway project:
# gcloud projects delete "$PROJECT_ID"
```

---

## Checkpoint

- [ ] `gcloud functions list --regions us-east1` shows neither function
- [ ] `gcloud eventarc triggers list --location us-east1` is empty
- [ ] `gcloud pubsub topics list` shows no `order-events*`
- [ ] The inbox bucket is gone
- [ ] Demo Firestore documents removed (DB kept if shared)

---

**Done.** You built a decoupled, event-driven serverless pipeline. Next:
[GCP Serverless Orchestration with Workflows](../../../../advanced/gcp/gcp-serverless-workflows-orchestration/README.md)
— coordinating multiple functions into a reliable, multi-step **order-fulfillment** workflow.
