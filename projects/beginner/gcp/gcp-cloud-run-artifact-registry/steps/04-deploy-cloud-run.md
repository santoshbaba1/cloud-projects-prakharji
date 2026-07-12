# Step 4 — Deploy the Image to Cloud Run

The image is built and stored. Now you'll **deploy it to Cloud Run**, which turns it into an
HTTPS-addressable service that starts on demand and scales to zero when idle. One command does it.

---

## 4.1 Deploy the Service

### gcloud CLI

```bash
gcloud run deploy meridian-web \
  --image "${IMAGE_PATH}:v1" \
  --region us-east1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars "GREETING=Hello from Meridian Retail,APP_VERSION=1.0"
```

Flag by flag:

| Flag | Why |
|------|-----|
| `meridian-web` | The **service name** (also becomes part of the URL) |
| `--image` | The exact Artifact Registry image + tag to run |
| `--region us-east1` | Where the service lives (matches the repo) |
| `--allow-unauthenticated` | Make it a **public** endpoint (no IAM token needed to call it) |
| `--port 8080` | The port your container listens on (matches the Dockerfile) |
| `--set-env-vars` | Injects config the app reads at runtime — no rebuild needed |

The first deploy takes ~30–60 seconds. When it finishes, gcloud prints the **Service URL** — copy it.

> **`--allow-unauthenticated` is a real choice.** It grants `roles/run.invoker` to `allUsers`, i.e.
> anyone on the internet can hit the URL. That's what you want for a public web app. For an internal
> API you'd omit it and call the service with an identity token instead.

### Console (Alternative)

1. **Cloud Run** → **Deploy container** → **Service**.
2. **Container image URL** → **Select** → pick `meridian-apps / meridian-web / v1`.
3. Region **us-east1**; **Authentication** → **Allow unauthenticated invocations**.
4. Under **Container(s) → Variables & Secrets**, add `GREETING` and `APP_VERSION`.
5. **Create**.

---

## 4.2 Call It

Grab the URL and hit both routes:

```bash
export URL="$(gcloud run services describe meridian-web \
  --region us-east1 --format='value(status.url)')"
echo "$URL"

curl -s "$URL/"          # → {"message":"Hello from Meridian Retail","revision":"meridian-web-00001-abc","version":"1.0"}
curl -s "$URL/healthz"   # → ok
```

The `revision` field shows which **revision** answered — remember that name; Step 5 creates a second
one. Note the URL is **HTTPS** with a managed certificate you didn't have to configure.

---

## 4.3 What Just Happened (Scale-to-Zero)

Cloud Run pulled your image, started a container, and routed the request to it. With no traffic for a
while, it scales the service **down to zero instances** — you stop paying for compute until the next
request (which pays a small "cold start" latency to spin an instance back up).

See the current state:

```bash
gcloud run services describe meridian-web --region us-east1 \
  --format='value(status.url,status.latestReadyRevisionName)'
```

---

## 4.4 Peek at the Revision

Every deploy creates an immutable **revision** (image + env + settings). List them:

```bash
gcloud run revisions list --service meridian-web --region us-east1 \
  --format='table(REVISION,ACTIVE,SERVICE)'
```

There's exactly one right now, receiving 100% of traffic. In the **Console**, the service's
**Revisions** tab shows the same, with a traffic column.

---

## Checkpoint

- [ ] `gcloud run deploy` succeeded and printed a **Service URL**
- [ ] `curl "$URL/"` returns the JSON greeting with `version: 1.0`
- [ ] `curl "$URL/healthz"` returns `ok`
- [ ] One revision exists and serves 100% of traffic

---

**Next:** [Step 5 — Ship v2, Split Traffic, and Roll Back](./05-update-and-revisions.md)
