# Challenges — EC2 + VPC Monitored Web App

Extend the project. Each builds on the architecture you deployed.

---

## 1. HTTPS on the ALB
Request a free **ACM certificate**, add a **443 listener** to the ALB, and redirect 80→443.
Use a domain you own (or a `*.elb.amazonaws.com` won't accept a public cert — try this with
your own Route 53 domain). *Skills: ACM, ALB listeners, HTTP→HTTPS redirect rules.*

## 2. The "no NAT" budget variant
Re-deploy with instances in **public** subnets and **no NAT Gateway** (saves ~$32/mo).
Compare the security trade-off: what's now directly reachable, and how does `ec2-sg` still
protect you? *Skills: cost/security trade-offs, security group reasoning.*

## 3. Scale on requests, not CPU
Replace the CPU target-tracking policy with one tracking **`ALBRequestCountPerTarget`**.
Why is request count often a better scaling signal than CPU for a web app?
*Skills: target tracking, ALB metrics.*

## 4. Custom application metric
Have the app publish its **own** business metric to CloudWatch with `boto3`
(`put_metric_data`) — e.g. a counter of `/api/load` calls — then alarm on it.
*Skills: embedded metrics, custom namespaces, IAM (add `cloudwatch:PutMetricData` to the task role).*

## 5. Full deploy-role permission policy
Write the complete least-privilege IAM permission policy for `GitHubActionsDeployRole`
(the S3 + SSM actions from Step 10) as JSON, scoped to the specific bucket ARN and a
resource condition on the SSM document. *Skills: least-privilege policy authoring.*

## 6. Blue/green-ish deploy with instance refresh
Instead of in-place `systemctl restart`, trigger an **ASG instance refresh** so new code
ships via brand-new instances and old ones drain from the ALB. *Skills: ASG instance refresh,
launch template versions.*

## 7. Alarm to Slack, not just email
Add a second SNS subscription that calls a **Lambda** which posts the alarm to a Slack
webhook. Reuse the fanout idea from
[sqs-sns-iam-messaging](../sqs-sns-iam-messaging/README.md). *Skills: SNS fanout, Lambda, secrets.*

---

> Stuck? Every challenge is solvable with services already in this repo's other projects —
> IAM/OIDC, Lambda, SNS/SQS. Cross-reference and reuse.
