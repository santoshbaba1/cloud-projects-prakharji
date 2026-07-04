# Step 5 — SNS: Turn Alarms Into Emails

Identical pattern to the EC2 project — proof that the *alerting* layer is independent of the
*compute* layer. Create a topic, confirm an email subscription, and point the alarms at it.

---

## 5.1 Console — Create the Topic and Subscribe

1. **SNS → Topics → Create topic** → Type **Standard**, Name `serverless-webapp-alerts` → Create.
2. **Create subscription** → Protocol **Email** → your address → Create.
3. **Click the confirmation link** in the email. Until confirmed, the subscription is
   **Pending** and delivers nothing.

---

## 5.2 Console — Wire Both Alarms to SNS

For **each** of `serverless-webapp-errors` and `serverless-webapp-slow`:

1. **CloudWatch → Alarms →** open the alarm **→ Actions → Edit**.
2. At the notification step, **In alarm → send to** `serverless-webapp-alerts`. Optionally add
   an **OK** action to the same topic for recovery emails.
3. **Update alarm.**

> If you ran `setup_monitoring.py` in Step 4, the topic and both alarm actions are already
> wired — you only need to confirm the email subscription.

---

## 5.3 End-to-End Test

```bash
API=https://abc123.execute-api.us-east-1.amazonaws.com
for i in $(seq 1 5); do curl -s "$API/api/load?seconds=5" >/dev/null; done
```

Within a few minutes you receive *"ALARM: serverless-webapp-slow …"* by email. To test the
**errors** alarm, temporarily break the function (e.g. add `raise Exception("boom")` at the
top of `handler`, deploy, hit any route, then revert) and watch the errors email arrive.

---

## 5.4 AWS CLI (Alternative)

```bash
REGION=us-east-1
TOPIC_ARN=$(aws sns create-topic --name serverless-webapp-alerts --query TopicArn --output text --region $REGION)
aws sns subscribe --topic-arn $TOPIC_ARN --protocol email --notification-endpoint you@example.com --region $REGION
# confirm the email, then:
aws cloudwatch put-metric-alarm --alarm-name serverless-webapp-errors \
  --namespace AWS/Lambda --metric-name Errors \
  --dimensions Name=FunctionName,Value=serverless-webapp \
  --statistic Sum --period 60 --evaluation-periods 1 \
  --threshold 1 --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions $TOPIC_ARN --ok-actions $TOPIC_ARN --region $REGION
```

---

## Checkpoint

- [ ] SNS topic `serverless-webapp-alerts` exists; email subscription **Confirmed**
- [ ] Both alarms send to the topic
- [ ] Driving `/api/load` produced a "slow" email
- [ ] (Optional) Forcing an exception produced an "errors" email, then you reverted it

---

**Next:** [Step 6 — CloudTrail Audit](./06-cloudtrail-audit.md)
