# Costs — GCP IAM & Storage Fundamentals

This project is designed to cost **$0.00** in essentially every realistic case. There's no compute,
no load balancer, no hourly-billed resource anywhere in it — the only thing that could ever bill you
is storing data, and this lab stores a few kilobytes of text files. Prices are list price in
`us-east1`.

---

## Service-by-Service

| Resource | Unit price | Always-Free allowance | Your usage | Cost |
|----------|-----------|-------------------------|------------|------|
| **Cloud Storage (Standard, us-east1)** | ~$0.020 / GB-month | **5 GB-months/month free** (regional US buckets) | A few KB across 3–4 text files | **$0** |
| **Class A operations** (create/upload) | $0.005 / 1,000 ops | 5,000 ops/month free | ~5 uploads + bindings | **$0** |
| **Class B operations** (list/get) | $0.0004 / 1,000 ops | 50,000 ops/month free | A few dozen `ls`/`describe` calls | **$0** |
| **Service accounts** | N/A | N/A | 1 (`doc-portal-sa`) | **Free — always** |
| **IAM roles, bindings, impersonation tokens** | N/A | N/A | Any number | **Free — always** |
| **Admin Activity audit logs** | N/A | N/A | Generated automatically by every step | **Free — always on, can't be disabled** |
| **Data Access audit logs** | ~$0.50 / million entries (if enabled) | — | **Not enabled in this lab** | **$0** |

---

## The Two Things That Could Cost You

1. **Leaving large files in the bucket long-term.** This lab uploads a handful of text files —
   effectively nothing. If you later used this same bucket to store gigabytes of real documents and
   forgot about it for months, standard-class storage bills continuously at ~$0.02/GB-month. Delete
   the bucket in [Step 6](steps/06-cleanup.md) when you're done with the lab.
2. **Enabling Data Access audit logs "just to see."** Step 5.1 explains why this project doesn't
   turn them on: for a bucket with any real read/write volume, Data Access logs generate a log entry
   *per object operation*, which adds up fast and bills per entry. Leave them off unless you have a
   specific compliance need to log every read.

---

## Free Tier Notes

- The **Always Free** tier gives every project 5 GB-months of regional US Standard storage per
  month, plus generous free operation quotas — this lab uses a rounding error of either.
- **IAM has no billing dimension at all.** Creating service accounts, granting roles, and
  impersonating them are unconditionally free, no matter how many you create.
- **Admin Activity logs are free and always on** — you don't pay anything to view the audit trail
  this project relies on in Step 5.

---

## Rule of Thumb

> If you finish all six steps and run cleanup, expect a bill of **$0.00**, full stop. The only way
> this project costs real money is turning it into a production system that stores large volumes of
> data or enables Data Access logging — neither of which this lab does.
