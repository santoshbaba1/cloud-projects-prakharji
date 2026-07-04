# Costs — IRSA Service Account Access

Region: **us-east-1**. Prices are list price and approximate; check the
[EKS pricing page](https://aws.amazon.com/eks/pricing/) for current numbers.

## Service-by-service breakdown

| Service | What runs | Unit price | If left running 24h |
|---------|-----------|-----------|---------------------|
| **EKS control plane** | 1 cluster `irsa-demo` | **$0.10 / hour** (no free tier) | **~$2.40** |
| **EC2 worker nodes** | 2× `t3.small` | ~$0.0208 / hr each | ~$1.00 |
| **EBS volumes** | node root volumes (2× 20 GB gp3) | ~$0.08/GB-mo | ~$0.10/day |
| **S3** | 1 tiny bucket, 1 object | free-tier eligible | ~$0.00 |
| **STS / AssumeRoleWithWebIdentity** | per call | **free** | $0.00 |
| **IAM role / OIDC provider** | 1 role, 1 provider | **free** | $0.00 |
| **Data transfer** | minimal in-lab | first GB free | ~$0.00 |

## Formula

```
Daily cost ≈ control plane ($2.40) + nodes (2 × $0.0208 × 24 ≈ $1.00) + EBS (~$0.10) ≈ $3.50/day
An afternoon (≈ 3–4 h) ≈ $0.45 control plane + $0.15 nodes ≈ $1–3 total
```

## Free tier notes

- **EKS has NO free tier** for the control plane — it bills from creation to deletion.
- STS, IAM roles, and the OIDC identity provider are **always free** — IRSA itself adds **$0**.
- The only real cost is "an EKS cluster is running," same as any EKS project in this repo.

## ⚠️ "Left running" warnings

- The **control plane charges per hour even while idle** — an EKS cluster you forgot about is
  ~$72/month doing nothing. **Run Step 7 the same day.**
- Worker nodes are EC2 instances — they bill independently of the control plane.
- If `eksctl delete cluster` fails midway, check for a **leftover CloudFormation stack**, **ELB**, or
  **EC2 instances** and remove them manually (see troubleshooting.md).

## Cheapest way to practise

The IRSA mechanism genuinely needs EKS (real OIDC + STS). But the **RBAC / namespace / ServiceAccount
concepts** are free on local `kind`/`minikube` — see
[k8s-optimization-and-recovery](../../../intermediate/kubernetes/k8s-optimization-and-recovery/README.md). Learn those for $0,
then spend the $1–3 here only for the AWS IRSA integration.
