# References — GCP Event-Driven Functions

## Official docs

- [Eventarc overview](https://cloud.google.com/eventarc/docs/overview)
- [Trigger a function from Cloud Storage (Eventarc)](https://cloud.google.com/functions/docs/calling/storage)
- [Trigger a function from Pub/Sub](https://cloud.google.com/functions/docs/calling/pubsub)
- [CloudEvents functions (Python)](https://cloud.google.com/functions/docs/writing/write-event-driven-functions)
- [Eventarc roles & the trust chain](https://cloud.google.com/eventarc/docs/all-roles-permissions)
- [Pub/Sub dead-letter topics](https://cloud.google.com/pubsub/docs/handling-failures)
- [Pub/Sub message ordering](https://cloud.google.com/pubsub/docs/ordering)
- [Firestore Python client](https://cloud.google.com/firestore/docs/quickstart-servers)
- [Retrying event-driven functions](https://cloud.google.com/functions/docs/bestpractices/retries)
- [`Increment` / atomic operations](https://cloud.google.com/firestore/docs/manage-data/add-data#increment_a_numeric_value)

## Related projects in this repo

- **Previous:** [`gcp-cloud-functions-basics`](../../../beginner/gcp/gcp-cloud-functions-basics/README.md) — HTTP functions + scheduling
- **Next:** [`gcp-serverless-workflows-orchestration`](../../../advanced/gcp/gcp-serverless-workflows-orchestration/README.md) — orchestrating functions with Workflows
- AWS counterparts: [`aws-lambda-s3-event-processing`](../../../beginner/aws/aws-lambda-s3-event-processing/README.md), [`aws-sqs-sns-messaging`](../../../beginner/aws/aws-sqs-sns-messaging/README.md), [`aws-lambda-sqs-sns-trigger`](../../../intermediate/aws/aws-lambda-sqs-sns-trigger/README.md)
- Firestore setup also appears in [`gcp-databases-workload-identity`](../../../advanced/gcp/gcp-databases-workload-identity/README.md)

## Concepts

- **Eventarc rides Pub/Sub:** even a "Cloud Storage trigger" is delivered via an Eventarc-managed
  Pub/Sub topic — which is why the trust chain involves Pub/Sub service agents.
- **At-least-once everywhere:** design every event handler to be safely re-runnable.
