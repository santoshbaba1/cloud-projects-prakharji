# Troubleshooting — API Gateway REST API + Lambda

Format: **Error → Cause → Fix.**

---

### `500 Internal server error` (and CloudWatch shows no Lambda invocation)

**Cause:** API Gateway tried to invoke a Lambda **alias** it has no permission for. When you
switched the integration to `quotes-api:${stageVariables.lambdaAlias}` (Step 4), the console's
auto-added permission only covered the bare function — not each alias.

**Fix:** add an invoke permission for *every* alias the stage variable can resolve to
(`live`, `canary`, `blue`, `green`):

```bash
REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
API_ID=<your-api-id>
aws lambda add-permission --function-name quotes-api --qualifier live \
  --statement-id apigw-invoke-live --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*" --region $REGION
```

---

### Changes to the API don't show up at the invoke URL

**Cause:** You edited resources/methods/integrations but didn't **redeploy**. A REST API only
serves what's in the deployment attached to the stage.

**Fix:** **Deploy API → select the `prod` stage → Deploy**. (Stage *variable* changes take
effect immediately and do **not** need a redeploy — only structural changes do.)

---

### `{"message":"Missing Authentication Token"}`

**Cause:** You hit a path/method that isn't defined, or you forgot the stage name in the URL.
This is API Gateway's generic "no matching route" response.

**Fix:** Include the stage: `https://<id>.execute-api.us-east-1.amazonaws.com/prod/quotes`,
and confirm the method exists on that resource.

---

### `/version` always returns the old version during a rolling deploy

**Cause:** Either the weight is very low (10% means ~1 in 10 requests) or you published the
version *before* the env-var update landed.

**Fix:** Loop the probe (`for i in $(seq 1 30)`) to see the split. If v2 *never* appears,
re-check that `publish-version` ran **after** `update-function-configuration` finished — use
`aws lambda wait function-updated` between them, then publish again.

---

### Canary tab: "promote" did nothing visible

**Cause:** Promote copies the **canary stage variable overrides** into the base stage, but if
your base alias (`live`) still points at v1, you also need to move that alias — or the base was
already pointing where the canary did.

**Fix:** After promoting, confirm `live` points at the new version
(`aws lambda get-alias --function-name quotes-api --name live`) and that `canarySettings` is
removed from the stage.

---

### `ResourceConflictException: Alias already exists`

**Cause:** Re-running a `create-alias` from an earlier attempt.

**Fix:** Use `update-alias` instead, or delete it first:
`aws lambda delete-alias --function-name quotes-api --name <alias>`.

---

### Proxy integration returns the body as a string with escaped quotes

**Cause:** Your handler returned a dict for `body` instead of a JSON **string**. With proxy
integration, `body` must be a string.

**Fix:** `json.dumps(...)` the body (as `_response()` in `app.py` already does).

---

### POST returns 400 "body must be valid JSON" even though you sent JSON

**Cause:** `curl` sent form-encoding, or you sent no `Content-Type`. The handler parses
`event["body"]` as JSON.

**Fix:** Send a JSON string: `curl -X POST $API/quotes -H 'Content-Type: application/json' -d '{"text":"hi"}'`.
