# Troubleshooting — GCP IAM & Storage Fundamentals

Error → Cause → Fix for the problems you're most likely to hit.

---

## Error: `ERROR: (gcloud.storage.buckets.add-iam-policy-binding) User [you@example.com] does not have permission to access namespace [...] (or it may not exist): Permission 'resourcemanager.projects.setIamPolicy' denied`

**Cause:** You tried to grant an IAM role but your own account lacks permission to grant it. This is
most common when your account holds `roles/resourcemanager.projectIamAdmin` (which can grant *most*
roles) but not `roles/owner`, and you attempt to grant something IAM-sensitive that `projectIamAdmin`
itself is blocked from delegating.

**Fix:**
```bash
gcloud projects get-iam-policy "$(gcloud config get-value project)" \
  --flatten="bindings[].members" \
  --filter="bindings.members:you@example.com" \
  --format="table(bindings.role)"
```
Confirm which roles you actually hold, then either use an account with `roles/owner` for the lab, or
grant only the roles your current permissions allow. This is the exact 403-reading exercise in
[Step 5.3](steps/05-audit-and-least-privilege-review.md).

---

## Error: `ERROR: (gcloud.storage.buckets.create) HTTPError 409: The requested bucket name is not available. The bucket namespace is shared by all users of the system.`

**Cause:** Cloud Storage bucket names are **globally unique across every GCP customer**, not just
your project. Someone else already owns the exact name you tried.

**Fix:** This project's naming convention (`meridian-docs-<PROJECT_ID>`) exists specifically to avoid
this — your project ID is already globally unique, so the combined name will be too. Double-check
you actually substituted your real project ID and didn't leave a placeholder:
```bash
echo "meridian-docs-$(gcloud config get-value project)"
```

---

## Error: `One or more users named in the ACL do not exist` / `Cannot get legacy ACL for a bucket that has uniform bucket-level access`

**Cause:** You (or a copied command) tried to run a legacy per-object ACL command — `gsutil acl ...`
or `gcloud storage objects update --add-acl-grant` — against a bucket with **uniform bucket-level
access** enabled (Step 3.4). Uniform access disables the legacy ACL system entirely; IAM is the only
mechanism.

**Fix:** Use an IAM binding instead of an ACL grant:
```bash
gcloud storage buckets add-iam-policy-binding "gs://${BUCKET}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.objectViewer"
```
If you genuinely need per-object ACLs for a different bucket, you'd have to create it **without**
`--uniform-bucket-level-access` — not recommended, and not what this project uses.

---

## Error: `ERROR: (gcloud.storage.cp) HTTPError 403: Permission 'iam.serviceAccounts.getAccessToken' denied on resource (or it may not exist).`

**Cause:** You ran a command with `--impersonate-service-account` but the caller (you) doesn't hold
`roles/iam.serviceAccountTokenCreator` **on that specific service account**. This is different from
holding storage permissions — impersonation is gated separately, on the SA resource itself.

**Fix:** Grant yourself the Token Creator role on the SA (this is [Step 2.5](steps/02-service-accounts-and-roles.md)):
```bash
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --member="user:YOUR_EMAIL@example.com" \
  --role="roles/iam.serviceAccountTokenCreator"
```
Then retry the impersonated command.

---

## Error: `PERMISSION_DENIED: Cloud Storage JSON API has not been used in project ... before or it is disabled`

**Cause:** The Cloud Storage API (or the IAM API, for a similarly-worded error) isn't enabled in your
project yet.

**Fix:**
```bash
gcloud services enable storage.googleapis.com
gcloud services enable iam.googleapis.com
```
Wait about a minute for the enablement to propagate, then retry. (This is Step 1.5.)

---

## Problem: A role you just granted still returns `PERMISSION_DENIED` a few seconds later

**Cause:** IAM policy changes are **eventually consistent**. Most bindings propagate in a few
seconds, but caches at various layers can occasionally take up to a couple of minutes.

**Fix:** Wait 30–60 seconds and retry. If it's still failing after 2 minutes, re-verify the binding
actually exists rather than continuing to wait:
```bash
gcloud storage buckets get-iam-policy "gs://${BUCKET}"
```
If the binding isn't there, the grant didn't actually succeed — re-run it and check for errors,
rather than assuming it's still propagating.

---

## Problem: Commands succeed, but resources show up in the wrong project (or you can't find what you just created)

**Cause:** `gcloud`'s default project (`gcloud config get-value project`) doesn't match the project
you think you're working in — often because you have multiple projects from other work/labs in this
repo and switched between them at some point.

**Fix:** Check and, if needed, reset the default before continuing:
```bash
gcloud config get-value project
gcloud config set project <THE_PROJECT_ID_YOU_MEANT>
```
Every command in this project reads `$PROJECT_ID` from this default — a stale value silently sends
resources to the wrong place instead of erroring.
