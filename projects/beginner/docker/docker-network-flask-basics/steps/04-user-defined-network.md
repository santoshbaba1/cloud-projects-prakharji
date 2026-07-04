# Step 4 — Create a User-Defined Network (Connectivity Works)

Now we fix Step 3's failure the right way: create our own bridge network, attach both containers to
it, and watch name resolution — and the whole app — start working. This is the heart of the lab.

---

## 4.1 Create the network

```bash
docker network create appnet
```

That's it. `create` with no `--driver` gives you a **bridge** network by default — but because *you*
created it, it's a **user-defined** bridge, which means Docker's embedded DNS is switched on for it.

List your networks to see it:

```bash
docker network ls
```

```
NETWORK ID     NAME      DRIVER    SCOPE
...            appnet    bridge    local
...            bridge    bridge    local
...            host      host      local
...            none      null      local
```

---

## 4.2 Run both containers on `appnet`

Same `docker run` commands as Step 3, with one addition: `--network appnet`.

```bash
docker run -d --name backend --network appnet flask-net-backend:1.0
docker run -d --name frontend --network appnet -p 8080:8080 flask-net-frontend:1.0
```

Both containers are now on `appnet`, and each is reachable by its `--name`.

---

## 4.3 Hit the frontend — this time it works

```bash
curl -s localhost:8080/ | python3 -m json.tool
```

Expected — a **200** with the backend's message nested inside:

```json
{
    "frontend": "ok",
    "backend_url": "http://backend:5000",
    "backend_said": {
        "container": "<backend-hostname>",
        "message": "Hello from the backend service",
        "service": "backend"
    }
}
```

The **only** thing that changed from Step 3 is the network. Same images, same code, same
`http://backend:5000` — but now the name `backend` resolves, so the call goes through.

---

## 4.4 See the DNS resolution yourself

Exec into the frontend and look up the name directly:

```bash
docker exec -it frontend python3 -c "import socket; print(socket.gethostbyname('backend'))"
```

It prints the backend's IP (e.g. `172.18.0.2`) — resolved by Docker's embedded DNS at `127.0.0.11`.
On the default bridge in Step 3, this same lookup raised an error.

---

## 4.5 Inspect the network

See both containers attached, with their IPs:

```bash
docker network inspect appnet
```

Look at the `"Containers"` block — you'll see `backend` and `frontend`, each with an `IPv4Address` on
the network's subnet. For a quick one-liner:

```bash
docker network inspect appnet -f '{{range .Containers}}{{.Name}} → {{.IPv4Address}}{{"\n"}}{{end}}'
```

```
backend → 172.18.0.2/16
frontend → 172.18.0.3/16
```

> **Why this is the fix:** Docker's DNS maps the *name* to whatever IP the container currently has. If
> the backend restarts and gets `172.18.0.9`, the frontend's next lookup of `backend` returns the new
> IP automatically. Names are stable; IPs are not. That's the whole reason user-defined networks
> exist.

---

## 4.6 (Optional) attach and detach a running container

You can connect a container to another network without recreating it:

```bash
docker network create appnet2
docker network connect appnet2 backend   # backend now on BOTH networks
docker network disconnect appnet2 backend
docker network rm appnet2
```

This is how you'd give one container a foot in two network segments (see Challenge 3).

---

## 4.7 Leave it running for now

Keep `backend` and `frontend` up — Step 5 will run the Compose version alongside them (on a
different published port), and Step 6 cleans everything up. If you'd rather tidy now, jump to
[Step 6](06-cleanup.md) and come back.

---

## Checkpoint

- [ ] `docker network create appnet` succeeded and shows in `docker network ls`
- [ ] Both containers run with `--network appnet`
- [ ] `curl localhost:8080` returned **200** with the backend's message
- [ ] `socket.gethostbyname('backend')` from inside the frontend returned an IP
- [ ] `docker network inspect appnet` lists both containers

---

**Next:** [Step 5 — Do It All With Docker Compose](05-docker-compose.md)
