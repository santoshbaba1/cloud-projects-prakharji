# Step 5 — Application Load Balancer

The ALB is the single public entry point. It listens on port 80, health-checks each
instance on `/health`, and forwards healthy traffic to the app on port 5000. We create the
**target group** first (the ASG will register instances into it in Step 6), then the ALB
and its listener.

---

## 5.1 Console — Create the Target Group

1. **EC2 console → Target Groups → Create target group**.

   | Field | Value |
   |-------|-------|
   | Target type | **Instances** |
   | Name | `webapp-tg` |
   | Protocol / Port | HTTP / **5000** |
   | VPC | `webapp-vpc` |
   | Health check path | `/health` |

2. Under **Advanced health check settings**:

   | Field | Value | Why |
   |-------|-------|-----|
   | Healthy threshold | 2 | 2 good checks → mark healthy quickly |
   | Unhealthy threshold | 2 | 2 bad checks → pull it out fast |
   | Interval | 15 s | How often the ALB polls `/health` |
   | Success codes | 200 | Our `/health` returns 200 |

3. **Create target group**. Don't register any targets — the ASG does that in Step 6.

---

## 5.2 Console — Create the Load Balancer

1. **Load Balancers → Create load balancer → Application Load Balancer**.

   | Field | Value |
   |-------|-------|
   | Name | `webapp-alb` |
   | Scheme | **Internet-facing** |
   | IP address type | IPv4 |
   | VPC | `webapp-vpc` |
   | Mappings | Both **public** subnets (`webapp-public-a`, `webapp-public-b`) |
   | Security group | `alb-sg` (remove the default) |

2. **Listeners and routing:** Protocol **HTTP**, Port **80**, **Forward to** `webapp-tg`.
3. **Create load balancer**. Wait until **State = Active** (1–2 minutes).
4. Copy the **DNS name** (e.g. `webapp-alb-123456789.us-east-1.elb.amazonaws.com`).

---

## 5.3 AWS CLI (Alternative)

```bash
REGION=us-east-1
# VPC_ID, PUB_A, PUB_B, ALB_SG from earlier steps

TG_ARN=$(aws elbv2 create-target-group --name webapp-tg \
  --protocol HTTP --port 5000 --vpc-id $VPC_ID --target-type instance \
  --health-check-path /health --healthy-threshold-count 2 \
  --unhealthy-threshold-count 2 --health-check-interval-seconds 15 \
  --query 'TargetGroups[0].TargetGroupArn' --output text --region $REGION)

ALB_ARN=$(aws elbv2 create-load-balancer --name webapp-alb \
  --subnets $PUB_A $PUB_B --security-groups $ALB_SG --scheme internet-facing \
  --type application --query 'LoadBalancers[0].LoadBalancerArn' --output text --region $REGION)

aws elbv2 create-listener --load-balancer-arn $ALB_ARN \
  --protocol HTTP --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN --region $REGION

aws elbv2 describe-load-balancers --load-balancer-arns $ALB_ARN \
  --query 'LoadBalancers[0].DNSName' --output text --region $REGION
echo "TG_ARN=$TG_ARN  ALB_ARN=$ALB_ARN"
```

> **Save `TG_ARN`** — the ASG needs it in Step 6. Also note the **ALB ARN suffix** (the
> part after `loadbalancer/`, e.g. `app/webapp-alb/0123...`) for the dashboard in Step 7.

---

## Checkpoint

- [ ] Target group `webapp-tg` (HTTP 5000, health check `/health`, 200) exists
- [ ] ALB `webapp-alb` is **Active**, internet-facing, in both public subnets, using `alb-sg`
- [ ] Listener on port 80 forwards to `webapp-tg`
- [ ] You saved the ALB DNS name, `TG_ARN`, and the ALB ARN suffix
- [ ] Targets are still empty (expected until Step 6)

---

**Next:** [Step 6 — Auto Scaling Group](./06-auto-scaling-group.md)
