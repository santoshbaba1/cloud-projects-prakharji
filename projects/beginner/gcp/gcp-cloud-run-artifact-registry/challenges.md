# Challenges — GCP Cloud Run & Artifact Registry

Extend the build-and-deploy flow toward how teams really ship. Each challenge builds on the service
from the main steps. Clean up extras afterward.

---

## 1. Build from Source with No Dockerfile (Buildpacks)

Cloud Run can build **and** deploy directly from source, using Google Cloud **buildpacks** — no
`Dockerfile` at all:

```bash
cd src
gcloud run deploy meridian-web-bp --source . --region us-east1 --allow-unauthenticated
```

- **Question:** Where did the image get stored, and what base image did buildpacks pick? Compare the
  image size to your hand-written `Dockerfile` build.

---

## 2. Make It Private and Call It with a Token

Redeploy **without** `--allow-unauthenticated`. Confirm an anonymous `curl` gets `403`, then call it
successfully with an identity token (`gcloud auth print-identity-token`).

- **Question:** What IAM role does `--allow-unauthenticated` grant to `allUsers`, and to whom would
  you grant `roles/run.invoker` for a service-to-service call instead?

---

## 3. Set a Concurrency and Min/Max Instances

Tune the service's scaling:

```bash
gcloud run services update meridian-web --region us-east1 \
  --concurrency=40 --min-instances=0 --max-instances=5
```

Load-test with a loop or `hey`/`ab` and watch instance count in **Cloud Run → Metrics**.

- **Question:** How does raising `--concurrency` change how many instances you need? What does
  `--min-instances=1` cost you (see [costs.md](costs.md))?

---

## 4. Store a Secret in Secret Manager

Move a sensitive value out of `--set-env-vars` and into **Secret Manager**, mounted as an env var:

```bash
echo -n "super-secret" | gcloud secrets create meridian-web-key --data-file=-
gcloud run services update meridian-web --region us-east1 \
  --set-secrets=API_KEY=meridian-web-key:latest
```

- **Question:** Why is a mounted secret safer than a plain env var, and which service account needs
  `roles/secretmanager.secretAccessor`?

---

## 5. Automate Builds with a Cloud Build Trigger

Connect a GitHub repo and create a **build trigger** so every push to `main` runs
`cloudbuild.yaml` and produces a new image tagged with the commit SHA (`$SHORT_SHA`).

- **Question:** Why is a git SHA a better image tag than `latest` for traceability?

---

## 6. Add a Deploy Step to the Build

Extend `cloudbuild.yaml` with a second step that runs `gcloud run deploy` after the image is pushed,
so one `builds submit` builds **and** deploys.

- **Question:** What extra IAM role does the Cloud Build service account need to deploy to Cloud Run,
  and why is that a reason to prefer a dedicated delivery tool? (This is exactly what the
  [Cloud Deploy project](../../../intermediate/gcp/gcp-cloud-deploy-pipeline/README.md) solves.)

---

## 7. Map a Custom Domain

Map a domain you own to the service with **Cloud Run domain mappings** (or a global external LB in
front). Watch Google provision a managed TLS certificate.

- **Question:** What DNS records does the mapping require, and why must DNS resolve before the cert
  provisions?
