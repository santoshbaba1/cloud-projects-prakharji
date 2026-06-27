# Costs — Monolith → Serverless Migration

Region **us-east-1**. The migration's headline lesson *is* a cost lesson: the monolith bills
while idle, the serverless target does not.

---

## Service-by-service

### EC2 (the monolith — temporary)

| Item | Rate | Notes |
|------|------|-------|
| `t3.micro` On-Demand | ~$0.0104 / hr | **Free tier:** 750 hrs/mo for 12 months |
| EBS gp3 root (8 GB) | ~$0.08 / GB-mo | A stopped instance still pays for this |

A few hours of `t3.micro` ≈ **$0.02–0.05** (or $0 under free tier). **This is the only resource
that bills while idle** — stop/terminate it in Step 7/8.

### Lambda (the new compute)

| Item | Rate | Notes |
|------|------|-------|
| Requests | $0.20 / M | **Free tier:** 1M requests/mo, always |
| Duration | $0.0000166667 / GB-s | **Free tier:** 400,000 GB-s/mo, always |

A workshop's worth of invokes: **$0.00**.

### API Gateway (HTTP API)

| Item | Rate | Notes |
|------|------|-------|
| Requests | $1.00 / M | **Free tier:** 1M/mo for 12 months |

A few hundred requests: **$0.00**.

### DynamoDB (on-demand)

| Item | Rate | Notes |
|------|------|-------|
| Write request units | $1.25 / M | **Free tier:** 25 WCU equiv |
| Read request units | $0.25 / M | **Free tier:** 25 RCU equiv |
| Storage | $0.25 / GB-mo | **Free tier:** 25 GB |

**No hourly charge.** An idle table costs nothing — the opposite of the EC2 box.

### CloudWatch

| Item | Rate | Notes |
|------|------|-------|
| Logs ingest | $0.50 / GB | First 5 GB/mo free |

Function logs at this scale: **$0.00**.

---

## The point, as a formula

```
Monthly cost (monolith)  ≈  730 hrs × $0.0104  =  ~$7.60   (even at zero traffic)
Monthly cost (serverless) ≈  requests × tiny    ≈  ~$0.00   (at zero traffic)
```

The serverless architecture converts a **fixed** cost (instance-hours) into a **variable** one
(per request). For a spiky, often-idle store, that's a large saving — and it's why
"scale to zero" is a real architectural property, not a slogan.

---

## Typical total for this lab

**Under $0.25**, essentially all of it EC2 hours — and $0 if you're inside the EC2 free tier.

## Left-running warning ⚠️

- **EC2 `bookstore-monolith`** — the one thing that keeps billing. Stop it the moment cutover
  is verified (Step 7); terminate it in cleanup (Step 8).
- A **stopped** instance still pays for its EBS volume — terminate to stop even that.
- DynamoDB on-demand and Lambda cost nothing idle, but delete them in Step 8 anyway for a
  clean account.
