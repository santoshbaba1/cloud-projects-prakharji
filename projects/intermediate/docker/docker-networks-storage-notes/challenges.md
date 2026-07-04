# Challenges

Extensions that push the networking and storage ideas further. Do them in any order.

## 1. Swap SQLite for a real database container

Add a `db` service (`postgres:16-alpine`) on the **backend** network with its own named volume
`db-data:/var/lib/postgresql/data`. Point the api at it (`psycopg`), keeping the api's own `/data`
volume only for backups. Note how the database is *also* unreachable from the host and has no egress —
the same isolation you gave the api. This is the production-shaped version of the lab.

## 2. A third, doubly-isolated tier

Add a `worker` service that only the api talks to. Put it on a **new** internal network `worker-net`
that the edge is *not* on, and attach the api to both `backend` and `worker-net`. Verify the edge
cannot reach the worker at all, but the api can. You've now built three trust zones.

## 3. Prove the volume outlives everything

Add notes, then `docker compose down` (no `-v`). Run `docker volume ls` — the volume is still there.
`docker compose up -d` again and confirm the notes came back. Then repeat with `down -v` and watch
them vanish. Write two sentences on when each is the behaviour you want in production.

## 4. Read-only root filesystem

Run the api with `--read-only` (or `read_only: true` in Compose) so its **container filesystem** is
immutable, relying only on the `/data` volume and `/cache` tmpfs for writes. This is a common
hardening step; find and fix whatever breaks (hint: Flask/tmp paths). Explain why an immutable root +
explicit writable mounts is safer.

## 5. Automated hot-backup sidecar

Turn the Step 5 manual backup into a `backup` service in Compose that mounts `notes-data:/data:ro`
and a host `./backups` dir, and on a schedule (a `while true; sleep; tar` loop, or an entrypoint that
runs once) writes timestamped tarballs. Keep the last N. This is the pattern real backup sidecars use.

## 6. Named volume with a bind-style driver / different location

Create the data volume with explicit driver options that store it at a specific host path
(`docker volume create --driver local --opt type=none --opt o=bind --opt device=/some/path notes-data`).
Compare this to a plain bind mount — when would you prefer a driver-configured volume over a raw bind?

## 7. Container-to-container TLS or a real reverse proxy

Replace the Flask edge with **nginx** (or Traefik/Caddy) as the gateway, reverse-proxying to the api
over the backend network, and terminate HTTPS at the edge with a self-signed cert mounted from a bind
mount. The api stays a pure internal service — exactly how you'd run this for real.

## 8. Observe DNS round-robin with a scaled, stateless tier

Make the api stateless again (point it at the Challenge-1 database) and `docker compose up -d --scale
api=3`. Hit the edge repeatedly and confirm Docker DNS load-balances across the three api replicas
while a single shared database keeps the data consistent.
