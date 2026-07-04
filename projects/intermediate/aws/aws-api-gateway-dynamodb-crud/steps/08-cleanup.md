# Step 8 — Cleanup

On-demand DynamoDB and pay-per-request API Gateway/Lambda don't bill at rest, so an
untouched project costs ~$0 — but clean up anyway for hygiene and to avoid stale aliases
confusing a rebuild. Delete in this order.

---

## 8.1 Delete the HTTP API

```bash
REGION=us-east-1
API_ID=<your-api-id>
aws apigatewayv2 delete-api --api-id $API_ID --region $REGION
```

Console: **API Gateway → APIs → tasks-http-api → Delete**.

---

## 8.2 Delete the Lambda Function

Removes its versions, aliases (`live`, `blue`, `green`), and resource permissions.

```bash
aws lambda delete-function --function-name tasks-api --region $REGION
```

---

## 8.3 Delete the DynamoDB Table

```bash
aws dynamodb delete-table --table-name tasks --region $REGION
```

Console: **DynamoDB → Tables → tasks → Delete** (type the table name to confirm).

---

## 8.4 Delete the CloudWatch Log Group

```bash
aws logs delete-log-group --log-group-name /aws/lambda/tasks-api --region $REGION
```

---

## 8.5 Delete the IAM Role

```bash
aws iam delete-role-policy --role-name TasksApiExecutionRole --policy-name TasksTableAccess
aws iam detach-role-policy --role-name TasksApiExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name TasksApiExecutionRole
```

---

## 8.6 Local Files

```bash
rm -f src/function.zip src/out.json green-out.json lambda-trust.json tasks-policy.json
```

---

## Checkpoint

- [ ] HTTP API deleted
- [ ] Lambda function deleted (versions + aliases gone)
- [ ] DynamoDB table `tasks` deleted
- [ ] Log group deleted
- [ ] IAM role + inline policy deleted
- [ ] Local artifacts removed

---

🎉 **Done.** You built a real CRUD API on an HTTP API + DynamoDB and shipped it three ways —
all at the Lambda-alias level. Put it beside [Project 1](../../aws-api-gateway-rest-lambda/README.md):
same strategies, REST's gateway canary vs HTTP's alias-only approach. That contrast is the
whole point of building the pair.
