# Step 1 — Create the EKS Cluster and the Namespace

You need a place for everything to live. In this step you create the **EKS cluster** (`irsa-demo`)
and a **namespace** (`apps`) inside it. The cluster is the runtime; the namespace is the labelled
drawer that will hold the ServiceAccount and pod.

> ⚠️ **The meter starts now.** The EKS control plane is **$0.10/hr** from the moment this finishes
> until you delete it in Step 7. Plan to finish in one sitting.

---

## 1.1 What You're Creating

| Thing | Value |
|-------|-------|
| Cluster name | `irsa-demo` |
| Region | `us-east-1` |
| Node group | 2× `t3.small` managed nodes |
| Namespace | `apps` |

---

## 1.2 Create the Cluster

### CLI (eksctl) — recommended

`eksctl` builds the control plane, a managed node group, the VPC, and the IAM wiring in one command.

```bash
eksctl create cluster \
  --name irsa-demo \
  --region us-east-1 \
  --nodegroup-name irsa-nodes \
  --node-type t3.small \
  --nodes 2 \
  --managed
```

This runs a CloudFormation stack and takes **~15–20 minutes**. When it finishes, `eksctl` points
your `kubeconfig` at the new cluster automatically.

> **Why eksctl over the console?** The console makes you hand-build the cluster role, node role, VPC,
> and node group separately. `eksctl` encodes the least-privilege wiring, is reproducible, and — most
> usefully for *this* project — can enable the OIDC provider for you in Step 2 with one flag.

### Console (alternative)

| Step | Action |
|------|--------|
| 1 | **EKS** → **Add cluster** → **Create** |
| 2 | Name `irsa-demo`, choose the latest Kubernetes version, region `us-east-1` |
| 3 | Pick/let it create the **cluster IAM role** (the EKS service role) |
| 4 | Networking: choose a VPC (or the default), leave the cluster endpoint **Public** for the lab |
| 5 | Create the cluster, wait until **Active** (~10–15 min) |
| 6 | Open the cluster → **Compute** → **Add node group** → name `irsa-nodes`, instance `t3.small`, desired size **2** |

> The Console path is good for *seeing* the pieces, but you'll still finish setup from the CLI — the
> rest of this project is CLI-first because IRSA is easiest to reason about as explicit commands.

---

## 1.3 Confirm kubectl Can Reach the Cluster

```bash
aws eks update-kubeconfig --name irsa-demo --region us-east-1   # needed if you used the Console
kubectl get nodes
kubectl get pods -A
```

You should see **2 nodes** in `Ready` state and the core system pods (`coredns`, `aws-node`,
`kube-proxy`) running.

---

## 1.4 Create the Namespace

A namespace is the isolation boundary for everything that follows. Apply the manifest:

```bash
kubectl apply -f manifests/00-namespace.yaml
kubectl get ns apps --show-labels
```

CLI one-liner alternative (no manifest):

```bash
kubectl create namespace apps
```

> **Why a dedicated namespace?** It scopes blast radius and is exactly what the human-access step
> (Step 6) will lock a teammate into. The IRSA trust policy in Step 4 also pins the ServiceAccount to
> *this* namespace by name — so the namespace is part of the security boundary, not just tidiness.

---

## Checkpoint

- [ ] `eksctl create cluster` (or the Console path) finished without error
- [ ] `kubectl get nodes` shows **2 `Ready`** nodes
- [ ] System pods are `Running`
- [ ] Namespace `apps` exists
- [ ] You've noted the time you created the cluster (so you remember to delete it!)

---

**Next:** [Step 2 — Enable the OIDC Provider](./02-enable-oidc-provider.md)
