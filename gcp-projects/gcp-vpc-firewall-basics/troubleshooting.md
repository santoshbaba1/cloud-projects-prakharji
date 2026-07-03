# Troubleshooting — GCP VPC & Firewall Basics

Error → Cause → Fix for the problems you're most likely to hit.

---

## Error: `gcloud: command not found`

**Cause:** The gcloud CLI isn't on your PATH, usually because the shell wasn't restarted after install.

**Fix:** Close and reopen your terminal (or run `exec -l $SHELL`). Re-run `gcloud --version`. On
Windows, use the terminal the installer opened, or reopen PowerShell.

---

## Error: `PERMISSION_DENIED: ... Compute Engine API has not been used in project ... before or it is disabled`

**Cause:** The Compute Engine API isn't enabled in your project.

**Fix:**
```bash
gcloud services enable compute.googleapis.com
```
Wait ~1 minute and retry. (This is Step 1.6.)

---

## Error: `Required 'compute.networks.create' permission` / billing errors

**Cause:** No billing account is linked to the project, or your account lacks the role.

**Fix:** Link billing (Step 1.5). As the project creator you're `Owner`, which is sufficient. Verify:
```bash
gcloud billing projects describe "$(gcloud config get-value project)"
```

---

## Problem: `gcloud compute ssh vm-a` hangs or times out

**Cause (most common):** Your `demo-allow-ssh` rule allows a **different** IP than you have now.
Home/office IPs change, and VPNs change them too.

**Fix:** Update the rule to your current IP:
```bash
gcloud compute firewall-rules update demo-allow-ssh \
  --source-ranges="$(curl -s ifconfig.me)/32"
```
**Other causes:** the VM isn't `RUNNING` yet (wait 30s), or your key hasn't propagated (retry once).

---

## Problem: Browser can't reach `http://<vm-a-external-ip>`

Work through these in order:

1. **Is the server running?** SSH into `vm-a` and confirm `sudo python3 hello_server.py` prints
   `Serving on port 80`. If it exited, re-run it.
2. **Right IP?** Use the **EXTERNAL** IP from `gcloud compute instances list`, not the internal
   `10.10.x.x`.
3. **Is the VM tagged `web`?** `demo-allow-http` only opens :80 on VMs with the `web` tag:
   ```bash
   gcloud compute instances describe vm-a --zone=us-east1-b --format='value(tags.items)'
   ```
   If empty, add it: `gcloud compute instances add-tags vm-a --zone=us-east1-b --tags=web`.
4. **`http` not `https`:** the server only speaks plain HTTP on port 80.

---

## Problem: `ping 10.10.2.2` from vm-a gets no reply

**Cause:** The `demo-allow-internal` rule is missing `icmp`, or the source range doesn't cover the VPC.

**Fix:** Confirm the rule allows `icmp` from `10.10.0.0/16`:
```bash
gcloud compute firewall-rules describe demo-allow-internal \
  --format='value(allowed,sourceRanges)'
```
Recreate it per [Step 3](steps/03-firewall-rules.md) if needed. Also make sure you're pinging the
**internal** IP, not the external one.

---

## Error on cleanup: `The network resource ... is already being used by ...`

**Cause:** You're deleting the VPC (or a subnet) while a VM or firewall rule still references it. GCP
deletes strictly child-before-parent.

**Fix:** Delete in order — **VMs → firewall rules → subnets → VPC**. See
[Step 6](steps/06-cleanup.md). List what's left with `gcloud compute instances list` and
`gcloud compute firewall-rules list --filter="network:demo-vpc"`.

---

## Error: `The resource ... already exists`

**Cause:** You ran a create command twice, or a previous run half-completed.

**Fix:** Either reuse the existing resource (it's fine) or delete it and recreate:
```bash
gcloud compute networks delete demo-vpc --quiet   # then recreate
```
