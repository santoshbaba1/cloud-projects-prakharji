# Step 1 — IAM: Execution Role with Scoped DynamoDB Access

This function does two things, so its role needs exactly two grants: write logs to
CloudWatch, and read/write **one** DynamoDB table. We scope the DynamoDB permission to the
`tasks` table's ARN only — never `Resource: "*"`. That's the least-privilege habit worth
building now.

---

## 1.1 What You're Creating

**Role name:** `TasksApiExecutionRole`
**Trust policy:** allows `lambda.amazonaws.com` to assume it.
**Permissions:**

| Permission | Service | Why It's Needed |
|------------|---------|-----------------|
| `logs:CreateLogGroup`, `CreateLogStream`, `PutLogEvents` | CloudWatch | Function logging (via `AWSLambdaBasicExecutionRole`) |
| `dynamodb:GetItem` | DynamoDB | `GET /tasks/{id}` |
| `dynamodb:Scan` | DynamoDB | `GET /tasks` (list) |
| `dynamodb:PutItem` | DynamoDB | `POST /tasks` (create) |
| `dynamodb:UpdateItem` | DynamoDB | `PUT /tasks/{id}` (update) |
| `dynamodb:DeleteItem` | DynamoDB | `DELETE /tasks/{id}` |

> **Why scope to one table?** If the function is ever compromised or buggy, the blast radius
> is a single table — it can't read or wipe other data in the account. The DynamoDB actions
> are restricted to `arn:aws:dynamodb:us-east-1:<account>:table/tasks`.

---

## 1.2 Console — Create the Role

1. **IAM → Roles → Create role** → AWS service → **Lambda** → Next.
2. Attach **`AWSLambdaBasicExecutionRole`** (the logging policy) → Next.
3. **Role name:** `TasksApiExecutionRole` → **Create role**.
4. Open the new role → **Add permissions → Create inline policy** → **JSON** tab → paste
   (replace `<account>` with your account id):

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Action": [
         "dynamodb:GetItem", "dynamodb:Scan",
         "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem"
       ],
       "Resource": "arn:aws:dynamodb:us-east-1:<account>:table/tasks"
     }]
   }
   ```

5. **Policy name:** `TasksTableAccess` → **Create policy**.

---

## 1.3 AWS CLI (Alternative)

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

cat > lambda-trust.json <<'JSON'
{ "Version": "2012-10-17",
  "Statement": [{ "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole" }] }
JSON

aws iam create-role --role-name TasksApiExecutionRole \
  --assume-role-policy-document file://lambda-trust.json
aws iam attach-role-policy --role-name TasksApiExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

cat > tasks-policy.json <<JSON
{ "Version": "2012-10-17",
  "Statement": [{ "Effect": "Allow",
    "Action": ["dynamodb:GetItem","dynamodb:Scan","dynamodb:PutItem","dynamodb:UpdateItem","dynamodb:DeleteItem"],
    "Resource": "arn:aws:dynamodb:us-east-1:${ACCOUNT_ID}:table/tasks" }] }
JSON

aws iam put-role-policy --role-name TasksApiExecutionRole \
  --policy-name TasksTableAccess --policy-document file://tasks-policy.json
```

---

## Checkpoint

- [ ] Role `TasksApiExecutionRole` trusts `lambda.amazonaws.com`
- [ ] `AWSLambdaBasicExecutionRole` attached (logging)
- [ ] Inline policy grants the 5 DynamoDB actions on **only** the `tasks` table ARN

---

**Next:** [Step 2 — Create the DynamoDB Table](./02-dynamodb-table.md)
