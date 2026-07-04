# Step 3 — Create the Lambda Function

Now we deploy `tasks-api`. It uses **`boto3`** to talk to DynamoDB — and `boto3` is already
included in the Lambda Python runtime, so the zip is still just our one file. We pass the
table name and version through environment variables.

---

## 3.1 Package the Code

```bash
cd src
zip function.zip app.py
```

> No `pip install` needed: `boto3` ships with the Lambda runtime. If you later add a library
> that *isn't* bundled, you'd use a Lambda **layer** — see
> [lambda-layers](../../../../beginner/aws/aws-lambda-layers/README.md).

---

## 3.2 Console — Create the Function

1. **Lambda → Create function → Author from scratch**.
2. **Function name:** `tasks-api`.
3. **Runtime:** `Python 3.14`.
4. **Permissions → Use an existing role →** `TasksApiExecutionRole`.
5. **Create function**.
6. **Code → Upload from → .zip file** → `src/function.zip` → Save.
7. **Configuration → Environment variables → Edit → Add two:**
   - `TABLE_NAME = tasks`
   - `APP_VERSION = 1.0.0`
8. **Code → Runtime settings → Edit → Handler:** `app.handler`.

---

## 3.3 Test in the Console

1. **Test** tab → **Create new event** named `list`, payload (HTTP API v2 shape):

   ```json
   {
     "rawPath": "/tasks",
     "requestContext": { "http": { "method": "GET", "path": "/tasks" } },
     "pathParameters": null,
     "body": null
   }
   ```

2. **Test.** Expect `200` and a JSON body listing your seed item (and `"version":"1.0.0"`).

3. Try a create — new event `create`:

   ```json
   {
     "rawPath": "/tasks",
     "requestContext": { "http": { "method": "POST", "path": "/tasks" } },
     "body": "{\"title\": \"ship it safely\"}"
   }
   ```

   Expect `201` with a generated `id`.

> A `500` with `AccessDeniedException` in the logs means the role's DynamoDB policy is missing
> or scoped to the wrong table ARN — revisit Step 1.

---

## 3.4 AWS CLI (Alternative)

```bash
REGION=us-east-1
ROLE_ARN=$(aws iam get-role --role-name TasksApiExecutionRole --query 'Role.Arn' --output text)

aws lambda create-function --function-name tasks-api \
  --runtime python3.14 --handler app.handler --role "$ROLE_ARN" \
  --zip-file fileb://function.zip \
  --environment "Variables={TABLE_NAME=tasks,APP_VERSION=1.0.0}" --region $REGION

aws lambda invoke --function-name tasks-api \
  --payload '{"rawPath":"/tasks","requestContext":{"http":{"method":"GET","path":"/tasks"}}}' \
  --cli-binary-format raw-in-base64-out out.json --region $REGION && cat out.json
```

---

## Checkpoint

- [ ] Function `tasks-api` exists, runtime `python3.14`, handler `app.handler`
- [ ] Env vars `TABLE_NAME=tasks` and `APP_VERSION=1.0.0` set
- [ ] Console test of `GET /tasks` returns `200`; `POST /tasks` returns `201`
- [ ] No `AccessDeniedException` in CloudWatch logs

---

**Next:** [Step 4 — Build the HTTP API](./04-http-api.md)
