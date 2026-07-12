# Step 2 — Create an Artifact Registry Repository

Before you can build an image, you need somewhere to **put** it. That's **Artifact Registry** — a
private, managed repository for container images (and other artifacts). In this step you'll create a
**Docker-format** repo called `meridian-apps` in `us-east1`.

> **Why not Container Registry (`gcr.io`)?** The older Container Registry is deprecated. Artifact
> Registry is its replacement: it supports multiple formats (Docker, Maven, npm, …), is regional,
> and has finer-grained IAM. Use it for anything new.

---

## 2.1 Understand the Image Path

Every image in Artifact Registry has a fully-qualified name built from four parts:

```
us-east1-docker.pkg.dev / PROJECT_ID / meridian-apps / meridian-web : v1
└────────── host ──────┘   └ project ┘   └── repo ──┘   └─ image ─┘  └tag┘
```

- **host** — always `REGION-docker.pkg.dev` for a Docker repo
- **repo** — the repository you're about to create (`meridian-apps`)
- **image** — the name of your app image (`meridian-web`)
- **tag** — a version label (`v1`, `latest`, a git SHA, …)

You'll type this path a lot, so save the prefix now:

```bash
export REGION=us-east1
export REPO=meridian-apps
export IMAGE=meridian-web
export IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE}"
echo "$IMAGE_PATH"
```

---

## 2.2 Create the Repository

### Console

1. Go to **Artifact Registry** → **Repositories** → **+ Create Repository**.
2. Fill in the form:

   | Field | Value |
   |-------|-------|
   | Name | `meridian-apps` |
   | Format | **Docker** |
   | Mode | Standard |
   | Region | `us-east1` |
   | Encryption | Google-managed key |

3. Click **Create**.

### gcloud CLI (Alternative)

```bash
gcloud artifacts repositories create "$REPO" \
  --repository-format=docker \
  --location="$REGION" \
  --description="Meridian Retail container images"
```

Confirm it exists:

```bash
gcloud artifacts repositories describe "$REPO" --location="$REGION" \
  --format='value(name,format)'
```

---

## 2.3 Configure Docker Authentication (Optional but Useful)

Cloud Build (Step 3) pushes to the repo **for you**, so you don't strictly need local Docker auth to
finish this project. But if you ever want to `docker push` from your laptop, tell Docker how to
authenticate to this registry host:

```bash
gcloud auth configure-docker "${REGION}-docker.pkg.dev"
```

This adds a credential helper entry so `docker` uses your gcloud identity for
`us-east1-docker.pkg.dev`. (Nothing to do here if you don't have Docker installed — Cloud Build
still works.)

---

## 2.4 Why the Repo Is Empty (and That's Fine)

Right now `gcloud artifacts docker images list "$IMAGE_PATH"` returns nothing — you haven't built an
image yet. The repo is just the **shelf**; Step 3 puts a box on it.

---

## Checkpoint

- [ ] `meridian-apps` repository exists in `us-east1`, format **Docker**
- [ ] `IMAGE_PATH` is exported and echoes `us-east1-docker.pkg.dev/<PROJECT_ID>/meridian-apps/meridian-web`
- [ ] (Optional) `gcloud auth configure-docker us-east1-docker.pkg.dev` succeeded

---

**Next:** [Step 3 — Build & Push the Image with Cloud Build](./03-build-with-cloud-build.md)
