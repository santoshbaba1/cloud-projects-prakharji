# Challenges — GCP Cloud Deploy Pipeline

Push the pipeline toward how teams really run continuous delivery. Each challenge assumes the
pipeline from the main steps exists (or rebuild it). Clean up extras afterward.

---

## 1. Add a Canary Rollout to Prod

Instead of an all-at-once prod deploy, use a **canary deployment strategy** so prod shifts traffic
gradually (e.g. 25% → 50% → 100%). Add a `strategy.canary` block to the `prod` stage in
`clouddeploy.yaml`, with `runCanary` phases and Cloud Run traffic percentages.

- **Question:** How does Cloud Deploy's canary differ from the manual Cloud Run traffic split you did
  in the [beginner project](../../../beginner/gcp/gcp-cloud-run-artifact-registry/steps/05-update-and-revisions.md)?

---

## 2. Add a Verify (Test) Job Before Promotion

Turn on `verify` for the staging target so Cloud Deploy runs an automated test (a Skaffold `verify`
container that curls `/healthz` and asserts 200) after the staging deploy — the release can't be
promoted until verification passes.

- **Question:** Why is an automated gate on staging safer than relying on a human to remember to test?

---

## 3. Trigger the Pipeline from GitHub Actions

Wire a real CI/CD flow: a GitHub Actions workflow that, on push to `main`, builds the image with
Cloud Build (authenticating via **Workload Identity Federation** — see
[gcp-databases-workload-identity](../../../advanced/gcp/gcp-databases-workload-identity/README.md))
and runs `gcloud deploy releases create` with the new image.

- **Question:** Why is WIF preferable to storing a service-account JSON key in a GitHub secret?

---

## 4. Add a Third Target in a Second Region

Extend the pipeline to `staging → prod-us → prod-eu`, where the third target is a Cloud Run service
in `europe-west1`. Add a `service-prod-eu.yaml` manifest and a matching Skaffold profile.

- **Question:** What changes if the third target is in a **different project** instead of a different
  region — for IAM and for the target's `run.location`?

---

## 5. Restrict Who Can Approve Prod

Create a group (or second user) with only `roles/clouddeploy.approver` and confirm they can approve
the prod rollout but **cannot** create releases. Remove approver rights from the release-creator.

- **Question:** How does this separation of duties map to real change-management controls?

---

## 6. Pin Every Release to a Digest via a Build Trigger

Replace manual `:v1`/`:v2` tags with a Cloud Build trigger that tags each image with `$SHORT_SHA` and
creates a Cloud Deploy release automatically, always passing the image **digest** to `--images`.

- **Question:** Why does pinning the digest (not the tag) guarantee staging and prod are byte-for-byte
  identical?

---

## 7. Rebuild It in Terraform

Define the delivery pipeline, both targets, and the Artifact Registry repo with the
`google_clouddeploy_delivery_pipeline` / `google_clouddeploy_target` Terraform resources.

- **Goal:** see the same objects you created with `gcloud deploy apply` as declarative IaC. Which
  parts still have to happen imperatively (building images, creating releases)?
