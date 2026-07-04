# Prerequisites

Everything you need before **Step 1**. Like the beginner lab, this is **fully local** — no cloud
account, no billing, no paid resources.

## Tools

| Tool | Version | Check | Notes |
|------|---------|-------|-------|
| **Docker Engine** | 20.10+ | `docker --version` | Docker Desktop or Docker Engine (Linux) |
| **Docker Compose v2** | 2.x | `docker compose version` | The plugin form (`docker compose`, a space). Used in Step 6 |
| **curl** | any | `curl --version` | Hits the edge gateway. A browser works too |
| **tar** | any | `tar --version` | For the backup step (present on macOS/Linux; the backup helper container also has it) |

> **Docker must be running** and able to pull `python:3.12-slim` (used both for the app images and as
> the backup helper). Verify with `docker run --rm hello-world`.

## Knowledge assumed

- **The beginner Docker networking lab**, done or understood:
  [`docker-network-flask-basics`](../../../beginner/docker/docker-network-flask-basics/README.md).
  You should already know what a **user-defined bridge network** is and that containers resolve each
  other by **name** on one. This project layers *multiple* networks, *isolation*, and *storage* on
  top of that foundation.
- Comfort running multi-flag `docker run` commands and reading JSON.
- You do **not** need to know SQL — the api handles SQLite for you; you only ever add/read notes.

## Ports used

| Port | Used by | Exposed to host? |
|------|---------|------------------|
| `8080` | edge gateway | **Yes** — published so you can `curl localhost:8080` |
| `5000` | api | **No** — internal to the `backend` network; unreachable from the host by design |

If `8080` is busy on your machine, publish the edge on another host port (e.g. `-p 9090:8080`) and
curl that instead.

## Disk

The two images share the `python:3.12-slim` base (~150–200 MB total once). The named volume holds a
tiny SQLite file (kilobytes). All reclaimed in the cleanup step.

## Cost

**$0.** Nothing here creates a cloud resource.
