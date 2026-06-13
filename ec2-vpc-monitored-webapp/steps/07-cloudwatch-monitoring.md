# Step 7 — CloudWatch: Metrics, Alarm, Dashboard

EC2 publishes CPU, network, and disk-I/O metrics for free — but **not memory**, because
that lives inside the OS. The **CloudWatch agent** (installed by user-data) fills that gap.
Here you'll configure the agent, create a high-CPU **alarm**, and build a **dashboard**.

---

## 7.1 Push the CloudWatch Agent Config

The agent config is in `scripts/cloudwatch-agent-config.json`. It collects
`mem_used_percent` and disk usage into a custom namespace `EC2MonitoredWebApp`, and ships
`/var/log/user-data.log` to a log group.

Store the config in **SSM Parameter Store**, then have the agent fetch it on every instance:

```bash
REGION=us-east-1

aws ssm put-parameter --name "/webapp/cloudwatch-agent-config" --type String \
  --value file://scripts/cloudwatch-agent-config.json --overwrite --region $REGION

# Tell the agent on every running instance to load it (no SSH — SSM Run Command):
aws ssm send-command \
  --document-name "AmazonCloudWatch-ManageAgent" \
  --targets "Key=tag:Project,Values=webapp" \
  --parameters '{"action":["configure"],"mode":["ec2"],
    "optionalConfigurationSource":["ssm"],
    "optionalConfigurationLocation":["/webapp/cloudwatch-agent-config"],
    "optionalRestart":["yes"]}' \
  --region $REGION
```

After a minute, **CloudWatch → Metrics → All metrics → EC2MonitoredWebApp** shows
`MemoryUtilization` per instance.

---

## 7.2 Console — Create the High-CPU Alarm

1. **CloudWatch → Alarms → Create alarm → Select metric**.
2. **EC2 → By Auto Scaling Group → `webapp-asg` → CPUUtilization** → Select metric.
3. Conditions:

   | Field | Value |
   |-------|-------|
   | Statistic | Average |
   | Period | 1 minute |
   | Threshold type | Static |
   | Whenever CPUUtilization is | **Greater than 60** |
   | Datapoints to alarm | **2 out of 2** |

4. **Next → Notification:** you'll attach the SNS topic in Step 8. For now choose **Remove**
   the notification (or come back after Step 8). **Alarm name:** `webapp-high-cpu`.
5. **Create alarm.**

---

## 7.3 Console — Build the Dashboard

1. **CloudWatch → Dashboards → Create dashboard** → name `webapp-monitoring`.
2. Add three widgets (**Add widget → Line**):
   - **ASG Average CPU** — `AWS/EC2 → CPUUtilization → AutoScalingGroupName webapp-asg`
   - **Memory** — `EC2MonitoredWebApp → MemoryUtilization`
   - **ALB Request Count** — `AWS/ApplicationELB → RequestCount → LoadBalancer <alb-suffix>`
3. **Save dashboard.**

---

## 7.4 Automation — Do 7.2–7.3 in One Command (Boto3)

The Console is good for learning; in real life you script it. `scripts/setup_monitoring.py`
creates the SNS topic (Step 8), the CPU alarm, **and** the dashboard in one idempotent run:

```bash
pip install boto3
python scripts/setup_monitoring.py \
  --asg-name webapp-asg \
  --alb-arn-suffix app/webapp-alb/0123456789abcdef \
  --email you@example.com
```

Re-running it is safe — every API call is create-or-update. This single script is the
"automation" deliverable: the entire monitoring stack as repeatable code.

---

## 7.5 Trip the Alarm

```bash
ALB=http://<ALB-DNS-name>
for i in $(seq 1 20); do curl -s "$ALB/api/load?seconds=8" >/dev/null & done; wait
```

Within ~2–3 minutes `webapp-high-cpu` flips to **In alarm** (red). Leave it — Step 8 turns
that red state into an email in your inbox.

---

## Checkpoint

- [ ] CloudWatch agent config delivered via SSM; `MemoryUtilization` visible in `EC2MonitoredWebApp`
- [ ] Alarm `webapp-high-cpu` exists (Avg CPU > 60% for 2 minutes)
- [ ] Dashboard `webapp-monitoring` shows CPU, memory, and ALB request count
- [ ] (Optional) `setup_monitoring.py` ran cleanly
- [ ] Driving `/api/load` flips the alarm to **In alarm**

---

**Next:** [Step 8 — SNS Alerts](./08-sns-alerts.md)
