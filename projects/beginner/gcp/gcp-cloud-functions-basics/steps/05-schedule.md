# Step 5 — Put It on a Schedule

Not every invocation comes from a user. **Cloud Scheduler** is a fully-managed cron that can call any
HTTP target on a recurring schedule. You'll have it "ping" the function every few minutes — Meridian's
nightly health check, sped up so you can watch it fire.

---

## 5.1 The Auth Question

Your function is currently **public** (`--allow-unauthenticated`), so Scheduler could just call the
URL with no credentials. But the production-correct pattern — and what you'll set up here — is for
Scheduler to present an **OIDC identity token** so the function could be locked down later. That needs
a service account Scheduler can act as.

Create a dedicated service account and let it invoke the function:

```bash
export PROJECT_ID="$(gcloud config get-value project)"

gcloud iam service-accounts create scheduler-invoker \
  --display-name "Cloud Scheduler → order-status invoker"

export SCHED_SA="scheduler-invoker@${PROJECT_ID}.iam.gserviceaccount.com"

# Allow the SA to invoke the function's Cloud Run service.
gcloud run services add-iam-policy-binding order-status \
  --region us-east1 \
  --member "serviceAccount:${SCHED_SA}" \
  --role roles/run.invoker
```

| Piece | Why |
|-------|-----|
| `scheduler-invoker` SA | The identity Scheduler uses to call the function — no user credentials in a cron |
| `roles/run.invoker` on the service | 2nd-gen functions authorize callers at the **Cloud Run** layer |
| OIDC token (below) | Scheduler signs the request as this SA; the function can verify it |

---

## 5.2 Create the Scheduled Job

```bash
gcloud scheduler jobs create http order-status-ping \
  --location us-east1 \
  --schedule "*/5 * * * *" \
  --uri "$URL/" \
  --http-method GET \
  --oidc-service-account-email "$SCHED_SA" \
  --oidc-token-audience "$URL"
```

| Flag | Why |
|------|-----|
| `--schedule "*/5 * * * *"` | Standard cron — **every 5 minutes** (dial to `* * * * *` to watch it faster) |
| `--uri "$URL/"` | Hits the heartbeat path (no `order_id`) |
| `--oidc-service-account-email` | Scheduler mints an OIDC token as this SA |
| `--oidc-token-audience` | The audience the token is minted for — the function's URL |

### Console (Alternative)

1. **Cloud Scheduler → Create job**. Region **us-east1**, name `order-status-ping`.
2. Frequency `*/5 * * * *`, timezone your choice.
3. Target type **HTTP**, URL = your function URL, method **GET**.
4. **Auth header → Add OIDC token**, service account `scheduler-invoker`, audience = the URL.
5. **Create**.

---

## 5.3 Force a Run and Watch It

Don't wait five minutes — trigger it now:

```bash
gcloud scheduler jobs run order-status-ping --location us-east1

# A few seconds later, confirm the heartbeat landed:
gcloud functions logs read order-status --gen2 --region us-east1 --limit 5 \
  | grep -i heartbeat
```

Check the job's own status (last run result, next run time):

```bash
gcloud scheduler jobs describe order-status-ping --location us-east1 \
  --format='value(state, lastAttemptTime, status.code)'
```

A successful run shows the target returned 2xx. If it shows an auth error, see
[troubleshooting.md](../troubleshooting.md) — it's almost always the `run.invoker` binding or a
mismatched audience.

---

## Checkpoint

- [ ] The `scheduler-invoker` SA has `run.invoker` on the function
- [ ] `order-status-ping` job exists in **us-east1**
- [ ] A manual `jobs run` produces a **heartbeat** log entry within seconds
- [ ] `jobs describe` shows the last attempt succeeded

---

**Next:** [Step 6 — Cleanup](./06-cleanup.md)
