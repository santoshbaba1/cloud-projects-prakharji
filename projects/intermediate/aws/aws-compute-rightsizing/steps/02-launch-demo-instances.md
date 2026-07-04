# Step 2 — Launch the Demo Instances

To see the rightsizer make different recommendations, you'll run **two** instances tagged
`Rightsize=true`:

- **Instance A** — launched and left alone → stays **idle** (max CPU ≈ 0%) → flagged `idle`.
- **Instance B** — you'll run a CPU-burn loop on it → looks **busy** → flagged `right-sized`.

Both are `t3.micro` (Free-Tier-eligible). In a real account these would be larger instances you
suspect are over-provisioned — the logic is identical.

> Launch them **early** and move on to Step 3. CloudWatch needs a little time (≈10–15 min) to
> accumulate `CPUUtilization` datapoints before the rightsizer has anything to read.

---

## 2.1 Launch Instance A (the idle one)

1. **EC2** → **Instances** → **Launch instances**.

   | Field | Value |
   |-------|-------|
   | Name | `rightsize-idle` |
   | AMI | **Amazon Linux 2023** (default) |
   | Instance type | `t3.micro` |
   | Key pair | *Proceed without a key pair* (we use SSM/console, no SSH needed) |
   | Network | Default VPC, **Auto-assign public IP: Enable** |

2. **Advanced details** → scroll to **Add tags** isn't here; instead expand **Add tags** in the
   *Summary* panel or after launch. Add tag:

   | Key | Value |
   |-----|-------|
   | `Rightsize` | `true` |

3. **Launch instance.**

## 2.2 Launch Instance B (the busy one)

Repeat 2.1 with:

| Field | Value |
|-------|-------|
| Name | `rightsize-busy` |
| Tag | `Rightsize=true` |
| IAM instance profile | attach a role with `AmazonSSMManagedInstanceCore` if you want SSM Session Manager access (optional but easiest way to log in) |

---

## 2.3 Generate Load on Instance B

You need *some* CPU on Instance B so it isn't also flagged idle. Easiest path is **SSM Session
Manager** (no SSH key, no open ports):

1. **EC2** → select `rightsize-busy` → **Connect** → **Session Manager** → **Connect**.
   (If the tab is greyed out, attach the `AmazonSSMManagedInstanceCore` managed policy to the
   instance's role and wait a minute.)
2. In the shell, run a burn loop for ~10 minutes:

   ```bash
   timeout 600 bash -c 'while true; do :; done' &
   timeout 600 bash -c 'while true; do :; done' &
   ```

   Two loops peg both vCPUs of a `t3.micro`. (Or copy `src/busy_loop.py` over and run
   `python3 busy_loop.py 600`.)

> No SSM access? Skip the load — Instance B will simply also show as `idle`. The recommendations
> are still valid; you just won't get the `right-sized` contrast. You can also use the
> **CPU credit balance** burst behavior by running `stress` if installed.

---

## 2.4 Confirm CPU Is Showing Up

After ~10–15 minutes, check the metric exists:

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=<INSTANCE_B_ID> \
  --start-time "$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --period 300 --statistics Maximum --region us-east-1
```

You should see `Maximum` values well above 40% for the busy instance and near 0 for the idle one.

---

## Checkpoint

- [ ] Two `t3.micro` instances running, both tagged `Rightsize=true`
- [ ] `rightsize-busy` has had a CPU-burn loop (or you accepted both showing idle)
- [ ] `get-metric-statistics` returns `CPUUtilization` datapoints for at least one instance
- [ ] You noted both **Instance IDs**

---

**Next:** [Step 3 — Create the Rightsizer Function](./03-create-function.md)
