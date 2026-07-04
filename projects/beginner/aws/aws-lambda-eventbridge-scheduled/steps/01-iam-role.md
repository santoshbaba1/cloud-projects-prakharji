# Step 1 — IAM: Create the Execution Role

Like every Lambda, the heartbeat function needs an **execution role** so the service
can assume it and write logs. Because this function *may* publish to SNS (Step 4), we
will also allow `sns:Publish` — scoped to a single topic, not all of SNS.

---

## 1.1 Open IAM

1. In the AWS Console, search for **IAM** and open it.
2. Left sidebar → **Roles** → **Create role**.

---

## 1.2 Configure the Trust Policy

| Field | Value |
|-------|-------|
| Trusted entity type | **AWS service** |
| Use case | **Lambda** |

Click **Next**.

> **Why:** The trust policy lets `lambda.amazonaws.com` call `sts:AssumeRole`. Without
> it, Lambda cannot use the role at all.

---

## 1.3 Attach the Basic Execution Policy

Search for `AWSLambdaBasicExecutionRole`, tick it, click **Next**.

| Policy | Why it's needed |
|--------|-----------------|
| `AWSLambdaBasicExecutionRole` | `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` — so the function can write to CloudWatch Logs |

---

## 1.4 Name and Create

| Field | Value |
|-------|-------|
| Role name | `ScheduledHeartbeatExecutionRole` |
| Description | `Execution role for scheduled-heartbeat — logs + SNS publish` |

Click **Create role**, then open it and **copy the Role ARN** for Step 2.

---

## 1.5 Add SNS Publish (Inline Policy)

You'll create the SNS topic in Step 4, but we add the permission now so the role is ready.

1. Open `ScheduledHeartbeatExecutionRole` → **Add permissions** → **Create inline policy**.
2. Choose the **JSON** tab and paste:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "sns:Publish",
    "Resource": "arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:heartbeat-alerts"
  }]
}
```

3. Replace `YOUR_ACCOUNT_ID` with your 12-digit account ID.
4. Name it `HeartbeatSnsPublish` and **Create policy**.

| Permission | Service | Why It's Needed |
|------------|---------|-----------------|
| `sns:Publish` | SNS | Send the heartbeat message to the `heartbeat-alerts` topic — scoped to *that one topic* |

> **Least privilege:** We name the exact topic ARN rather than `"Resource": "*"`. If the
> function is ever compromised, it can publish to this one topic and nothing else.

---

## AWS CLI (Alternative)

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws iam create-role \
  --role-name ScheduledHeartbeatExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": { "Service": "lambda.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }]
  }'

aws iam attach-role-policy \
  --role-name ScheduledHeartbeatExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam put-role-policy \
  --role-name ScheduledHeartbeatExecutionRole \
  --policy-name HeartbeatSnsPublish \
  --policy-document "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [{
      \"Effect\": \"Allow\",
      \"Action\": \"sns:Publish\",
      \"Resource\": \"arn:aws:sns:us-east-1:${ACCOUNT_ID}:heartbeat-alerts\"
    }]
  }"
```

---

## Checkpoint

- [ ] Role `ScheduledHeartbeatExecutionRole` exists with trusted entity `lambda.amazonaws.com`
- [ ] `AWSLambdaBasicExecutionRole` is attached
- [ ] Inline policy `HeartbeatSnsPublish` allows `sns:Publish` on the `heartbeat-alerts` ARN
- [ ] You copied the Role ARN

---

**Next:** [Step 2 — Create and Deploy the Function](./02-create-function.md)
