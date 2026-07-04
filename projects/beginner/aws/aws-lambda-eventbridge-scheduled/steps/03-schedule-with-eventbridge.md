# Step 3 — Schedule It with EventBridge

Now the interesting part: make the function run **on its own**, on a timer. You'll create
an **EventBridge rule** with a *schedule expression* and point it at the Lambda.

---

## 3.1 Schedule Expressions

EventBridge accepts two formats:

| Format | Example | Meaning |
|--------|---------|---------|
| `rate(...)` | `rate(5 minutes)` | Every 5 minutes, starting when you save |
| `rate(...)` | `rate(1 hour)` | Every hour |
| `cron(...)` | `cron(0 9 * * ? *)` | Every day at **09:00 UTC** |
| `cron(...)` | `cron(0/30 * * * ? *)` | Every 30 minutes |

> **cron fields:** `cron(Minutes Hours Day-of-month Month Day-of-week Year)`. AWS cron has
> **six** fields (not five) and uses `?` for "no specific value" in either the day-of-month
> *or* day-of-week field — you can't use `*` in both at once.
>
> **Timezone:** classic EventBridge rules are **UTC only**. For local-time schedules, see
> the EventBridge Scheduler note at the bottom.

For this walkthrough, use `rate(5 minutes)` so you don't wait long to see it fire.

---

## 3.2 Create the Rule (Console)

1. Search **EventBridge** → **Rules** → make sure the event bus is **default** → **Create rule**.

   | Field | Value |
   |-------|-------|
   | Name | `heartbeat-schedule` |
   | Description | `Fire scheduled-heartbeat on a timer` |
   | Event bus | `default` |
   | Rule type | **Schedule** |

   > If the console nudges you toward "EventBridge Scheduler", you can click
   > **"Use legacy / Continue to create rule"** — a scheduled *rule* is the simplest path
   > and auto-wires the Lambda permission for you.

2. **Schedule pattern** → **A schedule that runs at a regular rate** → `5` `Minutes`.
3. **Next** → **Target** → **AWS service** → **Lambda function** → select `scheduled-heartbeat`.
4. **Next** → **Next** → **Create rule**.

When you add a Lambda target this way, the console **automatically adds a resource-based
permission** to the function allowing `events.amazonaws.com` to invoke it. You can see it
under the function's **Configuration → Permissions → Resource-based policy statements**.

---

## 3.3 Watch It Fire

Wait ~5 minutes, then tail the logs:

```bash
aws logs tail /aws/lambda/scheduled-heartbeat --follow --since 10m
```

You should see a line like:

```
Heartbeat at 2026-06-14T12:05:00+00:00 (trigger=aws.events, env=dev)
```

`trigger=aws.events` proves **EventBridge** invoked it, not you.

---

## AWS CLI (Alternative)

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
FN_ARN=$(aws lambda get-function --function-name scheduled-heartbeat \
  --query 'Configuration.FunctionArn' --output text)

# 1. Create the scheduled rule
aws events put-rule \
  --name heartbeat-schedule \
  --schedule-expression "rate(5 minutes)" \
  --description "Fire scheduled-heartbeat on a timer"

# 2. Allow EventBridge to invoke the function (the resource-based permission)
aws lambda add-permission \
  --function-name scheduled-heartbeat \
  --statement-id heartbeat-schedule-invoke \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:${ACCOUNT_ID}:rule/heartbeat-schedule

# 3. Attach the Lambda as the rule's target
aws events put-targets \
  --rule heartbeat-schedule \
  --targets "Id"="1","Arn"="${FN_ARN}"
```

> **The `add-permission` step is the one beginners forget on the CLI.** The console does it
> for you; the CLI does not. Without it the rule fires but the invoke is denied — you'll see
> `FailedInvocations` on the rule's metrics and **no logs**.

---

## Passing Constant Input (preview of Project 2)

A target can pass static JSON to the function as the `event`. In the console it's
**Target → Additional settings → Configure target input → Constant (JSON text)**. On the CLI
add `"Input"='{"action":"stop"}'` to the target. Project 2 uses this to tell one function
whether to *start* or *stop* EC2.

---

## EventBridge Scheduler (the newer alternative)

AWS now also offers **EventBridge Scheduler** (a separate console section). It adds
timezone-aware schedules, one-time schedules, and a flexible time window — but it requires
its own IAM role that allows the scheduler to invoke your Lambda. We use classic **rules**
here because they're the simplest first step. Trying Scheduler is a challenge in
[challenges.md](../challenges.md).

---

## Checkpoint

- [ ] Rule `heartbeat-schedule` exists with state **Enabled** and schedule `rate(5 minutes)`
- [ ] The function shows a resource-based statement allowing `events.amazonaws.com`
- [ ] Logs show a run with `trigger=aws.events`
- [ ] The rule's **Monitoring** shows `Invocations` ≥ 1 and `FailedInvocations` = 0

---

**Next:** [Step 4 — Add SNS Notifications (Optional)](./04-add-sns-notifications.md)
