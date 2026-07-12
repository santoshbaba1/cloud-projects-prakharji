# Troubleshooting — GCP Cloud Run & Artifact Registry

Error → Cause → Fix. Most first-time issues are a missing API, a wrong image path, or the container
not listening on `$PORT`.

---

## `gcloud builds submit` fails with `PERMISSION_DENIED` / API not enabled

**Cause:** The Cloud Build or Artifact Registry API isn't enabled, or your account lacks build
permissions.

**Fix:** Re-run the Step 1 enable command and confirm your role:
```bash
gcloud services enable cloudbuild.googleapis.com artifactregistry.googleapis.com run.googleapis.com
gcloud projects get-iam-policy "$PROJECT_ID" --flatten='bindings[].members' \
  --filter="bindings.members:$(gcloud config get-value account)" --format='value(bindings.role)'
```
You need at least `roles/cloudbuild.builds.editor` (Owner/Editor covers it).

---

## Build fails: `denied: Permission "artifactregistry.repositories.uploadArtifacts" denied`

**Cause:** The **Cloud Build service account** can't push to Artifact Registry. On projects created
before Artifact Registry was default, the build SA may lack the writer role.

**Fix:** Grant the Cloud Build service account the Artifact Registry writer role:
```bash
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

---

## Build fails: `repository ... not found`

**Cause:** You're pushing to a repo that doesn't exist, or the region in the image path doesn't match
the repo's region.

**Fix:** Confirm the repo and that `IMAGE_PATH` uses the same region:
```bash
gcloud artifacts repositories list --location us-east1
echo "$IMAGE_PATH"   # must start us-east1-docker.pkg.dev/<PROJECT_ID>/meridian-apps/
```

---

## Cloud Run deploy fails: `The user-provided container failed to start and listen on the port`

**Cause #1:** The app isn't listening on `$PORT` (8080). Cloud Run health-checks the port and fails
the deploy if nothing answers.

**Fix:** The provided `Dockerfile` binds gunicorn to `$PORT` — don't hard-code a different port. If
you changed `app.py`, ensure it reads `PORT`:
```python
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
```

**Cause #2:** The container crashed on startup (bad import, syntax error).

**Fix:** Read the logs:
```bash
gcloud run services logs read meridian-web --region us-east1 --limit 50
```

---

## `curl "$URL/"` returns `403 Forbidden`

**Cause:** The service is **private** — you deployed without `--allow-unauthenticated`.

**Fix:** Either make it public, or call it with an identity token:
```bash
# Make public:
gcloud run services add-iam-policy-binding meridian-web --region us-east1 \
  --member=allUsers --role=roles/run.invoker
# Or call privately:
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$URL/"
```

---

## The new revision didn't get any traffic

**Cause:** You deployed with `--no-traffic` (Step 5.3) — that's intentional; the new revision is
reachable only via its tagged URL until you shift traffic.

**Fix:** Shift traffic explicitly:
```bash
gcloud run services update-traffic meridian-web --region us-east1 --to-latest
```

---

## Traffic split looks stuck on one revision

**Cause:** Connection reuse / small sample — a handful of `curl`s may stick to one backend.

**Fix:** Make many fresh requests and check the config, not just the responses:
```bash
for i in $(seq 1 20); do curl -s "$URL/" | grep -o '"version":"[^"]*"'; done
gcloud run services describe meridian-web --region us-east1 \
  --format='value(status.traffic)'
```

---

## Cleanup: images won't delete (`still referenced`)

**Cause:** A Cloud Run revision still references the image tag.

**Fix:** Delete the **service** first (removes all revisions), then the images:
```bash
gcloud run services delete meridian-web --region us-east1 --quiet
gcloud artifacts repositories delete meridian-apps --location us-east1 --quiet
```
