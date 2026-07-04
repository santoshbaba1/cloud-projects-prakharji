# Troubleshooting — Scheduled S3 Housekeeping

Error → Cause → Fix.

---

## KeyError: 'BUCKET' at function init

**Symptom:** The function fails immediately; logs show `KeyError: 'BUCKET'` before the handler
runs.

**Cause:** `BUCKET` is read with `os.environ["BUCKET"]` (no default) at module load. The env var
isn't set.

**Fix:** Set the `BUCKET` environment variable on the function (Step 3.2). This is intentional —
a housekeeper must never guess which bucket to clean.

---

## AccessDenied on ListBucket but GetObject works (or vice versa)

**Symptom:** `An error occurred (AccessDenied) when calling the ListObjectsV2 operation`, or the
list works but copies/deletes are denied.

**Cause:** The two S3 IAM ARN shapes are swapped. `s3:ListBucket` needs the **bucket** ARN
(`arn:aws:s3:::name`); `s3:GetObject/PutObject/DeleteObject` need the **object** ARN
(`arn:aws:s3:::name/*`).

**Fix:** Re-check the inline policy from Step 1.4 — bucket actions on the bucket ARN, object
actions on the `/*` ARN. They are *separate statements* for a reason.

---

## Nothing qualifies (count: 0) but objects exist

**Symptom:** Objects sit under `active/` yet the run reports `count: 0`.

**Causes & fixes:**

1. **Objects are newer than the cutoff.** With `RETENTION_DAYS=30`, freshly uploaded objects
   don't qualify. For the lab use `RETENTION_DAYS=0`.
2. **Wrong `PREFIX`.** The function only scans `PREFIX` (default `active/`). If your objects are
   at the bucket root or another prefix, set `PREFIX` to match (or `""` for the whole bucket).
3. **Wrong `BUCKET`.** Double-check the env var points at the bucket you seeded.

---

## NoSuchBucket / bucket name errors on create

**Symptom:** `create-bucket` fails, or `IllegalLocationConstraintException`.

**Causes & fixes:**

1. **Name already taken.** Bucket names are globally unique. Add a random suffix.
2. **Passing LocationConstraint in us-east-1.** Don't send
   `--create-bucket-configuration LocationConstraint=us-east-1` — us-east-1 rejects it. Omit the
   flag entirely for this region.

---

## Archived objects keep getting re-archived

**Symptom:** Each run moves objects deeper, e.g. `archive/archive/...`.

**Cause:** The `ARCHIVE_PREFIX` guard isn't matching — usually because `PREFIX` is set to `""`
(whole bucket) so the scan includes `archive/` itself.

**Fix:** Keep `PREFIX=active/` so the scan never sees `archive/`, or rely on the built-in guard
`if ACTION == "archive" and key.startswith(ARCHIVE_PREFIX): continue`. Don't set `PREFIX` to the
same value as (or a parent of) `ARCHIVE_PREFIX`.

---

## Deleted the wrong objects

**Symptom:** `ACTION=delete` removed objects you wanted to keep.

**Cause:** Ran `delete` without a dry-run, or with too-aggressive `RETENTION_DAYS`/`PREFIX`.

**Fix:** There's no undo unless **versioning** was enabled (Challenge 4). Going forward: always
`DRY_RUN=true` after any config change, and read the `keys` list before the real run. Consider
enabling versioning on important buckets so deletes are recoverable.

---

## update-function-configuration wiped my other env vars

**Symptom:** After changing one variable, `BUCKET` (or others) is suddenly missing.

**Cause:** `--environment` **replaces** the entire variable set.

**Fix:** Always pass the full `Variables={...}` map with every key, not just the one you're
changing.

---

## Task timed out after 60.00 seconds

**Cause:** A large bucket — thousands of copy+delete calls — exceeds the timeout.

**Fix:** Raise the timeout, process in smaller `PREFIX` batches, or use S3 **Batch Operations**
/ **Lifecycle rules** for very large jobs. See Challenge 5.

---

## General debugging checklist

1. `BUCKET`, `PREFIX`, `ACTION`, `RETENTION_DAYS`, `DRY_RUN` env vars all set correctly
2. IAM uses bucket-ARN for `ListBucket`, `/*`-ARN for object actions
3. `RETENTION_DAYS=0` for the lab so objects qualify
4. Rule has the invoke permission; `FailedInvocations = 0`
5. Function `Errors = 0`; read `/aws/lambda/s3-housekeeper` logs
