# Step 6 — Cleanup

This lab stays inside the free tier, but a deployed **service**, stored **images**, and the
**repository** still exist. Delete them so nothing lingers. Order doesn't strictly matter here (Cloud
Run doesn't depend on the repo once deployed), but do the service first, then the images/repo.

---

## 6.1 Delete the Cloud Run Service

Deleting the service removes **all** its revisions and the public URL.

### gcloud CLI

```bash
gcloud run services delete meridian-web --region us-east1 --quiet
```

### Console

**Cloud Run** → select **meridian-web** → **Delete**.

Confirm it's gone:

```bash
gcloud run services list --region us-east1
```

---

## 6.2 Delete the Images (or the Whole Repo)

You can delete individual image tags, or just delete the repository (which removes everything in it).

**Delete individual tags:**

```bash
gcloud artifacts docker images delete "${IMAGE_PATH}:v1" --delete-tags --quiet
gcloud artifacts docker images delete "${IMAGE_PATH}:v2" --delete-tags --quiet
```

**Or delete the whole repository** (simplest — removes all images at once):

```bash
gcloud artifacts repositories delete meridian-apps --location us-east1 --quiet
```

> If you plan to do the [intermediate Cloud Deploy project](../../../../intermediate/gcp/gcp-cloud-deploy-pipeline/README.md)
> next, you can **keep the `meridian-apps` repository** — that project reuses it. Just delete the
> Cloud Run service (6.1) to stop everything you don't need.

---

## 6.3 (Optional) Clean Up Build Artifacts

Cloud Build stores source tarballs and logs in an auto-created bucket
(`PROJECT_ID_cloudbuild` / `gs://run-sources-...`). These are tiny and free at this scale, but if you
want a spotless project:

```bash
gcloud builds list --limit 5 --format='value(id)'   # just to see them
# The staging bucket (safe to empty):
gsutil ls
# gsutil rm -r gs://YOUR_PROJECT_ID_cloudbuild   # only if you're sure
```

Leaving these is fine — they don't accrue meaningful cost.

---

## 6.4 Verify Nothing's Left

```bash
gcloud run services list --region us-east1                       # empty (or no meridian-web)
gcloud artifacts repositories list --location us-east1           # meridian-apps gone (if deleted)
```

---

## Checkpoint

- [ ] `meridian-web` Cloud Run service deleted
- [ ] Images/repository deleted (or repo intentionally kept for the next project)
- [ ] `gcloud run services list` no longer shows `meridian-web`

---

**You're done!** You built a container with Cloud Build, stored it in Artifact Registry, ran it on
Cloud Run, and shipped a new version with a traffic-split rollback.

**Next up:** [GCP Cloud Deploy Pipeline](../../../../intermediate/gcp/gcp-cloud-deploy-pipeline/README.md) —
promote this same image through **staging → prod** with an approval gate and one-command rollback.
