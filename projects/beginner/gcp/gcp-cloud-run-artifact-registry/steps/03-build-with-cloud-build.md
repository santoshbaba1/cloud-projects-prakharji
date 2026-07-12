# Step 3 — Build & Push the Image with Cloud Build

You have an app in `src/` and an empty repo. Now you'll turn the app into a **container image** and
push it to Artifact Registry — **without installing Docker locally**. **Cloud Build** does the build
on Google's servers: you upload the source, it runs your `Dockerfile`, and it pushes the result.

---

## 3.1 Look at What You're Building

The app is a tiny Flask service (`src/app.py`) with two routes:

- `/` returns JSON: `{"message": ..., "version": ..., "revision": ...}`
- `/healthz` returns `ok` — Cloud Run uses it to confirm the container is alive

The `src/Dockerfile` packages it on `python:3.12-slim` and runs it with **gunicorn** bound to
`$PORT`. Cloud Run sets `$PORT` to `8080` and expects your app to listen there — the Dockerfile's
`ENV PORT=8080` matches that.

> **Why gunicorn, not `flask run`?** Flask's dev server is single-threaded and not meant for real
> traffic. Gunicorn is a production WSGI server; `--workers 2 --threads 4` lets one Cloud Run
> instance handle several concurrent requests.

Move into the source directory (the build context):

```bash
cd src
```

---

## 3.2 Build — The One-Liner

The fastest way to build and push is `gcloud builds submit --tag`. It uploads the current directory,
builds the `Dockerfile`, and pushes the image to the path you give:

```bash
gcloud builds submit --tag "${IMAGE_PATH}:v1" .
```

What happens:

1. gcloud tars up `src/` and uploads it to a Cloud Build staging bucket.
2. Cloud Build runs `docker build` using your `Dockerfile`.
3. It **pushes** the finished image to `us-east1-docker.pkg.dev/.../meridian-web:v1`.
4. The command streams the build log and ends with `SUCCESS`.

> If `IMAGE_PATH` isn't set (new shell), re-export it from
> [Step 2.1](./02-artifact-registry.md#21-understand-the-image-path).

---

## 3.3 Build — The `cloudbuild.yaml` Way (Alternative)

The one-liner is great for a single image. For anything real you'll want a **build config file** so
the build is version-controlled and can do more than one step. `src/cloudbuild.yaml` does the same
build+push, driven by substitutions:

```bash
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_TAG=v1 .
```

`$PROJECT_ID` is injected by Cloud Build automatically; `_REGION`, `_REPO`, `_IMAGE`, and `_TAG` come
from the file's `substitutions:` block (override any with `--substitutions`). This is the pattern the
[intermediate Cloud Deploy project](../../../../intermediate/gcp/gcp-cloud-deploy-pipeline/README.md)
builds on.

> **Console path:** In the Cloud Console, **Cloud Build → History** shows every build (from either
> command) with its logs, duration, and the image it produced. There's no "click to build from
> local files" in the Console — builds start from the CLI or a source-repo trigger.

---

## 3.4 Confirm the Image Landed

List the images in the repo:

```bash
gcloud artifacts docker images list "$IMAGE_PATH" \
  --include-tags \
  --format='table(IMAGE,TAGS,CREATE_TIME)'
```

You should see one image tagged `v1`. In the **Console**, open **Artifact Registry → meridian-apps →
meridian-web** to see the same thing with its digest and size.

---

## 3.5 Go Back Up

Return to the project root so later steps' paths line up:

```bash
cd ..
```

---

## Checkpoint

- [ ] `gcloud builds submit` finished with **SUCCESS**
- [ ] `gcloud artifacts docker images list "$IMAGE_PATH"` shows `meridian-web:v1`
- [ ] Cloud Build → History shows the build (Console)
- [ ] You understand the image path `REGION-docker.pkg.dev/PROJECT/REPO/IMAGE:TAG`

---

**Next:** [Step 4 — Deploy the Image to Cloud Run](./04-deploy-cloud-run.md)
