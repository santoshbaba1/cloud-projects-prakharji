# Step 8 — Cleanup (delete the cluster — cost-critical)

⚠️ **This is the most important step in the project.** The EKS control plane bills **$0.10/hr
every hour the cluster exists**, used or not. Worker nodes and the ELB add more. Leaving this
running is the #1 way to get a surprise bill. Do this step the **same day** you created the
cluster.

---

## 8.1 Delete the LoadBalancer Service first

The `frontend` Service created an AWS ELB. **Delete the Service before the cluster** so eksctl
doesn't leave an orphaned, still-billing load balancer behind:

```bash
kubectl delete -f k8s/03-frontend.yaml
# confirm the ELB is gone (no hostname / removed from EC2 → Load Balancers)
kubectl -n shop get svc
```

Optionally delete the rest of the workloads too (cosmetic — the cluster delete removes them):

```bash
kubectl delete -f k8s/04-hpa.yaml -f k8s/02-orders.yaml -f k8s/01-catalog.yaml
```

---

## 8.2 Delete the EKS cluster

```bash
eksctl delete cluster --name shop-eks --region us-east-1
```

This tears down the node group, the control plane, and the CloudFormation stacks eksctl
created (~10–15 min). **This is the line that stops the $0.10/hr meter.**

---

## 8.3 Delete the ECR repositories

```bash
for s in catalog orders frontend; do
  aws ecr delete-repository --repository-name shop-$s --force --region us-east-1
done
```

---

## 8.4 Verify nothing is left billing

- **EKS → Clusters:** `shop-eks` is gone.
- **EC2 → Load Balancers:** no ELB from the `frontend` Service remains.
- **EC2 → Instances:** no `shop-nodes` workers remain.
- **CloudFormation:** the `eksctl-shop-eks-*` stacks are deleted.
- **ECR:** the three `shop-*` repos are gone.

```bash
eksctl get cluster --region us-east-1            # should not list shop-eks
aws elbv2 describe-load-balancers --query 'LoadBalancers[].LoadBalancerName' --output text
aws cloudformation list-stacks \
  --query "StackSummaries[?contains(StackName,'shop-eks') && StackStatus!='DELETE_COMPLETE'].StackName" \
  --output text
```

---

## Checkpoint

- [ ] `frontend` LoadBalancer Service deleted → ELB removed
- [ ] `eksctl delete cluster` completed (control plane gone)
- [ ] Worker nodes terminated; eksctl CloudFormation stacks deleted
- [ ] Three ECR repos deleted
- [ ] **Cost Explorer** shows no EKS/ELB/EC2 from this project tomorrow

You decomposed a monolith into Kubernetes microservices — and, crucially, **deleted the
cluster** so it costs you nothing going forward. 🎉
