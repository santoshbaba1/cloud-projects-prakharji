# Step 7 — Cleanup

Three billable resources ran at once here — the source EC2, the target RDS, and the DMS
replication instance — and the **replication instance has no free tier**. Tear everything down
in dependency order: task → endpoints → replication instance → databases.

---

## 7.1 Stop & Delete the Task

A task must be **stopped** before it can be deleted (you stopped it at cutover in Step 6).

```bash
aws dms delete-replication-task --replication-task-arn <task-arn>
```

Console: **DMS → Database migration tasks → `dms-migration-task` → Actions → Delete.**

## 7.2 Delete the Endpoints

```bash
aws dms delete-endpoint --endpoint-arn <source-endpoint-arn>
aws dms delete-endpoint --endpoint-arn <target-endpoint-arn>
```

## 7.3 Delete the Replication Instance (stops the no-free-tier meter)

```bash
aws dms delete-replication-instance --replication-instance-arn <repl-instance-arn>
```

Then delete the subnet group once the instance is gone:

```bash
aws dms delete-replication-subnet-group --replication-subnet-group-identifier dms-subnet-group
```

## 7.4 Delete the Databases

> Only after you've confirmed the migration is verified and you don't need the data.

```bash
# target RDS — skip the final snapshot for a throwaway lab
aws rds delete-db-instance --db-instance-identifier dms-target-rds \
  --skip-final-snapshot --delete-automated-backups

# source EC2 — terminate
aws ec2 terminate-instances --instance-ids <source-instance-id>
```

## 7.5 Networking + Logs

- Delete the security groups you created (`dms-sg`, `dms-target-sg`, the source SG) once nothing
  references them.
- Delete the DMS CloudWatch log group `dms-tasks-<...>` if you want a clean slate.

---

## 7.6 Verify nothing is left billing

- **DMS → Replication instances:** none.
- **RDS → Databases:** `dms-target-rds` gone (status *deleting* → gone).
- **EC2 → Instances:** `dms-source-mysql` terminated.

```bash
aws dms describe-replication-instances --query 'ReplicationInstances[].ReplicationInstanceIdentifier' --output text
aws rds describe-db-instances --query 'DBInstances[].DBInstanceIdentifier' --output text
```

---

## Checkpoint

- [ ] Task deleted; both endpoints deleted
- [ ] Replication instance **and** subnet group deleted (meter stopped)
- [ ] RDS target deleted; source EC2 terminated
- [ ] Extra security groups / log groups removed
- [ ] **Cost Explorer** shows no DMS/RDS/EC2 from this project tomorrow

You migrated a live MySQL database to managed RDS with full load + CDC — and left nothing
running. 🎉
