# EKS Projects

Hands-on projects focused on **Amazon EKS** (managed Kubernetes) — the security, identity, and
operational patterns you need to run real workloads on a cluster.

> ⚠️ **EKS is not free.** Every project here runs a real EKS control plane (**$0.10/hr**, no free
> tier) plus worker nodes. Budget **$1–3** per afternoon and **delete the cluster the same day** (the
> last step of each project). Each project README has a cost summary and a `costs.md`.

> **New to Kubernetes?** Do the free local lab in
> [k8s-optimization-and-recovery](../k8s-optimization-and-recovery/README.md) first (kubectl,
> namespaces, pods, HPA on `kind`/`minikube`, $0). Then come here for the AWS-specific pieces.

## Projects

| # | Project | Services | Description |
|---|---------|----------|-------------|
| 1 | [IRSA — Service Account Access](./irsa-service-account-access/README.md) | EKS, IAM, STS, OIDC, S3 | Give a pod AWS permissions with a ServiceAccount via **IRSA** (OIDC trust, no stored keys), then scope a teammate to one namespace with **RBAC + access entries**. Rich on *what OIDC/IRSA/ServiceAccounts are* and the end-to-end creation flow. |

## How these relate to the rest of the repo

- **Containers first?** [ecs-fargate-basics](../ecs-fargate-basics/README.md) and
  [ecs-fargate-advanced](../ecs-fargate-advanced/README.md) cover containers without Kubernetes.
- **Kubernetes concepts for $0?** [k8s-optimization-and-recovery](../k8s-optimization-and-recovery/README.md).
- **Decomposing an app onto EKS?** [monolith-to-microservices-eks](../monolith-to-microservices-eks/README.md).
- **IAM trust/OIDC fundamentals?** [iam-roles-and-policies](../iam-roles-and-policies/README.md) —
  especially the GitHub OIDC federation step, the same protocol IRSA uses.
