# Step 7 — Cleanup

Remove everything this lab created: containers, both networks, the volume, and the images. Nothing
costs money, but the named volume **persists on purpose** — so you have to remove it deliberately.

---

## 7.1 If you used Compose (Step 6)

One command removes the containers, both networks, **and** the volume (note the `-v`):

```bash
docker compose down -v
```

Add `--rmi local` to drop the built images in the same call:

```bash
docker compose down -v --rmi local
```

---

## 7.2 If you used the hand-run containers (Steps 3–5)

Remove the containers first (they hold the networks and volume open):

```bash
docker rm -f edge api 2>/dev/null || true
```

Then the networks:

```bash
docker network rm frontend backend 2>/dev/null || true
```

Then the volume — **this deletes your notes**:

```bash
docker volume rm notes-data 2>/dev/null || true
```

If `volume rm` says the volume is in use, a container still has it mounted — rerun the `docker rm -f`
above first.

---

## 7.3 Remove the images

```bash
docker rmi notes-edge:1.0 notes-api:1.0 2>/dev/null || true
```

(Skip if you used `--rmi local` in 7.1.)

---

## 7.4 Optional: remove the backup tarball

The Step 5 backup lives on your host, not in Docker:

```bash
rm -rf backups/
```

---

## 7.5 Verify everything is gone

```bash
docker ps -a      | grep -E 'edge|api'                 || echo "no containers"
docker network ls | grep -E 'frontend|backend|storage' || echo "no lab networks"
docker volume ls  | grep notes-data                    || echo "no volume"
docker images     | grep -E 'notes-(edge|api)'         || echo "no images"
```

All four printing the "no ..." line means the lab left no trace.

> To also drop the shared `python:3.12-slim` base and any dangling build cache system-wide (affects
> **all** projects, not just this one): `docker system prune -a`. Only if you're sure.

---

## Checkpoint

- [ ] Containers `edge` and `api` are gone
- [ ] Networks `frontend` and `backend` (or the `*_frontend`/`*_backend` Compose ones) are gone
- [ ] The `notes-data` volume is gone
- [ ] `notes-edge`/`notes-api` images are gone

---

🎉 **Done!** You built a segmented, stateful, two-tier app: a public edge fronting an isolated api,
persistent data on a named volume, host-managed config on a bind mount, ephemeral scratch on a tmpfs —
and you backed up and restored the volume through simulated data loss, then declared the whole
topology in Compose.

**Where to go next:**
- [Challenges](../challenges.md) — a real database container, a doubly-isolated tier, read-only rootfs, an automated backup sidecar
- [ECS on Fargate — Advanced](../../../../advanced/aws/aws-ecs-fargate-advanced/README.md) — networks, load balancing, and persistence in AWS
- [k8s Optimization & Recovery](../../../kubernetes/k8s-optimization-and-recovery/README.md) — persistent volumes and backup/restore with Velero
