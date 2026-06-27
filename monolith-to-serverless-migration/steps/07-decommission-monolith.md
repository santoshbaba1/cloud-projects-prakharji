# Step 7 — Decommission the Monolith

The fig has taken over; the host tree can rot. In a real migration this is the **most
disciplined** step — retiring the old system too early loses data, too late wastes money and
keeps two systems alive. You verify nothing depends on the monolith, take a final data
snapshot, **stop** it (reversible) before you **terminate** it (not), and only then declare
the migration done.

---

## 7.1 Prove nothing still uses it

1. **Traffic:** In EC2 → the instance → **Monitoring**, confirm `NetworkIn` has flatlined
   since the cutover. If you used the security group rule for port 5000, check there are no
   recent connections.
2. **Front door:** Confirm `bookstore-api` has **no** route still pointing at the monolith
   (no `HTTP_PROXY` catch-all left over from Step 6).
3. **Data:** Confirm `Orders` in DynamoDB contains every order the monolith had (compare
   counts with the SQLite `orders` table). Re-run the Step 2 exporter once more — it's
   idempotent — to catch any orders placed on the monolith *after* your first export.

```bash
# final reconciliation: counts should match
sqlite3 bookstore.db "SELECT COUNT(*) FROM orders;"     # on the EC2 box
aws dynamodb scan --table-name Orders --select COUNT --query Count
```

> **Why reconcile twice?** Between your first export (Step 2) and cutover (Step 6), the
> monolith may have taken more orders. The final idempotent re-export guarantees **zero data
> loss** — the cardinal rule of any migration.

---

## 7.2 Take a final snapshot (safety net)

Before you delete anything, keep a copy of the monolith's data in case you must roll back:

```bash
# on the EC2 box — copy the SQLite file somewhere durable
aws s3 cp bookstore.db s3://<your-bucket>/monolith-final/bookstore.db
```

Optionally create an **AMI** of the instance (EC2 → Actions → Image and templates → Create
image) so you could relaunch the exact monolith if the migration is reverted.

---

## 7.3 Stop first (reversible), then terminate

1. **Stop** the instance: EC2 → Instance state → **Stop instance**. A stopped instance costs
   only EBS storage and can be restarted — your reversible rollback point. Leave it stopped
   for a cool-down period (a day in real life; minutes in the lab) while you watch the
   serverless side in production.
2. Once you're confident, **Terminate**: EC2 → Instance state → **Terminate instance**.

```bash
# CLI: stop, observe, then terminate
aws ec2 stop-instances  --instance-ids <id>
aws ec2 terminate-instances --instance-ids <id>
```

> **Stop ≠ Terminate.** Stop is pause (keep the disk, restart anytime). Terminate is delete
> (instance and, by default, its root volume are gone). The two-phase retire — stop, observe,
> terminate — is how you decommission without burning the bridge prematurely.

---

## 7.4 You've migrated

The bookstore now runs entirely on **API Gateway + Lambda + DynamoDB**. No servers to patch,
each domain scales on its own, and the bill is ~$0 when nobody's shopping. That's the
serverless payoff the monolith couldn't give you — earned through a controlled, route-by-route
**Refactor**, not a big-bang rewrite.

---

## Checkpoint

- [ ] Monolith network traffic has flatlined; no front-door route targets it
- [ ] `Orders` count in DynamoDB matches the SQLite `orders` count (final reconcile)
- [ ] A final copy of `bookstore.db` is safe in S3 (and/or an AMI exists)
- [ ] Instance **stopped**, observed, then **terminated**
- [ ] The API URL serves the whole bookstore with no EC2 in the path

---

**Next:** [Step 8 — Cleanup](./08-cleanup.md)
