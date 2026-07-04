# Step 3 — Provision the EKS Cluster

Now you build the runtime the microservices will live on: a managed Kubernetes cluster on
**Amazon EKS**. `eksctl` does the heavy lifting — it creates the control plane, a managed node
group, the VPC, and the IAM wiring, then updates your `kubeconfig` so `kubectl` just works.

> ⚠️ **The meter starts now.** The EKS control plane is **$0.10/hr** from the moment this
> finishes until you delete it in Step 8. Plan to finish in one sitting.

---

## 3.1 What You're Creating

| Thing | Value |
|-------|-------|
| Cluster name | `shop-eks` |
| Region | `us-east-1` |
| Node group | 2× `t3.small` managed nodes |
| Kubernetes | latest eksctl default |

---

## 3.2 Create the Cluster (eksctl)

```bash
eksctl create cluster \
  --name shop-eks \
  --region us-east-1 \
  --nodegroup-name shop-nodes \
  --node-type t3.small \
  --nodes 2 \
  --managed
```

This runs a CloudFormation stack and takes **~15–20 minutes**. When it finishes, `eksctl`
points your `kubeconfig` at the new cluster automatically.

> **Why eksctl over the console?** The console requires you to hand-build the cluster role,
> node role, VPC, and node group separately. `eksctl` encodes the least-privilege wiring and
> is reproducible — closer to how you'd really run EKS.

---

## 3.3 Confirm kubectl Can Reach It

```bash
aws eks update-kubeconfig --name shop-eks --region us-east-1   # if needed
kubectl get nodes
kubectl get pods -A
```

You should see **2 nodes** in `Ready` state and the core system pods (`coredns`,
`aws-node`, `kube-proxy`) running.

---

## 3.4 Create the Namespace

Keep the shop's resources in their own namespace for a clean blast-radius boundary:

```bash
kubectl apply -f k8s/00-namespace.yaml
kubectl get ns shop
```

---

## Checkpoint

- [ ] `eksctl create cluster` finished without error
- [ ] `kubectl get nodes` shows 2 `Ready` nodes
- [ ] System pods are `Running`
- [ ] Namespace `shop` exists
- [ ] You've noted the time you created the cluster (so you remember to delete it!)

---

**Next:** [Step 4 — Deploy Catalog & Orders](./04-deploy-catalog-orders.md)
