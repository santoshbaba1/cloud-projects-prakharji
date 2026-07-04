# Challenges — Lambda on a Schedule with EventBridge

Finished the project? Extend it. These use only services introduced here (plus one optional
peek at EventBridge Scheduler).

---

## Challenge 1 — Switch to a cron Schedule

Change the rule from `rate(5 minutes)` to a daily `cron(...)` — say every weekday at 13:00 UTC:
`cron(0 13 ? * MON-FRI *)`. Confirm in the logs that it fires only on weekdays. Remember AWS
cron is **UTC** and **six fields**, with `?` in exactly one of day-of-month / day-of-week.

---

## Challenge 2 — Try EventBridge Scheduler (timezones)

Recreate the schedule using **EventBridge Scheduler** instead of a rule:

1. EventBridge → **Schedules** → **Create schedule**.
2. Use a cron with a **timezone** (e.g. `America/New_York`) so it ignores daylight saving math.
3. Target = `scheduled-heartbeat`. Scheduler will offer to **create an IAM role** that allows
   `scheduler.amazonaws.com` to invoke the function — note how this differs from the
   resource-based permission a *rule* uses.

**Why it matters:** Scheduler is the modern, timezone-aware successor to scheduled rules.

---

## Challenge 3 — One Function, Two Schedules, Different Input

Add a second rule, `heartbeat-schedule-hourly`, that fires `rate(1 hour)` and passes
**constant input** `{"environment": "prod-check"}`. Make the handler read
`event.get("environment", ENVIRONMENT)` so the message label changes based on which schedule
invoked it. This is the exact mechanism Project 2 uses for start vs stop.

---

## Challenge 4 — Alarm on a Dead Schedule

Implement the missed-run alarm from Step 5.4 end to end, then **prove it works**: disable the
rule, wait past the alarm period, and confirm the alarm goes to `ALARM` and emails you. Re-enable
and watch it return to `OK`.

---

## Challenge 5 — Skip Weekends in Code

Keep a daily schedule but make the **handler** decide whether to do real work: if
`datetime.now(timezone.utc).weekday() >= 5` (Saturday/Sunday), log "skipping weekend" and return
early without publishing. Compare this to Challenge 1 — when is "filter in the schedule" better
than "filter in the code", and vice versa?

---

## Challenge 6 — Idempotency

EventBridge is at-least-once. Make the heartbeat safely deduplicate: include a minute-bucket key
(e.g. `ran_at` truncated to the minute) and, before publishing, check/write a marker in a small
DynamoDB table with a conditional put so a duplicate invocation in the same minute does **not**
send a second email.
