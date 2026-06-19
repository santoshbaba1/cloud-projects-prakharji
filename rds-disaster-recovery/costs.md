# Costs — RDS Disaster Recovery

Unlike most projects in this repo, **this one really can cost a few dollars** if you're slow or
forget to clean up. RDS instances bill **per hour while they exist**, even when idle, and the DR
drills have you running several at once. Prices are list price; storage/transfer in `us-east-1` /
`us-west-2`.

---

## Service-by-Service

| Service | Unit price (after free tier) | Free tier | Your likely usage | Cost |
|---------|------------------------------|-----------|-------------------|------|
| **RDS db.t3.micro (MySQL, single-AZ)** | ~$0.017 / hr | 750 hrs/month for 12 months (one instance) | 1 primary for ~2 hrs + extras | **~$0** (1st instance) + ~$0.017/hr each extra |
| **RDS storage (gp3)** | $0.115 / GB-month | 20 GB/month for 12 months | 20 GB × few hrs | **~$0** |
| **Manual snapshots** | $0.095 / GB-month (backup storage beyond DB size) | backup up to DB size free | a few GB × hours | **~$0** |
| **Cross-region snapshot copy — transfer** | $0.02 / GB out of region | — | a few GB once | **~$0.01–0.10** |
| **Cross-region read replica — replication transfer** | $0.02 / GB out of region | — | tiny dataset | **~$0** |
| **Read replica instance** | ~$0.017 / hr (us-west-2) | not free-tier (2nd instance) | 1 for ~1 hr | **~$0.02** |

> The **Free Tier covers exactly one** db.t3.micro for 750 hrs/month. Every *additional* instance
> you run simultaneously — the PITR copy, the snapshot restore, the DR restore, the replica — is
> **billed**, even if each is only pennies per hour.

---

## Where the Money Actually Goes

- **Concurrent instances.** The drills naturally leave 2–4 instances running at once. Four
  db.t3.micro for an hour ≈ **$0.07** — small, but it compounds if you walk away.
- **Forgetting an instance in us-west-2.** The #1 surprise bill in this project: you clean up
  us-east-1, forget the DR region, and a replica quietly bills for days. **Always check both
  regions** ([Step 7.5](steps/07-cleanup.md)).
- **Snapshots left behind.** Manual snapshots persist until *you* delete them and bill for backup
  storage. Pennies, but they linger forever if ignored.
- **Multi-AZ by accident.** If you pick a non-"Free tier" template, RDS may default to **Multi-AZ**
  (two instances = double cost). Stick with the **Free tier** template (single-AZ) for the lab.

---

## How to Keep It Near $0

1. Use the **Free tier** template (single-AZ db.t3.micro) for the primary.
2. **Delete each restored/PITR/replica instance as soon as you've verified it**, instead of
   leaving them all running to the end.
3. Do the whole project in **one ~2-hour sitting**.
4. Run the [Step 7.5](steps/07-cleanup.md) two-region sweep and confirm empty lists.

---

## Left Running?

A single forgotten db.t3.micro is ~**$12/month**; an idle replica in us-west-2 the same again,
plus snapshot storage. There is **no $0 idle state** for an RDS instance — the only safe state is
**deleted**. Run [Step 7](steps/07-cleanup.md).

**Bottom line: careful single session + full cleanup → ~$1–$3 (often under $1).**
