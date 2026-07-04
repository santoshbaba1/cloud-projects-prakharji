# Challenges — GCP VPC & Firewall Basics

Extend the lab to deepen your understanding. Each builds on the network you already have. Remember to
clean up any extra resources afterward.

---

## 1. SSH the Right Way: Identity-Aware Proxy (IAP)

You pinned SSH to your home IP — but that breaks when your IP changes. Google's **IAP TCP
forwarding** lets you SSH **without any external IP on the VM and without opening :22 to your IP**.

- Create a rule allowing TCP :22 from IAP's range `35.235.240.0/20` (tag it `iap`).
- Remove the external IP from `vm-b` and connect with `gcloud compute ssh vm-b --tunnel-through-iap`.
- **Question:** Why is IAP more secure than an IP allow-list?

---

## 2. Add a Deny Rule and Watch Priority Win

Create a rule `demo-deny-http` (action **deny**, TCP :80, target tag `web`) at **priority 900** —
lower than `demo-allow-http`'s 1000.

- Reload the web page. It should now be blocked.
- Delete the deny rule; access returns.
- **Lesson:** lower priority number wins, and deny beats allow at the same priority.

---

## 3. Cross-Region Subnet

Add a third subnet `demo-subnet-c` in a **different region** (e.g. `europe-west1`, `10.10.3.0/24`)
and a VM in it. Ping it from `vm-a`.

- It still works with **no peering and no routes added** — proving a GCP VPC is truly global.
- **Question:** How does this differ from AWS, where cross-region needs VPC peering or Transit Gateway?

---

## 4. Egress Firewall Rule

All your rules were **ingress**. Create an **egress** deny rule that blocks `vm-b` from reaching the
internet (deny all egress to `0.0.0.0/0`), then try `curl ifconfig.me` on `vm-b`.

- **Question:** Internal pings still work — why? (Hint: subnet routes vs. the default route.)

---

## 5. VPC Flow Logs

Enable **VPC Flow Logs** on `demo-subnet-a`, regenerate some traffic, and inspect the logs in
**Logging**. Find the log entry for a blocked connection.

- **Question:** What fields tell you *why* a packet was allowed or denied?

---

## 6. Reserve a Static External IP

Reserve a **static** external IP and assign it to `vm-a` so the address survives a stop/start.

- Stop and start `vm-a`; confirm the IP is unchanged.
- **Cost note:** a static IP bills while **not** attached — release it in cleanup.

---

## 7. Reproduce It All in Python

Rewrite Steps 2–4 using the **Google Cloud Client Library for Python**
(`google-cloud-compute`). Write one script that creates the VPC, subnets, firewall rules, and VMs.

- **Goal:** see how the same API you called via `gcloud` looks from code — the foundation for
  infrastructure automation. Keep it readable: one function per resource.
