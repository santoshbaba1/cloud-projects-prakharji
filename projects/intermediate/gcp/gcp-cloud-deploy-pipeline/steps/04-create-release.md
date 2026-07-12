# Step 4 — Create a Release (Auto-Deploy to Staging)

A **release** captures a specific set of rendered manifests + pinned images. Creating one kicks off a
**rollout to the first stage (`staging`) automatically**. This is where the pipeline comes alive.

---

## 4.1 Create the Release

Run the release command from the `deploy/` directory (so Skaffold finds `skaffold.yaml` and the
manifests). The `--images` flag maps the manifest placeholder `meridian-web` to the real image you
built in Step 2:

```bash
cd deploy

gcloud deploy releases create rel-001 \
  --delivery-pipeline=meridian-web-pipeline \
  --region="$REGION" \
  --skaffold-file=skaffold.yaml \
  --images="meridian-web=${IMAGE_V1}"

cd ..
```

- `rel-001` — the release name (must be unique per pipeline)
- `--images=meridian-web=…` — substitutes the placeholder in the service manifests with your digest
  (or use `${IMAGE_PATH}:v1` if you skipped the digest in Step 2.3)

Cloud Deploy renders the staging manifest and **starts a rollout to staging** immediately.

---

## 4.2 Watch the Staging Rollout

```bash
gcloud deploy rollouts list \
  --delivery-pipeline=meridian-web-pipeline \
  --release=rel-001 --region="$REGION" \
  --format='table(name.basename(),targetId,state)'
```

Wait until the staging rollout shows `SUCCEEDED` (usually 1–2 minutes). In the **Console**, the
pipeline graph fills the **staging** box green and shows the release riding on it.

> **Rollout vs. release:** the **release** is the artifact; a **rollout** is one deployment of it to
> one target. Right now there's one rollout (to staging). Promotion (Step 5) creates the prod rollout.

---

## 4.3 Test the Staging Service

Cloud Deploy created the `meridian-web-staging` Cloud Run service. It's private by default — grant
public access so you can curl it (staging services are often kept internal; we open it for the lab):

```bash
gcloud run services add-iam-policy-binding meridian-web-staging \
  --region="$REGION" --member=allUsers --role=roles/run.invoker

STG_URL="$(gcloud run services describe meridian-web-staging \
  --region="$REGION" --format='value(status.url)')"
curl -s "$STG_URL/"
# → {"message":"Meridian Retail — STAGING","target":"staging","version":"1.0","revision":"..."}
```

The `target: staging` in the response comes from the env var in `service-staging.yaml` — proof the
staging manifest rendered.

---

## 4.4 Confirm Prod Is NOT Deployed Yet

The pipeline is **serial** — prod doesn't get the release until you promote it. Verify prod has no
service yet:

```bash
gcloud run services list --region="$REGION" --format='table(SERVICE)' | grep meridian-web
# → only meridian-web-staging so far
```

---

## Checkpoint

- [ ] Release `rel-001` created successfully
- [ ] The **staging** rollout reached `SUCCEEDED`
- [ ] `curl "$STG_URL/"` returns `target: staging`
- [ ] `meridian-web-prod` does **not** exist yet (serial pipeline)

---

**Next:** [Step 5 — Promote to Prod (Approval) & Roll Back](./05-promote-and-rollback.md)
