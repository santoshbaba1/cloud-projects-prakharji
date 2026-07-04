# Step 6 — Cleanup

The most important cleanup in this series: **terminate the EC2 instance(s)**. A stopped
instance still bills for its EBS volume, and a forgotten *running* one bills for compute.

---

## 6.1 Terminate the EC2 Instances

**Console:** EC2 → Instances → select `autopower-demo` (and `no-autopower` if you made it) →
**Instance state** → **Terminate (delete) instance**.

**CLI:**

```bash
# Grab the IDs (tagged demo instance)
IDS=$(aws ec2 describe-instances \
  --filters "Name=tag:AutoPower,Values=true" "Name=instance-state-name,Values=running,stopped" \
  --query 'Reservations[].Instances[].InstanceId' --output text)
echo "Terminating: $IDS"
aws ec2 terminate-instances --instance-ids $IDS

# If you launched the untagged one too:
aws ec2 terminate-instances --instance-ids $(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=no-autopower" "Name=instance-state-name,Values=running,stopped" \
  --query 'Reservations[].Instances[].InstanceId' --output text)
```

> **Terminate, not stop.** Stopping leaves the EBS volume billing. Termination deletes the
> default root volume and ends all charges.

Wait until state is `terminated` (or `shutting-down`) before moving on.

---

## 6.2 Delete the Two Schedules

```bash
for r in ec2-stop-schedule ec2-start-schedule; do
  aws events remove-targets --rule "$r" --ids "1"
  aws events delete-rule --name "$r"
done
```

(Console: disable, then delete each rule.)

---

## 6.3 Delete the Lambda Function

```bash
aws lambda delete-function --function-name ec2-scheduler
```

---

## 6.4 Delete the Log Group

```bash
aws logs delete-log-group --log-group-name /aws/lambda/ec2-scheduler
```

---

## 6.5 Delete the IAM Role

```bash
aws iam delete-role-policy \
  --role-name Ec2SchedulerExecutionRole --policy-name Ec2StartStopTagged

aws iam detach-role-policy \
  --role-name Ec2SchedulerExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam delete-role --role-name Ec2SchedulerExecutionRole
```

---

## Cleanup Checklist

- [ ] **All EC2 instances terminated** (verify in the console — this is the one that costs money)
- [ ] Rules `ec2-stop-schedule` and `ec2-start-schedule` deleted
- [ ] Function `ec2-scheduler` deleted
- [ ] Log group deleted
- [ ] Role `Ec2SchedulerExecutionRole` deleted

> Double-check **EC2 → Instances** shows nothing but `terminated`. A single instance you forgot
> is the most common surprise charge in this whole repo.

---

**Next project →** [Scheduled S3 Housekeeping](../../aws-lambda-s3-housekeeping/README.md).
