# Prerequisites

Everything you need before **Step 1**. This lab is **fully local** — no cloud account, no billing,
no paid resources.

## Tools

| Tool | Version | Check | Notes |
|------|---------|-------|-------|
| **Docker Engine** | 20.10+ | `docker --version` | Docker Desktop (macOS/Windows) or Docker Engine (Linux) both work |
| **Docker Compose v2** | 2.x | `docker compose version` | The **plugin** form (`docker compose`, a space). The legacy `docker-compose` binary also works but this lab uses v2 syntax |
| **curl** | any | `curl --version` | Used to hit the frontend. A browser works too |

> **Docker must be running.** On Docker Desktop, start the app. On Linux, `sudo systemctl start docker`
> (and consider adding yourself to the `docker` group so you don't need `sudo` — see the Docker docs).

Verify the daemon is up:

```bash
docker run --rm hello-world
```

If that prints "Hello from Docker!", you're ready.

## Knowledge assumed

- You can run commands in a terminal and read JSON output.
- You've seen a `Dockerfile` before, or are willing to take Step 2 on faith — it's four lines.
- **No networking theory required.** Step 1 teaches the two concepts you need (bridge networks and
  Docker's embedded DNS) from scratch.

## Ports used

| Port | Used by | Exposed to your host? |
|------|---------|----------------------|
| `5000` | backend Flask app | No — internal to the Docker network |
| `8080` | frontend Flask app | Yes — published so you can `curl localhost:8080` |

Make sure nothing else on your machine is already listening on **8080**. If it is, publish the
frontend on a different host port (e.g. `-p 9090:8080`) and curl that instead.

## Cost

**$0.** Nothing in this project creates a cloud resource. The only footprint is local disk for the
two images (~150 MB total), reclaimed in the cleanup step.
