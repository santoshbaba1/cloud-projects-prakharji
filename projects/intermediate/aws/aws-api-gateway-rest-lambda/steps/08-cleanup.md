# Step 8 — Cleanup

None of these resources cost much at rest (you pay per request), but tidy accounts are good
hygiene — and leftover aliases/permissions cause confusing errors if you rebuild later. Delete
in this order.

---

## 8.1 Delete the REST API

This removes all stages (`prod`, `staging`), deployments, resources, and methods at once.

```bash
REGION=us-east-1
API_ID=<your-api-id>
aws apigateway delete-rest-api --rest-api-id $API_ID --region $REGION
```

Console: **API Gateway → APIs → quotes-rest-api → Actions → Delete**.

---

## 8.2 Delete the Lambda Function

Deleting the function removes its versions and aliases (`live`, `canary`, `blue`, `green`) and
the resource-based permissions in one go.

```bash
aws lambda delete-function --function-name quotes-api --region $REGION
```

Console: **Lambda → quotes-api → Actions → Delete**.

---

## 8.3 Delete the CloudWatch Log Group

```bash
aws logs delete-log-group --log-group-name /aws/lambda/quotes-api --region $REGION
```

Console: **CloudWatch → Log groups → `/aws/lambda/quotes-api` → Delete**.

---

## 8.4 Delete the IAM Role

```bash
aws iam detach-role-policy --role-name QuotesApiExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name QuotesApiExecutionRole
```

Console: **IAM → Roles → QuotesApiExecutionRole → Delete**.

---

## 8.5 Local Files

```bash
rm -f src/function.zip src/out.json lambda-trust.json
```

---

## Checkpoint

- [ ] REST API deleted (all stages gone)
- [ ] Lambda function deleted (versions + aliases + permissions gone)
- [ ] Log group deleted
- [ ] IAM role deleted
- [ ] Local artifacts removed

---

🎉 **Done.** You built a REST API and shipped it three ways — rolling, canary, and
blue-green — using nothing but API Gateway and Lambda primitives. Now build the twin:
[api-gateway-http-dynamodb-crud](../../aws-api-gateway-dynamodb-crud/README.md), where the
API is an HTTP API with real DynamoDB state and every deployment happens at the Lambda-alias
level.
