# Troubleshooting

`Error → Cause → Fix` for the common snags in this project.

---

### Edge returns `503 api unreachable`

- **Error:** `curl localhost:8080/` returns `{"error":"api unreachable", ...}`.
- **Cause:** The edge can't reach the api. Usually the edge isn't attached to the **`backend`**
  network, or the api container isn't running yet.
- **Fix:** Confirm the edge is on **both** networks: `docker inspect -f '{{json .NetworkSettings.Networks}}' edge` should list `frontend` **and** `backend`. Confirm the api is `Up` (`docker ps`) and check `docker logs api`. If you ran them by hand, the edge needs `--network frontend` **and** a second `docker network connect backend edge`.

---

### `curl localhost:5000` (the api) refuses / times out — is that a bug?

- **Not a bug — that's the point.** The api has **no published port** and lives on an internal
  network. It is *supposed* to be unreachable from the host. Reach the app through the edge on
  `:8080`. To talk to the api directly for debugging, exec through the edge:
  `docker exec edge python3 -c "import requests; print(requests.get('http://api:5000/health').json())"`.

---

### The api's outbound internet call *succeeds* when it should fail

- **Error:** In Step 3, an egress test from inside the api returns data instead of failing.
- **Cause:** The `backend` network wasn't created as **internal**. A normal bridge has a gateway and
  allows egress.
- **Fix:** Recreate it: `docker network rm backend` (detach containers first) then
  `docker network create --internal backend`. In Compose, ensure `backend:` has `internal: true`.

---

### My notes disappeared after recreating the api

- **Cause:** You recreated the container **without** re-attaching the named volume, or you removed the
  volume. Data lives in the volume, not the container — if the new container has no
  `-v notes-data:/data`, it starts empty (and creates a *new* anonymous DB inside the container layer).
- **Fix:** Always run the api with `-v notes-data:/data`. Verify the volume still exists with
  `docker volume ls | grep notes-data` and inspect it with `docker volume inspect notes-data`.

---

### `docker volume rm notes-data` says the volume is in use

- **Error:** `volume is in use - [<container id>]`.
- **Cause:** A container (the api, or a leftover) still has the volume mounted.
- **Fix:** Stop/remove the container first: `docker rm -f api`, then remove the volume. With Compose,
  `docker compose down` detaches it; then `docker volume rm <project>_notes-data`.

---

### Editing `config/app.json` didn't change the page

- **Cause:** The api reads the config **on each `/config` request**, but the browser may show a
  cached page, or you edited a different file than the one bind-mounted. Also, a bind mount reflects
  host changes live, but only for the path you actually mounted (`./config`).
- **Fix:** Re-request `curl localhost:8080/` (or hard-refresh). Confirm the mount with
  `docker inspect -f '{{json .Mounts}}' api`. If you changed the mount path, restart the api.

---

### `read-only file system` when the api writes

- **Error:** api logs show `Read-only file system` on `/config`.
- **Cause:** `/config` is intentionally mounted `:ro`. The app never writes there — only `/data`
  (volume) and `/cache` (tmpfs) are writable.
- **Fix:** Nothing to fix if it's the config path — that's correct. If you added code that writes
  config, point it at `/data` instead, or drop the `:ro` flag (not recommended).

---

### `bind source path does not exist: .../config`

- **Cause:** You ran `docker run` from a directory where `./config` doesn't resolve, so the bind
  source is missing.
- **Fix:** Use an absolute path (`-v "$PWD/config:/config:ro"`) and run from the project root, or
  `cd` into the project directory first.

---

### `port is already allocated` (8080)

- **Cause:** Another process or a leftover edge container holds host port 8080.
- **Fix:** `docker rm -f edge`, or publish elsewhere: `-p 9090:8080` (then curl `:9090`).

---

### `docker compose down` didn't delete my data

- **Not a bug.** `down` removes containers and networks but **keeps named volumes** on purpose, so a
  redeploy doesn't wipe your database. To also remove the volume, use `docker compose down -v`.
