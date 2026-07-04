# Step 6 — Flip the Switch and Resize for Real

So far the function only *reports*. Now you'll let it **apply** a resize once, to watch the
stop → modify → start cycle and prove the tag-gated IAM works.

To get a genuine downsize recommendation, you need an instance that isn't already the smallest
type. If both your demo instances are `t3.micro`, launch a throwaway `t3.small` first.

---

## 6.1 Launch a Resizable Target (if needed)

1. **EC2** → **Launch instances** → name `rightsize-target`, type **`t3.small`**, tag
   `Rightsize=true`. Leave it idle.
2. Wait ~10–15 min so CloudWatch shows it as idle.

A dry-run now recommends shrinking it:

```json
{"instance_id": "i-0ccc...", "current_type": "t3.small",
 "finding": "idle", "recommended_type": "t3.micro", "applied": false}
```

---

## 6.2 Enable Applying

Set **two** environment variables on `compute-rightsizer`:

| Key | Value |
|-----|-------|
| `APPLY` | `true` |
| `DRY_RUN` | `false` |

> Both gates must open. `APPLY=true` alone still does nothing while `DRY_RUN=true`. This is
> deliberate friction — you can leave `APPLY=true` permanently and use `DRY_RUN` as the real
> on/off switch.

CLI reminder — pass **all** variables, since `--environment` replaces the whole set:

```bash
aws lambda update-function-configuration --function-name compute-rightsizer \
  --environment "Variables={TAG_KEY=Rightsize,TAG_VALUE=true,LOOKBACK_DAYS=1,IDLE_THRESHOLD=5,LOW_THRESHOLD=40,APPLY=true,DRY_RUN=false,SNS_TOPIC_ARN=<ARN>}"
```

---

## 6.3 Run It and Watch the Resize

```bash
python src/test_invoke.py
```

The response now shows `"applied": true` for the target. In the EC2 console you'll see the
instance go **stopping → stopped → pending → running**, and its **Instance type** column change
from `t3.small` to `t3.micro`. The function waited on the `instance_stopped` waiter between the
stop and the modify — you can't change type on a running instance.

Confirm:

```bash
aws ec2 describe-instances --instance-ids <TARGET_ID> \
  --query 'Reservations[].Instances[].InstanceType' --region us-east-1
```

---

## 6.4 Prove the Tag Gate

Pick an instance **not** tagged `Rightsize=true` (or remove the tag from one), and try to resize
it directly:

```bash
aws ec2 stop-instances --instance-ids <UNTAGGED_ID> --region us-east-1
# AccessDenied — the role's condition blocks it
```

The same `StopInstances` call that worked on a tagged instance is **denied** here. That's the
condition from Step 1.4 protecting everything you didn't opt in.

> **Turn it back off.** Set `DRY_RUN=true` again before leaving the lab so the weekly schedule
> goes back to *report-only*. Auto-applying resizes on a schedule is powerful and risky — most
> teams keep a human in the loop.

---

## Checkpoint

- [ ] With `APPLY=true` + `DRY_RUN=false`, one instance was resized (`"applied": true`)
- [ ] `describe-instances` confirms the new, smaller type
- [ ] A resize attempt on an **untagged** instance returns **AccessDenied**
- [ ] You set `DRY_RUN=true` again to leave the schedule in report-only mode

---

**Next:** [Step 7 — Cleanup](./07-cleanup.md)
