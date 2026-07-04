# Step 6 — Cleanup

Nothing here costs money, but a tidy machine is a happy machine. This removes every container, the
network, the Compose stack, and the two images this lab created.

---

## 6.1 Bring down the Compose stack

If you ran Step 5, this removes its containers **and** its auto-created network:

```bash
docker compose down
```

To also drop the built images in the same command:

```bash
docker compose down --rmi local
```

---

## 6.2 Remove the hand-run containers

If any Step 3/4 containers are still around:

```bash
docker rm -f backend frontend 2>/dev/null || true
```

`-f` stops them first if they're running. The `|| true` keeps the command quiet if they're already gone.

---

## 6.3 Remove the user-defined network

```bash
docker network rm appnet 2>/dev/null || true
```

If it complains about *active endpoints*, a container is still attached — run 6.2 first, then retry.

---

## 6.4 Remove the images

```bash
docker rmi flask-net-frontend:1.0 flask-net-backend:1.0
```

(Skip this if you used `docker compose down --rmi local` in 6.1.)

---

## 6.5 Verify everything is gone

```bash
docker ps -a         | grep -E 'backend|frontend'   # should print nothing
docker network ls    | grep -E 'appnet|flask'       # should print nothing
docker images        | grep flask-net               # should print nothing
```

All three returning nothing means the lab left no trace.

---

## 6.6 (Optional) reclaim more space

The `python:3.12-slim` base image is still cached (useful for other labs). To remove **all** unused
images, networks, and build cache system-wide:

```bash
docker system prune -a
```

> ⚠️ `docker system prune -a` deletes **every** unused image on your machine, not just this lab's.
> Only run it if you're sure.

---

## Checkpoint

- [ ] `docker compose down` reported the containers and network removed
- [ ] No `backend`/`frontend` containers in `docker ps -a`
- [ ] `appnet` and any `*_default` network are gone from `docker network ls`
- [ ] `flask-net-*` images are gone from `docker images`

---

🎉 **Done!** You built a two-container app, watched name resolution fail on the default bridge, fixed
it with a user-defined network, reproduced the whole thing with Docker Compose, and cleaned up.

**Where to go next:**
- [Challenges](../challenges.md) — add a database tier, network isolation, DNS aliases, scaling
- [ECS on Fargate Basics](../../../../intermediate/aws/aws-ecs-fargate-basics/README.md) — the same container in the cloud
- [Monolith → Microservices on EKS](../../../../advanced/kubernetes/eks-monolith-to-microservices/README.md) — service-to-service DNS on Kubernetes
