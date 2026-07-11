# Step 2 — Service Accounts & Roles

Meridian's document portal needs its own identity — one that isn't tied to any employee, can't log
into a browser, and can be locked down to exactly the access it needs. That's what a **service
account** is for. This step creates one, then walks through why some roles are the wrong choice for
it and which ones are right.

---

## 2.1 What Is a Service Account?

| Attribute | Detail |
|-----------|--------|
| **Identity format** | An email-shaped ID: `doc-portal-sa@<PROJECT_ID>.iam.gserviceaccount.com` |
| **Credentials** | No password. Authenticates via short-lived OAuth tokens, minted either from a downloaded key (avoid — Step 4 explains why) or via **impersonation** |
| **Who uses it** | Applications, VMs, CI/CD pipelines — anything that needs to call a Google Cloud API without a human typing a password |
| **Lifecycle** | Created and deleted like any other resource; deleting it immediately revokes everything it could do |

---

## 2.2 Basic Roles vs. Predefined Roles (and Why We Avoid Basic)

Every GCP project ships with three **basic roles** left over from before IAM existed. They're
tempting because they're short and always available — and that's exactly the problem.

| Basic role | What it grants | Why avoid it here |
|------------|-----------------|--------------------|
| **Owner** | Full control of *every* resource, **including IAM itself** — can grant/revoke any role to anyone | A leaked Owner credential can rewrite the project's entire access model, not just touch files |
| **Editor** | Modify almost every resource type in the project, but not IAM policies | Still project-wide: a portal SA with Editor could delete Compute instances, wipe unrelated buckets, modify databases — none of which the document portal has any reason to touch |
| **Viewer** | Read-only access to almost everything in the project | Broader read access than the portal needs — it should only be able to read *its own* bucket, not every dataset in the project |

> **Concrete bad outcome:** if `doc-portal-sa` held **Editor** and its credentials leaked (say, a
> key file committed to a public repo), the attacker wouldn't just read documents — they could
> delete every bucket, stop every VM, and drop every dataset in the project. Scoping the SA to a
> handful of storage permissions on one bucket means a leaked credential is a bad afternoon, not a
> company-ending incident.

**Predefined roles** fix this by bundling permissions per service, at a granularity you can actually
reason about:

| Predefined role | Grants | Typical holder |
|------------------|--------|-----------------|
| `roles/storage.objectViewer` | Read objects (`get`, `list`) — no write, no delete | A read-only consumer of the bucket |
| `roles/storage.objectAdmin` | Full control of **objects** (create/read/update/delete) — but not bucket settings or bucket-level IAM | `doc-portal-sa` — exactly what a document portal needs |
| `roles/storage.admin` | Full control of **buckets and objects**, including creating/deleting buckets and managing bucket IAM | You (the human operator), not the SA |
| `roles/iam.serviceAccountTokenCreator` | Lets a principal mint short-lived tokens **as** a service account (impersonation) | Granted to *you*, on the SA, so you can act as it without a key — used in Step 4 |

---

## 2.3 Console — Create the Service Account

1. Open **☰ → IAM & Admin → Service Accounts** → **+ Create Service Account**.
2. Fill in the form:

   | Field | Value |
   |-------|-------|
   | Service account name | `doc-portal-sa` |
   | Service account ID | `doc-portal-sa` (auto-fills from the name) |
   | Description | `Identity for the Meridian document portal` |

3. Click **Create and Continue**.
4. On the **"Grant this service account access to project"** screen, click **Continue** without
   adding a role. You'll grant access **scoped to the bucket** in Step 4 instead — a project-wide
   grant here would undercut the least-privilege point of this whole project.
5. Click **Done**.

---

## 2.4 gcloud CLI (Alternative)

```bash
# Create the service account (no roles yet — those come later, scoped narrowly)
gcloud iam service-accounts create doc-portal-sa \
  --display-name="Document Portal Service Account" \
  --description="Identity for the Meridian document portal"
```

Verify:

```bash
gcloud iam service-accounts list --filter="displayName:'Document Portal Service Account'"
```

---

## 2.5 Grant Yourself Permission to Impersonate the SA

You'll access the bucket **as** `doc-portal-sa` in Step 4 to prove its access is scoped correctly —
without ever downloading a key for it. That requires `roles/iam.serviceAccountTokenCreator`,
granted on the **service account itself**, to you.

### Console

1. Open **IAM & Admin → Service Accounts**, click `doc-portal-sa`.
2. Go to the **Permissions** tab → **Grant Access**.
3. Add yourself as the new principal, role **Service Account Token Creator**.
4. Click **Save**.

### gcloud CLI

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export SA_EMAIL="doc-portal-sa@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --member="user:YOUR_EMAIL@example.com" \
  --role="roles/iam.serviceAccountTokenCreator"
```

Verify:

```bash
gcloud iam service-accounts get-iam-policy "${SA_EMAIL}"
```

> Notice the resource being bound here is the **service account**, not the project or the bucket.
> `gcloud iam service-accounts add-iam-policy-binding` always grants a role **on** a specific SA
> (who may impersonate it) — a different thing from `gcloud projects add-iam-policy-binding`
> (grants a role across the whole project) or the bucket-scoped binding you'll use in Step 4.

---

## 2.6 Why Least Privilege Here Matters

- **The SA was created with zero roles.** It can't touch anything yet — access gets added
  deliberately, one narrow grant at a time, starting with the bucket in Step 4.
- **Impersonation rights are also a grant you should scope tightly.** Only principals that actually
  need to act as `doc-portal-sa` should hold `serviceAccountTokenCreator` on it — treat that binding
  with the same care as the SA's own permissions.
- **Project-level vs. resource-level is a real design choice, not a technicality.** A role granted
  on the project follows every current *and future* resource of that type; a role granted on one
  bucket or one SA doesn't.

---

## Checkpoint

- [ ] `doc-portal-sa` appears in `gcloud iam service-accounts list`
- [ ] The SA has **no** roles yet (nothing granted in this step beyond the impersonation binding)
- [ ] You hold `roles/iam.serviceAccountTokenCreator` **on** `doc-portal-sa`
- [ ] You can explain why Owner/Editor are the wrong choice for a service account
- [ ] You can explain the difference between `gcloud projects add-iam-policy-binding` and
      `gcloud iam service-accounts add-iam-policy-binding`

---

**Next:** [Step 3 — Create the Storage Bucket](./03-create-storage-bucket.md)
