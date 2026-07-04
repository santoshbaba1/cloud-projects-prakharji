# Costs — Kubernetes Optimization & Recovery

This is the one project in the repo with **no AWS bill at all** — everything runs in Docker on
your laptop. The "cost" is local resources and your time.

---

## What You Actually Spend

| Resource | Usage | Cost |
|----------|-------|------|
| **AWS** | none — nothing is created in AWS | **$0.00** |
| **Local CPU** | kind/minikube node + a few small pods + MinIO | ~1–2 vCPU while running |
| **Local memory** | cluster + app + metrics-server + Velero + MinIO | ~2–4 GB |
| **Local disk** | images (python-slim, minio, busybox) + cluster state | ~2–3 GB |

A machine with **2 vCPU and 4 GB free** runs this comfortably. The HPA load test (Step 4) briefly
pushes CPU up — that's the point — but it's bounded by the pods' `250m` CPU limits.

---

## If You Lift It to EKS (Challenge 7)

The moment you move to **Amazon EKS**, costs appear — and they're worth knowing before you try it:

| Service | Approx cost | Note |
|---------|-------------|------|
| **EKS control plane** | **$0.10 / hour** (~$73/mo) | Per cluster, always on — the big one |
| **Worker nodes (EC2)** | per instance/hour | e.g. 2× t3.small ≈ $0.04/hr total |
| **EBS volumes** | per GB-month | Node root + any PVs |
| **S3 (Velero backups)** | $0.023 / GB-month | Tiny for object backups |
| **Data transfer / NAT** | varies | NAT gateway is a common surprise (~$0.045/hr) |

> The EKS **control plane alone is ~$73/month** whether or not you run workloads — so on EKS,
> *delete the cluster when done*, exactly like the RDS project. Locally, none of this applies.

---

## Why Local Is the Right Call Here

The skills — requests/limits, HPA, probes, PDB, Velero backup/restore — are **identical** on a
local cluster and on EKS. Learning them for free on kind/minikube, then porting to EKS once you're
fluent (Challenge 7), is the cheapest path. The S3-compatible MinIO store means even the *backup*
workflow transfers unchanged.

---

## Left Running?

A local cluster left running just consumes laptop CPU/RAM (and laptop battery) — **no money**. Run
[Step 7](steps/07-cleanup.md) to reclaim those resources when you're done.

**Bottom line: $0.00 on AWS. Local resources only.**
