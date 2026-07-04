# Step 2 — Create the Bucket and Seed Objects

Create the bucket the housekeeper will manage, then upload a few sample objects under
`active/` so there's something to clean up.

---

## 2.1 Create the Bucket

Use the **exact name** you referenced in the Step 1 policy.

**Console:** S3 → **Create bucket** → Name = `YOUR_BUCKET_NAME`, Region **us-east-1**, leave
**Block all public access ON** (defaults). Create.

**CLI:**

```bash
BUCKET=YOUR_BUCKET_NAME
aws s3api create-bucket --bucket "$BUCKET" --region us-east-1
```

> us-east-1 is special: do **not** pass `--create-bucket-configuration` / `LocationConstraint`
> for this region or the call errors. Every other region requires it.

---

## 2.2 Seed Sample Objects

The script uploads four objects under `active/`:

```bash
pip install boto3   # if needed
python src/seed_objects.py YOUR_BUCKET_NAME
```

Expected:

```
uploaded s3://YOUR_BUCKET_NAME/active/report-jan.txt
uploaded s3://YOUR_BUCKET_NAME/active/report-feb.txt
uploaded s3://YOUR_BUCKET_NAME/active/logs/app.log
uploaded s3://YOUR_BUCKET_NAME/active/notes.md

Done. 4 objects under active/.
```

Verify:

```bash
aws s3 ls s3://YOUR_BUCKET_NAME/active/ --recursive
```

---

## 2.3 About Object Age

The housekeeper acts on objects **older than `RETENTION_DAYS`**, measured from each object's
`LastModified` time. You just uploaded these objects, so they're brand new — with a normal
`RETENTION_DAYS=30` they would *not* qualify.

> **For the lab, you'll set `RETENTION_DAYS=0` in Step 3** so freshly-uploaded objects are
> immediately eligible and you can watch the housekeeper work without waiting weeks. In
> production you'd use a real window like 30 or 90. You can't backdate `LastModified`, which is
> why we use `0` to demonstrate.

---

## Checkpoint

- [ ] Bucket exists in **us-east-1** with the name used in the Step 1 policy
- [ ] Four objects exist under `active/` (including the nested `active/logs/app.log`)
- [ ] You understand why the lab uses `RETENTION_DAYS=0`

---

**Next:** [Step 3 — Create the Housekeeper Function](./03-create-function.md)
