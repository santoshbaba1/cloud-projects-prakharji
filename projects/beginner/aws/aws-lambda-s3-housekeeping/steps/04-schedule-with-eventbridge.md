# Step 4 — Schedule It with EventBridge

Make the housekeeper run automatically on a daily schedule. This is the same EventBridge rule
pattern from Projects 1 and 2 — by now it should feel familiar.

---

## 4.1 Create the Daily Rule (Console)

1. **EventBridge** → **Rules** → **Create rule**.

   | Field | Value |
   |-------|-------|
   | Name | `s3-housekeeping-schedule` |
   | Rule type | **Schedule** |

2. Schedule: a daily cron — e.g. **03:00 UTC** every day: `cron(0 3 * * ? *)`.
   (Running off-hours keeps housekeeping out of the way of normal traffic.)
3. **Target** → **Lambda function** → `s3-housekeeper`.
4. No constant input needed — the function reads its behavior from env vars, and ignores the
   event payload.
5. **Next** → **Create rule**. The console adds the invoke permission automatically.

---

## AWS CLI (Alternative)

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
FN_ARN=$(aws lambda get-function --function-name s3-housekeeper \
  --query 'Configuration.FunctionArn' --output text)

aws events put-rule --name s3-housekeeping-schedule \
  --schedule-expression "cron(0 3 * * ? *)" \
  --description "Daily S3 housekeeping"

aws lambda add-permission \
  --function-name s3-housekeeper --statement-id s3-housekeeping-invoke \
  --action lambda:InvokeFunction --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:${ACCOUNT_ID}:rule/s3-housekeeping-schedule

aws events put-targets --rule s3-housekeeping-schedule \
  --targets "Id"="1","Arn"="${FN_ARN}"
```

---

## 4.2 Test Without Waiting Until 3 AM

Temporarily switch to a short rate, re-seed some objects, watch it fire, then switch back:

```bash
# seed fresh objects so there's something to archive
python src/seed_objects.py YOUR_BUCKET_NAME

# fire every 2 minutes for the test
aws events put-rule --name s3-housekeeping-schedule --schedule-expression "rate(2 minutes)"

# watch logs
aws logs tail /aws/lambda/s3-housekeeper --follow --since 5m

# ...once you've seen it run, restore the daily cron
aws events put-rule --name s3-housekeeping-schedule --schedule-expression "cron(0 3 * * ? *)"
```

> Don't leave it on `rate(2 minutes)` — it's harmless here but pointless, and it clutters your
> logs. Daily is the realistic cadence for housekeeping.

---

## Checkpoint

- [ ] Rule `s3-housekeeping-schedule` exists, **Enabled**, daily cron
- [ ] Function shows a resource-based statement for `events.amazonaws.com`
- [ ] A short-rate test showed a scheduled run in the logs (`trigger` from `aws.events`)
- [ ] Schedule restored to the daily cron

---

**Next:** [Step 5 — Test and Verify](./05-test-and-verify.md)
