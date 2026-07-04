# Step 6 — Auto Scaling Group

The ASG turns "a launch template" into "a self-healing, elastic fleet". It keeps a desired
number of instances running across both AZs, registers them into the target group, replaces
unhealthy ones, and scales out when CPU climbs.

---

## 6.1 Console — Create the ASG

1. **EC2 console → Auto Scaling Groups → Create Auto Scaling group**.
2. **Name:** `webapp-asg`. **Launch template:** `webapp-lt` (Latest version). Next.
3. **Network:**
   - VPC: `webapp-vpc`
   - Subnets: both **private** subnets (`webapp-private-a`, `webapp-private-b`)

   > Instances go in **private** subnets — no public IP. The ALB (public) reaches them.

4. **Load balancing:** Attach to an existing load balancer → **Choose from target groups**
   → `webapp-tg`.
5. **Health checks:** Turn on **ELB** health checks (in addition to EC2). Grace period
   `120` seconds — gives user-data time to finish before the ALB starts judging health.
6. **Group size:**

   | Setting | Value |
   |---------|-------|
   | Desired capacity | 2 |
   | Minimum capacity | 1 |
   | Maximum capacity | 4 |

7. **Scaling policy → Target tracking:** Metric **Average CPU utilization**, Target value
   **50**. (The ASG adds instances to keep average CPU near 50%.)
8. Next through the rest → **Create Auto Scaling group**.

---

## 6.2 Verify Traffic Flows End to End

1. Wait ~3 minutes. In **Target Groups → `webapp-tg` → Targets**, both instances should
   become **healthy**.
2. Open `http://<ALB-DNS-name>/` in a browser — you should see the JSON home response.
3. Refresh `http://<ALB-DNS-name>/api/info` a few times; the `instance_id` should alternate
   between the two instances — proof the ALB is load-balancing.

---

## 6.3 Watch It Scale (preview of monitoring)

Generate load against the CPU-burning endpoint and watch the ASG react:

```bash
ALB=http://<ALB-DNS-name>
# fire 20 parallel 8-second CPU burns
for i in $(seq 1 20); do curl -s "$ALB/api/load?seconds=8" >/dev/null & done; wait
```

Within a few minutes the **Activity** tab of the ASG shows a scale-out event. You'll wire
the *alarm + email* side of this in Steps 7–8.

---

## 6.4 AWS CLI (Alternative)

```bash
REGION=us-east-1
# PRIV_A, PRIV_B, TG_ARN from earlier steps

aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name webapp-asg \
  --launch-template LaunchTemplateName=webapp-lt,Version='$Latest' \
  --vpc-zone-identifier "$PRIV_A,$PRIV_B" \
  --target-group-arns $TG_ARN \
  --health-check-type ELB --health-check-grace-period 120 \
  --min-size 1 --max-size 4 --desired-capacity 2 --region $REGION

aws autoscaling put-scaling-policy \
  --auto-scaling-group-name webapp-asg \
  --policy-name cpu-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "PredefinedMetricSpecification": {"PredefinedMetricType": "ASGAverageCPUUtilization"},
    "TargetValue": 50.0
  }' --region $REGION
```

---

## Checkpoint

- [ ] ASG `webapp-asg` runs in both **private** subnets
- [ ] Desired 2 / Min 1 / Max 4
- [ ] Attached to `webapp-tg`; ELB health checks on; grace period 120 s
- [ ] Both targets show **healthy**
- [ ] ALB DNS serves the app; `instance_id` alternates across refreshes
- [ ] Target-tracking policy on Average CPU @ 50% exists

---

**Next:** [Step 7 — CloudWatch Monitoring](./07-cloudwatch-monitoring.md)
