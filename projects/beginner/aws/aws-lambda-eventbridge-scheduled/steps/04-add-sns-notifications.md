# Step 4 — Add SNS Notifications (Optional)

So far the heartbeat only writes to CloudWatch Logs — you have to go *look* to know it ran.
Let's make it **email you** on each run by publishing to an SNS topic. (Skip this step if
you only want logs; the function works fine without it.)

---

## 4.1 Create the SNS Topic

1. **SNS** → **Topics** → **Create topic**.

   | Field | Value |
   |-------|-------|
   | Type | **Standard** |
   | Name | `heartbeat-alerts` |

2. **Create topic**.

> The role you built in Step 1 already allows `sns:Publish` on exactly this topic ARN
> (`...:heartbeat-alerts`), so no IAM change is needed here.

---

## 4.2 Subscribe Your Email

1. On the topic → **Create subscription**.

   | Field | Value |
   |-------|-------|
   | Protocol | **Email** |
   | Endpoint | your email address |

2. **Create subscription**, then **check your inbox and click the confirmation link**.
   Until you confirm, the subscription stays `PendingConfirmation` and no mail is delivered.

---

## 4.3 Tell the Function About the Topic

The function publishes only when `SNS_TOPIC_ARN` is set. Add it as an environment variable.

1. **Lambda** → `scheduled-heartbeat` → **Configuration** → **Environment variables** → **Edit**.
2. Add:

   | Key | Value |
   |-----|-------|
   | `SNS_TOPIC_ARN` | the ARN of `heartbeat-alerts` (e.g. `arn:aws:sns:us-east-1:123456789012:heartbeat-alerts`) |
   | `ENVIRONMENT` | `dev` |

3. **Save**.

> **Why an env var, not a hard-coded ARN?** The same code runs unchanged in dev/prod — you
> point it at a different topic per environment. This is the [Lambda Basics](../../aws-lambda-basics/README.md)
> environment-variable pattern reused.

---

## 4.4 Test

```bash
python src/test_invoke.py
```

The response now shows the message that was published, and within a few seconds you should
receive an email titled **`[dev] Scheduled heartbeat`**. The next scheduled run (≤5 min) will
email you too.

---

## AWS CLI (Alternative)

```bash
TOPIC_ARN=$(aws sns create-topic --name heartbeat-alerts --query TopicArn --output text)

aws sns subscribe \
  --topic-arn "$TOPIC_ARN" \
  --protocol email \
  --notification-endpoint you@example.com
# → confirm via the email link

aws lambda update-function-configuration \
  --function-name scheduled-heartbeat \
  --environment "Variables={SNS_TOPIC_ARN=$TOPIC_ARN,ENVIRONMENT=dev}"
```

---

## Checkpoint

- [ ] Topic `heartbeat-alerts` exists with a **confirmed** email subscription
- [ ] `SNS_TOPIC_ARN` env var is set on the function
- [ ] A manual invoke produces an email within seconds
- [ ] Logs now show `Published heartbeat to SNS topic ...`

---

**Next:** [Step 5 — Monitor and Verify](./05-monitor-and-verify.md)
