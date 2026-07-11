# Troubleshooting — GCP Databases & Workload Identity

Error → Cause → Fix. Most problems here are one missing piece in an identity chain (WIF) or one
missing network path (Memorystore) — both patterns repeat, so once you've fixed one instance you'll
recognize the next.

---

## Error: `Firestore database already exists in a different mode`

**Cause:** Native vs. Datastore mode is chosen **once per project**, permanently, at first database
creation. If this project (or an earlier experiment) already has a Datastore-mode database, you
cannot create a Native-mode one alongside it.

**Fix:**
```bash
gcloud firestore databases list --format='value(name,type)'
```
If it shows `DATASTORE_MODE`, there is no in-place conversion. Use a different GCP project for this
lab, or continue the Datastore-mode API's document model (it's similar, but you'll lose real-time
listeners, which this project's teaching around Firestore assumes).

---

## Error: `redis-cli` / `cache_demo.py` connection times out reaching Memorystore

**Cause:** Memorystore has **no public IP** by design. The client (VM, Cloud Run, GKE pod) must be
in the **same VPC and region**, and — for serverless products — routed through a **Serverless VPC
Access connector**. A VM in a different VPC, or a Cloud Shell session, will simply time out.

**Fix:**
```bash
gcloud redis instances describe meridian-cache --region=us-east1 --format='value(authorizedNetwork)'
gcloud compute instances describe redis-test-vm --zone=us-east1-b --format='value(networkInterfaces[0].network)'
```
Both must reference the same network (`default`, unless you changed it). If they don't match, delete
and recreate the VM in the correct VPC, or recreate Memorystore in the VM's VPC.

---

## Error: GitHub Actions run fails with `unauthorized_client` or `permission denied` on `google-github-actions/auth@v2`

**Cause:** almost always the **attribute condition** on `github-provider` not matching the actual
repo/branch the workflow ran from, or the `workloadIdentityUser` binding's `principalSet` not matching
either.

**Fix:**
```bash
gcloud iam workload-identity-pools providers describe github-provider \
  --location=global --workload-identity-pool=github-pool \
  --format='value(attributeCondition)'
```
Confirm it's exactly `assertion.repository == 'YOUR_ORG/YOUR_REPO'` — a typo'd org/repo name, or
testing from a fork (which has a different `repository` claim), will fail here. Then confirm the
binding:
```bash
gcloud iam service-accounts get-iam-policy \
  meridian-deployer@<PROJECT_ID>.iam.gserviceaccount.com
```
The `principalSet://...attribute.repository/YOUR_ORG/YOUR_REPO` string must match character-for-character.

---

## Error: `PERMISSION_DENIED` on `iam.serviceAccounts.signBlob` or `getAccessToken` during impersonation

**Cause:** the identity attempting to impersonate `meridian-deployer` (your gcloud user, or the
federated GitHub principal) lacks `roles/iam.serviceAccountTokenCreator` (for direct impersonation) or
`roles/iam.workloadIdentityUser` (for the WIF path) on that specific service account.

**Fix:**
```bash
gcloud iam service-accounts add-iam-policy-binding \
  meridian-deployer@<PROJECT_ID>.iam.gserviceaccount.com \
  --member="user:you@example.com" \
  --role="roles/iam.serviceAccountTokenCreator"
```
Re-run the impersonation command from [Step 5.1](steps/05-impersonation-and-org-policy-guardrails.md#51-impersonation-recapped-and-extended).

---

## Error: `PERMISSION_DENIED: Secret Manager API has not been used` or access denied reading a secret version

**Cause:** either the Secret Manager API isn't enabled on the project, or the calling identity lacks
`roles/secretmanager.secretAccessor` on that specific secret.

**Fix:**
```bash
gcloud services enable secretmanager.googleapis.com
gcloud secrets get-iam-policy meridian-orders-db-password
```
Grant access scoped to the one secret (not project-wide) as shown in
[Step 3.4](steps/03-secret-manager-for-db-credentials.md#34-gcloud-cli-alternative).

---

## Error: `Operation denied by org policy` when creating a resource

**Cause:** an organization policy constraint (yours, or one already set by whoever administers your
org) is blocking the exact action you're taking — e.g., trying to create a public-facing resource
under `iam.allowedPolicyMemberDomains`, or trying to download a service-account key under
`iam.disableServiceAccountKeyCreation`.

**Fix:** this error is often **working as intended** — read it before trying to route around it.
```bash
gcloud org-policies describe <CONSTRAINT_NAME> --organization="${ORG_ID}"
```
If it's a constraint you deliberately set in [Step 5.2](steps/05-impersonation-and-org-policy-guardrails.md#52-org-policy-constraints-meridian-would-set)
and you need a temporary exception, org policies support per-resource overrides — but the better fix
is usually to change what you're trying to do, not the guardrail.

---

## Error: WIF provider creation fails with an issuer/discovery error

**Cause:** a typo'd `--issuer-uri`. It must be exactly `https://token.actions.githubusercontent.com`
— no trailing slash, no path, correct scheme.

**Fix:**
```bash
gcloud iam workload-identity-pools providers update-oidc github-provider \
  --location=global --workload-identity-pool=github-pool \
  --issuer-uri="https://token.actions.githubusercontent.com"
```
GCP validates the issuer against its OIDC discovery document at creation time — a wrong URL fails
immediately rather than silently, which is the fast way to catch this.

---

## Cleanup: `FAILED_PRECONDITION` deleting the Workload Identity Pool

**Cause:** the pool (or provider) still has an active binding referencing it, or you're deleting the
provider before removing dependent config.

**Fix:** delete the service account (and its bindings) first, then the provider, then the pool — see
the exact order in [Step 7.5](steps/07-cleanup.md#75-tear-down-workload-identity-federation). If it
still fails, list what's attached:
```bash
gcloud iam workload-identity-pools providers list --location=global --workload-identity-pool=github-pool
```
