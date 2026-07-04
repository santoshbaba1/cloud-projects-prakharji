# Step 4 — Deploy Catalog & Orders (service-to-service DNS)

Deploy the two backend microservices and prove the central microservices idea: **services find
each other by name, over the network.** `orders` validates a `book_id` by making an HTTP call to
`catalog` at `catalog.shop.svc.cluster.local` — the in-process function call from the monolith
is now a network hop. That hop is powerful (independent scaling) and dangerous (it can fail) —
both lessons land here.

---

## 4.1 Set the image URIs

Edit `k8s/01-catalog.yaml` and `k8s/02-orders.yaml`, replacing `<account>` in the `image:`
lines with your account id (or use `sed`):

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
sed -i "s/<account>/$ACCOUNT_ID/g" k8s/01-catalog.yaml k8s/02-orders.yaml k8s/03-frontend.yaml
```

---

## 4.2 Deploy Catalog

```bash
kubectl apply -f k8s/01-catalog.yaml
kubectl -n shop rollout status deploy/catalog
kubectl -n shop get pods -l app=catalog
```

Two `catalog` pods should reach `Running` and pass their readiness probe.

> **What the manifest sets up:** a Deployment of 2 replicas, resource requests/limits (so the
> scheduler can place them and the HPA has a baseline), `/health` readiness + liveness probes,
> and a **ClusterIP** Service named `catalog` — internal only, reachable cluster-wide as
> `catalog.shop.svc.cluster.local`.

---

## 4.3 Deploy Orders

`orders` reads `CATALOG_URL` from a **ConfigMap** (Twelve-Factor: config in the environment,
not baked into the image):

```bash
kubectl apply -f k8s/02-orders.yaml
kubectl -n shop rollout status deploy/orders
```

---

## 4.4 Prove the Service-to-Service Call

Exec into a throwaway pod and call orders, which will internally call catalog:

```bash
kubectl -n shop run curl --image=curlimages/curl -it --rm --restart=Never -- \
  sh -c '
    echo "--- orders -> catalog (valid book) ---";
    curl -s -X POST http://orders.shop.svc.cluster.local/orders \
      -H "content-type: application/json" -d "{\"book_id\":\"b1\",\"qty\":2}";
    echo;
    echo "--- orders -> catalog (bad book) ---";
    curl -s -X POST http://orders.shop.svc.cluster.local/orders \
      -H "content-type: application/json" -d "{\"book_id\":\"ghost\"}";
  '
```

Expect a `201` for `b1` (orders successfully reached catalog and validated it) and a `400
unknown book_id` for `ghost`. **That round trip is the network call between two microservices.**

> **Design-for-failure note:** if you scale catalog to zero (`kubectl -n shop scale deploy/catalog
> --replicas=0`) and retry, orders returns **503 catalog unavailable** — not a crash. The
> monolith never had this failure mode because the call was in-process. Scale catalog back to 2
> when done.

---

## Checkpoint

- [ ] `catalog` and `orders` Deployments are `Available` with 2 pods each
- [ ] A `POST /orders` with `b1` returns `201` (proves orders → catalog DNS call works)
- [ ] A bad `book_id` returns `400`; catalog scaled to 0 returns `503` (design-for-failure)
- [ ] You can explain what `catalog.shop.svc.cluster.local` resolves to

---

**Next:** [Step 5 — Frontend & Strangler Cutover](./05-frontend-and-cutover.md)
