# Troubleshooting — GCP Storage Security & Lifecycle

Error → Cause → Fix. Most problems here trace back to one missing IAM grant or one CEL syntax slip.

---

## Error: `Lifecycle rule condition never matches` (transitions never happen)

**Cause:** The lifecycle rule's matcher is more specific than it looks. A common mistake is chaining
`matchesStorageClass: ["STANDARD"]` on the Nearline→Coldline rule instead of `["NEARLINE"]` — the
condition then never matches any object, since nothing is ever in `STANDARD` *and* older than 90 days
in the way the rule expects.

**Fix:**
```bash
gcloud storage buckets describe gs://meridian-reports-<PROJECT_ID> \
  --format='value(lifecycle_config)'
```
Confirm each rule's `matchesStorageClass` matches the storage class objects will actually be *in* at
that point in their life — Rule 1 matches `STANDARD`, Rule 2 matches `NEARLINE`, not both matching
`STANDARD`. Also remember rules are evaluated roughly once every 24 hours — a correct rule still won't
show a transition instantly.

---

## Error: `Permission denied` on upload, only after enabling CMEK

**Cause:** The **GCS service agent** (`service-<PROJECT_NUMBER>@gs-project-accounts.iam.gserviceaccount.com`)
doesn't have `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the key. GCS uses its own service agent
to call KMS, not your credentials — this is easy to miss because every *other* permission in this
project is granted to a human or app identity, not to Google's own service agent.

**Fix:**
```bash
PROJECT_NUMBER=$(gcloud projects describe <PROJECT_ID> --format='value(projectNumber)')
gcloud kms keys add-iam-policy-binding meridian-storage-key \
  --keyring=meridian-keyring --location=us-east1 \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gs-project-accounts.iam.gserviceaccount.com" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"
```
If the service account doesn't exist yet, perform any operation on any bucket in the project first
(e.g. `gcloud storage ls`) to force GCS to lazily provision it, then retry the grant.

---

## Error: Signed URL returns `SignatureDoesNotMatch` or `403`

**Cause:** Either the URL expired (past its `--duration`), the object path in the URL doesn't
byte-for-byte match the object you signed for, or the URL was copy-pasted with encoding altered (e.g.
a chat client stripped `%2F`).

**Fix:** Regenerate the URL and copy it as one unbroken string, or test with `curl -sI` instead of a
browser to rule out client-side URL mangling:
```bash
curl -sI "<signed-url>" | head -1
```
If it's simply expired, generate a new one — signed URLs cannot be renewed, only reissued.

---

## Error: `Permission 'iam.serviceAccounts.signBlob' denied` during keyless signing

**Cause:** Your user (or the identity running `gcloud storage sign-url`) doesn't have
`roles/iam.serviceAccountTokenCreator` on the **specific service account** being impersonated — this
role must be granted on the service account resource itself, not at the project level, and a project-level
grant of a different role does not imply it.

**Fix:**
```bash
gcloud iam service-accounts add-iam-policy-binding \
  doc-portal-sa@<PROJECT_ID>.iam.gserviceaccount.com \
  --member="user:YOUR_EMAIL@example.com" \
  --role="roles/iam.serviceAccountTokenCreator"
```
Confirm with:
```bash
gcloud iam service-accounts get-iam-policy doc-portal-sa@<PROJECT_ID>.iam.gserviceaccount.com
```

---

## Error: `Object ... is subject to bucket's retention policy` when deleting

**This is by design, not a bug.** The object hasn't reached the minimum retention age yet — the
policy is doing exactly what it's supposed to. There is no `--force` flag that overrides an active
retention period; that guarantee is the entire point of the feature.

**Fix:** Either wait for the retention period to elapse, or (only for an **unlocked** policy, like the
one in this lab) shorten or clear the policy first:
```bash
gcloud storage buckets update gs://meridian-retention-demo-<PROJECT_ID> --clear-retention-period
```
If the policy were **locked**, there would be no fix — that's why [Step 3](steps/03-retention-and-cmek-encryption.md)
explicitly tells you never to run `--locked` outside a real production requirement.

---

## Error: Static website bucket returns `403 Forbidden`

**Cause:** Almost always one of two things: (1) the bucket was never actually made public — an
`allUsers` grant is missing, or (2) the grant was attempted but silently blocked by **Public Access
Prevention** on the bucket, or by an org policy constraint like `iam.allowedPolicyMemberDomains`
(restricts which domains/identities can be granted access at all, including `allUsers`).

**Fix:** Check the binding actually exists:
```bash
gcloud storage buckets get-iam-policy gs://meridian-product-photos-<PROJECT_ID>
```
Look for `allUsers` bound to `roles/storage.objectViewer`. If it's missing, re-run the grant from
[Step 4](steps/04-signed-urls-and-static-website.md). If the grant command itself errors out
mentioning an org policy, ask whoever administers the organization's policies (`gcloud resource-manager
org-policies describe iam.allowedPolicyMemberDomains --project=<PROJECT_ID>`) to confirm public buckets
are allowed for this project — some orgs intentionally block them entirely.

---

## Error: IAM Condition fails to save — CEL syntax error

**Cause:** A typo in the CEL expression: an unescaped quote, a missing closing parenthesis, or using
the wrong resource-name format (forgetting the literal `projects/_/buckets/...` prefix and writing a
bare bucket name instead).

**Fix:** The Console's condition editor validates CEL before saving and shows the exact parse error —
read it, it usually points at the offending character. For `gcloud`, test the expression string in
isolation first:
```bash
echo 'resource.name.startsWith("projects/_/buckets/meridian-reports-<PROJECT_ID>/objects/reports/2026/")'
```
Common fixes: match every open paren with a close paren, use double quotes consistently, and remember
`resource.name` for GCS objects always starts with the literal `projects/_/buckets/` — the underscore
is not a typo and not your project ID.
