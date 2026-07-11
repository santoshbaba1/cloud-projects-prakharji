# Costs — GCP Storage Security & Lifecycle

This project is **low cost, not free-tier** — read this before you start. A Cloud KMS key bills for
simply existing (a few cents a month, prorated to fractions of a cent for a lab session), and
CMEK/versioning/lifecycle transitions all add small storage-operation charges on top of plain Cloud
Storage. Budget **$0.05–$0.15** for a full session and clean up the same day
([Step 6](steps/06-cleanup.md)). Prices are list price in `us-east1`.

---

## Service-by-Service

| Resource | Unit price | Free tier | Your usage | Cost |
|----------|-----------|-----------|------------|------|
| **Cloud Storage — Standard** | $0.020 / GB-month | 5 GB-month free (Always Free, US regions) | 4 buckets, a few KB–MB of test objects | **~$0** |
| **Cloud Storage — Nearline / Coldline** | $0.010 / $0.004 per GB-month | none | Not reached live in the lab (rules only configured) | **$0** |
| **Cloud Storage — Class A operations** | $0.005 / 1,000 ops | 5,000/month free | Uploads, IAM/lifecycle updates — dozens of ops | **~$0** |
| **Cloud Storage — Class B operations** | $0.0004 / 1,000 ops | 50,000/month free | Reads, `describe` calls — well under free tier | **~$0** |
| **Cloud KMS — active key version** | ~$0.06 / key-version / month | none | 1 key version, active for the lab's duration | **~$0.01–0.02** (prorated) |
| **Cloud KMS — operations** | $0.03 / 10,000 operations | none | A handful of encrypt/decrypt calls during upload/verify | **~$0** |
| **Egress — static website + signed URLs** | $0.085–0.12 / GB (North America) | 1 GB/month free | A few KB–MB of test downloads | **~$0** |
| **IAM custom roles / conditions** | Free | — | — | **$0** |

**Realistic session cost: $0.02 – $0.10**, almost entirely the KMS key.

---

## The Two Things That Could Cost You

1. **A forgotten, active KMS key version.** Unlike a bucket, a Cloud KMS key version keeps billing
   indefinitely at a small flat monthly rate whether or not anything uses it — and unlike a VM, there's
   no obvious "still running" signal in the Console to notice. **Destroy the key version in
   [Step 6.4](steps/06-cleanup.md)** — the keyring and key object themselves are permanent and free,
   but the version is what costs money.
2. **Noncurrent object versions left behind.** Because this project turns versioning on, a plain
   `gcloud storage rm` on the reports bucket only removes the *live* object — every prior version
   silently remains, still billed as storage, until you delete with `--all-versions`
   ([Step 6.2](steps/06-cleanup.md)).

---

## Free Tier Notes

- The **Always Free** tier covers 5 GB-month of Standard storage in US multi-/dual-regions and
  US-region buckets, plus generous monthly operation allowances — a lab session's handful of test
  objects stays comfortably inside it.
- **Cloud KMS has no free tier.** Every active key version bills from the moment it's created,
  regardless of usage. This is the one line item in this project that isn't "basically free."
- **Nearline and Coldline classes both carry a minimum storage duration** (30 and 90 days
  respectively) — deleting or transitioning an object out early still bills for the *remaining* days
  of that minimum. This lab only configures the rules; it doesn't wait long enough to trigger a real
  transition, so this cost never actually materializes here, but it's the reason production lifecycle
  policies are tuned carefully rather than set aggressively "just in case."

---

## Rule of Thumb

> Everything in this project except the **Cloud KMS key version** rounds to zero for a single lab
> session. The KMS key is the one resource that bills simply for existing — destroy the key version in
> [Step 6](steps/06-cleanup.md) and there's nothing left to forget.
