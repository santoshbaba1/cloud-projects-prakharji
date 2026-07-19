# Step 4 — Read the Logs

A function you can't observe is a function you can't operate. Cloud Functions sends everything your
code writes to **stdout/stderr** into **Cloud Logging**. Because `main.py` prints **structured JSON**,
those logs arrive with real severities and searchable fields.

---

## 4.1 Generate Some Log Lines

Make a few calls that hit different log paths:

```bash
curl -s "$URL/?order_id=1001" >/dev/null   # INFO  "order looked up"
curl -s "$URL/?order_id=9999" >/dev/null   # WARNING "order not found"
curl -s "$URL/" >/dev/null                 # INFO  "heartbeat ping (no order_id)"
```

---

## 4.2 Tail the Logs from the CLI

```bash
gcloud functions logs read order-status --gen2 --region us-east1 --limit 20
```

Or read them as the Cloud Run service (same logs, richer filter):

```bash
gcloud run services logs read order-status --region us-east1 --limit 20
```

---

## 4.3 Query the Structured Fields

This is where structured logging pays off. In `main.py` each log line is a JSON object like:

```json
{"severity":"WARNING","message":"order not found","environment":"prod","order_id":"9999"}
```

Cloud Logging promotes `severity` to the entry's level and turns the other keys into
**`jsonPayload.*`** fields you can filter on. Find just the "not found" warnings:

```bash
gcloud logging read \
  'resource.type="cloud_run_revision"
   AND resource.labels.service_name="order-status"
   AND jsonPayload.message="order not found"' \
  --limit 10 --format='table(timestamp, jsonPayload.order_id, severity)'
```

### Console (Alternative)

1. **Logging → Logs Explorer**.
2. Query box, paste:
   ```
   resource.type="cloud_run_revision"
   resource.labels.service_name="order-status"
   severity>=WARNING
   ```
3. **Run query**. Expand an entry — you'll see `jsonPayload.order_id` as a real, clickable field.
   Click it → **Show matching entries** to build filters without typing.

> **Why not just `print("order not found")`?** A plain string lands as `textPayload` with severity
> `DEFAULT` — you can't filter by level or by `order_id`. One `json.dumps({...})` line turns log
> spelunking into structured queries. This is the single highest-leverage logging habit in
> serverless.

---

## 4.4 (Good to Know) Errors and Cold Starts

- An **unhandled exception** in your function is logged at `ERROR` with a stack trace and returns a
  500 to the caller — try it by temporarily breaking `main.py` if you're curious.
- The first request after idle pays a **cold start** (the instance spins up). You may see a short gap
  before the first log line. 2nd-gen functions support `--min-instances 1` to keep one warm (it
  costs money, so leave it at 0 for this lab).

---

## Checkpoint

- [ ] `gcloud functions logs read` shows your recent invocations
- [ ] You can filter to just `WARNING` "order not found" entries
- [ ] In Logs Explorer, `jsonPayload.order_id` appears as a distinct field
- [ ] You understand why structured JSON beats plain `print` strings

---

**Next:** [Step 5 — Put It on a Schedule](./05-schedule.md)
