# Step 2 — Launch a Test EC2 Instance

To see the scheduler work, you need something to switch on and off. You'll launch one tiny,
free-tier `t2.micro` and tag it `AutoPower=true` so the function will manage it. We deliberately
keep it minimal — no SSH key, no software, nothing to log into. It exists only to change state.

---

## 2.1 Launch the Instance (Console)

1. **EC2** → **Instances** → **Launch instances**.

| Field | Value |
|-------|-------|
| Name | `autopower-demo` |
| AMI | **Amazon Linux 2023** (free-tier eligible) |
| Instance type | **t2.micro** (free-tier eligible) |
| Key pair | **Proceed without a key pair** — we never log in |
| Network settings | Defaults are fine (default VPC) |
| Security group | Default; you can leave inbound empty (no access needed) |

2. **Add a tag** (this is the important part):

   | Key | Value |
   |-----|-------|
   | `AutoPower` | `true` |

   > **This tag is the opt-in switch.** The function only acts on instances with exactly
   > `AutoPower=true`. Anything without it is invisible to the scheduler.

3. **Launch instance**.

---

## 2.2 (Optional) Launch a Second, Untagged Instance

To *prove* the safety filter, launch a second `t2.micro` named `no-autopower` **without** the
tag. The scheduler should never touch it. (Skip if you'd rather not run two instances —
remember both bill if left up.)

---

## 2.3 Confirm It's Running

```bash
aws ec2 describe-instances \
  --filters "Name=tag:AutoPower,Values=true" \
  --query 'Reservations[].Instances[].{Id:InstanceId,State:State.Name,Type:InstanceType}' \
  --output table
```

Expected:

```
+---------------------+----------+-----------+
|         Id          |  State   |   Type    |
+---------------------+----------+-----------+
|  i-0abc123...       |  running |  t2.micro |
+---------------------+----------+-----------+
```

Wait until `State` is `running` before testing the function (a `pending` instance can't be
stopped yet).

---

## Checkpoint

- [ ] Instance `autopower-demo` is **running**
- [ ] It has the tag `AutoPower=true`
- [ ] The describe command lists it (and does **not** list any untagged instance)

> 💸 **Reminder:** this instance bills while running. You'll terminate it in Step 6. A
> `t2.micro` is free-tier, but only if you're within your 750 hours/month.

---

**Next:** [Step 3 — Create the Scheduler Function](./03-create-function.md)
