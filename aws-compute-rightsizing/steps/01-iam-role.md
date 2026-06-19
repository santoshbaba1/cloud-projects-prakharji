# Step 1 — IAM: Read CloudWatch, Resize Only Tagged Instances

This function can **stop, modify, and start EC2 instances** — so its permissions are split into
two halves on purpose:

- **Read-only** describes and CloudWatch reads on *all* instances (you can't filter a `Describe`
  by tag).
- **Mutating** actions (`StopInstances`, `ModifyInstanceAttribute`, `StartInstances`) gated by a
  **condition** so they only apply to instances tagged `Rightsize=true`.

That way a bug — or a bad event payload — can never resize an instance you didn't opt in.

---

## 1.1 Create the Role (Trust Policy)

1. **IAM** → **Roles** → **Create role**.

| Field | Value |
|-------|-------|
| Trusted entity type | **AWS service** |
| Use case | **Lambda** |

**Next**.

## 1.2 Attach Basic Execution (Logs)

Search `AWSLambdaBasicExecutionRole`, tick it, **Next**.

## 1.3 Name and Create

| Field | Value |
|-------|-------|
| Role name | `ComputeRightsizerExecutionRole` |
| Description | `compute-rightsizer — read CPU, resize Rightsize=true instances only` |

**Create role**, then open it and **copy the Role ARN**.

---

## 1.4 Add the Inline Policy

Open the role → **Add permissions** → **Create inline policy** → **JSON** tab. Paste:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadOnlyDiscovery",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "cloudwatch:GetMetricStatistics"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ResizeOnlyTaggedInstances",
      "Effect": "Allow",
      "Action": [
        "ec2:StopInstances",
        "ec2:StartInstances",
        "ec2:ModifyInstanceAttribute"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": { "aws:ResourceTag/Rightsize": "true" }
      }
    }
  ]
}
```

Name it `ComputeRightsizerPolicy` → **Create policy**.

| Permission | Service | Why It's Needed |
|------------|---------|-----------------|
| `ec2:DescribeInstances` | EC2 | List candidate instances and read their type/tags. `Describe` can't be tag-scoped, so it's `*` but read-only |
| `cloudwatch:GetMetricStatistics` | CloudWatch | Pull `CPUUtilization` per instance to judge utilization |
| `ec2:StopInstances` | EC2 | A type change requires the instance to be stopped first |
| `ec2:ModifyInstanceAttribute` | EC2 | Change the instance type while stopped |
| `ec2:StartInstances` | EC2 | Bring it back up on the new type |

> **Why the tag condition matters:** `aws:ResourceTag/Rightsize` is evaluated by EC2 at call
> time. If an instance isn't tagged `Rightsize=true`, the stop/modify/start calls are **denied** —
> even if the code asks for them. Read actions stay broad; *destructive* actions stay narrow.
>
> Notice there's **no** `ec2:TerminateInstances` anywhere — rightsizing never deletes.

If you also want SNS reports (Step 4), add this third statement now (replace the ARN after you
create the topic, or come back):

```json
{
  "Sid": "PublishReports",
  "Effect": "Allow",
  "Action": "sns:Publish",
  "Resource": "arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:rightsizing-alerts"
}
```

---

## AWS CLI (Alternative)

```bash
aws iam create-role \
  --role-name ComputeRightsizerExecutionRole \
  --assume-role-policy-document '{
    "Version":"2012-10-17",
    "Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]
  }'

aws iam attach-role-policy \
  --role-name ComputeRightsizerExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam put-role-policy \
  --role-name ComputeRightsizerExecutionRole \
  --policy-name ComputeRightsizerPolicy \
  --policy-document '{
    "Version":"2012-10-17",
    "Statement":[
      {"Sid":"ReadOnlyDiscovery","Effect":"Allow","Action":["ec2:DescribeInstances","cloudwatch:GetMetricStatistics"],"Resource":"*"},
      {"Sid":"ResizeOnlyTaggedInstances","Effect":"Allow","Action":["ec2:StopInstances","ec2:StartInstances","ec2:ModifyInstanceAttribute"],"Resource":"*","Condition":{"StringEquals":{"aws:ResourceTag/Rightsize":"true"}}}
    ]
  }'
```

---

## Checkpoint

- [ ] Role `ComputeRightsizerExecutionRole` exists, trusted by `lambda.amazonaws.com`
- [ ] `AWSLambdaBasicExecutionRole` attached
- [ ] Inline policy splits **read-only `*`** from **tag-gated** stop/modify/start
- [ ] No `TerminateInstances` permission anywhere
- [ ] You copied the Role ARN

---

**Next:** [Step 2 — Launch the Demo Instances](./02-launch-demo-instances.md)
