# Step 2 — Create and Deploy the Function

You'll deploy `heartbeat.py`, confirm it's `Active`, and run it once by hand before
attaching any schedule. Always prove the code works *before* automating it.

---

## 2.1 Review the Handler

Open `src/heartbeat.py`. Two things to notice:

```python
trigger = event.get("source", "manual")
```

- When **EventBridge** invokes the function, the `event` contains `"source": "aws.events"`.
  When *you* invoke it with an empty payload, there's no `source`, so it logs `manual`.
  This lets you tell scheduled runs apart from test runs in the logs.

```python
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
```

- The SNS publish is **optional**. If you don't set the env var, the function just logs.
  You'll set it in Step 4.

---

## 2.2 Package the Code

```bash
cd /path/to/lambda-eventbridge-scheduled

# -j strips the src/ prefix so heartbeat.py lands at the ZIP root
zip -j heartbeat.zip src/heartbeat.py
```

> **Why `-j`:** Lambda looks for `heartbeat.py` at the root of the archive. If it's
> nested under `src/`, you get `Runtime.ImportModuleError`.

---

## 2.3 Create the Function (Console)

1. **Lambda** → **Create function** → **Author from scratch**.

| Field | Value |
|-------|-------|
| Function name | `scheduled-heartbeat` |
| Runtime | **Python 3.14** |
| Architecture | x86_64 |
| Execution role | **Use an existing role** → `ScheduledHeartbeatExecutionRole` |

2. **Create function**.
3. **Code source** → **Upload from** → **.zip file** → select `heartbeat.zip` → **Save**.
4. **Configuration** → **General configuration** → **Edit**:

   | Setting | Value |
   |---------|-------|
   | Handler | `heartbeat.handler` |
   | Memory | 128 MB |
   | Timeout | 10 sec |

5. **Save**.

---

## 2.4 Run It Once by Hand

From your terminal:

```bash
python src/test_invoke.py
```

Expected output:

```
HTTP status   : 200
Function error: None
Response      : {
  "service": "scheduled-heartbeat",
  "environment": "dev",
  "ran_at": "2026-06-14T12:00:00+00:00",
  "trigger": "manual",
  "request_id": "..."
}
```

Note `"trigger": "manual"` — that confirms the function ran from your CLI, not a schedule.

### Via AWS CLI

```bash
aws lambda invoke \
  --function-name scheduled-heartbeat \
  --payload '{}' \
  --cli-binary-format raw-in-base64-out \
  response.json
cat response.json
```

---

## Checkpoint

- [ ] `scheduled-heartbeat` is **Active**, runtime **Python 3.14**, handler `heartbeat.handler`
- [ ] Manual invoke returns HTTP 200 with `"trigger": "manual"`
- [ ] A log group `/aws/lambda/scheduled-heartbeat` now exists

---

**Next:** [Step 3 — Schedule It with EventBridge](./03-schedule-with-eventbridge.md)
