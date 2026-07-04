# Challenges — API Gateway REST API + Lambda

Extend the project. The first few deepen the REST API itself; the later ones push the
deployment-strategy skills further.

---

## 1. Add DELETE and PUT
Add `DELETE /quotes/{id}` and `PUT /quotes/{id}` methods and the handler logic. Notice how
each new method needs its own integration pointed at the alias. *Skills: REST methods, proxy
routing.*

## 2. Validate requests at the gateway
Attach a **request validator** and a **model** so a `POST /quotes` missing `text` is rejected
by API Gateway *before* it reaches Lambda. Compare to the in-handler 400. *Skills: API Gateway
models, request validation.*

## 3. Rate-limit with a usage plan + API key
Create a **usage plan** (e.g. 10 req/s, 1000/day), an **API key**, and require the key on the
methods. Test that the 11th rapid request gets throttled. *Skills: usage plans, API keys,
throttling.*

## 4. Automate the rolling deploy
Write a Boto3 script that publishes a new version and steps the `live` alias 10 → 25 → 50 →
100, pausing to check the Lambda `Errors` metric between steps and aborting if it's non-zero.
This is a hand-rolled deployment controller. *Skills: Boto3, CloudWatch GetMetricData, safe
deploys.*

## 5. Canary with an automatic rollback signal
Put a **CloudWatch alarm** on the Lambda `Errors` metric. During a canary, if the alarm fires,
script the removal of `canarySettings`. *Skills: alarms, canary automation.*

## 6. Blue-green with a custom domain
Add an **API Gateway custom domain** + **ACM** certificate, map the base path to the `prod`
stage, and do blue-green by **remapping the base path** between two stages instead of flipping
a stage variable. *Skills: custom domains, ACM, base-path mapping.*

## 7. Compare with Project 2
Build [api-gateway-http-dynamodb-crud](../aws-api-gateway-dynamodb-crud/README.md) and write a
short note: which deployment strategy felt cleaner on REST (gateway canary) vs HTTP (alias
only), and why. *Skills: architecture trade-offs.*

---

> The big idea: you implemented rolling, canary, and blue-green **by hand** with native
> primitives. Tools like AWS CodeDeploy and SAM automate exactly these moves — now you know
> what they're doing under the hood.
