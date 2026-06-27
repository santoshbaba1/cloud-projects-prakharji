# Step 7 — Decommission the Monolith

The microservices now serve the whole shop with independent scaling, rolling deploys, and
self-healing. The monolith is redundant. Retire it the disciplined way: confirm nothing depends
on it, scale it to zero first (reversible), observe, then delete.

---

## 7.1 Prove nothing uses it

1. **Traffic:** confirm users hit the **frontend ELB**, not the monolith. Check
   `kubectl -n shop logs -l app=frontend` shows live requests; check the monolith (ECS task
   metrics or local container logs) shows none.
2. **Front door:** confirm your storefront DNS / the URL you hand out points at the EKS
   `frontend` ELB only.
3. **Parity:** re-run the Step 5 parity table one last time against the ELB.

> Since each microservice owns its own (in-memory, for this lab) data, there's no shared
> database to reconcile — but in a real system you'd confirm the services' datastores hold
> everything the monolith's DB did before retiring it. That data reconciliation is the
> non-negotiable gate (see [Project 1, Step 7](../../monolith-to-serverless-migration/steps/07-decommission-monolith.md)).

---

## 7.2 Scale to zero first (reversible)

If the monolith runs as an ECS service, set its desired count to **0** rather than deleting it.
It stops serving and (mostly) stops billing, but you can scale it back to 1 instantly if the
EKS path surprises you.

```bash
# ECS monolith service (if you ran the optional Step 1 ECS deploy)
aws ecs update-service --cluster <cluster> --service shop-monolith --desired-count 0
```

If it was just the local container from Step 1, simply stop it (`docker stop`).

---

## 7.3 Observe, then delete

Watch the EKS frontend handle 100% of traffic for a cool-down window. When you're confident:

- **ECS:** delete the monolith service and task definition; delete its ECR repo if unused.
- **Local:** nothing to delete beyond the stopped container.

The shop now runs entirely as three Kubernetes microservices. You executed a **Refactor**
migration with a controlled, parity-gated cutover — no big-bang.

---

## Checkpoint

- [ ] Frontend ELB serves all traffic; monolith serves none
- [ ] (If applicable) service datastores hold everything the monolith's did
- [ ] Monolith scaled to zero, observed, then deleted
- [ ] The shop is fully on EKS microservices

---

**Next:** [Step 8 — Cleanup (delete the cluster!)](./08-cleanup.md)
