# Step 7 — Cleanup

**This is the most important step in the project.** RDS instances bill **per hour while they
exist**, even idle, and you've created several across two regions. Snapshots bill for storage.
Delete everything in **both** regions.

> Tip: list everything first so you don't miss a region.
> ```bash
> for R in us-east-1 us-west-2; do echo "== $R =="; \
>   aws rds describe-db-instances --region $R --query 'DBInstances[].DBInstanceIdentifier'; \
>   aws rds describe-db-snapshots --region $R --snapshot-type manual --query 'DBSnapshots[].DBSnapshotIdentifier'; done
> ```

---

## 7.1 Delete Instances — us-east-1

`rds-dr-demo`, plus any of `rds-dr-demo-pitr`, `rds-dr-demo-fromsnap` you kept. Use
`--skip-final-snapshot` (lab data, no need to keep) and `--delete-automated-backups`:

```bash
for DB in rds-dr-demo rds-dr-demo-pitr rds-dr-demo-fromsnap; do
  aws rds delete-db-instance --db-instance-identifier $DB \
    --skip-final-snapshot --delete-automated-backups --region us-east-1 2>/dev/null
done
```

(Console: select each → **Actions → Delete** → uncheck "create final snapshot" → type `delete me`.)

> **Delete the replica before its source if it's still replicating.** A promoted replica is
> independent and deletes like any instance. An *un-promoted* replica should be deleted (or
> promoted) before you delete its primary.

---

## 7.2 Delete Instances — us-west-2

`rds-dr-demo-dr` and `rds-dr-replica` (whether promoted or not):

```bash
for DB in rds-dr-demo-dr rds-dr-replica; do
  aws rds delete-db-instance --db-instance-identifier $DB \
    --skip-final-snapshot --delete-automated-backups --region us-west-2 2>/dev/null
done
```

---

## 7.3 Delete Manual Snapshots — Both Regions

```bash
aws rds delete-db-snapshot --db-snapshot-identifier rds-dr-demo-snap-1 --region us-east-1
aws rds delete-db-snapshot --db-snapshot-identifier rds-dr-demo-snap-1-usw2 --region us-west-2
```

Automated backups are removed with their instance (the `--delete-automated-backups` flag);
retained automated backups, if any, appear under **Snapshots → System** and can be deleted there.

---

## 7.4 Delete the Security Groups

Once no instance uses them:

```bash
aws ec2 delete-security-group --group-name rds-dr-sg --region us-east-1
# and the us-west-2 SG you created in Step 5.2
```

---

## 7.5 Final Verification

```bash
for R in us-east-1 us-west-2; do echo "== $R =="; \
  aws rds describe-db-instances --region $R --query 'DBInstances[].DBInstanceIdentifier'; \
  aws rds describe-db-snapshots --region $R --snapshot-type manual --query 'DBSnapshots[].DBSnapshotIdentifier'; done
```

Both regions should return **empty lists** for instances and your manual snapshots.

---

## Checkpoint

- [ ] No RDS instances remain in **us-east-1** or **us-west-2**
- [ ] Manual snapshots deleted in both regions
- [ ] Security groups deleted
- [ ] The final `describe` calls return empty — **no hourly charges left**

You've finished the **recovery** project and run every standard RDS DR drill. Next, Project 3
applies optimization *and* recovery to Kubernetes →
[Kubernetes Optimization & Recovery](../k8s-optimization-and-recovery/README.md).
