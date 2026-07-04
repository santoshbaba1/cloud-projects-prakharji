# Challenges — S3 + CloudFront Static Website

Completed the project? These challenges deepen your understanding of CloudFront, S3, and
how real static sites are deployed.

---

## Challenge 1 — Add a Second Page and Link to It

**Goal:** Add an `about.html` page and link to it from `index.html`.

**Steps:**
1. Create `src/about.html` with some content and a link back to `/`.
2. Add a link to `/about.html` in `index.html`.
3. Upload both files to S3.
4. Create a cache invalidation for `/*`.
5. Visit `https://dxxxx.cloudfront.net/about.html`.

**What you'll learn:** How multiple objects map to URL paths, and why you must invalidate
after every content change.

---

## Challenge 2 — Add a Custom Domain with Free HTTPS

**Goal:** Serve the site at `www.yourdomain.com` instead of the `cloudfront.net` URL.

**Steps:**
1. Request a public certificate in **AWS Certificate Manager (ACM)** — it must be in
   **us-east-1** for CloudFront to use it.
2. Validate the certificate via DNS (add the CNAME record ACM gives you).
3. In the distribution settings, add the **Alternate domain name (CNAME)** and select the
   ACM certificate.
4. In your DNS (Route 53 or your registrar), point the domain at the CloudFront domain with
   an alias / CNAME record.

**What you'll learn:** How CloudFront, ACM, and DNS work together to deliver free HTTPS on a
custom domain.

---

## Challenge 3 — Compare OAC vs a Public Bucket

**Goal:** Understand why the private-bucket + OAC pattern is preferred.

**Steps:**
1. Note your current setup: bucket is private, only CloudFront can read it.
2. Read the AWS docs on the legacy "S3 static website hosting" public-bucket approach.
3. Write down 3 concrete downsides of the public approach (no access control, HTTP-only
   endpoint, bypasses the CDN, etc.).

**What you'll learn:** The security and architecture trade-offs between origin access
patterns.

---

## Challenge 4 — Subfolder Index Documents

**Goal:** Make `/blog/` serve `/blog/index.html` automatically (the default root object
only covers the site root, not subfolders).

**Steps:**
1. Upload `index.html` into a `blog/` prefix in the bucket.
2. Observe that `https://dxxxx.cloudfront.net/blog/` does **not** automatically serve it.
3. Add a **CloudFront Function** (viewer-request) that appends `index.html` to URLs ending
   in `/`.
4. Attach the function to the default cache behavior and test.

**What you'll learn:** The limits of the default root object and how CloudFront Functions
rewrite requests at the edge.

---

## Challenge 5 — Enable Access Logging

**Goal:** Capture a log of every request CloudFront serves.

**Steps:**
1. Create a second S3 bucket for logs.
2. In the distribution settings, enable **Standard logging** and point it at the log bucket.
3. Generate some traffic, wait a few minutes, and inspect the log files.

**What you'll learn:** How to observe real traffic to your CDN and where the logs live.

---

## Challenge 6 — Restrict Access by Geography

**Goal:** Block or allow visitors based on their country.

**Steps:**
1. In the distribution, open **Geographic restrictions**.
2. Set an **allow list** (e.g., only your country) or a **block list**.
3. Test from a VPN in another country, or verify the setting in the console.

**What you'll learn:** CloudFront geo-restriction and how edge locations enforce it.

---

## Challenge 7 — Tune the Cache TTL and Observe Behavior

**Goal:** See how TTL affects how quickly updates appear without an invalidation.

**Steps:**
1. Create a custom **cache policy** with a short TTL (e.g., 60 seconds min/default/max).
2. Attach it to the default cache behavior.
3. Update `index.html`, re-upload, and wait ~60 seconds — the change should appear with no
   invalidation.
4. Compare to the `CachingOptimized` policy (24h default).

**What you'll learn:** The trade-off between cache TTL (cost/performance) and how fresh your
content is — and why short TTLs reduce the need for invalidations.
