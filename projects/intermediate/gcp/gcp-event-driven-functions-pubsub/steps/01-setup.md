# Step 1 — Setup: APIs, Firestore, and a Runtime Service Account

This project touches more services than the beginner one, and event delivery depends on a chain of
IAM grants. You'll lay the groundwork here so Steps 3–4 just work.

---

## 1.1 Project and Region

```bash
export PROJECT_ID="$(gcloud config get-value project)"   # or set to your project
export REGION=us-east1
gcloud config set project "$PROJECT_ID"
gcloud config set run/region "$REGION"
gcloud config set functions/region "$REGION"
export PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
echo "Project $PROJECT_ID ($PROJECT_NUMBER) in $REGION"
```

---

## 1.2 Enable the APIs

```bash
gcloud services enable \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  eventarc.googleapis.com \
  pubsub.googleapis.com \
  storage.googleapis.com \
  firestore.googleapis.com \
  logging.googleapis.com
```

| API | Why |
|-----|-----|
| `eventarc` | Routes GCS events to the function |
| `pubsub` | The backbone Eventarc rides on **and** your explicit `order-events` topic |
| `storage` | The inbox bucket |
| `firestore` | The order + counter data store |

Enabling Eventarc for the first time can take a minute and provisions its service agent.

---

## 1.3 Create the Firestore Database (once per project)

Firestore allows **one database per project**. Check whether it exists:

```bash
gcloud firestore databases describe --database='(default)' \
  --format='value(name, type)' 2>/dev/null
```

If that errors with "not found", create it in **Native** mode in the region:

```bash
gcloud firestore databases create --location="$REGION"
```

> If it already exists (e.g. from the databases track), leave it — you'll just add new collections.
> Firestore's mode (Native vs. Datastore) is fixed at creation; this project needs **Native**.

---

## 1.4 Create the Runtime Service Account

Both functions will run **as a dedicated least-privilege service account** rather than the default
Compute SA. Create it now and grant what the *code* needs (the *event-delivery* grants come in
Step 3):

```bash
gcloud iam service-accounts create order-fns-sa \
  --display-name "Runtime SA for order pipeline functions"

export FN_SA="order-fns-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# What the code does: read objects, write Firestore, publish to Pub/Sub.
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${FN_SA}" --role roles/datastore.user
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${FN_SA}" --role roles/pubsub.publisher
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${FN_SA}" --role roles/storage.objectViewer
```

| Role | Why the code needs it |
|------|-----------------------|
| `roles/datastore.user` | `order-ingest` writes order docs; `order-notifier` increments the counter |
| `roles/pubsub.publisher` | `order-ingest` publishes to `order-events` |
| `roles/storage.objectViewer` | `order-ingest` downloads the uploaded file |

> **Least privilege in action:** this SA can read objects but not delete them, write Firestore but not
> administer it. Contrast with the AWS execution-role pattern in
> [`aws-lambda-s3-event-processing`](../../../../beginner/aws/aws-lambda-s3-event-processing/README.md).

---

## Checkpoint

- [ ] All APIs enabled (`gcloud services list --enabled` includes eventarc, pubsub, firestore)
- [ ] `gcloud firestore databases describe --database='(default)'` shows a Native DB in `us-east1`
- [ ] `order-fns-sa` exists with datastore.user, pubsub.publisher, storage.objectViewer
- [ ] `$PROJECT_NUMBER` and `$FN_SA` are exported in your shell

---

**Next:** [Step 2 — Inbox Bucket and Topic](./02-bucket-and-topic.md)
