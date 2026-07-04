# Step 3 — Create the Housekeeper Function

Deploy `s3_housekeeper.py` and run it in **dry-run / archive** mode first — see what it would
touch before anything is moved or deleted.

---

## 3.1 Review the Handler

Open `src/s3_housekeeper.py`. Notice:

```python
paginator = s3.get_paginator("list_objects_v2")
```

- A single `list_objects_v2` returns at most **1000** keys. A real bucket can hold millions, so
  we use a **paginator** to walk every page. Beginners who use a plain `list` silently miss
  everything past the first 1000 objects.

```python
if obj["LastModified"] >= cutoff:
    continue
```

- `LastModified` is timezone-aware (UTC), so we compare against a timezone-aware `cutoff`.
  Anything newer than the cutoff is skipped.

```python
# archive = copy then delete
s3.copy_object(...)
s3.delete_object(...)
```

- S3 has **no move operation**. "Archiving" is copy-to-new-prefix then delete-original.

```python
if ACTION == "archive" and key.startswith(ARCHIVE_PREFIX):
    continue
```

- A guard so an archive run never re-processes objects it already moved into `archive/`.

---

## 3.2 Package and Deploy

```bash
cd /path/to/lambda-s3-housekeeping
zip -j s3_housekeeper.zip src/s3_housekeeper.py
```

Console:

1. **Lambda** → **Create function** → **Author from scratch**.

   | Field | Value |
   |-------|-------|
   | Function name | `s3-housekeeper` |
   | Runtime | **Python 3.14** |
   | Execution role | **Use an existing role** → `S3HousekeeperExecutionRole` |

2. **Create function** → upload `s3_housekeeper.zip` → **Save**.
3. **Configuration → General configuration → Edit:**

   | Setting | Value | Why |
   |---------|-------|-----|
   | Handler | `s3_housekeeper.handler` | filename.function |
   | Memory | 128 MB | listing/copy is light |
   | Timeout | 60 sec | many copy+delete calls add up |

4. **Configuration → Environment variables → Edit**, add:

   | Key | Value |
   |-----|-------|
   | `BUCKET` | `YOUR_BUCKET_NAME` |
   | `PREFIX` | `active/` |
   | `ARCHIVE_PREFIX` | `archive/` |
   | `ACTION` | `archive` |
   | `RETENTION_DAYS` | `0` |
   | `DRY_RUN` | `true` |

5. **Save**.

> `BUCKET` has **no default** in the code — if it's unset the function fails fast at import with
> a `KeyError`. That's deliberate: a housekeeper should never guess which bucket to clean.

---

## 3.3 Dry-Run

```bash
python src/test_invoke.py
```

Expected — it lists what it *would* archive but changes nothing:

```
Response : {
  "action": "archive",
  "dry_run": true,
  "count": 4,
  "keys": ["active/logs/app.log", "active/notes.md", "active/report-feb.txt", "active/report-jan.txt"]
}
```

Confirm the objects are **still under `active/`**:

```bash
aws s3 ls s3://YOUR_BUCKET_NAME/ --recursive
```

---

## 3.4 Turn Off Dry-Run and Archive for Real

Set `DRY_RUN` to `false` (Console env vars, or CLI — remember to pass *all* vars):

```bash
aws lambda update-function-configuration \
  --function-name s3-housekeeper \
  --environment "Variables={BUCKET=YOUR_BUCKET_NAME,PREFIX=active/,ARCHIVE_PREFIX=archive/,ACTION=archive,RETENTION_DAYS=0,DRY_RUN=false}"
```

Run again, then list:

```bash
python src/test_invoke.py
aws s3 ls s3://YOUR_BUCKET_NAME/ --recursive
```

The four objects have moved from `active/...` to `archive/...`. A second run now archives
**0** objects (nothing left under `active/`, and the guard skips `archive/`) — proving the run
is **idempotent**.

---

## Checkpoint

- [ ] `s3-housekeeper` is **Active**, handler `s3_housekeeper.handler`, timeout 60s
- [ ] Dry-run reported 4 keys without moving anything
- [ ] With `DRY_RUN=false`, the objects moved from `active/` to `archive/`
- [ ] A repeat run archived 0 (idempotent)

---

**Next:** [Step 4 — Schedule It with EventBridge](./04-schedule-with-eventbridge.md)
