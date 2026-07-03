# Costs — GCP HTTP Load Balancer & Autoscaling

**Read this before you start.** Unlike the beginner project, this one **has no free-tier umbrella**.
The load balancer and Cloud NAT bill per hour whether or not anyone uses them. Budget **$0.20–$0.60**
for a session and **delete everything the same day** ([Step 7](steps/07-cleanup.md)). Prices are list
price in `us-east1`.

---

## Service-by-Service

| Resource | Unit price | Free tier | Your usage | Cost |
|----------|-----------|-----------|------------|------|
| **`e2-small` VM** | ~$0.0168 / hr | none (`e2-small` isn't the free `e2-micro`) | 2–6 VMs × ~2 hr | **~$0.07–0.20** |
| **External Application LB — forwarding rule** | ~$0.025 / hr | first 5 rules billed hourly | 1 rule × ~2 hr | **~$0.05** |
| **External Application LB — data processed** | ~$0.008–0.012 / GB | — | a few MB | **~$0** |
| **Cloud NAT — gateway** | ~$0.0014 / hr | — | 1 × ~2 hr | **~$0.003** |
| **Cloud NAT — data processed** | ~$0.045 / GB | — | apt/pip (tens of MB) | **~$0.01** |
| **Boot disks (standard PD)** | $0.04 / GB-month | 30 GB-month | 2–6 × 10 GB × ~2 hr | **~$0.01** |
| **Static IP (in use)** | $0 while attached | — | 1 global IP, in use | **$0** |
| **VPC / subnet / firewall / router** | Free | — | all of it | **$0** |

**Realistic 2-hour session: ~$0.20–0.40.**

---

## Where the Money Actually Goes

1. **The forwarding rule.** The single biggest line item (~$0.025/hr) and it bills the moment the LB
   exists — before any traffic. This is why you don't leave a load balancer up "to finish later."
2. **`e2-small` VMs during the scale test.** Six VMs briefly during the load test add up faster than
   the two-VM baseline. They scale back down, but delete the MIG when done.
3. **Cloud NAT left running.** Small per-hour charge, but it's easy to forget because it's not a VM.
4. **A reserved-but-unused static IP.** After you delete the LB, an *unattached* static IP bills
   ~$0.007/hr. Release `web-lb-ip` in cleanup — [Step 7.1](steps/07-cleanup.md).

---

## Why `e2-small` and Not the Free `e2-micro`?

The Always-Free tier covers one `e2-micro`, but `e2-micro` has only ~1 GB RAM — tight for
`pip install flask` plus running the app across multiple autoscaled VMs. `e2-small` (2 GB) is
reliable for the lab. If you want to minimize cost, you can drop the template to `e2-micro` and lower
the MIG max to 3 — expect occasional slow boots.

---

## Rule of Thumb

> The load balancer + NAT bill **per hour, idle or not**. There is no "it's basically free if I
> forget it" here. Finish the lab, run [Step 7](steps/07-cleanup.md), and verify
> `gcloud compute forwarding-rules list` and `gcloud compute addresses list` are empty.
