# Step 7 — Cleanup

This is the last step every time in this repo, and it's especially important here: **Memorystore
bills per hour with no free tier**, and the WIF pool/provider/SA are exactly the kind of "invisible
because they're not a VM" resources that get forgotten. Delete in this order — **compute → data →
identity** — so nothing is deleted while something else still depends on it.

---

## 7.1 Delete the Test GCE VM

```bash
gcloud compute instances delete redis-test-vm --zone=us-east1-b --quiet
```

---

## 7.2 Delete Memorystore

The single most important line in this step — this is the resource that keeps billing if you skip it.

```bash
gcloud redis instances delete meridian-cache --region=us-east1 --quiet
```

Verify:

```bash
gcloud redis instances list --region=us-east1
```

Expect no output.

---

## 7.3 Delete Firestore Data

Firestore doesn't work like the other resources here — you generally **delete the data, not the
database itself**. The `(default)` database is a project-level singleton; most teams leave it in
place (it costs nothing while empty) and only clear out the documents/collections a lab created.

Delete the sample documents:

```bash
gcloud firestore documents delete \
  "projects/$(gcloud config get-value project)/databases/(default)/documents/carts/cart_alice" --quiet
gcloud firestore documents delete \
  "projects/$(gcloud config get-value project)/databases/(default)/documents/carts/cart_bob" --quiet
```

**If you want the database itself gone** (e.g., you're tearing down the whole project and want a
clean slate for a future Native/Datastore mode choice), Firestore does support deleting the entire
database:

```bash
gcloud firestore databases delete --database='(default)' --quiet
```

> ⚠️ This is destructive and, like the mode choice in Step 1, **not something to run casually** — it
> removes every collection in the database, not just this project's. Only run it if you're certain.

---

## 7.4 Delete the Secret Manager Secret

```bash
gcloud secrets delete meridian-orders-db-password --quiet
```

---

## 7.5 Tear Down Workload Identity Federation

Delete the binding's owner (the service account) and the pool/provider. Deleting the service account
implicitly removes bindings that reference it; the pool and provider are deleted independently.

```bash
gcloud iam service-accounts delete \
  "meridian-deployer@$(gcloud config get-value project).iam.gserviceaccount.com" --quiet

gcloud iam workload-identity-pools providers delete github-provider \
  --location="global" --workload-identity-pool="github-pool" --quiet

gcloud iam workload-identity-pools delete github-pool \
  --location="global" --quiet
```

> A deleted Workload Identity Pool is only **soft-deleted for 30 days** before permanent removal —
> if you recreate a pool with the same ID within that window, `gcloud` will tell you to either
> restore it or choose a different ID.

---

## 7.6 Remove Any Org Policy Changes

If you set the org-level constraint in [Step 5](./05-impersonation-and-org-policy-guardrails.md) and
it's not something you want to keep enforced org-wide, clear it:

```bash
gcloud org-policies delete iam.disableServiceAccountKeyCreation \
  --organization="${ORG_ID}"
```

If you only did the project-level key audit (no org access), there's nothing to revert here.

---

## 7.7 Final Verification Sweep

```bash
gcloud compute instances list
gcloud redis instances list --region=us-east1
gcloud secrets list --filter="name:meridian-orders-db-password"
gcloud iam workload-identity-pools list --location=global
gcloud iam service-accounts list --filter="email:meridian-deployer*"
```

Every one of these should come back empty (except Firestore, which — per 7.3 — you likely left in
place with just its documents cleared).

---

## Checkpoint

- [ ] `redis-test-vm` is deleted
- [ ] `meridian-cache` Memorystore instance is deleted — **verified with `gcloud redis instances list`**
- [ ] `carts` collection documents are removed (or the whole database, if you chose that path)
- [ ] `meridian-orders-db-password` secret is deleted
- [ ] `github-pool` / `github-provider` / `meridian-deployer` are all deleted
- [ ] Any org policy changes are reverted, or intentionally left in place
- [ ] The final verification sweep returns empty for every resource this project created
