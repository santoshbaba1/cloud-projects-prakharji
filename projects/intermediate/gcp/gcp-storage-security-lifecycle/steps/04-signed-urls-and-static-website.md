# Step 4 — Signed URLs & Static Website

Meridian needs two very different kinds of public-ish access: a customer should be able to download
*their own* receipt without a Google account, and *anyone* should be able to browse product photos.
The first is sensitive and must stay private-by-default with a narrow, expiring exception. The second
is genuinely public and can just be a public bucket. Conflating the two — making a receipts bucket
public "for convenience," or generating a permanent link for a product photo — is exactly the kind of
mistake this step is designed to prevent.

---

## 4.1 Signed URLs, Conceptually

| Concept | What it means |
|---------|---------------|
| **Signed URL** | A URL with a cryptographic signature and expiry baked into the query string; anyone holding the URL can access the object until it expires, no Google auth required |
| **Keyed signing** | Historically done with a downloaded service-account **JSON key file** — the private key signs the URL locally |
| **Keyless signing** | The URL is signed via a remote **`signBlob`** call using short-lived **impersonation** — no private key ever touches disk |
| **Why keyless wins** | A downloaded JSON key is a long-lived secret that can leak (committed to git, left on a laptop) and has no built-in expiry; impersonation credentials are short-lived and tied to *your* authenticated session |

To sign a URL keylessly, the **caller** (you, via `gcloud`) needs `roles/iam.serviceAccountTokenCreator`
on the service account being impersonated, and that service account needs
`iam.serviceAccounts.signBlob` permission on itself (bundled into `roles/iam.serviceAccountTokenCreator`
when granted on the account's own resource, which is exactly the setup below).

---

## 4.2 What You'll Create

| Object | Value |
|--------|-------|
| Signer identity | `doc-portal-sa` (from Project 1) — you'll grant yourself Token Creator on it |
| Signed object | `gs://meridian-reports-<PROJECT_ID>/reports/2026/q1-report.txt` (from Step 3) |
| Expiry | 15 minutes |
| Public bucket | `meridian-product-photos-<PROJECT_ID>` |
| Public grant | `allUsers` → `roles/storage.objectViewer` |

---

## 4.3 Console — Grant Yourself Token Creator on `doc-portal-sa`

1. **☰ → IAM & Admin → Service Accounts → `doc-portal-sa`**.
2. **Permissions** tab → **Grant Access**.
3. Principal: your own user email. Role: **Service Account Token Creator**.
4. **Save.**

---

## 4.4 gcloud CLI (Alternative)

```bash
PROJECT_ID=$(gcloud config get-value project)
SA_EMAIL="doc-portal-sa@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --member="user:YOUR_EMAIL@example.com" \
  --role="roles/iam.serviceAccountTokenCreator"
```

This grants Token Creator **on the service account itself**, not on the project — you're allowing
yourself to impersonate exactly this one identity, nothing broader.

---

## 4.5 Generate a Signed URL, Keylessly

```bash
gcloud storage sign-url \
  "gs://meridian-reports-$PROJECT_ID/reports/2026/q1-report.txt" \
  --impersonate-service-account="$SA_EMAIL" \
  --duration=15m
```

The output is a full HTTPS URL with `X-Goog-Signature`, `X-Goog-Expires`, and related query
parameters. Paste it into a browser (or `curl` it) — it works without you being logged into any Google
account in that browser. Wait past the 15-minute window and try again: the same URL now returns
`403 SignatureDoesNotMatch` / expired-token errors, proving the expiry is enforced server-side, not
just cosmetic.

> **Contrast with a JSON key.** The old approach — `gcloud iam service-accounts keys create` to
> download a private key, then sign locally — works too, but that key file has **no expiry** and grants
> everything the service account can do, forever, to whoever holds the file. Keyless signing gives you
> the same URL with none of that standing risk.

---

## 4.6 Static Website Hosting, Conceptually

| Concept | What it means |
|---------|---------------|
| **Static website bucket** | A public bucket configured with a `mainPageSuffix` (e.g. `index.html`) and `notFoundPage` (404 page), served directly over `storage.googleapis.com` or a custom domain |
| **`allUsers`** | The special IAM member meaning literally anyone on the internet, authenticated or not |
| **Public access prevention** | An org-policy / bucket setting that can **block** `allUsers` grants even if you try to add one — a safety net against accidental public buckets |

---

## 4.7 Console — Create the Public Product-Photos Bucket

1. **☰ → Cloud Storage → Buckets → Create.**

   | Field | Value |
   |-------|-------|
   | Name | `meridian-product-photos-<PROJECT_ID>` |
   | Location | Region → `us-east1` |
   | Access control | Uniform |
   | Public access prevention | **Off** (this bucket is meant to be public) |

2. Upload a sample `index.html` and a `404.html` (any minimal HTML — this is a lab, not a design
   review) to the bucket root.
3. Open the bucket → **Configuration** tab → **Website configuration** → **Edit**:

   | Field | Value |
   |-------|-------|
   | Main page | `index.html` |
   | 404 page | `404.html` |

4. **Permissions** tab → **Grant Access** → Principal `allUsers` → Role **Storage Object Viewer** →
   **Save** → confirm the "Public to internet" warning.

---

## 4.8 gcloud CLI (Alternative)

```bash
# 1. Create the bucket with public access prevention explicitly off
gcloud storage buckets create "gs://meridian-product-photos-$PROJECT_ID" \
  --location=us-east1 \
  --uniform-bucket-level-access \
  --public-access-prevention=inherited

# 2. Upload sample pages
echo "<h1>Meridian Retail — Product Photos</h1>" > /tmp/index.html
echo "<h1>404 — Not Found</h1>" > /tmp/404.html
gcloud storage cp /tmp/index.html /tmp/404.html "gs://meridian-product-photos-$PROJECT_ID/"

# 3. Configure the website
gcloud storage buckets update "gs://meridian-product-photos-$PROJECT_ID" \
  --web-main-page-suffix=index.html \
  --web-error-page=404.html

# 4. Make it public
gcloud storage buckets add-iam-policy-binding "gs://meridian-product-photos-$PROJECT_ID" \
  --member=allUsers --role=roles/storage.objectViewer
```

Verify:

```bash
curl -sI "https://storage.googleapis.com/meridian-product-photos-$PROJECT_ID/index.html" | head -1
# Expected: HTTP/1.1 200 OK
```

If this returns `403`, see [troubleshooting.md](../troubleshooting.md) — it's almost always a blocked
`allUsers` grant, either from public access prevention or an org policy.

---

## 4.9 Public Bucket vs. Signed URL — Same Storage Service, Opposite Postures

| | Product photos | Customer receipt |
|---|---|---|
| Sensitivity | None — marketing content, meant to be seen by everyone | Personal financial data, one specific customer |
| Access model | Permanently public (`allUsers`) | Private by default, one narrow time-boxed exception |
| Right choice | **Public bucket** | **Signed URL** |
| Wrong choice | Signed URL (pointless overhead for public content) | Public bucket or a permanent link (a data leak waiting to happen) |

The technology (a URL that serves bytes from Cloud Storage) is identical in both cases — the
difference is entirely about **who should be able to construct that URL and for how long**. Get that
judgment call right, and CMEK/retention/conditions from the earlier steps stay meaningful; get it
wrong, and a public bucket flag undoes all of it in one click.

---

## Checkpoint

- [ ] A signed URL for `q1-report.txt` was generated via `--impersonate-service-account`, no JSON key
      downloaded
- [ ] The signed URL worked before expiry and failed after
- [ ] `meridian-product-photos-<PROJECT_ID>` serves `index.html` publicly with no authentication
- [ ] You can articulate why the receipts bucket should never get an `allUsers` grant

---

**Next:** [Step 5 — Bucket Logging & Audit](./05-bucket-logging-and-audit.md)
