# Costs — Scheduled S3 Housekeeping

Everything here is pay-per-use and tiny. A handful of small objects and a daily Lambda run cost
**~$0** and stay inside the Free Tier. Prices are list price in `us-east-1`.

---

## Service-by-Service

| Service | Unit price (after free tier) | Free tier | Your likely usage | Cost |
|---------|------------------------------|-----------|-------------------|------|
| **S3 — storage** | $0.023 / GB-month (Standard) | 5 GB for 12 months | A few KB | **~$0** |
| **S3 — PUT/COPY/POST/LIST** | $0.005 / 1,000 requests | 2,000 PUT + 20,000 GET/month | Dozens | **~$0** |
| **S3 — GET/DELETE** | GET $0.0004/1,000; DELETE free | 20,000 GET/month | Dozens | **~$0** |
| **AWS Lambda** | $0.20 / M req + compute | 1M req + 400k GB-s/month | A few invokes/day | **~$0** |
| **EventBridge — scheduled rules** | Free | — | 1 rule | **$0** |
| **CloudWatch Logs** | $0.50 / GB | 5 GB/month | Kilobytes | **~$0** |

> **DELETE requests are free**; **COPY counts as a PUT** (so archiving an object = 1 PUT + 1 free
> DELETE). At lab scale this rounds to nothing.

---

## What Could Surprise You

- **Archiving doesn't shrink storage by itself.** Moving `active/ → archive/` keeps the bytes —
  it just relocates them. To actually reduce cost, pair archiving with cheaper storage classes
  (see below) or a real `delete`.
- **Lots of tiny objects = lots of requests.** On a real bucket, the cost is dominated by
  per-request charges (LIST/COPY/PUT), not storage. Batching matters at scale.
- **Forgotten test loops.** Re-seeding + `rate(2 minutes)` during testing is free-tier, but
  switch back to the daily cron so you're not running needlessly.

---

## Lambda vs. S3 Lifecycle Rules

For pure age-based **transition or expiration**, native **S3 Lifecycle rules** are free, require
no code, and run server-side — prefer them when your logic is "objects older than N days →
delete / move to Glacier." Reach for a **Lambda** (this project) when you need *custom* logic:
conditional rules, cross-prefix moves with renaming, notifications, or touching other services in
the same run. This project teaches the Lambda path because it generalizes; for simple expiry,
Lifecycle is the cheaper, sturdier default.

---

## Left Running?

No hourly charge. The only residual cost of skipping cleanup is a few KB of S3 storage and a
daily no-op invoke — still ~$0. Run [Step 6 — Cleanup](steps/06-cleanup.md) anyway to keep your
account tidy.

**Bottom line: a full run of this project costs ~$0.00.**
