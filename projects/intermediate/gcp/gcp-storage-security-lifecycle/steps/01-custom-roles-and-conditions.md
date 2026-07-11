# Step 1 — Custom Roles & IAM Conditions

Project 1 granted principals **predefined** roles like `roles/storage.objectViewer`. Predefined
roles are convenient but coarse — `objectAdmin`, for example, includes delete and ACL permissions a
reports-uploader job has no business having. In this step you'll build a **custom role** with exactly
three permissions, then go one step further with an **IAM Condition** that restricts *where* in the
bucket that role can write. This is the kind of access Meridian's security reviewer will actually sign
off on.

> **Prerequisites:** `gcloud config set project <PROJECT_ID>` from Project 1, and
> `gcloud config set compute/region us-east1`. Set a shell variable for convenience:
> `PROJECT_ID=$(gcloud config get-value project)`.

---

## 1.1 Why Not Just Use a Predefined Role?

| Concept | What it means |
|---------|---------------|
| **Predefined role** | A Google-curated bundle of permissions (e.g. `roles/storage.objectAdmin`) covering a common job |
| **Custom role** | A role you define yourself, listing the exact permissions a job needs — nothing more |
| **Why bother** | `objectAdmin` includes `storage.objects.delete` and `storage.objects.setIamPolicy`; an uploader job needs neither. Granting it anyway is over-provisioning |
| **Where to start** | Don't write a permission list from scratch — copy the permission list of the closest predefined role and delete what you don't need |
| **Role launch stage** | Custom roles can be `ALPHA`, `BETA`, or `GA` — the stage is metadata for your own rollout process, GCP enforces the role either way |

Inspect the predefined role you'd otherwise have used, to see what it grants and what you're trimming:

```bash
gcloud iam roles describe roles/storage.objectCreator
```

You'll see it grants `storage.objects.create` and `storage.objects.list` — close, but the uploader
job also needs to read back an object it just wrote to confirm the upload, so you'll add
`storage.objects.get` and build your own role rather than trying to bolt that onto a predefined one.

---

## 1.2 What You'll Create

| Object | Value |
|--------|-------|
| Custom role ID | `MeridianReportsUploader` |
| Permissions | `storage.objects.create`, `storage.objects.get`, `storage.objects.list` |
| Bound to | The reports-uploader principal (a user or service account — use your own account for this lab) |
| Condition title | `reports-2026-prefix-only` |
| Condition expression | `resource.name.startsWith("projects/_/buckets/meridian-reports-PROJECT_ID/objects/reports/2026/")` |

The role alone says "this principal can create/get/list objects in any bucket it has access to." The
**condition** narrows that down to "...but only inside `reports/2026/` in this one bucket." Together
they implement least privilege in two independent dimensions: **what** actions, and **where**.

---

## 1.3 Console — Create the Custom Role

1. **☰ → IAM & Admin → Roles → Create Role.**
2. Fill in the role:

   | Field | Value |
   |-------|-------|
   | Title | `Meridian Reports Uploader` |
   | Description | `Upload and verify report objects; no delete, no ACL changes` |
   | ID | `MeridianReportsUploader` |
   | Role launch stage | General Availability |

3. Click **Add Permissions** and add exactly:
   - `storage.objects.create`
   - `storage.objects.get`
   - `storage.objects.list`
4. Click **Create**.

---

## 1.4 gcloud CLI (Alternative)

```bash
gcloud iam roles create MeridianReportsUploader \
  --project="$PROJECT_ID" \
  --title="Meridian Reports Uploader" \
  --description="Upload and verify report objects; no delete, no ACL changes" \
  --permissions=storage.objects.create,storage.objects.get,storage.objects.list \
  --stage=GA
```

Verify the exact permission set landed as intended:

```bash
gcloud iam roles describe MeridianReportsUploader --project="$PROJECT_ID" \
  --format='value(includedPermissions)'
```

---

## 1.5 Console — Bind the Role With a Condition

The reports bucket (`meridian-reports-$PROJECT_ID`) doesn't exist yet — you'll create it in
[Step 2](./02-versioning-and-lifecycle-rules.md). IAM Conditions can still reference it now; the
binding just has no effect until the bucket exists.

1. **☰ → IAM & Admin → IAM → Grant Access.**
2. **New principals**: your own user email (standing in for the uploader job).
3. **Role**: search for and select **`Meridian Reports Uploader`** (custom role).
4. Click **Add IAM Condition**:

   | Field | Value |
   |-------|-------|
   | Title | `reports-2026-prefix-only` |
   | Description | `Only objects under reports/2026/ in the reports bucket` |
   | Condition type | Custom |
   | Condition (CEL) | `resource.name.startsWith("projects/_/buckets/meridian-reports-PROJECT_ID/objects/reports/2026/")` |

   Replace `PROJECT_ID` with your actual project ID — bucket names in `resource.name` are literal, not
   variables.

5. Click **Save**, then **Save** again on the IAM screen.

---

## 1.6 gcloud CLI (Alternative)

```bash
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="user:YOUR_EMAIL@example.com" \
  --role="projects/$PROJECT_ID/roles/MeridianReportsUploader" \
  --condition="expression=resource.name.startsWith('projects/_/buckets/meridian-reports-$PROJECT_ID/objects/reports/2026/'),title=reports-2026-prefix-only,description=Only objects under reports/2026/ in the reports bucket"
```

Verify the binding and its condition landed correctly:

```bash
gcloud projects get-iam-policy "$PROJECT_ID" --format=json \
  | python3 -c "
import json, sys
policy = json.load(sys.stdin)
for b in policy['bindings']:
    if b['role'].endswith('MeridianReportsUploader'):
        print(json.dumps(b, indent=2))
"
```

---

## 1.7 Understanding the CEL Expression

| Piece | Meaning |
|-------|---------|
| `resource.name` | The full resource path GCP evaluates the condition against — for GCS objects, `projects/_/buckets/<bucket>/objects/<object-path>` |
| `.startsWith(...)` | A CEL string function; true only if the object path begins with the given prefix |
| `projects/_/buckets/...` | The literal `_` is intentional — it's a placeholder GCP uses in this resource-name format, not your project ID |

**Where conditions apply:** IAM Conditions are only supported on bindings for resource types and
roles that declare **condition support** — project-level bindings on most GCP-managed and custom
IAM roles support it (as used here), but a handful of legacy roles and some Cloud Identity-related
bindings do not. If you try to attach a condition to an unsupported binding, `gcloud` or the Console
rejects the entire binding with an explicit error rather than silently ignoring the condition.

> **Policy troubleshooting:** when access looks wrong, don't guess — pull the JSON policy
> (`gcloud projects get-iam-policy --format=json`) and diff it against what you expect, the same way
> you'd diff any other config. For more complex cases spanning multiple resources and inherited
> bindings, **Policy Analyzer** (under **IAM & Admin → Policy Troubleshooter**) traces exactly which
> binding grants (or denies) a given principal a given permission on a given resource.

---

## 1.8 Why This Matters

- **Two independent least-privilege levers.** The role controls *actions*; the condition controls
  *scope*. Auditors ask about both separately, and it's much easier to reason about "can only create,
  get, list" and "only under this prefix" as two short, composable statements than one giant role.
- **Custom roles decay less than you'd think.** Building from a predefined role's permission list
  (`gcloud iam roles describe`) means you inherit Google's understanding of what a permission set
  needs, then trim — rather than guessing permission strings from scratch and under- or
  over-granting.
- **Conditions are enforced server-side, at request time**, on every API call — there's no way for a
  caller to bypass them by hitting a different endpoint.

---

## Checkpoint

- [ ] `MeridianReportsUploader` exists with exactly `storage.objects.create`, `storage.objects.get`,
      `storage.objects.list`
- [ ] The role is bound to your principal at the project level with a CEL condition scoping it to
      `reports/2026/` in the (not-yet-created) reports bucket
- [ ] `gcloud projects get-iam-policy --format=json` shows the binding with its `condition` block
- [ ] You can explain why `projects/_/buckets/...` uses a literal underscore, not your project ID

---

**Next:** [Step 2 — Versioning & Lifecycle Rules](./02-versioning-and-lifecycle-rules.md)
