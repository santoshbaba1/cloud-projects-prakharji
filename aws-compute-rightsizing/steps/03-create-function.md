# Step 3 — Create the Rightsizer Function

Deploy `compute_rightsizer.py` and run it in **DRY_RUN** mode — it reads CPU and reports
recommendations but changes nothing.

---

## 3.1 Review the Handler

Open `src/compute_rightsizer.py`. The key ideas:

```python
resp = cw.get_metric_statistics(
    Namespace="AWS/EC2", MetricName="CPUUtilization",
    Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
    StartTime=start, EndTime=end, Period=3600,
    Statistics=["Average", "Maximum"],
)
```

- We ask CloudWatch for hourly `Average` **and** `Maximum`. We classify on **max** so a workload
  that's quiet on average but spikes hard isn't wrongly shrunk.

```python
if max_cpu < IDLE_THRESHOLD:      # default 5%
    return ("idle", _down(current_type))
if max_cpu < LOW_THRESHOLD:       # default 40%
    return ("over-provisioned", _down(current_type))
return ("right-sized", None)
```

- Three buckets. Note `idle` still suggests a smaller type, but the **real** advice for idle is
  "stop it" — the report says `idle` so you know the difference.

```python
if not points:
    return (float("nan"), float("nan"))   # no data => "no-data", never "idle"
```

- A brand-new instance has no metrics yet. We refuse to call that "idle" — guessing idle on an
  instance with no data would be how you accidentally shrink something important.

```python
if APPLY and not DRY_RUN and recommended and recommended != current_type:
    _resize(instance_id, recommended)
```

- **Two** gates protect the resize: `APPLY` must be true *and* `DRY_RUN` false. Reporting is the
  default; changing compute is opt-in twice.

---

## 3.2 Package and Deploy

```bash
cd /path/to/aws-compute-rightsizing
zip -j compute_rightsizer.zip src/compute_rightsizer.py
```

Console:

1. **Lambda** → **Create function** → **Author from scratch**.

   | Field | Value |
   |-------|-------|
   | Function name | `compute-rightsizer` |
   | Runtime | **Python 3.14** |
   | Execution role | **Use an existing role** → `ComputeRightsizerExecutionRole` |

2. **Create function** → upload `compute_rightsizer.zip` → **Save**.
3. **Configuration → General configuration → Edit:**

   | Setting | Value | Why |
   |---------|-------|-----|
   | Handler | `compute_rightsizer.handler` | filename.function |
   | Memory | 128 MB | a few API calls, light |
   | Timeout | 120 sec | a live resize waits for the instance to stop |

4. **Configuration → Environment variables → Edit**, add:

   | Key | Value |
   |-----|-------|
   | `TAG_KEY` | `Rightsize` |
   | `TAG_VALUE` | `true` |
   | `LOOKBACK_DAYS` | `1` |
   | `IDLE_THRESHOLD` | `5` |
   | `LOW_THRESHOLD` | `40` |
   | `APPLY` | `false` |
   | `DRY_RUN` | `true` |

5. **Save**.

---

## 3.3 Dry-Run

```bash
python src/test_invoke.py
```

Expected — recommendations only, nothing changed:

```
Response: {
  "dry_run": true,
  "apply": false,
  "count": 2,
  "findings": [
    {"instance_id": "i-0aaa...", "current_type": "t3.micro", "max_cpu": 0.3,
     "finding": "idle", "recommended_type": null, "applied": false},
    {"instance_id": "i-0bbb...", "current_type": "t3.micro", "max_cpu": 98.7,
     "finding": "right-sized", "recommended_type": null, "applied": false}
  ]
}
```

`recommended_type` is `null` for `t3.micro` because it's already the smallest in the table — the
*finding* is what matters here (`idle` vs `right-sized`). To see a real downsize recommendation,
launch one instance as `t3.small` and re-run: an idle `t3.small` → recommends `t3.micro`.

> **Seeing `"finding": "no-data"`?** CloudWatch hasn't collected enough datapoints yet. Wait
> ~10 minutes after launch and re-run. This is the safety net from 3.1 doing its job.

---

## Checkpoint

- [ ] `compute-rightsizer` is **Active**, handler `compute_rightsizer.handler`, timeout 120s
- [ ] Dry-run returned a `findings` array with one entry per tagged instance
- [ ] The idle instance reads `idle`; the loaded one reads `right-sized` (or both `idle` if you
      skipped the load)
- [ ] Nothing was resized (`"applied": false` everywhere)

---

**Next:** [Step 4 — Schedule It and Email the Report](./04-schedule-and-report.md)
