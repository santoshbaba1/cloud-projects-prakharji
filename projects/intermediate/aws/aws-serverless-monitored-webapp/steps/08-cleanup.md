# Step 8 — Cleanup

Serverless cleanup is short — there's no network or fleet to unwind. Idle resources here
cost ~$0, but tidy up so nothing counts against free-tier limits (dashboards beyond 3) or
lingers in your account.

---

## 8.1 Deletion Order

| # | Resource | Where | Notes |
|---|----------|-------|-------|
| 1 | **API Gateway** `serverless-webapp-api` | API Gateway console | Delete the API (removes routes + stage) |
| 2 | **Lambda function** `serverless-webapp` | Lambda console | |
| 3 | **CloudWatch alarms** | CloudWatch → Alarms | `serverless-webapp-errors`, `serverless-webapp-slow` |
| 4 | **CloudWatch dashboard** | CloudWatch → Dashboards | `serverless-webapp-monitoring` (counts toward free 3) |
| 5 | **Lambda log group** | CloudWatch → Log groups | `/aws/lambda/serverless-webapp` |
| 6 | **SNS topic** | SNS | `serverless-webapp-alerts` |
| 7 | **CloudTrail trail + S3 bucket** | CloudTrail / S3 | Only if you created one just for this project; empty the bucket first |
| 8 | **IAM roles** | IAM | `LambdaWebAppExecutionRole`, `GitHubLambdaDeployRole` |

> Keep the **GitHub OIDC provider** and any shared CloudTrail if the EC2 project still uses
> them. They're free and account-wide.

---

## 8.2 CLI Teardown

```bash
REGION=us-east-1

aws apigatewayv2 delete-api --api-id $API_ID --region $REGION
aws lambda delete-function --function-name serverless-webapp --region $REGION
aws cloudwatch delete-alarms --alarm-names serverless-webapp-errors serverless-webapp-slow --region $REGION
aws cloudwatch delete-dashboards --dashboard-names serverless-webapp-monitoring --region $REGION
aws logs delete-log-group --log-group-name /aws/lambda/serverless-webapp --region $REGION
aws sns delete-topic --topic-arn $TOPIC_ARN --region $REGION

# IAM (detach/delete inline policy first if present)
aws iam detach-role-policy --role-name LambdaWebAppExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name LambdaWebAppExecutionRole
```

---

## 8.3 Final Verification

- [ ] API Gateway API deleted (its invoke URL now 404s)
- [ ] Lambda function deleted
- [ ] Both alarms and the dashboard deleted
- [ ] SNS topic deleted
- [ ] Lambda log group deleted
- [ ] CloudTrail trail/bucket deleted *if it was project-specific*
- [ ] Roles deleted (kept the shared OIDC provider if EC2 project needs it)

---

You've now built the **same application twice** — once on native AWS (EC2/VPC/ALB) and once
serverless (API Gateway/Lambda) — with identical monitoring, alerting, audit, and CI/CD.
Re-read the comparison table in the [README](../README.md#native-vs-serverless--side-by-side)
now that you've felt both: the ops burden, the cost-at-idle, and the metrics each exposes.
