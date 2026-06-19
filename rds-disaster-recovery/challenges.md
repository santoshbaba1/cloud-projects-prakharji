# Challenges — RDS Disaster Recovery

Deepen the DR practice. These build on what you provisioned.

---

## Challenge 1 — Write Down Your RPO and RTO Numbers

For each of the four methods you ran (PITR, manual snapshot, cross-region copy, replica+promote),
**measure** the real numbers in your account: how far back could you recover (RPO) and how long
did recovery take wall-clock (RTO)? Put them in a table. Then pick which method you'd use for: a
dropped table, a corrupted instance, a full regional outage. Justify each.

---

## Challenge 2 — Hide the Endpoint Behind DNS

Every restore changed the endpoint, breaking the "where does my app point?" problem. Put a
**Route 53 CNAME** (e.g. `db.internal.example.com`) in front of the primary. Practice failover by
**repointing the CNAME** to the promoted replica. Discuss TTL: a 300s TTL means up to 5 minutes of
stale resolution after you flip — how does that factor into RTO?

---

## Challenge 3 — Multi-AZ vs Read Replica

Enable **Multi-AZ** on the primary (modify the instance) and trigger a failover
(`reboot-db-instance --force-failover`). Note that Multi-AZ failover keeps the **same endpoint**
and takes ~60–120s, but is **same-region** (it's an HA feature, not DR). Contrast it with the
cross-region replica from Step 6: same-region HA vs cross-region DR — you usually want both.

---

## Challenge 4 — Automate Backups with AWS Backup

Replace the manual snapshot + manual cross-region copy with an **AWS Backup** plan: a backup rule
that snapshots `rds-dr-demo` on a schedule and **copies each backup to us-west-2** automatically,
into a DR backup vault. This is how real teams keep DR snapshots fresh without a human. Compare it
to the [Compute Rightsizing](../aws-compute-rightsizing/README.md) Lambda approach — managed
service vs your own code.

---

## Challenge 5 — Write a Failback Runbook

Promotion is one-way, so after a DR failover you have a new primary in us-west-2 and a stale (or
recovered) us-east-1. Write the **failback** procedure: how do you get production back to
us-east-1 without losing the writes that happened in us-west-2 during the outage? (Hint: snapshot
the new primary, restore in us-east-1, re-establish replication the other direction, cut over in a
maintenance window.) No code required — the runbook *is* the deliverable.

---

## Challenge 6 — Encrypt Everything, End to End

Recreate the primary with **storage encryption** using a customer-managed **KMS key**. Now redo
the cross-region snapshot copy and observe that you **must** supply a destination-region KMS key
(`--kms-key-id`). Document the key-management implications of multi-region encrypted DR: you need
a key in *every* region you might recover into.

---

## Challenge 7 — Restore-Test on a Schedule

A backup you've never restored is a hope, not a plan. Design a periodic **restore test**: a
scheduled job (EventBridge + Lambda, reusing the
[scheduling pattern](../lambda-eventbridge-scheduled/README.md)) that restores the latest snapshot
to a throwaway instance, runs `db_verify.py`-style checks, reports pass/fail to SNS, then deletes
the test instance. This proves your backups are actually recoverable — and tears itself down so it
doesn't bill.
