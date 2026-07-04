# Cost Breakdown — EC2 + VPC Monitored Web App

All prices are **us-east-1**, on-demand, as of 2025. Always confirm with the
[AWS Pricing Calculator](https://calculator.aws/).

---

## Per-Service Costs

### Amazon EC2 — the compute

| Item | Formula | This project (2 × t3.micro) |
|------|---------|------------------------------|
| t3.micro on-demand | $0.0104 / instance-hour | 2 × $0.0104 = **$0.021/hr** |
| Free tier | 750 hrs/month of t2/t3.micro for first 12 months | 2 instances ≈ 1,460 hrs/mo → ~half free |

> With the 12-month free tier, two t3.micro instances are *mostly* free for the first year.

### NAT Gateway — usually the biggest line item ⚠️

| Item | Rate | Notes |
|------|------|-------|
| Hourly | **$0.045 / hr** | Charged whenever it exists, traffic or not |
| Data processing | $0.045 / GB | On top of the hourly charge |
| **Monthly if left running** | **~$32.40/mo** | This is the cost people forget |

**Cheaper variant:** for a pure learning run you can skip the NAT Gateway and put the
instances in the **public** subnets (like the ECS basics project does). You lose the
"private tier" security lesson but save ~$32/mo. See challenges.md.

### Application Load Balancer

| Item | Rate | Notes |
|------|------|-------|
| Hourly | **$0.0225 / hr** | Fixed, even at zero traffic → ~$16.20/mo |
| LCU | $0.008 / LCU-hour | Negligible at workshop traffic |

### CloudWatch

| Item | Rate | Free tier |
|------|------|-----------|
| Custom metrics (memory) | $0.30 / metric / mo | First 10 metrics free |
| Alarms | $0.10 / alarm / mo | First 10 alarms free |
| Dashboards | $3.00 / dashboard / mo | First 3 dashboards free |
| Logs ingestion | $0.50 / GB | First 5 GB/mo free |

At workshop scale you stay inside every free-tier bucket → effectively **$0**.

### SNS, CloudTrail, VPC, IAM, ASG, SSM

| Service | Cost |
|---------|------|
| **SNS** | Email: first 1,000 notifications/month **free** |
| **CloudTrail** | One management-events trail **free**; S3 storage of logs is pennies |
| **VPC / IGW / route tables** | **Free** |
| **IAM / Auto Scaling / SSM Run Command** | **Free** |
| **Elastic IP** | Free *while attached* to the NAT Gateway; **$0.005/hr if left unattached** ⚠️ |

---

## Total Cost Scenarios

| Scenario | EC2 | NAT | ALB | CW/SNS/CT | Total |
|----------|-----|-----|-----|-----------|-------|
| **4-hour workshop session** | ~$0.08 | ~$0.18 | ~$0.09 | ~$0 | **~$0.40** |
| **Left running 24 hours** | ~$0.50 | ~$1.08 | ~$0.54 | ~$0 | **~$2.30** ⚠️ |
| **Left running 1 month** | ~$15 (free-tier-dependent) | ~$32 | ~$16 | ~$0 | **~$48–63/mo** ⚠️⚠️ |

---

## "I Left It Running" Warnings

1. **NAT Gateway (~$32/mo)** — the single biggest surprise charge. Delete it in cleanup.
2. **ALB (~$16/mo)** — fixed hourly charge regardless of traffic.
3. **Unattached Elastic IP ($3.60/mo)** — releasing the NAT but forgetting its EIP keeps billing.
4. **Dashboards beyond 3 / alarms beyond 10** — cheap, but they add up if you re-run often.

> Always complete [Step 11 — Cleanup](steps/11-cleanup.md) and verify in Cost Explorer the
> next day. The NAT Gateway + ALB together are ~$48/month if forgotten.
