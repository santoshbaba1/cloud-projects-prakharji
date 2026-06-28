# Challenges — IRSA Service Account Access

Extend the project. Each builds real EKS security muscle.

---

### 1. Swap IRSA for **EKS Pod Identity**

EKS Pod Identity is the newer alternative to IRSA — no OIDC trust policy to hand-edit; you create an
**association** between a SA and a role instead.

- Install the **EKS Pod Identity Agent** add-on.
- `aws eks create-pod-identity-association --cluster-name irsa-demo --namespace apps --service-account s3-reader --role-arn ...`.
- Compare: the role's trust policy now trusts `pods.eks.amazonaws.com` instead of the OIDC provider.
- Write down two pros and two cons versus IRSA.

---

### 2. Two workloads, two roles, one namespace

Add a second ServiceAccount `sqs-reader` with its own role that can read **SQS** but not S3. Prove
each pod can only do its own thing — least privilege *per workload*, not per namespace.

---

### 3. Tighten the `:sub` and break it on purpose

Change the trust policy `:sub` to a wrong namespace, recreate the pod, and observe the exact
`AssumeRoleWithWebIdentity` denial. Then fix it. This cements *why* the `:sub` claim is the security
boundary.

---

### 4. Read-only vs. read-write teammate

Add a second RBAC `Role` `team-a-viewer` (only `get`/`list`/`watch`) and a second group
`team-a-viewers`. Map a different IAM principal to it via an access entry. Confirm the viewer can read
pods but not delete them (`kubectl auth can-i delete pods -n apps --as-group=team-a-viewers` → no).

---

### 5. Audit IRSA with CloudTrail

Find the `AssumeRoleWithWebIdentity` events in CloudTrail. Identify the ServiceAccount subject in the
request. Build a metric filter/alarm that fires if any **unexpected** `:sub` ever assumes the role.

---

### 6. Cross-namespace isolation test

Create a second namespace `apps-b` with its own SA + role, and confirm the `apps` teammate (RBAC
group `team-a-devs`) is **Forbidden** in `apps-b`. Prove namespace isolation holds for humans.

---

### 7. Restrict the role further with a session tag or source condition

Add a `Condition` to the permission policy (e.g. an `s3:prefix` condition on `ListBucket`) so the pod
can only list one prefix of the bucket. Verify the narrower boundary from inside the pod.

---

### 8. Reproduce the trust policy with `eksctl` and diff it

Run `eksctl create iamserviceaccount --name s3-reader-2 ...` and inspect the trust policy eksctl
generated (IAM console → role → Trust relationships). Diff it against your hand-written one in
`policies/trust-policy.json`. They should be equivalent — confirm the `:sub`/`:aud` match.
