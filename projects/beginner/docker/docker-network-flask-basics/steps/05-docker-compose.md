# Step 5 — Do It All With Docker Compose

You just built the network by hand: `network create`, two `docker run`s with `--network`, and a
published port. **Docker Compose does every one of those for you from a single file.** Now that you
know what's happening underneath, Compose will feel like a convenience rather than magic.

---

## 5.1 Read the Compose file

[`docker-compose.yml`](../docker-compose.yml) in the project root:

```yaml
services:
  backend:
    build: ./src/backend
    image: flask-net-backend:1.0
    container_name: backend
    # No `ports:` — reachable only inside the network, by name.

  frontend:
    build: ./src/frontend
    image: flask-net-frontend:1.0
    container_name: frontend
    environment:
      BACKEND_URL: http://backend:5000
    ports:
      - "8080:8080"
    depends_on:
      - backend
```

Map each line back to what you did by hand:

| By hand (Steps 2–4) | Compose equivalent |
|---------------------|--------------------|
| `docker build -t ... ./src/backend` | `build: ./src/backend` |
| `docker network create appnet` | **automatic** — Compose creates a default network |
| `docker run --network appnet` | **automatic** — every service joins that network |
| `--name backend` | `container_name: backend` (service name works as a DNS name regardless) |
| `-p 8080:8080` | `ports: ["8080:8080"]` |
| start backend before frontend | `depends_on: [backend]` |

> **The network is the part you no longer write.** Compose auto-creates a **user-defined bridge**
> named `<project>_default` (project name = the folder name) and attaches both services to it.
> Because it's user-defined, DNS-by-name works — services reach each other by **service name**
> (`backend`), exactly like Step 4. You get the good network for free.

---

## 5.2 Bring the stack up

> If your hand-run `frontend` from Step 4 is still using host port 8080, either stop it
> (`docker rm -f backend frontend`) or change the Compose host port to `"8081:8080"` first. The
> container **names** `backend`/`frontend` will also collide — removing the Step 4 containers is the
> cleanest path.

From the project root:

```bash
docker compose up -d
```

Compose builds any missing images, creates the network, and starts both services. Watch the output —
it explicitly says it's creating a network:

```
[+] Running 3/3
 ✔ Network docker-network-flask-basics_default  Created
 ✔ Container backend                            Started
 ✔ Container frontend                           Started
```

---

## 5.3 Verify

```bash
curl -s localhost:8080/ | python3 -m json.tool
```

Same **200** and same JSON as Step 4 — the frontend reached the backend by name over the
Compose-created network:

```json
{
    "frontend": "ok",
    "backend_url": "http://backend:5000",
    "backend_said": { "service": "backend", "message": "Hello from the backend service", "...": "..." }
}
```

Confirm the auto-created network and its members:

```bash
docker network ls | grep flask
docker compose ps
```

You'll see the `docker-network-flask-basics_default` network and both services `running`.

---

## 5.4 Read the logs and scale (optional)

Compose aggregates logs from every service:

```bash
docker compose logs frontend
docker compose logs -f            # follow all services, Ctrl+C to stop
```

Try client-side DNS load balancing — run three backends behind the one name:

```bash
docker compose up -d --scale backend=3
```

Now hit the frontend a few times and watch the `container` field change as Docker's DNS round-robins
across the three backend containers:

```bash
for i in 1 2 3 4; do curl -s localhost:8080/ | python3 -c "import sys,json; print(json.load(sys.stdin)['backend_said']['container'])"; done
```

> Scaling `backend` needs the `container_name: backend` line removed (a fixed name can't apply to 3
> containers). This is a nice lead-in to [Challenge 5](../challenges.md).

---

## 5.5 Bring the stack down

```bash
docker compose down
```

That stops and removes both containers **and** the network Compose created — one command undoes
everything `up` did. (Images remain; we remove those in Step 6.)

---

## Checkpoint

- [ ] `docker compose up -d` created a `*_default` network and started both services
- [ ] `curl localhost:8080` returned the backend message via the Compose network
- [ ] You can point to which hand-run commands each Compose line replaced
- [ ] `docker compose down` removed the containers and the network

---

**Next:** [Step 6 — Cleanup](06-cleanup.md)
