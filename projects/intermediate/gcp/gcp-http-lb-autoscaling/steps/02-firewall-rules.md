# Step 2 — Firewall Rules

Your VMs are private, but two kinds of traffic still need to reach them: the **load balancer's health
checks** and **your SSH sessions**. Google's load balancer and health checkers send traffic from
**specific Google-owned IP ranges** — you must allow those explicitly, or every backend will look
"unhealthy" and the LB will serve `502`s.

---

## 2.1 The Rules You'll Create

| Rule | Allows | From (source) | To (target tag) | Why |
|------|--------|---------------|-----------------|-----|
| `web-allow-health-check` | TCP :80 | `35.191.0.0/16`, `130.211.0.0/22` | `web` | Google's health checkers + LB live here |
| `web-allow-iap-ssh` | TCP :22 | `35.235.240.0/20` | `web` | SSH via IAP (no external IP needed) |
| `web-allow-internal` | all | `10.20.0.0/24` | `web` | VM-to-VM traffic inside the subnet |

> **Why those two health-check ranges?** `130.211.0.0/22` and `35.191.0.0/16` are the fixed,
> Google-published source ranges for **load balancer** and **health-check** probes. They're the same
> for every customer. Memorize them — a missing allow rule for these is the #1 cause of "why is my
> load balancer returning 502?"

Every VM in the group carries the network tag **`web`**, so all three rules target that tag.

---

## 2.2 Console — Create the Rules

**☰ → VPC network → Firewall → Create firewall rule**, three times.

### `web-allow-health-check`

| Field | Value |
|-------|-------|
| Name | `web-allow-health-check` |
| Network | `web-vpc` |
| Direction / Action | Ingress / Allow |
| Targets | Specified target tags → `web` |
| Source IPv4 ranges | `35.191.0.0/16`, `130.211.0.0/22` |
| Protocols and ports | TCP `80` |

### `web-allow-iap-ssh`

| Field | Value |
|-------|-------|
| Name | `web-allow-iap-ssh` |
| Network | `web-vpc` |
| Targets | Specified target tags → `web` |
| Source IPv4 ranges | `35.235.240.0/20` |
| Protocols and ports | TCP `22` |

### `web-allow-internal`

| Field | Value |
|-------|-------|
| Name | `web-allow-internal` |
| Network | `web-vpc` |
| Targets | Specified target tags → `web` |
| Source IPv4 ranges | `10.20.0.0/24` |
| Protocols and ports | Allow all |

---

## 2.3 gcloud CLI (Alternative)

```bash
# 1. Allow health checks + load-balancer probes on :80 (Google's fixed ranges)
gcloud compute firewall-rules create web-allow-health-check \
  --network=web-vpc \
  --direction=INGRESS --action=ALLOW \
  --rules=tcp:80 \
  --source-ranges=35.191.0.0/16,130.211.0.0/22 \
  --target-tags=web

# 2. Allow SSH via Identity-Aware Proxy (so you don't need external IPs)
gcloud compute firewall-rules create web-allow-iap-ssh \
  --network=web-vpc \
  --direction=INGRESS --action=ALLOW \
  --rules=tcp:22 \
  --source-ranges=35.235.240.0/20 \
  --target-tags=web

# 3. Allow all traffic between VMs inside the subnet
gcloud compute firewall-rules create web-allow-internal \
  --network=web-vpc \
  --direction=INGRESS --action=ALLOW \
  --rules=all \
  --source-ranges=10.20.0.0/24 \
  --target-tags=web
```

Verify:

```bash
gcloud compute firewall-rules list --filter="network:web-vpc"
```

---

## 2.4 Notice What's *Not* Here

There's **no rule allowing :80 from `0.0.0.0/0`.** The public never talks to the VMs directly — they
talk to the **load balancer**, which then forwards from the health-check ranges you allowed. That's
the security win of this architecture: the backends are only reachable through the front door.

---

## Checkpoint

- [ ] `web-allow-health-check` allows :80 from `35.191.0.0/16` **and** `130.211.0.0/22`
- [ ] `web-allow-iap-ssh` allows :22 from `35.235.240.0/20`
- [ ] `web-allow-internal` allows all traffic from `10.20.0.0/24`
- [ ] All three target the tag `web`
- [ ] There is **no** rule opening :80 to the whole internet

---

**Next:** [Step 3 — Instance Template](./03-instance-template.md)
