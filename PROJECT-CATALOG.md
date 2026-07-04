# Project Catalog

The main navigation page for this repo. Pick a project by **level, cloud/tech, domain, time, or
cost** — then jump straight in. The `Order` column is a **suggestion**, not a required path; do
projects in any order you like.

> **Links point to current folders.** Folders haven't moved yet — see
> [docs/repo-migration-plan.md](docs/repo-migration-plan.md) for the target
> `projects/<level>/<tech>/` layout. This catalog will be **auto-generated from project metadata**
> after the move (Phase 5).

**Legend** — Cost: 🟢 free-tier · 🟡 small lab cost · 🔴 real hourly cost (no free tier). Status: ✅ ready.

## All projects

| Order | Level | Cloud/Tech | Domain | Project | Time | Cost | Status |
|------:|-------|-----------|--------|---------|------|------|--------|
| 1 | Beginner | AWS | Serverless | [Lambda Basics](./lambda-basics/README.md) | 45–60m | 🟢 | ✅ |
| 2 | Beginner | AWS | Serverless | [Lambda + S3 Event Processing](./lambda-s3-event-processing/README.md) | 60m | 🟢 | ✅ |
| 3 | Beginner | AWS | Serverless | [Lambda Layers](./lambda-layers/README.md) | 45m | 🟢 | ✅ |
| 4 | Beginner | AWS | Serverless | [Lambda on a Schedule (EventBridge)](./lambda-eventbridge-scheduled/README.md) | 45m | 🟢 | ✅ |
| 5 | Beginner | AWS | Cost-Opt | [Scheduled EC2 Start/Stop](./lambda-ec2-start-stop-scheduler/README.md) | 60m | 🟡 | ✅ |
| 6 | Beginner | AWS | Storage | [Scheduled S3 Housekeeping](./lambda-s3-housekeeping/README.md) | 45m | 🟢 | ✅ |
| 7 | Beginner | AWS | Storage | [S3 + CloudFront Static Website](./s3-cloudfront-static-website/README.md) | 60m | 🟢 | ✅ |
| 8 | Beginner | AWS | Messaging | [SNS + SQS Fanout Messaging](./sqs-sns-iam-messaging/README.md) | 45m | 🟢 | ✅ |
| 9 | Intermediate | AWS | Messaging | [Lambda Triggered by SQS + SNS](./lambda-sqs-sns-trigger/README.md) | 60m | 🟢 | ✅ |
| 10 | Intermediate | AWS | Observability | [Lambda Troubleshooting & Boto3](./lambda-troubleshooting-monitoring/README.md) | 90m | 🟢 | ✅ |
| 11 | Intermediate | AWS | Security-IAM | [IAM Roles & Policies (6 scenarios)](./iam-roles-and-policies/README.md) | 90m | 🟢 | ✅ |
| 12 | Intermediate | AWS | Serverless | [API Gateway REST + Lambda](./api-gateway-rest-lambda/README.md) | 90m | 🟢 | ✅ |
| 13 | Intermediate | AWS | Serverless | [API Gateway HTTP + DynamoDB CRUD](./api-gateway-http-dynamodb-crud/README.md) | 90m | 🟢 | ✅ |
| 14 | Intermediate | AWS | Serverless | [Serverless Monitored Web App](./serverless-monitored-webapp/README.md) | 2–3h | 🟡 | ✅ |
| 15 | Intermediate | AWS | Cost-Opt | [EC2 Compute Rightsizing](./aws-compute-rightsizing/README.md) | 90m | 🟡 | ✅ |
| 16 | Intermediate | AWS | Containers | [ECS Fargate Basics](./ecs-fargate-basics/README.md) | 90m | 🟡 | ✅ |
| 17 | Advanced | AWS | Containers | [ECS Fargate Advanced (ALB/VPC/ASG)](./ecs-fargate-advanced/README.md) | 3h | 🔴 | ✅ |
| 18 | Advanced | AWS | Compute | [EC2 + VPC Monitored Web App](./ec2-vpc-monitored-webapp/README.md) | 3–4h | 🔴 | ✅ |
| 19 | Advanced | AWS | Disaster-Recovery | [RDS Disaster Recovery](./rds-disaster-recovery/README.md) | 3h | 🔴 | ✅ |
| 20 | Advanced | AWS | Migration | [Monolith → Serverless](./monolith-to-serverless-migration/README.md) | 3h | 🟡 | ✅ |
| 21 | Advanced | AWS | Migration | [Database Migration with DMS](./database-migration-dms/README.md) | 3h | 🔴 | ✅ |
| 22 | Advanced | Kubernetes (EKS) | Migration | [Monolith → Microservices on EKS](./monolith-to-microservices-eks/README.md) | 3–4h | 🔴 | ✅ |
| 23 | Advanced | Kubernetes (EKS) | Security-IAM | [IRSA — Service Account Access](./eks-projects/irsa-service-account-access/README.md) | 2h | 🔴 | ✅ |
| 24 | Intermediate | Kubernetes (local) | SRE | [K8s Optimization & Recovery](./k8s-optimization-and-recovery/README.md) | 2–3h | 🟢 | ✅ |
| 25 | Beginner | GCP | Networking | [GCP VPC & Firewall Basics](./gcp-projects/gcp-vpc-firewall-basics/README.md) | 60m | 🟢 | ✅ |
| 26 | Intermediate | GCP | Networking | [GCP HTTP LB & Autoscaling](./gcp-projects/gcp-http-lb-autoscaling/README.md) | 90m | 🔴 | ✅ |

> 🔴 **Real-cost projects** (17, 18, 19, 21, 22, 23, 26): bill per hour with no free-tier umbrella.
> Do the cleanup step **the same day**.

## By level

### Beginner
Start here if you're new to the cloud. Single-service, mostly free-tier.
- 1 Lambda Basics · 2 Lambda + S3 · 3 Lambda Layers · 4 EventBridge Schedule · 5 EC2 Start/Stop · 6 S3 Housekeeping · 7 S3 + CloudFront · 8 SNS + SQS · 25 GCP VPC & Firewall

### Intermediate
Multiple services wired together; some incur small costs.
- 9 Lambda+SQS+SNS · 10 Lambda Troubleshooting · 11 IAM Roles · 12 API GW REST · 13 API GW HTTP+DynamoDB · 14 Serverless Web App · 15 Compute Rightsizing · 16 ECS Fargate Basics · 24 K8s Opt & Recovery · 26 GCP HTTP LB

### Advanced
Full architectures, real cost, production patterns.
- 17 ECS Advanced · 18 EC2+VPC Web App · 19 RDS DR · 20 Monolith→Serverless · 21 DMS · 22 Microservices on EKS · 23 IRSA

## By cloud / technology

### AWS Projects
1–21 (all AWS). Serverless, containers, IAM, messaging, storage, migration, DR, cost-optimization.

### GCP Projects
25 GCP VPC & Firewall Basics · 26 GCP HTTP LB & Autoscaling — the repo's Google Cloud networking labs (`gcloud` CLI, region `us-east1`).

### Kubernetes Projects
24 K8s Optimization & Recovery (local, $0) · 22 Microservices on EKS · 23 IRSA (both real EKS). New to K8s? Do **24** first — it's free and local.

### DevOps Projects
CI/CD + deployment strategies live inside: 14 Serverless Web App & 18 EC2 Web App (GitHub Actions OIDC pipelines), 12/13 API Gateway (rolling/canary/blue-green), 17 ECS Advanced (rolling deploys).

### SRE Projects
24 K8s Optimization & Recovery (HPA, probes, PDB, Velero backup/restore) · 19 RDS DR (RPO/RTO drills).

### Azure Projects
*None yet.* First Azure project lands under `projects/<level>/azure/` — see
[docs/repo-migration-plan.md](docs/repo-migration-plan.md).

### Platform Engineering Projects
*None yet.* Planned — see [docs/repo-migration-plan.md](docs/repo-migration-plan.md).

## Series (do in order)

Some projects are designed as short series. Even when they span levels, the narrative runs in order:

| Series | Projects |
|--------|----------|
| Lambda | 1 → 2 → 3 → 10 |
| Lambda Automation | 4 → 5 → 6 |
| ECS & Fargate | 16 → 17 |
| Web App: Native vs Serverless | 18 (native) ↔ 14 (serverless) |
| API Gateway | 12 → 13 |
| Optimization & Recovery | 15 → 19 → 24 |
| Migration | 20 → 22 → 21 |
