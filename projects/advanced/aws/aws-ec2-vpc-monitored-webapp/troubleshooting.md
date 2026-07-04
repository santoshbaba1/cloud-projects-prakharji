# Troubleshooting — EC2 + VPC Monitored Web App

Format: **Symptom → Cause → Fix**.

---

## Networking & Instances

### Targets stuck "unhealthy" in the target group
- **Cause:** App not listening, wrong health-check path/port, or `ec2-sg` doesn't allow 5000 from `alb-sg`.
- **Fix:** SSM into the instance → `systemctl status webapp.service` and `curl localhost:5000/health`. Confirm the target group health check is **HTTP /health on port 5000** and that `ec2-sg` inbound allows TCP 5000 **from `alb-sg`** (Step 2).

### `curl http://<ALB-DNS>` times out
- **Cause:** `alb-sg` doesn't allow 80 from your IP, or the ALB isn't in public subnets, or targets are unhealthy.
- **Fix:** Verify `alb-sg` inbound 80 from `0.0.0.0/0`, the ALB is **internet-facing** in both public subnets, and at least one target is healthy.

### Instance has no internet (user-data fails to install packages)
- **Cause:** Private subnet's route table doesn't point `0.0.0.0/0` at the NAT Gateway, or NAT isn't **Available** yet.
- **Fix:** Confirm `webapp-rt-private` has `0.0.0.0/0 → webapp-nat` and is associated with both private subnets. Wait until the NAT Gateway shows **Available**.

### "Can't connect" — there's no key pair / no SSH
- **Cause:** This project intentionally omits SSH (port 22) and key pairs.
- **Fix:** Use **SSM Session Manager** (EC2 → Connect → Session Manager). It needs `AmazonSSMManagedInstanceCore` on the instance role (Step 3) and the instance to have outbound internet via NAT.

### user-data didn't run / app not installed
- **Cause:** user-data only runs on **first boot**; editing it later won't re-run it. Or a script error.
- **Fix:** `sudo cat /var/log/user-data.log` (and `/var/log/cloud-init-output.log`) on the instance. To re-test, launch a fresh instance from the template.

---

## Monitoring

### `MemoryUtilization` metric never appears
- **Cause:** CloudWatch agent not running or config not delivered.
- **Fix:** Confirm the SSM `AmazonCloudWatch-ManageAgent` command succeeded (Step 7), the instance role has `CloudWatchAgentServerPolicy`, and check `amazon-cloudwatch-agent-ctl -a status` via SSM.

### Alarm stuck in "Insufficient data"
- **Cause:** No datapoints yet (instances just launched) or wrong dimension.
- **Fix:** Wait one full period. Confirm the alarm's dimension is `AutoScalingGroupName=webapp-asg`. `TreatMissingData=notBreaching` keeps it out of false alarm.

### Alarm fires but no email
- **Cause:** SNS subscription still **Pending** — you didn't click the confirmation link.
- **Fix:** SNS → Subscriptions → status must be **Confirmed**. Re-request and confirm if needed. Check spam.

### `/api/load` doesn't raise CPU enough to trip the alarm
- **Cause:** gunicorn has 2 workers but you sent one request; one core barely moves the average.
- **Fix:** Fire many in parallel: `for i in $(seq 1 20); do curl -s "$ALB/api/load?seconds=8" & done; wait`. t3 instances also have CPU credits — sustained load is what trips it.

---

## CloudTrail

### No logs in the S3 bucket
- **Cause:** Delivery lag (up to 15 min), or the bucket policy doesn't allow CloudTrail to write.
- **Fix:** Wait 15 minutes. If you created the bucket by hand (CLI), attach the CloudTrail service bucket policy (`cloudtrail.amazonaws.com` `s3:PutObject` with the `bucket-owner-full-control` ACL condition). Letting the Console create the bucket avoids this.

---

## GitHub Actions Deploy

### `Error: Could not assume role with OIDC`
- **Cause:** Trust policy `sub` doesn't match the repo/branch, or the OIDC provider is missing.
- **Fix:** The `sub` condition must match `repo:ORG/REPO:ref:refs/heads/main` exactly. Confirm the `token.actions.githubusercontent.com` identity provider exists with audience `sts.amazonaws.com`.

### `SendCommand` fails with "Instances not in a valid state"
- **Cause:** The instances aren't registered with SSM (no role, or no outbound internet).
- **Fix:** Instance role needs `AmazonSSMManagedInstanceCore`; the instance needs NAT outbound. Check **Systems Manager → Fleet Manager** — instances should be listed as **Managed**.

### Deploy succeeds but the app still shows the old version
- **Cause:** `systemctl restart` ran but gunicorn cached the old code, or sync path is wrong.
- **Fix:** Confirm the SSM command synced to `/opt/webapp/` and restarted `webapp.service`. SSM → Run Command → command history shows per-instance stdout/stderr.
