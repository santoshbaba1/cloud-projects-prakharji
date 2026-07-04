# Step 3 — The Default Bridge Limitation (Watch It Fail)

The fastest way to *understand* user-defined networks is to first feel the pain of not having one. In
this step we run both containers on the **default bridge** and watch the frontend fail to find the
backend by name. This failure is the point — don't skip it.

---

## 3.1 Run both containers on the default bridge

When you don't pass `--network`, a container joins the **default bridge** (`bridge`). Start the
backend, then the frontend:

```bash
docker run -d --name backend flask-net-backend:1.0
docker run -d --name frontend -p 8080:8080 flask-net-frontend:1.0
```

- `-d` — detached (runs in the background)
- `--name` — gives each container a stable name
- `-p 8080:8080` — publishes only the frontend to your host

Confirm both are running:

```bash
docker ps
```

You should see `backend` and `frontend` both `Up`.

---

## 3.2 Hit the frontend — and watch it fail

```bash
curl -s localhost:8080/ | python3 -m json.tool
```

You'll get a **503** with a DNS error, something like:

```json
{
    "error": "backend unreachable",
    "backend_url": "http://backend:5000",
    "detail": "HTTPConnectionPool(host='backend', port=5000): ... Failed to resolve 'backend' ..."
}
```

The key phrase is **`Failed to resolve 'backend'`**. The frontend *is* running, the backend *is*
running — but the frontend literally cannot turn the name `backend` into an IP address.

---

## 3.3 Why it failed

The default bridge network does **not** run Docker's embedded DNS for container names. There is no
one to answer "what IP is `backend`?", so the lookup fails before any HTTP request is even attempted.

You can prove the backend is otherwise fine by talking to it **by IP** (which *does* work on the
default bridge). Grab its IP and curl it from inside the frontend container:

```bash
# find the backend's IP on the default bridge
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' backend

# exec into the frontend and curl that IP directly (replace 172.17.0.2)
docker exec -it frontend python3 -c "import requests; print(requests.get('http://172.17.0.2:5000/api/message').json())"
```

That call **succeeds** — the containers *can* reach each other, they just can't do it by **name**.
And hardcoding that IP is exactly the trap we described in Step 1: restart the backend and the IP may
change, breaking the frontend. We want names.

> **Legacy footnote:** the old `--link` flag could inject names on the default bridge, but it's
> deprecated and you should not use it. The modern answer is a user-defined network — Step 4.

---

## 3.4 Tear down these containers

We'll recreate them properly in the next step, so remove them now:

```bash
docker rm -f backend frontend
```

---

## Checkpoint

- [ ] Both containers ran on the default bridge
- [ ] `curl localhost:8080` returned a **503** with **`Failed to resolve 'backend'`**
- [ ] Curling the backend **by IP** worked — proving the issue is name resolution, not connectivity
- [ ] You removed both containers with `docker rm -f`

---

**Next:** [Step 4 — Create a User-Defined Network](04-user-defined-network.md)
