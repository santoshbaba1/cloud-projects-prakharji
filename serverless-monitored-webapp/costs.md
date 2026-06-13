# Cost Breakdown — Serverless Monitored Web App

All prices **us-east-1**, as of 2025. The headline: **at workshop scale this project is
effectively free**, and it costs **~$0 when idle** — the opposite of the EC2 project's
always-on NAT Gateway + ALB.

---

## Per-Service Costs

### AWS Lambda

| Item | Rate | Free tier (always free) |
|------|------|--------------------------|
| Requests | $0.20 per **1M** requests | First **1M requests/month** free |
| Compute | $0.0000166667 per **GB-second** | First **400,000 GB-seconds/month** free |

A few thousand short invocations (even the 5-second `/api/load` ones) stay deep inside the
free tier → **$0**. Example: 10,000 invokes × 0.2 s × 128 MB ≈ 256 GB-s, vs 400,000 free.

### API Gateway (HTTP API)

| Item | Rate | Free tier |
|------|------|-----------|
| Requests | **$1.00 per 1M** | First **1M requests/month free for 12 months** |

> HTTP API is ~70% cheaper than the older REST API ($3.50/1M). We chose it deliberately.

### CloudWatch

| Item | Rate | Free tier |
|------|------|-----------|
| Alarms | $0.10 / alarm / mo | First 10 free (we use 2) |
| Dashboard | $3.00 / dashboard / mo | First 3 free (we use 1) |
| Logs | $0.50 / GB ingested | First 5 GB/mo free |

### SNS / CloudTrail / IAM

| Service | Cost |
|---------|------|
| **SNS** | First 1,000 email notifications/month **free** |
| **CloudTrail** | One management-events trail **free**; S3 log storage is pennies |
| **IAM / OIDC** | **Free** |

---

## Total Cost Scenarios

| Scenario | Lambda | API GW | CW/SNS/CT | Total |
|----------|--------|--------|-----------|-------|
| **Workshop session** | $0 (free tier) | $0 (free tier) | $0 (free tier) | **~$0.00** |
| **Left "running" 1 month, no traffic** | $0 | $0 | $0 | **~$0.00** |
| **1M requests in a month (post-free-tier)** | ~$0.20 + compute | ~$1.00 | ~$0 | **~$1.20+** |

---

## Why "Left Running" Is Cheap Here

The EC2 project's NAT Gateway (~$32/mo) and ALB (~$16/mo) bill **24/7 whether or not anyone
visits**. This project has **no always-on infrastructure**: Lambda and API Gateway cost
money only when a request arrives. Leaving it deployed overnight costs essentially nothing.

**The one thing to tidy up:** if you created an extra **CloudWatch dashboard** beyond the
free 3, or a **CloudTrail S3 bucket** that accumulates logs, delete them in
[Step 8 — Cleanup](steps/08-cleanup.md). Otherwise there's no urgent cost clock ticking —
which is itself one of the biggest advantages of serverless.

---

## Cost Comparison vs. the EC2 Project

| | EC2 project | This project |
|--|-------------|--------------|
| Idle monthly cost | **~$48** (NAT + ALB) | **~$0** |
| Cost driver | Time (always on) | Requests (pay per use) |
| Cheapest at | High, steady traffic | Low / spiky traffic |

This trade-off — **pay-for-time vs. pay-for-use** — is the core economic lesson of the two
projects.
