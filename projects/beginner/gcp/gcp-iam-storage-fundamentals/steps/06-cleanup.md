# Step 6 — Cleanup

Delete everything you created so nothing is left behind. The order here mirrors the theme of this
whole project: **data first, then identity** — delete the bucket (and the objects in it) before
deleting the service account that was granted access to it.

> Unlike VMs or load balancers, nothing in this project bills by the hour — a forgotten bucket with
> a few KB of text files costs fractions of a cent. Still, clean up: an unused service account with
> standing (if narrow) access is exactly the kind of thing a real security review flags.

---

## 6.1 Console — Delete in Order

1. **Bucket and its objects** (**Cloud Storage → Buckets**): select `meridian-docs-<PROJECT_ID>` →
   **Delete** → confirm by typing the bucket name. This deletes every object inside it along with
   the bucket-level IAM bindings you created in Step 4.
2. **Service account** (**IAM & Admin → Service Accounts**): select `doc-portal-sa` → **Delete**.
   This also removes the `serviceAccountTokenCreator` binding you granted yourself on it in Step 2 —
   that binding lived *on* the SA, so it can't outlive it.

---

## 6.2 gcloud CLI (Alternative)

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export BUCKET="meridian-docs-${PROJECT_ID}"
export SA_EMAIL="doc-portal-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# 1. Delete the bucket and every object in it
gcloud storage rm --recursive "gs://${BUCKET}" --quiet

# 2. Delete the service account
gcloud iam service-accounts delete "${SA_EMAIL}" --quiet
```

> **Nothing left at the project level.** Because every grant in this project was scoped to the
> bucket or the service account itself (Steps 2 and 4 deliberately avoided
> `gcloud projects add-iam-policy-binding`), deleting these two resources removes every binding you
> created — there's no leftover project-level IAM policy to clean up separately. That's the payoff
> of scoping narrowly from the start.

---

## 6.3 Verify Nothing Is Left

```bash
gcloud storage buckets list --filter="name:meridian-docs"   # should be empty
gcloud iam service-accounts list --filter="email:doc-portal-sa"  # should be empty
```

If bucket deletion fails with an error about objects still present, see
[troubleshooting.md](../troubleshooting.md) — `gcloud storage rm --recursive` should handle it, but
a partially-uploaded object or a retention lock can occasionally need a second pass.

> **Keeping the project?** You'll reuse the same gcloud install, login, project, and billing in the
> [next project in this series](../../../../intermediate/gcp/gcp-storage-security-lifecycle/README.md).
> Only the bucket and service account above need deleting.

---

## Checkpoint

- [ ] `gcloud storage buckets list` no longer shows `meridian-docs-<PROJECT_ID>`
- [ ] `gcloud iam service-accounts list` no longer shows `doc-portal-sa`
- [ ] No bucket-level or service-account-level bindings remain (they were deleted along with their
      resources)

🎉 **You've built a least-privilege identity and storage model from scratch.** You now understand
IAM principals, policy bindings, service accounts, key-less impersonation, and how to read an audit
log — the foundation for the rest of the
[GCP IAM, Storage & Databases series](../../../../intermediate/gcp/gcp-storage-security-lifecycle/README.md).
