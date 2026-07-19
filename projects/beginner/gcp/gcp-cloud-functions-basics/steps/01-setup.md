# Step 1 — Setup: Project, APIs, and a Local Run

Before deploying anything you'll point gcloud at a project, turn on the APIs this lab needs, and
(optionally) run the function on your own machine to see that it's just plain Python.

---

## 1.1 Pick a Project and Region

```bash
# Use an existing project or create one (project IDs are globally unique).
export PROJECT_ID="meridian-serverless-$(whoami)"   # edit to taste
gcloud projects create "$PROJECT_ID" 2>/dev/null || true
gcloud config set project "$PROJECT_ID"
gcloud config set run/region us-east1
gcloud config set functions/region us-east1
```

> If you already have a project with billing linked, just
> `gcloud config set project <your-project-id>` and skip the create.

Confirm billing is linked (2nd-gen functions need it):

```bash
gcloud billing projects describe "$PROJECT_ID" --format='value(billingEnabled)'
# → True
```

If it prints `False` (or errors), link a billing account in the Console:
**Billing → Account management → link a project**, or:

```bash
gcloud billing accounts list
gcloud billing projects link "$PROJECT_ID" --billing-account=XXXXXX-XXXXXX-XXXXXX
```

---

## 1.2 Enable the APIs

A 2nd-gen function touches five services. Enable them all now:

```bash
gcloud services enable \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com \
  logging.googleapis.com
```

| API | Why it's needed |
|-----|-----------------|
| `cloudfunctions` | The Functions control plane you deploy to |
| `run` | 2nd-gen functions **are** Cloud Run services |
| `cloudbuild` | Buildpacks build your source into an image |
| `artifactregistry` | Stores the built image (`gcf-artifacts` repo, auto-created) |
| `cloudscheduler` | The cron job in Step 5 |
| `logging` | Reading logs in Step 4 |

This can take a minute the first time.

---

## 1.3 (Optional) Run It Locally

The whole point of the Functions Framework is that your code is *just Python* — you can run the exact
same handler on your laptop with no GCP at all. From `src/`:

```bash
cd src
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
STORE_NAME="Meridian Retail (local)" \
  functions-framework --target order_status --debug --port 8080
```

In another terminal:

```bash
curl -s "http://localhost:8080/?order_id=1001"
# → {"store":"Meridian Retail (local)","environment":"dev","order_id":"1001","order":{...}}

curl -s "http://localhost:8080/?order_id=9999"   # → 404 not found
curl -s "http://localhost:8080/"                 # → heartbeat ok
```

Stop it with **Ctrl-C** and `deactivate`. This is the same `functions-framework` runner Google uses
inside the container — what runs locally is what runs in the cloud.

---

## Checkpoint

- [ ] `gcloud config get-value project` shows your project
- [ ] `billingEnabled` is `True`
- [ ] `gcloud services list --enabled` includes `cloudfunctions`, `run`, and `cloudscheduler`
- [ ] (Optional) the function answered locally on port 8080

---

**Next:** [Step 2 — Deploy the HTTP Function](./02-deploy-http-function.md)
