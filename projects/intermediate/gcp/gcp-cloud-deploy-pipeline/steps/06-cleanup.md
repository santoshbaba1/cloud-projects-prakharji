# Step 6 — Cleanup

The **delivery pipeline carries a small per-day charge**, so deleting it is the cost-critical part of
this step — do it even if you leave everything else. Then remove the two Cloud Run services and the
images.

---

## 6.1 Delete the Delivery Pipeline (Cost-Critical)

Deleting the pipeline with `--force` also removes its releases, rollouts, and targets:

```bash
gcloud deploy delivery-pipelines delete meridian-web-pipeline \
  --region="$REGION" --force --quiet
```

Confirm it's gone:

```bash
gcloud deploy delivery-pipelines list --region="$REGION"
```

> If you created the targets separately or `--force` leaves any behind, delete them explicitly:
> `gcloud deploy targets delete staging --region="$REGION" --quiet` (and `prod`).

---

## 6.2 Delete the Cloud Run Services

```bash
gcloud run services delete meridian-web-staging --region="$REGION" --quiet
gcloud run services delete meridian-web-prod --region="$REGION" --quiet
```

Confirm:

```bash
gcloud run services list --region="$REGION" | grep meridian-web || echo "none left"
```

---

## 6.3 Delete the Images / Repository

If you're **not** keeping `meridian-apps` for other work, delete the whole repo:

```bash
gcloud artifacts repositories delete meridian-apps --location="$REGION" --quiet
```

Or remove just the tags you created:

```bash
gcloud artifacts docker images delete "${IMAGE_PATH}:v1" --delete-tags --quiet
gcloud artifacts docker images delete "${IMAGE_PATH}:v2" --delete-tags --quiet
```

---

## 6.4 (Optional) Revoke the IAM Grants

If this was a throwaway project you can leave the role bindings; if you want to undo Step 1's grants:

```bash
EXEC_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
for ROLE in roles/clouddeploy.jobRunner roles/run.developer roles/iam.serviceAccountUser; do
  gcloud projects remove-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${EXEC_SA}" --role="$ROLE" --quiet
done
```

> Leave these if you plan to redo the lab — they're harmless and grant no standing access to
> resources you've deleted.

---

## 6.5 Verify Nothing's Left

```bash
gcloud deploy delivery-pipelines list --region="$REGION"    # empty
gcloud run services list --region="$REGION" | grep meridian-web || echo "no services"
gcloud artifacts repositories list --location="$REGION"      # meridian-apps gone (if deleted)
```

---

## Checkpoint

- [ ] Delivery pipeline `meridian-web-pipeline` deleted (stops the per-day charge)
- [ ] Both Cloud Run services deleted
- [ ] Images/repository deleted (or intentionally kept)
- [ ] (Optional) IAM grants revoked

---

**You're done!** You built an image once, promoted it through **staging → prod** with an approval
gate, and rolled it back — a real continuous-delivery pipeline on **Cloud Deploy**.

**Related:** Compare this managed-CD approach to the native deployment strategies in the
[AWS API Gateway Series](../../../../intermediate/aws/aws-api-gateway-rest-lambda/README.md).
