# Step 3 — API Gateway: The Public HTTPS Endpoint

API Gateway is what the ALB was in the EC2 project — the public front door — except it's
fully managed, HTTPS by default, and scales with no configuration. We use the **HTTP API**
flavour (cheaper and simpler than the older REST API).

---

## 3.1 Console — Create the HTTP API

1. **API Gateway console → Create API → HTTP API → Build**.
2. **Integrations:** Add integration → **Lambda** → `serverless-webapp`.
3. **API name:** `serverless-webapp-api` → Next.
4. **Configure routes** — add one route per endpoint, all method `GET`, all integrating
   with the `serverless-webapp` Lambda:

   | Method | Resource path |
   |--------|---------------|
   | GET | `/` |
   | GET | `/health` |
   | GET | `/api/info` |
   | GET | `/api/load` |

5. **Stages:** keep the default `$default` stage with **auto-deploy** on → Next → **Create**.
6. Copy the **Invoke URL** (e.g. `https://abc123.execute-api.us-east-1.amazonaws.com`).

> Adding the Lambda integration from the console automatically grants API Gateway permission
> to invoke the function (a resource-based policy on the Lambda). With the CLI you add this
> permission yourself — see 3.3.

---

## 3.2 Test the Live API

```bash
API=https://abc123.execute-api.us-east-1.amazonaws.com
curl -s $API/                       # service metadata, "compute":"AWS Lambda"
curl -s $API/health                 # {"status":"healthy",...}
curl -s "$API/api/load?seconds=2"   # burns 2s; watch Duration in CloudWatch next
```

All four routes should respond. A path you didn't define (e.g. `/nope`) returns API
Gateway's own `{"message":"Not Found"}` — your handler's 404 only fires for paths that *are*
routed to it.

---

## 3.3 AWS CLI (Alternative — quick create)

```bash
REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
FN_ARN=$(aws lambda get-function --function-name serverless-webapp \
  --query 'Configuration.FunctionArn' --output text --region $REGION)

API_ID=$(aws apigatewayv2 create-api --name serverless-webapp-api \
  --protocol-type HTTP --target $FN_ARN \
  --query 'ApiId' --output text --region $REGION)

# Allow API Gateway to invoke the function
aws lambda add-permission --function-name serverless-webapp \
  --statement-id apigw-invoke --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*" --region $REGION

echo "API_ID=$API_ID"
aws apigatewayv2 get-api --api-id $API_ID --query 'ApiEndpoint' --output text --region $REGION
```

> The `--target` shortcut creates a catch-all `$default` route to the function, so all four
> paths reach your handler and it routes internally. **Save `API_ID`** — Step 4's dashboard
> needs it.

---

## Checkpoint

- [ ] HTTP API `serverless-webapp-api` exists with a `$default` auto-deploy stage
- [ ] Routes for `/`, `/health`, `/api/info`, `/api/load` reach the Lambda
- [ ] `curl`ing the invoke URL returns JSON from every endpoint
- [ ] You saved the **Invoke URL** and **API_ID**

---

**Next:** [Step 4 — CloudWatch Monitoring](./04-cloudwatch-monitoring.md)
