# Step 5 — Impersonation & Org Policy Guardrails

Step 4 built one keyless deploy path. This step does two things: recaps **service account
impersonation** — the general mechanism WIF relies on — and then looks at **org policy**, the
guardrails that make it structurally hard for anyone on the team to backslide into downloading a key
file "just this once."

---

## 5.1 Impersonation, Recapped and Extended

If you did
[gcp-iam-storage-fundamentals](../../../../beginner/gcp/gcp-iam-storage-fundamentals/README.md)
(Project 1), you already impersonated `doc-portal-sa` to act with its permissions temporarily. WIF in
Step 4 is the *same* mechanism, just triggered by a federated external token instead of by your own
gcloud login.

| How it works | Detail |
|---------------|--------|
| **Impersonation** | Acting *as* a service account's identity for a short time, via `iam.serviceAccounts.getAccessToken`, without ever holding its key |
| **Required role** | `roles/iam.serviceAccountTokenCreator` on the target SA, granted to whoever/whatever needs to impersonate it |
| **What WIF does under the hood** | The matching GitHub principal is granted `roles/iam.workloadIdentityUser` on `meridian-deployer` — a specialized form of "may impersonate this SA," scoped to federated identities instead of gcloud users |
| **Common human use** | An engineer with broad project access impersonates a narrowly-scoped SA to test exactly what that SA can (and can't) do |

Try it yourself against `meridian-deployer`:

```bash
gcloud auth print-access-token \
  --impersonate-service-account="meridian-deployer@$(gcloud config get-value project).iam.gserviceaccount.com"
```

If this succeeds, you (or whatever identity granted you `serviceAccountTokenCreator`) can act as
`meridian-deployer` — worth double-checking that only the identities you intend can do this:

```bash
gcloud iam service-accounts get-iam-policy \
  "meridian-deployer@$(gcloud config get-value project).iam.gserviceaccount.com"
```

---

## 5.2 Org Policy: Constraints Meridian Would Set

**Organization Policy** constraints apply at the org, folder, or project level and restrict *what is
even possible* — a stronger guarantee than "we trained everyone not to do X." A key-creation ban at
the org level means no IAM grant, however generous, can be used to create a key; the API call itself
is refused.

These three constraints are the ones a real security-conscious org sets alongside a project like this
one:

| Constraint | What it prevents |
|------------|-------------------|
| `iam.disableServiceAccountKeyCreation` | No one, for any service account, in any project under this org/folder, can create a downloadable JSON key — full stop |
| `storage.uniformBucketLevelAccess` (enforced) | No bucket in scope can use legacy per-object ACLs — closes the exact gap the [gcp-storage-security-lifecycle](../../../../intermediate/gcp/gcp-storage-security-lifecycle/README.md) project (Project 2) hardens manually |
| `iam.allowedPolicyMemberDomains` | IAM bindings can only reference identities from an approved set of domains — stops "grant access to any gmail.com account" mistakes |

**If you have org-level access**, apply the key-creation ban (the one most relevant to this project):

```bash
ORG_ID=<your organization ID>   # gcloud organizations list

cat <<EOF > /tmp/disable-sa-keys.yaml
name: organizations/${ORG_ID}/policies/iam.disableServiceAccountKeyCreation
spec:
  rules:
    - enforce: true
EOF

gcloud org-policies set-policy /tmp/disable-sa-keys.yaml
```

Verify:

```bash
gcloud org-policies describe iam.disableServiceAccountKeyCreation \
  --organization="${ORG_ID}"
```

> **Careful:** this constraint applies to **every** project under the org/folder you set it on — not
> just this lab's project. If you have org access and other projects rely on downloaded keys, this
> will break them. Understand the blast radius before enforcing it outside a sandbox org.

---

## 5.3 No Org Access? A Project-Level Fallback

Most personal GCP projects aren't attached to an organization, so `gcloud org-policies` isn't
available to you. That's fine — the *practice* that matters is verifiable without org policy at all:
**confirm this entire series never created a key file.**

```bash
# Check every service account created across this series for downloaded keys
for SA in doc-portal-sa meridian-deployer; do
  echo "== ${SA} =="
  gcloud iam service-accounts keys list \
    --iam-account="${SA}@$(gcloud config get-value project).iam.gserviceaccount.com" \
    --format='table(name,keyType,validAfterTime)' 2>/dev/null
done
```

Expect to see only **`SYSTEM_MANAGED`** key types (Google-internal keys used for signing, which you
never download or handle) — no `USER_MANAGED` entries. A `USER_MANAGED` key is exactly the thing WIF
and impersonation exist to make unnecessary. If you ever see one on a service account from this
series, it means a key was downloaded at some point — delete it:

```bash
gcloud iam service-accounts keys delete <KEY_ID> \
  --iam-account="<SA_EMAIL>"
```

This is the same audit an org policy would enforce automatically — you're just doing it by hand,
once, on your own project.

---

## 5.4 Why This Matters

- **Impersonation and WIF are the same trust primitive** wearing two different hats — one for humans
  acting temporarily as a role, one for external CI systems. Understanding one explains the other.
- **Org policy turns "best practice" into "not possible to violate."** A team that relies on
  training alone will eventually have someone download a key under deadline pressure; a team with
  `iam.disableServiceAccountKeyCreation` enforced structurally can't.
- **The project-level audit is worth doing even without org access** — it's the concrete proof that
  every identity this series created (`doc-portal-sa`, `meridian-deployer`, and any others) really is
  keyless.

---

## Checkpoint

- [ ] You successfully impersonated `meridian-deployer` and can explain what role made that possible
- [ ] You reviewed `meridian-deployer`'s IAM policy and confirmed only the intended identities can impersonate it
- [ ] (Org access) `iam.disableServiceAccountKeyCreation` is enforced, or you understand exactly what it would do
- [ ] (No org access) `gcloud iam service-accounts keys list` shows only `SYSTEM_MANAGED` keys for every SA in this series

---

**Next:** [Step 6 — Database Decision Matrix](./06-database-decision-matrix.md)
