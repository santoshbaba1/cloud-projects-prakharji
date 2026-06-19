# Step 4 — Autoscale with an HPA

In Project 1 you *manually* resized one instance. Kubernetes can do it **automatically** with a
**Horizontal Pod Autoscaler (HPA)**: when average CPU across pods crosses a target, it adds
replicas; when load drops, it removes them. This is the cloud-native answer to demand changes —
scale **out**, not just **up**.

---

## 4.1 Apply the HPA

```bash
kubectl apply -f k8s/hpa.yaml
kubectl get hpa -n webapp
```

```
NAME     REFERENCE           TARGETS   MINPODS   MAXPODS   REPLICAS
webapp   Deployment/webapp   2%/50%    2         6         2
```

`TARGETS` reads `current%/target%`. The target is **50% of the CPU request** (100m), i.e. ~50m
average per pod. Idle, you're at ~2% → it stays at the floor of **2** replicas.

> If `TARGETS` shows `<unknown>/50%`, metrics-server isn't reporting yet — wait a minute or revisit
> [Step 1.3](./01-setup-cluster.md). The HPA literally can't act without metrics.

---

## 4.2 Generate Load

Run the load-generator Job — a pod inside the cluster that hammers `/burn` for ~3 minutes:

```bash
kubectl apply -f k8s/load-generator.yaml
```

In a second terminal, watch the autoscaler react:

```bash
kubectl get hpa -n webapp -w
# and, alongside:
kubectl get pods -n webapp -w
```

Within ~1–2 minutes you'll see `TARGETS` climb past 50%, `REPLICAS` rise toward **6**, and new
`webapp-*` pods appear and become Ready. The HPA is adding capacity to hold the CPU target.

---

## 4.3 Watch It Scale Back In

When the Job finishes (~3 min) load drops. Scale-**in** is deliberately slower than scale-out
(default 5-minute stabilization window) so a brief lull doesn't thrash your replica count. Keep
watching:

```bash
kubectl get hpa -n webapp -w
```

After the cooldown, `REPLICAS` settles back to **2**. You just watched demand-driven optimization:
capacity followed load up and back down, automatically.

---

## 4.4 Connect It Back to the Series

| | EC2 (Project 1) | Kubernetes (here) |
|--|------------------|-------------------|
| Unit scaled | instance **size** (vertical) | pod **count** (horizontal) |
| Trigger | weekly CloudWatch review | live HPA on CPU% |
| Action | stop / modify type | add / remove replicas |
| Speed | minutes (stop+modify) | seconds (schedule a pod) |

Horizontal scaling is usually preferable for stateless web apps (no downtime, finer granularity).
Vertical (rightsizing the request/limit, or a **VPA**) still matters for getting each pod's
baseline right — see [Challenge 3](../challenges.md).

---

## Checkpoint

- [ ] `kubectl get hpa` shows a real `current/target` (not `<unknown>`)
- [ ] Under the load Job, `REPLICAS` scaled up toward `maxReplicas` (6)
- [ ] After load stopped, it scaled back to `minReplicas` (2) following the cooldown
- [ ] You can contrast horizontal (HPA) vs vertical (EC2 resize) scaling

---

**Next:** [Step 5 — Self-Healing & Disruption Budget](./05-resilience-probes-pdb.md)
