# Step 6 — Cleanup

No hourly charges here, but the schedule keeps firing and the bucket keeps storing objects until
you remove them. A bucket must be **emptied before it can be deleted**.

---

## 6.1 Delete the Schedule

```bash
aws events remove-targets --rule s3-housekeeping-schedule --ids "1"
aws events delete-rule --name s3-housekeeping-schedule
```

(Console: disable, then delete the rule.)

---

## 6.2 Empty and Delete the Bucket

```bash
BUCKET=YOUR_BUCKET_NAME

# Empty it (removes every object, including archive/)
aws s3 rm s3://$BUCKET --recursive

# Then delete the now-empty bucket
aws s3api delete-bucket --bucket $BUCKET --region us-east-1
```

> **Empty first.** `delete-bucket` fails with `BucketNotEmpty` if any object remains. If you
> enabled versioning (Challenge 4), you must also delete all object *versions* and delete
> markers — `aws s3 rm --recursive` alone won't clear those.

---

## 6.3 Delete the Lambda Function

```bash
aws lambda delete-function --function-name s3-housekeeper
```

---

## 6.4 Delete the Log Group

```bash
aws logs delete-log-group --log-group-name /aws/lambda/s3-housekeeper
```

---

## 6.5 Delete the IAM Role

```bash
aws iam delete-role-policy \
  --role-name S3HousekeeperExecutionRole --policy-name S3HousekeeperBucketAccess

aws iam detach-role-policy \
  --role-name S3HousekeeperExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam delete-role --role-name S3HousekeeperExecutionRole
```

---

## Cleanup Checklist

- [ ] Rule `s3-housekeeping-schedule` deleted (no more runs)
- [ ] Bucket emptied **and** deleted
- [ ] Function `s3-housekeeper` deleted
- [ ] Log group deleted
- [ ] Role `S3HousekeeperExecutionRole` deleted

---

## 🎉 Series Complete

You've finished the **Lambda Automation Series** — three schedule-driven automations on one
EventBridge + Lambda foundation:

1. **[Scheduled Heartbeat](../../aws-lambda-eventbridge-scheduled/README.md)** — the scheduling pattern itself
2. **[EC2 Start/Stop](../../aws-lambda-ec2-start-stop-scheduler/README.md)** — cost savings on idle compute
3. **S3 Housekeeping** — automated storage hygiene

Keep going with **event-driven** Lambda in
[Lambda with S3 Event Processing](../../aws-lambda-s3-event-processing/README.md), or deepen your
debugging in [Lambda Troubleshooting & Monitoring](../../../../intermediate/aws/aws-lambda-troubleshooting-monitoring/README.md).
