# Step 3 — Automated Backups and Point-in-Time Recovery

This is the recovery you'll reach for most: someone runs a bad `DELETE` and you need to rewind to
*just before it*. Because you set **backup retention = 7 days** in Step 1, RDS has been quietly
storing a daily snapshot plus transaction logs every 5 minutes — enough to restore to **any
second** in that window.

> **RDS restores never happen in place.** PITR creates a **brand-new instance** with a new
> endpoint, restored to the moment you pick. Your damaged instance is untouched. You verify the
> new one, then cut your app over to it.

---

## 3.1 Cause a "Disaster"

Note the current time (UTC), then delete data — simulating the accident:

```bash
# record this moment first:  date -u
python - <<'PY'
import os, pymysql
c = pymysql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                    password=os.environ["DB_PASSWORD"], database="appdb", autocommit=True)
with c.cursor() as cur:
    cur.execute("DELETE FROM orders WHERE id > 5")   # wipes the second batch
    cur.execute("SELECT COUNT(*) FROM orders"); print("orders now:", cur.fetchone()[0])
PY
```

`db_verify.py` now shows fewer rows. The data is "gone" on the live instance.

---

## 3.2 Restore to a Point in Time

1. **RDS** → **Databases** → select `rds-dr-demo` → **Actions** → **Restore to point in time**.
2. Choose **Custom** restore time and pick a timestamp **after your Step 2 marker but before the
   delete in 3.1**. (Or use **Latest restorable time** to get everything up to ~5 min ago — which
   here would include the delete, so pick a custom earlier time.)
3. New DB identifier: `rds-dr-demo-pitr`.
4. Instance class `db.t3.micro`, same `rds-dr-sg`, **Public access: Yes**.
5. **Restore.** Wait ~10 minutes for **Available**.

```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier rds-dr-demo \
  --target-db-instance-identifier rds-dr-demo-pitr \
  --restore-time 2026-06-19T14:05:00Z \
  --db-instance-class db.t3.micro \
  --publicly-accessible \
  --vpc-security-group-ids <SG_ID> \
  --region us-east-1
```

---

## 3.3 Verify the Rewind

Get the new endpoint and verify against it:

```bash
aws rds describe-db-instances --db-instance-identifier rds-dr-demo-pitr \
  --query 'DBInstances[0].Endpoint.Address' --output text --region us-east-1

python src/db_verify.py --host <PITR_ENDPOINT> --user admin --password '<YOUR_PW>'
```

The restored instance has the rows as they existed **at your chosen time** — the deleted batch is
back. You recovered with an **RPO of seconds** (the gap to the last transaction log) and an **RTO
of ~10 minutes** (the restore time).

> **The endpoint changed.** This is the operational catch of every RDS restore: your app must now
> point at `rds-dr-demo-pitr`. Production teams handle this with a **CNAME / Route 53 record** in
> front of the database so failover is a DNS flip, not a config change everywhere
> ([Challenge 3](../challenges.md)).

---

## Checkpoint

- [ ] You recorded a UTC time, then deleted the second batch of rows
- [ ] `rds-dr-demo-pitr` restored to a time **before** the delete
- [ ] `db_verify.py` against the PITR endpoint shows the deleted rows restored
- [ ] You can explain why the **endpoint changed** and how Route 53 would hide that

> **Cost watch:** you now have **two** instances running. If you're done with the PITR copy,
> delete `rds-dr-demo-pitr` now (no final snapshot needed) to stop its hourly charge — or keep
> going and clean up everything in Step 7.

---

**Next:** [Step 4 — Manual Snapshot and Restore](./04-manual-snapshot-and-restore.md)
