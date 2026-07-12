# Step 5 — Promote to Prod (Approval) & Roll Back

Staging looks good. Now you'll **promote** the release toward prod — which pauses at the **approval
gate** you configured — approve it, verify prod, then practice a **rollback**. This is the payoff:
the same tested image reaches prod through a controlled, auditable gate.

---

## 5.1 Promote the Release

Promotion advances the release to the next stage in the pipeline (`staging → prod`):

```bash
gcloud deploy releases promote \
  --release=rel-001 \
  --delivery-pipeline=meridian-web-pipeline \
  --region="$REGION"
```

Because the `prod` target has `requireApproval: true`, the prod rollout is created in a
**PENDING_APPROVAL** state — it does **not** deploy yet.

```bash
gcloud deploy rollouts list \
  --delivery-pipeline=meridian-web-pipeline \
  --release=rel-001 --region="$REGION" \
  --format='table(name.basename(),targetId,state)'
# prod rollout → PENDING_APPROVAL
```

---

## 5.2 Approve the Prod Rollout

Grab the pending prod rollout's name and approve it:

```bash
ROLLOUT="$(gcloud deploy rollouts list \
  --delivery-pipeline=meridian-web-pipeline --release=rel-001 --region="$REGION" \
  --filter='targetId=prod' --format='value(name.basename())')"
echo "$ROLLOUT"

gcloud deploy rollouts approve "$ROLLOUT" \
  --release=rel-001 \
  --delivery-pipeline=meridian-web-pipeline \
  --region="$REGION"
```

> **Console:** the pipeline graph shows an **Approve** button on the prod stage — clicking it does
> the same thing. In a real org, only people with `roles/clouddeploy.approver` can approve, which is
> how you separate "who can deploy to staging" from "who can release to prod."

After approval the prod rollout proceeds. Watch it reach `SUCCEEDED`:

```bash
gcloud deploy rollouts list \
  --delivery-pipeline=meridian-web-pipeline --release=rel-001 --region="$REGION" \
  --format='table(targetId,state)'
```

---

## 5.3 Test the Prod Service

```bash
gcloud run services add-iam-policy-binding meridian-web-prod \
  --region="$REGION" --member=allUsers --role=roles/run.invoker

PRD_URL="$(gcloud run services describe meridian-web-prod \
  --region="$REGION" --format='value(status.url)')"
curl -s "$PRD_URL/"
# → {"message":"Meridian Retail","target":"prod","version":"1.0","revision":"..."}
```

Note `target: prod` and the greeting without the "STAGING" suffix — same image, different per-target
config. Staging and prod now both run the **identical** `meridian-web@sha256:...` you built once.

---

## 5.4 Ship a v2, Then Roll Back

Let's simulate a bad release and recover. Build a v2 image and cut a second release:

```bash
# (Optional) change src/app.py's default greeting to see a difference, then:
cd src && gcloud builds submit --tag "${IMAGE_PATH}:v2" . && cd ..
IMAGE_V2="$(gcloud artifacts docker images describe "${IMAGE_PATH}:v2" \
  --format='value(image_summary.fully_qualified_digest)')"

cd deploy
gcloud deploy releases create rel-002 \
  --delivery-pipeline=meridian-web-pipeline --region="$REGION" \
  --skaffold-file=skaffold.yaml --images="meridian-web=${IMAGE_V2}"
cd ..

# Promote rel-002 to prod and approve it (as in 5.1–5.2)…
gcloud deploy releases promote --release=rel-002 \
  --delivery-pipeline=meridian-web-pipeline --region="$REGION"
```

Suppose rel-002 is bad. **Roll back prod** to the previous good release — Cloud Deploy creates a new
rollout that redeploys `rel-001` to prod:

```bash
gcloud deploy targets rollback prod \
  --delivery-pipeline=meridian-web-pipeline \
  --region="$REGION"
```

This prompts for the release to roll back to (defaults to the previous one, `rel-001`) and, because
prod requires approval, you approve the rollback rollout the same way as in 5.2. Verify prod is back:

```bash
curl -s "$PRD_URL/" | grep -o '"version":"[^"]*"'
```

> **Why this is powerful:** rollback isn't a rebuild or a manual `gcloud run deploy` — it's a
> first-class pipeline action with the same approval gate and audit trail as a forward deploy.

---

## Checkpoint

- [ ] Promotion created a **PENDING_APPROVAL** prod rollout
- [ ] You approved it and the prod rollout reached `SUCCEEDED`
- [ ] `curl "$PRD_URL/"` returns `target: prod`
- [ ] You created a second release and **rolled prod back** to the previous release

---

**Next:** [Step 6 — Cleanup](./06-cleanup.md)
