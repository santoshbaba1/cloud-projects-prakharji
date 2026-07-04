# Step 5 — Full Load + CDC Migration Task

The task is where the migration actually happens. You'll create a **Migrate existing data and
replicate ongoing changes** task (full load + CDC). It first **bulk-copies** `shopdb`'s rows to
RDS (full load), then **switches to CDC** and keeps the target in sync by replaying the source's
binlog — so the source database never has to go offline during the copy.

---

## 5.1 What You're Creating

| Field | Value |
|-------|-------|
| Task identifier | `dms-migration-task` |
| Replication instance | `dms-repl-instance` |
| Source / target endpoint | `dms-source-endpoint` / `dms-target-endpoint` |
| Migration type | **Migrate existing data and replicate ongoing changes** (full load + CDC) |
| Target table prep | **Do nothing** (target is empty) or **Drop tables on target** |
| Table mappings | Include schema `shopdb`, all tables (`%`) |

> **Why full load + CDC and not just full load?** Full load alone copies a *snapshot*; any write
> that lands on the source during/after the copy is lost. CDC replays those writes continuously,
> so source and target converge and you can cut over with **near-zero data loss (low RPO)**.

---

## 5.2 Table Mappings (what to migrate)

DMS needs a selection rule. The simplest: include everything in `shopdb`.

```json
{
  "rules": [{
    "rule-type": "selection",
    "rule-id": "1",
    "rule-name": "include-shopdb",
    "object-locator": { "schema-name": "shopdb", "table-name": "%" },
    "rule-action": "include"
  }]
}
```

> **Why explicit mappings?** They make the migration's scope auditable — you migrate exactly
> what you intend, nothing more. In a real migration you'd often transform or filter here too.

---

## 5.3 Create + Start the Task

**DMS → Database migration tasks → Create task:**

1. **Identifier:** `dms-migration-task`; pick the replication instance and both endpoints.
2. **Migration type:** *Migrate existing data and replicate ongoing changes.*
3. **Target table preparation mode:** *Do nothing* (empty target).
4. **Enable validation:** check it (you'll use it in Step 6).
5. **Table mappings:** paste the JSON above (or use the guided UI: schema `shopdb`, table `%`).
6. **Start task:** *Automatically on create.* **Create task.**

### CLI alternative

```bash
aws dms create-replication-task \
  --replication-task-identifier dms-migration-task \
  --source-endpoint-arn <source-endpoint-arn> \
  --target-endpoint-arn <target-endpoint-arn> \
  --replication-instance-arn <repl-instance-arn> \
  --migration-type full-load-and-cdc \
  --table-mappings file://table-mappings.json \
  --replication-task-settings '{"ValidationSettings":{"EnableValidation":true}}'
```

---

## 5.4 Watch It Migrate

In the task's **Table statistics** tab you'll see the lifecycle:

| Phase | What you see |
|-------|--------------|
| **Full load** | `customers` and `orders` go to *Table completed*, with row counts |
| **CDC starting** | Task status → *Load complete, replication ongoing* |
| **CDC running** | New source writes appear as Inserts/Updates/Deletes |

Confirm the full load landed by verifying the target now matches the source:

```bash
python3 src/db_verify.py --host <rds-endpoint> --user admin --password 'ChangeMe_Strong#1'
# compare counts + checksums against the SOURCE output from Step 1
```

> The task should now sit in **replication ongoing** — leave it there. Step 6 proves CDC works
> live, then cuts over.

---

## Checkpoint

- [ ] `dms-migration-task` created as **full load + CDC**, validation enabled
- [ ] Table statistics show `customers` and `orders` **fully loaded** with correct row counts
- [ ] Task status is **Load complete, replication ongoing**
- [ ] `db_verify.py` against RDS matches the Step 1 source counts/checksums

---

**Next:** [Step 6 — Validate & Cut Over](./06-validate-and-cutover.md)
