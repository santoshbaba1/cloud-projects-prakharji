# Troubleshooting — S3 + CloudFront Static Website

A reference for the errors you're most likely to hit during this project.
Format: **Error → Cause → Fix**.

---

## Error: `AccessDenied` when opening the CloudFront URL

**Symptom:** Visiting `https://dxxxx.cloudfront.net/` returns an XML `AccessDenied` page.

**Cause:** CloudFront can reach S3, but S3 is refusing the request. Almost always the
**bucket policy** is missing or wrong — the bucket doesn't yet trust your distribution.

**Fix:**
1. Go to **CloudFront → your distribution → Origins**, select the origin, and **Copy policy**.
2. Go to **S3 → your bucket → Permissions → Bucket policy → Edit** and paste it. Save.
3. Confirm the policy's `AWS:SourceArn` matches your distribution ARN
   (`arn:aws:cloudfront::ACCOUNT_ID:distribution/DISTRIBUTION_ID`).
4. Wait a moment and retry.

---

## Error: `AccessDenied` at the root `/` but a specific file works

**Symptom:** `https://dxxxx.cloudfront.net/index.html` works, but
`https://dxxxx.cloudfront.net/` (no file name) returns AccessDenied or an error.

**Cause:** The **Default root object** is not set, so CloudFront doesn't know which file
to serve for `/`.

**Fix:** **CloudFront → your distribution → Settings → Edit →** set **Default root object**
to `index.html`. Save and wait for redeploy.

> Note: the default root object only applies to the **root** (`/`). It does **not** apply
> to subfolders — `/blog/` will not automatically serve `/blog/index.html` (see Challenge 4).

---

## Error: I updated the file but still see the old version

**Symptom:** You re-uploaded `index.html` to S3, refreshed the browser, but the old
content is still showing.

**Cause:** CloudFront is serving the **cached** copy from the edge. It won't fetch the new
file from S3 until the cached copy's TTL expires (up to ~24 hours with `CachingOptimized`).

**Fix:** Create a cache invalidation:
**CloudFront → your distribution → Invalidations → Create invalidation →** path `/*`.
Then hard-refresh your browser (Ctrl/Cmd + Shift + R). See
[Step 4.4](steps/04-error-pages-and-caching.md).

---

## Error: Custom error page doesn't appear (raw S3 403 shows instead)

**Symptom:** Requesting a missing file shows a raw `AccessDenied` / 403 XML page rather
than your `error.html`.

**Cause:** Either no custom error response is configured, or only **404** is configured.
With a **private bucket + OAC**, S3 returns **403** (not 404) for a missing object, so you
must map the **403** code.

**Fix:** **CloudFront → your distribution → Error pages →** create a custom error response
for **403** with response page `/error.html`. (Map 404 too, to be safe.) See
[Step 4.2](steps/04-error-pages-and-caching.md).

---

## Error: Changes to the distribution aren't taking effect

**Symptom:** You changed a setting but the behavior is unchanged.

**Cause:** The distribution is still **Deploying**. Config changes propagate to all edge
locations and take **5–15 minutes**.

**Fix:** Wait until the distribution's status reads **Deployed** before testing. Then also
invalidate the cache (`/*`) if the change affects already-cached content.

---

## Error: I used the S3 *website* endpoint and OAC doesn't work

**Symptom:** Origin access control settings don't seem to apply, or you still get errors
even after the bucket policy is set.

**Cause:** The origin was set to the **S3 static website endpoint**
(`...s3-website-us-east-1.amazonaws.com`). OAC only works with the **S3 REST endpoint**
(`...s3.amazonaws.com`), which is what the dropdown gives you.

**Fix:** Edit the origin and pick the bucket from the **Origin domain dropdown** (do not
type the website endpoint). The website endpoint is an HTTP-only public endpoint and is a
different pattern entirely.

---

## Error: File downloads instead of displaying in the browser

**Symptom:** Instead of rendering the page, the browser downloads `index.html` as a file.

**Cause:** The object's **Content-Type** is wrong (e.g. `binary/octet-stream` instead of
`text/html`).

**Fix:** Re-upload setting the correct type:
```bash
aws s3 cp src/index.html "s3://$BUCKET/index.html" --content-type text/html
```
Then invalidate the cache so CloudFront serves the corrected object.

---

## Error: Bucket name already exists / can't create bucket

**Symptom:** `BucketAlreadyExists` or `BucketAlreadyOwnedByYou`.

**Cause:** S3 bucket names are **globally unique** across all AWS accounts.

**Fix:** Pick a more unique name, e.g. `static-site-yourname-2026-001`, and use it
consistently in all later steps.

---

## Still stuck?

- Confirm the distribution status is **Deployed**, not Deploying.
- Confirm the bucket policy `AWS:SourceArn` exactly matches the distribution ARN.
- Confirm both files are at the **root** of the bucket with Content-Type `text/html`.
- Try an incognito window or `curl -I` to rule out local browser caching.
