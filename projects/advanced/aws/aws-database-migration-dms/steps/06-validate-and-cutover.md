# Step 6 — Validate & Cut Over

The target is loaded and CDC is streaming. Now you do the two things that make a migration
*trustworthy*: **prove the data matches** (validation) and **demonstrate live changes replicate**
(CDC), then perform a controlled **cutover** to RDS. This is where RPO/RTO stop being theory.

---

## 6.1 Demonstrate CDC with Live Writes

While the task sits in *replication ongoing*, keep writing to the **source** and watch the rows
appear in the **target**:

```bash
# write 20 live orders to the SOURCE over 20 seconds
python3 src/cdc_writer.py --host <source-public-ip> --user admin \
  --password 'ChangeMe_Strong#1' --count 20

# within seconds, the TARGET should show 20 more orders (status CDC-LIVE)
python3 src/db_verify.py --host <rds-endpoint> --user admin --password 'ChangeMe_Strong#1'
```

The new orders land in RDS without any further action — that's CDC replaying the binlog. **The
source stayed open the entire time.** That's the near-zero-downtime property.

---

## 6.2 Validate Parity

Two independent checks:

1. **Your own check:** run `db_verify.py` against **source** and **target**; the row counts and
   `CHECKSUM TABLE` values must be identical.
2. **DMS validation:** open the task → **Table statistics** → the **Validation state** column
   should read **Validated** for each table (this is the validation you enabled in Step 5).

```bash
# CDC latency near zero means the target is caught up — safe to cut over
aws dms describe-replication-tasks \
  --query 'ReplicationTasks[?ReplicationTaskIdentifier==`dms-migration-task`].ReplicationTaskStats' \
  --output json
```

> **RPO in practice:** if you cut over while CDC latency ≈ 0, the data you lose is essentially
> nothing — that's a low **Recovery Point Objective**. The brief moment you stop source writes
> and repoint the app is your **RTO** (downtime).

---

## 6.3 Cut Over to RDS

The disciplined sequence — stop writes, let CDC drain, switch, verify:

1. **Quiesce the source:** stop the application writing to the source MySQL (and stop
   `cdc_writer.py`). For a real app, put it in maintenance mode briefly.
2. **Let CDC drain:** wait until the task's CDC latency / *source latency* reaches ~0 so the last
   writes have replicated.
3. **Repoint the app:** change your application's DB connection string from the **source EC2
   host** to the **RDS endpoint**. (In this lab, "the app" is `db_verify.py` — just run it
   against RDS from now on.)
4. **Verify on the target:** confirm counts/checksums on RDS include the final writes.
5. **Stop the task:** once the app is on RDS and verified, stop `dms-migration-task` — CDC is no
   longer needed.

```bash
aws dms stop-replication-task --replication-task-arn <task-arn>
```

> **Why stop writes before repointing?** If both the source and the app-on-RDS take writes at
> once, they diverge (split-brain). A clean cutover means **one** writable database at a time:
> source → (brief pause, drain CDC) → RDS.

---

## 6.4 You've Migrated

`shopdb` now lives on **managed RDS**, with every row — including the CDC-LIVE orders written
during migration — intact. You performed a **Replatform** with **near-zero downtime** via full
load + CDC, and you *proved* parity rather than hoping for it.

---

## Checkpoint

- [ ] `cdc_writer.py` orders appeared in RDS within seconds (CDC proven)
- [ ] `db_verify.py` source vs target: identical counts **and** checksums
- [ ] DMS shows tables **Validated**; CDC latency ≈ 0
- [ ] App (here, `db_verify.py`) now points at the **RDS endpoint**
- [ ] Source writes stopped; task stopped after cutover

---

**Next:** [Step 7 — Cleanup](./07-cleanup.md)
