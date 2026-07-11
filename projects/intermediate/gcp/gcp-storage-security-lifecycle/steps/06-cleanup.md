# Step 6 — Cleanup ⚠️

This project bills real (small) money while it runs — four buckets, a KMS key, and versioned objects
all cost something even when idle. Two of the protections you just built (**object versioning** and
the **retention policy**) exist specifically to make deletion harder, so cleanup here has more steps
than usual — follow the order below.

> Rough cost if left running: a few cents a day, dominated by the Cloud KMS key
> (see [costs.md](../costs.md)). Not scary, but there's no reason to pay it.

---

## 6.1 Remove the Retention Policy Before Deleting Its Bucket

The `meridian-retention-demo-<PROJECT_ID>` bucket still has an **unlocked** retention policy from
[Step 3](./03-retention-and-cmek-encryption.md). Remove the policy first, or the object inside it will
refuse to delete until the retention period naturally expires.

```bash
PROJECT_ID=$(gcloud config get-value project)

# 1. Remove the (unlocked) retention policy
gcloud storage buckets update "gs://meridian-retention-demo-$PROJECT_ID" --clear-retention-period

# 2. Now the test object can be deleted, and the bucket removed entirely
gcloud storage rm --recursive "gs://meridian-retention-demo-$PROJECT_ID"
```

> If you ever locked a retention policy in real usage (never do this in a lab), this step would be
> impossible — the bucket becomes permanent until every object naturally ages past its retention
> period. That's the entire point of `--locked`; there is no cleanup shortcut for it.

---

## 6.2 Delete All Object Versions, Then the Reports Bucket

`meridian-reports-<PROJECT_ID>` has **object versioning** on, so a normal delete only removes the
*live* version of each object — noncurrent versions silently remain and keep billing. Use
`--all-versions` to actually clear everything.

```bash
# Delete every version of every object, then the bucket itself
gcloud storage rm --recursive --all-versions "gs://meridian-reports-$PROJECT_ID"
```

`gcloud storage rm --recursive` on an empty bucket also removes the bucket itself — no separate
`buckets delete` call needed. If you'd rather delete objects and bucket as two explicit steps:

```bash
gcloud storage rm --all-versions "gs://meridian-reports-$PROJECT_ID/**"
gcloud storage buckets delete "gs://meridian-reports-$PROJECT_ID"
```

---

## 6.3 Delete the Product-Photos and Access-Logs Buckets

Neither bucket has versioning or retention, so this is a plain recursive delete:

```bash
gcloud storage rm --recursive "gs://meridian-product-photos-$PROJECT_ID"
gcloud storage rm --recursive "gs://meridian-access-logs-$PROJECT_ID"
```

---

## 6.4 Destroy the KMS Key Version

**Cloud KMS keyrings and keys cannot be deleted** — they're permanent namespaces by design, so a key
name can never be silently reused by someone else later. What you *can* do is schedule every key
**version** for destruction, which stops billing for that version and makes any data still encrypted
with it permanently unrecoverable (which is fine here — the reports bucket that used it is already
gone).

```bash
# List the key's versions
gcloud kms keys versions list --key=meridian-storage-key --keyring=meridian-keyring --location=us-east1

# Schedule version 1 for destruction (24-hour grace period before it's actually destroyed)
gcloud kms keys versions destroy 1 \
  --key=meridian-storage-key --keyring=meridian-keyring --location=us-east1
```

Verify it's scheduled:

```bash
gcloud kms keys versions describe 1 \
  --key=meridian-storage-key --keyring=meridian-keyring --location=us-east1 \
  --format='value(state)'
# Expected: DESTROY_SCHEDULED
```

> The empty keyring and key **object** remain forever in the project — that's expected and free. Only
> the key **version** (the actual cryptographic material) is destroyed, and only that incurs cost.

---

## 6.5 Delete the Custom Role and IAM Bindings

```bash
# Remove the conditional IAM binding first
gcloud projects remove-iam-policy-binding "$PROJECT_ID" \
  --member="user:YOUR_EMAIL@example.com" \
  --role="projects/$PROJECT_ID/roles/MeridianReportsUploader" \
  --condition="expression=resource.name.startsWith('projects/_/buckets/meridian-reports-$PROJECT_ID/objects/reports/2026/'),title=reports-2026-prefix-only,description=Only objects under reports/2026/ in the reports bucket"

# Remove the Token Creator grant on doc-portal-sa from Step 4
gcloud iam service-accounts remove-iam-policy-binding \
  "doc-portal-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --member="user:YOUR_EMAIL@example.com" \
  --role="roles/iam.serviceAccountTokenCreator"

# Delete the custom role itself (soft-delete; recoverable for ~7 days, then purged)
gcloud iam roles delete MeridianReportsUploader --project="$PROJECT_ID"
```

---

## 6.6 Console (Alternative)

Delete in this order:

1. **Cloud Storage → Buckets** → open `meridian-retention-demo-<PROJECT_ID>` → **Protection** tab →
   remove the retention policy → then delete the bucket.
2. **Cloud Storage → Buckets** → `meridian-reports-<PROJECT_ID>` → check **Show deleted data**
   (reveals noncurrent versions) → select all objects and versions → **Delete** → then delete the
   bucket.
3. **Cloud Storage → Buckets** → delete `meridian-product-photos-<PROJECT_ID>` and
   `meridian-access-logs-<PROJECT_ID>`.
4. **Security → Key Management** → `meridian-keyring` → `meridian-storage-key` → select the key
   version → **Destroy**.
5. **IAM & Admin → IAM** → remove your conditional binding on `MeridianReportsUploader`.
6. **IAM & Admin → Service Accounts** → `doc-portal-sa` → **Permissions** → remove your Token Creator
   binding.
7. **IAM & Admin → Roles** → select `Meridian Reports Uploader` → **Delete**.

---

## 6.7 Verify Nothing Is Left (and Still Billing)

```bash
gcloud storage buckets list --format='value(name)' | grep meridian   # empty
gcloud kms keys versions list --key=meridian-storage-key --keyring=meridian-keyring \
  --location=us-east1 --format='value(name,state)'                   # DESTROY_SCHEDULED or DESTROYED
gcloud iam roles list --project="$PROJECT_ID" --format='value(name)' | grep MeridianReportsUploader
  # empty once the ~7-day soft-delete purge completes; DELETED state until then
```

> **The two easiest things to forget:** noncurrent object **versions** in the reports bucket (a plain
> delete leaves them behind, still billing) and the **KMS key version** (keyrings/keys themselves
> can't be deleted, but leaving the version active costs a few cents a month forever if skipped).

---

## Checkpoint

- [ ] All four `meridian-*` buckets from this project are gone
- [ ] The retention-demo bucket's policy was cleared *before* deletion, not worked around
- [ ] The reports bucket's objects were deleted with `--all-versions`, not a plain delete
- [ ] The KMS key version is `DESTROY_SCHEDULED` or `DESTROYED`
- [ ] The conditional IAM binding, the Token Creator grant, and `MeridianReportsUploader` itself are
      all removed

🎉 **You took Meridian Retail's documents bucket from "exists" to "production-grade"**: least-privilege
custom roles scoped by IAM Conditions, automatic lifecycle tiering, retention guarantees, CMEK
encryption, keyless signed URLs, a properly public static site, and an access-logging trail — then
tore every bit of it down cleanly. Continue to
[Project 3 — Cloud SQL Managed Database](../../gcp-cloud-sql-managed-database/README.md) when you're
ready.
