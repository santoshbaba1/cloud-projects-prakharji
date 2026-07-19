# Challenges — GCP Cloud Functions Basics

Extend the finished project. Each builds on what you deployed; none require deleting it first.

---

### 1. Lock the function down (remove public access)

Redeploy with `--no-allow-unauthenticated` and prove the world can no longer call it. Then call it
yourself with an identity token (`gcloud auth print-identity-token`) and confirm the Scheduler job
*still* works because it uses its OIDC service account. This is the real production posture.

---

### 2. Add a second route without a second function

`main.py` only branches on `order_id`. Add a `?format=text` query param that returns a plain-text
summary (`Order 1001: Wool Overcoat — shipped`) instead of JSON, using the same function. Notice you
did not need a router or Flask — one handler can serve multiple shapes.

---

### 3. Move config to Secret Manager

`STORE_NAME` is harmless, but pretend it's an API key. Create a Secret Manager secret and mount it
with `--set-secrets "STORE_NAME=meridian-store-name:latest"` instead of `--set-env-vars`. Grant the
function's runtime SA `roles/secretmanager.secretAccessor`. This is the pattern the advanced projects
use for real credentials.

---

### 4. Add a `min-instances` and measure cold starts

Call the function after 15 idle minutes and note the first-request latency (cold start). Redeploy
with `--min-instances 1`, repeat, and compare. Explain the cost/latency trade-off in one sentence,
then set it back to 0.

---

### 5. Emit a custom metric from logs

Create a **log-based metric** that counts `order not found` warnings (`jsonPayload.message="order not
found"`). Then build a Cloud Monitoring alert that fires if more than N not-founds happen in 5
minutes — a cheap way to detect a broken client without any extra code.

---

### 6. Convert it to an event trigger (bridge to the next project)

Instead of HTTP, deploy a copy triggered by a **Pub/Sub topic** (`--trigger-topic order-events`).
Publish a message with `gcloud pubsub topics publish` and watch the function fire from the event. You
just previewed the [intermediate project](../../../intermediate/gcp/gcp-event-driven-functions-pubsub/README.md).

---

### 7. Add a unit test

Write a `test_main.py` that imports `order_status` and calls it with a fake request object (a small
class exposing `.args` and `.is_json`). Assert the 200/404/heartbeat paths. Run it with `pytest` — no
GCP needed, because the Functions Framework handler is just a Python function.
