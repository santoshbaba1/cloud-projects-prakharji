# Step 6 — Docker Compose

You just built two networks (one internal), a named volume, a read-only bind mount, and a tmpfs — by
hand, across several commands. Compose declares **all of it** in one file. Now that you've done it the
hard way, each line maps to something you understand.

> If your hand-run `edge`/`api` from Steps 3–5 are still up, remove them first so names and the host
> port don't collide: `docker rm -f edge api`. (Leave the `notes-data` volume if you want Compose to
> reuse your data — see 6.4.)

---

## 6.1 Read the Compose file

[`docker-compose.yml`](../docker-compose.yml) in the project root. The key sections:

```yaml
services:
  edge:
    image: notes-edge:1.0
    ports: ["8080:8080"]
    networks: [frontend, backend]     # on BOTH — the bridge between tiers
    depends_on: [api]

  api:
    image: notes-api:1.0
    networks: [backend]               # internal only
    volumes:
      - notes-data:/data              # named volume
      - ./config:/config:ro           # read-only bind mount
    tmpfs:
      - /cache                        # tmpfs

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true                    # no egress, no host reach

volumes:
  notes-data:                         # declared here so Compose manages its lifecycle
```

Map it back to your hand-run commands:

| By hand (Steps 3–5) | Compose |
|---------------------|---------|
| `docker network create frontend` | `networks: { frontend: { driver: bridge } }` |
| `docker network create --internal backend` | `networks: { backend: { internal: true } }` |
| `docker volume create notes-data` | top-level `volumes: { notes-data: }` |
| `--network backend`, `docker network connect backend edge` | per-service `networks:` lists |
| `-v notes-data:/data` | `volumes: [notes-data:/data]` |
| `-v "$PWD/config:/config:ro"` | `volumes: [./config:/config:ro]` |
| `--tmpfs /cache` | `tmpfs: [/cache]` |
| `-p 8080:8080` | `ports: ["8080:8080"]` |

Everything you reasoned about is now declarative.

---

## 6.2 Bring the stack up

From the project root:

```bash
docker compose up -d
```

Watch Compose create the networks and volume, then start both services:

```
[+] Running 5/5
 ✔ Network docker-networks-storage-notes_frontend   Created
 ✔ Network docker-networks-storage-notes_backend    Created
 ✔ Volume  docker-networks-storage-notes_notes-data Created
 ✔ Container api                                     Started
 ✔ Container edge                                    Started
```

> Compose **prefixes** networks and volumes with the project name (the folder), e.g.
> `docker-networks-storage-notes_notes-data`. That's why a hand-created `notes-data` and a
> Compose `notes-data` are *different* volumes unless you tell Compose otherwise.

---

## 6.3 Verify — same app, same isolation

```bash
curl -s -X POST localhost:8080/notes -H 'content-type: application/json' -d '{"body":"via compose"}'
curl -s localhost:8080/notes ; echo
```

Spot-check that the isolation Compose set up matches Step 3:

```bash
docker compose exec api python3 -c "import socket; socket.setdefaulttimeout(4); socket.create_connection(('1.1.1.1',443))" \
  || echo "→ api still has no egress (internal network, via Compose)"
docker compose ps
```

---

## 6.4 The `down` vs `down -v` distinction (important)

Bring the stack down but **keep the data**:

```bash
docker compose down
docker volume ls | grep notes-data     # still there
```

`down` removes containers and networks but **preserves named volumes** — so `docker compose up -d`
again brings your notes right back. Prove it:

```bash
docker compose up -d
curl -s localhost:8080/notes ; echo    # "via compose" is still there
```

To remove the volume too — a real teardown — add `-v`:

```bash
docker compose down -v
docker volume ls | grep notes-data || echo "→ volume removed"
```

> **Remember this in production:** `down` is a safe redeploy (data kept); `down -v` is a destroy
> (data gone). Reaching for `-v` out of habit is how people delete databases.

---

## Checkpoint

- [ ] `docker compose up -d` created two networks (one internal), a volume, and both containers
- [ ] You can map every Compose line to the hand-run command it replaces
- [ ] The api still has no egress under Compose
- [ ] `docker compose down` kept the volume; `up` again restored the notes
- [ ] `docker compose down -v` removed the volume

---

**Next:** [Step 7 — Cleanup](07-cleanup.md)
