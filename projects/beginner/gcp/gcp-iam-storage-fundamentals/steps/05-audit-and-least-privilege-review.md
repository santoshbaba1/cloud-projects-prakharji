# Step 5 — Audit & Least-Privilege Review

Granting the right roles once isn't the end of the story — you also need to be able to **prove**
what's granted, **see** who used it, and **catch** anything broader than it should be. This step
looks at Cloud Audit Logs, deliberately triggers a permission failure so you know what one looks
like, and reviews the bucket's IAM policy with a critical eye.

---

## 5.1 Cloud Audit Logs — Two Kinds

| Log type | What it captures | Enabled by default? | Cost |
|----------|--------------------|------------------------|------|
| **Admin Activity** | Configuration changes: creating a bucket, granting a role, deleting a service account | **Yes, always on**, can't be disabled | Free |
| **Data Access** | Read/write of actual data: every object `get`, every `list` call | **No** — off by default for most services, including Cloud Storage | Billed per log entry once enabled; can generate high volume |

Every `add-iam-policy-binding` call and every bucket creation you ran in Steps 2–4 already produced
an **Admin Activity** log entry — no setup required. This project deliberately does **not** enable
Data Access logs: for a lab bucket, the log volume/cost isn't worth it, but production systems
handling sensitive documents (contracts, PII) often do enable them precisely to answer "who read
this file, and when."

---

## 5.2 Console — View the Admin Activity Log

1. Open **☰ → Logging → Logs Explorer**.
2. In the query box, filter to Storage's admin actions:

   ```
   protoPayload.serviceName="storage.googleapis.com"
   logName:"activity"
   ```

3. Run the query. You should see entries for `storage.buckets.create` and the
   `storage.setIamPermissions` calls from Step 4 — each with **who** made the change and **when**.

### gcloud CLI (Alternative)

```bash
gcloud logging read \
  'protoPayload.serviceName="storage.googleapis.com" AND logName:"activity"' \
  --limit=10 \
  --format="table(timestamp, protoPayload.methodName, protoPayload.authenticationInfo.principalEmail)"
```

---

## 5.3 Deliberately Trigger — and Read — a 403

You already saw one denial in Step 4 (the SA couldn't delete the bucket). Here's another, closer to
what a real operator debugging access hits: try to grant a role you **don't** have permission to
grant. `roles/resourcemanager.projectIamAdmin` (not `roles/owner`) can grant most roles, but is
itself blocked from granting IAM-sensitive roles it doesn't already hold — if your account is
scoped down to just `projectIamAdmin` + `storage.admin` as this project's prerequisites allow, this
will surface a real 403 for you to read:

```bash
gcloud storage buckets add-iam-policy-binding "gs://${BUCKET}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"
```

If your account is `roles/owner`, this command will actually succeed — which is itself the lesson:
**Owner can grant anything, including roles broader than the granter should be handing out.** Either
way, immediately undo it so the SA stays scoped to `objectAdmin` only:

```bash
gcloud storage buckets remove-iam-policy-binding "gs://${BUCKET}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"
```

> If the grant *did* fail for you, read the error message closely — GCP's 403s name the exact
> missing permission (e.g. `resourcemanager.projects.setIamPolicy`), which is the fastest way to
> know what to ask for. See [troubleshooting.md](../troubleshooting.md) for the full pattern.

---

## 5.4 Review the Bucket's Current IAM Policy

Pull the full policy and read every binding as if you were auditing someone else's project:

```bash
gcloud storage buckets get-iam-policy "gs://${BUCKET}"
```

Ask of each binding:

1. **Does this principal still need this access?** (Here: just `doc-portal-sa` with `objectAdmin`.)
2. **Is the role the narrowest one that covers the actual need?** (`objectAdmin`, not `storage.admin`.)
3. **Is it scoped to the right resource?** (The bucket, not the whole project.)

If you followed Steps 2–4 as written, the answer to all three is yes — which is the point: reviewing
a tightly-scoped policy should be quick and boring. A five-minute review that turns up nothing is
success, not wasted effort.

> **Real-world note:** your own account likely holds `roles/owner` for this lab, which is
> intentionally broad so you can complete every step. In a real organization, the *operator* role
> would itself be narrower — typically `roles/resourcemanager.projectIamAdmin` + `roles/storage.admin`,
> exactly what this project's prerequisites describe, rather than blanket `Owner`.

---

## 5.5 IAM Recommender (Brief Mention)

**IAM Recommender** (under **IAM & Admin → Recommendations**) watches actual permission *usage* over
time and suggests replacing over-broad roles with narrower ones a principal has actually exercised.
It typically needs on the order of **90 days of observed activity** before it has enough signal to
recommend anything useful — so a bucket you created five minutes ago won't show recommendations yet.
Worth knowing it exists; [Challenge 5](../challenges.md) has you check back on a longer-lived project.

---

## Checkpoint

- [ ] You located the Admin Activity log entries for Step 2–4's IAM changes
- [ ] You saw a `PERMISSION_DENIED` and read the specific permission it named
- [ ] The bucket's IAM policy contains exactly one binding: `doc-portal-sa` → `roles/storage.objectAdmin`
- [ ] You can explain why Data Access logs are off by default and what enabling them costs

---

**Next:** [Step 6 — Cleanup](./06-cleanup.md)
