# Prerequisites — GCP Serverless Orchestration

Everything you need before **Step 1**.

## Prior projects

Do these first — this capstone assumes both:

- [`gcp-cloud-functions-basics`](../../../beginner/gcp/gcp-cloud-functions-basics/README.md) — you can deploy and invoke a 2nd-gen function
- [`gcp-event-driven-functions-pubsub`](../../../intermediate/gcp/gcp-event-driven-functions-pubsub/README.md) — you've wired a multi-service IAM chain (Eventarc trust chain), which is excellent prep for this project's identity chain

## Account & billing

- A **Google Cloud project** with a **billing account linked**. Unlike the earlier serverless
  projects, **API Gateway has no free tier**, so this lab costs a small amount (pennies for a few
  calls). See [costs.md](costs.md).

## Tools

| Tool | Version | Check |
|------|---------|-------|
| gcloud CLI | ≥ 470 | `gcloud version` |
| A JSON tool | any | `python3 -m json.tool` used to pretty-print |
| `envsubst` (from gettext) or `sed` | any | Step 4 substitutes URLs into the workflow YAML |

## Permissions

Owner/Editor is simplest for a lab. Least-privilege additions beyond the earlier projects:

| Role | Why |
|------|-----|
| `roles/workflows.admin` | Create and manage the workflow |
| `roles/cloudtasks.admin` | Create the shipping queue |
| `roles/apigateway.admin` | Create the API, config, and gateway |
| `roles/iam.serviceAccountAdmin` | Create the four service accounts |
| `roles/resourcemanager.projectIamAdmin` | Grant the invoker/enqueuer/actAs roles |
| `roles/serviceusage.serviceUsageAdmin` | Enable the APIs |

## Concepts assumed

- You're comfortable with **OIDC service-account auth** between Google services (the intermediate
  project introduced it via Eventarc).
- You can read a Mermaid flowchart — [architecture.md](architecture.md) leans on them heavily.

## Region

All resources use **`us-east1`**. API Gateway is regional; the functions, workflow, and queue all
live in the same region.
