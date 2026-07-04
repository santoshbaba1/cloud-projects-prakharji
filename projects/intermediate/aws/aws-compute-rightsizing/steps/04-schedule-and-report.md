# Step 4 — Schedule It and Email the Report

Rightsizing is a *periodic* chore — once a week is plenty. You'll create an **EventBridge rule**
that invokes the function on a schedule, and wire up an **SNS topic** so the report lands in your
inbox instead of only in the logs.

---

## 4.1 Create the SNS Topic

1. **SNS** → **Topics** → **Create topic** → **Standard**.

   | Field | Value |
   |-------|-------|
   | Name | `rightsizing-alerts` |

2. **Create topic**, then **Create subscription**:

   | Field | Value |
   |-------|-------|
   | Protocol | **Email** |
   | Endpoint | your email |

3. Confirm the subscription from the email AWS sends you.
4. **Copy the Topic ARN.**

Now give the function the ARN and the publish permission:

- **Lambda** → `compute-rightsizer` → **Configuration → Environment variables** → add
  `SNS_TOPIC_ARN` = the topic ARN.
- If you didn't add the `PublishReports` statement in [Step 1.4](./01-iam-role.md), add it now to
  `ComputeRightsizerPolicy` (scoped to this topic ARN).

Re-run `python src/test_invoke.py` — you should get an **email** with the same report you saw in
the response.

---

## 4.2 Create the EventBridge Schedule

1. **Amazon EventBridge** → **Rules** → **Create rule**.

   | Field | Value |
   |-------|-------|
   | Name | `rightsizing-schedule` |
   | Event bus | `default` |
   | Rule type | **Schedule** |

2. Schedule pattern → **A schedule that runs at a regular rate** for testing
   (`rate(10 minutes)`), or a cron for production:

   ```
   cron(0 13 ? * MON *)      # every Monday 13:00 UTC
   ```

3. **Target** → **AWS service** → **Lambda function** → `compute-rightsizer`.
4. **Create**.

EventBridge adds the resource-based permission that lets the rule invoke your function
automatically (the same `lambda:InvokeFunction` grant you'd otherwise add by hand with
`lambda add-permission`).

> Use `rate(10 minutes)` only while testing, then switch back to the weekly cron. A report every
> 10 minutes is noise — and a reminder that *schedule frequency is itself a cost/usefulness
> decision.*

---

## AWS CLI (Alternative)

```bash
aws sns create-topic --name rightsizing-alerts
aws sns subscribe --topic-arn <TOPIC_ARN> --protocol email --notification-endpoint you@example.com

aws events put-rule --name rightsizing-schedule \
  --schedule-expression 'cron(0 13 ? * MON *)'

aws lambda add-permission --function-name compute-rightsizer \
  --statement-id rightsizing-schedule --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:<ACCOUNT_ID>:rule/rightsizing-schedule

aws events put-targets --rule rightsizing-schedule \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:<ACCOUNT_ID>:function:compute-rightsizer"
```

---

## Checkpoint

- [ ] SNS topic `rightsizing-alerts` exists with a **confirmed** email subscription
- [ ] `SNS_TOPIC_ARN` set on the function; a manual invoke **emails** you the report
- [ ] EventBridge rule `rightsizing-schedule` targets the function
- [ ] You've switched the schedule back to weekly cron after any rate-based testing

---

**Next:** [Step 5 — Enable & Compare AWS Compute Optimizer](./05-compute-optimizer.md)
