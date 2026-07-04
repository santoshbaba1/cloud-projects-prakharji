# Step 1 — Source: Self-Managed MySQL on EC2 (with binlog for CDC)

You need a database to migrate *from*. In this step you run MySQL yourself on an EC2 instance —
the stand-in for an on-prem or self-hosted database. The crucial detail is **binary logging in
ROW format**: DMS reads the binlog to capture ongoing changes (CDC), and without it you can only
do a one-time full load, not a live migration.

---

## 1.1 What You're Creating

| Thing | Value |
|-------|-------|
| Instance name | `dms-source-mysql` |
| AMI / type | Amazon Linux 2023, `t3.micro` |
| Engine | MySQL 8 (community) |
| DB / tables | `shopdb` → `customers`, `orders` |
| Inbound | 3306 from the **DMS replication instance** (Step 3) and your IP for seeding |

---

## 1.2 Launch the Instance

**EC2 → Launch instances** → name `dms-source-mysql`, Amazon Linux 2023, `t3.micro`. Security
group inbound: `MySQL/Aurora 3306` from **My IP** (you'll add the DMS source later). Note the
**private IP** (DMS will use it) and **public IP** (you'll seed over it).

---

## 1.3 Install MySQL + Enable binlog (ROW)

SSH/SSM in, then:

```bash
sudo dnf install -y mariadb105-server   # MySQL-compatible; or install MySQL community
sudo systemctl enable --now mariadb
```

Enable binary logging in **ROW** format (required for DMS CDC) and a server id:

```bash
sudo tee /etc/my.cnf.d/dms.cnf >/dev/null <<'CNF'
[mysqld]
server-id = 1
log_bin = mysql-bin
binlog_format = ROW
binlog_row_image = FULL
expire_logs_days = 1
CNF
sudo systemctl restart mariadb
```

> **Why ROW + FULL image?** CDC needs the *before and after* values of each changed row to
> replay it faithfully into the target. `STATEMENT` format replays SQL text, which DMS can't
> reliably translate; `binlog_row_image=FULL` ensures every column is captured.

---

## 1.4 Create a Migration User

DMS connects as a DB user that can read the data **and** the binlog:

```bash
sudo mysql <<'SQL'
CREATE USER 'admin'@'%' IDENTIFIED BY 'ChangeMe_Strong#1';
GRANT SELECT ON *.* TO 'admin'@'%';
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'admin'@'%';
FLUSH PRIVILEGES;
SQL
```

> **Why `REPLICATION SLAVE/CLIENT`?** Those privileges let DMS read the binlog stream for CDC —
> the same grants a MySQL read replica needs. `SELECT` covers the full load.

---

## 1.5 Seed Data

From your laptop (or the instance), seed `shopdb` and record the counts — your **RPO marker**:

```bash
pip install -r src/requirements.txt
python3 src/db_seed.py --host <source-public-ip> --user admin --password 'ChangeMe_Strong#1'
# SOURCE seeded: 4 customers, 12 orders
```

Confirm with the verifier (you'll re-run this against the target later):

```bash
python3 src/db_verify.py --host <source-public-ip> --user admin --password 'ChangeMe_Strong#1'
```

---

## Checkpoint

- [ ] `dms-source-mysql` is running; MySQL/MariaDB is up
- [ ] `binlog_format=ROW` is active: `sudo mysql -e "SHOW VARIABLES LIKE 'binlog_format';"` → `ROW`
- [ ] User `admin` has `SELECT` + `REPLICATION SLAVE/CLIENT`
- [ ] `shopdb` has 4 customers and 12 orders (your RPO marker)
- [ ] You noted the instance's **private IP** for the DMS endpoint

---

**Next:** [Step 2 — Create the RDS Target](./02-target-rds.md)
