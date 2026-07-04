# Challenges — Scheduled S3 Housekeeping

Extend the janitor. These build on what you deployed.

---

## Challenge 1 — Two-Stage Lifecycle (Archive, Then Delete)

Run the function twice on a schedule with different configs: one schedule **archives** objects
older than 30 days (`active/ → archive/`), a second **deletes** objects in `archive/` older than
90 days. You'll need a second EventBridge rule and a way to vary `ACTION`/`PREFIX` per run — pass
them as **constant input** in the event and read `event.get(...)` with the env var as fallback.

---

## Challenge 2 — Report Instead of (or Before) Acting

Add a summary to SNS after each run (reuse the
[Project 1 SNS pattern](../aws-lambda-eventbridge-scheduled/steps/04-add-sns-notifications.md)):
`"Archived 12 objects (3.4 MB) from active/ on 2026-06-14"`. Compute the total bytes from each
object's `Size`. Add `sns:Publish` to the role scoped to your topic.

---

## Challenge 3 — Move to a Cheaper Storage Class

Instead of moving to an `archive/` prefix, change the storage **class** in place:
`copy_object(..., StorageClass="GLACIER_IR")` (or `STANDARD_IA`). Compare the trade-offs:
retrieval cost/latency vs. storage savings. When is this better than your own `archive/` prefix?

---

## Challenge 4 — Safe Deletes with Versioning

Enable **versioning** on the bucket. Now a `delete` writes a *delete marker* instead of erasing
data, so mistakes are recoverable. Update the cleanup step to purge old **versions** too. Discuss:
versioning makes deletes safe but storage grows — how would a lifecycle rule on noncurrent
versions help?

---

## Challenge 5 — Scale to a Huge Bucket

The single-function approach hits the timeout on millions of objects. Redesign for scale:
(a) have the function process one page, store a continuation token, and re-invoke itself; **or**
(b) replace the Lambda with an **S3 Lifecycle rule** for pure expiry; **or** (c) use **S3 Batch
Operations**. Write up when each approach wins.

---

## Challenge 6 — Lambda vs. Lifecycle Decision Guide

No code: write a short decision guide (a paragraph or table) for "should this cleanup be a Lambda
or an S3 Lifecycle rule?" Cover cost, custom logic, cross-service actions, notifications, and
operational risk. Use it to justify which of *your* real buckets would use which.
