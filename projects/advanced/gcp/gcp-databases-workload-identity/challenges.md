# Challenges — GCP Databases & Workload Identity

Extend the project past the guided steps. A few of these cost real money the moment you provision the
resource — they say so explicitly. Clean up anything you add here, same as the main steps.

---

## 1. Add Firestore Security Rules

Step 1 accessed Firestore entirely server-side, so Security Rules never came into play. Write a basic
rules file that would apply if a browser client read `carts` directly:

- A customer may only read/write a cart document where `customer_id` matches their authenticated
  identity.
- No client may write `status: "checked_out"` directly (that should only happen server-side).

Test it in the **Firestore Rules simulator** (Console → Firestore → Rules → Simulator) before ever
deploying it against real data.

---

## 2. Try Firestore in Datastore Mode, and Compare

In a **separate, throwaway GCP project** (since the mode choice is permanent), create a Datastore-mode
database and rerun a version of `firestore_demo.py` against it using the same client library.

- What changes about the write/query API surface?
- What do you lose (real-time listeners) and what, if anything, do you gain?

---

## 3. Add a TTL Policy to a Firestore Collection

Firestore supports a native **TTL policy** on a collection — documents past their TTL field are
automatically deleted, no cron job required.

- Add a `expires_at` timestamp field to cart documents (e.g., 24 hours after `created_at`).
- Configure a TTL policy on the `carts` collection field.
- **Question:** why is this a better fit for "abandoned cart cleanup" than a scheduled Cloud Function
  that scans and deletes?

---

## 4. Provision a Minimal Bigtable Instance and Tear It Down Immediately

Bigtable has **no free tier and a real hourly cost the second an instance exists** — even the smallest
development instance. Provision one, confirm you can write and read a single row, then delete it in
the same sitting.

```bash
gcloud bigtable instances create meridian-events-demo \
  --cluster=meridian-events-demo-c1 --cluster-zone=us-east1-b \
  --display-name="Bigtable demo" --instance-type=DEVELOPMENT
```

**Cost note:** even a `DEVELOPMENT`-type instance bills per node-hour. Verify deletion immediately
after:
```bash
gcloud bigtable instances delete meridian-events-demo --quiet
gcloud bigtable instances list
```
The list command must come back empty before you consider this challenge done.

---

## 5. Provision a Minimal Spanner Instance and Tear It Down Immediately

Same shape as Challenge 4, but for Spanner — also **no free tier**, and Spanner's minimum billable
unit (processing units) is not cheap even at the smallest size.

```bash
gcloud spanner instances create meridian-orders-demo \
  --config=regional-us-east1 --description="Spanner demo" --processing-units=100
```

**Cost note:** 100 processing units is the smallest Spanner allows and still bills continuously while
it exists — expect this to cost more per hour than everything else in this entire project combined.
Delete it the moment you've confirmed connectivity:
```bash
gcloud spanner instances delete meridian-orders-demo --quiet
gcloud spanner instances list
```

---

## 6. Extend the Workflow to Deploy a Cloud Run Service Using the WIF-Authenticated Identity

Take `src/workflow-example.yml` further: after the `google-github-actions/auth@v2` step succeeds, add
a step that deploys a container to **Cloud Run** using the now-authenticated `meridian-deployer`
identity.

- Grant `meridian-deployer` `roles/run.admin` and `roles/iam.serviceAccountUser` (scoped, not
  project-wide `roles/owner`).
- Confirm the deploy succeeds using only the WIF-derived credentials — no key file anywhere in the
  run.

---

## 7. Apply an Actual Organization Policy Constraint (If You Have Org Access)

If your GCP identity has access to an organization (not just a personal project), go beyond the
`iam.disableServiceAccountKeyCreation` walkthrough in Step 5 and apply **one more** constraint from
[the full list](https://cloud.google.com/resource-manager/docs/organization-policy/org-policy-constraints):

- `iam.allowedPolicyMemberDomains`, scoped to your own domain.
- Attempt an IAM grant to an outside-domain identity and confirm it's now refused.
- Document exactly what error you get, and where in the chain (API call vs. Console) it's blocked.

---

**Pick two or three, not all seven** — Challenges 4 and 5 in particular are meant to be done once,
carefully, with cleanup verified immediately, not left running while you work through the rest.
