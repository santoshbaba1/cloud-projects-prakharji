# Step 1 — Provision the RDS Database

You'll create one small MySQL instance, `rds-dr-demo`, that your laptop can reach so the Python
scripts can seed and verify data. Keep it small and short-lived — this is the thing that bills by
the hour.

> **Security note for a lab:** we make the database **publicly accessible** and open port 3306 to
> **your IP only** so you can connect from your laptop without a bastion. That's fine for a
> throwaway lab. *Never* expose a real production database to the internet — put it in a private
> subnet behind your app. We call this out again in [troubleshooting](../troubleshooting.md).

---

## 1.1 Create the Database

1. **RDS** → **Databases** → **Create database** → **Standard create**.

   | Field | Value | Why |
   |-------|-------|-----|
   | Engine | **MySQL** | The scripts use PyMySQL |
   | Templates | **Free tier** | Forces a single-AZ db.t3.micro |
   | DB instance identifier | `rds-dr-demo` | |
   | Master username | `admin` | |
   | Master password | *(set one, save it)* | You'll pass it to the scripts |
   | Instance class | `db.t3.micro` | Free-tier-eligible |
   | Storage | 20 GB gp3, **disable** autoscaling | Keep cost predictable |
   | Public access | **Yes** | So your laptop can connect (lab only) |
   | VPC security group | **Create new** → `rds-dr-sg` | We'll lock it to your IP |

2. **Additional configuration** (expand):

   | Field | Value | Why |
   |-------|-------|-----|
   | Initial database name | `appdb` | The scripts use `appdb` |
   | **Backup retention period** | **7 days** | Enables PITR over a week (Step 3) |
   | Backup window | default | When the daily snapshot runs |

3. **Create database.** It takes ~5–10 minutes to become **Available**.

---

## 1.2 Lock the Security Group to Your IP

1. Find your public IP: `curl -s https://checkip.amazonaws.com`.
2. **EC2** → **Security Groups** → `rds-dr-sg` → **Inbound rules** → **Edit**:

   | Type | Port | Source |
   |------|------|--------|
   | MySQL/Aurora | 3306 | `<your-ip>/32` |

3. **Save rules.**

> Why `/32`? It's exactly one address — yours. A `0.0.0.0/0` rule would let the whole internet
> attempt to log in. Least privilege applies to network reachability too, not just IAM.

---

## 1.3 Grab the Endpoint

When the instance is **Available**, open it and copy the **Endpoint** (looks like
`rds-dr-demo.xxxx.us-east-1.rds.amazonaws.com`). You'll use it as `--host` everywhere.

```bash
aws rds describe-db-instances --db-instance-identifier rds-dr-demo \
  --query 'DBInstances[0].Endpoint.Address' --output text --region us-east-1
```

---

## AWS CLI (Alternative)

```bash
aws rds create-db-instance \
  --db-instance-identifier rds-dr-demo \
  --engine mysql --db-instance-class db.t3.micro \
  --master-username admin --master-user-password '<YOUR_PW>' \
  --allocated-storage 20 --storage-type gp3 \
  --db-name appdb \
  --backup-retention-period 7 \
  --publicly-accessible \
  --vpc-security-group-ids <SG_ID> \
  --region us-east-1
```

---

## Checkpoint

- [ ] `rds-dr-demo` is **Available**, `db.t3.micro`, single-AZ
- [ ] **Backup retention = 7 days** (this powers PITR)
- [ ] `rds-dr-sg` allows 3306 from **your IP /32** only
- [ ] You copied the **endpoint** and saved the master password

---

**Next:** [Step 2 — Seed Data and Record a Baseline](./02-seed-and-baseline.md)
