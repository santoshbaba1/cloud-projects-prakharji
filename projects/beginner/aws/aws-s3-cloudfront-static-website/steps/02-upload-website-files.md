# Step 2 — S3: Upload Your Website Files

Now you'll put the two HTML files from `src/` into your bucket. CloudFront will serve
these to visitors.

The files are:
- **`index.html`** — your home page. CloudFront will serve this when someone visits `/`.
- **`error.html`** — a custom 404/403 page. CloudFront will serve this when a file
  can't be found (configured in Step 4).

---

## 2.1 What You're Uploading

```
s3://static-site-<your-unique-name>/
├── index.html      Content-Type: text/html
└── error.html      Content-Type: text/html
```

> **Content-Type matters.** It tells the browser to *render* the file as a web page
> instead of *downloading* it. The Console and the `aws s3 cp` command both detect
> `.html` automatically and set `text/html` for you — but it's worth knowing why.

---

## 2.2 Console — Upload the Files

1. Open **S3** → click your bucket → you're on the **Objects** tab.
2. Click **Upload**.
3. Click **Add files** and select both files from this project's `src/` folder:
   - `index.html`
   - `error.html`
4. Expand **Properties** (optional) and confirm the **Content-Type** is detected as
   `text/html` for each file. Leave it as-is.
5. Leave **Permissions** and **Encryption** at their defaults (the bucket stays private).
6. Click **Upload**.
7. When it finishes, click **Close**. You should now see both files in the Objects list.

> Upload the files at the **root** of the bucket, not inside a folder. CloudFront's
> default root object setting (`index.html`) looks for the file at the root.

---

## 2.3 Console — Verify

1. In the Objects list you should see `index.html` and `error.html`.
2. Click `index.html` → note the **Object URL** at the top. If you open it in a browser
   right now, you'll get **Access Denied** — that's correct! The bucket is private and
   not reachable directly. CloudFront will be the only way in.

---

## 2.4 AWS CLI (Alternative)

```bash
# From the project root (where the src/ folder is)
# $BUCKET should still be set from Step 1

aws s3 cp src/index.html  "s3://$BUCKET/index.html"  --content-type text/html
aws s3 cp src/error.html  "s3://$BUCKET/error.html"  --content-type text/html

# List the bucket contents to confirm
aws s3 ls "s3://$BUCKET/"
```

Expected output:
```
2026-06-07 10:00:00       1234 error.html
2026-06-07 10:00:00       1567 index.html
```

---

## Checkpoint

- [ ] `index.html` and `error.html` are at the **root** of the bucket
- [ ] Both objects have Content-Type `text/html`
- [ ] Opening the object's S3 URL directly returns **Access Denied** (proof the bucket is private)

---

**Next:** [Step 3 — Create the CloudFront Distribution](./03-create-cloudfront.md)
