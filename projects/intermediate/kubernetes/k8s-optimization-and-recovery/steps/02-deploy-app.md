# Step 2 — Build and Deploy the App

You'll build the Flask image, make it available to the cluster (local clusters don't pull from
your laptop's Docker by default), and deploy the namespace, ConfigMap, Deployment, and Service.

---

## 2.1 Build the Image

```bash
cd /path/to/k8s-optimization-and-recovery
docker build -t webapp:1.0 .
```

## 2.2 Make the Image Visible to the Cluster

A local cluster runs in its own container/VM and **can't see images in your laptop's Docker**
unless you load them in. This is the #1 beginner snag (`ImagePullBackOff`).

**Run only the one command that matches the cluster you created in Step 1** — then continue to 2.3.

| Step 1 choice | What to run |
|---------------|-------------|
| **kind** | `kind load docker-image webapp:1.0 --name optrec` |
| **minikube** | `minikube image load webapp:1.0 --profile optrec` |
| **Docker Desktop** | *Nothing — skip to 2.3.* See note below. |

### kind

```bash
kind load docker-image webapp:1.0 --name optrec
```

### minikube

```bash
minikube image load webapp:1.0 --profile optrec
```

### Docker Desktop built-in Kubernetes — nothing to load

Docker Desktop wires its Docker image store directly into its bundled Kubernetes node, so an image
you just built with `docker build` is **already visible to the cluster**. There is no load step —
**skip straight to 2.3**. (The `kind load` command does not apply here: that cluster is managed by
Docker Desktop, not the `kind` CLI, so there's no `optrec` cluster to load into.)

### Why this works — applies to all three paths

Whichever path you took, the Deployment sets `imagePullPolicy: IfNotPresent` so the cluster uses
the **local** `webapp:1.0` image (loaded, or already present on Docker Desktop) instead of trying
to pull it from a registry it doesn't exist in.

> **If pods show `ImagePullBackOff` / `ErrImageNeverPull`** (any cluster type): change
> `imagePullPolicy` in `k8s/deployment.yaml` to `Never` (use only the local image, never pull)
> and re-apply.

---

## 2.3 Deploy

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Watch the pods come up:

```bash
kubectl get pods -n webapp -w
```

Two `webapp-*` pods should reach **Running** and **1/1 READY** (readiness probe passing).

---

## 2.4 Reach the Service

Port-forward the ClusterIP service to your laptop:

```bash
kubectl port-forward -n webapp svc/webapp 8080:80
```

In another terminal:

```bash
curl -s localhost:8080/         # {"message":"hello...","pod":"webapp-xxxx"}
curl -s localhost:8080/         # run a few times — note the "pod" field
curl -s localhost:8080/data     # reads the ConfigMap-mounted message.txt
```

> **Heads-up:** with `kubectl port-forward` the `pod` value **stays the same** across calls —
> port-forward pins to one backing pod, it doesn't load-balance across the two. That's expected.
> To actually see requests spread over both pods, hit the Service from *inside* the cluster
> instead, e.g. `kubectl run -n webapp tmp --rm -it --image=curlimages/curl --restart=Never -- \
> sh -c 'for i in 1 2 3 4 5 6; do curl -s webapp/; echo; done'` — now the `pod` field rotates.

The `/data` value (`v1 — this value was captured by the Velero backup`) comes from the ConfigMap.
Remember it — in Step 6 you'll delete everything and prove Velero brings it back.

---

## Checkpoint

- [ ] `docker build` produced `webapp:1.0`
- [ ] The image was **loaded into** the cluster (kind/minikube), not just built locally
- [ ] Two `webapp` pods are **Running / 1/1**
- [ ] `curl localhost:8080/` returns JSON (the `pod` name stays fixed under port-forward — see the 2.4 note)
- [ ] `/data` returns the ConfigMap message

---

**Next:** [Step 3 — Right-Size with Requests & Limits](./03-requests-limits.md)
