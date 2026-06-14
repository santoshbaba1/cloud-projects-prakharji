# Deployment Strategies — Shipping `serverless-webapp` Safely

This guidance shows how to roll out a new version of the `serverless-webapp` Lambda **without
downtime and with fast rollback**, using only native Lambda + API Gateway primitives (no
CodeDeploy). It complements the project's GitHub Actions pipeline (Step 7), which today runs a
plain `update-function-code` — a *full, instant* deploy. The strategies below give you a
**gradual or reversible** alternative.

> Want a from-scratch, build-it-yourself version of this material? Do the dedicated projects:
> - [api-gateway-rest-lambda](../api-gateway-rest-lambda/README.md) — REST API, includes API
>   Gateway's **native gateway-level canary release**
> - [api-gateway-http-dynamodb-crud](../api-gateway-http-dynamodb-crud/README.md) — HTTP API
>   (like this project), all deploys at the **Lambda-alias** level
>
> This file is the "how to apply it to the app you already built here" summary.

---

## Why this app needs a small change first

In Step 3 this project wired the **HTTP API integration directly to the function** (the bare
`serverless-webapp`, no qualifier). Deployment strategies need the integration to point at a
**Lambda alias** instead, so you can move the alias without touching the API. One-time setup:

```bash
REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
API_ID=<your-api-id>   # saved in Step 3

# 1. Publish the current code as version 1 and create the 'live' alias
aws lambda publish-version --function-name serverless-webapp --region $REGION \
  --query 'Version' --output text
aws lambda create-alias --function-name serverless-webapp \
  --name live --function-version 1 --region $REGION

# 2. Repoint the HTTP API integration at the alias ARN
INTEGRATION_ID=$(aws apigatewayv2 get-integrations --api-id $API_ID \
  --query 'Items[0].IntegrationId' --output text --region $REGION)
LIVE_ARN=$(aws lambda get-alias --function-name serverless-webapp --name live \
  --query 'AliasArn' --output text --region $REGION)
aws apigatewayv2 update-integration --api-id $API_ID \
  --integration-id $INTEGRATION_ID --integration-uri $LIVE_ARN --region $REGION

# 3. Grant API Gateway permission to invoke the alias
aws lambda add-permission --function-name serverless-webapp --qualifier live \
  --statement-id apigw-invoke-live --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*" --region $REGION
```

From now on, publish a new **version** for each release and use the alias to control traffic.

---

## 1. Rolling deployment (gradual)

Shift traffic to the new version in steps. The HTTP API keeps calling `live`; you change what
`live` resolves to.

```bash
REGION=us-east-1
# After update-function-code, publish the new snapshot:
NEW=$(aws lambda publish-version --function-name serverless-webapp \
  --query 'Version' --output text --region $REGION)

# 10% → new version
aws lambda update-alias --function-name serverless-webapp --name live \
  --function-version 1 --routing-config "{\"AdditionalVersionWeights\":{\"$NEW\":0.10}}" --region $REGION
# watch CloudWatch Errors/Duration (this project's Step 4 alarms still apply), then:
aws lambda update-alias --function-name serverless-webapp --name live \
  --function-version 1 --routing-config "{\"AdditionalVersionWeights\":{\"$NEW\":0.50}}" --region $REGION
# 100%
aws lambda update-alias --function-name serverless-webapp --name live \
  --function-version $NEW --routing-config '{}' --region $REGION
```

**Rollback:** `update-alias --name live --function-version 1 --routing-config '{}'`.

---

## 2. Canary deployment (hold + watch)

Same weighting, but **hold** at a low percentage and let this project's existing **CloudWatch
error / p95-duration alarms** be your go/no-go signal. Lambda emits metrics per version, so
you can compare the canary version against the current one in the dashboard you built in Step 4.

```bash
# hold 10% on the new version
aws lambda update-alias --function-name serverless-webapp --name live \
  --function-version 1 --routing-config "{\"AdditionalVersionWeights\":{\"$NEW\":0.10}}" --region $REGION
```

- **Promote:** `update-alias --name live --function-version $NEW --routing-config '{}'`
- **Abort:** `update-alias --name live --function-version 1 --routing-config '{}'`

If you'd rather do canary **at the gateway layer** (a percentage on a separate stage with its
own metrics), that's a REST-API-only feature — see
[api-gateway-rest-lambda](../api-gateway-rest-lambda/README.md). This project's HTTP API does
canary at the alias.

---

## 3. Blue-green deployment (instant flip)

Run both versions behind named aliases and repoint the integration to cut over atomically.

```bash
REGION=us-east-1; API_ID=<your-api-id>
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws lambda create-alias --function-name serverless-webapp --name blue  --function-version 1     --region $REGION
aws lambda create-alias --function-name serverless-webapp --name green --function-version $NEW  --region $REGION
for A in blue green; do
  aws lambda add-permission --function-name serverless-webapp --qualifier $A \
    --statement-id apigw-invoke-$A --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*" --region $REGION
done

INTEGRATION_ID=$(aws apigatewayv2 get-integrations --api-id $API_ID --query 'Items[0].IntegrationId' --output text --region $REGION)
GREEN_ARN=$(aws lambda get-alias --function-name serverless-webapp --name green --query 'AliasArn' --output text --region $REGION)

# flip to green:
aws apigatewayv2 update-integration --api-id $API_ID --integration-id $INTEGRATION_ID --integration-uri $GREEN_ARN --region $REGION
# rollback: repoint the integration back to the blue alias ARN
```

This app is **stateless** (no database), so the blue-green shared-state caveat from
[api-gateway-http-dynamodb-crud](../api-gateway-http-dynamodb-crud/steps/07-blue-green-deployment.md)
doesn't bite here — but keep it in mind if you add the DynamoDB challenge.

---

## Wiring it into the GitHub Actions pipeline (Step 7)

Today the workflow does:

```yaml
- run: aws lambda update-function-code --function-name serverless-webapp --zip-file fileb://function.zip
```

To make CI do a **canary**, add steps after the code update:

```yaml
- name: Publish new version
  run: echo "NEW=$(aws lambda publish-version --function-name serverless-webapp --query Version --output text)" >> $GITHUB_ENV
- name: Start 10% canary
  run: aws lambda update-alias --function-name serverless-webapp --name live --function-version $BASELINE --routing-config "{\"AdditionalVersionWeights\":{\"$NEW\":0.10}}"
# (optional) gate on a CloudWatch alarm here, then:
- name: Promote
  run: aws lambda update-alias --function-name serverless-webapp --name live --function-version $NEW --routing-config '{}'
```

For a fully managed version of this (automatic linear/canary with alarm-based rollback),
graduate to **AWS SAM**'s `DeploymentPreference` or **CodeDeploy** — but you now understand
exactly what they automate.

---

## Cleanup note

These add aliases and resource-based permissions to the function. When you run
[Step 8 — Cleanup](steps/08-cleanup.md), deleting the function removes its versions, aliases,
and permissions in one go — no extra teardown needed.
