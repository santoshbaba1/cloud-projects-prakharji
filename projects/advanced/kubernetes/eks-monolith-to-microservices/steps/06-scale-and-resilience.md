# Step 6 — Scaling & Resilience (the payoff)

This is where microservices earn their complexity. You'll see the two properties the monolith
couldn't give you: **independent elastic scaling** (only the hot service grows) and
**self-healing** (Kubernetes reschedules failed pods automatically). You'll also do a
**rolling update** of one service without touching the others.

---

## 6.1 Install metrics-server (HPA needs it)

The HPA scales on CPU, which it reads from `metrics-server`:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl -n kube-system rollout status deploy/metrics-server
kubectl top nodes        # works once metrics-server is up (~30s)
```

---

## 6.2 Independent Autoscaling (HPA on catalog only)

```bash
kubectl apply -f k8s/04-hpa.yaml
kubectl -n shop get hpa catalog
```

Now generate load against **catalog** and watch *only catalog* scale, while orders and frontend
stay at 2 replicas:

```bash
# load generator: hammer catalog from inside the cluster
kubectl -n shop run load --image=busybox --restart=Never -- \
  /bin/sh -c 'while true; do wget -q -O- http://catalog.shop.svc.cluster.local/books >/dev/null; done'

# watch it grow (2 -> up to 6), then the others staying put
kubectl -n shop get hpa catalog -w
kubectl -n shop get deploy
```

After CPU passes 50%, the HPA adds catalog replicas (up to 6). **Orders and frontend don't
move** — that's per-service elasticity the monolith fundamentally can't do. Stop the load:

```bash
kubectl -n shop delete pod load
```

Catalog scales back down after the cool-down.

---

## 6.3 Rolling Update of One Service

Ship a "v2" of catalog without redeploying anything else. Build/push a new tag, then:

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
kubectl -n shop set image deploy/catalog \
  catalog=$ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/shop-catalog:2
kubectl -n shop rollout status deploy/catalog
```

Kubernetes replaces pods gradually (readiness-gated), so there's **no downtime**, and `orders`
and `frontend` are untouched. Roll back instantly if needed:

```bash
kubectl -n shop rollout undo deploy/catalog
```

> **Contrast:** in the monolith, shipping a catalog change meant redeploying (and risking) the
> whole shop. Here it's one Deployment's rollout, independently revertible.

---

## 6.4 Self-Healing

Kill a pod and watch the ReplicaSet replace it — no human action:

```bash
kubectl -n shop get pods -l app=orders
kubectl -n shop delete pod <one-orders-pod>
kubectl -n shop get pods -l app=orders -w   # a fresh pod appears automatically
```

The **liveness probe** does the same for a hung-but-not-dead container: if `/health` stops
responding, Kubernetes restarts the container. The **readiness probe** keeps traffic away from a
pod until it's actually ready — so rollouts and restarts never serve a half-started pod.

---

## Checkpoint

- [ ] `kubectl top nodes` works (metrics-server up)
- [ ] Under load, **only** catalog scales (HPA 2→…→6); orders/frontend stay at 2
- [ ] A `set image` rolling update on catalog completes with no downtime; `rollout undo` works
- [ ] Deleting a pod auto-creates a replacement
- [ ] You can state the difference between a liveness and a readiness probe

---

**Next:** [Step 7 — Decommission the Monolith](./07-decommission-monolith.md)
