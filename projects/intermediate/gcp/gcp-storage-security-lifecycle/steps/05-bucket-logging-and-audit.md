# Step 5 — Bucket Logging & Audit

Everything so far controls **who can do what**. This step is about knowing **who actually did what** —
a public bucket and a CMEK-encrypted bucket both need a trail. Cloud Storage's built-in usage logs are
the lightweight option; **Cloud Audit Logs** is the heavier, off-by-default option for individual
data-access events. You'll set up the first and understand when you'd reach for the second.

---

## 5.1 Two Different Kinds of Logs

| Concept | What it means |
|---------|---------------|
| **Bucket usage logs** | Periodic CSV log **objects** written into a separate bucket, summarizing storage and requests for a source bucket |
| **Cloud Audit Logs — Admin Activity** | Always-on, free, records configuration changes (creating a bucket, changing IAM, setting a lifecycle rule) |
| **Cloud Audit Logs — Data Access** | **Off by default** for GCS; records individual object reads/writes when enabled — high volume, has a per-GB ingestion cost in Cloud Logging |
| **Why usage logs still matter** | They're the cheap, always-simple option for "which buckets are getting hit and how much," without turning on the more expensive per-object Data Access logs |

---

## 5.2 What You'll Create

| Object | Value |
|--------|-------|
| Log bucket | `meridian-access-logs-<PROJECT_ID>` |
| Logging source | `meridian-reports-<PROJECT_ID>` and `meridian-product-photos-<PROJECT_ID>` |
| Log object prefix | `reports-access` and `photos-access` respectively |

---

## 5.3 Console — Create the Log Bucket

1. **☰ → Cloud Storage → Buckets → Create.**

   | Field | Value |
   |-------|-------|
   | Name | `meridian-access-logs-<PROJECT_ID>` |
   | Location | Region → `us-east1` |
   | Access control | Uniform |
   | Storage class | Standard |

2. **Create.**

The log bucket needs the **Cloud Storage Analytics/Log service account** to be able to write into it
— Google grants this automatically when you enable usage logs through the Console or `storage.googleapis.com`
project-level configuration in the next step.

---

## 5.4 Console — Enable Usage Logs on the Reports Bucket

1. Open `meridian-reports-<PROJECT_ID>` → **Configuration** tab → **Usage logs** (under **Cloud
   Storage logs** / **Data protection**, naming varies slightly by Console version) → **Edit**.
2. Set:

   | Field | Value |
   |-------|-------|
   | Log bucket | `meridian-access-logs-<PROJECT_ID>` |
   | Log object prefix | `reports-access` |

3. **Save.** Repeat for `meridian-product-photos-<PROJECT_ID>` with prefix `photos-access`.

---

## 5.5 gcloud CLI (Alternative)

```bash
PROJECT_ID=$(gcloud config get-value project)

# 1. Create the log bucket
gcloud storage buckets create "gs://meridian-access-logs-$PROJECT_ID" \
  --location=us-east1 --uniform-bucket-level-access

# 2. Point usage logs from the reports bucket at it
gcloud storage buckets update "gs://meridian-reports-$PROJECT_ID" \
  --log-bucket="meridian-access-logs-$PROJECT_ID" \
  --log-object-prefix=reports-access

# 3. Same for the product-photos bucket
gcloud storage buckets update "gs://meridian-product-photos-$PROJECT_ID" \
  --log-bucket="meridian-access-logs-$PROJECT_ID" \
  --log-object-prefix=photos-access
```

Verify the configuration landed:

```bash
gcloud storage buckets describe "gs://meridian-reports-$PROJECT_ID" \
  --format='value(logging_config)'
```

---

## 5.6 Inspect a Sample Log Line

Usage logs are written **once a day**, as CSV objects named like
`reports-access_usage_<date>_<hash>_v0`, so you won't see one appear immediately in this lab — but the
format is worth knowing in advance. A row looks roughly like:

```
"reports-access","meridian-reports-my-project-123","2026-07-11T09:00:00Z","2026-07-11T09:00:01Z",
"GET","200","1024","object","reports/2026/q1-report.txt","user@example.com","203.0.113.4",...
```

Key columns: **bucket**, **time**, **method** (GET/PUT/DELETE), **status code**, **bytes served**,
**object name**, **caller** (when available), and **source IP**. You can query these with `bq load`
into BigQuery for real analysis once volume grows — that's the standard next step in production, and
mirrors AWS S3 server access logs conceptually (bucket → per-request log lines → analyzed downstream).

---

## 5.7 When You'd Reach for Cloud Audit Logs Data Access Instead

Usage logs answer "how much traffic, from where, at what daily granularity." They don't give you a
real-time, per-request audit trail suitable for a security investigation. **Cloud Audit Logs — Data
Access** does, but:

- It's **disabled by default** for Cloud Storage specifically because of volume and cost — every
  single object read/write becomes a log entry in Cloud Logging, and Cloud Logging bills per GB
  ingested past its free allotment.
- You enable it per-service, per-project, via an **IAM Audit Config** (`gcloud projects
  get-iam-policy` / `set-iam-policy` with an `auditConfigs` block, or **IAM & Admin → Audit Logs** in
  the Console) — not a bucket setting.
- **Admin Activity** audit logs (bucket created, IAM changed, lifecycle rule updated) are **always on
  and free**, regardless of Data Access settings — you already have an audit trail for every
  configuration change made in this project, including everything from Steps 1–4.

For this lab, usage logs are enough. In production, Data Access logs are the tool you'd turn on
specifically for the reports bucket if it ever needs to satisfy a compliance requirement around
"prove exactly who read this file and when."

---

## Checkpoint

- [ ] `meridian-access-logs-<PROJECT_ID>` exists and is empty of anything except future log objects
- [ ] `meridian-reports-<PROJECT_ID>` and `meridian-product-photos-<PROJECT_ID>` both show a
      `logging_config` pointing at the log bucket with distinct prefixes
- [ ] You can explain the difference between usage logs, Admin Activity audit logs, and Data Access
      audit logs — and which of the three is off by default

---

**Next:** [Step 6 — Cleanup](./06-cleanup.md)
