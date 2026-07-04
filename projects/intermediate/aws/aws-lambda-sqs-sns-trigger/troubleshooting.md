# Troubleshooting

---

## "The role defined for the function cannot be assumed by Lambda"

**Symptom:** Creating the Lambda function immediately after creating the IAM role returns this error.

**Cause:** IAM is eventually consistent. A newly created role takes 5–15 seconds to propagate globally before the Lambda service can assume it.

**Fix:** Wait 15 seconds after creating or attaching policies to `OrderProcessorLambdaRole`, then retry creating the function. Do not delete and recreate the role — that resets the clock.

---

## Lambda is not being triggered after sending a message to OrderQueue

**Check 1 — Event source mapping state**
- Lambda → `OrderProcessor` → Configuration → Triggers
- The SQS trigger will show **Creating** for up to 30 seconds after you add it. Wait until the state changes to **Enabled** before testing.
- Messages sent while the mapping is in **Creating** are held in SQS and will be processed once the mapping becomes **Enabled** — they are not lost.

**Check 2 — IAM role has SQS permissions**
- IAM → Roles → `OrderProcessorLambdaRole`
- Confirm `AWSLambdaSQSQueueExecutionRole` is attached
- This policy grants `sqs:ReceiveMessage`, `sqs:DeleteMessage`, and `sqs:GetQueueAttributes` — all required for the event source mapping

**Check 3 — You sent to the correct queue**
- Make sure you sent the message to `OrderQueue`, not `OrderDLQ` or `ProcessedOrders`

---

## Lambda invocation succeeds but I receive no email from OrderNotifications

**Check 1 — Email subscription is confirmed**
- SNS → Subscriptions — status must be **Confirmed**, not **PendingConfirmation**
- Check your spam folder for the AWS confirmation email; Gmail and Outlook frequently filter it

**Check 2 — SNS_TOPIC_ARN environment variable is set correctly**
- Lambda → `OrderProcessor` → Configuration → Environment variables
- The value must be the full ARN: `arn:aws:sns:<region>:<account-id>:OrderNotifications`
- A common mistake is copying the topic name instead of the ARN

**Check 3 — Lambda logs show an SNS publish error**
- CloudWatch → Log groups → `/aws/lambda/OrderProcessor`
- Look for `botocore.exceptions.ClientError` lines near the `Failed to process message` output

---

## I receive no alerts from OrderAlerts

**Check 1 — ALERT_SNS_TOPIC_ARN is set**
- Lambda → `OrderProcessor` → Configuration → Environment variables
- If `ALERT_SNS_TOPIC_ARN` is absent the function silently skips alerts; it is an optional variable
- Add it with the ARN of `OrderAlerts`

**Check 2 — OrderAlerts email subscription is confirmed**
- SNS → Topics → `OrderAlerts` → Subscriptions tab — status must be **Confirmed**

**Check 3 — Subscription filter policy is blocking alerts**
- If you added a filter policy (e.g. `status = FAILED`), SUCCESS alerts are filtered out by design
- SNS → `OrderAlerts` → Subscriptions → click subscription → check **Subscription filter policy**
- Remove or widen the filter to receive all alerts

---

## Messages end up in OrderDLQ immediately (not after 3 retries)

The DLQ receives messages only after `maxReceiveCount` failed receive attempts. If messages arrive too quickly:
- SQS → `OrderQueue` → Dead-letter queue tab — verify **Maximum receives** is `3`, not `1`

---

## DLQ takes much longer than expected (>5 minutes)

**Why it takes time:** SQS uses a visibility timeout (default: 30 seconds) to hide a message from other consumers after it is received. Lambda must fail, the visibility timeout must expire, then Lambda picks it up again — three times. With a 30-second timeout that is a minimum of ~90 seconds before the message reaches the DLQ.

**If it is taking much longer:**
- Check CloudWatch logs for the Lambda function — it may be timing out on each attempt rather than failing fast, which adds the Lambda timeout duration to each cycle
- Lambda → `OrderProcessor` → Configuration → General configuration — confirm **Timeout** is ≤ 30 seconds for this project

---

## ApproximateReceiveCount in the DLQ shows N+1 (e.g., 4 instead of 3)

This is expected. SQS increments `ApproximateReceiveCount` each time a message is received, including the receive from the DLQ itself. A message that was retried 3 times by Lambda and then received once from the DLQ will show a count of **4**. This is not an error.

---

## "AccessDenied" in CloudWatch logs when Lambda publishes to SNS

The execution role is missing `sns:Publish` permission.

**Fix:**
- IAM → Roles → `OrderProcessorLambdaRole`
- Confirm `AmazonSNSFullAccess` (or a custom policy with `sns:Publish`) is attached
- This applies to both `SNS_TOPIC_ARN` and `ALERT_SNS_TOPIC_ARN` — both must be accessible by the same role

---

## ProcessedOrders queue is not receiving messages from SNS

**Check — SQS access policy**
- SQS → `ProcessedOrders` → Access policy tab
- The policy must allow `sns.amazonaws.com` to call `sqs:SendMessage` with a `SourceArn` condition pointing to `OrderNotifications`
- If the policy is missing entirely, SNS silently drops messages with no visible error in Lambda logs — check the SNS topic's **Delivery status** (requires a CloudWatch IAM role on the topic)
- See Step 3.8 for the correct policy

---

## Lambda times out before processing the message

Default timeout is 3 seconds. If downstream SNS calls are slow (e.g. cold start + network latency):
- Lambda → `OrderProcessor` → Configuration → General configuration → Edit
- Increase **Timeout** to 30 seconds for this project
- Note: increasing Lambda timeout also increases how long each DLQ retry cycle takes (see DLQ timing section above)

---

## "Report batch item failures" not working — entire batch is retried

- Verify **Report batch item failures** is checked on the event source mapping (Step 5)
- The Lambda function must return `{"batchItemFailures": [{"itemIdentifier": "<messageId>"}]}` for specific failures
- An unhandled exception (no try/except) causes Lambda to return an error response, which retries the **entire batch**
- Check CloudWatch logs for unhandled exceptions outside the `for record in event["Records"]` loop

---

## DLQ never receives failed messages — they are silently deleted

**Symptom:** Sending a malformed message produces `Failed to process message ...` in the Lambda logs, but the message **never** appears in `OrderDLQ`. CloudWatch shows the failure logged only **once** (not retried), and `OrderQueue` ends up empty.

**Cause:** The handler in this project **catches every exception** and signals failure only by *returning* a `batchItemFailures` response — it never re-raises. That return value is honored **only when "Report batch item failures" is enabled** on the event source mapping. If it is **disabled**, the event source mapping ignores the response, sees an invocation that completed without throwing, treats the whole batch as a success, and **deletes the message**. The receive count never increments, so `maxReceiveCount` is never reached and the message never reaches the DLQ.

This is the opposite symptom from the entry above: there the *whole batch* is retried; here the failed message is *silently dropped* with no retry at all.

**Fix:**

1. Confirm the setting is on:
   - Lambda → `OrderProcessor` → **Configuration** → **Triggers** → click the SQS trigger → **Report batch item failures** must be checked.
   - CLI: `aws lambda list-event-source-mappings --function-name OrderProcessor --query 'EventSourceMappings[].FunctionResponseTypes'` should return `[["ReportBatchItemFailures"]]`, not `[[]]`.
2. If it is off, enable it:
   ```bash
   aws lambda update-event-source-mapping \
     --uuid <event-source-mapping-uuid> \
     --function-response-types ReportBatchItemFailures
   ```
3. Re-test with a malformed message and wait ~90 seconds (3 retries × 30s visibility timeout) before polling `OrderDLQ`.

> **Alternative design:** if you intentionally do **not** enable batch-item-failure reporting, the handler must `raise` on failure instead of returning `batchItemFailures`. A raised exception fails the invocation, which prevents SQS from deleting the message so it can be retried and eventually moved to the DLQ. Returning a failure response and disabling the flag are mutually incompatible — pick one.

---

## Handler not found error

- Lambda → `OrderProcessor` → Configuration → General configuration
- **Handler** must match `<filename>.<function_name>`
- If you used the inline editor with the default file `lambda_function.py`: handler = `lambda_function.lambda_handler`
- If you uploaded `handler.py`: handler = `handler.lambda_handler`

---

## KeyError: 'SNS_TOPIC_ARN' on Lambda invocation

The required environment variable is missing.

**Fix:**
- Lambda → `OrderProcessor` → Configuration → Environment variables → Edit
- Add `SNS_TOPIC_ARN` with the full ARN of `OrderNotifications`
- Click **Deploy** after saving environment variables — a saved config change does not redeploy the function, but a new invocation will pick up the new variables immediately
