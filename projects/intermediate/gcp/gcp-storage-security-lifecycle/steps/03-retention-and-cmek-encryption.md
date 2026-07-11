# Step 3 — Retention Policies & CMEK Encryption

Two unrelated protections live in this step because they're both about *data you can't afford to lose
or leak*: a **retention policy** stops anyone (including you) from deleting an object before a minimum
age, and **CMEK** puts a key you control — not just Google's default key — between your data and disk.
The retention demo uses a **throwaway bucket you'll delete at the end of this step**; the CMEK setup
applies permanently to the reports bucket from Step 2.

---

## 3.1 Retention Policies, Conceptually

| Concept | What it means |
|---------|---------------|
| **Retention policy** | A minimum age (e.g. 30 days) an object must reach before it can be deleted or overwritten — enforced by GCP, not your application |
| **Unlocked retention policy** | Can still be shortened or removed by someone with `storage.buckets.update` — safe to experiment with |
| **Bucket lock (`--locked`)** | Makes the retention policy **permanent** — it can only ever be *increased*, never shortened or removed, not even by the project owner, not even by Google support |
| **Why this exists** | Regulatory holds (financial records, legal discovery) need a guarantee that survives an angry admin or a compromised credential — "irreversible" is the point, not a bug |

> ⚠️ **This step's retention policy is deliberately left unlocked, on a bucket you'll delete
> immediately after.** Never run `gcloud storage buckets update --locked` against a bucket you might
> need to delete or a retention period you might need to shorten — once locked, there is **no undo**,
> not even by contacting Google support. Locking is a one-way door meant for actual compliance
> requirements, not a lab exercise.

---

## 3.2 Console — Retention Policy Demo (Throwaway Bucket)

1. **☰ → Cloud Storage → Buckets → Create.**

   | Field | Value |
   |-------|-------|
   | Name | `meridian-retention-demo-<PROJECT_ID>` |
   | Location | Region → `us-east1` |
   | Access control | Uniform |

2. Open the bucket → **Protection** tab → **Retention policy** → **Set retention policy**.

   | Field | Value |
   |-------|-------|
   | Retention period | `1` day (short, so you can observe the block without waiting long) |
   | Lock policy | **Leave unchecked** |

3. Upload any small test file to the bucket (drag-and-drop in the Console, or `gcloud storage cp`).
4. Try to delete that object immediately. The Console/CLI will refuse — that's the policy working.

---

## 3.3 gcloud CLI (Alternative)

```bash
PROJECT_ID=$(gcloud config get-value project)

# 1. Create the throwaway bucket
gcloud storage buckets create "gs://meridian-retention-demo-$PROJECT_ID" \
  --location=us-east1 --uniform-bucket-level-access

# 2. Set an UNLOCKED retention policy (1 day, just to demonstrate the block)
gcloud storage buckets update "gs://meridian-retention-demo-$PROJECT_ID" \
  --retention-period=1d

# 3. Upload a test object and try to delete it — this should fail
echo "retention test" > /tmp/retention-test.txt
gcloud storage cp /tmp/retention-test.txt "gs://meridian-retention-demo-$PROJECT_ID/"
gcloud storage rm "gs://meridian-retention-demo-$PROJECT_ID/retention-test.txt"
# Expected: an error mentioning the object is retained until its retention period expires
```

Confirm the policy itself, and that it's still unlocked:

```bash
gcloud storage buckets describe "gs://meridian-retention-demo-$PROJECT_ID" \
  --format='value(retention_policy)'
# "locked: false" confirms you can still remove this policy — do so before deleting the bucket in Step 6
```

This bucket and its retention policy get cleaned up in [Step 6](./06-cleanup.md) — the delete order
matters there specifically because of this policy, so read that step's retention note before you skip
ahead.

---

## 3.4 CMEK Encryption, Conceptually

| Concept | What it means |
|---------|---------------|
| **Google-managed encryption** | The default — Google encrypts every object at rest, you never see or manage the key |
| **CMEK** | You create and own the key in **Cloud KMS**; GCS calls out to KMS to encrypt/decrypt on your behalf |
| **Keyring / key** | A keyring is a namespace for keys, pinned to a location; a key lives inside it and can have multiple versions |
| **GCS service agent** | A Google-managed service identity (`service-<PROJECT_NUMBER>@gs-project-accounts.iam.gserviceaccount.com`), one per project, that Cloud Storage itself uses to call other Google APIs |
| **Why the service agent needs a grant** | GCS doesn't use *your* credentials to talk to KMS — it uses its own service agent, so that agent needs `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the key before any bucket can use it as CMEK |

---

## 3.5 What You'll Create

| Object | Value |
|--------|-------|
| Keyring | `meridian-keyring` |
| Key | `meridian-storage-key` |
| Location | `us-east1` (must match the bucket's region) |
| Grant | GCS service agent → `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the key |
| Applied to | `meridian-reports-<PROJECT_ID>` (the bucket from Step 2), as its **default encryption key** |

---

## 3.6 Console — Create the Keyring and Key

1. **☰ → Security → Key Management → Create Key Ring.**

   | Field | Value |
   |-------|-------|
   | Key ring name | `meridian-keyring` |
   | Location type | Region → `us-east1` |

2. Inside the keyring, **Create Key**:

   | Field | Value |
   |-------|-------|
   | Key name | `meridian-storage-key` |
   | Protection level | Software |
   | Purpose | Symmetric encrypt/decrypt |

---

## 3.7 gcloud CLI (Alternative)

```bash
# Enable the KMS API if you haven't already
gcloud services enable cloudkms.googleapis.com

# 1. Create the keyring
gcloud kms keyrings create meridian-keyring --location=us-east1

# 2. Create the key inside it
gcloud kms keys create meridian-storage-key \
  --keyring=meridian-keyring --location=us-east1 \
  --purpose=encryption
```

---

## 3.8 Grant the GCS Service Agent Access to the Key

```bash
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
GCS_SA="service-${PROJECT_NUMBER}@gs-project-accounts.iam.gserviceaccount.com"

gcloud kms keys add-iam-policy-binding meridian-storage-key \
  --keyring=meridian-keyring --location=us-east1 \
  --member="serviceAccount:${GCS_SA}" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"
```

> The GCS service agent is created lazily — if this fails with "service account does not exist," first
> perform any operation on a bucket (e.g. list objects) to force GCS to provision it, then retry.

### Console (Alternative)

1. **☰ → Security → Key Management → `meridian-keyring` → `meridian-storage-key` → Permissions**.
2. **Grant Access** → principal `service-<PROJECT_NUMBER>@gs-project-accounts.iam.gserviceaccount.com`
   → role **Cloud KMS CryptoKey Encrypter/Decrypter**.

---

## 3.9 Set the Key as the Bucket's Default Encryption

```bash
gcloud storage buckets update "gs://meridian-reports-$PROJECT_ID" \
  --default-encryption-key="projects/$PROJECT_ID/locations/us-east1/keyRings/meridian-keyring/cryptoKeys/meridian-storage-key"
```

### Console (Alternative)

1. Open `meridian-reports-<PROJECT_ID>` → **Configuration** tab → **Encryption** → **Edit**.
2. Select **Customer-managed key** → `meridian-storage-key` → **Save**.

---

## 3.10 Upload and Verify

```bash
echo "Q1 2026 report" > /tmp/q1-report.txt
gcloud storage cp /tmp/q1-report.txt "gs://meridian-reports-$PROJECT_ID/reports/2026/q1-report.txt"

gcloud storage objects describe "gs://meridian-reports-$PROJECT_ID/reports/2026/q1-report.txt" \
  --format='value(kmsKeyName)'
```

Expected: the full resource name of `meridian-storage-key`, ending in `/cryptoKeyVersions/1`. Any
object uploaded to this bucket from now on is encrypted with your key by default — no per-upload flag
needed.

---

## 3.11 Why This Matters

- **CMEK is about control, not strength.** Google-managed encryption is just as strong
  cryptographically — CMEK's value is that *you* hold the ability to revoke access to the key (and
  therefore the data) independently of GCS itself, which some compliance regimes require.
- **The service-agent grant is the step everyone forgets.** It's not your identity encrypting the
  data — it's GCS's own service agent, and if that grant is missing every write to the bucket fails
  with a permission error that has nothing to do with *your* IAM permissions. See
  [troubleshooting.md](../troubleshooting.md) for the exact symptom.
- **Retention and CMEK compose.** In production you might combine a locked retention policy *and*
  CMEK on the same bucket — this step deliberately keeps them on separate buckets so a mistake in one
  demo can't strand the other.

---

## Checkpoint

- [ ] `meridian-retention-demo-<PROJECT_ID>` demonstrated a delete being blocked by an **unlocked**
      retention policy — and you know why you'd never run `--locked` in a lab
- [ ] `meridian-keyring` and `meridian-storage-key` exist in `us-east1`
- [ ] The GCS service agent has `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the key
- [ ] `meridian-reports-<PROJECT_ID>` shows the key as its default encryption key
- [ ] A freshly uploaded object's `kmsKeyName` matches `meridian-storage-key`

---

**Next:** [Step 4 — Signed URLs & Static Website](./04-signed-urls-and-static-website.md)
