# Step 6 — Cleanup

Everything here is free-tier, but a deployed function, its Cloud Run service, and a Scheduler job all
keep *existing* until you delete them. Tear down in reverse order of creation.

---

## 6.1 Delete the Scheduler Job

```bash
gcloud scheduler jobs delete order-status-ping --location us-east1 --quiet
```

---

## 6.2 Delete the Function

Deleting the 2nd-gen function also removes the underlying **Cloud Run service** and its revisions:

```bash
gcloud functions delete order-status --gen2 --region us-east1 --quiet
```

Verify nothing is left:

```bash
gcloud functions list --regions us-east1
gcloud run services list --region us-east1
```

Both should no longer list `order-status`.

---

## 6.3 Delete the Invoker Service Account (optional)

```bash
export PROJECT_ID="$(gcloud config get-value project)"
gcloud iam service-accounts delete \
  "scheduler-invoker@${PROJECT_ID}.iam.gserviceaccount.com" --quiet
```

---

## 6.4 Remove the Built Images (optional)

Buildpacks stored your image in an auto-created Artifact Registry repo. It's tiny and inside the free
tier, but to be thorough:

```bash
gcloud artifacts repositories list --location us-east1
# Delete the functions artifacts repo if present (name is usually 'gcf-artifacts'):
gcloud artifacts repositories delete gcf-artifacts --location us-east1 --quiet
```

---

## 6.5 (Optional) Disable APIs

If this was a throwaway project you can disable the APIs so nothing can accrue later:

```bash
gcloud services disable cloudscheduler.googleapis.com --force
gcloud services disable cloudfunctions.googleapis.com --force
# Leave run/build enabled if you'll do the next project in the same project.
```

> If you created a **dedicated project** for this lab, the cleanest option of all is to delete the
> whole project: `gcloud projects delete "$PROJECT_ID"`.

---

## Checkpoint

- [ ] `gcloud scheduler jobs list --location us-east1` is empty
- [ ] `gcloud functions list` no longer shows `order-status`
- [ ] `gcloud run services list --region us-east1` no longer shows `order-status`
- [ ] (Optional) the invoker SA and artifacts repo are gone

---

**Done.** You deployed, configured, observed, and scheduled a serverless function. Next up:
[GCP Event-Driven Functions with Pub/Sub](../../../../intermediate/gcp/gcp-event-driven-functions-pubsub/README.md)
— functions that fire from **events** instead of HTTP.
