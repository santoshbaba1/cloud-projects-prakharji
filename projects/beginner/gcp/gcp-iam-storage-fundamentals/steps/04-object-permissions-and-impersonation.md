# Step 4 — Object Permissions & Impersonation

The bucket exists but `doc-portal-sa` still can't touch it — Step 2 deliberately left it roleless.
This step uploads a couple of real objects, grants the SA a **bucket-scoped** role, and then proves
that scoping works by accessing the bucket **as the service account** — with no downloaded key.

---

## 4.1 Upload a Couple of Documents

### Console

1. Open the `meridian-docs-<PROJECT_ID>` bucket → **Upload → Upload files**.
2. Upload any small file from your machine (a `.txt` or `.pdf` works fine).

### gcloud CLI (Alternative)

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export BUCKET="meridian-docs-${PROJECT_ID}"

# Create two small sample documents locally
echo "Meridian Retail — Employee Handbook (draft)" > handbook.txt
echo "Meridian Retail — Q3 Vendor Contract (confidential)" > vendor-contract.txt

# Upload both
gcloud storage cp handbook.txt vendor-contract.txt "gs://${BUCKET}/"
```

Verify:

```bash
gcloud storage ls "gs://${BUCKET}"
```

---

## 4.2 Grant `doc-portal-sa` a Bucket-Scoped Role

The portal needs to read and write documents, but has no business creating or deleting the *bucket*
itself, and no business touching any other bucket in the project. `roles/storage.objectAdmin`,
granted **on this one bucket**, is exactly that shape of access.

### Console

1. Open the `meridian-docs-<PROJECT_ID>` bucket → **Permissions** tab → **Grant Access**.
2. New principal: `doc-portal-sa@<PROJECT_ID>.iam.gserviceaccount.com`.
3. Role: **Storage Object Admin**.
4. Click **Save**.

### gcloud CLI

```bash
export SA_EMAIL="doc-portal-sa@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud storage buckets add-iam-policy-binding "gs://${BUCKET}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.objectAdmin"
```

Verify:

```bash
gcloud storage buckets get-iam-policy "gs://${BUCKET}"
```

You should see one binding: `roles/storage.objectAdmin` → `serviceAccount:doc-portal-sa@...`. Notice
this binding lives on the **bucket**, not the project — `gcloud projects get-iam-policy
"${PROJECT_ID}"` would **not** show it.

---

## 4.3 Why Key-less Impersonation Instead of a Downloaded Key

The traditional way to let code "be" a service account is `gcloud iam service-accounts keys create`
— which writes a **JSON key file** containing long-lived credentials to disk. That file:

- Never expires on its own (it must be manually revoked)
- Can be copied, committed to a repo, or leaked exactly like a password
- Grants everything the SA can do to whoever holds the file, indefinitely

**Impersonation** is the modern alternative: instead of a static file, gcloud asks Google's IAM
Credentials API for a **short-lived token** (typically valid ~1 hour), minted on the spot using
*your own* authenticated identity plus the `roles/iam.serviceAccountTokenCreator` binding from
Step 2.5. Nothing is written to disk, nothing to leak, and the access disappears the moment the
token expires or your Token Creator grant is revoked.

> **Requirement:** impersonation only works if the caller holds `roles/iam.serviceAccountTokenCreator`
> **on that specific service account** — exactly the binding you set up in Step 2.5. Without it,
> gcloud returns `PERMISSION_DENIED` for `iam.serviceAccounts.getAccessToken` (see
> [troubleshooting.md](../troubleshooting.md)).

---

## 4.4 gcloud CLI — Access the Bucket *As* the Service Account

```bash
# List the bucket's contents, acting as doc-portal-sa instead of yourself
gcloud storage ls "gs://${BUCKET}" \
  --impersonate-service-account="${SA_EMAIL}"

# Upload a new file as the SA — proves objectAdmin allows writes
echo "Meridian Retail — Onboarding Guide" > onboarding.txt
gcloud storage cp onboarding.txt "gs://${BUCKET}/" \
  --impersonate-service-account="${SA_EMAIL}"

# Download a file as the SA — proves objectAdmin allows reads
gcloud storage cp "gs://${BUCKET}/handbook.txt" ./handbook-downloaded.txt \
  --impersonate-service-account="${SA_EMAIL}"
```

All three should succeed. Now prove the scoping actually holds — try something `objectAdmin` does
**not** grant:

```bash
# Try to delete the BUCKET itself (not just an object) as the SA
gcloud storage buckets delete "gs://${BUCKET}" \
  --impersonate-service-account="${SA_EMAIL}"
```

This should fail with `PERMISSION_DENIED` — `roles/storage.objectAdmin` covers objects, not bucket
lifecycle. That failure is the least-privilege model working exactly as designed.

---

## 4.5 Why Impersonation > Keys Here

- **No credential to leak.** There's no file on any laptop, in any repo, or in any CI secret store
  that grants standing access to `doc-portal-sa`.
- **Access is auditable and revocable at the source.** Removing your `serviceAccountTokenCreator`
  binding instantly stops anyone from impersonating the SA through you — no key rotation, no hunting
  for copies of a file.
- **The failure you just saw is a feature.** `doc-portal-sa` can serve the document portal's real
  workload (read/write objects) and structurally cannot do the one thing that would be catastrophic
  if it were ever compromised: destroy the bucket.

---

## Checkpoint

- [ ] At least one object exists in `meridian-docs-<PROJECT_ID>`
- [ ] `doc-portal-sa` holds `roles/storage.objectAdmin` **on the bucket** (not the project)
- [ ] `gcloud storage ls`/`cp` succeed with `--impersonate-service-account`
- [ ] `gcloud storage buckets delete --impersonate-service-account` **fails** with `PERMISSION_DENIED`
- [ ] You can explain why impersonation avoids the risks of a downloaded key

---

**Next:** [Step 5 — Audit & Least-Privilege Review](./05-audit-and-least-privilege-review.md)
