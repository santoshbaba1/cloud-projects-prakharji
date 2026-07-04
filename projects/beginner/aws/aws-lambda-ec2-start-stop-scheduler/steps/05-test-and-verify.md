# Step 5 — Test and Verify

Confirm three things: the schedules fire, the instance changes state, and the **untagged**
instance is never touched. Then look at where the savings actually come from.

---

## 5.1 Watch State Changes

```bash
# Re-run this every ~30s around your schedule time
aws ec2 describe-instances \
  --filters "Name=tag:AutoPower,Values=true" \
  --query 'Reservations[].Instances[].{Id:InstanceId,State:State.Name}' \
  --output table
```

You should see `running → stopping → stopped` after the stop schedule, and the reverse after
the start schedule.

---

## 5.2 Read the Function Logs

```bash
aws logs tail /aws/lambda/ec2-scheduler --since 30m
```

Healthy stop run:

```
stop 1 instance(s): ['i-0abc123...']
```

When there's nothing to do (e.g. stop runs but everything's already stopped):

```
No running instances tagged AutoPower=true — nothing to stop
```

That "nothing to do" path is normal and safe — it's the idempotency from Step 3 at work.

---

## 5.3 Prove the Safety Filter

If you launched the untagged `no-autopower` instance in Step 2.2, confirm it stayed running
through a stop cycle:

```bash
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=no-autopower" \
  --query 'Reservations[].Instances[].State.Name' --output text
```

It should still read `running`. Both the **code filter** and the **IAM condition** kept it safe.

---

## 5.4 Where the Savings Come From

| Instance state | EC2 compute charge | EBS volume charge |
|----------------|--------------------|-------------------|
| `running` | **Yes** (per second) | Yes |
| `stopped` | **No** | **Yes** (small) |
| `terminated` | No | No (volume deleted) |

> **Key insight:** stopping kills the *compute* bill (the big number) but the root **EBS
> volume keeps billing** (a few cents/GB-month) because your data is preserved. Powering a dev
> box off 12h/day cuts its compute cost ~50%. To pay *nothing*, you must **terminate** — which
> you'll do in cleanup.

Rough math for one `m5.large` (~$0.096/hr) left off 12h every weekday:
~$0.096 × 12 × ~21 days ≈ **$24/month saved** per instance, for one small Lambda.

---

## 5.5 Check the Rule Health

EventBridge → each rule → **Monitoring**: `Invocations` climbing, `FailedInvocations = 0`. A
non-zero `FailedInvocations` with no Lambda logs means a missing invoke permission (see
[troubleshooting.md](../troubleshooting.md)).

---

## Checkpoint

- [ ] Stop schedule moved the tagged instance to `stopped`
- [ ] Start schedule moved it back to `running`
- [ ] The untagged instance was never affected
- [ ] Logs show clean runs (including harmless "nothing to" messages)

---

**Next:** [Step 6 — Cleanup](./06-cleanup.md)
