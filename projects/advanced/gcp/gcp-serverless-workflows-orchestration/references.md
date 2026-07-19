# References — GCP Serverless Orchestration

## Official docs

- [Cloud Workflows overview](https://cloud.google.com/workflows/docs/overview)
- [Workflows syntax reference](https://cloud.google.com/workflows/docs/reference/syntax)
- [Retry & error handling in Workflows](https://cloud.google.com/workflows/docs/reference/syntax/catching-errors)
- [Workflows standard library (`http`, `base64`, `json`)](https://cloud.google.com/workflows/docs/reference/stdlib/overview)
- [Cloud Tasks connector for Workflows](https://cloud.google.com/workflows/docs/reference/googleapis/cloudtasks/v2/Overview)
- [Call a workflow from a function (Executions API)](https://cloud.google.com/workflows/docs/executing-workflow)
- [Cloud Tasks: create HTTP target tasks with OIDC](https://cloud.google.com/tasks/docs/creating-http-target-tasks)
- [API Gateway: get started](https://cloud.google.com/api-gateway/docs/get-started-cloud-functions)
- [API Gateway: authenticate to a backend](https://cloud.google.com/api-gateway/docs/authenticate-service-account)
- [`iam.serviceAccountUser` / actAs](https://cloud.google.com/iam/docs/service-account-permissions#user-role)

## Patterns

- **Saga pattern** — [microservices.io/patterns/data/saga](https://microservices.io/patterns/data/saga.html):
  compensating transactions instead of distributed 2PC.
- **Orchestration vs. choreography** — the two ways to compose services; this project is orchestration,
  the [intermediate project](../../../intermediate/gcp/gcp-event-driven-functions-pubsub/README.md) is
  choreography.

## Related projects in this repo

- **Previous in track:** [`gcp-cloud-functions-basics`](../../../beginner/gcp/gcp-cloud-functions-basics/README.md), [`gcp-event-driven-functions-pubsub`](../../../intermediate/gcp/gcp-event-driven-functions-pubsub/README.md)
- AWS counterparts: [`aws-api-gateway-dynamodb-crud`](../../../intermediate/aws/aws-api-gateway-dynamodb-crud/README.md), [`aws-monolith-to-serverless-migration`](../../../advanced/aws/aws-monolith-to-serverless-migration/README.md)
- API Gateway idea (GCP) also relates to [`gcp-cloud-run-artifact-registry`](../../../beginner/gcp/gcp-cloud-run-artifact-registry/README.md) (the Cloud Run runtime behind functions)

## Concepts

- **AWS analogy:** Cloud Workflows ≈ **Step Functions**; Cloud Tasks ≈ **SQS + a dispatcher**; API
  Gateway ≈ **API Gateway**. The saga/compensation and retry ideas transfer directly.
