# Step 1 — IAM: Create the Bucket-Scoped Role

This function can **delete objects**, so its permissions must be tight. The role gets list,
read, write, and delete — but only on **one bucket**, named explicitly. It can't touch any
other bucket in your account.

> You'll create the bucket in Step 2. Pick its name **now** so the policy can reference it.
> Bucket names are globally unique, so use a suffix you own, e.g.
> `s3-housekeeping-demo-<your-initials>-<random>`.

---

## 1.1 Create the Role (Trust Policy)

1. **IAM** → **Roles** → **Create role**.

| Field | Value |
|-------|-------|
| Trusted entity type | **AWS service** |
| Use case | **Lambda** |

**Next**.

---

## 1.2 Attach Basic Execution (Logs)

Search `AWSLambdaBasicExecutionRole`, tick it, **Next**.

---

## 1.3 Name and Create

| Field | Value |
|-------|-------|
| Role name | `S3HousekeeperExecutionRole` |
| Description | `s3-housekeeper — list/get/put/delete on one bucket only` |

**Create role**, then open it and **copy the Role ARN**.

---

## 1.4 Add the Bucket Policy (Inline)

1. Open the role → **Add permissions** → **Create inline policy** → **JSON** tab.
2. Paste, replacing `YOUR_BUCKET_NAME` with the name you'll create in Step 2:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListTheBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME"
    },
    {
      "Sid": "ReadWriteDeleteObjects",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
    }
  ]
}
```

3. Name it `S3HousekeeperBucketAccess` → **Create policy**.

| Permission | Service | Why It's Needed |
|------------|---------|-----------------|
| `s3:ListBucket` | S3 | Enumerate objects to find old ones. Note it targets the **bucket ARN** (no `/*`) |
| `s3:GetObject` | S3 | `copy_object` reads the source object during archive |
| `s3:PutObject` | S3 | Write the copy into `archive/` |
| `s3:DeleteObject` | S3 | Remove the original (archive) or the object (delete) |

> **Two ARN shapes, on purpose:** bucket-level actions (`ListBucket`) use the **bucket** ARN
> (`arn:aws:s3:::name`); object-level actions use the **object** ARN with `/*`
> (`arn:aws:s3:::name/*`). Mixing these up is the #1 S3 IAM mistake — `ListBucket` on a `/*`
> resource silently denies, and `GetObject` on the bucket ARN does too.

---

## AWS CLI (Alternative)

```bash
BUCKET=YOUR_BUCKET_NAME

aws iam create-role \
  --role-name S3HousekeeperExecutionRole \
  --assume-role-policy-document '{
    "Version":"2012-10-17",
    "Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]
  }'

aws iam attach-role-policy \
  --role-name S3HousekeeperExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam put-role-policy \
  --role-name S3HousekeeperExecutionRole \
  --policy-name S3HousekeeperBucketAccess \
  --policy-document "{
    \"Version\":\"2012-10-17\",
    \"Statement\":[
      {\"Effect\":\"Allow\",\"Action\":\"s3:ListBucket\",\"Resource\":\"arn:aws:s3:::${BUCKET}\"},
      {\"Effect\":\"Allow\",\"Action\":[\"s3:GetObject\",\"s3:PutObject\",\"s3:DeleteObject\"],\"Resource\":\"arn:aws:s3:::${BUCKET}/*\"}
    ]
  }"
```

---

## Checkpoint

- [ ] Role `S3HousekeeperExecutionRole` exists, trusted by `lambda.amazonaws.com`
- [ ] `AWSLambdaBasicExecutionRole` attached
- [ ] Inline policy uses the **bucket ARN** for `ListBucket` and the **`/*` ARN** for object actions
- [ ] You copied the Role ARN and chosen bucket name

---

**Next:** [Step 2 — Create the Bucket and Seed Objects](./02-create-bucket-and-seed.md)
