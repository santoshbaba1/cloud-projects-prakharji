# Cost Guide — S3 + CloudFront Static Website

This guide breaks down every AWS charge you can incur while completing this project.
The short version: **for a learning project this size, the cost is effectively $0.00** —
it fits comfortably inside the AWS Free Tier. Prices below are for **us-east-1** /
CloudFront's global pricing and are based on AWS public pricing.

---

## Services Used and Their Pricing Model

| Service | Pricing Model | Free Tier |
|---------|--------------|-----------|
| Amazon S3 | Per GB stored + per 1,000 requests + data transfer | 5 GB storage, 20,000 GET, 2,000 PUT/month (12-month free tier) |
| Amazon CloudFront | Per GB data transfer out + per 10,000 requests | **1 TB out + 10M requests/month — always free** |
| Cache invalidations | Per invalidation path | First **1,000 paths/month free** |
| Origin Access Control | Free | Always free |
| Bucket policy / IAM | Free | Always free |

---

## Service-by-Service Breakdown

### 1. Amazon S3

You store two tiny HTML files (a few kilobytes total) and make a handful of requests.

| Action | Price | This Project |
|--------|-------|--------------|
| Storage | $0.023 per GB / month | ~0.000003 GB → **$0.00** |
| PUT/COPY/POST requests | $0.005 per 1,000 | 2 uploads → **$0.00** |
| GET requests | $0.0004 per 1,000 | CloudFront fetches each file once per edge → **$0.00** |
| Data transfer **to CloudFront** | **$0.00** (free) | S3 → CloudFront transfer is always free |

> **Key point:** data transfer from S3 *to CloudFront* is **free**. You only pay for data
> transfer *out of CloudFront* to the internet — and that has a huge free tier (next).

---

### 2. Amazon CloudFront

CloudFront's **perpetual free tier** (not just the first 12 months) covers:

| Allowance | Free Tier |
|-----------|-----------|
| Data transfer out to internet | **1 TB per month** |
| HTTP/HTTPS requests | **10,000,000 per month** |

| Action | Price (beyond free tier) | This Project |
|--------|--------------------------|--------------|
| Data transfer out | ~$0.085 per GB (first 10 TB, North America/Europe) | A few KB of test traffic → **$0.00** |
| HTTPS requests | ~$0.01 per 10,000 | A few dozen requests → **$0.00** |

A learning project sends maybe a few megabytes total — about **0.0000001%** of the free tier.

---

### 3. Cache Invalidations

| Action | Price | This Project |
|--------|-------|--------------|
| Invalidation path | First **1,000 paths/month free**, then $0.005/path | 1–2 invalidations of `/*` → **$0.00** |

> `/*` counts as **one path**, no matter how many files it clears.

---

### 4. Origin Access Control, Bucket Policy, IAM

| Item | Cost |
|------|------|
| Origin Access Control | Free |
| S3 bucket policy | Free |
| IAM | Free |

---

## Cost by Scenario

| Scenario | S3 | CloudFront | Invalidations | Total |
|----------|----|-----------|--------------|-------|
| Complete the project (test traffic) | $0.00 | $0.00 | $0.00 | **$0.00** |
| Leave everything running idle for a month | ~$0.00 | $0.00 | $0.00 | **~$0.00** |
| Real low-traffic blog (~10 GB out/month) | ~$0.01 | $0.00 (within 1 TB) | $0.00 | **~$0.01/month** |

> Unlike compute services (EC2, Fargate), **there is no hourly charge** for an idle
> CloudFront distribution or for files sitting in S3. The risk of "forgetting to turn it
> off" is essentially zero here.

---

## AWS Free Tier Summary

| Service | Free Tier Allowance |
|---------|---------------------|
| Amazon S3 | 5 GB storage, 20,000 GET, 2,000 PUT per month (first 12 months) |
| Amazon CloudFront | 1 TB data transfer out + 10M requests per month (**always free**) |
| CloudFront invalidations | 1,000 paths per month (**always free**) |

---

## What You Will NOT Be Charged For

- S3 → CloudFront data transfer (always free)
- Creating the CloudFront distribution or leaving it idle
- The Origin Access Control
- The bucket policy or IAM
- AWS Management Console usage
- Your first 1,000 invalidation paths each month

---

## Cleanup Reminder

Because nothing here bills hourly, cleanup is about tidiness rather than cost. Still,
complete [Step 5 — Cleanup](steps/05-cleanup.md) to remove the distribution, bucket, and
OAC so you don't accumulate stray resources across projects.
