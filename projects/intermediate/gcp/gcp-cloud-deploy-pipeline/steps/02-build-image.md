# Step 2 — Build the Image Once

The core idea of continuous delivery is **build once, deploy many**. You build **one** immutable
image here; Cloud Deploy promotes that exact image to staging and then prod — no rebuild between
stages, so what you tested is literally what ships.

> This is the same build flow as the beginner project's Step 3. If the `meridian-apps` repo already
> exists from that project, you can reuse it — otherwise create it below.

---

## 2.1 Ensure the Artifact Registry Repo Exists

```bash
export REPO=meridian-apps
export IMAGE=meridian-web
export IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE}"

# Create the repo only if it isn't there yet:
gcloud artifacts repositories describe "$REPO" --location "$REGION" >/dev/null 2>&1 \
  || gcloud artifacts repositories create "$REPO" \
       --repository-format=docker --location="$REGION" \
       --description="Meridian Retail container images"
```

---

## 2.2 Build & Push a Tagged Image

Build the app in `src/` and tag it `v1`. Use an **immutable, meaningful tag** (here `v1`; in real
life a git SHA) — Cloud Deploy pins a release to a specific image, so `latest` would be ambiguous.

```bash
cd src
gcloud builds submit --tag "${IMAGE_PATH}:v1" .
cd ..
```

Confirm it landed:

```bash
gcloud artifacts docker images list "$IMAGE_PATH" --include-tags \
  --format='table(TAGS,CREATE_TIME)'
```

---

## 2.3 Capture the Exact Image Reference

Cloud Deploy releases are most reproducible when pinned to an image **digest** (`@sha256:...`) rather
than a mutable tag. Grab the digest now — you'll pass it at release time in Step 4:

```bash
export IMAGE_V1="$(gcloud artifacts docker images describe "${IMAGE_PATH}:v1" \
  --format='value(image_summary.fully_qualified_digest)')"
echo "$IMAGE_V1"
# → us-east1-docker.pkg.dev/<PROJECT>/meridian-apps/meridian-web@sha256:...
```

> **Tag vs. digest:** A tag like `:v1` can be re-pushed to point at different bytes; a digest is
> content-addressed and can never change. Pinning the digest guarantees staging and prod run the
> *identical* image. Using `:v1` also works for this lab if you skip the digest — just be consistent.

---

## Checkpoint

- [ ] `meridian-apps` repo exists in `us-east1`
- [ ] `meridian-web:v1` is built and listed in the repo
- [ ] `IMAGE_V1` holds the fully-qualified digest (or you'll use the `:v1` tag consistently)

---

**Next:** [Step 3 — Define the Delivery Pipeline & Targets](./03-define-pipeline.md)
