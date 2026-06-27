# Step 3 — DMS Replication Instance

The **replication instance** is the compute that actually runs the migration — it connects to
both databases, performs the full load, and streams CDC. Before you create it you need a **DMS
subnet group** (which subnets it can live in) and the **security-group plumbing** so it can
reach the source EC2 and the target RDS on port 3306.

---

## 3.1 What You're Creating

| Thing | Value |
|-------|-------|
| Subnet group | `dms-subnet-group` (≥2 subnets, multi-AZ) |
| Replication instance | `dms-repl-instance`, class `dms.t3.micro` |
| Engine version | latest default |
| Public access | No (it talks to both DBs inside the VPC) |
| Security group | `dms-sg` (egress to 3306 of source + target) |

---

## 3.2 Create the Subnet Group

**DMS → Subnet groups → Create subnet group** → name `dms-subnet-group`, pick your VPC, add at
least **two subnets in different AZs** (DMS requires multi-AZ subnet coverage even for a
single-AZ instance).

```bash
aws dms create-replication-subnet-group \
  --replication-subnet-group-identifier dms-subnet-group \
  --replication-subnet-group-description "DMS lab subnets" \
  --subnet-ids subnet-aaaa subnet-bbbb
```

---

## 3.3 Create the Replication Instance

**DMS → Replication instances → Create replication instance:**

| Field | Value |
|-------|-------|
| Name | `dms-repl-instance` |
| Class | `dms.t3.micro` |
| VPC | same as source/target |
| Subnet group | `dms-subnet-group` |
| Multi-AZ | No (lab) |
| Publicly accessible | **No** |

```bash
aws dms create-replication-instance \
  --replication-instance-identifier dms-repl-instance \
  --replication-instance-class dms.t3.micro \
  --replication-subnet-group-identifier dms-subnet-group \
  --no-publicly-accessible
aws dms wait replication-instance-available \
  --replication-instance-arn <arn-from-previous-output>
```

It takes ~10 minutes. ⚠️ **The meter is now running** — `dms.t3.micro` has **no free tier**.

---

## 3.4 Open the Network Path (the part people forget)

The replication instance must reach **3306** on both databases. Find its security group (or the
ENIs' SG), then:

- **Source EC2 SG (`dms-source-mysql`)** → add inbound `MySQL 3306` from `dms-sg` (or the repl
  instance's private IP/CIDR).
- **Target RDS SG (`dms-target-sg`)** → add inbound `MySQL 3306` from `dms-sg`.

```bash
# example: allow the DMS SG into the RDS SG on 3306
aws ec2 authorize-security-group-ingress \
  --group-id <rds-sg-id> --protocol tcp --port 3306 --source-group <dms-sg-id>
aws ec2 authorize-security-group-ingress \
  --group-id <source-ec2-sg-id> --protocol tcp --port 3306 --source-group <dms-sg-id>
```

> **Why this matters:** the #1 reason a DMS "Test connection" fails (Step 4) is a closed
> security-group path, not bad credentials. Getting the network right now saves you that
> debugging later.

---

## Checkpoint

- [ ] `dms-subnet-group` exists with ≥2 subnets in different AZs
- [ ] `dms-repl-instance` (`dms.t3.micro`) is **Available**, not public
- [ ] Source EC2 SG allows 3306 from the DMS security group
- [ ] Target RDS SG allows 3306 from the DMS security group

---

**Next:** [Step 4 — Endpoints + Test Connections](./04-endpoints.md)
