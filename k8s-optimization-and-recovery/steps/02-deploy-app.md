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

### kind

```bash
kind load docker-image webapp:1.0 --name optrec
```

### minikube

```bash
minikube image load webapp:1.0 --profile optrec
```

The Deployment uses `imagePullPolicy: IfNotPresent` so the cluster uses this loaded image instead
of trying to pull `webapp:1.0` from a registry.

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
curl -s localhost:8080/         # run a few times — the pod name changes (load spreads)
curl -s localhost:8080/data     # reads the ConfigMap-mounted message.txt
```

The `/data` value (`v1 — this value was captured by the Velero backup`) comes from the ConfigMap.
Remember it — in Step 6 you'll delete everything and prove Velero brings it back.

---

## Checkpoint

- [ ] `docker build` produced `webapp:1.0`
- [ ] The image was **loaded into** the cluster (kind/minikube), not just built locally
- [ ] Two `webapp` pods are **Running / 1/1**
- [ ] `curl localhost:8080/` returns JSON and rotates pod names across calls
- [ ] `/data` returns the ConfigMap message

---

**Next:** [Step 3 — Right-Size with Requests & Limits](./03-requests-limits.md)
