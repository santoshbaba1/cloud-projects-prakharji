# Step 1 — S3: Create a Private Bucket for Your Website Files

**Amazon S3 (Simple Storage Service)** stores files ("objects") in containers called
**buckets**. Your two HTML files will live here. This bucket is the **origin** —
the place CloudFront fetches content from.

A common beginner approach is to turn on *S3 Static Website Hosting* and make the
bucket public. We will **not** do that. Instead we keep the bucket **fully private**
and let only CloudFront read it. This is the modern, secure pattern and it's what
AWS recommends.

> **Why keep it private?** A public bucket is reachable by anyone on the internet via
> its S3 URL, which bypasses CloudFront entirely (no caching, no HTTPS-by-default, no
> access control). Keeping it private means there is exactly **one** front door: your
> CloudFront distribution.

---

## 1.1 What You're Creating

```
Bucket name:           static-site-<your-unique-name>   (globally unique!)
Region:                us-east-1
Block Public Access:   ON  (all four settings checked)
Bucket Versioning:     Disabled (fine for this project)
```

> **Bucket names are globally unique across all of AWS.** If `static-site-demo` is
> taken, add something unique: `static-site-prakhar-2026`. Write your final name down —
> you'll use it in every later step.

---

## 1.2 Console — Create the Bucket

1. Open the [AWS Console](https://console.aws.amazon.com) and search for **S3**.
2. Click **Create bucket**.
3. Fill in the form:

   | Field | Value |
   |-------|-------|
   | AWS Region | **us-east-1 (N. Virginia)** |
   | Bucket name | `static-site-<your-unique-name>` |
   | Object Ownership | **ACLs disabled (recommended)** |
   | Block Public Access settings | **Block all public access** — leave the master checkbox **ON** |
   | Bucket Versioning | Disable |
   | Default encryption | Leave default (**SSE-S3**) |

4. Leave everything else at its default.
5. Click **Create bucket**.

> **Keep "Block all public access" ON.** This is intentional. CloudFront will still be
> able to read the bucket because in Step 3 we attach a **bucket policy** that grants
> read access specifically to your distribution. Blocking *public* access does not block
> *CloudFront* access — the two are separate mechanisms.

---

## 1.3 Console — Verify

1. From the S3 bucket list, click your bucket name.
2. Go to the **Permissions** tab.
3. Confirm **Block public access (bucket settings)** shows **On** for all four settings.
4. The bucket is empty — that's expected. You'll upload files in Step 2.

---

## 1.4 AWS CLI (Alternative)

```bash
# Set a unique bucket name once, reuse it in later steps
export BUCKET=static-site-<your-unique-name>

# Create the bucket in us-east-1
# (us-east-1 is special: do NOT pass --create-bucket-configuration for this region)
aws s3api create-bucket \
  --bucket "$BUCKET" \
  --region us-east-1

# Block all public access (this is ON by default for new buckets, but be explicit)
aws s3api put-public-access-block \
  --bucket "$BUCKET" \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Confirm the block settings
aws s3api get-public-access-block --bucket "$BUCKET"
```

---

## Checkpoint

- [ ] Bucket exists in **us-east-1** with a globally unique name
- [ ] **Block all public access** is **ON** (all four settings)
- [ ] The bucket is currently empty
- [ ] You have written down your exact bucket name for later steps

---

**Next:** [Step 2 — Upload Your Website Files](./02-upload-website-files.md)
