# Troubleshooting — Scheduled EC2 Start/Stop

Error → Cause → Fix.

---

## UnauthorizedOperation when starting/stopping

**Symptom:** Logs show
`An error occurred (UnauthorizedOperation) when calling the StopInstances operation`.

**Cause:** The IAM condition `aws:ResourceTag/AutoPower = true` did not match. Either the
instance isn't tagged correctly, or the tag value isn't exactly `true` (case-sensitive,
no spaces).

**Fix:** Check the actual tags:

```bash
aws ec2 describe-instances --instance-ids i-0abc123... \
  --query 'Reservations[].Instances[].Tags'
```

The key must be `AutoPower` and value `true` exactly. Fix the tag, or fix `TAG_KEY`/`TAG_VALUE`
env vars to match what you used.

---

## The function finds 0 instances (affected: [])

**Symptom:** Response is `{"action":"stop","affected":[],...}` even though an instance is running.

**Causes & fixes:**

1. **Wrong state for the action.** "stop" only looks at `running` instances; "start" only at
   `stopped`. If you call `stop` while the instance is still `pending`, it's not yet `running`,
   so it's skipped. Wait for `running`.
2. **Tag mismatch** — see the previous entry.
3. **Wrong region.** The instance is in a different region than the Lambda. Both must be
   `us-east-1` (or set the function's region to match).

---

## DryRunOperation / nothing actually changes

**Symptom:** Logs say `DRY_RUN=true — not calling EC2` and the instance never changes state.

**Cause:** The `DRY_RUN` env var is still `true`.

**Fix:**

```bash
aws lambda update-function-configuration \
  --function-name ec2-scheduler \
  --environment "Variables={TAG_KEY=AutoPower,TAG_VALUE=true,DRY_RUN=false}"
```

> Note: `update-function-configuration` **replaces** all env vars — always pass the full set,
> not just the one you're changing.

---

## ValueError: event['action'] must be 'start' or 'stop'

**Symptom:** Function errors with this message.

**Cause:** The EventBridge target's **constant input** is missing or malformed — the function
got an empty `event`. Common when the input was typed as plain text instead of JSON, or the
key is misspelled (`"Action"` vs `"action"`).

**Fix:** In the rule's target, **Configure target input → Constant (JSON text)** must be exactly
`{"action": "stop"}` (lowercase key). On the CLI, the `Input` value must be valid JSON.

---

## The schedule fires but the instance isn't touched (no logs)

**Symptom:** Rule `Invocations` and `FailedInvocations` both climb; no Lambda logs.

**Cause:** Missing resource-based permission for that specific rule (CLI users forget
`add-permission`). Each rule needs its **own** permission statement.

**Fix:**

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws lambda add-permission --function-name ec2-scheduler \
  --statement-id ec2-stop-invoke --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:${ACCOUNT_ID}:rule/ec2-stop-schedule
# repeat with ec2-start-invoke / ec2-start-schedule
```

---

## Task timed out after 30.00 seconds

**Symptom:** Timeout on functions managing many instances.

**Cause:** `describe` + start/stop over a large fleet exceeds the timeout.

**Fix:** Raise the timeout (`--timeout 60`). The Start/Stop calls themselves are async on AWS's
side — the function returns once the request is *accepted*, not once instances finish
transitioning, so this is rare for modest fleets.

---

## cron schedule fired at the wrong hour

**Cause:** EventBridge rules are **UTC**. `cron(0 20 ...)` is 20:00 UTC, not 8 PM local.

**Fix:** Convert local → UTC, or use **EventBridge Scheduler** (timezone-aware). Watch out for
the day-of-week shifting when your local evening crosses midnight UTC.

---

## General debugging checklist

1. Instance is tagged exactly `AutoPower=true` and in `us-east-1`
2. `DRY_RUN=false` when you expect real changes
3. The target's constant input is valid JSON with lowercase `action`
4. Each rule has its own invoke permission; `FailedInvocations = 0`
5. Function `Errors = 0`; read `/aws/lambda/ec2-scheduler` logs
