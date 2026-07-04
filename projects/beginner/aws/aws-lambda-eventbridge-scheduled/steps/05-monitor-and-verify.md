# Step 5 — Monitor and Verify

A scheduled job is only useful if you can answer two questions: **"Did it run?"** and
**"Did it fail?"** Here's how to check both for the rule *and* the function.

---

## 5.1 Did the Rule Fire? (EventBridge metrics)

1. **EventBridge** → **Rules** → `heartbeat-schedule` → **Monitoring** tab.

| Metric | What it tells you |
|--------|-------------------|
| `Invocations` | How many times the rule fired and sent to the target |
| `FailedInvocations` | The rule fired but could **not** invoke the target — almost always a missing/incorrect resource-based permission |
| `TriggeredRules` | How many times the rule matched (for schedules, == invocations) |

> **Rule of thumb:** `FailedInvocations > 0` with **no Lambda logs** = the permission from
> Step 3 is missing or wrong. Re-check the resource-based policy.

---

## 5.2 Did the Function Succeed? (Lambda metrics)

1. **Lambda** → `scheduled-heartbeat` → **Monitor** tab → **Metrics**.

| Metric | Healthy value |
|--------|---------------|
| `Invocations` | Climbs by ~1 every 5 minutes |
| `Errors` | `0` |
| `Duration` | Tens of ms |
| `Throttles` | `0` |

---

## 5.3 Read the Logs

```bash
# Stream new log lines as they arrive
aws logs tail /aws/lambda/scheduled-heartbeat --follow

# Or query the last hour with Logs Insights
aws logs start-query \
  --log-group-name /aws/lambda/scheduled-heartbeat \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /Heartbeat/ | sort @timestamp desc'
```

Each scheduled run logs `trigger=aws.events`; each manual test logs `trigger=manual`.

---

## 5.4 Alarm on a Missed Run (optional but recommended)

A schedule that silently stops firing is the classic cron failure. Create a CloudWatch alarm
that fires when the function has **zero** invocations over a window longer than its interval.

1. **CloudWatch** → **Alarms** → **Create alarm** → **Select metric** →
   **Lambda → By Function Name → `scheduled-heartbeat` → Invocations**.
2. Statistic **Sum**, period **15 minutes**.
3. Condition: **Lower** than **1** (i.e. `Invocations < 1` for 1 period means it missed several
   5-minute slots).
4. Treat **missing data as breaching** (no data = it didn't run).
5. Action: notify the `heartbeat-alerts` topic. Name it `heartbeat-missed-runs`.

> **Why "missing data = breaching"?** If the function never runs, Lambda emits *no* metric at
> all — not a zero. Telling the alarm to treat absent data as a breach is what catches a dead
> schedule.

---

## Checkpoint

- [ ] Rule shows `Invocations` climbing and `FailedInvocations = 0`
- [ ] Function shows `Errors = 0`
- [ ] Logs show repeated `trigger=aws.events` runs
- [ ] (Optional) Alarm `heartbeat-missed-runs` is in `OK` while the schedule runs

---

**Next:** [Step 6 — Cleanup](./06-cleanup.md)
