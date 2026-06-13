# Step 1 — IAM: The Lambda Execution Role

Every Lambda function assumes an **execution role** when it runs. At minimum it needs
permission to write its logs to CloudWatch. We grant exactly that and nothing more.

---

## 1.1 What You're Creating

**Role name:** `LambdaWebAppExecutionRole`
**Trust policy:** allows `lambda.amazonaws.com` to assume it.
**Permissions:**

| Permission | Service | Why It's Needed |
|------------|---------|-----------------|
| `logs:CreateLogGroup` | CloudWatch | Create the function's log group on first run |
| `logs:CreateLogStream` | CloudWatch | Create a log stream per execution environment |
| `logs:PutLogEvents` | CloudWatch | Write log lines (your `print`s and errors) |

> The AWS-managed policy **`AWSLambdaBasicExecutionRole`** grants exactly these three.
> That's the whole role — our app calls no other AWS services. Compare this to the EC2
> project's instance role, which also needed SSM and the CloudWatch agent; Lambda's logging
> is built in, so the role is smaller.

---

## 1.2 Console — Create the Role

You can let the Lambda console create this role for you in Step 2 — but creating it
explicitly first makes the permission model clear:

1. **IAM → Roles → Create role**.
2. **Trusted entity:** AWS service → **Lambda** → Next.
3. Attach **`AWSLambdaBasicExecutionRole`**.
4. **Role name:** `LambdaWebAppExecutionRole` → **Create role**.

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

aws iam create-role --role-name LambdaWebAppExecutionRole \
  --assume-role-policy-document file://lambda-trust.json

aws iam attach-role-policy --role-name LambdaWebAppExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

---

## Checkpoint

- [ ] Role `LambdaWebAppExecutionRole` trusts `lambda.amazonaws.com`
- [ ] `AWSLambdaBasicExecutionRole` is attached
- [ ] No other permissions are attached (least privilege)

---

**Next:** [Step 2 — Create the Lambda Function](./02-lambda-function.md)
