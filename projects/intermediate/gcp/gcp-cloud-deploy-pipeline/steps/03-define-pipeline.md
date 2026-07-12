# Step 3 — Define the Delivery Pipeline & Targets

Now you declare **what** the pipeline is (the promotion path) and **where** it deploys (the targets),
then register it with Cloud Deploy. This is all in `deploy/clouddeploy.yaml`, with `deploy/skaffold.yaml`
and the two `service-*.yaml` manifests describing **how** each stage renders.

---

## 3.1 Read the Pipeline Definition

Open `deploy/clouddeploy.yaml`. It has three documents (separated by `---`):

1. **DeliveryPipeline `meridian-web-pipeline`** — a `serialPipeline` with two stages: `staging` then
   `prod`. Each stage names a **target** and the **Skaffold profile** that renders it.
2. **Target `staging`** — a Cloud Run location. Deploys happen automatically.
3. **Target `prod`** — the same Cloud Run location, but with **`requireApproval: true`** so its
   rollout pauses until a human approves.

```yaml
serialPipeline:
  stages:
    - targetId: staging
      profiles: [staging]
    - targetId: prod
      profiles: [prod]
```

> **Why two services in one project?** In production, staging and prod are usually separate projects
> or regions. To keep this lab single-project and cheap, both targets point at the same Cloud Run
> location and differ by **service name** (`meridian-web-staging` vs `meridian-web-prod`), selected
> by the Skaffold profile. The pipeline mechanics are identical either way.

---

## 3.2 Read the Skaffold + Manifest Files

- `deploy/skaffold.yaml` uses `deploy.cloudrun: {}` and defines a **profile per target**; each profile
  points at that stage's manifest (`service-staging.yaml` / `service-prod.yaml`).
- `deploy/service-staging.yaml` and `deploy/service-prod.yaml` are **Cloud Run (Knative) Service**
  manifests. Both use `image: meridian-web` as a **placeholder** — Cloud Deploy replaces it with the
  real image you pass at release time (Step 4). They differ only in service name and `TARGET`/greeting
  env vars, proving the *same image* runs in both with per-stage config.

---

## 3.3 Substitute Your Project ID

The targets reference the Cloud Run location as `projects/PROJECT_ID/locations/us-east1`. Replace the
placeholder with your real project ID:

```bash
cd deploy
sed -i.bak "s/PROJECT_ID/${PROJECT_ID}/g" clouddeploy.yaml
grep 'locations/' clouddeploy.yaml   # confirm your real project ID is now present
```

> On macOS `sed -i.bak` writes a `clouddeploy.yaml.bak` backup — delete it if you like. (BSD `sed`
> requires the `.bak` suffix argument, which is why it's there.)

---

## 3.4 Register the Pipeline & Targets

`gcloud deploy apply` reads the YAML and creates/updates the pipeline and targets:

```bash
gcloud deploy apply --file=clouddeploy.yaml --region="$REGION"
cd ..
```

Confirm they exist:

```bash
gcloud deploy delivery-pipelines describe meridian-web-pipeline --region="$REGION" \
  --format='value(name)'
gcloud deploy targets list --region="$REGION" --format='table(targetId,requireApproval)'
```

You should see the pipeline and two targets, with `prod` showing `requireApproval: True`.

> **Console:** **Cloud Deploy → Delivery pipelines → meridian-web-pipeline** shows a visual
> staging → prod graph. It's empty of releases until Step 4.

---

## Checkpoint

- [ ] `PROJECT_ID` substituted into `clouddeploy.yaml` (no literal `PROJECT_ID` left in `locations/`)
- [ ] `gcloud deploy apply` succeeded
- [ ] Pipeline `meridian-web-pipeline` and targets `staging`/`prod` exist
- [ ] `prod` target has `requireApproval: True`

---

**Next:** [Step 4 — Create a Release (Auto-Deploy to Staging)](./04-create-release.md)
