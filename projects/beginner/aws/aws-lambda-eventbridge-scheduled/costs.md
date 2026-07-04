# Costs — Lambda on a Schedule with EventBridge

Everything here is **pay-per-use** and tiny. An idle project costs **$0**; even left running,
a heartbeat is fractions of a cent. Prices are list price in `us-east-1`.

---

## Service-by-Service

| Service | Unit price (after free tier) | Free tier | Your likely usage | Cost |
|---------|------------------------------|-----------|-------------------|------|
| **EventBridge — scheduled rules** | Scheduled rules on the default bus are **free** | — | 1 rule firing every 5 min | **$0** |
| **AWS Lambda — requests** | $0.20 / million | 1M req/month (always) | ~8,600/month at 5-min rate | **~$0** |
| **AWS Lambda — compute** | $0.0000166667 / GB-s | 400,000 GB-s/month (always) | Sub-second @128 MB | **~$0** |
| **CloudWatch Logs** | $0.50 / GB ingested | 5 GB/month | Kilobytes | **~$0** |
| **SNS — email** | $0 for the first 1,000 email notifications/month | 1,000 emails/month | A few hundred | **~$0** |
| **CloudWatch alarm** (optional) | $0.10 / alarm / month | 10 alarms free | 1 | **$0** |

> **Note:** *EventBridge custom-event* publishing is billed at $1.00/million events, but
> **scheduled rules don't publish custom events** — they're free. You only pay for what the
> target (Lambda) does.

---

## What Could Surprise You

- **A `rate(1 minute)` schedule** during testing is still well within free tier (~43,000
  invokes/month), but switch back to a sane interval (or delete the rule) when done.
- **SNS email volume:** every run emails you. At `rate(5 minutes)` that's ~288 emails/day.
  Free for the first 1,000/month, then $2 per 100,000 — but mostly it's just an annoying inbox.
  Lengthen the interval or skip Step 4 if you don't want the mail.

---

## Left Running?

There is **no hourly charge** — no NAT, no load balancer, no idle compute. The only "cost" of
forgetting cleanup is a function that keeps firing (and emailing). Still, run
[Step 6 — Cleanup](steps/06-cleanup.md) to stop the noise.

**Bottom line: a full run of this project costs ~$0.00.**
