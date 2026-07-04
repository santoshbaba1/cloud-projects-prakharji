# Step 5 — Cross-Region Snapshot Copy

Everything so far lives in **us-east-1**. If that region had an outage, all of it would be
unreachable. The simplest regional-resilience pattern is to **copy a snapshot to a second
region** so you can rebuild there. Your DR region is **us-west-2**.

---

## 5.1 Copy the Snapshot to us-west-2

1. **RDS** → **Snapshots** → `rds-dr-demo-snap-1` → **Actions** → **Copy snapshot**.
2. Settings:

   | Field | Value |
   |-------|-------|
   | Destination Region | **US West (Oregon) us-west-2** |
   | New snapshot identifier | `rds-dr-demo-snap-1-usw2` |
   | Encryption | leave as source (unencrypted lab snapshot copies fine) |

3. **Copy snapshot.** The copy transfers across regions — a few minutes for a small DB.

```bash
SRC_ARN=$(aws rds describe-db-snapshots \
  --db-snapshot-identifier rds-dr-demo-snap-1 \
  --query 'DBSnapshots[0].DBSnapshotArn' --output text --region us-east-1)

aws rds copy-db-snapshot \
  --source-db-snapshot-identifier "$SRC_ARN" \
  --target-db-snapshot-identifier rds-dr-demo-snap-1-usw2 \
  --region us-west-2
```

> **Encryption gotcha:** if the source snapshot were **KMS-encrypted**, a cross-region copy must
> be **re-encrypted with a KMS key in the destination region** (pass `--kms-key-id` of a
> us-west-2 key). A key from us-east-1 won't work in us-west-2. Our lab DB is unencrypted to keep
> this simple; the [challenges](../challenges.md) cover the encrypted path.

---

## 5.2 Restore in the DR Region

Now treat us-west-2 as if us-east-1 is gone. You'll need a security group **in us-west-2** (its
own default VPC) that allows 3306 from your IP — create one just like Step 1.2, but in the DR
region.

1. **Switch the console region to us-west-2.**
2. **RDS** → **Snapshots** → `rds-dr-demo-snap-1-usw2` → **Restore snapshot**.
3. New identifier `rds-dr-demo-dr`, `db.t3.micro`, the us-west-2 SG, **Public access: Yes**.
4. **Restore**, wait for **Available**.

```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier rds-dr-demo-dr \
  --db-snapshot-identifier rds-dr-demo-snap-1-usw2 \
  --db-instance-class db.t3.micro \
  --publicly-accessible \
  --vpc-security-group-ids <USW2_SG_ID> \
  --region us-west-2
```

---

## 5.3 Verify in us-west-2

```bash
aws rds describe-db-instances --db-instance-identifier rds-dr-demo-dr \
  --query 'DBInstances[0].Endpoint.Address' --output text --region us-west-2

python src/db_verify.py --host <DR_ENDPOINT> --user admin --password '<YOUR_PW>'
```

Your data now lives and serves in a **different region**. This is the backbone of a
**backup-and-restore DR strategy**: keep snapshots copied to a DR region, and on a regional
disaster, restore and redirect. RPO = age of the last copied snapshot; RTO = copy-already-done +
restore time.

> **Automate the copy in production.** You wouldn't copy snapshots by hand. **AWS Backup** can run
> a backup plan that takes RDS snapshots on a schedule *and* copies them cross-region
> automatically — see [Challenge 4](../challenges.md).

---

## Checkpoint

- [ ] `rds-dr-demo-snap-1-usw2` exists in **us-west-2**
- [ ] A us-west-2 security group allows 3306 from your IP
- [ ] `rds-dr-demo-dr` restored in us-west-2 and is **Available**
- [ ] `db_verify.py` confirms the data in the DR region
- [ ] You understand the KMS re-encryption rule for cross-region encrypted copies

---

**Next:** [Step 6 — Cross-Region Read Replica & Failover](./06-cross-region-replica-failover.md)
