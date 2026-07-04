# Step 6 — Cleanup

This project has **no hourly charges**, but the rule keeps firing the function forever (and
emailing you) until you remove it. Tear everything down in this order.

---

## 6.1 Disable, Then Delete the Rule

A target must be removed before the rule can be deleted.

**Console:** EventBridge → Rules → `heartbeat-schedule` → **Disable**, then **Delete**
(the console removes its targets for you).

**CLI:**

```bash
aws events disable-rule --name heartbeat-schedule
aws events remove-targets --rule heartbeat-schedule --ids "1"
aws events delete-rule --name heartbeat-schedule
```

> **Why disable first:** disabling stops it firing *immediately*, even before you finish the
> rest of cleanup.

---

## 6.2 Delete the Lambda Function

```bash
aws lambda delete-function --function-name scheduled-heartbeat
```

Deleting the function also removes its resource-based permission and its log group is no
longer written to.

---

## 6.3 Delete the SNS Topic (if you did Step 4)

```bash
TOPIC_ARN=$(aws sns list-topics \
  --query "Topics[?contains(TopicArn, 'heartbeat-alerts')].TopicArn | [0]" --output text)
aws sns delete-topic --topic-arn "$TOPIC_ARN"
```

Deleting the topic removes its subscriptions too.

---

## 6.4 Delete the Log Group

```bash
aws logs delete-log-group --log-group-name /aws/lambda/scheduled-heartbeat
```

---

## 6.5 Delete the IAM Role

```bash
aws iam delete-role-policy \
  --role-name ScheduledHeartbeatExecutionRole --policy-name HeartbeatSnsPublish

aws iam detach-role-policy \
  --role-name ScheduledHeartbeatExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam delete-role --role-name ScheduledHeartbeatExecutionRole
```

---

## 6.6 Delete the Alarm (if you created one)

```bash
aws cloudwatch delete-alarms --alarm-names heartbeat-missed-runs
```

---

## Cleanup Checklist

- [ ] Rule `heartbeat-schedule` deleted (no more invocations / emails)
- [ ] Function `scheduled-heartbeat` deleted
- [ ] SNS topic `heartbeat-alerts` deleted
- [ ] Log group deleted
- [ ] Role `ScheduledHeartbeatExecutionRole` deleted
- [ ] Alarm `heartbeat-missed-runs` deleted (if created)

---

You've built a serverless cron job. **Next project →**
[Scheduled EC2 Start/Stop](../../aws-lambda-ec2-start-stop-scheduler/README.md), where the same
schedule pattern saves real money by powering EC2 off overnight.
