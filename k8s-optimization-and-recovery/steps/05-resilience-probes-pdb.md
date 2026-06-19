# Step 5 — Self-Healing & Disruption Budget

Recovery in Kubernetes starts *before* any backup tool: the platform constantly works to keep your
declared state true. This step shows two built-in recovery mechanisms — **self-healing** via the
Deployment + probes, and the **PodDisruptionBudget (PDB)** that protects availability during
planned disruptions.

---

## 5.1 Self-Healing: Delete a Pod, Watch It Return

A Deployment's job is to keep `replicas` pods alive. Kill one and the ReplicaSet recreates it:

```bash
kubectl get pods -n webapp
kubectl delete pod -n webapp <one-webapp-pod>
kubectl get pods -n webapp -w
```

A new pod appears **immediately** and reaches Ready. You didn't do anything — the controller
reconciled actual state back to desired state. That's the most common "recovery" in Kubernetes,
happening constantly.

---

## 5.2 Probes: How Kubernetes Knows a Pod Is Unhealthy

Your Deployment defines two probes against `/healthz`:

```yaml
readinessProbe: { httpGet: { path: /healthz, port: 5000 }, periodSeconds: 5 }
livenessProbe:  { httpGet: { path: /healthz, port: 5000 }, periodSeconds: 10 }
```

- **Readiness** decides whether a pod receives Service traffic. Failing readiness → pulled from the
  load-balancing pool but **not** restarted (it might just be warming up).
- **Liveness** decides whether the container is **hung**. Failing liveness → kubelet **restarts**
  the container.

Watch a liveness restart by breaking health temporarily. Exec in and make `/healthz` unreachable
(kill the process), then watch the **RESTARTS** column tick up:

```bash
kubectl exec -n webapp <pod> -- kill 1     # kill the app process
kubectl get pods -n webapp -w              # RESTARTS increments, pod returns to Ready
```

> **Readiness vs liveness is a classic mix-up.** Readiness = "should I send traffic?" Liveness =
> "should I restart it?" Pointing liveness at a slow dependency can cause restart loops; readiness
> is the safer gate for "temporarily busy."

---

## 5.3 PodDisruptionBudget: Protect Availability During Drains

A PDB constrains **voluntary** disruptions (node drains, rolling upgrades) so you don't lose all
pods at once. Yours guarantees at least one pod stays up:

```bash
kubectl apply -f k8s/pdb.yaml
kubectl get pdb -n webapp
```

```
NAME     MIN AVAILABLE   ALLOWED DISRUPTIONS
webapp   1               1
```

Simulate a node drain (on a single-node local cluster the node *is* everything, so this is
illustrative):

```bash
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data --force --dry-run=server
```

With `minAvailable: 1`, the eviction API will **refuse** to take the last pod below 1 — a rolling
node upgrade must wait for a replacement pod to be Ready first. That's how you patch nodes without
an outage.

> **PDB protects against *voluntary* disruptions only** (things `kubectl drain` / the cluster
> autoscaler do). It does **not** save you from a node crashing — that's what replicas across
> multiple nodes are for. On one local node it's a teaching artifact; on EKS with 3 nodes it's
> real protection.

---

## Checkpoint

- [ ] Deleting a pod triggered automatic recreation (self-healing)
- [ ] You saw a **liveness** restart increment the RESTARTS count
- [ ] You can explain readiness (traffic gate) vs liveness (restart trigger)
- [ ] The PDB reports `MIN AVAILABLE 1` and you understand it guards *voluntary* disruptions

---

**Next:** [Step 6 — Back Up & Restore with Velero](./06-backup-restore-velero.md)
