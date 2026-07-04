# Step 1 — IAM: Create the EC2 Control Role

This function can power EC2 instances on and off, so its role deserves care. It gets exactly
three EC2 actions — **describe, start, stop** — and **nothing else**. No `TerminateInstances`,
no `RunInstances`. If the function is ever misused, the worst it can do is toggle power.

---

## 1.1 Create the Role (Trust Policy)

1. **IAM** → **Roles** → **Create role**.

| Field | Value |
|-------|-------|
| Trusted entity type | **AWS service** |
| Use case | **Lambda** |

**Next**.

---

## 1.2 Attach Basic Execution (Logs)

Search `AWSLambdaBasicExecutionRole`, tick it, **Next**.

| Policy | Why |
|--------|-----|
| `AWSLambdaBasicExecutionRole` | CloudWatch Logs write access |

---

## 1.3 Name and Create

| Field | Value |
|-------|-------|
| Role name | `Ec2SchedulerExecutionRole` |
| Description | `ec2-scheduler — describe/start/stop EC2 only` |

**Create role**, then open it and **copy the Role ARN**.

---

## 1.4 Add the EC2 Control Policy (Inline)

1. Open the role → **Add permissions** → **Create inline policy** → **JSON** tab.
2. Paste:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DescribeIsGlobal",
      "Effect": "Allow",
      "Action": "ec2:DescribeInstances",
      "Resource": "*"
    },
    {
      "Sid": "StartStopOnlyTaggedInstances",
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:StopInstances"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": { "aws:ResourceTag/AutoPower": "true" }
      }
    }
  ]
}
```

3. Name it `Ec2StartStopTagged` → **Create policy**.

| Permission | Service | Why It's Needed |
|------------|---------|-----------------|
| `ec2:DescribeInstances` | EC2 | List instances to find the tagged ones. **Describe actions don't support resource-level permissions**, so this must be `Resource: "*"` |
| `ec2:StartInstances`, `ec2:StopInstances` | EC2 | Power instances on/off — **gated by a condition** so it works *only* on instances tagged `AutoPower=true` |

> **Defense in depth:** even though the *code* filters by tag, the **IAM condition** enforces
> it too. If someone changed the code to target every instance, IAM would still refuse to
> start/stop anything not tagged `AutoPower=true`. Code filters for correctness; IAM filters
> for security.

---

## AWS CLI (Alternative)

```bash
aws iam create-role \
  --role-name Ec2SchedulerExecutionRole \
  --assume-role-policy-document '{
    "Version":"2012-10-17",
    "Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]
  }'

aws iam attach-role-policy \
  --role-name Ec2SchedulerExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam put-role-policy \
  --role-name Ec2SchedulerExecutionRole \
  --policy-name Ec2StartStopTagged \
  --policy-document '{
    "Version":"2012-10-17",
    "Statement":[
      {"Effect":"Allow","Action":"ec2:DescribeInstances","Resource":"*"},
      {"Effect":"Allow","Action":["ec2:StartInstances","ec2:StopInstances"],"Resource":"*",
       "Condition":{"StringEquals":{"aws:ResourceTag/AutoPower":"true"}}}
    ]
  }'
```

---

## Checkpoint

- [ ] Role `Ec2SchedulerExecutionRole` exists, trusted by `lambda.amazonaws.com`
- [ ] `AWSLambdaBasicExecutionRole` attached
- [ ] Inline policy `Ec2StartStopTagged` grants describe + tag-gated start/stop only
- [ ] You copied the Role ARN

---

**Next:** [Step 2 — Launch a Test EC2 Instance](./02-launch-test-ec2.md)
