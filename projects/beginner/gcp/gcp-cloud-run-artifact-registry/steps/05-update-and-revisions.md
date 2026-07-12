# Step 5 — Ship v2, Split Traffic, and Roll Back

Real apps change. Here you'll make a small edit, rebuild a **v2** image, deploy it as a new
**revision**, then use Cloud Run's **traffic splitting** to do a mini canary and an instant
**rollback** — all without touching the URL your users have.

---

## 5.1 Change the App

Edit `src/app.py` and change the default greeting so v2 is visibly different. Update this line:

```python
GREETING = os.environ.get("GREETING", "Hello from Meridian Retail")
```

to:

```python
GREETING = os.environ.get("GREETING", "Welcome to Meridian Retail v2")
```

(You can also bump `VERSION`'s default to `2.0`.) Save the file.

---

## 5.2 Build v2

Rebuild and push with a new tag so the two versions are distinct in the registry:

```bash
cd src
gcloud builds submit --tag "${IMAGE_PATH}:v2" .
cd ..
```

Confirm both tags exist:

```bash
gcloud artifacts docker images list "$IMAGE_PATH" --include-tags \
  --format='table(TAGS,CREATE_TIME)'
```

---

## 5.3 Deploy v2 — But Hold Traffic

By default `gcloud run deploy` sends **100%** of traffic to the new revision immediately. To canary
instead, deploy with `--no-traffic` and `--tag` so the new revision is reachable at its own URL
without taking production traffic yet:

```bash
gcloud run deploy meridian-web \
  --image "${IMAGE_PATH}:v2" \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars "GREETING=Welcome to Meridian Retail v2,APP_VERSION=2.0" \
  --no-traffic \
  --tag v2
```

Now there are **two** revisions, but v1 still serves 100% of the main URL. Test v2 in isolation via
its tagged URL (printed by the deploy, of the form `https://v2---meridian-web-....run.app`):

```bash
gcloud run revisions list --service meridian-web --region us-east1 \
  --format='table(REVISION,ACTIVE,TRAFFIC_TAGS)'

export V2_URL="$(gcloud run services describe meridian-web --region us-east1 \
  --format='value(status.traffic.url)' --flatten='status.traffic' \
  --filter='status.traffic.tag=v2')"
curl -s "$V2_URL/"   # → the v2 greeting, while the main URL is still v1
```

---

## 5.4 Canary: Send 10% to v2

Split live traffic — 90% to the current revision, 10% to the v2-tagged one:

```bash
gcloud run services update-traffic meridian-web --region us-east1 \
  --to-tags v2=10
```

Hit the **main** URL a few times and watch the mix (roughly 1 in 10 shows v2):

```bash
for i in $(seq 1 10); do curl -s "$URL/" | grep -o '"message":"[^"]*"'; done
```

Happy with v2? Promote it to 100%:

```bash
gcloud run services update-traffic meridian-web --region us-east1 --to-tags v2=100
```

---

## 5.5 Roll Back Instantly

Suppose v2 misbehaves. Rollback is a **traffic change**, not a rebuild — point 100% back at the v1
revision. Get its exact name, then route to it:

```bash
gcloud run revisions list --service meridian-web --region us-east1 \
  --format='value(REVISION)'
# e.g. meridian-web-00001-abc

gcloud run services update-traffic meridian-web --region us-east1 \
  --to-revisions meridian-web-00001-abc=100
```

Verify the main URL is back to v1:

```bash
curl -s "$URL/" | grep -o '"version":"[^"]*"'   # → "version":"1.0"
```

That instant, no-rebuild rollback — because every revision is kept and immutable — is the whole point
of revisions. The [intermediate project](../../../../intermediate/gcp/gcp-cloud-deploy-pipeline/README.md)
formalizes this promote/rollback flow across **staging and prod** with Cloud Deploy.

---

## Checkpoint

- [ ] Two revisions exist; you tested v2 at its tagged URL before shifting traffic
- [ ] A 10% canary split showed a mix of v1/v2 on the main URL
- [ ] You promoted v2 to 100%, then **rolled back** to v1 with a traffic update (no rebuild)
- [ ] You understand: revisions are immutable, rollback = re-point traffic

---

**Next:** [Step 6 — Cleanup](./06-cleanup.md)
