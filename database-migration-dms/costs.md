# Costs — Database Migration with AWS DMS

Region **us-east-1**. ⚠️ **This project bills while running** — three resources are live at the
same time, and the DMS replication instance has **no free tier**. Finish in one sitting and run
Step 7.

---

## Service-by-service

### DMS replication instance — no free tier

| Item | Rate | Notes |
|------|------|-------|
| `dms.t3.micro` | ~$0.018/hr | **No free tier.** Storage (50 GB default) ~$0.115/GB-mo |

This is the resource to delete first after cutover. It bills every hour it exists.

### EC2 source (self-managed MySQL)

| Item | Rate | Notes |
|------|------|-------|
| `t3.micro` | ~$0.0104/hr | **Free tier:** 750 hrs/mo for 12 months |
| EBS gp3 root | ~$0.08/GB-mo | Small |

### RDS target (MySQL)

| Item | Rate | Notes |
|------|------|-------|
| `db.t3.micro` single-AZ | ~$0.017/hr | **Free tier:** 750 hrs/mo `db.t3.micro` for 12 months |
| Storage 20 GB gp3 | ~$0.115/GB-mo | **Free tier:** 20 GB |
| Backups | first = DB size free | 1-day retention here |

### CloudWatch / data transfer

In-VPC traffic between DMS and the DBs is free or negligible; task logs are tiny at this scale.

---

## Rough total

```
DMS repl instance : $0.018/hr  ×  ~3 hrs  ≈  $0.05   (no free tier)
EC2 source        : $0.0104/hr ×  ~3 hrs  ≈  $0.03   ($0 under free tier)
RDS target        : $0.017/hr  ×  ~3 hrs  ≈  $0.05   ($0 under free tier)
                                         --------
An afternoon lab                         ≈  ~$0.10–0.50
```

Inside the 12-month free tier, only the **replication instance** really costs you — a few cents
for the lab, but **~$13/month** if you forget to delete it.

## Left-running warning ⚠️

- **DMS replication instance** — no free tier; the #1 thing to delete (Step 7.3).
- **RDS target** — bills hourly past the free tier; `--skip-final-snapshot` avoids a lingering
  snapshot charge if you don't need it.
- **EC2 source** — terminate it; a stopped instance still pays for its EBS volume.
- **Orphaned snapshots / subnet group** — delete the subnet group after the instance; check RDS
  snapshots.
