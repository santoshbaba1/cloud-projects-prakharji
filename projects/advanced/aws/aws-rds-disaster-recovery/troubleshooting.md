# Troubleshooting — RDS Disaster Recovery

Error → Cause → Fix.

---

## Can't connect: connection times out

**Symptom:** `db_seed.py` / `db_verify.py` hang then fail with a timeout (often
`OperationalError 2003`).

**Causes & fixes:**

1. **Security group doesn't allow your IP.** The SG must allow **3306** from your current public
   IP `/32`. Your IP changes (coffee shop, VPN, ISP reassignment) — re-check `curl
   https://checkip.amazonaws.com` and update the rule.
2. **Public access = No.** The instance must be **Publicly accessible** *and* in a subnet with an
   internet gateway (default VPC public subnets qualify). Restored instances default to the source
   setting — set Public access: Yes on each restore.
3. **Wrong region SG.** The us-west-2 instances need a **us-west-2** security group; an
   us-east-1 SG can't be attached to them.

---

## Access denied for user 'admin'

**Symptom:** `pymysql.err.OperationalError 1045 Access denied`.

**Cause:** Wrong master password, or you're hitting the wrong instance.

**Fix:** Use the master password you set in Step 1. A **restored** instance keeps the *source's*
master credentials — same username/password as the original, not a new one.

---

## "Unknown database 'appdb'"

**Cause:** You didn't set an **initial database name** when creating the instance, so `appdb`
doesn't exist.

**Fix:** `db_seed.py` runs `CREATE DATABASE IF NOT EXISTS appdb` for you — run the **seeder**
first against a fresh instance. `db_verify.py` assumes `appdb` already exists.

---

## PITR: "restore time is not within the restorable window"

**Symptom:** Restore-to-point-in-time rejects your timestamp.

**Causes & fixes:**

1. **Backup retention = 0.** PITR needs automated backups **on**. You set retention to **7 days**
   in Step 1; if it's 0, no PITR is possible — enable backups and wait for the next window.
2. **Time too early or too late.** Valid range is between the **earliest restorable time** and the
   **latest restorable time** (≈ now minus 5 min). Use `describe-db-instances` →
   `LatestRestorableTime` / `EarliestRestorableTime`, and pick a time inside it.
3. **Brand-new instance.** Right after creation there's no history yet — wait until the first
   automated backup completes.

---

## Cross-region copy fails on an encrypted snapshot

**Symptom:** `copy-db-snapshot` to us-west-2 errors about the KMS key.

**Cause:** A KMS-encrypted snapshot can't be decrypted in another region with the source region's
key.

**Fix:** Pass `--kms-key-id` of a **us-west-2** KMS key so the copy is re-encrypted there. (Our
lab DB is unencrypted to avoid this; the encrypted path is [Challenge 6](challenges.md).)

---

## Read replica stuck "Creating" for a long time

**Cause:** Cross-region replicas seed from a snapshot and then catch up — this legitimately takes
10–20+ minutes, longer than a same-region operation.

**Fix:** Be patient; watch the **Status** and the `ReplicaLag` metric. If it errors out, confirm
the source instance has **automated backups enabled** (a replica can't be created from a source
with retention 0).

---

## Can't write to the replica

**Symptom:** Inserts against the replica fail with `--read-only` / `1290`.

**Cause (expected):** A read replica is **read-only** by design until you **promote** it.

**Fix:** This is correct behavior. To make it writable, **Promote** it (Step 6.3). After
promotion, writes succeed.

---

## Can't delete the primary: "instance has read replicas"

**Cause:** RDS won't delete a primary that still has dependent replicas.

**Fix:** **Promote** (or delete) the replica first, then delete the primary
([Step 7.1](steps/07-cleanup.md)).

---

## Surprise bill after you "cleaned up"

**Cause:** Almost always an instance or snapshot left in **us-west-2**. People clean up the region
they were looking at and forget the DR region.

**Fix:** Run the two-region sweep in [Step 7.5](steps/07-cleanup.md). There is **no free idle
state** for an RDS instance — only *deleted* costs nothing.

---

## General debugging checklist

1. SG allows 3306 from your **current** IP, in the **right region**
2. Instance is **Available** and **Publicly accessible**
3. Use the **source's** master username/password on restored instances
4. PITR needs retention > 0 and a timestamp inside the restorable window
5. Replicas are read-only until **promoted**; promotion is one-way
6. After any drill, check **both regions** for leftover instances/snapshots
