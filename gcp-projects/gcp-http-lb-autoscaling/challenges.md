# Challenges — GCP HTTP Load Balancer & Autoscaling

Extend the web tier toward production. Each challenge assumes the LB + MIG from the main steps are
still up (or rebuild them). Clean up extras afterward.

---

## 1. Add HTTPS with a Google-Managed Certificate

Serve traffic over TLS without buying or renewing certs yourself.

- Reserve a domain (or use a free one) and point an A record at `web-lb-ip`.
- Create a **managed SSL certificate** for the domain.
- Add a **target HTTPS proxy** + a `:443` forwarding rule using the cert.
- **Question:** Why does a managed cert require the domain's DNS to resolve to the LB *before* it
  provisions?

---

## 2. Redirect HTTP → HTTPS

Once HTTPS works, change the `:80` path to **301-redirect** to `:443` using a URL map redirect action,
so no one is served plaintext.

- **Question:** Where in the LB chain does the redirect happen — proxy, URL map, or backend?

---

## 3. Rolling Update to a New Template Version

Ship new code the MIG way, with zero downtime.

- Edit `app.py` (e.g. change the greeting), bake a new template `web-template-v2`.
- Run a **rolling update**:
  ```bash
  gcloud compute instance-groups managed rolling-action start-update web-mig \
    --region=us-east1 --version=template=web-template-v2 \
    --max-surge=2 --max-unavailable=0
  ```
- Watch instances replace gradually while `curl` keeps returning 200.
- **Question:** What does `--max-unavailable=0` guarantee, and what does it cost you?

---

## 4. Path-Based Routing

Add a second MIG (`api-mig`) and change the URL map so `/api/*` routes to `api-backend` while `/`
stays on `web-backend`.

- **Question:** How is this different from running two separate load balancers?

---

## 5. Turn On Cloud CDN

Enable **Cloud CDN** on the backend service and add a cacheable route to the app. Measure the
latency difference on a cache hit vs. miss.

- **Question:** Which responses are safe to cache, and how does `Cache-Control` control it?

---

## 6. Scale on Requests-Per-Second Instead of CPU

Reconfigure the autoscaler to target **load-balancing utilization** / RPS rather than CPU.

- **Question:** For a lightweight web app, why might RPS be a better scaling signal than CPU?

---

## 7. Rebuild It in Python

Recreate the MIG + load balancer using the **`google-cloud-compute`** Python client library, one
readable function per resource (template, MIG, health check, backend service, URL map, proxy,
forwarding rule).

- **Goal:** see the same API you drove with `gcloud` as code — the basis for real IaC.
- Compare the effort to doing it in **Terraform** (a stretch goal): which pieces map 1:1?
