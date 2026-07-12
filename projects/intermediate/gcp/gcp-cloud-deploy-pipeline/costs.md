# Costs — GCP Cloud Deploy Pipeline

Most of this project rides the same **free tiers** as the beginner Cloud Run project. The one thing
that is **not free** is **Cloud Deploy itself**: a delivery pipeline carries a small **per-day
charge** as long as it exists. It's pennies for a lab session, but it accrues **every day you leave
the pipeline up** — so cleanup matters. Prices are list price in `us-east1`.

---

## Service-by-Service

| Resource | Unit price | Free tier | Your usage | Cost |
|----------|-----------|-----------|------------|------|
| **Cloud Deploy — delivery pipeline** | ~$0.15 / pipeline / day | none | 1 pipeline, a few hours | **~$0.02–0.05** |
| **Cloud Run — requests/compute** | see beginner | 2M req + 180k vCPU-sec/mo | staging + prod, idle | **$0** |
| **Cloud Build** | $0.003 / build-min | 120 build-min/day | 1–2 builds + deploy jobs | **$0** |
| **Artifact Registry** | $0.10 / GB-month | 0.5 GB | 1 image | **$0** |

**Realistic session cost: under $0.10.**

---

## The One Line Item That Isn't Free

**Cloud Deploy bills per delivery pipeline per day** — it's prorated, so a pipeline that exists for a
few hours costs a fraction of the daily rate. The trap is **leaving it up**: an idle pipeline you
forgot about keeps charging the daily rate every day. That's why [Step 6.1](steps/06-cleanup.md)
deletes the pipeline first and calls it the cost-critical action.

Two Cloud Run services and stored images are effectively free at this scale (scale-to-zero + under
the storage free tier), exactly as in the
[beginner project's costs](../../../beginner/gcp/gcp-cloud-run-artifact-registry/costs.md).

---

## Where Money Would Grow

1. **A forgotten pipeline.** The daily per-pipeline charge is small but relentless. Delete pipelines
   you're not actively using.
2. **Min instances > 0 on the services.** As in the beginner project, pinning a warm instance means
   24/7 Cloud Run compute. This lab leaves min at 0 on both targets.
3. **Many old images.** Each release pins an image; if you build lots of versions, prune old tags to
   stay under the 0.5 GB Artifact Registry free tier.

---

## Rule of Thumb

> Cloud Run + Build + Artifact Registry stay ~$0. **Cloud Deploy is the meter that keeps running** —
> a pipeline bills per day whether or not you release anything. Finish the lab and run
> [Step 6](steps/06-cleanup.md) so `gcloud deploy delivery-pipelines list` comes back empty.
