# AWS Hands-On Projects

A collection of **24 hands-on projects** designed for students to build real-world cloud skills through guided, step-by-step exercises — mostly in their own AWS accounts, plus local Kubernetes labs.

> 🚀 **First time here? Start with [SETUP.md](SETUP.md)** — it installs every tool you need
> (AWS CLI, Python, Git, Docker, …) with steps for **Linux, macOS, and Windows**.

## Projects

### IAM & Security

| Project | Services | Description |
|---------|----------|-------------|
| [IAM Roles & Policies](./iam-roles-and-policies/README.md) | IAM, STS, Lambda, EC2, ECS | Master trust vs. permission policies by building six real-world roles: user-assumed via CLI/STS, Lambda/EC2/ECS service roles, cross-account with External ID, and GitHub OIDC federation |

### Storage & CDN

| Project | Services | Description |
|---------|----------|-------------|
| [S3 + CloudFront Static Website](./s3-cloudfront-static-website/README.md) | S3, CloudFront, OAC, IAM | Host a static site in a private S3 bucket served globally over HTTPS via CloudFront; learn origin access control, default root object, custom error pages, caching, and cache invalidation |

### Messaging & Queuing

| Project | Services | Description |
|---------|----------|-------------|
| [Event-Driven Messaging with SNS & SQS](./sqs-sns-iam-messaging/README.md) | SNS, SQS, IAM | Build a fanout messaging system using pub/sub architecture |
| [Lambda Triggered by SQS with SNS Notification](./lambda-sqs-sns-trigger/README.md) | Lambda, SQS, SNS, IAM, CloudWatch | Build a serverless order-processing pipeline: SQS triggers Lambda, Lambda publishes results to SNS |

### Lambda Series (Beginner → Advanced)

Work through these four projects in order. Each builds on the previous.

| # | Project | Services | Description |
|---|---------|----------|-------------|
| 1 | [Lambda Basics](./lambda-basics/README.md) | Lambda, IAM, CloudWatch | Deploy your first Lambda, understand handlers, invoke via Console/CLI/Boto3, and read CloudWatch Logs |
| 2 | [Lambda with S3 Event Processing](./lambda-s3-event-processing/README.md) | Lambda, S3, IAM, CloudWatch | Trigger Lambda automatically on S3 uploads; process text/CSV files and write results to a destination bucket |
| 3 | [Lambda Layers](./lambda-layers/README.md) | Lambda, IAM, CloudWatch | Package third-party libraries (`requests`, `pandas`) as reusable Lambda Layers; attach multiple layers to one function |
| 4 | [Lambda Troubleshooting & Boto3 Automation](./lambda-troubleshooting-monitoring/README.md) | Lambda, S3, EC2, SQS, CloudWatch, Log Insights | Debug 8 failure scenarios, master Log Insights queries, configure DLQs, and automate EC2/S3/SQS with Boto3 |

### Lambda Automation Series (Beginner)

Three short, beginner-friendly projects that all share one idea: **run Lambda on a schedule
with Amazon EventBridge** (a serverless cron job). Start with Project 1 — it teaches the
scheduling pattern the other two reuse to automate real chores. Each is fully hands-on with a
`DRY_RUN` safety switch where it matters.

| # | Project | Services | Description |
|---|---------|----------|-------------|
| 1 | [Lambda on a Schedule with EventBridge](./lambda-eventbridge-scheduled/README.md) | Lambda, EventBridge, CloudWatch, SNS | Learn the scheduling pattern itself: an EventBridge `rate`/`cron` rule fires a heartbeat Lambda that logs and (optionally) emails you via SNS; add a missed-run alarm |
| 2 | [Scheduled EC2 Start/Stop](./lambda-ec2-start-stop-scheduler/README.md) | Lambda, EventBridge, EC2, IAM, CloudWatch | Save money: two schedules pass `{"action":"stop"}` / `{"action":"start"}` to one tag-driven Lambda that powers idle EC2 off overnight — with a tag-gated IAM policy and `DRY_RUN` |
| 3 | [Scheduled S3 Housekeeping](./lambda-s3-housekeeping/README.md) | Lambda, EventBridge, S3, IAM, CloudWatch | Keep a bucket tidy: a daily Lambda archives (or deletes) objects older than a retention window using a paginator, with `archive`-before-`delete` safety and a Lambda-vs-Lifecycle discussion |

### ECS & Fargate Series (Beginner → Advanced)

Work through these two projects in order. Project 1 covers fundamentals; Project 2 builds a production-grade deployment.

| # | Project | Services | Description |
|---|---------|----------|-------------|
| 1 | [ECS Fargate Basics](./ecs-fargate-basics/README.md) | ECS, Fargate, ECR Public, IAM, CloudWatch | Containerize a Flask app, push to ECR Public, run as a Fargate task — understand ECS fundamentals |
| 2 | [ECS Fargate Advanced](./ecs-fargate-advanced/README.md) | ECS, Fargate, ECR Public, ALB, VPC, IAM, CloudWatch, Auto Scaling | Production-grade deployment: VPC networking, Application Load Balancer, rolling deployments, Auto Scaling, Container Insights, Docker Compose |

### Web App Architecture — Native vs. Serverless (Beginner → Advanced)

Build the **same monitored web application twice** — once on native AWS, once serverless —
to compare cost, operations, scaling, and observability. Each is a complete, end-to-end
cloud architecture with monitoring, alerting, audit, and a GitHub Actions CI/CD pipeline.

| # | Project | Services | Description |
|---|---------|----------|-------------|
| 1 | [EC2 + VPC Monitored Web App](./ec2-vpc-monitored-webapp/README.md) | EC2, VPC, ALB, Auto Scaling, CloudWatch, SNS, CloudTrail, IAM, SSM, GitHub Actions | Full native architecture: custom VPC (public/private subnets, NAT), EC2 fleet behind an ALB with Auto Scaling, CloudWatch metrics/alarms/dashboards, SNS email alerts, CloudTrail audit, Boto3 monitoring automation, and an OIDC→SSM deploy pipeline |
| 2 | [Serverless Monitored Web App](./serverless-monitored-webapp/README.md) | API Gateway, Lambda, CloudWatch, SNS, CloudTrail, IAM, GitHub Actions | The same app with no servers: API Gateway + Lambda, the same CloudWatch/SNS/CloudTrail observability, Boto3 automation, and an OIDC→`update-function-code` pipeline — with a side-by-side native-vs-serverless comparison |

### API Gateway Series (Beginner → Intermediate)

Two projects that build an API on **API Gateway + Lambda**, then teach the part most tutorials
skip: **how to ship a new version safely.** Each covers **rolling**, **canary**, and
**blue-green** deployments using only **native** Lambda + API Gateway primitives — no
CodeDeploy — so you can see exactly what each strategy does. Build both to compare REST vs HTTP
APIs and gateway-level vs alias-level deploys.

| # | Project | Services | Description |
|---|---------|----------|-------------|
| 1 | [API Gateway REST API + Lambda](./api-gateway-rest-lambda/README.md) | API Gateway (REST), Lambda, IAM, CloudWatch | Build a Quotes API with REST resources/methods + proxy integration and a deployment stage, then ship v2 three ways: **rolling** (weighted Lambda alias), **canary** (API Gateway's native gateway-level canary release), and **blue-green** (instant stage-variable flip + rollback) |
| 2 | [API Gateway HTTP API + Lambda + DynamoDB](./api-gateway-http-dynamodb-crud/README.md) | API Gateway (HTTP), Lambda, DynamoDB, IAM, CloudWatch | Build a full CRUD Tasks API (GET/POST/PUT/DELETE) on the cheaper HTTP API with durable DynamoDB state, then do **rolling / canary / blue-green** entirely at the **Lambda-alias** level (HTTP API has no gateway canary) — repointing the integration for an atomic cutover |

> The existing [Serverless Monitored Web App](./serverless-monitored-webapp/README.md) also
> ships a [deployment-strategies.md](./serverless-monitored-webapp/deployment-strategies.md)
> guide to apply these same techniques to that app.

### Optimization & Recovery Series

Three projects on one theme: **keeping cloud systems lean and resilient.** Two cover AWS, one
covers Kubernetes. Each is hands-on, with a safety switch (`DRY_RUN` / verify-before-act) wherever
something can change or delete infrastructure. Together they cover rightsizing compute,
disaster-recovery for databases, and both halves at once on Kubernetes.

| # | Project | Services | Description |
|---|---------|----------|-------------|
| 1 | [EC2 Compute Rightsizing](./aws-compute-rightsizing/README.md) | Lambda, EventBridge, EC2, CloudWatch, SNS, Compute Optimizer | **Optimization.** A scheduled Lambda reads each instance's CloudWatch CPU, labels it idle/over-provisioned/right-sized, emails an SNS report, and (opt-in, tag-gated) resizes via stop→modify→start — then compares your logic to AWS Compute Optimizer |
| 2 | [RDS Disaster Recovery](./rds-disaster-recovery/README.md) | RDS, EC2 (SG), KMS, two regions | **Recovery.** Seed a MySQL DB, then recover it four ways — point-in-time restore, manual snapshot, cross-region snapshot copy, and a cross-region read-replica failover — measuring RPO/RTO for each |
| 3 | [Kubernetes Optimization & Recovery](./k8s-optimization-and-recovery/README.md) | kind/minikube, metrics-server, HPA, Velero, MinIO | **Both, on Kubernetes (local, $0).** Right-size with requests/limits, autoscale with an HPA, self-heal with probes + a PDB, then back up the namespace with Velero, delete it, and restore it |

### Migration Series

Three projects on one theme: **moving a workload from one architecture to a better-fit one**,
each mapped to AWS's **6 R's** (Refactor, Refactor, Replatform) and driven by the **Strangler
Fig** / **full-load + CDC** patterns. Every step is manual (Console + CLI) so you see each moving
part. Each README spells out *why* the target architecture is better, *what type* of migration it
is, and *which principles* apply.

| # | Project | Services | Description |
|---|---------|----------|-------------|
| 1 | [Monolith → Serverless](./monolith-to-serverless-migration/README.md) | EC2, Lambda, API Gateway (HTTP), DynamoDB, IAM | **Refactor.** Run a Flask + SQLite monolith on EC2, then strangle it route-by-route into two domain Lambdas (catalog/orders) + DynamoDB behind an HTTP API — migrating data and traffic with no big-bang cutover, then retire the EC2 box |
| 2 | [Monolith → Microservices on EKS](./monolith-to-microservices-eks/README.md) | EKS, ECR, ELB, EC2, IAM | **Refactor.** Decompose a single container into `catalog`/`orders`/`frontend` microservices on Kubernetes — service-to-service DNS, ConfigMaps, probes, **HPA**, rolling updates, self-healing — then cut over from the monolith. ⚠️ Real EKS cost; $0 local `kind` alternative included |
| 3 | [Database Migration with DMS](./database-migration-dms/README.md) | DMS, RDS (MySQL), EC2, VPC, IAM | **Replatform.** Migrate a live self-managed MySQL to managed RDS with **full load + CDC** for near-zero downtime — replication instance, endpoints, validation, and a clean parity-checked cutover (RPO/RTO) |

### EKS Projects

Projects in the [`eks-projects/`](./eks-projects/README.md) directory focus on **Amazon EKS**
security, identity, and operations. ⚠️ Each runs a real EKS control plane (**$0.10/hr**, no free
tier) — delete the cluster the same day. New to Kubernetes? Do the free local lab in
[k8s-optimization-and-recovery](./k8s-optimization-and-recovery/README.md) first.

| # | Project | Services | Description |
|---|---------|----------|-------------|
| 1 | [IRSA — Service Account Access](./eks-projects/irsa-service-account-access/README.md) | EKS, IAM, STS, OIDC, S3 | Give a pod AWS permissions via a ServiceAccount with **IRSA** (OIDC trust, zero stored keys) end-to-end — cluster OIDC provider, trust + permission policies, SA annotation, verified pod — then scope a teammate to one namespace with **RBAC + access entries**. Rich diagrams explaining *what OIDC/IRSA/ServiceAccounts are* and the full creation flow |

---

## How This Repo Is Organized

Each project lives in its own directory and follows a consistent layout:

```
project-name/
├── README.md           # Architecture overview and what you'll build
├── Dockerfile          # (container projects) How to build the image
├── docker-compose.yml  # (advanced container projects) Local dev setup
├── steps/              # Numbered, sequential step files
│   ├── 01-*.md
│   ├── 02-*.md
│   └── ...
├── src/                # Application source code
├── troubleshooting.md  # Common errors and fixes
└── challenges.md       # Extra challenges to deepen understanding
```

## Prerequisites (All Projects)

- An active AWS account with console access
- A user or role with sufficient permissions (each project specifies exactly what's needed)
- Basic familiarity with the AWS Management Console
- The required tooling installed on your laptop — see **[SETUP.md](SETUP.md)** for
  AWS CLI, Python, Git, Docker, and more, with **Linux / macOS / Windows** instructions

## Contributing a New Project

1. Create a new directory using kebab-case naming (e.g., `s3-static-website`)
2. Follow the directory structure above
3. Add an entry to the table in this README
4. Keep steps atomic — one concept per file
