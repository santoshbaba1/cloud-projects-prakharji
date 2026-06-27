# Step 2 — Build & Push the Microservice Images

Decomposition starts here. The monolith's three responsibilities are already split into three
small apps under `src/`: `catalog`, `orders`, `frontend`. In this step you containerize each
and push it to its own **ECR** repository, so EKS can pull them in Step 4.

---

## 2.1 What You're Creating

| ECR repo | Source | Talks to |
|----------|--------|----------|
| `shop-catalog` | `src/catalog` | nobody (owns book data) |
| `shop-orders` | `src/orders` | `catalog` (validate book_id) |
| `shop-frontend` | `src/frontend` | `catalog`, `orders` |

> **Why three images, not one?** A microservice is independently deployable — that starts with
> an independently buildable artifact. Three repos = three release streams.

---

## 2.2 Create the ECR Repositories

### Console
**ECR → Repositories → Create repository** (private) → name `shop-catalog`. Repeat for
`shop-orders`, `shop-frontend`.

### CLI alternative
```bash
for s in catalog orders frontend; do
  aws ecr create-repository --repository-name shop-$s --region us-east-1
done
```

---

## 2.3 Authenticate Docker to ECR

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGISTRY=$ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin $REGISTRY
```

---

## 2.4 Build, Tag, Push (all three)

```bash
for s in catalog orders frontend; do
  docker build -t shop-$s:1 src/$s
  docker tag  shop-$s:1 $REGISTRY/shop-$s:1
  docker push $REGISTRY/shop-$s:1
done
```

> **Apple Silicon / ARM laptop?** EKS nodes are x86 by default. Build for the node arch:
> `docker build --platform linux/amd64 -t shop-$s:1 src/$s`. A mismatched arch shows up later
> as `exec format error` in the pod logs.

---

## 2.5 Record the image URIs

You'll paste these into the k8s manifests in Step 4:

```
<account>.dkr.ecr.us-east-1.amazonaws.com/shop-catalog:1
<account>.dkr.ecr.us-east-1.amazonaws.com/shop-orders:1
<account>.dkr.ecr.us-east-1.amazonaws.com/shop-frontend:1
```

Verify they landed:

```bash
for s in catalog orders frontend; do
  aws ecr list-images --repository-name shop-$s --query 'imageIds[].imageTag' --output text
done
```

---

## Checkpoint

- [ ] Three ECR repos exist: `shop-catalog`, `shop-orders`, `shop-frontend`
- [ ] `docker push` succeeded for all three `:1` tags
- [ ] `aws ecr list-images` shows tag `1` in each repo
- [ ] You've noted the three full image URIs

---

**Next:** [Step 3 — Provision the EKS Cluster](./03-provision-eks.md)
