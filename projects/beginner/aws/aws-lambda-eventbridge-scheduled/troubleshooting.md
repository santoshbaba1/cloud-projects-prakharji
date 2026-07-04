# Troubleshooting — Lambda on a Schedule with EventBridge

Error → Cause → Fix for the issues you're most likely to hit.

---

## The rule shows Invocations but the function never runs (no logs)

**Symptom:** EventBridge → rule → Monitoring shows `Invocations` and `FailedInvocations`
climbing together, but `/aws/lambda/scheduled-heartbeat` has no new events.

**Cause:** The rule fired but was **denied** permission to invoke the Lambda. The
resource-based permission allowing `events.amazonaws.com` is missing. This happens when you
create the rule and target on the **CLI** and forget `aws lambda add-permission`.

**Fix:**

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws lambda add-permission \
  --function-name scheduled-heartbeat \
  --statement-id heartbeat-schedule-invoke \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:${ACCOUNT_ID}:rule/heartbeat-schedule
```

The console "Add target" flow does this automatically — this is almost always a CLI-only bug.

---

## The schedule never fires at all (zero invocations)

**Symptom:** Minutes pass and `Invocations` stays at 0.

**Causes & fixes:**

1. **The rule is disabled.** `aws events describe-rule --name heartbeat-schedule` →
   check `"State": "ENABLED"`. Enable with `aws events enable-rule --name heartbeat-schedule`.
2. **Bad schedule expression.** `rate(5 minute)` (singular) is invalid — it must be
   `rate(5 minutes)`. A `rate(1 ...)` *must* be singular: `rate(1 minute)`, `rate(1 hour)`.
3. **No target attached.** `aws events list-targets-by-rule --rule heartbeat-schedule`
   should list the function. If empty, re-run `put-targets`.

---

## cron() fires at the wrong time

**Symptom:** You set `cron(0 9 * * ? *)` expecting 9 AM local, but it runs at a different hour.

**Cause:** Classic EventBridge rules are **UTC only**. `cron(0 9 ...)` is 09:00 **UTC**.

**Fix:** Convert your local time to UTC, or use **EventBridge Scheduler**, which supports
timezones (e.g. `America/New_York`) and daylight-saving handling.

---

## "Parameter ScheduleExpression is not valid"

**Symptom:** `put-rule` rejects your cron.

**Cause:** AWS cron has **six** fields and special day-of-week rules. The most common mistake
is using `*` in *both* day-of-month and day-of-week — exactly one must be `?`.

**Fix:** `cron(0 9 * * ? *)` ✅ (every day) — day-of-month `*`, day-of-week `?`.
`cron(0 9 ? * MON-FRI *)` ✅ (weekdays) — day-of-month `?`, day-of-week `MON-FRI`.

---

## AccessDeniedException on sns:Publish

**Symptom:** Logs show `An error occurred (AuthorizationError) ... not authorized to perform: SNS:Publish`.

**Cause:** The execution role's inline `sns:Publish` resource ARN doesn't match the topic
(wrong account ID, region, or topic name).

**Fix:** Compare the ARN in the inline policy with the real topic ARN:

```bash
aws sns list-topics --query "Topics[?contains(TopicArn,'heartbeat-alerts')]"
aws iam get-role-policy --role-name ScheduledHeartbeatExecutionRole --policy-name HeartbeatSnsPublish
```

They must match exactly.

---

## I get the email twice for one scheduled slot

**Symptom:** Occasionally two emails for the same minute.

**Cause:** EventBridge scheduled delivery is **at-least-once**, not exactly-once. Rare
duplicate invocations are expected behavior, not a bug.

**Fix:** For a heartbeat it doesn't matter. For actions that must not repeat (e.g. charging a
card), make the handler **idempotent** — design it so running twice has the same effect as
running once.

---

## Can't delete the rule: "Rule can't be deleted since it has targets"

**Cause:** Targets must be removed before deleting a rule.

**Fix:**

```bash
aws events remove-targets --rule heartbeat-schedule --ids "1"
aws events delete-rule --name heartbeat-schedule
```

---

## General debugging checklist

1. Rule `State` is `ENABLED` and the expression is valid
2. The rule has the Lambda as a target (`list-targets-by-rule`)
3. The function has a resource-based statement for `events.amazonaws.com`
4. `FailedInvocations = 0` on the rule
5. `Errors = 0` on the function; check logs for `[ERROR]`
