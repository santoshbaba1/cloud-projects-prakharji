# Challenges — Kubernetes Optimization & Recovery

Push the cluster further. These build on what you deployed.

---

## Challenge 1 — Find the Right Request from Real Data

Run the load Job a few times while watching `kubectl top pods`. Record steady-state and peak CPU.
Now **set the request to match reality** (e.g. if peak is ~180m, a `100m` request under-reserves
and the node may overcommit). Re-apply and observe scheduling. Write a sentence on the trade-off:
requests too low → overcommit/eviction risk; too high → wasted, fewer pods per node.

---

## Challenge 2 — Memory Limits and OOMKilled

Drop the memory limit to `16Mi`, re-apply, and hit the app. Watch `kubectl describe pod` report
`OOMKilled` and the RESTARTS climb. Then raise it back. Discuss why a **memory** limit breach is
fatal (killed) while a **CPU** limit breach is merely throttled — and why that makes memory the
scarier resource to under-set.

---

## Challenge 3 — Vertical Pod Autoscaler (VPA)

Install the **VPA** and run it in `recommendation` mode against the Deployment. Compare its
suggested requests/limits to the values you hand-picked. Discuss when to use VPA (right-sizing a
single pod's baseline) vs HPA (scaling pod count) — and why running both on CPU at once can
conflict.

---

## Challenge 4 — Make the PDB Actually Bite

Recreate the cluster with multiple workers (`kind create cluster --config` with several
`worker` nodes), spread the Deployment across them, then `kubectl drain` one node **without**
`--force`. Watch the eviction respect `minAvailable: 1` — the drain blocks until a replacement pod
is Ready elsewhere. This is the real-world value the single-node lab can only hint at.

---

## Challenge 5 — Back Up a Stateful Volume

Add a `PersistentVolumeClaim` and write data into it from the app, then enable Velero **File System
Backup** (`--default-volumes-to-fs-backup`) so the volume contents — not just the Kubernetes
objects — are captured. Delete and restore, and prove the *file data* came back, not just the PVC
definition. This is the difference between backing up config and backing up state.

---

## Challenge 6 — Scheduled Backups + Restore Drill

Create a recurring backup and a discipline to test it:
```bash
velero schedule create webapp-daily --schedule "0 2 * * *" --include-namespaces webapp
```
Then write a short runbook: weekly, restore the latest backup into a **new** namespace
(`--namespace-mappings webapp:webapp-test`), verify `/data`, and delete the test namespace. A
backup you've never restored isn't a backup.

---

## Challenge 7 — Port It to Amazon EKS

Lift the whole project to **Amazon EKS** (`eksctl create cluster`), install metrics-server and the
HPA the same way, and point Velero at a real **S3 bucket** with an IAM-scoped role (IRSA) instead
of MinIO. Note what changes (cluster provisioning, S3 endpoint/credentials, real costs from
[costs.md](costs.md)) and what stays **identical** (every `kubectl`/`velero` command). Then
**delete the cluster** — the EKS control plane bills ~$73/month.
