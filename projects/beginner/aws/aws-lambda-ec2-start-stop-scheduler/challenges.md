# Challenges — Scheduled EC2 Start/Stop

Extend the scheduler. These build directly on what you deployed.

---

## Challenge 1 — Per-Instance Schedules via Tags

Instead of one global schedule, let each instance declare its own hours with tags like
`AutoPowerStart=12:00` and `AutoPowerStop=00:00` (UTC). Change the handler so a single
`rate(15 minutes)` schedule wakes the function, which then starts/stops each instance whose
tagged time matches the current 15-minute window. This is how real "instance scheduler"
solutions work.

---

## Challenge 2 — Weekend-Aware

Make the function refuse to *start* instances on Saturday/Sunday even if a start schedule fires,
so a misconfigured weekday cron can't accidentally power a fleet up over the weekend. Add a log
line explaining the skip.

---

## Challenge 3 — Summary Notification

Wire in SNS (reuse the pattern from
[Project 1, Step 4](../aws-lambda-eventbridge-scheduled/steps/04-add-sns-notifications.md)). After
each run, publish a summary: `"Stopped 4 instances at 00:00 UTC: [...]"`. Add `sns:Publish` to
the role, scoped to your topic ARN.

---

## Challenge 4 — Cover More Resources

Extend beyond EC2: also stop/start **RDS DB instances** tagged `AutoPower=true`
(`rds:StopDBInstance` / `rds:StartDBInstance`). Note RDS has its own quirks — instances can't
stay stopped more than 7 days, and some engines/configs can't be stopped at all. Add the RDS
permissions to the role, gated by the same tag condition.

---

## Challenge 5 — Confirm It Actually Stopped (Waiter)

`stop_instances` returns immediately. Add a Boto3 **waiter** (`ec2.get_waiter("instance_stopped")`)
so the function only returns once the instances reach `stopped`, and have it raise/alert if they
don't within the timeout. Discuss the trade-off: longer (and more expensive) invocations vs.
stronger confirmation.

---

## Challenge 6 — Switch to EventBridge Scheduler

Replace both rules with **EventBridge Scheduler** schedules using a real timezone
(e.g. `Europe/London`) so you stop worrying about UTC conversion and daylight saving. Compare
the IAM model: Scheduler needs a role it can assume to invoke Lambda, versus the resource-based
permission a classic rule uses.
