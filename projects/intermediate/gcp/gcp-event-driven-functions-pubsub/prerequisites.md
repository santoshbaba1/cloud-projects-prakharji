# Prerequisites — GCP Event-Driven Functions

Everything you need before **Step 1**.

## Prior project

Do [`gcp-cloud-functions-basics`](../../../beginner/gcp/gcp-cloud-functions-basics/README.md) first.
This project assumes you can deploy a 2nd-gen function and read logs, and does not re-explain those.

## Account & billing

- A **Google Cloud project** with a **billing account linked**. Costs stay in free tiers, but
  Functions/Eventarc/Pub/Sub require billing enabled.

## Tools

| Tool | Version | Check |
|------|---------|-------|
| gcloud CLI | ≥ 470 | `gcloud version` |
| gsutil (bundled with gcloud) | — | `gsutil version` |
| Python | 3.12 | only for optional local testing |

## Permissions

Owner/Editor is simplest. Least-privilege additions beyond the beginner project:

| Role | Why |
|------|-----|
| `roles/eventarc.admin` | Create/inspect Eventarc triggers |
| `roles/pubsub.admin` | Create the topic, subscription, and dead-letter topic |
| `roles/storage.admin` | Create the inbox bucket |
| `roles/datastore.owner` | Create the Firestore DB and read/write documents |
| `roles/iam.serviceAccountAdmin` | Create the `order-fns-sa` runtime service account |
| `roles/resourcemanager.projectIamAdmin` | Grant the trust-chain roles in Step 3 |

## One-per-project resources

- **Firestore** has a single database per project. If you've already done
  [`gcp-databases-workload-identity`](../../../advanced/gcp/gcp-databases-workload-identity/README.md)
  (which uses a `carts` collection), the DB already exists — this project just adds `orders` and
  `stats` collections to it. Step 1 handles both cases.

## Region

All resources use **`us-east1`**. Eventarc, the bucket, the topic, and both functions must share the
region (or the bucket be in a compatible location) for the GCS trigger to work.
