# Costs — Cloud SQL Managed Database

**Read this before you start.** Cloud SQL is one of the few services in this repo with genuinely
**no permanent free tier** — every instance you create bills per hour from creation to deletion,
whether or not you ever connect to it. This project deliberately runs **three instances at once**
partway through (primary, PITR restore, read replica), so a careless multi-day session can add up
faster than the beginner GCP labs. Prices are list price in `us-east1`.

---

## Service-by-Service

| Resource | Unit price | Free tier | Your usage | Cost |
|----------|-----------|-----------|------------|------|
| **Cloud SQL — primary (`db-f1-micro`, shared-core)** | ~$0.0150–0.0300 / hr | none | 1 instance × ~2 hr | **~$0.03–0.06** |
| **Cloud SQL — PITR-restored instance** | ~$0.0150–0.0300 / hr | none | 1 instance × ~0.5–1 hr | **~$0.01–0.03** |
| **Cloud SQL — read replica** | ~$0.0150–0.0300 / hr | none | 1 instance × ~0.5–1 hr | **~$0.01–0.03** |
| **SSD storage (10 GB × 3 instances)** | $0.17 / GB-month | none | ~30 GB × a few hours | **~$0.01–0.02** |
| **Backup storage** | $0.08 / GB-month | first backup up to instance size may be included, depending on plan | a few GB × a few hours | **~$0–0.01** |
| **Network egress (Auth Proxy / replica traffic)** | $0.01–0.12 / GB depending on destination | small monthly allowance | a few MB | **~$0** |

**Typical session cost: $0.10 – $0.20** for 2–3 hours if you clean up the same day.

---

## The Two Things That Could Cost You

1. **Running all three instances longer than needed.** The project has you spin up the PITR
   restore and the read replica for *verification*, not for keeping around. The moment you've
   confirmed `db_verify.py` shows `PASS` against one, delete it rather than waiting until
   [Step 6](steps/06-cleanup.md) — three simultaneous shared-core instances for an afternoon is
   pennies; three simultaneous instances for a forgotten week is real money.
2. **Leaving the primary running after the lab ends.** There is no idle discount and no
   auto-shutdown. An instance created on a Friday and noticed the following Friday has billed for
   a full week regardless of whether a single query ran against it. Cloud SQL instances are the
   *opposite* of a free-tier VM — assume every minute they exist costs something.

---

## Free Tier Notes

- **There is no Always-Free tier for Cloud SQL** — unlike Compute Engine's free `e2-micro`, every
  Cloud SQL instance (even the smallest shared-core tier) bills from the moment it's `RUNNABLE`.
- **What actually is free (or close to it):** the VPC networking, firewall/authorized-network
  config, and IAM database authentication itself cost nothing — you're only ever billed for
  compute (the instance), storage, and backup storage beyond any small included allowance.
- **New-customer credits** (if you're on a trial or promotional credit) will cover this project's
  cost many times over — but don't rely on that as a reason to skip cleanup; credits expire and
  the underlying meter doesn't care.

---

## Rule of Thumb

> A Cloud SQL instance bills **per hour, idle or not, with no free tier to fall back on** — and
> this project runs three of them for part of its runtime. There is no "basically free if I
> forget it" here. Finish the lab, run [Step 6 — Cleanup](steps/06-cleanup.md), and confirm
> `gcloud sql instances list` returns empty before you close the terminal.
