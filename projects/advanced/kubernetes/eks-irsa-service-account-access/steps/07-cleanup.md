# Step 7 — Cleanup (Cost-Critical)

> ⚠️ **The EKS control plane bills $0.10/hr until the cluster is deleted — whether or not you use it.**
> This is the most important step in the project. Do it the same day.

Delete in roughly the reverse order you created things.

---

## 7.1 Delete the Kubernetes Objects

```bash
kubectl delete -f manifests/test-pod.yaml --ignore-not-found
kubectl delete -f manifests/rbac-rolebinding.yaml --ignore-not-found
kubectl delete -f manifests/rbac-role.yaml --ignore-not-found
kubectl delete -f manifests/serviceaccount.yaml --ignore-not-found
kubectl delete -f manifests/00-namespace.yaml --ignore-not-found   # removes the apps namespace
```

---

## 7.2 Delete the Access Entry

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
PRINCIPAL_ARN="arn:aws:iam::$ACCOUNT_ID:user/dev-team-a"   # adjust to what you mapped

aws eks delete-access-entry \
  --cluster-name irsa-demo \
  --region us-east-1 \
  --principal-arn "$PRINCIPAL_ARN"
```

---

## 7.3 Delete the IAM Role

```bash
aws iam delete-role-policy --role-name IrsaS3ReaderRole --policy-name IrsaS3ReadAccess
aws iam delete-role --role-name IrsaS3ReaderRole
```

> If you used `eksctl create iamserviceaccount`, instead run:
> `eksctl delete iamserviceaccount --name s3-reader --namespace apps --cluster irsa-demo --region us-east-1`
> (it removes the CloudFormation-managed role for you).

---

## 7.4 Empty and Delete the S3 Bucket

```bash
BUCKET="irsa-demo-bucket-$ACCOUNT_ID"
aws s3 rm "s3://$BUCKET" --recursive
aws s3 rb "s3://$BUCKET"
```

---

## 7.5 Delete the OIDC Provider (optional)

The OIDC provider costs **nothing**, so you can keep it. To remove it:

```bash
OIDC_ARN=$(aws iam list-open-id-connect-providers \
  --query "OpenIDConnectProviderList[?contains(Arn, 'oidc.eks')].Arn | [0]" --output text)
aws iam delete-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_ARN"
```

> ⚠️ Don't delete this if other clusters/roles in the account still rely on the same provider.

---

## 7.6 Delete the Cluster (the big one)

```bash
eksctl delete cluster --name irsa-demo --region us-east-1
```

This tears down the control plane, node group, and the VPC/IAM that `eksctl` created
(~10–15 min). If you created the cluster in the Console, delete the **node group first**, then the
**cluster**, in the EKS console.

---

## 7.7 Verify Nothing Is Still Billing

```bash
aws eks list-clusters --region us-east-1          # should not list irsa-demo
aws ec2 describe-instances --region us-east-1 \
  --filters "Name=tag:eks:cluster-name,Values=irsa-demo" \
  --query "Reservations[].Instances[].State.Name"  # should be empty/terminated
```

---

## Checkpoint

- [ ] All Kubernetes objects deleted (namespace `apps` gone)
- [ ] Access entry removed
- [ ] IAM role `IrsaS3ReaderRole` deleted
- [ ] S3 bucket emptied and removed
- [ ] **Cluster `irsa-demo` deleted** — `list-clusters` no longer shows it
- [ ] No worker EC2 instances left running

✅ **You're done.** You built IRSA end-to-end, proved a pod gets AWS access with zero stored keys,
and scoped a teammate to one namespace with RBAC — and you can explain why those are two different
mechanisms.
