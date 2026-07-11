# Troubleshooting — Cloud SQL Managed Database

Error → Cause → Fix for the problems you're most likely to hit.

---

## Error: `Can't connect to MySQL server on '<ip>' (110)` / connection refused or timed out

**Cause:** Almost always one of two things: the instance's authorized networks don't include your
current public IP, or you're trying to reach a **private IP** instance from outside its VPC. Your
IP also changes across networks (home, office, coffee shop, VPN), so a rule that worked yesterday
can silently stop working today.

**Fix:**
```bash
MY_IP=$(curl -s ifconfig.me)
gcloud sql instances patch meridian-orders-db --authorized-networks="${MY_IP}/32"
```
If you're using the Cloud SQL Auth Proxy instead, confirm it's still running in its terminal and
that you're connecting to `127.0.0.1:3306`, not the instance's public IP directly.

---

## Error: `dial tcp ... connectex: No connection could be made` (Cloud SQL Auth Proxy)

**Cause:** The Auth Proxy itself failed to authenticate — usually stale or missing Application
Default Credentials, or the account running it lacks `roles/cloudsql.client`.

**Fix:**
```bash
gcloud auth application-default login
gcloud projects add-iam-policy-binding "$(gcloud config get-value project)" \
  --member="user:$(gcloud config get-value account)" \
  --role="roles/cloudsql.client"
```
Restart the proxy after fixing credentials — it authenticates once at startup.

---

## Error: `ERROR 1045 (28000): User does not exist` (IAM database authentication)

**Cause:** Enabling the `cloudsql_iam_authentication` flag does **not** automatically register any
IAM principal as a database user. You must explicitly add yourself with
`--type=cloud_iam_user` before Cloud SQL will recognize your token as a valid login.

**Fix:**
```bash
gcloud sql users create "$(gcloud config get-value account)" \
  --instance=meridian-orders-db \
  --type=cloud_iam_user
```
Then re-run `gcloud sql generate-login-token` and connect again (see
[Step 3](steps/03-iam-database-authentication.md)).

---

## Error: `ERROR: (gcloud.sql.backups.create) HttpError 400: The instance or operation is not in a state that allows the operation to be initiated` / insufficient storage or quota

**Cause:** A backup was already in progress, storage is at capacity because
`--no-storage-auto-increase` is set (Step 1), or the instance was mid-restart from a flag change.

**Fix:** Wait for any in-flight operation to finish (`gcloud sql operations list --instance=meridian-orders-db`),
and check free storage:
```bash
gcloud sql instances describe meridian-orders-db --format='value(settings.dataDiskSizeGb)'
```
If storage is genuinely full, increase it manually — `gcloud sql instances patch meridian-orders-db --storage-size=20`
— rather than turning auto-increase back on for a lab instance.

---

## "My restore didn't actually restore anything — it made a whole new instance"

**Cause:** This isn't a bug — it's how Cloud SQL PITR (and every restore path) works. There is no
"restore in place." `gcloud sql instances clone --point-in-time` or the console's "Restore to
point in time" always produce a **new instance** with its own name, IP, and connection name. Your
original instance is left completely untouched, for better or worse.

**Fix:** Point your app/scripts at the **new** instance's IP after verifying it
(`db_verify.py --host <new-ip>`), then decide whether to keep the old one, delete it, or promote a
DNS/connection-name layer in front of both so the switch is transparent (see
[Challenge 3](challenges.md)).

---

## Replica shows growing lag, or "promote" doesn't seem reversible

**Cause:** Replica lag is normal under write bursts and usually catches up on its own — check the
`cloudsql.googleapis.com/database/replication/replica_lag` metric before assuming something's
broken. Promotion, on the other hand, is **intentionally one-way**: once you run
`gcloud sql instances promote-replica`, the instance detaches from its primary permanently and
starts accepting writes independently.

**Fix:** For lag, just wait and watch the metric — it's not an error unless it climbs indefinitely.
For promotion, treat it as a failover decision, not a reversible test: only promote when you
actually intend the replica to become the new primary.

---

## Locked out after resetting the root password

**Cause:** Resetting the root password (via `gcloud sql users set-password`) takes effect
immediately — any script, proxy session, or `gcloud sql connect` shell using the old password
starts failing right away, including ones you forgot were still open.

**Fix:**
```bash
gcloud sql users set-password root --host=% --instance=meridian-orders-db --password='<NEW_PASSWORD>'
```
Update every place the old password was exported (`DB_PASSWORD` env var, `.env` files, open
terminals) before you assume something else is broken. Prefer connecting as `orders_app` or via
IAM database authentication for day-to-day work — save root for genuine admin tasks so a reset
doesn't ripple through the app.

---

## General debugging checklist

1. Authorized networks include your **current** IP, or the Auth Proxy is running and healthy
2. IAM principals must be explicitly added with `gcloud sql users create --type=cloud_iam_user`
   before IAM DB auth will recognize them
3. Restores and clones **always** produce a new instance — update your connection target
4. Replica lag is a metric to watch, not automatically an error; promotion is one-way
5. A password reset invalidates every existing session using the old password
6. `gcloud sql operations list --instance=<name>` shows what the instance is doing right now
