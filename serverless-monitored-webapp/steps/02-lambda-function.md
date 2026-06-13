# Step 2 — Create the Lambda Function

Now the compute tier — a single function that replaces the entire EC2 fleet. The code is
`src/app.py`; its entry point is `app.handler`.

---

## 2.1 Console — Create the Function

1. **Lambda console → Create function → Author from scratch**.

   | Field | Value |
   |-------|-------|
   | Function name | `serverless-webapp` |
   | Runtime | **Python 3.14** |
   | Architecture | `x86_64` |
   | Permissions | Use an existing role → `LambdaWebAppExecutionRole` |

2. **Create function.**

---

## 2.2 Add the Code

1. In the **Code** tab, open the inline editor's `lambda_function.py`.
2. Replace its entire contents with `src/app.py` from this project.
3. **Important:** set the **Handler** to `app.handler` (Runtime settings → Edit). The file
   is `app.py` and the function is `handler`, so the handler string is `app.handler`. If you
   keep the default filename `lambda_function.py`, rename the file to `app.py` or set the
   handler to `lambda_function.handler` to match.
4. Click **Deploy**.

> For a multi-file app you'd upload a zip instead — that's exactly what the GitHub Actions
> pipeline does in Step 7.

---

## 2.3 Test It in the Console

1. **Test** tab → create a new event. Paste an API Gateway HTTP API v2 event:

   ```json
   {
     "rawPath": "/health",
     "requestContext": {"http": {"path": "/health", "method": "GET"}},
     "queryStringParameters": null
   }
   ```

2. **Test.** The response should be:

   ```json
   {"statusCode": 200, "headers": {"Content-Type": "application/json"},
    "body": "{\"status\": \"healthy\", ...}"}
   ```

3. Try another event with `"rawPath": "/api/load"` and
   `"queryStringParameters": {"seconds": "2"}` — note the **Duration** reported in the
   execution result climbs to ~2 seconds. That's the metric you'll alarm on in Step 4.

---

## 2.4 Increase the Timeout

The default Lambda timeout is 3 seconds, but `/api/load?seconds=10` can run longer:

1. **Configuration → General configuration → Edit**.
2. Set **Timeout** to `15` seconds. **Save**.

---

## 2.5 AWS CLI (Alternative)

```bash
REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

cd src && zip ../function.zip app.py && cd ..

aws lambda create-function --function-name serverless-webapp \
  --runtime python3.14 --handler app.handler \
  --role arn:aws:iam::$ACCOUNT_ID:role/LambdaWebAppExecutionRole \
  --zip-file fileb://function.zip --timeout 15 --region $REGION
```

---

## Checkpoint

- [ ] Function `serverless-webapp` exists on runtime **python3.14**
- [ ] Handler is set to `app.handler` and matches the filename
- [ ] A `/health` test event returns `statusCode 200`
- [ ] An `/api/load` test event shows increased Duration
- [ ] Timeout raised to 15 seconds

---

**Next:** [Step 3 — API Gateway](./03-api-gateway.md)
