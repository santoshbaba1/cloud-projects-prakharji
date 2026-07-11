# Step 3 — Create the Storage Bucket

With `doc-portal-sa` created but still empty-handed, it's time to build the thing it will eventually
access: a Cloud Storage bucket to hold Meridian's documents. This step covers the choices every new
bucket forces on you — name, storage class, location, and access model — and why each answer fits a
document-portal workload.

---

## 3.1 Bucket Naming Is Global

Cloud Storage bucket names are **globally unique across every GCP customer**, not just your project
— like S3 bucket names on AWS. `docs` or `meridian-docs` will already be taken. This project suffixes
the name with your **project ID**, which is already guaranteed unique:

```
meridian-docs-<PROJECT_ID>
```

e.g. `meridian-docs-my-networking-labs-1234`. Bucket names must also be lowercase, and may contain
only letters, digits, hyphens, underscores, and dots.

---

## 3.2 Storage Classes — Pick the Right One

| Storage class | Minimum storage duration | Retrieval cost | Good for |
|----------------|---------------------------|------------------|-----------|
| **Standard** | None | None | Frequently accessed data — this project |
| **Nearline** | 30 days | Per-GB retrieval fee | Data accessed roughly once a month |
| **Coldline** | 90 days | Higher per-GB retrieval fee | Data accessed a few times a year |
| **Archive** | 365 days | Highest per-GB retrieval fee | Long-term backups, compliance retention |

Meridian's employees will read and write these documents regularly during business hours — that's a
**Standard**-class access pattern. Picking Nearline/Coldline/Archive for actively-used files would
mean paying a retrieval fee every time someone opens a file, and an early-deletion penalty if it's
removed before the minimum duration. (The [next project in this series](../../../../intermediate/gcp/gcp-storage-security-lifecycle/README.md)
covers **lifecycle rules** that automatically move aging objects to cheaper classes.)

---

## 3.3 Bucket Location — Single-Region vs. Multi-Region

| Location type | What it means | Trade-off |
|-----------------|----------------|-----------|
| **Single-region** (e.g. `us-east1`) | Data stored redundantly across zones within one region | Cheaper; fine if all readers are in/near one region |
| **Multi-region** (e.g. `us`) | Data replicated across multiple regions on the continent | Higher availability and lower latency for a geographically spread audience; costs more |

Meridian's document portal is used by one regional office, and this repo's GCP convention is
`us-east1` throughout. A **single-region** bucket in `us-east1` is the right (and cheaper) choice
here — there's no distributed user base to justify multi-region redundancy.

---

## 3.4 Uniform Bucket-Level Access

Cloud Storage has two access models:

| Model | How it works |
|-------|--------------|
| **Fine-grained (legacy ACLs)** | Individual objects can carry their own per-object ACLs *in addition to* the bucket's IAM policy — two systems governing the same data, which is easy to get out of sync |
| **Uniform bucket-level access** | **IAM only.** Every object in the bucket is governed by the bucket's IAM policy, full stop. No per-object ACL commands work while it's enabled |

Uniform access is simpler to reason about — "who can access this bucket" has exactly one source of
truth — and it's what this project uses. (Trying to run a legacy ACL command against a uniform
bucket produces a specific error; see [troubleshooting.md](../troubleshooting.md).)

---

## 3.5 Console — Create the Bucket

1. Open **☰ → Cloud Storage → Buckets** → **+ Create**.
2. Fill in the form:

   | Field | Value |
   |-------|-------|
   | Name | `meridian-docs-<PROJECT_ID>` (use your actual project ID) |
   | Location type | **Region** |
   | Location | `us-east1` |
   | Storage class | **Standard** |
   | Access control | **Uniform** |
   | Protection tools | Leave at defaults (none needed for this lab) |

3. Click **Create**.

---

## 3.6 gcloud CLI (Alternative)

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export BUCKET="meridian-docs-${PROJECT_ID}"

gcloud storage buckets create "gs://${BUCKET}" \
  --location=us-east1 \
  --default-storage-class=STANDARD \
  --uniform-bucket-level-access
```

Verify:

```bash
gcloud storage buckets describe "gs://${BUCKET}" \
  --format="value(name,location,storageClass)"
```

Expected output:

```
meridian-docs-my-networking-labs-1234  US-EAST1  STANDARD
```

---

## 3.7 Why This Matters

- **The project ID suffix solves the global-uniqueness problem deterministically** — no random
  digits to remember, and no collisions with anyone else's bucket.
- **Standard + single-region matches the actual access pattern.** Picking a cheaper class or a
  wider location "just in case" adds cost and complexity the workload doesn't need.
- **Uniform bucket-level access removes an entire class of misconfiguration** — a stray per-object
  ACL that grants more access than the bucket's IAM policy intends. With uniform access, the IAM
  policy is the *only* thing to review.

---

## Checkpoint

- [ ] `meridian-docs-<PROJECT_ID>` exists and is visible under Cloud Storage → Buckets
- [ ] Location is `us-east1`, storage class is `STANDARD`
- [ ] Uniform bucket-level access is **enabled**
- [ ] You can explain why Standard (not Nearline/Coldline/Archive) fits this workload

---

**Next:** [Step 4 — Object Permissions & Impersonation](./04-object-permissions-and-impersonation.md)
