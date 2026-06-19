# Step 6 — Cross-Region Read Replica & Failover

Snapshot copy (Step 5) has a real weakness: your DR data is only as fresh as the **last copy**.
If snapshots copy nightly, a disaster at noon loses up to a day. A **cross-region read replica**
fixes that — it continuously replicates the primary into us-west-2, so the DR copy is seconds
behind. On disaster you **promote** it to a standalone primary. This is the **lowest-RTO** option
in the series.

---

## 6.1 Create the Cross-Region Read Replica

1. **RDS** → **Databases** → `rds-dr-demo` → **Actions** → **Create read replica**.
2. Settings:

   | Field | Value |
   |-------|-------|
   | Destination region | **us-west-2** |
   | DB instance identifier | `rds-dr-replica` |
   | Instance class | `db.t3.micro` |
   | Public access | **Yes** (lab) |

3. **Create read replica.** Creating a cross-region replica takes longer (it seeds from a
   snapshot, then catches up) — ~10–20 minutes.

```bash
aws rds create-db-instance-read-replica \
  --db-instance-identifier rds-dr-replica \
  --source-db-instance-identifier arn:aws:rds:us-east-1:<ACCOUNT_ID>:db:rds-dr-demo \
  --db-instance-class db.t3.micro \
  --publicly-accessible \
  --region us-west-2
```

> A read replica is **read-only** and **asynchronous**. Writes go to the primary; the replica
> applies them a short time later (**replica lag**). Check lag with the `ReplicaLag` CloudWatch
> metric — that lag *is* your RPO if you fail over right now.

---

## 6.2 Write to the Primary, Watch It Appear on the Replica

Add a row on the **primary** (us-east-1), then read the **replica** (us-west-2) a few seconds
later:

```bash
python src/db_seed.py --host <PRIMARY_ENDPOINT> --user admin --password '<YOUR_PW>' --rows 1
sleep 10
python src/db_verify.py --host <REPLICA_ENDPOINT> --user admin --password '<YOUR_PW>'
```

The new row shows up on the replica without you copying anything — that's continuous replication.
Trying to *write* to the replica fails (`--read-only`), proving it's a replica, not a primary.

---

## 6.3 Fail Over: Promote the Replica

Now simulate losing us-east-1. **Promote** the replica — it becomes an independent, writable
primary in us-west-2 and stops replicating:

1. **RDS** (region us-west-2) → `rds-dr-replica` → **Actions** → **Promote**.
2. Confirm. Promotion takes a few minutes (the instance reboots).

```bash
aws rds promote-read-replica \
  --db-instance-identifier rds-dr-replica --region us-west-2
```

After promotion, verify it's now writable:

```bash
python src/db_seed.py --host <REPLICA_ENDPOINT> --user admin --password '<YOUR_PW>' --rows 1
python src/db_verify.py --host <REPLICA_ENDPOINT> --user admin --password '<YOUR_PW>'
```

The write **succeeds** — `rds-dr-replica` is now a standalone primary. You've completed a
**cross-region failover** with an RPO of seconds (the replica lag at promotion) and the lowest RTO
in this project (promote + reboot, no full restore).

> **The catch:** promotion is **one-way**. Once promoted, the replica no longer follows the old
> primary; you now have two independent databases that will **diverge**. Real failover runbooks
> include a *failback* plan — re-establish replication in the other direction once the original
> region recovers ([Challenge 5](../challenges.md)). This is why replicas give the best RTO but
> demand the most operational discipline.

---

## Checkpoint

- [ ] `rds-dr-replica` came up in us-west-2 and showed **Replicating**
- [ ] A row written to the primary appeared on the replica within seconds
- [ ] After **Promote**, the replica accepts writes (it's now standalone)
- [ ] You can explain replica lag = RPO, and why promotion is one-way

---

**Next:** [Step 7 — Cleanup](./07-cleanup.md)
