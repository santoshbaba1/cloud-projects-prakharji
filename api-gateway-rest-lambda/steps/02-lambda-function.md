# Step 2 — Create the Lambda Function

Now we create `quotes-api`, the function API Gateway will call. We deploy `src/app.py` and
set an `APP_VERSION` environment variable to `1.0.0` — that value is what `/version` returns,
and it's how you'll *see* which release is serving traffic during the deployment steps.

---

## 2.1 Package the Code

The function is a single file with no dependencies, so the zip is tiny:

```bash
cd src
zip function.zip app.py
```

---

## 2.2 Console — Create the Function

1. **Lambda → Create function → Author from scratch**.
2. **Function name:** `quotes-api`.
3. **Runtime:** `Python 3.14`.
4. **Architecture:** `x86_64` (default).
5. **Permissions → Change default execution role → Use an existing role →** `QuotesApiExecutionRole`.
6. **Create function**.
7. **Code** tab → **Upload from → .zip file** → upload `src/function.zip` → Save.
8. **Configuration → Environment variables → Edit → Add:** `APP_VERSION = 1.0.0` → Save.
9. **Code → Runtime settings → Edit → Handler:** `app.handler` → Save.

---

## 2.3 Test in the Console

1. **Test** tab → **Create new event**.
2. **Event name:** `list`, paste this proxy-style event:

   ```json
   { "httpMethod": "GET", "path": "/quotes", "pathParameters": null, "body": null }
   ```

3. **Test.** You should get a `200` with a body listing two quotes and `"version": "1.0.0"`.

---

## 2.4 AWS CLI (Alternative)

```bash
REGION=us-east-1
ROLE_ARN=$(aws iam get-role --role-name QuotesApiExecutionRole \
  --query 'Role.Arn' --output text)

aws lambda create-function --function-name quotes-api \
  --runtime python3.14 --handler app.handler \
  --role "$ROLE_ARN" --zip-file fileb://function.zip \
  --environment "Variables={APP_VERSION=1.0.0}" --region $REGION

aws lambda invoke --function-name quotes-api \
  --payload '{"httpMethod":"GET","path":"/quotes"}' \
  --cli-binary-format raw-in-base64-out out.json --region $REGION && cat out.json
```

---

## Checkpoint

- [ ] Function `quotes-api` exists with runtime `python3.14` and handler `app.handler`
- [ ] Environment variable `APP_VERSION=1.0.0` is set
- [ ] A console test of `GET /quotes` returns `200` with `"version":"1.0.0"`

---

**Next:** [Step 3 — Build the REST API](./03-rest-api.md)
