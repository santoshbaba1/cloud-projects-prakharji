# Troubleshooting — Serverless Monitored Web App

Format: **Symptom → Cause → Fix**.

---

## Lambda

### `Runtime.ImportModuleError` / "Unable to import module 'app'"
- **Cause:** The handler string doesn't match the file/function name.
- **Fix:** Handler must be `app.handler` (file `app.py`, function `handler`). If the console
  created `lambda_function.py`, either rename it to `app.py` or set the handler to
  `lambda_function.handler`. Update under **Runtime settings → Edit**.

### `Task timed out after 3.00 seconds` on `/api/load`
- **Cause:** Default Lambda timeout is 3 s; `/api/load?seconds=10` runs longer.
- **Fix:** **Configuration → General configuration → Edit → Timeout = 15 s** (Step 2.4).

### Function returns but the browser shows a raw `{ "statusCode": 200, ... }`
- **Cause:** You invoked Lambda directly (or via a non-proxy integration) instead of through
  the HTTP API, so API Gateway didn't unwrap the response.
- **Fix:** Call the **API Gateway invoke URL**, not the Lambda. The HTTP API proxy
  integration reads `statusCode`/`headers`/`body` and returns proper HTTP.

### Changes to the code don't take effect
- **Cause:** You edited the inline editor but didn't click **Deploy**, or deployed a stale zip.
- **Fix:** Click **Deploy** in the console editor; for CLI/Actions, confirm
  `update-function-code` ran and `aws lambda wait function-updated` returned.

---

## API Gateway

### `{"message":"Not Found"}` from the API
- **Cause:** That path has no route defined on the HTTP API (API Gateway's own 404, before
  your handler runs).
- **Fix:** Add the route (Step 3.1) or use the `--target` catch-all (Step 3.3) so all paths
  reach the function. Note: your handler's *own* 404 only fires for routed paths.

### `{"message":"Internal Server Error"}` (HTTP 500)
- **Cause:** The Lambda errored or returned a malformed response shape.
- **Fix:** Check `/aws/lambda/serverless-webapp` logs for the stack trace. Ensure the handler
  returns a dict with `statusCode`, `headers`, and a **string** `body` (JSON-encoded).

### `403 Forbidden` / "not authorized to perform: lambda:InvokeFunction"
- **Cause:** API Gateway lacks permission to invoke the function (CLI path — the console adds
  it automatically).
- **Fix:** Add the resource permission with `aws lambda add-permission` (Step 3.3).

---

## Monitoring

### No metrics for the function
- **Cause:** The function has never been invoked, or you're looking at the wrong dimension.
- **Fix:** Invoke it once via the API. Lambda metrics use dimension
  `FunctionName=serverless-webapp`.

### Duration alarm never fires even under load
- **Cause:** Threshold/statistic mismatch, or requests too fast.
- **Fix:** Confirm the alarm uses **ExtendedStatistic p95** with threshold 3000 ms. Drive
  several `/api/load?seconds=5` calls so p95 clears 3 s.

### Alarm fires but no email
- **Cause:** SNS subscription still **Pending**.
- **Fix:** SNS → Subscriptions must read **Confirmed**; click the link in the confirmation
  email (check spam).

---

## GitHub Actions Deploy

### `Could not assume role with OIDC`
- **Cause:** Trust policy `sub` doesn't match `repo:ORG/REPO:ref:refs/heads/main`, or the
  OIDC provider is missing.
- **Fix:** Fix the `sub` condition and confirm the
  `token.actions.githubusercontent.com` provider exists with audience `sts.amazonaws.com`.

### `AccessDenied: lambda:UpdateFunctionCode`
- **Cause:** The deploy role's permission policy doesn't cover the function ARN.
- **Fix:** Scope the policy `Resource` to
  `arn:aws:lambda:us-east-1:<ACCOUNT_ID>:function:serverless-webapp` (Step 7.3).

### Deploy succeeds but `version` is unchanged
- **Cause:** You bumped `APP_VERSION` in the wrong file, or the zip didn't include the edit.
- **Fix:** Confirm the change is in `src/app.py` and the workflow zips that file. Check the
  Actions log's package step.
