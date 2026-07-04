# Troubleshooting — IRSA Service Account Access

Format: **Error → Cause → Fix.**

---

### `get-caller-identity` in the pod shows the **node role**, not `IrsaS3ReaderRole`

- **Cause:** the pod didn't get IRSA credentials injected, so the SDK fell back to the EC2 node's
  instance role.
- **Fix:** confirm the pod actually uses the SA (`spec.serviceAccountName: s3-reader`) and that the SA
  is annotated:
  ```bash
  kubectl -n apps get pod irsa-test -o jsonpath='{.spec.serviceAccountName}'; echo
  kubectl -n apps get sa s3-reader -o jsonpath='{.metadata.annotations}'; echo
  ```
  The annotation injection only happens **at pod creation** — if you annotated the SA *after* the pod
  started, delete and recreate the pod.

---

### `AccessDenied` / `Not authorized to perform sts:AssumeRoleWithWebIdentity`

- **Cause:** the role's **trust policy** doesn't match the token. Usually a wrong `:sub`, a missing
  OIDC provider, or the wrong account/OIDC ID.
- **Fix:**
  1. Confirm the OIDC provider exists: `aws iam list-open-id-connect-providers`.
  2. Confirm the trust policy `:sub` is **exactly** `system:serviceaccount:apps:s3-reader`.
  3. Confirm the `:aud` is `sts.amazonaws.com`.
  4. Confirm the `Federated` ARN's OIDC ID matches `aws eks describe-cluster ... oidc.issuer`.

---

### Pod env has **no** `AWS_ROLE_ARN` / `AWS_WEB_IDENTITY_TOKEN_FILE`

- **Cause:** the SA wasn't annotated before the pod started, or the EKS pod-identity webhook didn't
  fire.
- **Fix:** annotate the SA, then **recreate** the pod:
  ```bash
  kubectl annotate sa s3-reader -n apps \
    eks.amazonaws.com/role-arn=arn:aws:iam::<ACCOUNT_ID>:role/IrsaS3ReaderRole --overwrite
  kubectl -n apps delete pod irsa-test --ignore-not-found
  kubectl apply -f manifests/test-pod.yaml
  ```

---

### Console "Web identity" role wizard — role is assumable by *any* SA

- **Cause:** the wizard sets the `:aud` condition but **not** `:sub`.
- **Fix:** edit the role's trust policy and add the `:sub` `StringEquals` condition pinning
  `system:serviceaccount:apps:s3-reader`. Without it, every SA in the cluster can assume the role.

---

### `s3 ls` (no bucket) returns `AccessDenied` from the pod

- **Cause:** this is **correct** — `s3:ListAllMyBuckets` is not in the permission policy. The role can
  only `ListBucket`/`GetObject` on the one demo bucket.
- **Fix:** none needed — this proves least privilege. Reference a specific bucket:
  `aws s3 ls s3://irsa-demo-bucket-<ACCOUNT_ID>/`.

---

### Teammate can authenticate but `kubectl get pods -n apps` is **Forbidden**

- **Cause:** access entry exists (authentication works) but no RBAC binds their group to a Role
  (authorization missing).
- **Fix:** apply `rbac-role.yaml` + `rbac-rolebinding.yaml`, and confirm the RoleBinding's
  `subjects[].name` matches the **group** in the access entry (`team-a-devs`).

---

### Teammate gets `error: You must be logged in to the server (Unauthorized)`

- **Cause:** no access entry for their IAM principal (authentication missing), or wrong principal ARN.
- **Fix:** create the access entry (Step 6.3) with the exact ARN of the identity they assume. Verify
  with `aws eks list-access-entries --cluster-name irsa-demo`.

---

### `eksctl delete cluster` fails / hangs

- **Cause:** a dependency (ELB from a `LoadBalancer` Service, leftover ENIs, stuck CFN stack) blocks
  VPC deletion.
- **Fix:** delete any `type=LoadBalancer` Services first (`kubectl get svc -A`), then re-run delete.
  If a CloudFormation stack is stuck, delete it in the CFN console and remove orphaned EC2/ELB/ENI
  resources manually. Then re-run `eksctl delete cluster --name irsa-demo --region us-east-1`.

---

### `update-kubeconfig` works but `kubectl` says `Unauthorized` for **you** (the creator)

- **Cause:** rare — usually you're using a different IAM identity than the one that created the
  cluster. The creator gets implicit admin; others need an access entry.
- **Fix:** use the creating identity, or add an access entry/`AmazonEKSClusterAdminPolicy` for your
  current identity.
