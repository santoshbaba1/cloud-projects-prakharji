# Step 9 — CloudTrail: The Account Audit Trail

CloudWatch tells you how the app is *performing*. **CloudTrail** tells you *who did what* in
your AWS account — every API call, from every user, role, and service, with the source IP
and timestamp. It's the backbone of security forensics and compliance.

---

## 9.1 What You're Creating

A **multi-Region trail** named `webapp-audit-trail` that logs **management events** (control
-plane actions like `RunInstances`, `CreateLoadBalancer`, `PutMetricAlarm`) to a dedicated
**S3 bucket**. One management-events trail is **free**.

> CloudTrail already keeps the last 90 days of management events in **Event history** for
> free — but that's not a trail you control, can't query long-term, and isn't delivered to
> S3. Creating your own trail gives you durable, queryable audit logs.

---

## 9.2 Console — Create the Trail

1. **CloudTrail console → Trails → Create trail**.

   | Field | Value |
   |-------|-------|
   | Trail name | `webapp-audit-trail` |
   | Storage location | **Create new S3 bucket** |
   | Bucket name | `webapp-audit-trail-<your-unique-suffix>` |
   | Log file SSE-KMS encryption | Optional (leave off for the workshop) |
   | Log file validation | **Enabled** (detects tampering) |

2. **Event types:** check **Management events**; keep **Read** and **Write** both on.
   Leave Data events and Insights off (they cost extra).
3. **Next → Create trail.** Logging begins immediately; events appear in S3 within ~5–15 min.

---

## 9.3 Read the Audit Trail

**Fastest — Event history (no setup):**
1. **CloudTrail → Event history**.
2. Filter **Event name = `RunInstances`** → you'll see the ASG launching your instances,
   including which role made the call and from what IP.
3. Try **Event name = `PutMetricAlarm`** to see the alarm you created in Step 7.

**From the S3 bucket:** logs land under
`AWSLogs/<account-id>/CloudTrail/us-east-1/YYYY/MM/DD/` as gzipped JSON. Each record has
`eventName`, `userIdentity`, `sourceIPAddress`, and `requestParameters`.

---

## 9.4 Why This Matters

When something unexpected happens — an instance you didn't launch, a security group rule
that changed — CloudTrail answers "who, when, and from where". Pair it with the
[iam-roles-and-policies](../../../../intermediate/aws/aws-iam-roles-and-policies/README.md) project: every `AssumeRole`
and federated GitHub OIDC login shows up here, so you can trace a deploy all the way back
to a specific GitHub Actions run.

---

## 9.5 AWS CLI (Alternative)

```bash
REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET=webapp-audit-trail-$ACCOUNT_ID

aws s3api create-bucket --bucket $BUCKET --region $REGION
# (Attach the CloudTrail bucket policy — the Console does this automatically;
#  see troubleshooting.md if you create the bucket by hand.)

aws cloudtrail create-trail --name webapp-audit-trail \
  --s3-bucket-name $BUCKET --is-multi-region-trail --enable-log-file-validation --region $REGION
aws cloudtrail start-logging --name webapp-audit-trail --region $REGION
```

---

## Checkpoint

- [ ] Trail `webapp-audit-trail` exists and is **logging**
- [ ] Logs are delivered to the S3 bucket (folders appear within ~15 min)
- [ ] Log file validation is enabled
- [ ] You found the `RunInstances` and `PutMetricAlarm` events in Event history

---

**Next:** [Step 10 — GitHub Actions Deploy](./10-github-actions-deploy.md)
