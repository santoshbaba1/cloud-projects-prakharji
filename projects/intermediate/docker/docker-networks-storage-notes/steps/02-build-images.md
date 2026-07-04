# Step 2 — Build the Two Images

Same idea as the beginner lab: build the images before we wire up networks and storage. The new thing
to notice is the **api's storage-aware code** — it's written to use the three mounts we'll attach.

---

## 2.1 Tour the storage-aware api

Open [`src/api/app.py`](../src/api/app.py). Three environment-driven paths line up with the three
mounts we'll add in Step 3:

```python
DATA_DIR   = os.environ.get("DATA_DIR",   "/data")     # named volume  -> SQLite lives here
CONFIG_PATH= os.environ.get("CONFIG_PATH","/config/app.json")  # bind mount (ro)
CACHE_DIR  = os.environ.get("CACHE_DIR",  "/cache")    # tmpfs -> ephemeral marker
```

- `/data/notes.db` is the SQLite database. Because `/data` will be a **named volume**, the database
  outlives the container.
- `/config/app.json` is read on every `/config` request. Because `/config` will be a **read-only bind
  mount**, editing the file on your host changes the app — and the app can't write back.
- `/cache/last_write.txt` is written on every note. Because `/cache` will be a **tmpfs**, that marker
  vanishes when the container stops.

The api does **not** care whether those paths are mounts or plain directories — that's the point of
Docker storage. The code stays the same; the `docker run` flags decide the durability.

---

## 2.2 Build both images

From the **project root** (the folder with `docker-compose.yml`):

```bash
docker build -t notes-api:1.0 ./src/api
docker build -t notes-edge:1.0 ./src/edge
```

- `notes-api:1.0` — the private, stateful service (Flask + SQLite; SQLite ships with Python, so no
  extra dependency).
- `notes-edge:1.0` — the gateway (Flask + `requests`).

---

## 2.3 Verify

```bash
docker images | grep -E 'notes-(api|edge)'
```

Expected — two images:

```
notes-edge   1.0   <id>   ...   ~150MB
notes-api    1.0   <id>   ...   ~130MB
```

---

## 2.4 (Optional) sanity-check the api alone with a volume

Run the api by itself, giving it a throwaway volume so you can see it persist, and publish its port
*just this once* to talk to it directly:

```bash
docker run --rm -d --name api-test -p 5000:5000 -v test-vol:/data notes-api:1.0
curl -s -X POST localhost:5000/notes -H 'content-type: application/json' -d '{"body":"first note"}'
curl -s localhost:5000/notes ; echo
docker rm -f api-test
docker volume rm test-vol
```

You'll see the note echoed back, then listed. We remove the test container and its volume right away —
in the real lab the api is **never** published; the edge reaches it over the private network instead.

---

## Checkpoint

- [ ] `docker images` shows `notes-api:1.0` and `notes-edge:1.0`
- [ ] You can point to the three storage paths in the api code and say what each becomes
- [ ] (Optional) the standalone api saved and listed a note on a volume
- [ ] No leftover `api-test` container or `test-vol` volume

---

**Next:** [Step 3 — Networks and Isolation](03-networks-and-isolation.md)
