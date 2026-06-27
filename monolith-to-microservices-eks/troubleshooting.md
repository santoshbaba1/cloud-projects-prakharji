# Troubleshooting — Monolith → Microservices on EKS

Format: **Error → Cause → Fix.**

---

### Pod stuck in `ImagePullBackOff` / `ErrImagePull`

**Cause:** The `image:` URI is wrong, the tag wasn't pushed, or the node group can't pull from
ECR (missing `AmazonEC2ContainerRegistryReadOnly` on the node role).

**Fix:** Confirm the URI matches `aws ecr list-images` output and the `<account>` was replaced
(Step 4.1). `eksctl`-managed node groups get ECR read by default; if you built the nodes by
hand, attach `AmazonEC2ContainerRegistryReadOnly` to the node role.

---

### Pod crashes with `exec format error`

**Cause:** Image built for ARM (Apple Silicon) but EKS nodes are x86_64.

**Fix:** Rebuild with `docker build --platform linux/amd64 ...` and push again (Step 2.4).

---

### Pod is `Running` but never becomes `Ready`

**Cause:** The readiness probe to `/health` is failing — wrong `containerPort`, app not
listening on `0.0.0.0:8080`, or the app is slow to start.

**Fix:** `kubectl -n shop describe pod <pod>` and read the Events. Confirm the container listens
on 8080 (the apps default to `PORT=8080`) and the probe path/port match the manifest.

---

### `orders` returns `503 catalog unavailable`

**Cause:** `orders` can't reach `catalog` — catalog has zero ready pods, the Service name/port
is wrong, or `CATALOG_URL` is misconfigured.

**Fix:** `kubectl -n shop get pods -l app=catalog` (need ≥1 Ready). Confirm the `catalog`
Service exists on port 80 and `orders-config` ConfigMap sets
`CATALOG_URL=http://catalog.shop.svc.cluster.local:80`. (A `503` under catalog-down is *correct*
design-for-failure behavior — only a problem if catalog should be up.)

---

### DNS name doesn't resolve inside the cluster

**Cause:** CoreDNS isn't healthy, or you used the wrong FQDN (namespace mismatch).

**Fix:** `kubectl -n kube-system get pods -l k8s-app=kube-dns` should be Running. The full name
is `<service>.<namespace>.svc.cluster.local` — here `catalog.shop.svc.cluster.local`. From a pod
in the `shop` namespace, the short name `catalog` also works.

---

### `frontend` Service has no `EXTERNAL-IP` / hostname (stuck `<pending>`)

**Cause:** The ELB is still provisioning (~1–2 min), or the cluster's subnets aren't tagged for
load balancers.

**Fix:** Wait and re-check `kubectl -n shop get svc frontend`. `eksctl` tags subnets correctly
by default; if you brought your own VPC, public subnets need
`kubernetes.io/role/elb=1`.

---

### `kubectl top nodes` → `error: Metrics API not available`

**Cause:** `metrics-server` isn't installed, so the HPA also can't scale.

**Fix:** Apply it (Step 6.1) and wait for its Deployment to be Available. On some clusters you
must add `--kubelet-insecure-tls` to its args.

---

### HPA shows `<unknown>/50%` for CPU

**Cause:** metrics-server isn't ready yet, or the Deployment has no CPU **requests** (HPA needs
requests to compute a percentage).

**Fix:** Ensure metrics-server is up, and that `catalog` sets `resources.requests.cpu` (the
manifest sets `100m`). Wait ~30s for metrics to populate.

---

### `eksctl create cluster` fails partway / `kubectl` can't connect

**Cause:** A half-built CloudFormation stack, or `kubeconfig` not updated.

**Fix:** `aws eks update-kubeconfig --name shop-eks --region us-east-1`. If creation failed,
delete the partial stacks (`eksctl delete cluster --name shop-eks`) and retry — leftover
`eksctl-shop-eks-*` stacks otherwise block a clean recreate.

---

### After `eksctl delete cluster`, an ELB is still in the EC2 console

**Cause:** The `frontend` LoadBalancer Service wasn't deleted before the cluster, so its ELB was
orphaned — and it keeps billing.

**Fix:** Delete it manually in **EC2 → Load Balancers**. Next time, delete the Service first
(Step 8.1). Always re-check Load Balancers after a cluster delete.
