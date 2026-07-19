# Step 3 — Invoke and Reconfigure

You have a live endpoint. Now you'll exercise its behaviour and — the important part — change how it
responds **without touching code**, by updating environment variables and redeploying.

---

## 3.1 Exercise Every Path

```bash
# A shipped order
curl -s "$URL/?order_id=1001" | python3 -m json.tool

# A cancelled order
curl -s "$URL/?order_id=1003" | python3 -m json.tool

# An unknown order → 404
curl -si "$URL/?order_id=9999" | head -n 1     # HTTP/2 404

# No order_id → treated as a health "heartbeat" (used by the schedule in Step 5)
curl -s "$URL/" | python3 -m json.tool
```

The function also accepts a **POST with JSON**:

```bash
curl -s -X POST "$URL" -H 'Content-Type: application/json' \
  -d '{"order_id":"1002"}' | python3 -m json.tool
```

That's because `main.py` reads `order_id` from the query string *or* the JSON body — a common pattern
for a function that serves both browsers and API clients.

---

## 3.2 Change Config Without Changing Code

The store name and environment come from env vars. Update them and redeploy — no code change:

```bash
gcloud functions deploy order-status \
  --gen2 --region us-east1 --source ./src --entry-point order_status \
  --trigger-http \
  --update-env-vars "STORE_NAME=Meridian Retail — PROD,ENVIRONMENT=prod"
```

> `--update-env-vars` **merges** (changes just these keys). `--set-env-vars` **replaces** the whole
> set. Use update when you only want to tweak one value.

Now the response reflects the new config:

```bash
curl -s "$URL/?order_id=1001" | python3 -m json.tool
# "store": "Meridian Retail — PROD", "environment": "prod"
```

This is the serverless payoff for configuration: the **same immutable build** behaves differently per
environment. In the next projects you'll graduate config from env vars to **Secret Manager** for
anything sensitive.

---

## 3.3 See the New Revision

Because 2nd-gen functions are Cloud Run services, each deploy creates a **revision**:

```bash
gcloud run revisions list --service order-status --region us-east1 \
  --format='table(REVISION,ACTIVE,SERVICE)'
```

You'll see two now — the redeploy created a second revision that took 100% of traffic. (Traffic
splitting/rollback across these revisions is exactly what the App Delivery track's Cloud Run project
teaches.)

---

## Checkpoint

- [ ] All four call paths behave as expected (shipped, cancelled, 404, heartbeat)
- [ ] The POST-with-JSON form works
- [ ] After `--update-env-vars`, the response shows `PROD` / `prod` with no code change
- [ ] `gcloud run revisions list` shows a second revision

---

**Next:** [Step 4 — Read the Logs](./04-logging.md)
