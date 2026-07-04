# Troubleshooting

`Error → Cause → Fix` for the common snags in this project.

---

### `Cannot connect to the Docker daemon`

- **Error:** `Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?`
- **Cause:** Docker Engine isn't running (Desktop app closed, or the Linux service is stopped).
- **Fix:** Start Docker Desktop, or on Linux `sudo systemctl start docker`. Verify with
  `docker run --rm hello-world`.

---

### Frontend returns `503 backend unreachable` with a name-resolution error

- **Error:** JSON like `{"error":"backend unreachable","detail":"...Failed to resolve 'backend'..."}`.
- **Cause:** The two containers are **not on the same user-defined network**. On the **default bridge**,
  Docker does **not** provide DNS resolution by container name — this is expected in **Step 3** and is
  the whole point of the lab.
- **Fix:** Put both containers on a user-defined network (**Step 4**): create it with
  `docker network create appnet` and run each container with `--network appnet`. Then name resolution
  works.

---

### `docker: Error response from daemon: Conflict. The container name "/backend" is already in use`

- **Error:** Container name conflict on `docker run`.
- **Cause:** A container with that name already exists (from an earlier step or a failed run).
- **Fix:** Remove it first: `docker rm -f backend frontend`, then re-run. (`-f` stops it if running.)

---

### `docker: Error ... port is already allocated` (port 8080)

- **Error:** `Bind for 0.0.0.0:8080 failed: port is already allocated`.
- **Cause:** Something else on your host — or a leftover frontend container — is using port 8080.
- **Fix:** Stop the other process, or publish on a different host port: `-p 9090:8080`, then
  `curl localhost:9090`. Find a leftover container with `docker ps` and `docker rm -f <name>`.

---

### `curl localhost:8080` returns *Connection refused*

- **Error:** curl can't connect at all.
- **Cause:** The frontend container isn't running, or you forgot to **publish** its port with `-p 8080:8080`.
  Merely `EXPOSE`-ing a port in the Dockerfile does **not** publish it to the host.
- **Fix:** Confirm `docker ps` shows the frontend with `0.0.0.0:8080->8080/tcp`. If not, re-run with
  `-p 8080:8080`.

---

### Name resolves but the call still fails / times out

- **Error:** frontend logs show a connection error to `backend:5000` even though both are on `appnet`.
- **Cause:** The backend container isn't listening yet (still starting), crashed, or is on a different port.
- **Fix:** Check `docker logs backend` — it should say Flask is running on `0.0.0.0:5000`. Make sure you
  didn't override `PORT`. Give it a second or two after `docker run` before hitting the frontend.

---

### `docker network rm appnet` says the network has active endpoints

- **Error:** `error while removing network: network appnet ... has active endpoints`.
- **Cause:** Containers are still attached to the network.
- **Fix:** Remove the containers first (`docker rm -f backend frontend`), then remove the network.

---

### `docker compose up` can't find the file or build context

- **Error:** `no configuration file provided` or a build error about `./src/backend`.
- **Cause:** You're not in the project root, so the relative `build:` paths don't resolve.
- **Fix:** `cd` into `docker-network-flask-basics/` (the folder containing `docker-compose.yml`) before
  running `docker compose up`.

---

### `docker compose` (v2) vs `docker-compose` (v1)

- **Error:** `docker: 'compose' is not a docker command`.
- **Cause:** The Compose v2 plugin isn't installed; you only have the legacy standalone binary.
- **Fix:** Install the Compose plugin (bundled with Docker Desktop; on Linux see the Docker docs), or
  substitute `docker-compose` (with a hyphen) for `docker compose` in every command.
