# Challenges — GCP IAM & Storage Fundamentals

Extend the lab to deepen your understanding. Each builds on the service account and bucket you
already have. Remember to clean up any extra resources afterward.

---

## 1. Grant Access to a Real Google Group

Step 1.1 explained groups but couldn't have you provision one, since that needs Cloud Identity or
Google Workspace admin access. If you have access to either:

- Create a group (e.g. `meridian-readers@yourdomain.com`) via the
  [Google Groups](https://groups.google.com/) admin UI or Cloud Identity.
- Grant `roles/storage.objectViewer` on the bucket to `group:meridian-readers@yourdomain.com`
  instead of an individual user.
- Add and remove yourself from the group and watch your access to the bucket change without any
  IAM binding being touched directly.
- **Question:** Why does granting access to groups instead of individuals scale better in a real
  organization with dozens of employees joining and leaving?

---

## 2. Try the IAM Policy Simulator

Before granting a role for real, GCP can tell you what it *would* allow. Open **IAM & Admin →
Policy Troubleshooter** (or **Policy Simulator** if available in your console).

- Simulate: can `doc-portal-sa` call `storage.buckets.delete` on `meridian-docs-<PROJECT_ID>`?
  Confirm it predicts **denied**, matching what you saw for real in Step 4.4.
- Simulate the same question for `storage.objects.create` — confirm it predicts **allowed**.
- **Lesson:** the simulator lets you validate a least-privilege design *before* granting it,
  catching over- or under-scoped roles without ever touching production access.

---

## 3. Add a Second Bucket With a Deny Policy

GCP supports explicit **IAM deny policies** — bindings that block access even if some other
binding would otherwise allow it (deny always wins).

- Create a second bucket, `meridian-archive-<PROJECT_ID>`.
- Grant `doc-portal-sa` `roles/storage.objectAdmin` on it (same pattern as Step 4.2).
- Add a **deny policy** blocking `storage.objects.delete` for `doc-portal-sa` on this bucket
  specifically, using `gcloud iam policies create` against the bucket's resource path.
- Confirm the SA can still create/read objects but a delete attempt is refused — even though
  `objectAdmin` alone would normally allow it.
- **Question:** When would you reach for a deny policy instead of just granting a narrower role?

---

## 4. Build a Custom Role

Predefined roles are convenient but sometimes too broad. `roles/storage.objectAdmin` includes
permissions (like `storage.objects.setIamPolicy` on individual objects, when ACLs are in play) that
the document portal never actually uses.

- Create a **custom role** containing only `storage.objects.get`, `storage.objects.create`,
  `storage.objects.list`, and `storage.objects.delete`.
- Grant it to `doc-portal-sa` on the bucket **instead of** `roles/storage.objectAdmin`, and confirm
  Step 4's upload/download/list operations still work.
- **Lesson:** predefined roles are a good default, but custom roles let you shave a grant down to
  the exact permission set a workload uses — at the cost of having to maintain the role yourself as
  GCP's APIs evolve.

---

## 5. Explore IAM Recommender on a Longer-Lived Project

Step 5.5 mentioned IAM Recommender needs real usage history (roughly 90 days) to produce useful
suggestions — too long for this lab's timeline.

- If you have access to an older GCP project with real activity, open **IAM & Admin →
  Recommendations** on it and read through any recommendations shown.
- **Goal:** understand the *shape* of a Recommender suggestion (e.g. "replace Editor with these 3
  specific roles based on 90 days of observed usage") even if you can't generate one fresh today.

---

## 6. Contrast With an AWS IAM Role

This repo's [`aws-iam-roles-and-policies`](../../../intermediate/aws/aws-iam-roles-and-policies/README.md)
project builds the AWS equivalent of what you just did on GCP.

- Read that project's Step 3 (Lambda execution role) and compare its **trust policy** +
  **permission policy** pair against the single **binding** you wrote for `doc-portal-sa` here.
- Compare AWS's `sts:AssumeRole` (a person or service explicitly assumes a role, receiving temporary
  credentials) against GCP's **impersonation** (Step 4.3) — both solve "act as this other identity
  without a standing key," but the mechanics differ.
- **Question:** Which model do you find easier to audit at a glance — two documents per role (AWS)
  or one binding list per resource (GCP) — and why?

---

## 7. View Organization-Level Policy (If You Have One)

Everything in this project was granted at the project or resource level. If your Google account
belongs to an actual Google Cloud **organization** (not just a standalone project):

- Run `gcloud resource-manager org-policies list --organization=<ORG_ID>` to see org-wide
  constraints, such as `constraints/iam.disableServiceAccountKeyCreation` — a policy that would have
  *enforced* the key-less impersonation approach from Step 4.3 instead of just recommending it.
- **Goal:** see how an organization can turn "best practice" (impersonation over keys) into a
  structurally enforced rule that no project owner can override locally.
