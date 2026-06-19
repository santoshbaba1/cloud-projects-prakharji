# Troubleshooting — Kubernetes Optimization & Recovery

Error → Cause → Fix.

---

## `kubectl top` says "Metrics API not available"

**Symptom:** `error: Metrics API not available`, and the HPA shows `<unknown>/50%`.

**Causes & fixes:**

1. **metrics-server not installed.** Install it (Step 1.2). minikube: `minikube addons enable
   metrics-server`. kind: apply `components.yaml`.
2. **kind: TLS handshake failing.** metrics-server can't verify the kubelet's self-signed cert.
   Add `--kubelet-insecure-tls` to its args (Step 1.2 patch). Without it, the deployment runs but
   reports no metrics.
3. **Too soon.** It scrapes on an interval; wait 30–60s after the pod is Ready and retry.

---

## Pods stuck in `ImagePullBackOff` / `ErrImagePull`

**Symptom:** `webapp` pods never start; events show it can't pull `webapp:1.0`.

**Cause:** The cluster runs in its own container/VM and **can't see your laptop's local image**.

**Fix:** Load the image into the cluster after building (Step 2.2):
- kind: `kind load docker-image webapp:1.0 --name optrec`
- minikube: `minikube image load webapp:1.0 --profile optrec`

The Deployment uses `imagePullPolicy: IfNotPresent` so it won't try a registry once the image is
loaded. Rebuilt the image? **Reload it** — the cluster keeps the old copy otherwise.

---

## HPA shows `<unknown>/50%` and never scales

**Cause:** No metrics (see the first entry) **or** the Deployment has no CPU **request**. The HPA
computes utilization as a percentage of the **request**; with no request there's nothing to divide
by.

**Fix:** Ensure metrics-server works *and* the Deployment sets `resources.requests.cpu` (it does —
`100m`). Confirm with `kubectl describe hpa -n webapp`.

---

## HPA doesn't scale even under load

**Causes & fixes:**

1. **Load too weak.** The load Job hits `/burn?ms=400` in a loop; if it finished or never started,
   check `kubectl logs -n webapp job/load-generator`.
2. **Limit caps CPU below the trigger math.** With request `100m` and target `50%`, the HPA wants
   to keep pods near `50m`. A loop pegging the pod to its `250m` limit pushes far past that, which
   *should* scale out — if it doesn't, metrics are stale; wait a cycle.
3. **maxReplicas reached.** It won't go past `6`. That's expected.

---

## Pod keeps restarting (CrashLoopBackOff or rising RESTARTS)

**Causes & fixes:**

1. **Liveness probe failing.** If `/healthz` isn't reachable (wrong port, app not listening),
   liveness restarts the container repeatedly. Confirm the container listens on `5000` and
   `/healthz` returns 200: `kubectl logs -n webapp <pod>`.
2. **Memory limit too low (OOMKilled).** `kubectl describe pod` shows `Reason: OOMKilled`. Raise
   the memory limit. (If you lowered it in Step 3.3 to see this, put it back to `128Mi`.)

---

## Velero backup stuck in `InProgress` or `Failed`

**Causes & fixes:**

1. **Backup location not Available.** `velero backup-location get` must show **Available**. If not,
   the MinIO endpoint/credentials are wrong — recheck the `s3Url=http://minio.velero.svc:9000`,
   `s3ForcePathStyle=true`, and the `credentials-velero` file (user `minio` / pass `minio123`).
2. **Bucket missing.** The `velero` bucket must exist in MinIO (the `mc mb m/velero` step). Without
   it, backups fail to upload.
3. **MinIO not ready.** `kubectl get pods -n velero` — MinIO must be Running before Velero can
   write.

---

## Restore completes but pods aren't Running

**Cause:** After a restore, the image must still be present in the cluster. On kind/minikube the
image survives a namespace delete (it's at the node level), so this usually works — but if you
deleted the *cluster* you must rebuild and reload (Step 2.2).

**Fix:** Reload `webapp:1.0` into the cluster, then the recreated pods can start. Restoring objects
doesn't restore images.

---

## `kubectl drain` removes everything despite the PDB

**Cause:** On a **single-node** local cluster, draining the only node is an edge case — and `--force`
overrides budgets. The PDB protects against *graceful* eviction, which a single-node `drain
--force` bypasses.

**Fix:** This is a teaching limitation of one node. To see a PDB truly hold the line, use a
multi-node cluster (`kind create cluster` with multiple workers) — [Challenge 4](challenges.md).

---

## General debugging checklist

1. `kubectl get pods -A` — is everything Running? Read events with `kubectl describe`.
2. Image **loaded** into the cluster (not just built) after every rebuild.
3. metrics-server **1/1** and `kubectl top nodes` returns numbers before expecting HPA/`top`.
4. Velero: backup-location **Available**, bucket exists, MinIO Running.
5. Logs are your friend: `kubectl logs -n <ns> <pod>` and `velero backup describe --details`.
