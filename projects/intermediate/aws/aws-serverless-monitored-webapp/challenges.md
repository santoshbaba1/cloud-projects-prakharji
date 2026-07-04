# Challenges — Serverless Monitored Web App

Extend the serverless build. Several mirror the EC2 project's challenges so you can compare
how the *same goal* is met in each architecture.

---

## 1. Add real state with DynamoDB
Add a `POST /api/visits` route that increments a counter in a **DynamoDB** table, and `GET
/api/visits` to read it. Grant the execution role `dynamodb:UpdateItem`/`GetItem` on **only
that table's ARN**. *Skills: DynamoDB, least-privilege IAM, stateful serverless.*

## 2. Scale signal: alarm on Throttles
Lambda's elasticity is bounded by **concurrency**. Add an alarm on the `Throttles` metric and
SNS-notify when the function is being throttled. Then raise **reserved concurrency** and
observe. *Skills: Lambda concurrency, Throttles metric.*

## 3. Infrastructure as code with AWS SAM
Re-create the function + HTTP API + alarms with a single **`template.yaml`** and
`sam deploy`. Compare the effort to the click-ops steps. *Skills: AWS SAM, IaC.*

## 4. Cold-start investigation with X-Ray
Enable **AWS X-Ray** active tracing. Hit the API after an idle period and find the cold-start
init segment in the trace. Compare to the duration p95 alarm. *Skills: X-Ray, cold starts.*

## 5. Custom business metric (Embedded Metric Format)
Emit a custom metric (e.g. count of `/api/load` calls) using CloudWatch **Embedded Metric
Format** (structured JSON logs) — no extra API call needed. Alarm on it. *Skills: EMF,
structured logging.* (Mirror of the EC2 project's challenge 4.)

## 6. Canary deploy with Lambda aliases + weighted routing
Publish a **version**, create a `live` **alias**, and shift 10% of traffic to a new version
before going to 100%. *Skills: Lambda versions/aliases, weighted aliases, safe deploys.*

## 7. Same alert, two channels
Add a second SNS subscriber: a small Lambda that posts the alarm to **Slack**. This is the
identical fanout you'd build in the EC2 project's challenge 7 — proving the alerting layer is
portable across architectures. *Skills: SNS fanout, Lambda, secrets.*

---

> Notice how many of these match the EC2 project's challenges. The *application* and the
> *operational goals* are the same — only the AWS primitives differ. That's the whole point
> of building the app twice.
