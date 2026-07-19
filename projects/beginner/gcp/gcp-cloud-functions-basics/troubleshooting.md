# Troubleshooting — GCP Cloud Functions Basics

Error → Cause → Fix. Most first-time issues are a missing API, a wrong entry point, or the runtime
service account lacking a permission.

---

## `gcloud functions deploy` fails: `API [cloudfunctions|run|cloudbuild] not enabled`

**Cause:** One of the five required APIs isn't on.

**Fix:** Re-run the Step 1 enable block:
```bash
gcloud services enable cloudfunctions.googleapis.com run.googleapis.com \
  cloudbuild.googleapis.com artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com logging.googleapis.com
```

---

## Deploy fails: `Build failed: could not find function [order_status]` / entry point error

**Cause:** `--entry-point` doesn't match the Python function name, or `main.py` isn't at the root of
`--source`.

**Fix:** The value after `--entry-point` must equal the function decorated with
`@functions_framework.http`. Here it's `order_status`. Confirm `main.py` and `requirements.txt` sit
directly inside the `src/` folder you point `--source` at.

---

## Deploy fails: `Build failed` with a pip / requirements error

**Cause:** `requirements.txt` is missing, empty, or lists a package that can't install.

**Fix:** Ensure `src/requirements.txt` contains `functions-framework==3.*`. Read the build log link
that `gcloud` prints, or:
```bash
gcloud builds list --limit 3
gcloud builds log <BUILD_ID>
```

---

## `curl` returns `403 Forbidden`

**Cause:** The function is private — you deployed **without** `--allow-unauthenticated`, or removed
the public binding.

**Fix:** Either make it public or call it with a token:
```bash
# Make public:
gcloud run services add-iam-policy-binding order-status --region us-east1 \
  --member=allUsers --role=roles/run.invoker
# Or call privately:
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$URL/?order_id=1001"
```

---

## `curl` returns `500 Internal Server Error`

**Cause:** The function raised an unhandled exception.

**Fix:** Read the error (it's logged at `ERROR` with a traceback):
```bash
gcloud functions logs read order-status --gen2 --region us-east1 --limit 20
```
Fix `main.py` and redeploy.

---

## Scheduler job runs but the function isn't invoked / job shows `PERMISSION_DENIED`

**Cause #1:** The `scheduler-invoker` SA doesn't have `roles/run.invoker` on the service.

**Fix:**
```bash
gcloud run services add-iam-policy-binding order-status --region us-east1 \
  --member "serviceAccount:scheduler-invoker@$(gcloud config get-value project).iam.gserviceaccount.com" \
  --role roles/run.invoker
```

**Cause #2:** The OIDC **audience** doesn't match the function URL.

**Fix:** The `--oidc-token-audience` must equal the function's base URL (`$URL`). Recreate the job
with the correct audience, or `gcloud scheduler jobs update http order-status-ping
--oidc-token-audience "$URL"`.

---

## Logs show my messages as plain text, not structured fields

**Cause:** You printed a bare string instead of a JSON object, or the JSON isn't valid on one line.

**Fix:** Emit a single-line JSON object with a `severity` key (see `_structured_log` in `main.py`).
Cloud Logging only parses valid one-line JSON on stdout/stderr into `jsonPayload`.

---

## `gcloud functions describe … serviceConfig.uri` is empty

**Cause:** You described a **1st-gen** function (omit `--gen2`) or the deploy hasn't finished.

**Fix:** Add `--gen2` and confirm `state: ACTIVE`:
```bash
gcloud functions describe order-status --gen2 --region us-east1 --format='value(state)'
```

---

## Deploy is slow / times out on the first run

**Cause:** The very first build in a new project provisions the build/artifacts backend.

**Fix:** This is normal — first deploys take 1–2 minutes. If it exceeds ~5 minutes, check
`gcloud builds list` for a stuck build and re-run the deploy.
