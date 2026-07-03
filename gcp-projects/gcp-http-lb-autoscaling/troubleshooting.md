# Troubleshooting — GCP HTTP Load Balancer & Autoscaling

Error → Cause → Fix. Load balancers have many moving parts; most problems are one missing link in the
chain.

---

## The load balancer returns `502 Server Error` (the classic)

Almost always one of these, in order of likelihood:

1. **Health-check firewall rule missing.** The LB probes from `35.191.0.0/16` and `130.211.0.0/22`.
   Without `web-allow-health-check` allowing :80 from those ranges, every backend is "unhealthy" and
   the LB has nowhere to send traffic.
   ```bash
   gcloud compute firewall-rules describe web-allow-health-check \
     --format='value(sourceRanges,allowed,targetTags)'
   ```
   It must list both ranges, `tcp:80`, and tag `web`.

2. **You just created it — wait.** Backends can take **3–7 minutes** to pass health checks and for
   the LB config to propagate globally. Grab a coffee, then retry.

3. **The app isn't listening on :80.** SSH into a VM (via IAP) and check:
   ```bash
   gcloud compute ssh <vm-name> --zone=us-east1-b --tunnel-through-iap
   curl -s localhost:80/healthz   # should print "ok"
   sudo tail /var/log/app.log     # startup-script output
   ```

4. **Named port mismatch.** The MIG's named port (`http:80`) must match the backend service's
   `--port-name=http`. Check with:
   ```bash
   gcloud compute instance-groups managed describe web-mig --region=us-east1 \
     --format='value(namedPorts)'
   ```

Check overall backend health directly:
```bash
gcloud compute backend-services get-health web-backend --global
```

---

## Backends never become healthy

**Cause:** The startup script failed, so Flask isn't running (often no internet to `pip install`).

**Fix:** Confirm **Cloud NAT** is working — private VMs can't reach the internet without it.
```bash
gcloud compute routers nats describe web-nat --router=web-router --region=us-east1
```
SSH in via IAP and check `/var/log/app.log` and `/var/log/syslog` for the startup script. Re-check
that the template used `--no-address` **and** NAT exists — a private VM with no NAT can't install
anything.

---

## `gcloud compute ssh ... --tunnel-through-iap` fails

**Cause:** The `web-allow-iap-ssh` rule is missing, or the IAP API isn't enabled.

**Fix:** Ensure the rule allows :22 from `35.235.240.0/20` to tag `web`. Enable IAP if prompted:
```bash
gcloud services enable iap.googleapis.com
```

---

## Autoscaler won't scale out under load

**Causes & fixes:**

- **Load isn't hitting CPU.** The `/load` route must actually run. Verify a single call works:
  `curl http://<LB_IP>/load` should pause ~15s then reply. If it 502s, fix the LB first.
- **Not enough concurrent load.** One request at a time won't move average CPU. Use the parallel loop
  or the Python `loadtest.py` in [Step 6](steps/06-test-and-scale.md).
- **Cooldown / ramp.** The autoscaler evaluates over a window — give it **2–4 minutes** of sustained
  load before expecting new VMs.
- **Already at max.** Check it isn't capped: `--max-num-replicas` is 6.

---

## Autoscaler killed my new VMs immediately (autohealing loop)

**Cause:** No `--initial-delay`, so the MIG health-checked VMs before the startup script finished
installing Flask, declared them unhealthy, and recreated them — forever.

**Fix:** Set an initial delay so new VMs get time to boot:
```bash
gcloud compute instance-groups managed update web-mig --region=us-east1 --initial-delay=120
```

---

## `curl` always returns the *same* hostname

**Not necessarily a bug.** With few requests and connection reuse you may stick to one backend. Force
fresh connections:
```bash
for i in $(seq 1 10); do curl -s "http://<LB_IP>/" ; done
```
Also confirm both VMs are healthy (`get-health` above). If only one is healthy, traffic *should* all
go to it.

---

## Cleanup: `resource is in use by another resource`

**Cause:** Deleting a load-balancer component out of order. Each piece references the one behind it.

**Fix:** Delete **front to back**: forwarding rule → target proxy → URL map → backend service →
health check → static IP. Then MIG → template. See [Step 7](steps/07-cleanup.md).

---

## Surprise bill after "cleanup"

**Cause:** A reserved static IP or Cloud NAT left behind — neither is a VM, so they're easy to miss.

**Fix:**
```bash
gcloud compute addresses list   # release any web-lb-ip
gcloud compute routers list     # delete web-router (takes NAT with it)
```
