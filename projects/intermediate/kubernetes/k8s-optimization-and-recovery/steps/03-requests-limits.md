# Step 3 — Right-Size with Requests & Limits

This is the Kubernetes version of EC2 rightsizing from
[Project 1](../../../aws/aws-compute-rightsizing/README.md). Instead of choosing an instance type, you tell
Kubernetes how much CPU/memory each pod **requests** (reserves) and its **limit** (ceiling). Get
this wrong and you either waste capacity (requests too high) or get pods throttled and
**OOMKilled** (limits too low).

The Deployment you applied already sets them:

```yaml
resources:
  requests:   { cpu: "100m", memory: "64Mi" }   # scheduler reserves this
  limits:     { cpu: "250m", memory: "128Mi" }  # hard ceiling
```

---

## 3.1 See Real Usage with `kubectl top`

```bash
kubectl top pods -n webapp
```

```
NAME            CPU(cores)   MEMORY(bytes)
webapp-xxxx     2m           38Mi
webapp-yyyy     2m           37Mi
```

Idle, each pod uses ~2 millicores and ~38Mi. Compare to the **request** (100m / 64Mi): you're
reserving far more than idle needs — which is correct (requests should cover *typical* load, not
idle), but if real peak stays this low you're over-provisioned. **Right-sizing is reading these
numbers and adjusting**, exactly like reading CloudWatch CPU in Project 1.

---

## 3.2 Understand the QoS Class It Produced

```bash
kubectl get pod -n webapp -l app=webapp \
  -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.status.qosClass}{"\n"}{end}'
```

You'll see **`Burstable`** — because requests are set but **lower than** limits. The three classes:

| QoS class | When | Eviction priority |
|-----------|------|-------------------|
| `Guaranteed` | requests **==** limits for every resource | evicted **last** |
| `Burstable` | requests set, **<** limits (our app) | evicted in the middle |
| `BestEffort` | **no** requests or limits | evicted **first** |

> **"No limits" is the trap.** A `BestEffort` pod with no requests/limits looks "simpler" but the
> scheduler can't reserve room for it, it can burst until it starves neighbors, and it's the
> **first** thing evicted under pressure. Always set at least requests.

---

## 3.3 Watch a Limit Bite (Optional but Illuminating)

The CPU limit is `250m` — a quarter core. Hit `/burn`, which tries to peg a full core, and watch
`kubectl top` cap the pod near 250m instead of letting it run away:

```bash
# with port-forward running from Step 2:
curl -s "localhost:8080/burn?ms=3000" &
kubectl top pods -n webapp        # the burning pod sits ~250m, not higher — throttled to its limit
```

That throttling is the CPU limit protecting the node. (A *memory* limit is harsher: exceed it and
the container is **OOMKilled** and restarted — try lowering `memory` limit drastically and
re-applying if you want to see it, then put it back.)

---

## 3.4 Right-Size from Data

You've now *measured* (top), *classified* (QoS), and *seen the ceiling* (throttle). That's the
full rightsizing loop. If `kubectl top` showed steady-state CPU well under the request, you'd
lower the request to pack more pods per node; if pods were getting OOMKilled, you'd raise the
memory limit. Same discipline as Project 1, different lever.

---

## Checkpoint

- [ ] `kubectl top pods -n webapp` shows real CPU/memory per pod
- [ ] You identified the pods' QoS class as **Burstable** and can say why
- [ ] You can explain why `BestEffort` (no limits) is a bad default
- [ ] You saw a `/burn` pod throttled near its `250m` CPU limit

---

**Next:** [Step 4 — Autoscale with an HPA](./04-autoscaling-hpa.md)
