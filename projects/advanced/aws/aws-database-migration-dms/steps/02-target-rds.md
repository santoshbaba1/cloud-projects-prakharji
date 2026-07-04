# Step 2 — Target: Amazon RDS for MySQL

Now the destination: a managed **RDS for MySQL** instance. It starts **empty** — DMS will create
the tables (full load can auto-create them) and fill them. Keeping the engine the same (MySQL →
MySQL) is what makes this a **homogeneous** migration with no schema conversion.

---

## 2.1 What You're Creating

| Thing | Value |
|-------|-------|
| DB identifier | `dms-target-rds` |
| Engine | MySQL 8.0 |
| Class | `db.t3.micro` (free-tier eligible 12 mo) |
| Storage | 20 GB gp3, single-AZ (lab) |
| Master user | `admin` / a strong password |
| Public access | No (DMS reaches it inside the VPC) |
| Inbound | 3306 from the **DMS replication instance** security group (Step 3) |

---

## 2.2 Console — Create the Database

1. **RDS → Create database → Standard create → MySQL.**
2. **Templates:** Free tier (or Dev/Test). **DB instance identifier:** `dms-target-rds`.
3. **Credentials:** master username `admin`, set a strong password.
4. **Instance:** `db.t3.micro`. **Storage:** 20 GB gp3.
5. **Connectivity:** same VPC as the source EC2; **Public access: No**. Create or pick a
   security group `dms-target-sg` (you'll open 3306 to DMS in Step 3).
6. **Additional configuration:** **uncheck** automated backups isn't required for the lab, but
   leaving the default 1-day retention is fine. **Create database.**

> **Why no public access?** The database should only be reachable from inside the VPC — the DMS
> replication instance lives there too. Least exposure = smaller attack surface.

### CLI alternative

```bash
aws rds create-db-instance \
  --db-instance-identifier dms-target-rds \
  --engine mysql --engine-version 8.0 \
  --db-instance-class db.t3.micro \
  --allocated-storage 20 --storage-type gp3 \
  --master-username admin --master-user-password 'ChangeMe_Strong#1' \
  --no-publicly-accessible --backup-retention-period 1
aws rds wait db-instance-available --db-instance-identifier dms-target-rds
```

---

## 2.3 Record the Endpoint

When it's **Available**, copy the **endpoint** (`dms-target-rds.xxxx.us-east-1.rds.amazonaws.com`):

```bash
aws rds describe-db-instances --db-instance-identifier dms-target-rds \
  --query 'DBInstances[0].Endpoint.Address' --output text
```

> Leave the target **empty** — don't seed it. Proving DMS populated it from zero is the whole
> demonstration. (DMS's full load can auto-create the schema; for stricter control you'd
> pre-create tables, which Challenge 2 explores.)

---

## Checkpoint

- [ ] `dms-target-rds` is **Available**
- [ ] It's MySQL 8.0, `db.t3.micro`, **not** publicly accessible
- [ ] You recorded the RDS **endpoint address**
- [ ] The target is **empty** (no `shopdb` yet) — DMS will create it

---

**Next:** [Step 3 — DMS Replication Instance](./03-replication-instance.md)
