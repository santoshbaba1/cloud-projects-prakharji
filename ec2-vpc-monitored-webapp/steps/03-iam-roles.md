# Step 3 — IAM: The Instance Profile

EC2 instances need permissions to do their job: let SSM manage them (deploys + shell),
and let the CloudWatch agent push metrics and logs. We grant these through an **instance
profile** — an IAM role that EC2 assumes on the instance's behalf, so no credentials are
ever stored on the box.

---

## 3.1 What You're Creating

**Role name:** `WebAppInstanceRole`
**Trust policy:** allows `ec2.amazonaws.com` to assume it.
**Attached managed policies:**

| Permission set | Managed policy | Why It's Needed |
|----------------|----------------|-----------------|
| SSM management | `AmazonSSMManagedInstanceCore` | SSM Run Command deploys (Step 10) + no-SSH shell |
| CloudWatch agent | `CloudWatchAgentServerPolicy` | Push memory/disk metrics and ship logs (Step 7) |

Why these two and nothing more? Least privilege. The instance never needs to read S3 or
launch other instances, so we don't grant it those. (The deploy in Step 10 adds a narrow
S3 read for the artifact bucket — we'll attach that inline policy then.)

> An **instance profile** is just a container that lets EC2 hand the role to the OS. When
> you create the role for EC2 in the Console, AWS creates the matching instance profile
> automatically. With the CLI you create it explicitly (shown below).

---

## 3.2 Console — Create the Role

1. **IAM console → Roles → Create role**.
2. **Trusted entity type:** AWS service → **EC2** → Next.
3. Attach policies — search and check:
   - `AmazonSSMManagedInstanceCore`
   - `CloudWatchAgentServerPolicy`
4. Next → **Role name:** `WebAppInstanceRole` → **Create role**.

That's it — the instance profile `WebAppInstanceRole` is created automatically and is
selectable in the launch template in Step 4.

---

## 3.3 AWS CLI (Alternative)

```bash
REGION=us-east-1

cat > ec2-trust.json <<'JSON'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ec2.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
JSON

aws iam create-role --role-name WebAppInstanceRole \
  --assume-role-policy-document file://ec2-trust.json

aws iam attach-role-policy --role-name WebAppInstanceRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
aws iam attach-role-policy --role-name WebAppInstanceRole \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy

# Instance profile (Console does this for you; CLI is explicit)
aws iam create-instance-profile --instance-profile-name WebAppInstanceRole
aws iam add-role-to-instance-profile \
  --instance-profile-name WebAppInstanceRole --role-name WebAppInstanceRole
```

---

## Checkpoint

- [ ] Role `WebAppInstanceRole` trusts `ec2.amazonaws.com`
- [ ] `AmazonSSMManagedInstanceCore` attached
- [ ] `CloudWatchAgentServerPolicy` attached
- [ ] An instance profile named `WebAppInstanceRole` exists

---

**Next:** [Step 4 — Launch EC2 with User Data](./04-launch-ec2.md)
