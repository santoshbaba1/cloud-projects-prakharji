# Step 4 — Deploy to a Stage (and Point It at an Alias)

Here's the thing newcomers trip on: **building the API doesn't make it live.** A REST API
goes public only when you create a **deployment** (a snapshot of the API config) and assign
it to a **stage** (a named, addressable copy — `dev`, `prod`, …). Change the API? You must
**redeploy** for the change to appear.

We'll also do one forward-looking thing now that makes every later deployment step easy: wire
the stage's Lambda integration to an **alias** through a **stage variable**, instead of
hardwiring it to the function. That single indirection is what makes rolling, canary, and
blue-green possible without ever editing the API again.

---

## 4.1 Publish the Lambda: Version 1 + the `live` Alias

A Lambda **version** is an immutable snapshot of code+config; `$LATEST` is the mutable draft.
An **alias** is a named pointer to a version (think: a git branch pointing at a commit). The
API will call the *alias*, so we can move the pointer later without touching API Gateway.

```bash
REGION=us-east-1

# Publish the current code as immutable version 1
aws lambda publish-version --function-name quotes-api --region $REGION \
  --query 'Version' --output text          # prints: 1

# Create alias "live" pointing at version 1
aws lambda create-alias --function-name quotes-api \
  --name live --function-version 1 --region $REGION
```

Console equivalent: **Lambda → quotes-api → Versions → Publish new version**, then
**Aliases → Create alias** → name `live`, version `1`.

---

## 4.2 Point the Integration at the Alias via a Stage Variable

We want the integration URI to read the alias name from a **stage variable** named
`lambdaAlias`. That way `prod` can say `lambdaAlias = live` and a canary can override it.

For **each** method you created (GET/POST `/quotes`, GET `/quotes/{id}`, GET `/version`):

1. Select the method → **Integration request** → **Edit**.
2. In the **Lambda function** box, set it to use the stage variable and alias:

   ```
   quotes-api:${stageVariables.lambdaAlias}
   ```

   (In the console you can type `quotes-api:${stageVariables.lambdaAlias}` as the function
   name.) Save.

Because the function name now contains a stage variable, you must grant API Gateway
permission to invoke the **alias** explicitly (the console's auto-permission only covered the
bare function):

```bash
REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
API_ID=<your-api-id>

aws lambda add-permission --function-name quotes-api \
  --qualifier live \
  --statement-id apigw-invoke-live --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*" --region $REGION
```

> You'll add one more `add-permission` for each *new* alias you introduce in later steps
> (e.g. `canary`, `green`). API Gateway can only invoke an alias it has explicit permission
> for. This is the #1 cause of `500 Internal server error` in this project — see
> [troubleshooting.md](../troubleshooting.md).

---

## 4.3 Create the `prod` Deployment + Stage

**Console:**

1. **Deploy API** (top right).
2. **Stage:** *New stage* → **Stage name:** `prod` → **Deploy**.
3. On the stage page, open **Stage variables → Add** → `lambdaAlias = live` → Save.
4. Copy the **Invoke URL** at the top (e.g. `https://abc123.execute-api.us-east-1.amazonaws.com/prod`).

**CLI:**

```bash
aws apigateway create-deployment --rest-api-id $API_ID \
  --stage-name prod --variables lambdaAlias=live --region $REGION
```

---

## 4.4 Test the Live API

```bash
API=https://abc123.execute-api.us-east-1.amazonaws.com/prod
curl -s $API/quotes              # the two quotes, "version":"1.0.0"
curl -s $API/quotes/1            # one quote
curl -s "$API/version"           # {"version":"1.0.0"}
curl -s -X POST $API/quotes -d '{"text":"Make it work, then make it right."}'
```

`GET /version` returning `1.0.0` confirms the stage → variable → `live` alias → version 1
chain works end to end. Keep that command handy — it's your "which version is serving?"
probe for the next three steps.

---

## Checkpoint

- [ ] Lambda **version 1** is published and alias **`live`** points to it
- [ ] Every method's integration uses `quotes-api:${stageVariables.lambdaAlias}`
- [ ] API Gateway has `lambda:InvokeFunction` permission on the **`live`** alias
- [ ] Stage **`prod`** exists with stage variable `lambdaAlias=live`
- [ ] `curl $API/version` returns `{"version":"1.0.0"}`

---

**Next:** [Step 5 — Rolling Deployment](./05-rolling-deployment.md)
