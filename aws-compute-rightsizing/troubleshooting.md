# Troubleshooting — EC2 Compute Rightsizing

Error → Cause → Fix.

---

## findings is empty (count: 0) but instances are running

**Symptom:** The function returns `"count": 0` even though you have instances.

**Causes & fixes:**

1. **Tag mismatch.** It only looks at instances tagged `TAG_KEY=TAG_VALUE` (default
   `Rightsize=true`). Check the tag's key *and* value, including case.
2. **Instance not running.** The filter requires `instance-state-name = running`. A `stopped`
   instance is skipped (it's already not billing for compute).
3. **Wrong region.** The function and your instances must be in the same region (`us-east-1`).

---

## Every instance shows "finding": "no-data"

**Symptom:** `max_cpu` is `NaN`, finding is `no-data`.

**Cause:** CloudWatch has no `CPUUtilization` datapoints yet. Basic EC2 metrics arrive at 5-minute
granularity and a brand-new instance has nothing for the first several minutes.

**Fix:** Wait ~10–15 minutes after launch and re-run. This is intentional — the code refuses to
call an instance "idle" with no evidence, which would be a dangerous default.

---

## A loaded instance still shows "idle"

**Symptom:** You ran a CPU burn loop but the instance reads `idle` / low `max_cpu`.

**Causes & fixes:**

1. **Metrics lag.** Your load was real but CloudWatch hasn't aggregated the spike into the window
   yet. Keep the load running longer and re-run.
2. **`LOOKBACK_DAYS` too wide.** With `LOOKBACK_DAYS=1`, a 10-minute burst is a small fraction of
   24 hours, but `Maximum` should still catch it. If you used a long lookback and `Average`, the
   spike washes out — we classify on `Maximum` precisely to avoid this.
3. **t3 burst/credits.** A `while true` loop pegs CPU, but if the instance ran out of CPU credits
   it may be throttled. Use two loops on a 2-vCPU `t3.micro`.

---

## recommended_type is always null

**Symptom:** Findings are correct but `recommended_type` is `null` everywhere.

**Cause:** The instance is already the **smallest** type in the `DOWNSIZE` table (e.g.
`t3.micro` has nothing below it), or it's in a family the table doesn't cover.

**Fix:** Launch a `t3.small` (or larger) to see a real downsize recommendation
([Step 6.1](steps/06-apply-rightsizing.md)). The *finding* (`idle`/`over-provisioned`) is the
signal; the recommended type is just the suggested next step.

---

## AccessDenied on StopInstances / ModifyInstanceAttribute

**Symptom:** A resize fails with `AccessDenied`.

**Cause (usually correct behavior):** The role's condition only allows mutating actions on
instances tagged `Rightsize=true`. An untagged instance is *supposed* to be denied
([Step 6.4](steps/06-apply-rightsizing.md)).

**If it denies a tagged instance too:** the tag value must be exactly `true`. Also confirm the
inline policy's `Condition` key is `aws:ResourceTag/Rightsize` (matching your `TAG_KEY`).

---

## Nothing gets resized even with the target tagged

**Symptom:** `"applied": false` though you expected a resize.

**Cause:** Only **one** of the two gates is open. Both `APPLY=true` **and** `DRY_RUN=false` are
required. Also, `recommended_type` must be non-null and different from the current type.

**Fix:** Set both env vars ([Step 6.2](steps/06-apply-rightsizing.md)) and target a non-smallest
instance type.

---

## IncorrectInstanceState: instance must be stopped

**Symptom:** `ModifyInstanceAttribute` fails saying the instance is running.

**Cause:** Something started the instance between the stop and the modify, or the stop waiter
timed out.

**Fix:** The handler uses `get_waiter("instance_stopped")` before modifying. If you hit this,
raise the Lambda timeout (a stop can take >1 min) and ensure no Auto Scaling group or schedule is
re-starting the instance.

---

## No SNS email arrives

**Causes & fixes:**

1. **Subscription not confirmed.** Click the confirmation link in the email AWS sent.
2. **`SNS_TOPIC_ARN` not set / wrong.** Add it to the function's env vars; it must match the topic.
3. **Missing `sns:Publish`.** Add the `PublishReports` statement (Step 1.4 / 4.1) scoped to the
   topic ARN, or you'll see `AuthorizationError` in the logs.

---

## update-function-configuration wiped my other env vars

**Cause:** `--environment` **replaces** the entire variable map.

**Fix:** Always pass the full `Variables={...}` set with every key, not just the one you're
changing.

---

## General debugging checklist

1. Instances **running**, in `us-east-1`, tagged `Rightsize=true`
2. CloudWatch has had ~10–15 min to collect CPU datapoints
3. Read path works: dry-run returns findings with real `max_cpu`
4. To apply: `APPLY=true` **and** `DRY_RUN=false`, target is not already smallest
5. Tag-gated denials on untagged instances are **expected**, not a bug
6. Read `/aws/lambda/compute-rightsizer` logs for the per-instance lines
