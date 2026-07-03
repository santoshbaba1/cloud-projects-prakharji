# GCP Projects

Hands-on projects focused on **Google Cloud Platform** networking — the same build-it-yourself,
step-by-step style as the rest of this repo, but on GCP instead of AWS. Every step gives you both a
**Console (web UI)** path and a **gcloud CLI** path.

> **New to GCP?** Start with the **beginner** project below — its
> [Step 1](./gcp-vpc-firewall-basics/steps/01-install-gcloud.md) installs and authenticates the
> `gcloud` CLI and creates your project. Do it before the intermediate project.

> **Coming from the AWS projects?** A GCP **VPC is global** (only subnets are regional), firewalls
> are **default-deny ingress** and target **network tags**, and the equivalent of an ALB + Auto
> Scaling Group is a **Managed Instance Group + Application Load Balancer**. The concepts rhyme; the
> names differ.

## Projects

| # | Level | Project | Services | Description |
|---|-------|---------|----------|-------------|
| 1 | Beginner | [VPC & Firewall Basics](./gcp-vpc-firewall-basics/README.md) | VPC, Subnets, Firewall, Compute Engine | Install & authenticate the gcloud CLI, then build a custom VPC with two subnets, three firewall rules, and two VMs — and prove it works with SSH, private ping, a web page, and watching the firewall block traffic |
| 2 | Intermediate | [HTTP Load Balancer & Autoscaling](./gcp-http-lb-autoscaling/README.md) | VPC, Cloud NAT, Instance Templates, MIG, Health Checks, Application LB | Put **private** autoscaling VMs behind a **global HTTP load balancer**, give them outbound via **Cloud NAT**, then load-test to scale out and kill a VM to watch it self-heal |

## Cost & Cleanup

- **Project 1** is essentially free (`e2-micro` free tier) — **$0.00–$0.05** if you clean up.
- **Project 2** has **no free-tier umbrella** — the load balancer and Cloud NAT bill per hour. Budget
  **$0.20–$0.60** and delete everything the same day.
- Every project ends with a **cleanup step** and a `costs.md`. Do the cleanup.

## Prerequisites

- A Google account with a **billing account** linked (a new-user free-trial credit is fine).
- The **gcloud CLI** — installed in
  [Project 1, Step 1](./gcp-vpc-firewall-basics/steps/01-install-gcloud.md).
- All steps use region **`us-east1`** / zone **`us-east1-b`**.

## How these relate to the rest of the repo

- **AWS networking equivalent:** [ec2-vpc-monitored-webapp](../ec2-vpc-monitored-webapp/README.md)
  builds a comparable web tier (VPC + ALB + Auto Scaling) on AWS — a good side-by-side.
- **IAM/OIDC fundamentals** carry over from [iam-roles-and-policies](../iam-roles-and-policies/README.md).
