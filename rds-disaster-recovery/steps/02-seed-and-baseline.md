# Step 2 — Seed Data and Record a Baseline

Recovery only means something if you can prove the data came back. You'll load known rows and
record an **RPO marker** — a timestamp you can later say "I want to recover to just after this."

---

## 2.1 Install the Client and Seed

```bash
pip install pymysql
cd /path/to/rds-disaster-recovery

python src/db_seed.py --host <ENDPOINT> --user admin --password '<YOUR_PW>' --rows 5
```

Output:

```
Seeded 5 row(s). Table now has 5 order(s).
RPO MARKER (UTC): 2026-06-19T14:03:11Z  <-- restore to a time after this
```

**Write down that marker.** In Step 3 you'll restore to a moment just after it.

> Tip: set `DB_HOST`, `DB_USER`, `DB_PASSWORD` as env vars so you don't retype them:
> ```bash
> export DB_HOST=<ENDPOINT> DB_USER=admin DB_PASSWORD='<YOUR_PW>'
> python src/db_seed.py --rows 5
> ```

---

## 2.2 Verify the Baseline

```bash
python src/db_verify.py --host <ENDPOINT> --user admin --password '<YOUR_PW>'
```

```
Host    : rds-dr-demo.xxxx.us-east-1.rds.amazonaws.com
Orders  : 5
Newest  : (5, 'customer-5', Decimal('24.00'), datetime.datetime(2026, 6, 19, 14, 3, 11))
```

This `db_verify.py` is your **proof tool** — you'll run it against every restored instance and
promoted replica in the next steps and expect to see these same 5 orders.

---

## 2.3 (Optional) Add More Rows to Mark Time

Run the seeder again to add 5 more rows a few minutes later (10 total). The two batches have
different `created_at` times — useful in Step 3 when you PITR to *between* them and watch the
second batch disappear.

```bash
python src/db_seed.py --rows 5     # now 10 orders total
```

---

## Checkpoint

- [ ] `db_seed.py` reported a row count and an **RPO MARKER** timestamp (saved)
- [ ] `db_verify.py` shows the expected order count and newest row
- [ ] (Optional) You added a second batch so you have two distinct `created_at` times

---

**Next:** [Step 3 — Automated Backups and Point-in-Time Recovery](./03-automated-backups-and-pitr.md)
