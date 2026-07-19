# Step 2 — Deploy the HTTP Function

Now you'll ship `order_status` to **Cloud Functions (2nd gen)**. One command uploads your source,
builds it with buildpacks, and stands up a scale-to-zero HTTPS endpoint.

---

## 2.1 Deploy

From the project root (the folder that contains `src/`):

```bash
gcloud functions deploy order-status \
  --gen2 \
  --runtime python312 \
  --region us-east1 \
  --source ./src \
  --entry-point order_status \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars "STORE_NAME=Meridian Retail,ENVIRONMENT=dev" \
  --memory 256Mi \
  --max-instances 3
```

Flag by flag:

| Flag | Why |
|------|-----|
| `order-status` | The **function name** (and the Cloud Run service name) |
| `--gen2` | Use 2nd gen — runs on Cloud Run, more triggers, concurrency, longer timeouts |
| `--runtime python312` | The language runtime buildpacks will use |
| `--source ./src` | Folder to upload; must contain `main.py` + `requirements.txt` |
| `--entry-point order_status` | The **Python function name** to invoke (not the deploy name) |
| `--trigger-http` | Make it an HTTP endpoint (vs. an event trigger — that's the next project) |
| `--allow-unauthenticated` | Public endpoint, no IAM token needed to call it (a beginner simplification) |
| `--set-env-vars` | Inject config the code reads at runtime |
| `--max-instances 3` | Cap concurrency so a runaway loop can't scale (and bill) without bound |

The first deploy takes **1–2 minutes** — it's building a container behind the scenes. Watch the
output: it uploads the source, runs Cloud Build, then creates the Cloud Run service.

> **Why `--entry-point` matters.** `main.py` could define several functions. The entry point tells
> the Functions Framework which one is *the* handler. It must exactly match the Python function name
> decorated with `@functions_framework.http`.

### Console (Alternative)

1. **Cloud Functions** → **Create function**.
2. Environment **2nd gen**, name `order-status`, region **us-east1**.
3. Trigger **HTTPS**, **Allow unauthenticated invocations**.
4. **Runtime, build...** → add env vars `STORE_NAME` / `ENVIRONMENT`; set Max instances to 3.
5. **Next** → Runtime **Python 3.12**, Entry point `order_status`. Paste `main.py` and
   `requirements.txt` into the inline editor (or upload the `src/` zip).
6. **Deploy**.

---

## 2.2 Grab the URL

```bash
export URL="$(gcloud functions describe order-status --gen2 --region us-east1 \
  --format='value(serviceConfig.uri)')"
echo "$URL"
# → https://order-status-xxxxxxxxxx-ue.a.run.app   (an HTTPS Cloud Run URL)
```

Notice the URL is a **`run.app`** address — proof that a 2nd-gen function is a Cloud Run service. You
can see it in **both** the Cloud Functions list and the Cloud Run list in the Console.

---

## 2.3 First Call

```bash
curl -s "$URL/?order_id=1001"
# → {"store":"Meridian Retail","environment":"dev","order_id":"1001","order":{"item":"Wool Overcoat","status":"shipped","total":189.0}}
```

If you get JSON back, your function is live on the internet, HTTPS included, with a certificate you
never had to configure.

---

## Checkpoint

- [ ] `gcloud functions deploy` finished with `state: ACTIVE`
- [ ] `describe … serviceConfig.uri` prints an `https://…run.app` URL
- [ ] `curl "$URL/?order_id=1001"` returns the order JSON
- [ ] The function shows up under **both** Cloud Functions and Cloud Run in the Console

---

**Next:** [Step 3 — Invoke and Reconfigure](./03-invoke-and-config.md)
