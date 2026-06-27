# Troubleshooting — Database Migration with AWS DMS

Format: **Error → Cause → Fix.**

---

### Endpoint "Test connection" fails: `Cannot connect ... timeout`

**Cause:** Network path, not credentials. The replication instance can't reach the DB on 3306 —
a security group blocks it, or you used the wrong host (public vs private).

**Fix:** Source endpoint must use the EC2 **private IP**; target must use the **RDS endpoint
hostname**. Add inbound `3306` from the **DMS security group** to both the source EC2 SG and the
RDS SG (Step 3.4). Confirm MySQL is listening (`bind-address` not `127.0.0.1`).

---

### Test connection fails: `Access denied for user 'admin'`

**Cause:** Wrong password, or the user isn't allowed from the DMS host (`'admin'@'%'` missing).

**Fix:** Recreate the user as `'admin'@'%'` (Step 1.4) with the right password. For the target,
use the RDS master credentials from Step 2.

---

### CDC won't start: `binary logging not enabled` / `binlog_format must be ROW`

**Cause:** The source MySQL isn't configured for row-based binary logging, so DMS can't capture
ongoing changes.

**Fix:** Set `log_bin`, `binlog_format=ROW`, `binlog_row_image=FULL`, and a `server-id`, then
restart (Step 1.3). Verify: `SHOW VARIABLES LIKE 'binlog_format';` → `ROW`. The migration user
needs `REPLICATION SLAVE, REPLICATION CLIENT`.

---

### Full load works but CDC shows 0 changes

**Cause:** No writes are happening on the source, or the binlog grant/format is missing so the
binlog stream isn't being read.

**Fix:** Run `cdc_writer.py` against the **source** to generate changes. Confirm the binlog
settings and replication grants from Step 1. Check the task's CloudWatch logs for binlog read
errors.

---

### Task error: `Error during full load ... table already exists`

**Cause:** Target table preparation mode is *Do nothing* but the target already has the tables
(e.g. you re-ran the task).

**Fix:** Use **Drop tables on target** to start clean, or **Truncate**, depending on whether you
want the schema recreated. For a fresh empty RDS, *Do nothing* is correct.

---

### `db_verify.py` checksums differ between source and target

**Cause:** CDC hasn't caught up yet (latency > 0), or writes happened on the source after you
sampled it.

**Fix:** Stop writing to the source, wait for the task's CDC/source latency to reach ~0, then
re-run `db_verify.py` on both. Order-of-rows doesn't affect `CHECKSUM TABLE`, but in-flight CDC
does — let it drain (Step 6.3).

---

### Validation state stuck `Pending` / `Error`

**Cause:** DMS data validation needs a primary key on each table; `orders`/`customers` must have
one (they do here). Large tables also validate slowly.

**Fix:** Confirm every migrated table has a primary key. For this lab they do — give validation a
minute after full load. Check the task's **Validation** statistics for the per-table reason.

---

### RDS target unreachable from your laptop for `db_verify.py`

**Cause:** RDS is `--no-publicly-accessible` (correct), so it's only reachable inside the VPC.

**Fix:** Run `db_verify.py` from the **source EC2** (same VPC) against the RDS endpoint, or use a
bastion/SSM port-forward. Don't make RDS public just to test — that defeats the isolation.

---

### Can't delete the replication instance — "task still references it"

**Cause:** The migration task (or endpoints) still exist.

**Fix:** Delete in order: **task → endpoints → replication instance → subnet group** (Step 7).
A task must be **stopped** before it can be deleted.
