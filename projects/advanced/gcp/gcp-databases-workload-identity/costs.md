# Costs — GCP Databases & Workload Identity

**Read this before you start.** Most of this project is free or near-free — Firestore, Secret
Manager, IAM, and Workload Identity Federation cost effectively nothing at lab scale. **Memorystore is
the exception: it has no free tier and bills every hour it exists.** Prices are list price in
`us-east1`.

---

## Service-by-Service

| Resource | Unit price | Free tier | Your usage | Cost |
|----------|-----------|-----------|------------|------|
| **Firestore** | $0.06/100K reads, $0.18/100K writes, $0.18/GB storage-month | 50K reads, 20K writes, 20K deletes, 1 GiB storage **per day** | A handful of documents, a few reads/writes | **~$0** |
| **Memorystore for Redis — Basic, 1 GB** | ~$0.049/hr | **none** | ~1–1.5 hr provisioned | **~$0.05–0.08** |
| **`e2-micro` test VM** | ~$0.0063/hr (or free-tier eligible) | 1 `e2-micro`/month in eligible regions | ~30 min | **~$0 – $0.01** |
| **Secret Manager** | $0.06/active secret version/month, $0.03/10K access ops | first 6 active versions/month free | 1 secret, 1 version, a few accesses | **~$0** |
| **Workload Identity Federation** | — | — | 1 pool, 1 provider | **$0** |
| **IAM (roles, SA, impersonation, org policy)** | — | — | all of it | **$0** |
| **Boot disk (test VM)** | $0.04/GB-month | 30 GB-month free | 1 × 10 GB × ~30 min | **~$0** |

**Realistic 2-hour session: ~$0.05 – $0.15.**

---

## The Two Things That Could Cost You

1. **Memorystore left running.** This is the whole ballgame. At ~$0.049/hr, a forgotten instance is
   ~$1.18/day, ~$35/month — for a resource that was only ever meant to exist for one lab session.
   Unlike a VM, there's no "it auto-stops eventually." **[Step 7.2](steps/07-cleanup.md#72-delete-memorystore)
   is the single most important line in cleanup.**
2. **Challenges 4 and 5 (Bigtable / Spanner), if left up.** Neither is part of the main steps, but if
   you do the optional challenges, both bill continuously and neither has a free tier — Spanner's
   minimum instance size in particular is not cheap. Verify deletion immediately, as the challenge
   descriptions call out.

---

## Free Tier Notes

- **Firestore's free tier is genuinely generous** — 50K reads / 20K writes / 20K deletes **per day**,
  plus 1 GiB of storage, resets daily. A lab like this one, or even fairly serious development
  traffic, rarely exceeds it.
- **Secret Manager is nearly free at this scale** — the first 6 active secret versions per month cost
  nothing, and access operations are billed in $0.03-per-10,000 increments.
- **Workload Identity Federation has no usage-based charge at all.** Pools, providers, and the token
  exchanges themselves are free — the only cost anywhere near WIF is the compute/resources the
  authenticated identity goes on to touch.
- **IAM — roles, bindings, impersonation, org policy — is always free**, same as every other project
  in this repo.

---

## Rule of Thumb

> Everything in this project is close enough to free that you could forget about it for a week and
> barely notice — **except Memorystore, which bills per hour from the moment it's `READY` until the
> moment you delete it.** If you only remember to clean up one resource before closing your laptop,
> make it `meridian-cache`.
