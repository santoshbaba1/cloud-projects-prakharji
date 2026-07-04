# Step 1 — Run the Monolith (the "before")

Before decomposing anything, run the monolith as it is: one container serving the whole shop.
This is your baseline — the thing you'll strangle into microservices. Running it first makes
the "why" concrete: one image, one port, one scaling knob.

---

## 1.1 What You're Building

`src/monolith/app.py` is a single Flask app with three responsibilities bolted together:

| Route | Domain (future service) |
|-------|--------------------------|
| `GET /` | storefront (→ `frontend`) |
| `GET /books`, `GET /books/{id}` | catalog (→ `catalog`) |
| `POST /orders` | orders (→ `orders`) |

On AWS you'd run this as **one ECS/Fargate task** — see
[ecs-fargate-basics](../../../../intermediate/aws/aws-ecs-fargate-basics/README.md). For this step, a local container is
enough to feel its shape.

---

## 1.2 Build and Run It

```bash
cd src/monolith
docker build -t shop-monolith:1 .
docker run --rm -p 8080:8080 shop-monolith:1
```

In another terminal:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/books
curl -X POST http://localhost:8080/orders \
  -H 'content-type: application/json' -d '{"book_id":"b1","qty":2}'
open http://localhost:8080/        # the storefront page
```

---

## 1.3 Name the Limits (the migration's "why")

| You ask… | Monolith answer | Microservices answer (later) |
|----------|-----------------|-------------------------------|
| Catalog gets hammered, orders is quiet — scale just catalog? | No — scale the whole image | Yes — catalog HPA scales alone |
| Ship a storefront tweak — what's redeployed/retested? | The whole app | Only `frontend` |
| The orders code has a memory leak — what's affected? | Catalog + storefront too (same process) | Only `orders` pods |
| Two teams want to release on different days? | They must coordinate one deploy | Each owns its own service + cadence |

> **Optional — see it as one ECS task.** Push `shop-monolith:1` to ECR and run it as a single
> Fargate task (reuse [ecs-fargate-basics](../../../../intermediate/aws/aws-ecs-fargate-basics/README.md)). That's the true
> "AWS before" you'll migrate away from. The local container teaches the same lesson faster.

---

## Checkpoint

- [ ] `shop-monolith:1` image builds and runs
- [ ] `/`, `/books`, and `POST /orders` all work from the **one** container
- [ ] You can name at least 3 limits the monolith shape imposes

---

**Next:** [Step 2 — Build & Push the Microservice Images](./02-build-push-images.md)
