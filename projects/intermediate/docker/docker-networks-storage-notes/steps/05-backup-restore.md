# Step 5 — Backup and Restore

A named volume keeps your data safe from container churn — but not from `docker volume rm`, a disk
failure, or a fat-fingered command. Real operations back volumes up. Here you'll tar the volume out to
your host, **simulate data loss**, and restore it into a fresh volume. This is the canonical Docker
backup pattern, and it works because *any* container can mount the volume.

> Continues from Step 4 — you should have a few notes in `notes-data`.

---

## 5.1 Confirm what we're protecting

```bash
curl -s localhost:8080/notes ; echo
```

Note how many notes you have — you'll verify the same set returns after the restore.

---

## 5.2 Back up the volume to a tarball

The trick: run a **throwaway helper container** that mounts the volume (read-only) **and** a host
directory, then tar one into the other. We use `python:3.12-slim` because you already have it — any
image with `tar` works.

```bash
mkdir -p backups
docker run --rm \
  -v notes-data:/data:ro \
  -v "$PWD/backups:/backup" \
  python:3.12-slim \
  tar czf /backup/notes-backup.tar.gz -C /data .
ls -lh backups/
```

Breakdown:

| Flag | Why |
|------|-----|
| `--rm` | delete the helper as soon as it finishes |
| `-v notes-data:/data:ro` | mount the volume **read-only** — a backup must never mutate the source |
| `-v "$PWD/backups:/backup"` | a host directory to drop the tarball into |
| `tar czf ... -C /data .` | archive everything in the volume |

You now have `backups/notes-backup.tar.gz` on your **host** — safe even if every container and volume
is deleted.

---

## 5.3 Simulate data loss

Detach the volume (remove the api) and destroy it:

```bash
docker rm -f api
docker volume rm notes-data
docker volume ls | grep notes-data || echo "→ notes-data is gone"
```

The database is now genuinely deleted. (If `volume rm` complains the volume is in use, a container
still has it mounted — remove that container first.)

---

## 5.4 Restore into a fresh volume

Recreate an empty volume, then run the helper again — this time **writing** the tarball back in:

```bash
docker volume create notes-data
docker run --rm \
  -v notes-data:/data \
  -v "$PWD/backups:/backup" \
  python:3.12-slim \
  tar xzf /backup/notes-backup.tar.gz -C /data
```

Note the volume is mounted **writable** here (no `:ro`) — we're restoring into it.

---

## 5.5 Bring the api back and verify

```bash
docker run -d --name api \
  --network backend \
  -v notes-data:/data \
  -v "$PWD/config:/config:ro" \
  --tmpfs /cache \
  notes-api:1.0

curl -s localhost:8080/notes ; echo
```

**Your notes are back** — the exact set from 5.1, restored from a tarball into a brand-new volume,
served by a brand-new container. Data outlived both the container **and** the original volume.

> **Why this works:** a volume is just a managed directory. Because its lifecycle is independent of
> any single container, a helper container can mount it to copy data out or in. That same independence
> is why named volumes — not the container filesystem — are where durable data belongs.

---

## 5.6 (Optional) a note on hot backups

We backed up while the api was stopped-ish (we removed it in 5.3). For a database being actively
written, a raw file copy can catch an inconsistent moment. Production answers: use the database's own
dump tool (`pg_dump`, `mysqldump`), enable WAL and copy consistently, or snapshot at the storage
layer. [Challenge 5](../challenges.md) turns this manual backup into an automated sidecar.

---

## Checkpoint

- [ ] `backups/notes-backup.tar.gz` exists on the host
- [ ] `docker volume rm notes-data` deleted the data
- [ ] Restoring the tarball into a fresh `notes-data` brought the notes back
- [ ] You can explain why any container (not just the api) can back up the volume

---

**Next:** [Step 6 — Docker Compose](06-docker-compose.md)
