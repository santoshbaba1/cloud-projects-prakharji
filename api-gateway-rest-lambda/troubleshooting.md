# Troubleshooting — API Gateway REST API + Lambda

Format: **Error → Cause → Fix.**

---

### `500 Internal server error` (and CloudWatch shows no Lambda invocation)

**Cause:** API Gateway tried to invoke a Lambda **alias** it has no permission for. When you
switched the integration to the stage-variable ARN
`arn:aws:lambda:us-east-1:<ACCOUNT_ID>:function:quotes-api:${stageVariables.lambdaAlias}`
(Step 4), the console either couldn't auto-add a permission at all (the qualifier is a
`${…}` placeholder, not a real alias) or covered only the bare function — never each alias.

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

**Cause:** Despite the wording, this is **almost never about auth.** It's API Gateway's
generic "**no matching route** for this method + path on the deployed stage." The request
reached API Gateway but didn't match any resource/method. Common triggers:

- **Stage name missing from the URL** — e.g. calling `.../quotes` instead of `.../prod/quotes`.
- **Hitting the bare stage root** — `.../prod` with no resource path. The root `/` has no
  method, so it returns this error.
- **Not deployed / not redeployed** — the resource or method exists in the console but wasn't
  deployed to `prod`, so the stage doesn't serve it.
- **Wrong HTTP method** — e.g. `POST` to a path that only defines `GET`, or `GET /version`
  when the `/version` resource/method was never created.
- **Path typo or trailing slash** mismatch.

**Fix:** First, list what's actually deployed and compare against the URL you're calling:

```bash
REGION=us-east-1
API_ID=<your-api-id>

# Every resource path + the methods defined on it:
aws apigateway get-resources --rest-api-id $API_ID --region $REGION \
  --query 'items[].{path:path,methods:keys(resourceMethods)}' --output table

# Confirm the prod stage exists and has a deployment:
aws apigateway get-stages --rest-api-id $API_ID --region $REGION \
  --query 'item[].{stage:stageName,deployment:deploymentId}' --output table
```

- Path **not listed** → wrong path, or create the resource/method and **redeploy**.
- Path listed but **missing your verb** → add/deploy that method.
- Looks right but stage is missing or `deploymentId` is stale → **Deploy API → prod** again.

Then call the full URL: `https://<id>.execute-api.us-east-1.amazonaws.com/prod/quotes`.

> This is a *routing* error — distinct from `500 Internal server error`, which is the Lambda
> **alias-permission** issue above. A `403` here means routing; a `500` means the route matched
> but invoking the alias failed.

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
