# Step 11 — Cleanup

Delete resources in **dependency order** (children before parents), or AWS will block you
with "resource in use" errors. The big costs — **NAT Gateway** and **ALB** — go first.

---

## 11.1 Deletion Order

| # | Resource | Where | Notes |
|---|----------|-------|-------|
| 1 | **Auto Scaling Group** `webapp-asg` | EC2 → Auto Scaling Groups | Delete → terminates all instances |
| 2 | **Launch template** `webapp-lt` | EC2 → Launch Templates | |
| 3 | **Load balancer** `webapp-alb` | EC2 → Load Balancers | Stops the ~$16/mo charge |
| 4 | **Target group** `webapp-tg` | EC2 → Target Groups | After the ALB is gone |
| 5 | **NAT Gateway** `webapp-nat` | VPC → NAT Gateways | ⚠️ Biggest cost; then release its Elastic IP |
| 6 | **Elastic IP** | VPC → Elastic IPs | **Release** it or it bills while unattached |
| 7 | **CloudWatch alarm + dashboard** | CloudWatch | `webapp-high-cpu`, `webapp-monitoring` |
| 8 | **SNS topic + subscription** | SNS | `webapp-alerts` |
| 9 | **CloudWatch log groups** | CloudWatch → Log groups | `/ec2/webapp/*` |
| 10 | **CloudTrail trail + S3 bucket** | CloudTrail / S3 | Empty the bucket first |
| 11 | **Internet Gateway** | VPC | Detach from VPC, then delete |
| 12 | **Subnets, route tables, VPC** | VPC | Delete the VPC last (removes subnets/RTs) |
| 13 | **IAM roles / OIDC provider** | IAM | `WebAppInstanceRole`, `GitHubActionsDeployRole` |
| 14 | **SSM parameter** | SSM → Parameter Store | `/webapp/cloudwatch-agent-config` |

> Deleting the **VPC** also removes its subnets, route tables, and security groups — but
> only **after** the NAT Gateway, ALB, and all instances inside it are gone.

---

## 11.2 CLI Teardown (fast path)

```bash
REGION=us-east-1

# 1. ASG (force-terminates instances)
aws autoscaling delete-auto-scaling-group --auto-scaling-group-name webapp-asg \
  --force-delete --region $REGION

# 2. Launch template
aws ec2 delete-launch-template --launch-template-name webapp-lt --region $REGION

# 3-4. ALB then target group
aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN --region $REGION
sleep 30
aws elbv2 delete-target-group --target-group-arn $TG_ARN --region $REGION

# 5-6. NAT Gateway then release EIP
aws ec2 delete-nat-gateway --nat-gateway-id $NAT_ID --region $REGION
aws ec2 wait nat-gateway-deleted --nat-gateway-ids $NAT_ID --region $REGION
aws ec2 release-address --allocation-id $EIP_ALLOC --region $REGION

# 7-8. CloudWatch + SNS
aws cloudwatch delete-alarms --alarm-names webapp-high-cpu --region $REGION
aws cloudwatch delete-dashboards --dashboard-names webapp-monitoring --region $REGION
aws sns delete-topic --topic-arn $TOPIC_ARN --region $REGION

# 10. CloudTrail + bucket
aws cloudtrail delete-trail --name webapp-audit-trail --region $REGION
aws s3 rb s3://$BUCKET --force

# 11-12. IGW, subnets, route tables, VPC
aws ec2 detach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID --region $REGION
aws ec2 delete-internet-gateway --internet-gateway-id $IGW_ID --region $REGION
# delete each subnet and non-main route table, then:
aws ec2 delete-vpc --vpc-id $VPC_ID --region $REGION

# 13-14. IAM + SSM
aws iam remove-role-from-instance-profile --instance-profile-name WebAppInstanceRole --role-name WebAppInstanceRole
aws iam delete-instance-profile --instance-profile-name WebAppInstanceRole
# detach managed policies, then: aws iam delete-role --role-name WebAppInstanceRole
aws ssm delete-parameter --name /webapp/cloudwatch-agent-config --region $REGION
```

---

## 11.3 Final Verification

- [ ] No running EC2 instances tagged `Project=webapp`
- [ ] No NAT Gateways and **no unattached Elastic IPs** (these bill silently!)
- [ ] No ALB or target group
- [ ] SNS topic and CloudWatch alarm/dashboard deleted
- [ ] CloudTrail trail deleted and its S3 bucket emptied + removed
- [ ] VPC `webapp-vpc` deleted
- [ ] **Billing → Cost Explorer** shows no ongoing EC2/ELB/NAT charges tomorrow

> Double-check **Elastic IPs** and **NAT Gateways** in the EC2/VPC consoles — a forgotten
> NAT Gateway is the #1 surprise bill from this project (~$32/month).

---

You've built and torn down a complete, monitored, auto-scaling web tier on native AWS. Now
run the **[serverless companion](../../serverless-monitored-webapp/README.md)** and compare.
