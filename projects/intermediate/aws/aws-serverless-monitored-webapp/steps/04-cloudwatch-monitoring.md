# Step 4 — CloudWatch: Logs, Alarms, Dashboard

Lambda is wired to CloudWatch out of the box — every invocation publishes **Invocations,
Errors, Duration, Throttles** and writes logs automatically (that's what the execution role
from Step 1 is for). Here you'll read the logs and add alarms on the metrics that matter for
serverless: **errors** and **duration**.

---

## 4.1 Read the Logs

1. **CloudWatch → Log groups → `/aws/lambda/serverless-webapp`**.
2. Open the latest log stream. Each invocation shows `START`, your output, and an `END` /
   `REPORT` line. The **REPORT** line includes `Duration`, `Billed Duration`, `Memory Size`,
   and `Max Memory Used` — the serverless equivalent of the EC2 project's CPU/memory metrics.

> No CloudWatch agent to install here — unlike EC2, Lambda reports memory automatically in
> every REPORT line.

---

## 4.2 Console — Alarm on Errors

1. **CloudWatch → Alarms → Create alarm → Select metric**.
2. **Lambda → By Function Name → `serverless-webapp` → Errors** → Select metric.
3. Conditions:

   | Field | Value |
   |-------|-------|
   | Statistic | **Sum** |
   | Period | 1 minute |
   | Threshold | **Greater than or equal to 1** |
   | Datapoints to alarm | 1 of 1 |

4. Notification: SNS topic (you'll create it in Step 5 — come back, or use Boto3 in 4.4).
   **Alarm name:** `serverless-webapp-errors`. **Create alarm.**

---

## 4.3 Console — Alarm on Duration (p95)

1. **Create alarm → Lambda → `serverless-webapp` → Duration**.
2. Set **Statistic = p95**, Period 1 min, **Greater than 3000** (ms), 2 of 2 datapoints.
3. **Alarm name:** `serverless-webapp-slow`. **Create alarm.**

> Why p95, not Average? A serverless app can have a fast median but a slow tail (cold starts,
> the occasional heavy request). p95 catches the tail that average hides.

---

## 4.4 Automation — Alarms + Dashboard in One Command

`scripts/setup_monitoring.py` creates the SNS topic (Step 5), both alarms, **and** a
dashboard (Invocations/Errors/Duration/API-5xx) in one idempotent run:

```bash
pip install boto3
python scripts/setup_monitoring.py \
  --function-name serverless-webapp \
  --api-id abc123 \
  --email you@example.com
```

This is the serverless counterpart to the EC2 project's automation script — same plumbing,
different metrics.

---

## 4.5 Trip the Duration Alarm

```bash
API=https://abc123.execute-api.us-east-1.amazonaws.com
for i in $(seq 1 5); do curl -s "$API/api/load?seconds=5" >/dev/null; done
```

Each call runs ~5 s, above the 3,000 ms p95 threshold. Within a couple of minutes
`serverless-webapp-slow` flips to **In alarm** — and Step 5 turns that into an email.

---

## Checkpoint

- [ ] You found `Duration` / `Max Memory Used` in the log group's REPORT lines
- [ ] Alarm `serverless-webapp-errors` (Sum Errors ≥ 1) exists
- [ ] Alarm `serverless-webapp-slow` (p95 Duration > 3000 ms) exists
- [ ] (Optional) `setup_monitoring.py` created the dashboard `serverless-webapp-monitoring`
- [ ] Driving `/api/load?seconds=5` flips the slow alarm to **In alarm**

---

**Next:** [Step 5 — SNS Alerts](./05-sns-alerts.md)
