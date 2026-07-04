# Step 5 — Test and Verify

Confirm both behaviors — **archive** (safe) and **delete** (irreversible) — and learn how to
reason about a janitor that runs unattended every night.

---

## 5.1 Verify Archive Behavior

After an archive run, list the whole bucket:

```bash
aws s3 ls s3://YOUR_BUCKET_NAME/ --recursive
```

You should see objects under `archive/...` and nothing under `active/...`. The nested path is
preserved — `active/logs/app.log` becomes `archive/logs/app.log`.

Check the logs for the move lines:

```bash
aws logs tail /aws/lambda/s3-housekeeper --since 15m
```

```
active/logs/app.log qualifies (LastModified=...)
Moved active/logs/app.log -> archive/logs/app.log
Done. 4 object(s) archiveed
```

---

## 5.2 Try Delete Mode (carefully)

`delete` is irreversible — there's no recycle bin (unless versioning is on; see Challenge 4).
**Dry-run first, always.**

1. Re-seed fresh objects: `python src/seed_objects.py YOUR_BUCKET_NAME`.
2. Switch to delete + dry-run:

```bash
aws lambda update-function-configuration \
  --function-name s3-housekeeper \
  --environment "Variables={BUCKET=YOUR_BUCKET_NAME,PREFIX=active/,ARCHIVE_PREFIX=archive/,ACTION=delete,RETENTION_DAYS=0,DRY_RUN=true}"
python src/test_invoke.py     # lists what WOULD be deleted; nothing removed
```

3. Confirm the list looks right, then set `DRY_RUN=false` and run again. The `active/` objects
   are now gone for good.

```bash
aws s3 ls s3://YOUR_BUCKET_NAME/active/ --recursive   # empty
```

> **Habit to keep:** every time you change `ACTION`, `PREFIX`, or `RETENTION_DAYS`, do one
> `DRY_RUN=true` pass and read the `keys` list before letting it run for real. The cost of a
> dry-run is one cheap invoke; the cost of a wrong `delete` is your data.

---

## 5.3 Reason About a Nightly Janitor

| Question | Answer |
|----------|--------|
| What if it runs and there's nothing old? | `count: 0`, no changes — safe and cheap |
| What if it runs twice (at-least-once)? | Idempotent: archive guards `archive/`; delete on a gone key is a no-op |
| What if the bucket has 1M objects? | The paginator handles all pages; mind the 60s timeout (see Challenge 5) |
| How do I know it's healthy? | `Errors = 0` on the function, `FailedInvocations = 0` on the rule |

---

## 5.4 Check Rule + Function Health

- EventBridge → `s3-housekeeping-schedule` → **Monitoring**: `Invocations` ↑, `FailedInvocations = 0`.
- Lambda → `s3-housekeeper` → **Monitor**: `Errors = 0`, `Duration` well under the timeout.

---

## Checkpoint

- [ ] Archive run moved objects `active/ → archive/`, preserving sub-paths
- [ ] Delete run (after a dry-run) removed `active/` objects permanently
- [ ] A no-op run returns `count: 0` cleanly
- [ ] Rule and function metrics are healthy

---

**Next:** [Step 6 — Cleanup](./06-cleanup.md)
