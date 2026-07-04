# Step 4 — Storage and Persistence

The api is running with three different mounts. Now we make the differences **visible**: the volume
survives the container being destroyed, the bind mount reflects the host live, and the tmpfs is gone
on restart. This is where "containers are ephemeral, storage is not" stops being a slogan.

> Continues from Step 3 — the `api` and `edge` containers, the `notes-data` volume, and the two
> networks should still be up.

---

## 4.1 Add a couple of notes

```bash
curl -s -X POST localhost:8080/notes -H 'content-type: application/json' -d '{"body":"buy milk"}'
curl -s -X POST localhost:8080/notes -H 'content-type: application/json' -d '{"body":"ship the release"}'
curl -s localhost:8080/notes ; echo
```

You should see your notes with ids and timestamps. These are now in `notes.db` **on the volume**, not
inside the container.

---

## 4.2 The headline test: destroy the container, keep the data

Remove the api container **entirely** — not stop, *remove*:

```bash
docker rm -f api
```

The container is gone. Now recreate it from the image, re-attaching the **same** volume:

```bash
docker run -d --name api \
  --network backend \
  -v notes-data:/data \
  -v "$PWD/config:/config:ro" \
  --tmpfs /cache \
  notes-api:1.0
```

Check your notes:

```bash
curl -s localhost:8080/notes ; echo
```

**They're still there.** A brand-new container, yet the data survived — because it lives in
`notes-data`, whose lifecycle is independent of any container. This is exactly what happens on a real
redeploy: new container, same volume, no data loss.

> **Contrast:** if you had run the api **without** `-v notes-data:/data`, the database would have been
> written into the container's own writable layer and `docker rm` would have taken it with it. Try it
> later if you're curious — run a second api with no volume and watch it start empty.

---

## 4.3 The bind mount: edit config on the host, see it in the app

The page title comes from `config/app.json` on your host, mounted read-only into the api. Change it:

```bash
# edit config/app.json on the host — change "title" to something new, e.g. "My Notes"
```

Because the api reads the file on each request, and a bind mount reflects host changes live, just
re-request:

```bash
curl -s localhost:8080/ | head -2
```

The new title shows up — no rebuild, no copy. That's the bind-mount superpower: the **host** owns the
file. (And because it's mounted `:ro`, the container can't modify it — a safety property, not a bug.)

> If you prefer, `docker restart api` first — either way the change appears because the source of
> truth is your host file.

---

## 4.4 The tmpfs: ephemeral by design

Every note POST writes a marker to `/cache/last_write.txt` on the **tmpfs**. Add a note (so the marker
exists), then read the file straight from inside the container:

```bash
curl -s -X POST localhost:8080/notes -H 'content-type: application/json' -d '{"body":"marker"}' >/dev/null
docker exec api cat /cache/last_write.txt ; echo
```

You'll see a timestamp. Now **restart** the api and read again:

```bash
docker restart api
docker exec api cat /cache/last_write.txt 2>/dev/null || echo "(gone — tmpfs was wiped)"
```

The file is gone — the tmpfs is RAM-backed and tied to the container's run, so a restart wipes it.
Your **notes**, meanwhile, are still intact (volume). Same container, two mounts, two completely
different durability guarantees.

> The api also exposes this marker at its internal `/cache` endpoint (returning `last_write: null`
> once wiped) if you'd rather read it over HTTP from the edge.

---

## 4.5 Inspect the volume

See where Docker keeps it and what's mounted where:

```bash
docker volume inspect notes-data
docker inspect -f '{{json .Mounts}}' api | python3 -m json.tool
```

The `Mounts` output lists all three: the `volume` (`notes-data`), the `bind` (`/config`, `RW:false`),
and the `tmpfs` (`/cache`). One command, the whole storage picture.

---

## Checkpoint

- [ ] Notes added through the edge appear in `GET /notes`
- [ ] After `docker rm -f api` and recreating **with the volume**, the notes are still there
- [ ] Editing `config/app.json` on the host changed the page title (bind mount, live)
- [ ] After `docker restart api`, the `/cache` marker is `null` (tmpfs is ephemeral)
- [ ] `docker inspect` shows the volume, the read-only bind, and the tmpfs

---

**Next:** [Step 5 — Backup and Restore](05-backup-restore.md)
