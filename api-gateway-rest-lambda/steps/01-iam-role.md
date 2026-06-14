# Step 1 — IAM: The Lambda Execution Role

Every Lambda function assumes an **execution role** when it runs. Our Quotes API touches no
other AWS service, so it needs exactly one thing: permission to write its logs to CloudWatch.
We grant that and nothing more — least privilege from line one.

---

## 1.1 What You're Creating

**Role name:** `QuotesApiExecutionRole`
**Trust policy:** allows `lambda.amazonaws.com` to assume it.
**Permissions:**

| Permission | Service | Why It's Needed |
|------------|---------|-----------------|
| `logs:CreateLogGroup` | CloudWatch | Create the function's log group on first run |
| `logs:CreateLogStream` | CloudWatch | Create a log stream per execution environment |
| `logs:PutLogEvents` | CloudWatch | Write log lines (your `print`s and errors) |

> The AWS-managed policy **`AWSLambdaBasicExecutionRole`** grants exactly these three. We
> attach it rather than hand-writing the policy. Later steps (versions, aliases, canary)
> need **no new Lambda permissions** — they're API Gateway and Lambda *control-plane*
> actions you perform as the operator, not things the function itself does.

---

## 1.2 Console — Create the Role

1. **IAM → Roles → Create role**.
2. **Trusted entity type:** AWS service → **Use case: Lambda** → Next.
3. Search and check **`AWSLambdaBasicExecutionRole`** → Next.
4. **Role name:** `QuotesApiExecutionRole` → **Create role**.

---

## 1.3 AWS CLI (Alternative)

```bash
cat > lambda-trust.json <<'JSON'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
JSON

aws iam create-role --role-name QuotesApiExecutionRole \
  --assume-role-policy-document file://lambda-trust.json

aws iam attach-role-policy --role-name QuotesApiExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

---

## Checkpoint

- [ ] Role `QuotesApiExecutionRole` trusts `lambda.amazonaws.com`
- [ ] `AWSLambdaBasicExecutionRole` is attached
- [ ] No other permissions are attached (least privilege)

---

**Next:** [Step 2 — Create the Lambda Function](./02-lambda-function.md)
