# Costs — Monolith → Microservices on EKS

Region **us-east-1**. ⚠️ **Unlike most projects in this repo, this one is NOT free.** The EKS
control plane has **no free tier** and bills per hour. Treat this as a paid lab and delete
everything the same day.

---

## Service-by-service

### EKS control plane — the big one

| Item | Rate | Notes |
|------|------|-------|
| Cluster | **$0.10 / hour** (~$2.40/day, ~$73/mo) | **No free tier.** Bills whether idle or busy |

This is the cost that matters. One forgotten cluster = ~$73/month.

### EC2 worker nodes

| Item | Rate | Notes |
|------|------|-------|
| 2× `t3.small` On-Demand | ~$0.0208/hr each (~$0.042/hr total) | Free tier (`t3.micro`) doesn't cover `t3.small` |
| EBS gp3 (per node) | ~$0.08/GB-mo | Small root volumes |

### Elastic Load Balancer (frontend Service)

| Item | Rate | Notes |
|------|------|-------|
| Classic/NLB hours | ~$0.0225/hr | Created by `type: LoadBalancer` |
| Data processed | small | Negligible at lab scale |

**Delete the Service before the cluster** (Step 8.1) or the ELB can be orphaned and keep
billing.

### ECR

| Item | Rate | Notes |
|------|------|-------|
| Storage | $0.10/GB-mo | **Free tier:** 500 MB/mo for 12 months |

Three small Python images fit comfortably in the free tier.

---

## Rough total

```
EKS control plane : $0.10/hr  ×  ~4 hrs  ≈  $0.40
Worker nodes      : $0.042/hr ×  ~4 hrs  ≈  $0.17
ELB               : $0.0225/hr × ~3 hrs  ≈  $0.07
ECR               : ~$0 (free tier)
                                       --------
An afternoon lab                       ≈  ~$1
```

Left running for a month by accident: **~$80+**. That asymmetry is the whole reason Step 8
exists and why it's the most important step.

## Left-running warning ⚠️

- **EKS cluster** — $0.10/hr forever until `eksctl delete cluster`. The #1 surprise-bill risk.
- **ELB** — delete the `frontend` Service first so the load balancer is removed cleanly.
- **Worker nodes** — terminated by the cluster delete, but verify in EC2 → Instances.
- **Orphaned CloudFormation stacks** — if a delete half-fails, check `eksctl-shop-eks-*` stacks
  and delete them manually.

> **Want $0?** Do the local `kind`/`minikube` version in
> [README Appendix A](README.md#appendix-a--run-it-locally-for-0). It teaches the same
> Kubernetes concepts with no AWS bill.
