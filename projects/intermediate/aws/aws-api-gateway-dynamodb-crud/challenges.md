# Challenges — API Gateway HTTP API + Lambda + DynamoDB

Extend the project. Early ones deepen the CRUD/HTTP-API skills; later ones push the
alias-level deployment work further.

---

## 1. Protect writes with JWT authorization
HTTP APIs support a **JWT authorizer** natively. Add one (e.g. Cognito or any OIDC provider)
and require it on `POST`/`PUT`/`DELETE` while leaving `GET` public. *Skills: HTTP API
authorizers, OIDC/JWT.*

## 2. Query by status with a GSI
`GET /tasks` does a full `Scan`. Add a **Global Secondary Index** on `done` and a
`GET /tasks?done=true` route that `Query`s the index instead. Compare cost/latency.
*Skills: DynamoDB GSI, Query vs Scan.*

## 3. Conditional writes (no lost updates)
Make `PUT` use a **condition expression** (`attribute_exists(id)`) so updating a deleted task
fails cleanly, and add optimistic locking with a `version` attribute. *Skills: DynamoDB
condition expressions, concurrency.*

## 4. Automate canary promotion with Boto3
Script the canary: set `live` to 10% v2, sleep, read the `Errors` metric for `tasks-api:2`
via CloudWatch, then **promote** (live → v2) if zero or **abort** (live → v1) otherwise. This
is a hand-built deployment controller — exactly what CodeDeploy automates. *Skills: Boto3,
CloudWatch GetMetricData, safe deploys.*

## 5. Blue-green safe schema change
Ship a green version that adds a `priority` attribute. Prove that rolling back to blue still
works (blue ignores the new attribute) — then ship a *breaking* change and watch it fail on
rollback. Write up the lesson. *Skills: backward-compatible schema evolution.*

## 6. Add structured request logging
Enable **HTTP API access logs** to CloudWatch with a JSON log format capturing method, path,
status, and latency. Build a Log Insights query for the p95 latency per route. *Skills: access
logging, Log Insights.*

## 7. Infrastructure as code
Re-create the table + function + HTTP API + alias with **AWS SAM** (`template.yaml`) and use
SAM's `AutoPublishAlias` + `DeploymentPreference` to do a canary automatically. Compare to the
manual alias commands you ran here. *Skills: AWS SAM, IaC, managed deploys.*

---

> You did rolling, canary, and blue-green **by hand** at the alias level — the most portable
> serverless deployment technique. Project 1 showed the REST-API gateway-canary alternative;
> together they cover the full deployment-strategy toolkit without any CI/CD framework hiding
> the mechanics.
