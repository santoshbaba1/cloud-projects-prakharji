# Costs — GCP VPC & Firewall Basics

This project is designed to cost **essentially nothing** ($0.00–$0.05) if you clean up the same day.
Google Cloud's **Always Free** tier and per-second billing keep it cheap. Prices are list price in
`us-east1`.

---

## Service-by-Service

| Resource | Unit price | Always-Free allowance | Your usage | Cost |
|----------|-----------|-----------------------|------------|------|
| **`e2-micro` VM** | ~$0.0084 / hr | **1 `e2-micro`/month free** (us-east1/us-west1/us-central1) | 2 VMs × ~1 hr | **~$0** (1st free) + ~$0.01 (2nd) |
| **Boot disk (standard PD)** | $0.04 / GB-month | 30 GB-month free | 2 × 10 GB × ~1 hr | **~$0** |
| **VPC / subnets / firewall / routes** | Free | — | all of it | **$0** |
| **Internal (VPC) traffic** | Free within a zone | — | ping/curl between VMs | **$0** |
| **Internet egress (North America)** | $0.085–0.12 / GB | **1 GB/month free** | a few KB of web requests | **$0** |
| **External IP (while VM running)** | ~$0.0011 / hr in-use | — | 2 IPs × ~1 hr | **~$0** |

---

## The Two Things That Could Cost You

1. **Leaving VMs running.** VMs bill per second **while RUNNING**, even idle. Two `e2-micro` left up
   for a week ≈ **$3**. Delete them in [Step 6](steps/06-cleanup.md).
2. **An unattached (static) external IP.** This project uses *ephemeral* IPs (released when the VM is
   deleted), so this isn't a risk here — but reserving a static IP and not using it bills ~$0.007/hr.

---

## Free Tier Notes

- The **Always Free** `e2-micro` covers exactly **one** instance per month, and only in `us-east1`,
  `us-west1`, or `us-central1`. That's why this repo uses `us-east1`.
- Networking primitives (VPC, subnets, firewall rules, routes) are **never** billed — you only pay
  for VMs, disks, static IPs, and egress.

---

## Rule of Thumb

> If you finish all six steps in one sitting and run cleanup, expect a bill of **$0.00** (or a couple
> of cents for the second VM). The only way this project costs real money is forgetting the VMs.
