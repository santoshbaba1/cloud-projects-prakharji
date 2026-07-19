# References — GCP Cloud Functions Basics

## Official docs

- [Cloud Run functions (2nd gen) overview](https://cloud.google.com/functions/docs/concepts/version-comparison)
- [Write HTTP functions (Python)](https://cloud.google.com/functions/docs/writing/write-http-functions)
- [Functions Framework for Python](https://github.com/GoogleCloudPlatform/functions-framework-python)
- [Deploy a function with `gcloud functions deploy`](https://cloud.google.com/sdk/gcloud/reference/functions/deploy)
- [Environment variables in functions](https://cloud.google.com/functions/docs/configuring/env-var)
- [Structured logging](https://cloud.google.com/logging/docs/structured-logging)
- [Cloud Scheduler: schedule an HTTP target](https://cloud.google.com/scheduler/docs/creating)
- [Authenticate Scheduler to a private function (OIDC)](https://cloud.google.com/scheduler/docs/http-target-auth)
- [Buildpacks used by Cloud Functions](https://cloud.google.com/docs/buildpacks/overview)

## Related projects in this repo

- [`aws-lambda-basics`](../../../beginner/aws/aws-lambda-basics/README.md) — the AWS equivalent (Lambda + CloudWatch Logs)
- [`aws-lambda-eventbridge-scheduled`](../../../beginner/aws/aws-lambda-eventbridge-scheduled/README.md) — AWS scheduled-Lambda counterpart to Step 5
- [`gcp-cloud-run-artifact-registry`](../../../beginner/gcp/gcp-cloud-run-artifact-registry/README.md) — the Cloud Run service a 2nd-gen function is built on
- **Next:** [`gcp-event-driven-functions-pubsub`](../../../intermediate/gcp/gcp-event-driven-functions-pubsub/README.md)

## Concepts

- **1st vs 2nd gen:** 2nd gen runs on Cloud Run + Eventarc, supporting more event types, request
  concurrency, longer timeouts (up to 60 min), and larger instances. Prefer 2nd gen for new work.
- **Why buildpacks:** you ship source, Google detects Python and containerizes it — no `Dockerfile`
  to maintain for simple functions.
