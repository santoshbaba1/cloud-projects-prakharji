# Step 4 — Launch EC2 with a User-Data Bootstrap

Instead of launching one hand-configured server, you'll create a **launch template** — a
reusable blueprint the Auto Scaling Group (Step 6) uses to stamp out identical instances.
The template's **user-data** script (`scripts/user-data.sh`) installs Python, the app, and
the CloudWatch agent automatically on first boot.

---

## 4.1 Why a Launch Template (not a plain instance)?

The ASG needs a template to know *what* to launch when it scales out or replaces a failed
instance. Everything that makes an instance "ours" — AMI, type, security group, instance
profile, and the bootstrap script — lives in one versioned object.

**What the user-data script does** (read `scripts/user-data.sh`):
1. Installs `python3`, `pip`, and the `amazon-cloudwatch-agent`
2. Writes the Flask app and `requirements.txt` to `/opt/webapp`
3. Installs dependencies and runs the app via **gunicorn** as a **systemd** service on
   port 5000 (so it restarts on crash and survives reboots)
4. Starts the CloudWatch agent if its config is present

---

## 4.2 Console — Create the Launch Template

1. **EC2 console → Launch Templates → Create launch template**.

   | Field | Value |
   |-------|-------|
   | Name | `webapp-lt` |
   | AMI | **Amazon Linux 2023** (x86_64) |
   | Instance type | `t3.micro` |
   | Key pair | **Proceed without a key pair** (we use SSM, not SSH) |
   | Subnet | Don't include in template (the ASG picks subnets) |
   | Security group | `ec2-sg` |

2. **Advanced details:**
   - **IAM instance profile:** `WebAppInstanceRole`
   - **User data:** paste the entire contents of `scripts/user-data.sh`

3. Also under Advanced details, add a **Resource tag**: `Project = webapp` (the Step 10
   deploy pipeline targets instances by this tag).

4. **Create launch template**.

---

## 4.3 Quick Smoke Test (one throwaway instance)

Before building the ASG, launch a single instance straight from the template to confirm
the bootstrap works:

1. **Launch templates →** select `webapp-lt` **→ Actions → Launch instance from template**.
2. Set **Subnet** to `webapp-public-a` *for this test only* and enable auto-assign public
   IP, so you can curl it directly. (Real instances go in private subnets via the ASG.)
3. Launch, wait ~3 minutes for user-data to finish.
4. Connect with **SSM** (no SSH): select the instance → **Connect → Session Manager → Connect**.
5. In the session:

   ```bash
   systemctl status webapp.service       # should be active (running)
   curl -s localhost:5000/health         # {"status":"healthy",...}
   sudo tail -n 20 /var/log/user-data.log
   ```

6. **Terminate this test instance** when satisfied — the ASG creates the real ones.

---

## 4.4 AWS CLI (Alternative — Create the Template)

```bash
REGION=us-east-1
AMI_ID=$(aws ssm get-parameter --region $REGION \
  --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query 'Parameter.Value' --output text)

aws ec2 create-launch-template \
  --launch-template-name webapp-lt \
  --region $REGION \
  --launch-template-data "{
    \"ImageId\": \"$AMI_ID\",
    \"InstanceType\": \"t3.micro\",
    \"IamInstanceProfile\": {\"Name\": \"WebAppInstanceRole\"},
    \"SecurityGroupIds\": [\"$EC2_SG\"],
    \"TagSpecifications\": [{\"ResourceType\": \"instance\",
      \"Tags\": [{\"Key\": \"Project\", \"Value\": \"webapp\"}]}],
    \"UserData\": \"$(base64 -w0 scripts/user-data.sh)\"
  }"
```

> `UserData` must be **base64-encoded** when passed via the CLI. The Console encodes it for you.

---

## Checkpoint

- [ ] Launch template `webapp-lt` exists (AL2023, t3.micro, `ec2-sg`, `WebAppInstanceRole`)
- [ ] User-data from `scripts/user-data.sh` is attached
- [ ] Instances are tagged `Project=webapp`
- [ ] Smoke-test instance returned `{"status":"healthy"}` on `/health`
- [ ] Smoke-test instance terminated

---

**Next:** [Step 5 — Application Load Balancer](./05-application-load-balancer.md)
