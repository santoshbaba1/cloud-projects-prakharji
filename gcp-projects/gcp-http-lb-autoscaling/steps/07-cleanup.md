# Step 7 — Cleanup ⚠️

**This project bills real (small) money while it runs** — 2–6 `e2-small` VMs, a load balancer, and a
Cloud NAT gateway. Delete everything now. Load-balancer pieces must be deleted in **reverse order**
of creation (front-to-back), because each references the one behind it.

> Rough cost if left running: **~$0.10–0.20/hr** (see [costs.md](../costs.md)). A forgotten load
> balancer + MIG over a weekend is a real bill.

---

## 7.1 Delete the Load Balancer (front → back)

```bash
# Forwarding rule first (it holds the static IP + proxy)
gcloud compute forwarding-rules delete web-forwarding-rule --global --quiet

# Then the proxy, URL map, backend service
gcloud compute target-http-proxies delete web-http-proxy --quiet
gcloud compute url-maps delete web-url-map --quiet
gcloud compute backend-services delete web-backend --global --quiet

# The LB health check and the static IP
gcloud compute health-checks delete web-lb-hc --quiet
gcloud compute addresses delete web-lb-ip --global --quiet
```

---

## 7.2 Delete the MIG, Template, and Autohealing Health Check

```bash
# Deleting the MIG deletes its VMs and the autoscaler with it
gcloud compute instance-groups managed delete web-mig --region=us-east1 --quiet

# Now the template and the Step-4 health check are unreferenced
gcloud compute instance-templates delete web-template --quiet
gcloud compute health-checks delete web-hc --quiet
```

---

## 7.3 Delete Cloud NAT, Router, and the Network

```bash
# NAT lives on the router; delete it first
gcloud compute routers nats delete web-nat --router=web-router --region=us-east1 --quiet
gcloud compute routers delete web-router --region=us-east1 --quiet

# Firewall rules, then subnet, then VPC
gcloud compute firewall-rules delete \
  web-allow-health-check web-allow-iap-ssh web-allow-internal --quiet
gcloud compute networks subnets delete web-subnet --region=us-east1 --quiet
gcloud compute networks delete web-vpc --quiet
```

---

## 7.4 Console (Alternative)

Delete in this order (each screen is under **☰**):

1. **Network services → Load balancing** → delete the load balancer `web-url-map` (this removes the
   forwarding rule, proxy, URL map, and backend service together).
2. **VPC network → IP addresses** → release `web-lb-ip`.
3. **Compute Engine → Health checks** → delete `web-lb-hc` and `web-hc`.
4. **Compute Engine → Instance groups** → delete `web-mig`.
5. **Compute Engine → Instance templates** → delete `web-template`.
6. **Network services → Cloud NAT** → delete `web-nat`; then **Cloud Routers** → delete `web-router`.
7. **VPC network → Firewall** → delete the three `web-allow-*` rules.
8. **VPC network → VPC networks** → delete `web-vpc` (removes the subnet).

---

## 7.5 Verify Nothing Is Left (and Still Billing)

```bash
gcloud compute forwarding-rules list          # empty
gcloud compute backend-services list          # empty
gcloud compute instance-groups managed list   # empty
gcloud compute addresses list                 # no web-lb-ip
gcloud compute routers list                   # no web-router
gcloud compute networks list                  # no web-vpc
```

> **The two easiest things to forget:** the **static IP** (`web-lb-ip`) bills while reserved even
> after the LB is gone, and **Cloud NAT** bills per hour. Both are covered above — just confirm the
> `addresses list` and `routers list` are empty.

---

## Checkpoint

- [ ] All load-balancer components deleted (forwarding rule, proxy, URL map, backend service)
- [ ] `web-mig`, `web-template`, and both health checks deleted
- [ ] Cloud NAT and Cloud Router deleted
- [ ] Static IP `web-lb-ip` released
- [ ] `web-vpc`, its subnet, and firewall rules deleted

🎉 **You built a production-shaped web tier**: private autoscaling VMs behind a global HTTP load
balancer, reachable outbound via Cloud NAT, healing themselves and scaling on demand — then tore it
all down cleanly.
