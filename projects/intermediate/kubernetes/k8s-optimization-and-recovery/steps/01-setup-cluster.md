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

### Option C — Docker Desktop built-in Kubernetes (Windows/WSL or macOS)

If you already run Docker Desktop, you can use its bundled single-node cluster instead of
installing kind/minikube. It uses kind technology under the hood (the node is named
`desktop-control-plane`), but **Docker Desktop creates and manages it — you don't run the `kind`
CLI** (the `kind load` step in Step 2 won't apply; see the note there).

1. Docker Desktop → **Settings → Kubernetes → Enable Kubernetes** → *Apply & Restart*.
2. On **Windows/WSL**, also enable **Settings → Resources → WSL Integration** for your distro,
   or the `docker`/`kubectl` CLIs in WSL can't reach the engine (`Cannot connect to the Docker
   daemon`).
3. Point kubectl at it:

```bash
kubectl config use-context docker-desktop
```

> **Note:** this cluster is **separate** from any `kind create cluster --name optrec` cluster.
> Throughout this project, wherever a command references the `optrec`/`kind-optrec` cluster,
> use the `docker-desktop` context instead.

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

### kind or Docker Desktop — apply the manifest (with a local-cluster TLS flag)

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# kind & Docker Desktop nodes use self-signed kubelet certs; tell metrics-server to accept them (LAB ONLY):
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
- [ ] You know which tool you chose (kind / minikube / Docker Desktop) — it affects how you load the image in Step 2

---

**Next:** [Step 2 — Build and Deploy the App](./02-deploy-app.md)
