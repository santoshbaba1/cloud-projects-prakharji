# Step 1 — Project Setup & Enable the APIs

Before you can build or deploy a container, three Google Cloud services need to be **enabled** on
your project: **Cloud Build** (builds images), **Artifact Registry** (stores them), and **Cloud
Run** (runs them). This step turns them on and sets your working region.

> **New to gcloud?** If you haven't installed and authenticated the CLI yet, do
> [Step 1 of the networking project](../../../../beginner/gcp/gcp-vpc-firewall-basics/steps/01-install-gcloud.md)
> first — it walks through `gcloud` install, `gcloud auth login`, creating a project, and linking
> billing. Come back here once `gcloud config get-value project` prints your project ID.

---

## 1.1 Confirm Your Project & Billing

Everything you build lives inside one **project**, and Cloud Run requires **billing** to be linked
(even though this lab stays in the free tier).

```bash
# Which project am I working in?
gcloud config get-value project

# If it's not set, point at yours (replace with your ID):
gcloud config set project YOUR_PROJECT_ID

# Store it in a shell variable — later steps reuse it
export PROJECT_ID="$(gcloud config get-value project)"
echo "$PROJECT_ID"
```

Confirm billing is linked:

```bash
gcloud billing projects describe "$PROJECT_ID" \
  --format='value(billingEnabled)'
```

It should print `True`. If it prints `False`, link a billing account — see the
[networking project's Step 1.5](../../../../beginner/gcp/gcp-vpc-firewall-basics/steps/01-install-gcloud.md).

---

## 1.2 Set the Region

We use **`us-east1`** throughout this repo. Cloud Run and Artifact Registry are both **regional**,
so setting a default now saves you typing `--region` on every command.

```bash
gcloud config set run/region us-east1
export REGION=us-east1
```

> **Why regional?** An Artifact Registry repo and a Cloud Run service each live in one region. Your
> image and the service that runs it should share a region so pulls are fast and free of
> cross-region egress.

---

## 1.3 Enable the Three APIs

Each Google Cloud service must be enabled per project before first use.

### Console

1. Go to **APIs & Services** → **Enabled APIs & services** → **+ Enable APIs and Services**.
2. Search for and **Enable** each of these (one at a time):
   - **Cloud Build API**
   - **Artifact Registry API**
   - **Cloud Run Admin API**

### gcloud CLI (Alternative)

Enable all three in one command:

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  run.googleapis.com
```

This takes a minute. Confirm they're on:

```bash
gcloud services list --enabled \
  --filter='config.name:(cloudbuild.googleapis.com OR artifactregistry.googleapis.com OR run.googleapis.com)' \
  --format='value(config.name)'
```

You should see all three listed.

---

## 1.4 What Each Service Does (30-Second Map)

| Service | Its job here | AWS analogue |
|---------|--------------|--------------|
| **Cloud Build** | Turns `src/` + `Dockerfile` into a pushed image | CodeBuild |
| **Artifact Registry** | Stores the image in a private Docker repo | ECR |
| **Cloud Run** | Runs the image as a scale-to-zero HTTPS service | App Runner / Fargate |

You'll touch them in exactly that order: **build → store → run**.

---

## Checkpoint

- [ ] `gcloud config get-value project` prints your project ID
- [ ] `billingEnabled` is `True`
- [ ] Default Cloud Run region is `us-east1` (`gcloud config get-value run/region`)
- [ ] Cloud Build, Artifact Registry, and Cloud Run APIs are all enabled

---

**Next:** [Step 2 — Create an Artifact Registry Repository](./02-artifact-registry.md)
