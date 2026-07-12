# Step 1 — Setup & IAM for Cloud Deploy

Cloud Deploy orchestrates deployments **on your behalf** — it renders manifests, calls Cloud Run, and
runs jobs using a **service account**. So this step does two things: enable the APIs, and give the
execution service account the roles it needs. Getting IAM right now saves you a confusing
`PERMISSION_DENIED` mid-rollout.

> **Prerequisite:** You've done the
> [beginner Cloud Run project](../../../../beginner/gcp/gcp-cloud-run-artifact-registry/README.md), so
> gcloud is authenticated, billing is linked, and you're comfortable with the image path
> `us-east1-docker.pkg.dev/PROJECT/meridian-apps/meridian-web`.

---

## 1.1 Set Project & Region Variables

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export REGION=us-east1
export PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
echo "$PROJECT_ID / $PROJECT_NUMBER / $REGION"
```

Set the Cloud Deploy default region so you can omit `--region`:

```bash
gcloud config set deploy/region "$REGION"
```

---

## 1.2 Enable the APIs

You need Cloud Deploy on top of the three from the beginner project:

### Console

**APIs & Services → Enable APIs and Services** → enable **Cloud Deploy API** (the others —
Cloud Build, Artifact Registry, Cloud Run — are already on from the beginner project).

### gcloud CLI (Alternative)

```bash
gcloud services enable \
  clouddeploy.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com
```

---

## 1.3 Understand Who Acts (the Execution Service Account)

Cloud Deploy runs its render and deploy work as an **execution service account**. By default that's
the **Compute Engine default service account**:

```
PROJECT_NUMBER-compute@developer.gserviceaccount.com
```

That account must be allowed to:

| Role | Why it's needed |
|------|-----------------|
| `roles/clouddeploy.jobRunner` | Lets Cloud Deploy run its render/deploy **jobs** as this SA |
| `roles/run.developer` | Deploy and update **Cloud Run** services (the targets) |
| `roles/iam.serviceAccountUser` | **actAs** the Cloud Run runtime SA when creating a service |

> **Why the split?** `jobRunner` lets the pipeline *use* the SA for its internal jobs; `run.developer`
> lets that SA *change Cloud Run*; `serviceAccountUser` is required because deploying a Cloud Run
> service means assigning it a runtime identity, and IAM makes you prove you're allowed to "act as"
> that identity. Least privilege = grant exactly these three, not Editor.

---

## 1.4 Grant the Roles

```bash
EXEC_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${EXEC_SA}" \
  --role="roles/clouddeploy.jobRunner"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${EXEC_SA}" \
  --role="roles/run.developer"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${EXEC_SA}" \
  --role="roles/iam.serviceAccountUser"
```

> **Newer projects:** Google may create a dedicated Compute Engine default SA only after Compute is
> used. If `${PROJECT_NUMBER}-compute@...` doesn't exist, create a purpose-built SA (e.g.
> `clouddeploy-exec`) instead and grant it the same three roles, then pass
> `--execution-service-account` when you apply the pipeline. For this lab the default SA is simplest.

---

## 1.5 Verify

```bash
gcloud projects get-iam-policy "$PROJECT_ID" \
  --flatten='bindings[].members' \
  --filter="bindings.members:${EXEC_SA}" \
  --format='table(bindings.role)'
```

You should see `clouddeploy.jobRunner`, `run.developer`, and `iam.serviceAccountUser` in the list.

---

## Checkpoint

- [ ] `PROJECT_ID`, `PROJECT_NUMBER`, and `REGION` are exported
- [ ] Cloud Deploy API (plus Build/Run/Artifact Registry) enabled
- [ ] Default deploy region set to `us-east1`
- [ ] Execution SA has `clouddeploy.jobRunner`, `run.developer`, `iam.serviceAccountUser`

---

**Next:** [Step 2 — Build the Image Once](./02-build-image.md)
