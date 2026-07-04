# Step 3 — Create the Scheduler Function

Deploy `ec2_scheduler.py`, then test it **in `DRY_RUN` mode first** so you can see what it
*would* do before it actually powers anything off.

---

## 3.1 Review the Handler

Open `src/ec2_scheduler.py`. Key ideas:

```python
action = (event.get("action") or "").lower()
...
wanted_state = "running" if action == "stop" else "stopped"
```

- One function, two behaviors. The **event** decides: `{"action":"stop"}` vs `{"action":"start"}`.
- It only looks at instances in the *relevant* state — you can't stop a stopped instance, so
  "stop" filters for `running` and "start" filters for `stopped`. This keeps the action
  **idempotent**: running it twice does nothing the second time.

```python
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
```

- With `DRY_RUN=true`, the function logs the instance IDs it *would* change but makes no
  Start/Stop call. Always dry-run a destructive automation first.

---

## 3.2 Package and Deploy

```bash
cd /path/to/lambda-ec2-start-stop-scheduler
zip -j ec2_scheduler.zip src/ec2_scheduler.py
```

Console:

1. **Lambda** → **Create function** → **Author from scratch**.

   | Field | Value |
   |-------|-------|
   | Function name | `ec2-scheduler` |
   | Runtime | **Python 3.14** |
   | Execution role | **Use an existing role** → `Ec2SchedulerExecutionRole` |

2. **Create function** → **Code source** → **Upload from** → **.zip file** → `ec2_scheduler.zip` → **Save**.
3. **Configuration → General configuration → Edit:**

   | Setting | Value | Why |
   |---------|-------|-----|
   | Handler | `ec2_scheduler.handler` | filename.function |
   | Memory | 128 MB | plenty for API calls |
   | Timeout | 30 sec | `describe` + `start/stop` over many instances can take a few seconds |

4. **Configuration → Environment variables → Edit**, add:

   | Key | Value |
   |-----|-------|
   | `TAG_KEY` | `AutoPower` |
   | `TAG_VALUE` | `true` |
   | `DRY_RUN` | `true` |

5. **Save**.

---

## 3.3 Dry-Run Test

```bash
python src/test_invoke.py stop
```

Expected — it *finds* the instance but doesn't stop it:

```
HTTP status   : 200
Function error: None
Response      : {
  "action": "stop",
  "affected": ["i-0abc123..."],
  "dry_run": true
}
```

Confirm the instance is **still running** (`describe-instances` from Step 2.3). Logs will show
`DRY_RUN=true — not calling EC2`.

---

## 3.4 Turn Dry-Run Off

Once you trust it, set `DRY_RUN` to `false`:

- Console: **Configuration → Environment variables** → change `DRY_RUN` to `false` → **Save**.
- CLI:

```bash
aws lambda update-function-configuration \
  --function-name ec2-scheduler \
  --environment "Variables={TAG_KEY=AutoPower,TAG_VALUE=true,DRY_RUN=false}"
```

Now a real stop:

```bash
python src/test_invoke.py stop
```

Watch the instance transition `running → stopping → stopped` (takes ~1 minute). Then start it
again:

```bash
python src/test_invoke.py start
```

---

## Checkpoint

- [ ] `ec2-scheduler` is **Active**, handler `ec2_scheduler.handler`, timeout 30s
- [ ] Dry-run reported the instance under `affected` without changing its state
- [ ] With `DRY_RUN=false`, `stop` then `start` actually toggled the instance
- [ ] An untagged instance (if you launched one) was **never** affected

---

**Next:** [Step 4 — Schedule Start and Stop](./04-schedule-start-stop.md)
