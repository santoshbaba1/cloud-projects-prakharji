# Challenges — Monolith → Serverless Migration

Extend the migration. Early ones deepen the serverless build; later ones make the strangler
cutover more production-like.

---

## 1. Add a third slice and strangle it
Add a `reviews` domain to the monolith (`GET/POST /reviews`), then repeat the whole pattern:
`Reviews` table → `BookstoreReviewsRole` → `bookstore-reviews` Lambda → new routes. Prove the
strangler scales to N slices. *Skills: repeatable decomposition.*

## 2. Gradual cutover with Route 53 weighted records
Instead of an all-or-nothing route swap, put both the monolith and the API behind a custom
domain and use **Route 53 weighted records** to send 10% → 50% → 100% of `/books*` traffic to
serverless. *Skills: DNS-based traffic shifting, gradual migration.*

## 3. HTTP_PROXY passthrough for true parallel running
Implement the optional `$default` HTTP_PROXY integration so un-migrated routes transparently
hit the EC2 monolith through the **same** API URL. Migrate one route at a time and confirm the
client never sees a URL change. *Skills: API Gateway HTTP_PROXY, strangler facade.*

## 4. Event-driven fulfilment with DynamoDB Streams
Turn on a **stream** on `Orders` and add a `bookstore-fulfilment` Lambda triggered by it that
"ships" the order (logs / SNS email). The monolith did this inline; now it's asynchronous and
decoupled. *Skills: DynamoDB Streams, event-driven design.*

## 5. Contract tests to guarantee parity
Write a test suite that runs the **same** requests against the monolith URL and the API URL and
asserts identical responses. Run it before every cutover as your go/no-go gate. *Skills:
contract testing, safe migration gates.*

## 6. Infrastructure as Code with AWS SAM
Re-create the tables + both functions + the HTTP API in a single SAM `template.yaml`. Compare
the reproducibility to the click-ops you did here. *Skills: AWS SAM, IaC.*

## 7. Observability for the migration
Add a CloudWatch **dashboard** that overlays monolith `NetworkIn` against API Gateway request
count, so you can literally watch traffic move from the old box to the new front door during
cutover. Add an alarm on Lambda `Errors`. *Skills: CloudWatch dashboards/alarms, migration
observability.*

---

> You migrated by **growing the new system around the old one and retiring it route by route** —
> the Strangler Fig pattern. That's how real monolith-to-serverless migrations ship without a
> scary big-bang weekend. Compare with the container path in
> [monolith-to-microservices-eks](../monolith-to-microservices-eks/README.md): same pattern,
> different runtime.
