# Step 4 — Schedule Start and Stop

Now wire the automation: **two** EventBridge rules pointing at the *same* function, each
passing a different **constant input** so one stops and one starts.

A realistic pattern is "stop at 8 PM, start at 8 AM, weekdays only." To see it work without
waiting hours, this walkthrough uses near-term times you can adjust.

---

## 4.1 Pick Your cron Times (UTC!)

EventBridge rules run in **UTC**. Convert your local time first. Examples:

| Intent (local US-Eastern, EDT = UTC−4) | UTC cron |
|----------------------------------------|----------|
| Stop 8:00 PM weekdays | `cron(0 0 ? * TUE-SAT *)` (00:00 UTC next day) |
| Start 8:00 AM weekdays | `cron(0 12 ? * MON-FRI *)` |

> Day-of-week shifts when your local evening crosses midnight UTC — double-check with a
> converter. For a quick test, just set times a few minutes ahead and watch.

---

## 4.2 Create the STOP Rule (Console)

1. **EventBridge** → **Rules** → **Create rule**.

   | Field | Value |
   |-------|-------|
   | Name | `ec2-stop-schedule` |
   | Rule type | **Schedule** |

2. Schedule: **A fine-grained schedule (cron)** → enter your stop cron (e.g. `cron(0 0 ? * TUE-SAT *)`).
3. **Target** → **Lambda function** → `ec2-scheduler`.
4. **Additional settings** → **Configure target input** → **Constant (JSON text)** → enter:

   ```json
   {"action": "stop"}
   ```

5. **Next** → **Create rule**. The console adds the invoke permission automatically.

---

## 4.3 Create the START Rule

Repeat 4.2 with:

| Field | Value |
|-------|-------|
| Name | `ec2-start-schedule` |
| Cron | your start time, e.g. `cron(0 12 ? * MON-FRI *)` |
| Constant input | `{"action": "start"}` |

> **Same function, two schedules, two inputs.** This is the constant-input mechanism previewed
> in Project 1 — it's what lets one function do both jobs.

---

## AWS CLI (Alternative)

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
FN_ARN=$(aws lambda get-function --function-name ec2-scheduler \
  --query 'Configuration.FunctionArn' --output text)

# --- STOP schedule ---
aws events put-rule --name ec2-stop-schedule \
  --schedule-expression "cron(0 0 ? * TUE-SAT *)"

aws lambda add-permission \
  --function-name ec2-scheduler --statement-id ec2-stop-invoke \
  --action lambda:InvokeFunction --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:${ACCOUNT_ID}:rule/ec2-stop-schedule

aws events put-targets --rule ec2-stop-schedule \
  --targets "Id"="1","Arn"="${FN_ARN}","Input"='{"action":"stop"}'

# --- START schedule ---
aws events put-rule --name ec2-start-schedule \
  --schedule-expression "cron(0 12 ? * MON-FRI *)"

aws lambda add-permission \
  --function-name ec2-scheduler --statement-id ec2-start-invoke \
  --action lambda:InvokeFunction --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:${ACCOUNT_ID}:rule/ec2-start-schedule

aws events put-targets --rule ec2-start-schedule \
  --targets "Id"="1","Arn"="${FN_ARN}","Input"='{"action":"start"}'
```

> Each rule needs its **own** `add-permission` statement-id and its **own** `source-arn`. A
> single permission for one rule does not cover the other.

---

## 4.4 Quick End-to-End Test Without Waiting

Don't want to wait until your cron time? Temporarily set the stop rule to `rate(2 minutes)`,
watch the instance stop, then **change it back** to your real cron:

```bash
aws events put-rule --name ec2-stop-schedule --schedule-expression "rate(2 minutes)"
# ...watch it stop...
aws events put-rule --name ec2-stop-schedule --schedule-expression "cron(0 0 ? * TUE-SAT *)"
```

---

## Checkpoint

- [ ] `ec2-stop-schedule` exists, **Enabled**, constant input `{"action":"stop"}`
- [ ] `ec2-start-schedule` exists, **Enabled**, constant input `{"action":"start"}`
- [ ] Both rules show the function as a target with `FailedInvocations = 0`
- [ ] A short-interval test confirmed the instance actually changes state

---

**Next:** [Step 5 — Test and Verify](./05-test-and-verify.md)
