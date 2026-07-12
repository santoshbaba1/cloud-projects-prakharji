# Costs — GCP Cloud Run & Artifact Registry

**Good news:** this project stays inside Google Cloud's **free tiers** for a normal session. You need
billing enabled (Cloud Run requires it), but you should see **$0.00**. This page shows *where* charges
would appear so you understand the pricing model — and so you clean up before anything grows. Prices
are list price in `us-east1`.

---

## Service-by-Service

| Resource | Unit price | Free tier | Your usage | Cost |
|----------|-----------|-----------|------------|------|
| **Cloud Run — requests** | $0.40 / million | **2 million / month** | a few dozen | **$0** |
| **Cloud Run — vCPU** | $0.000024 / vCPU-sec | **180,000 vCPU-sec / month** | seconds | **$0** |
| **Cloud Run — memory** | $0.0000025 / GiB-sec | **360,000 GiB-sec / month** | seconds | **$0** |
| **Cloud Build** | $0.003 / build-minute | **120 build-minutes / day** | 2–3 short builds | **$0** |
| **Artifact Registry — storage** | $0.10 / GB-month | **0.5 GB** | 1 image (~150 MB) | **$0** |
| **Network egress** | ~$0.12 / GB | 1 GB / month (N. America) | a few KB | **$0** |

**Realistic session cost: $0.00.**

---

## The Key Idea: Scale to Zero

Cloud Run's headline feature is that with **no traffic it runs zero instances** — you pay **nothing**
for an idle service. You're billed only for the CPU/memory used **while actually handling a request**
(plus a rounding to the nearest 100 ms). This is fundamentally different from an always-on VM or the
[GCP HTTP LB project](../../../intermediate/gcp/gcp-http-lb-autoscaling/README.md), where the load
balancer and VMs bill per hour whether or not anyone visits.

---

## Where Money *Would* Appear

1. **Min instances > 0.** If you set `--min-instances=1` to avoid cold starts, that one instance runs
   24/7 and bills for idle CPU/memory — this is the most common surprise. This lab leaves min at 0.
2. **A large or growing image catalog.** One image is free; dozens of old tags can exceed 0.5 GB and
   bill $0.10/GB-month. Delete unused tags (cleanup Step 6.2).
3. **Heavy build usage.** Past 120 build-minutes/day, builds cost $0.003/minute. Not a concern here.
4. **High request volume.** Past 2M requests/month you pay per request + compute — only relevant for
   a real production app.

---

## Rule of Thumb

> Cloud Run is genuinely **pay-per-use**: idle = $0. The only things that persist after your session
> are the **stored image** and the **service definition** — both free at this scale, but delete them
> in [Step 6](steps/06-cleanup.md) to keep the project tidy and avoid slow storage creep.
