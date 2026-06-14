# Costs — API Gateway REST API + Lambda

Everything in this project is **pay-per-request**. Nothing runs 24/7, so an idle project
costs essentially **$0**. The numbers below are list price in `us-east-1`; at workshop volume
you stay inside the free tier.

---

## Service-by-Service

| Service | Unit price (after free tier) | Free tier | Your likely usage | Cost |
|---------|------------------------------|-----------|-------------------|------|
| **API Gateway (REST)** | $3.50 / million requests | 1M req/month for 12 months | A few hundred | **~$0** |
| **AWS Lambda — requests** | $0.20 / million requests | 1M req/month (always) | A few hundred | **~$0** |
| **AWS Lambda — compute** | $0.0000166667 / GB-second | 400,000 GB-s/month (always) | Tiny (sub-second invokes) | **~$0** |
| **CloudWatch Logs** | $0.50 / GB ingested | 5 GB ingest/month | Kilobytes | **~$0** |
| **CloudWatch metrics** | First 10 custom metrics free | — | None custom | **$0** |

> **REST vs HTTP API price:** REST is **$3.50/M**, HTTP is **$1.00/M**. We use REST here only
> for its native canary release. For a production API without that need, HTTP API (Project 2)
> is ~3.5× cheaper.

---

## What Could Surprise You

- **The `/api/load`-style stress loops** in the deployment steps (`for i in seq 1 20`) are a
  few hundred requests total — still free-tier. Don't script *millions* of probe requests.
- **Versions and aliases are free.** Publishing v1/v2 and creating `live`/`canary`/`blue`/
  `green` aliases costs nothing; they're just metadata pointers.
- **Multiple stages are free** to exist (`prod`, `staging`) — you only pay per request they
  serve.

---

## Left Running?

There is **no hourly charge** in this project — no NAT gateway, no load balancer, no
provisioned concurrency. If you forget to clean up, your bill stays ~$0. Still, do
[Step 8 — Cleanup](steps/08-cleanup.md) so stale aliases/permissions don't confuse a future
rebuild.

**Bottom line: a full run of this project costs ~$0.00.**
