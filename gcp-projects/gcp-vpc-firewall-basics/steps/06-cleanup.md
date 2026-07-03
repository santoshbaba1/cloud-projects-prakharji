# Step 6 — Cleanup

Delete everything you created so nothing keeps running. In GCP you must delete resources in
**dependency order**: VMs first, then firewall rules, then subnets, then the VPC. A VPC won't delete
while anything still lives inside it.

> Even though `e2-micro` VMs are free-tier eligible, deleting them is good hygiene — and the free
> tier only covers **one** `e2-micro` per month, so leaving two running could bill a few cents.

---

## 6.1 Console — Delete in Order

1. **VM instances** (**Compute Engine → VM instances**): select `vm-a` and `vm-b` → **Delete**.
2. **Firewall rules** (**VPC network → Firewall**): select `demo-allow-ssh`, `demo-allow-internal`,
   `demo-allow-http` → **Delete**.
3. **VPC network** (**VPC network → VPC networks**): open `demo-vpc` → **Delete VPC network**. This
   removes the subnets with it.

---

## 6.2 gcloud CLI (Alternative)

```bash
# 1. Delete both VMs
gcloud compute instances delete vm-a vm-b --zone=us-east1-b --quiet

# 2. Delete the firewall rules
gcloud compute firewall-rules delete \
  demo-allow-ssh demo-allow-internal demo-allow-http --quiet

# 3. Delete the subnets
gcloud compute networks subnets delete demo-subnet-a --region=us-east1 --quiet
gcloud compute networks subnets delete demo-subnet-b --region=us-east1 --quiet

# 4. Delete the VPC
gcloud compute networks delete demo-vpc --quiet
```

---

## 6.3 Verify Nothing Is Left

```bash
gcloud compute instances list          # should be empty
gcloud compute networks list           # demo-vpc should be gone
gcloud compute firewall-rules list     # the three demo-* rules should be gone
```

If a delete fails with a "resource is in use" error, something still references it — delete that
child first. See [troubleshooting.md](../troubleshooting.md).

> **Keeping the project?** You'll reuse the same gcloud install, login, project, and billing in the
> [intermediate project](../../gcp-http-lb-autoscaling/README.md). Only the network resources above
> need deleting.

---

## Checkpoint

- [ ] `gcloud compute instances list` returns nothing
- [ ] `gcloud compute networks list` no longer shows `demo-vpc`
- [ ] No `demo-*` firewall rules remain

🎉 **You've built and torn down your first Google Cloud network.** You now understand VPCs, subnets,
firewall rules, network tags, and internal vs. external IPs — the foundation for the
[intermediate load-balancing project](../../gcp-http-lb-autoscaling/README.md).
