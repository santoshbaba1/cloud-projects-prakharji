# Step 5 — Cleanup: Delete All Resources

This project costs essentially nothing while idle, but it's good practice to remove
resources you're done with. CloudFront has one quirk: **you must disable a distribution
before you can delete it**, and disabling takes a few minutes to deploy.

Delete in this order:

```
1. Disable + delete the CloudFront distribution
2. Empty the S3 bucket
3. Delete the S3 bucket
4. (Optional) Delete the Origin Access Control
```

---

## 5.1 Console — Disable and Delete the Distribution

1. Open **CloudFront** → select your distribution → click **Disable**.
2. Confirm. The status changes to **Deploying**; wait until **Last modified** shows a
   date again and the **Enabled** column reads **Disabled** (5–15 minutes).
3. With the distribution still selected, click **Delete** → confirm.

> You cannot delete an **enabled** distribution. If **Delete** is greyed out, the
> distribution is either still enabled or still deploying — wait and refresh.

---

## 5.2 Console — Empty and Delete the Bucket

1. Open **S3** → select your bucket → click **Empty**.
2. Type `permanently delete` to confirm, then click **Empty**.
3. With the bucket selected, click **Delete**, type the bucket name to confirm, and
   click **Delete bucket**.

> A bucket must be **empty** before it can be deleted. The **Empty** step removes
> `index.html` and `error.html` first.

---

## 5.3 Console — Delete the Origin Access Control (Optional)

1. Open **CloudFront** → in the left sidebar under **Security**, click **Origin access**.
2. Select your OAC (`static-site-oac`) and click **Delete**.

> An OAC costs nothing to keep, but deleting it leaves your account tidy. You can only
> delete an OAC once no distribution references it (the distribution is already gone).

---

## 5.4 AWS CLI (Alternative)

```bash
# 1. Get the current distribution config + ETag, set Enabled=false, then update it
#    (CloudFront requires the full config object to disable — easiest via Console)
aws cloudfront get-distribution-config --id DISTRIBUTION_ID
# ...edit Enabled to false, then:
aws cloudfront update-distribution --id DISTRIBUTION_ID \
  --distribution-config file://disabled-config.json --if-match ETAG

# Wait until Status is Deployed, then delete (needs the new ETag)
aws cloudfront delete-distribution --id DISTRIBUTION_ID --if-match NEW_ETAG

# 2. Empty and delete the bucket
aws s3 rm "s3://$BUCKET" --recursive
aws s3api delete-bucket --bucket "$BUCKET" --region us-east-1

# 3. Delete the OAC
aws cloudfront delete-origin-access-control --id OAC_ID --if-match OAC_ETAG
```

---

## Checkpoint

- [ ] CloudFront distribution is **disabled**, then **deleted**
- [ ] S3 bucket is **emptied**, then **deleted**
- [ ] (Optional) Origin Access Control is deleted
- [ ] No `static-site-*` resources remain in S3 or CloudFront

---

🎉 **Project complete!** You hosted a static website on a private S3 bucket, served it
globally through CloudFront with HTTPS, secured the origin with OAC, added a custom error
page, and learned how caching and invalidation work.

See **[challenges.md](../challenges.md)** to extend the project (custom domain, access logs,
geo-restriction, and more).
