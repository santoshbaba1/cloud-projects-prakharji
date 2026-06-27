# Challenges — Monolith → Microservices on EKS

Extend the migration. Early ones deepen the Kubernetes build; later ones make the architecture
production-grade.

---

## 1. One ALB with an Ingress instead of an ELB-per-service
Install the **AWS Load Balancer Controller** and replace the `frontend` LoadBalancer Service
with an **Ingress** that path-routes (`/` → frontend) through a single ALB. Compare cost and
flexibility. *Skills: Ingress, AWS Load Balancer Controller, path routing.*

## 2. Real datastores (true data ownership)
Give `catalog` a DynamoDB table and `orders` its own table (reuse
[api-gateway-http-dynamodb-crud](../api-gateway-http-dynamodb-crud/README.md) patterns) via
**IRSA** (IAM Roles for Service Accounts). Now "database-per-service" is literal, not in-memory.
*Skills: IRSA, DynamoDB, decentralized data.*

## 3. PodDisruptionBudget + self-healing drill
Add a **PDB** so voluntary disruptions (node drain) never take catalog below 1 replica. Drain a
node and watch pods reschedule with no outage. *Skills: PDB, resilience.* (See
[k8s-optimization-and-recovery](../k8s-optimization-and-recovery/README.md).)

## 4. Per-service CI/CD
Wire **GitHub Actions** (OIDC → ECR push → `kubectl set image`) so pushing to `src/catalog`
deploys only `catalog`. Three pipelines, three release cadences — the microservices payoff in
CI. *Skills: GitHub Actions, OIDC, GitOps-lite.*

## 5. Gradual traffic shifting at the edge
Put the frontend behind a custom domain and use **Route 53 weighted records** (or two frontend
Deployments + Service selector tricks) to shift 10% → 50% → 100% during a release. *Skills:
canary at the edge, weighted DNS.*

## 6. Observability across services
Add **Container Insights** (or Prometheus + Grafana) and trace a `/checkout` request as it hops
frontend → orders → catalog. Find the p95 latency added by each network hop. *Skills:
distributed tracing, the true cost of a network call.*

## 7. Service mesh for resilience
Add **App Mesh** (or Istio/Linkerd) to get automatic retries, timeouts, and mTLS between
services — moving the `orders → catalog` failure handling out of app code and into the mesh.
*Skills: service mesh, sidecars, zero-trust networking.*

---

> You split a monolith into independently scaled, independently deployed, self-healing
> Kubernetes microservices — and learned that a service call is a **network** call with its own
> failure modes. Compare with the serverless path in
> [monolith-to-serverless-migration](../monolith-to-serverless-migration/README.md): same
> Strangler Fig pattern, functions instead of containers.
