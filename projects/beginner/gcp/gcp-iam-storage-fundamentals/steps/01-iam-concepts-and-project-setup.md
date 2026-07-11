# Step 1 — IAM Concepts & Project Setup

Every action on Google Cloud — creating a bucket, reading a file, deleting a service account — is
checked against IAM first. Before you build anything for Meridian Retail's document portal, you need
the vocabulary: **who** can be granted access (principals) and **how** GCP writes down "who can do
what" (a policy). This step also enables the two APIs the rest of the project needs.

---

## 1.1 IAM Principals — Who Can Be Granted Access

A **principal** is any identity IAM can grant a role to. GCP has four kinds:

| Principal type | What it is | Used in this project? |
|-----------------|-----------|------------------------|
| **Google Account** (user) | An individual person's identity — any Gmail address or a Workspace account | Yes — you, running every step |
| **Group** | A Google Group (via Cloud Identity/Workspace) containing multiple users; grant a role once, everyone in the group gets it | Explained only here — creating a real group needs Workspace admin access most solo learners don't have. [Challenge 1](../challenges.md) covers it if you do |
| **Service account** | A non-human identity for an application or workload; no password, authenticates via short-lived tokens | Yes — `doc-portal-sa`, created in Step 2 |
| **Domain** | Every user in a verified Google Workspace domain (e.g. `@meridianretail.com`) | Explained only — needs a verified domain |

> **Why this matters for Meridian:** the document portal is *software*, not a person. It needs its
> own identity — a service account — so it can be granted exactly the storage access it needs, no
> more, independent of any employee's account.

---

## 1.2 Anatomy of an IAM Policy

Unlike AWS, where a role carries **two** separate documents (a trust policy saying who can assume
it, and a permission policy saying what it can do), GCP folds "who" and "what" into **one policy**
attached directly to the resource. A policy is a list of **bindings**:

```json
{
  "bindings": [
    {
      "role": "roles/storage.objectViewer",
      "members": [
        "serviceAccount:doc-portal-sa@meridian-retail-1234.iam.gserviceaccount.com"
      ]
    },
    {
      "role": "roles/storage.admin",
      "members": [
        "user:you@example.com"
      ],
      "condition": {
        "title": "expires-end-of-quarter",
        "expression": "request.time < timestamp('2026-10-01T00:00:00Z')"
      }
    }
  ]
}
```

| Term | What it means |
|------|---------------|
| **Policy** | The complete set of access grants on one resource (project, bucket, service account, …) |
| **Binding** | One entry pairing a `role` with the `members[]` who hold it |
| **Role** | A named bundle of permissions, e.g. `roles/storage.objectViewer` = `storage.objects.get` + `storage.objects.list` |
| **Member** | A principal string: `user:`, `group:`, `serviceAccount:`, or `domain:` prefix + identifier |
| **Condition** *(optional)* | A CEL expression that narrows *when* a binding applies (time window, resource name pattern, …) |

There's no separate "assume role" step to *use* a resource-level grant — if your principal is listed
in a binding on the bucket, you can act on it immediately. The closest GCP equivalent to AWS's
`AssumeRole` is **service account impersonation**, which you'll use in Step 4.

---

## 1.3 Where Policies Attach — the Resource Hierarchy

IAM policies attach at any level of GCP's resource hierarchy, and lower levels **inherit** grants
from higher ones (the effective policy is the union of every level):

```
Organization
└── Folder (optional)
    └── Project              ← most grants in this repo happen here
        └── Bucket / SA / …  ← this project also grants directly on the bucket and the SA
```

Granting `roles/storage.admin` at the **project** level gives that access to *every* bucket in the
project, forever, to whoever holds it. Granting the same role on **one bucket** limits the blast
radius to that bucket. You'll see both patterns in this project — and prefer the narrower one.

---

## 1.4 Console — Enable the APIs You'll Need

1. Open **☰ → APIs & Services → Enabled APIs & services** → **+ Enable APIs and Services**.
2. Search for **Cloud Storage API**, open it, click **Enable**.
3. Repeat for **Identity and Access Management (IAM) API**.

---

## 1.5 gcloud CLI (Alternative)

```bash
# Cloud Storage: buckets and objects
gcloud services enable storage.googleapis.com

# IAM: service accounts and policy bindings
gcloud services enable iam.googleapis.com
```

This project assumes gcloud is **already installed and authenticated** — this step only verifies
that, it doesn't repeat the install walkthrough:

```bash
# Confirm which account you're logged in as
gcloud auth list

# Confirm which project every command below will target
gcloud config get-value project
```

Expected output looks like:

```
$ gcloud auth list
                Credentialed Accounts
ACTIVE  ACCOUNT
*       you@example.com

$ gcloud config get-value project
my-networking-labs-1234
```

> If `gcloud config get-value project` prints `(unset)` or the wrong project, fix it now with
> `gcloud config set project <PROJECT_ID>` — every command in this project depends on it. See
> [troubleshooting.md](../troubleshooting.md) for the "wrong project context" scenario.

---

## 1.6 Why This Matters

- **Principals and bindings are the entire access model.** There's no hidden layer — if you can
  list every binding on a resource, you know exactly who can touch it.
- **Least privilege starts with picking the narrowest principal.** Meridian's portal doesn't need a
  human's account with broad access; it needs a service account scoped to exactly one bucket.
- **The resource hierarchy is a lever, not just a shortcut.** Granting at the project level is
  convenient but multiplies risk across every resource under it — a theme every remaining step
  reinforces.

---

## Checkpoint

- [ ] `gcloud auth list` shows your account as `ACTIVE`
- [ ] `gcloud config get-value project` prints the project you intend to use
- [ ] Cloud Storage API and IAM API both show **Enabled**
- [ ] You can explain the difference between a **principal**, a **role**, and a **binding**

---

**Next:** [Step 2 — Service Accounts & Roles](./02-service-accounts-and-roles.md)
