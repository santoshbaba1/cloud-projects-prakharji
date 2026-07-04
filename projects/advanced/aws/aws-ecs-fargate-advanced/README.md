# ECS Fargate Advanced — Production-Grade Container Deployment

```yaml
level: advanced
cloud: aws
domain: containers
technology:
  - ecs
  - fargate
  - ecr
  - alb
  - vpc
  - iam
  - cloudwatch
  - auto-scaling
estimated_time: 3 hours
estimated_cost: hourly
deployment_type: console + cli
cleanup_required: true
status: ready
```

## What You'll Build

You will deploy a production-ready containerized Python Flask application on **Amazon ECS with Fargate**, fronted by an **Application Load Balancer (ALB)**, with **Auto Scaling**, **CloudWatch Container Insights**, and proper **VPC networking**. Every IAM permission is explicitly defined and explained.

By the end of this project you will understand:

- How to design a VPC with public subnets for a Fargate-based workload
- Every IAM role and policy involved in an ECS deployment — and why each permission exists
- How to build a production Dockerfile with a non-root user
- How to use Docker Compose for local development and testing
- How to register a multi-container-ready Task Definition with environment variables and health checks
- How to create an ECS Service that keeps N tasks always running
- How to put an Application Load Balancer in front of your ECS Service
- How to configure ECS Service Auto Scaling based on CPU utilization
- How to use CloudWatch Container Insights for metrics and log querying
- How to tear everything down cleanly

---

## Architecture Diagram

```
                         ┌──────────────────────────────────────────────────┐
                         │                  Your AWS Account                 │
                         │                                                    │
                         │   ┌──────────────────────────────────────────┐   │
                         │   │          VPC: 10.0.0.0/16                │   │
                         │   │                                          │   │
                         │   │   Availability Zone A    AZ B            │   │
                         │   │   ┌────────────────┐ ┌────────────────┐  │   │
                         │   │   │ Public Subnet  │ │ Public Subnet  │  │   │
                         │   │   │ 10.0.1.0/24   │ │ 10.0.2.0/24   │  │   │
                         │   │   │                │ │                │  │   │
                         │   │   │ ┌──────────┐   │ │ ┌──────────┐  │  │   │
                         │   │   │ │ECS Task 1│   │ │ │ECS Task 2│  │  │   │
                         │   │   │ │(Flask)   │   │ │ │(Flask)   │  │  │   │
                         │   │   │ │port 5000 │   │ │ │port 5000 │  │  │   │
                         │   │   │ └────┬─────┘   │ │ └────┬─────┘  │  │   │
                         │   │   └──────│──────────┘ └──────│────────┘  │   │
                         │   │          │    ┌──────────────┘            │   │
                         │   │          ▼    ▼                           │   │
                         │   │   ┌──────────────────┐                   │   │
                         │   │   │  Target Group    │                   │   │
                         │   │   │  port 5000       │                   │   │
                         │   │   └────────┬─────────┘                   │   │
                         │   │            │                              │   │
                         │   │   ┌────────▼─────────┐                   │   │
                         │   │   │  Application     │                   │   │
                         │   │   │  Load Balancer   │                   │   │
                         │   │   │  (Internet-facing│                   │   │
                         │   │   │   port 80)       │                   │   │
                         │   │   └────────┬─────────┘                   │   │
                         │   └────────────│─────────────────────────────┘   │
                         │                │                                  │
                         └────────────────│──────────────────────────────────┘
                                          │ HTTP
                                          ▼
                                    Internet Users
                                    (your browser)

  Supporting Services
  ┌─────────────────────────────────────────────────────────────────────┐
  │  ECR Public  →  ECS pulls image at task start                       │
  │  CloudWatch Logs  →  All container stdout goes here automatically   │
  │  CloudWatch Container Insights  →  CPU/Memory metrics per task      │
  │  Application Auto Scaling  →  Scales task count 1–4 on CPU %       │
  │  IAM  →  Two roles: Task Execution Role + Task Role                 │
  └─────────────────────────────────────────────────────────────────────┘
```

---

## Services Used

| Service | Role in This Project | Why It's Needed |
|---------|---------------------|-----------------|
| **Amazon VPC** | Custom network with 2 public subnets | Isolates resources; ALB requires subnets in 2+ AZs |
| **Amazon ECR Public** | Stores the Docker image | Publicly accessible; no auth needed to pull |
| **Amazon ECS** | Runs and manages containers | Container orchestration control plane |
| **AWS Fargate** | Serverless compute for ECS tasks | No EC2 to provision or patch |
| **Application Load Balancer** | Distributes traffic across ECS tasks | High availability; single DNS endpoint for users |
| **AWS IAM** | Two roles: Execution Role + Task Role | Principle of least privilege for every action |
| **Amazon CloudWatch Logs** | Container log storage | Captures all app output automatically |
| **CloudWatch Container Insights** | CPU/Memory metrics per task | Enables scaling policies and dashboards |
| **Application Auto Scaling** | Scales task count automatically | Handles traffic spikes without manual intervention |

---

## IAM Roles — Full Breakdown

This project uses **two separate IAM roles**. Understanding the difference is critical.

### Role 1: ECS Task Execution Role

**Who uses it:** The ECS control plane (the `ecs-tasks.amazonaws.com` service), not your application code.

**When it's used:** At task startup — ECS uses this role to pull the container image and create the CloudWatch log group.

**Permissions required:**

| Permission | Service | Why It's Needed |
|------------|---------|-----------------|
| `ecr:GetAuthorizationToken` | ECR | Get a temporary auth token to pull the image |
| `ecr:BatchCheckLayerAvailability` | ECR | Verify image layers exist before pulling |
| `ecr:GetDownloadUrlForLayer` | ECR | Download each layer of the image |
| `ecr:BatchGetImage` | ECR | Retrieve the full image manifest |
| `logs:CreateLogGroup` | CloudWatch | Create the log group if it doesn't exist |
| `logs:CreateLogStream` | CloudWatch | Create a log stream for this task instance |
| `logs:PutLogEvents` | CloudWatch | Write log lines to the stream |

> **Managed Policy used:** `AmazonECSTaskExecutionRolePolicy` — covers all of the above exactly.

**Trust Policy:** Allows `ecs-tasks.amazonaws.com` to assume this role.

---

### Role 2: ECS Task Role

**Who uses it:** Your application code running inside the container.

**When it's used:** Any time your app calls an AWS API (S3, DynamoDB, SSM, etc.) using boto3 or the AWS SDK.

**Permissions in this project:** This role has **no permissions** in the basic version — our Flask app does not call any AWS services. It is defined here so you know where to add permissions when your app needs them.

> **How to add permissions:** Attach a policy to this role — for example, if the app reads from S3, attach a policy with `s3:GetObject` on the specific bucket.

**Why keep them separate?** The Execution Role is infrastructure-level. The Task Role is application-level. Mixing them would give your application code unnecessary infrastructure permissions (like the ability to pull any ECR image), violating least privilege.

---

## Project Structure

```
ecs-fargate-advanced/
├── README.md                           ← You are here
├── Dockerfile                          ← Production Dockerfile (non-root user, layered caching)
├── docker-compose.yml                  ← Local development setup
├── src/
│   ├── app.py                          ← Flask app with / /health /info endpoints
│   └── requirements.txt               ← Python dependencies
├── steps/
│   ├── 01-vpc-networking.md            ← Create VPC, subnets, IGW, route tables
│   ├── 02-iam-roles-permissions.md     ← Create Execution Role and Task Role
│   ├── 03-ecr-public-repo.md          ← Create ECR Public repository
│   ├── 04-docker-build-push.md        ← Build, tag, and push the Docker image
│   ├── 05-ecs-cluster.md              ← Create ECS Cluster with Container Insights
│   ├── 06-task-definition.md          ← Register Task Definition with logging config
│   ├── 07-alb-target-group.md         ← Create ALB, listener, and target group
│   ├── 08-ecs-service.md              ← Create ECS Service with ALB integration
│   ├── 09-auto-scaling.md             ← Configure step scaling policies
│   ├── 10-monitoring-logging.md       ← CloudWatch dashboards and log queries
│   └── 11-cleanup.md                  ← Tear down all resources in correct order
├── costs.md                           ← Service-by-service cost breakdown with formulas
├── troubleshooting.md
└── challenges.md
```

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| AWS account | Console access with permissions for ECS, ECR, EC2 (VPC/ALB/SG), IAM, CloudWatch |
| AWS CLI | `aws --version` → 2.x |
| Docker | `docker --version`; Docker daemon running locally |
| Docker Compose | `docker compose version` → v2.x (built into Docker Desktop) |
| Region | All steps use **us-east-1** |
| Completed | [ECS Fargate Basics](../../../intermediate/aws/aws-ecs-fargate-basics/README.md) — concepts from that project are not re-explained here |

---

## What You'll Learn Step by Step

| Step | File | Goal |
|------|------|------|
| 1 | `01-vpc-networking.md` | Build the VPC, 2 public subnets, Internet Gateway, route tables |
| 2 | `02-iam-roles-permissions.md` | Create the Task Execution Role and Task Role with exact permissions |
| 3 | `03-ecr-public-repo.md` | Create ECR Public repo; authenticate Docker with AWS |
| 4 | `04-docker-build-push.md` | Build production image, test locally with Docker Compose, push to ECR |
| 5 | `05-ecs-cluster.md` | Create ECS cluster with Container Insights enabled |
| 6 | `06-task-definition.md` | Register a Task Definition with env vars, health check, and log config |
| 7 | `07-alb-target-group.md` | Create ALB, target group, listener, and security groups |
| 8 | `08-ecs-service.md` | Launch ECS Service connected to ALB; verify traffic flows |
| 9 | `09-auto-scaling.md` | Add step scaling: scale out at 60% CPU, scale in at 20% CPU |
| 10 | `10-monitoring-logging.md` | Explore Container Insights, write CloudWatch Logs Insights queries |
| 11 | `11-cleanup.md` | Delete all resources in correct dependency order |

Start with **Step 1 →** [`steps/01-vpc-networking.md`](steps/01-vpc-networking.md)

---

## Estimated Time

3 – 4 hours for a first-time learner.

## Estimated Cost

| Service | Configuration | Cost per Hour | Notes |
|---------|--------------|---------------|-------|
| **AWS Fargate** | 2 tasks · 0.5 vCPU · 1 GB each | **~$0.049/hr** | Charged per task while RUNNING |
| **Application Load Balancer** | 1 ALB · minimal traffic | **~$0.008/hr** | Fixed charge even with zero requests |
| **CloudWatch Container Insights** | 2 tasks · metrics | **~$0.001/hr** | Negligible at learning scale |
| **Amazon ECR Public** | Image push + pull | **Free** | Always free |
| **Amazon CloudWatch Logs** | Container stdout | **Free** | Within 5 GB/month free tier |
| **VPC, IAM, Auto Scaling, ECS** | Control plane | **Free** | No charge for these services |

**Typical session cost (4 hours): ~$0.24**  
**If left running 24 hours: ~$1.38** ⚠️

> ⚠️ The ALB charges **$0.008/hour even with zero traffic**. Delete it immediately after testing — it costs ~$5.76/month if forgotten. Always complete [Step 11 — Cleanup](steps/11-cleanup.md).

For a full service-by-service breakdown, pricing formulas, Fargate Spot savings, free tier details, and monthly "left running" scenarios → see **[costs.md](costs.md)**.

---

## What's Next

- Add HTTPS to the ALB with an **ACM certificate**
- Move ECS tasks to **private subnets** with a NAT Gateway
- Add an **Amazon RDS** database and pass the connection string via **AWS Secrets Manager**
- Build a **CI/CD pipeline** with GitHub Actions to auto-deploy on push
