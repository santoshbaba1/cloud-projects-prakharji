# Step 2 — Build the Two Images

Before containers can run, we need images. In this step you'll build the `backend` and `frontend`
images from their Dockerfiles. Nothing here touches networking yet — we're just getting the two
services ready to run.

---

## 2.1 Look at what you're building

Each service is one small `app.py`, one `requirements.txt`, and a four-line `Dockerfile`. The
Dockerfiles are identical except for the exposed port:

**[`src/backend/Dockerfile`](../src/backend/Dockerfile)**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

> **`EXPOSE` is documentation, not publishing.** `EXPOSE 5000` records that the app listens on 5000;
> it does **not** open the port to your host. Only `-p` / `--publish` at `docker run` time (or `ports:`
> in Compose) actually publishes a port. We rely on this: the backend is exposed but never published,
> so it's reachable only from inside the Docker network — exactly what we want for an internal API.

The frontend Dockerfile is the same but `EXPOSE 8080`, and its `requirements.txt` adds `requests`
(it makes an HTTP call to the backend).

---

## 2.2 Build both images

Run these from the **project root** (the folder containing `docker-compose.yml`):

```bash
docker build -t flask-net-backend:1.0 ./src/backend
docker build -t flask-net-frontend:1.0 ./src/frontend
```

- `-t flask-net-backend:1.0` — **tags** the image `name:version` so we can refer to it later.
- `./src/backend` — the **build context**: the folder Docker sends to the daemon and where it looks
  for the `Dockerfile`.

The first build downloads the `python:3.12-slim` base image (~50 MB) and installs Flask; subsequent
builds are cached and near-instant.

---

## 2.3 Verify

```bash
docker images | grep flask-net
```

Expected — two images:

```
flask-net-frontend   1.0   <id>   ...   ~150MB
flask-net-backend    1.0   <id>   ...   ~130MB
```

---

## 2.4 (Optional) sanity-check one container in isolation

Run the backend alone, publishing its port just this once so you can hit it directly:

```bash
docker run --rm -d --name backend-test -p 5000:5000 flask-net-backend:1.0
curl localhost:5000/api/message
docker rm -f backend-test
```

You should get:

```json
{"container":"<hostname>","message":"Hello from the backend service","service":"backend"}
```

That proves the image works. Note we had to **publish** `-p 5000:5000` to reach it from the host —
in the real lab the backend is never published; the *frontend* reaches it over the Docker network
instead. We remove this test container right away so it doesn't collide with later steps.

---

## Checkpoint

- [ ] `docker images` shows `flask-net-backend:1.0` and `flask-net-frontend:1.0`
- [ ] You understand that `EXPOSE` documents a port but `-p` is what publishes it
- [ ] (Optional) the standalone backend returned its JSON message
- [ ] No leftover `backend-test` container (`docker ps -a` is clean)

---

**Next:** [Step 3 — The Default Bridge Limitation](03-default-bridge.md)
