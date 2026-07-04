# Costs — Scheduled EC2 Start/Stop

This project's automation (Lambda + EventBridge) is effectively free. The only thing that can
cost money is **the EC2 instance you launch** — which is why cleanup matters here more than
anywhere else in the series. Prices are list price in `us-east-1`.

---

## Service-by-Service

| Service | Unit price (after free tier) | Free tier | Your likely usage | Cost |
|---------|------------------------------|-----------|-------------------|------|
| **EC2 — t2.micro compute** | ~$0.0116 / hour | 750 hours/month for 12 months | A few hours during the lab | **~$0** (if in free tier) |
| **EBS — gp3 root volume** | ~$0.08 / GB-month | 30 GB-month for 12 months | 8 GB for a few hours | **~$0–$0.01** |
| **AWS Lambda** | $0.20 / M requests + compute | 1M req + 400k GB-s/month | A handful of invokes | **~$0** |
| **EventBridge — scheduled rules** | Free | — | 2 rules | **$0** |
| **CloudWatch Logs** | $0.50 / GB | 5 GB/month | Kilobytes | **~$0** |

---

## What Could Surprise You

- **A forgotten *running* instance** is the real risk. Outside the free tier a `t2.micro` is
  ~$8.50/month; a larger type is far more. Terminate in [Step 6](steps/06-cleanup.md).
- **A *stopped* instance is NOT free** — its EBS volume keeps billing (a few cents). Stopping
  saves *compute*, not storage. Only **termination** stops all charges.
- **Two instances** (if you launched the untagged one) bill independently. Terminate both.
- **Free-tier hours are shared** across all your `t2.micro`/`t3.micro` usage that month — if
  you've already used them elsewhere, this lab's instance is billed.

---

## The Point of This Project

The savings are real and the opposite of a cost: powering dev/test instances off ~12 hours a
day roughly **halves** their compute bill. One small, free Lambda can save tens to hundreds of
dollars a month across a fleet. The automation pays for itself many times over — *as long as
you also clean up this lab's demo instance.*

**Bottom line: ~$0.00–$0.01 if you terminate the instance the same day.**
