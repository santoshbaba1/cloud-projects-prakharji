# Costs — API Gateway HTTP API + Lambda + DynamoDB

Everything here is **pay-per-request** with **no hourly charge** — an idle project costs
essentially **$0**. List prices are `us-east-1`; at workshop volume you stay in the free tier.

---

## Service-by-Service

| Service | Unit price (after free tier) | Free tier | Your likely usage | Cost |
|---------|------------------------------|-----------|-------------------|------|
| **API Gateway (HTTP)** | $1.00 / million requests | 1M req/month for 12 months | A few hundred | **~$0** |
| **AWS Lambda — requests** | $0.20 / million | 1M req/month (always) | A few hundred | **~$0** |
| **AWS Lambda — compute** | $0.0000166667 / GB-second | 400,000 GB-s/month (always) | Sub-second invokes | **~$0** |
| **DynamoDB — writes (on-demand)** | $1.25 / million WRU | 25 WRU-equiv/month (12 mo, provisioned) | A few hundred | **~$0** |
| **DynamoDB — reads (on-demand)** | $0.25 / million RRU | 25 RRU-equiv/month (12 mo, provisioned) | A few hundred | **~$0** |
| **DynamoDB — storage** | $0.25 / GB-month | 25 GB/month | Kilobytes | **~$0** |
| **CloudWatch Logs** | $0.50 / GB ingested | 5 GB ingest/month | Kilobytes | **~$0** |

> **HTTP vs REST price:** HTTP API is **$1.00/M** vs REST's **$3.50/M** — ~3.5× cheaper. The
> trade-off you accepted: no native gateway canary (you do canary at the alias instead).

---

## What Could Surprise You

- **`Scan` is the most expensive read pattern.** `GET /tasks` does a full table `Scan`. Fine
  for a tiny demo table; on a large table, prefer `Query` against a key or index (see
  [challenges.md](challenges.md) #2). Scan cost scales with table size, not result size.
- **On-demand has no idle cost** but bills *every* request. The deployment-step probe loops
  (`seq 1 50`) are a few hundred operations — free-tier territory. Don't script millions.
- **Versions, aliases, and the HTTP API itself are free to exist** — you only pay per request
  served and per item stored.

---

## Left Running?

No hourly charges anywhere — no NAT, no ALB, no provisioned capacity. A forgotten project
stays ~$0. Still, run [Step 8 — Cleanup](steps/08-cleanup.md) so the `tasks` table and stale
aliases don't linger.

**Bottom line: a full run of this project costs ~$0.00.**
