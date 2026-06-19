# Step 7 — Cleanup

Leftover **EC2 instances are the only thing here that bills by the hour** — terminate them first.

---

## 7.1 Terminate the Demo Instances

1. **EC2** → **Instances** → select `rightsize-idle`, `rightsize-busy`, and `rightsize-target`.
2. **Instance state** → **Terminate (delete) instance** → confirm.

```bash
aws ec2 terminate-instances --instance-ids <ID_A> <ID_B> <ID_C> --region us-east-1
```

Terminating also stops their CloudWatch metric charges (there are none at this scale anyway).

## 7.2 Delete the Schedule

```bash
aws events remove-targets --rule rightsizing-schedule --ids 1
aws events delete-rule --name rightsizing-schedule
```

## 7.3 Delete the Function

```bash
aws lambda delete-function --function-name compute-rightsizer
```

## 7.4 Delete the SNS Topic

```bash
aws sns delete-topic --topic-arn <TOPIC_ARN>
```

## 7.5 Delete the Role

```bash
aws iam delete-role-policy --role-name ComputeRightsizerExecutionRole --policy-name ComputeRightsizerPolicy
aws iam detach-role-policy --role-name ComputeRightsizerExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name ComputeRightsizerExecutionRole
```

## 7.6 (Optional) Opt Out of Compute Optimizer

It's free to leave on, but if you want a clean slate:

```bash
aws compute-optimizer update-enrollment-status --status Inactive --region us-east-1
```

---

## Checkpoint

- [ ] All three demo instances show **terminated**
- [ ] EventBridge rule, Lambda, SNS topic, and IAM role deleted
- [ ] `describe-instances` shows nothing left running
- [ ] (Optional) Compute Optimizer set back to Inactive

You've finished the **optimization** project. Next up is **recovery** →
[RDS Disaster Recovery](../rds-disaster-recovery/README.md).
