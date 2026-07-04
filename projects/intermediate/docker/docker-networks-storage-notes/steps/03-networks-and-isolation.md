# Step 3 — Networks and Isolation

Now the interesting part. We create **two** networks — a normal `frontend` and an **internal**
`backend` — put the api on the private one only, the edge on both, and then **prove** the isolation
with our own eyes.

---

## 3.1 Create the two networks and the volume

```bash
docker network create frontend
docker network create --internal backend
docker volume create notes-data
```

- `frontend` — a normal bridge (has a gateway → internet + host reach).
- `backend` — created with **`--internal`**: no gateway, so no egress and no host reach. This is the
  private tier.
- `notes-data` — the named volume for the SQLite database (used in this step and the next).

Confirm:

```bash
docker network ls | grep -E 'frontend|backend'
docker volume ls  | grep notes-data
```

---

## 3.2 Run the api on the private network, with all three mounts

```bash
docker run -d --name api \
  --network backend \
  -v notes-data:/data \
  -v "$PWD/config:/config:ro" \
  --tmpfs /cache \
  notes-api:1.0
```

Read the flags — this is the whole storage story on one command:

| Flag | Meaning |
|------|---------|
| `--network backend` | api joins **only** the internal network |
| `-v notes-data:/data` | **named volume** → persistent SQLite |
| `-v "$PWD/config:/config:ro"` | **bind mount**, read-only → host-managed config |
| `--tmpfs /cache` | **tmpfs** → ephemeral scratch in RAM |

> No `-p` for the api — it is never published. Run this from the **project root** so `$PWD/config`
> resolves to the real config directory.

---

## 3.3 Run the edge on both networks

A container can only be given **one** `--network` at `run` time, so we attach the second one right
after with `docker network connect`:

```bash
docker run -d --name edge \
  --network frontend \
  -p 8080:8080 \
  -e API_URL=http://api:5000 \
  notes-edge:1.0

docker network connect backend edge
```

Now `edge` is on `frontend` (published to your host) **and** `backend` (so it can resolve and reach
`api`).

---

## 3.4 It works — through the front door

```bash
curl -s localhost:8080/ | head
```

You'll get HTML with the title from the bind-mounted config and `(no notes yet)`. Add one:

```bash
curl -s -X POST localhost:8080/notes -H 'content-type: application/json' -d '{"body":"hello from step 3"}'
curl -s localhost:8080/notes ; echo
```

The edge proxied both calls to the api over the `backend` network. 

---

## 3.5 Prove the isolation (three experiments)

**A — the api is NOT reachable from the host.** It has no published port and lives on an internal
network:

```bash
curl -s --max-time 3 localhost:5000/health || echo "→ api is unreachable from the host (expected)"
```

You get *connection refused* / a timeout. Good — nothing on your machine can reach the api directly.

**B — but the edge CAN reach it, by name.** Exec into the edge and call the api:

```bash
docker exec edge python3 -c "import requests; print(requests.get('http://api:5000/health').json())"
```

Prints `{'status': 'ok', 'service': 'api', ...}`. The edge is on `backend`, so DNS resolves `api` and
the call succeeds.

**C — the api has NO internet egress.** Try an outbound call *from inside the api* (short timeout so
it fails fast):

```bash
docker exec api python3 -c "import socket; socket.setdefaulttimeout(4); socket.create_connection(('1.1.1.1',443))" \
  && echo "reached internet (unexpected!)" \
  || echo "→ api has no internet egress (expected — internal network)"
```

It fails — because `backend` is internal, the api has no route out. Compare with the edge, which
*does* have egress (it's on `frontend` too):

```bash
docker exec edge python3 -c "import socket; socket.setdefaulttimeout(4); socket.create_connection(('1.1.1.1',443)); print('edge reached internet')"
```

> **What you just proved:** the api can do its job (serve the edge, read/write its volume) while being
> unreachable from the host **and** unable to call out. That's network segmentation — the security
> backbone of every real multi-tier app.

---

## 3.6 (Optional) look at who's on each network

```bash
docker network inspect backend  -f '{{range .Containers}}{{.Name}} {{end}}'   # → api edge
docker network inspect frontend -f '{{range .Containers}}{{.Name}} {{end}}'   # → edge
```

---

## Checkpoint

- [ ] Two networks exist; `backend` is `internal`
- [ ] The api runs on `backend` only, with volume + bind mount + tmpfs
- [ ] The edge runs on `frontend` and was connected to `backend`
- [ ] `curl localhost:8080/` works; a note round-trips
- [ ] Host → api is refused; edge → api works; api → internet fails; edge → internet works

Leave everything running — Step 4 uses these containers.

---

**Next:** [Step 4 — Storage and Persistence](04-storage-persistence.md)
