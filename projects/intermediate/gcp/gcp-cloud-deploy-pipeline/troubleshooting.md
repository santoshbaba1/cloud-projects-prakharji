# Troubleshooting — GCP Cloud Deploy Pipeline

Error → Cause → Fix. Most pipeline failures are an **IAM** gap on the execution service account or a
mismatch between the `--images` key and the manifest placeholder.

---

## `gcloud deploy apply` fails: `Permission 'clouddeploy.deliveryPipelines.create' denied`

**Cause:** Your **user** account lacks Cloud Deploy admin permission (this is separate from the
*execution* SA roles).

**Fix:** Grant yourself the admin role (Owner/Editor also covers it):
```bash
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="user:$(gcloud config get-value account)" \
  --role="roles/clouddeploy.admin"
```

---

## Staging rollout fails immediately in `render` or `deploy`

**Cause:** The **execution service account** is missing a role — the most common setup mistake.

**Fix:** Re-check Step 1's grants on `PROJECT_NUMBER-compute@developer.gserviceaccount.com`:
```bash
EXEC_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
gcloud projects get-iam-policy "$PROJECT_ID" --flatten='bindings[].members' \
  --filter="bindings.members:${EXEC_SA}" --format='table(bindings.role)'
```
It must include `clouddeploy.jobRunner`, `run.developer`, and `iam.serviceAccountUser`. Inspect the
failed rollout's job for the exact denied permission:
```bash
gcloud deploy rollouts describe <ROLLOUT> --release=rel-001 \
  --delivery-pipeline=meridian-web-pipeline --region="$REGION"
```

---

## Rollout fails: `iam.serviceaccounts.actAs` denied

**Cause:** Deploying a Cloud Run service assigns it a runtime identity; the execution SA needs to
"act as" it. Missing `roles/iam.serviceAccountUser`.

**Fix:**
```bash
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

---

## Release fails: `image "meridian-web" not found` / placeholder not replaced

**Cause:** The `--images` key doesn't match the placeholder in the service manifests. The manifests
use `image: meridian-web`, so the flag must be `--images=meridian-web=<real image>`.

**Fix:** Match the key exactly:
```bash
gcloud deploy releases create rel-00X \
  --delivery-pipeline=meridian-web-pipeline --region="$REGION" \
  --skaffold-file=skaffold.yaml \
  --images="meridian-web=${IMAGE_PATH}:v1"
```

---

## `gcloud deploy apply` succeeds but the target region is wrong / `PROJECT_ID` literal remains

**Cause:** You forgot the `sed` substitution in Step 3.3, so the target's `run.location` still says
`projects/PROJECT_ID/...`.

**Fix:** Substitute and re-apply:
```bash
cd deploy
sed -i.bak "s/PROJECT_ID/${PROJECT_ID}/g" clouddeploy.yaml
gcloud deploy apply --file=clouddeploy.yaml --region="$REGION"
```

---

## Prod rollout is stuck / never deploys

**Cause:** Not a bug — the `prod` target has `requireApproval: true`, so the rollout sits in
`PENDING_APPROVAL` until approved.

**Fix:** Approve it (Step 5.2):
```bash
gcloud deploy rollouts approve <ROLLOUT> --release=rel-001 \
  --delivery-pipeline=meridian-web-pipeline --region="$REGION"
```

---

## `curl` to a service returns `403 Forbidden`

**Cause:** Cloud Deploy creates the Cloud Run service **private**. It doesn't add `allUsers`.

**Fix:** Grant public invoke for the lab (or call with an identity token):
```bash
gcloud run services add-iam-policy-binding meridian-web-staging \
  --region="$REGION" --member=allUsers --role=roles/run.invoker
```

---

## `skaffold` / render errors about apiVersion

**Cause:** The `skaffold/v4beta7` schema must match a version your Cloud Deploy render supports.

**Fix:** Cloud Deploy pins Skaffold versions over time. If render rejects the schema, bump the
`apiVersion` in `deploy/skaffold.yaml` to the current supported one (see the error message, which
names the expected version) and recreate the release.

---

## Cleanup: pipeline won't delete (`has child resources`)

**Cause:** Releases/rollouts still attached.

**Fix:** Use `--force` (removes children) as in Step 6.1:
```bash
gcloud deploy delivery-pipelines delete meridian-web-pipeline \
  --region="$REGION" --force --quiet
```
