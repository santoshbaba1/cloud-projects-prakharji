# Step 1 — Create a Local Cluster + metrics-server

You'll run a real Kubernetes cluster on your laptop. Pick **one** of kind or minikube — the rest
of the project works the same on either. You also install **metrics-server**, the add-on that
feeds both `kubectl top` (Step 3) and the HPA (Step 4).

---

## 1.1 Create the Cluster

### Option A — kind (Kubernetes IN Docker)

```bash
# install: https://kind.sigs.k8s.io  (brew install kind / go install / binary)
kind create cluster --name optrec
kubectl cluster-info --context kind-optrec
```

### Option B — minikube

```bash
# install: https://minikube.sigs.k8s.io
minikube start --cpus=2 --memory=4096 --profile optrec
kubectl config use-context optrec
```

Confirm the node is **Ready**:

```bash
kubectl get nodes
```

---

## 1.2 Install metrics-server

`kubectl top` and the HPA need a metrics source. The cluster doesn't ship one by default.

### minikube — one command

```bash
minikube addons enable metrics-server --profile optrec
```

### kind — apply the manifest (with a local-cluster TLS flag)

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# kind nodes use self-signed kubelet certs; tell metrics-server to accept them (LAB ONLY):
kubectl patch -n kube-system deployment metrics-server --type=json \
  -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
```

> **Why `--kubelet-insecure-tls` is lab-only:** it tells metrics-server to skip verifying the
> kubelet's certificate. On kind that's fine because everything is on your laptop; on a real
> cluster you'd provision proper certs instead. We flag every such shortcut so you don't carry it
> into production.

---

## 1.3 Verify Metrics Are Flowing

Give it ~30–60 seconds, then:

```bash
kubectl get deployment metrics-server -n kube-system   # READY 1/1
kubectl top nodes                                      # shows CPU/memory, not an error
```

If `kubectl top nodes` returns numbers, you're ready. If it says *"Metrics API not available,"*
wait another minute (it scrapes on an interval) — see [troubleshooting](../troubleshooting.md).

---

## Checkpoint

- [ ] `kubectl get nodes` shows one **Ready** node
- [ ] `metrics-server` deployment is **1/1**
- [ ] `kubectl top nodes` returns CPU/memory numbers
- [ ] You know which tool you chose (kind vs minikube) — it affects how you load the image in Step 2

---

**Next:** [Step 2 — Build and Deploy the App](./02-deploy-app.md)
