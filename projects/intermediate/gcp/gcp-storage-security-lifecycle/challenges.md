# Challenges — GCP Storage Security & Lifecycle

Extend the project past the base lab. Each challenge assumes the buckets, key, and roles from the main
steps are still up (or that you'll recreate the specific pieces you need). Clean up any extras
afterward.

---

## 1. Trigger a Cloud Function on Object Finalize

Add a **Cloud Function (2nd gen)** subscribed to the `google.cloud.storage.object.v1.finalized` event
on `meridian-reports-<PROJECT_ID>`, so a new report upload automatically triggers processing (even
just logging the object name and size to start).

- Note that this function's service account needs its **own** narrow IAM grant on the bucket — resist
  the temptation to reuse `MeridianReportsUploader` for a completely different job.
- **Question:** Why is an event-driven trigger a better fit here than a polling job that lists the
  bucket every few minutes?

---

## 2. Try Object Replication to a Second Bucket/Region

Cloud Storage doesn't have a single-click "replicate this bucket" like some other providers — instead,
look at **Storage Transfer Service**'s bucket-to-bucket transfer jobs configured for ongoing sync, or
a Pub/Sub-notification-driven copy function.

- Replicate `meridian-product-photos-<PROJECT_ID>` to a bucket in a second region (e.g. `us-west1`).
- **Question:** What's the actual RPO of your replication approach — seconds, minutes, or "whenever
  the next scheduled job runs"?

---

## 3. Use Storage Transfer Service to Import a Public Dataset

Point **Storage Transfer Service** at a public GCS bucket (e.g. one of Google's public datasets) and
import a small subset into a throwaway bucket in your project.

- Compare this to writing your own `gcloud storage cp` loop — what does the managed transfer job give
  you (retries, scheduling, integrity checks) that a shell script doesn't?
- **Cost note:** clean up the imported data immediately; public datasets can be large.

---

## 4. Mount a Bucket Locally With Cloud Storage FUSE

Install `gcsfuse` and mount `meridian-reports-<PROJECT_ID>` as a local filesystem path.

- Read and write a file through the mount, then verify it shows up via `gcloud storage ls`.
- **Question:** FUSE makes object storage *look* like a filesystem — what POSIX semantics (partial
  writes, file locking, rename) does it not actually give you underneath?

---

## 5. Tighten the IAM Condition to a Time Window

Extend the CEL expression from [Step 1](steps/01-custom-roles-and-conditions.md) so
`MeridianReportsUploader` only works during a specific window, e.g. business hours in one timezone,
using CEL's `request.time` and a date comparison.

- Try both an absolute expiry (`request.time < timestamp("2026-12-31T00:00:00Z")`) and something
  closer to a recurring window, and note which one CEL actually supports cleanly.
- **Question:** Where would a genuinely recurring (daily) time-window condition be better implemented
  — in the IAM condition itself, or somewhere else entirely?

---

## 6. Compare CMEK vs. Google-Managed Encryption — Cost and Ops Tradeoff

Create a second bucket identical to the reports bucket but left on Google-managed (default)
encryption. Run the same upload/download workload against both.

- Tabulate: extra cost (KMS key-version-month + operations), extra ops burden (key rotation policy,
  IAM grant on the service agent, key destruction procedure), and what you actually gain (revocable
  control, key access audit trail via Cloud Audit Logs on the KMS key itself).
- **Lesson:** CMEK is a real tradeoff, not a strictly-better setting — write down when you'd actually
  recommend it to a team versus when Google-managed encryption is the right call.

---

## 7. Try Autoclass Instead of Manual Lifecycle Rules

Create a bucket with **Autoclass** enabled instead of the three manual lifecycle rules from
[Step 2](steps/02-versioning-and-lifecycle-rules.md).

- Autoclass automatically moves objects between storage classes based on actual access patterns,
  rather than a fixed age schedule you define yourself.
- **Goal:** understand the tradeoff — Autoclass removes the need to hand-tune age thresholds, but
  removes the fine-grained control (and predictability) of an explicit lifecycle policy. Decide which
  one you'd actually pick for Meridian's reports bucket, and why.
