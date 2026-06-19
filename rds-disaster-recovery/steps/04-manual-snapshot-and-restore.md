# Step 4 — Manual Snapshot and Restore

Automated backups expire (7 days here) and you don't control their timing. A **manual snapshot**
is a named restore point **you** take and keep until you delete it — perfect before a risky
migration, or as a long-term archive. It's also the unit you'll **copy across regions** in Step 5.

---

## 4.1 Take a Manual Snapshot

1. **RDS** → **Databases** → `rds-dr-demo` → **Actions** → **Take snapshot**.
2. Snapshot name: `rds-dr-demo-snap-1`.
3. **Take snapshot.** It goes **Creating → Available** in a few minutes.

```bash
aws rds create-db-snapshot \
  --db-instance-identifier rds-dr-demo \
  --db-snapshot-identifier rds-dr-demo-snap-1 \
  --region us-east-1

aws rds wait db-snapshot-available \
  --db-snapshot-identifier rds-dr-demo-snap-1 --region us-east-1
```

> A snapshot is **storage-only and crash-consistent** as of the moment you take it. It doesn't run
> or bill like an instance — you pay only for the snapshot storage (pennies at this size). This is
> why teams snapshot *before* anything risky: cheap insurance.

---

## 4.2 Restore the Snapshot to a New Instance

A snapshot isn't usable until you **restore** it into an instance:

1. **RDS** → **Snapshots** → select `rds-dr-demo-snap-1` → **Actions** → **Restore snapshot**.
2. New DB identifier: `rds-dr-demo-fromsnap`, class `db.t3.micro`, SG `rds-dr-sg`,
   **Public access: Yes**.
3. **Restore.** Wait for **Available**.

```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier rds-dr-demo-fromsnap \
  --db-snapshot-identifier rds-dr-demo-snap-1 \
  --db-instance-class db.t3.micro \
  --publicly-accessible \
  --vpc-security-group-ids <SG_ID> \
  --region us-east-1
```

---

## 4.3 Verify

```bash
aws rds describe-db-instances --db-instance-identifier rds-dr-demo-fromsnap \
  --query 'DBInstances[0].Endpoint.Address' --output text --region us-east-1

python src/db_verify.py --host <FROMSNAP_ENDPOINT> --user admin --password '<YOUR_PW>'
```

The data matches what was in `rds-dr-demo` **at snapshot time** — RPO is "since the snapshot,"
RTO is the restore duration.

> **PITR vs manual snapshot:** PITR gives you *any second* but only within the retention window
> and only same-region. A manual snapshot is a *fixed point* but lasts forever and can be
> **copied to another region** (next step) or **shared to another account**. You want both in a
> real DR plan.

---

## Checkpoint

- [ ] Snapshot `rds-dr-demo-snap-1` is **Available**
- [ ] `rds-dr-demo-fromsnap` restored from it and is **Available**
- [ ] `db_verify.py` confirms the data on the restored instance
- [ ] You can state when you'd choose a manual snapshot over PITR

> **Cost watch:** delete `rds-dr-demo-fromsnap` once verified if you want to minimize concurrent
> instances. **Keep the snapshot** `rds-dr-demo-snap-1` — Step 5 copies it across regions.

---

**Next:** [Step 5 — Cross-Region Snapshot Copy](./05-cross-region-copy.md)
