# Challenges — Cloud SQL Managed Database

Push past the guided steps. Each challenge assumes `meridian-orders-db` (or a fresh instance) is
still up. Clean up anything extra you create afterward.

---

## 1. Switch to PostgreSQL and Compare

Recreate the instance with `--database-version=POSTGRES_15` instead of MySQL. Redo the seed/verify
scripts using `psycopg2` (or `pg8000`) instead of `pymysql` — note what actually changes: the
connection library, yes, but also IAM database authentication's setup steps and the SQL dialect
for grants.

- **Question:** What, if anything, about the backup/PITR/replica model is different between the
  two engines on Cloud SQL?

---

## 2. Enable Cloud SQL Insights and Analyze a Slow Query

Write a query that's deliberately slow (e.g. a full-table scan on `orders` without an index, or a
`SLEEP()` call inside a stored procedure) and run it several times through `db_verify.py`-style
scripts. Find it in **Query Insights**, then add an index or rewrite the query and confirm the
improvement in the same dashboard.

- **Goal:** go from "the app feels slow" to "this exact query, this exact wait event" using only
  console tools — no code changes to the app itself required to diagnose it.

---

## 3. Try Private Service Connect Instead of Legacy Private IP

This project used public IP + authorized networks for lab simplicity. Rebuild connectivity using
**Private Service Connect (PSC)** — Google's newer, VPC-Service-Controls-compatible replacement
for the older private-IP-via-VPC-peering model — so the instance has no public IP and no peering
relationship to manage.

- **Question:** What operational problems did VPC peering for Cloud SQL have that PSC was built
  to avoid (hint: it involves how peering ranges interact across projects)?

---

## 4. Set Up a Maintenance Window

Configure a specific maintenance window (day + hour) and a maintenance **deny period** (e.g. block
updates during Meridian's Black Friday week). Trigger a manual maintenance update and observe how
Cloud SQL respects — or doesn't — your window under different update-track settings
(`canary` vs `stable`).

- **Goal:** understand the difference between *when* Google is allowed to touch your instance and
  *what* it's allowed to do without your explicit action.

---

## 5. Automatic IAM Auth with `cloud-sql-proxy`

Step 3 generated a login token manually with `gcloud sql generate-login-token`. The Cloud SQL Auth
Proxy (v2) can do this automatically with the `--auto-iam-authn` flag, refreshing the token behind
the scenes so a long-running app connection never has to manage tokens itself.

```bash
./cloud-sql-proxy "${INSTANCE_CONN}" --auto-iam-authn --port 3306
```

- **Question:** With `--auto-iam-authn` handling refresh, what's actually left for `orders_app`'s
  password to do that IAM auth can't cover?

---

## 6. Cost Out HA (Regional) vs. Single-Zone

Modify `meridian-orders-db` to **regional (HA)** availability (`--availability-type=REGIONAL`) and
compare the hourly cost shown in the console/pricing calculator against the single-zone instance
you've been running. Force a failover (`gcloud sql instances failover`) and time how long it takes
compared to a PITR restore or replica promotion.

- **Goal:** build the same RPO/RTO-vs-cost table this project's README implies, but with real
  numbers from your own account.

---

## 7. Export a Backup to a GCS Bucket

Export `meridian_orders` to a SQL dump in a Cloud Storage bucket — ideally the documents bucket
from [Project 1](../../../beginner/gcp/gcp-iam-storage-fundamentals/README.md) or its
lifecycle-managed twin from [Project 2](../gcp-storage-security-lifecycle/README.md), giving the
export a lifecycle rule that moves it to Nearline after 30 days.

```bash
gcloud sql export sql meridian-orders-db gs://<your-bucket>/meridian-orders-backup.sql \
  --database=meridian_orders
```

- **Question:** Unlike an automated backup (deleted with its instance), an exported dump in GCS
  survives the instance entirely. When would you reach for an export instead of relying on
  Cloud SQL's built-in backups?

**Next up:** these ideas (Secret Manager, Workload Identity, no manual passwords at all) are
exactly where [Project 4 — Databases & Workload Identity](../../../advanced/gcp/gcp-databases-workload-identity/README.md)
picks up.
