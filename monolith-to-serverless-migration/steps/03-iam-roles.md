# Step 3 — Per-Function IAM Roles (least privilege)

In the monolith, one process could touch *every* table — there was no boundary. The serverless
version restores the boundary in IAM: **each function gets its own role, scoped to only the
data it owns.** Catalog can read `Books`. Orders can write `Orders` and *read* `Books` (to
validate a `book_id`) — but it can never touch `Books` writes, and catalog can never touch
`Orders` at all.

---

## 3.1 What You're Creating

| Role | Trusts | Grants |
|------|--------|--------|
| `BookstoreCatalogRole` | `lambda.amazonaws.com` | Logs; **read** `Books` |
| `BookstoreOrdersRole` | `lambda.amazonaws.com` | Logs; **read/write** `Orders`; **read** `Books` |

| Permission | Service | Why It's Needed |
|------------|---------|-----------------|
| `logs:CreateLogGroup/Stream`, `PutLogEvents` | CloudWatch | Function logging (via `AWSLambdaBasicExecutionRole`) |
| `dynamodb:GetItem`, `Scan` on `Books` | DynamoDB | Catalog lists/reads books |
| `dynamodb:GetItem`, `PutItem` on `Orders` | DynamoDB | Orders creates/reads orders |
| `dynamodb:GetItem` on `Books` (orders role) | DynamoDB | Validate `book_id` before creating an order |

> **Why split the roles at all?** Independent blast radius. A bug in `bookstore-orders` can't
> scan or wipe the catalog; a compromised `bookstore-catalog` can't read anyone's orders.

---

## 3.2 Console — Catalog Role

1. **IAM → Roles → Create role → AWS service → Lambda → Next.**
2. Attach **`AWSLambdaBasicExecutionRole`** → Next.
3. **Role name:** `BookstoreCatalogRole` → **Create role**.
4. Open it → **Add permissions → Create inline policy → JSON** (replace `<account>`):

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Action": ["dynamodb:GetItem", "dynamodb:Scan"],
       "Resource": "arn:aws:dynamodb:us-east-1:<account>:table/Books"
     }]
   }
   ```
   Name it `CatalogBooksRead` → **Create policy**.

## 3.3 Console — Orders Role

Repeat for `BookstoreOrdersRole`, with this inline policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["dynamodb:GetItem", "dynamodb:PutItem"],
      "Resource": "arn:aws:dynamodb:us-east-1:<account>:table/Orders"
    },
    {
      "Effect": "Allow",
      "Action": ["dynamodb:GetItem"],
      "Resource": "arn:aws:dynamodb:us-east-1:<account>:table/Books"
    }
  ]
}
```

---

## 3.4 CLI Alternative

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

cat > lambda-trust.json <<'JSON'
{ "Version": "2012-10-17",
  "Statement": [{ "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole" }] }
JSON

# --- Catalog role ---
aws iam create-role --role-name BookstoreCatalogRole \
  --assume-role-policy-document file://lambda-trust.json
aws iam attach-role-policy --role-name BookstoreCatalogRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
cat > catalog-policy.json <<JSON
{ "Version": "2012-10-17",
  "Statement": [{ "Effect": "Allow",
    "Action": ["dynamodb:GetItem","dynamodb:Scan"],
    "Resource": "arn:aws:dynamodb:us-east-1:${ACCOUNT_ID}:table/Books" }] }
JSON
aws iam put-role-policy --role-name BookstoreCatalogRole \
  --policy-name CatalogBooksRead --policy-document file://catalog-policy.json

# --- Orders role ---
aws iam create-role --role-name BookstoreOrdersRole \
  --assume-role-policy-document file://lambda-trust.json
aws iam attach-role-policy --role-name BookstoreOrdersRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
cat > orders-policy.json <<JSON
{ "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow",
      "Action": ["dynamodb:GetItem","dynamodb:PutItem"],
      "Resource": "arn:aws:dynamodb:us-east-1:${ACCOUNT_ID}:table/Orders" },
    { "Effect": "Allow",
      "Action": ["dynamodb:GetItem"],
      "Resource": "arn:aws:dynamodb:us-east-1:${ACCOUNT_ID}:table/Books" } ] }
JSON
aws iam put-role-policy --role-name BookstoreOrdersRole \
  --policy-name OrdersTablesAccess --policy-document file://orders-policy.json
```

---

## Checkpoint

- [ ] `BookstoreCatalogRole` can read **only** `Books`
- [ ] `BookstoreOrdersRole` can read/write `Orders` and **read** `Books`
- [ ] Neither role uses `Resource: "*"`
- [ ] You can explain why catalog cannot reach the `Orders` table

---

**Next:** [Step 4 — Build the Catalog Lambda](./04-catalog-lambda.md)
