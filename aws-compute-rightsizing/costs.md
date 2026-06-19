# Costs — EC2 Compute Rightsizing

The irony of a cost-optimization project is that **its own demo instances are the only real
cost**. Everything else is free at this scale. Prices are list price in `us-east-1`.

---

## Service-by-Service

| Service | Unit price (after free tier) | Free tier | Your likely usage | Cost |
|---------|------------------------------|-----------|-------------------|------|
| **EC2 — t3.micro** | ~$0.0104 / hr | 750 hrs/month for 12 months | 2–3 instances for ~1 hr | **~$0** (Free Tier) or ~$0.03/hr |
| **EBS — gp3 root** | $0.08 / GB-month | 30 GB/month for 12 months | ~8 GB × hours | **~$0** |
| **AWS Lambda** | $0.20 / M req + compute | 1M req + 400k GB-s/month | a few invokes | **~$0** |
| **CloudWatch — metrics** | basic EC2 metrics free | — | reads only | **$0** |
| **CloudWatch — GetMetricStatistics** | $0.01 / 1,000 calls | — | a few dozen | **~$0** |
| **EventBridge — scheduled rules** | Free | — | 1 rule | **$0** |
| **SNS — email** | $0 for email; $0.50/M HTTP | 1,000 email/month | a few | **~$0** |
| **AWS Compute Optimizer** | **Free** | — | enrollment + reads | **$0** |

> **Free Tier vs not:** If your account is older than 12 months, those `t3.micro` hours cost about
> **1¢/hour each**. Three instances for an hour is roughly **3¢** total. Still trivial — *as long
> as you terminate them.*

---

## What Could Surprise You

- **Forgetting to terminate.** Two `t3.micro` left running for a month outside the Free Tier is
  ~$15. That dwarfs every other line item here combined. [Step 7](steps/07-cleanup.md) is the
  whole ballgame.
- **A resize that fails mid-cycle.** If `modify-instance-attribute` errors after the stop, the
  instance is left **stopped** (you pay for EBS, not compute). Re-run or start it manually — it
  won't silently cost you compute, but a stopped instance still holds its EBS volume.
- **Bigger demo types.** If you swap the `t3.micro`s for `t3.small`/`t3.large` to see real
  downsize recommendations, you leave the Free Tier — keep those short-lived.

---

## The Point of the Project

This lab *spends* a few cents to teach you how to *save* dollars. In a real account the same
function routinely finds idle `m5.large`s ($70/mo each) that should be `t3.medium` or stopped
entirely — the savings are real and recurring. The cost of *running the optimizer* (pennies of
Lambda) is noise against what it finds.

---

## Left Running?

Terminate the EC2 instances and you're at **$0/hr**. The Lambda, rule, topic, and Compute
Optimizer enrollment have **no standing charge**. Still, run [Step 7](steps/07-cleanup.md) to keep
the account tidy.

**Bottom line: finish in one sitting and clean up → ~$0.00–$0.10.**
