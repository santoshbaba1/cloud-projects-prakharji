# Step 2 — DynamoDB Tables + Migrate the Data

The monolith keeps everything in one SQLite file with two tables, `books` and `orders`.
The serverless target uses **two separate DynamoDB tables** — one per domain — because each
will be owned by a different function. This is the **database-per-service** principle: a
service owns its data and nobody else writes it directly.

In this step you create the tables and copy the existing data across, so the new world starts
with the same catalog the old world had.

---

## 2.1 What You're Creating

| Table | Partition key | Billing | Owner (later) |
|-------|---------------|---------|---------------|
| `Books` | `id` (String) | On-demand | `bookstore-catalog` |
| `Orders` | `id` (String) | On-demand | `bookstore-orders` |

> **Why on-demand billing?** No capacity planning, no hourly charge when idle — you pay per
> request. Perfect for a workshop and for spiky real traffic alike.

---

## 2.2 Console — Create the Tables

1. **DynamoDB → Tables → Create table.**
2. **Table name:** `Books`. **Partition key:** `id` — **String**.
3. **Table settings:** Customize → **Read/write capacity → On-demand**. **Create table.**
4. Repeat for **`Orders`** (partition key `id`, String, On-demand).

### CLI alternative

```bash
for T in Books Orders; do
  aws dynamodb create-table \
    --table-name "$T" \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
done
aws dynamodb wait table-exists --table-name Books
aws dynamodb wait table-exists --table-name Orders
```

---

## 2.3 Migrate the Data (SQLite → DynamoDB)

This is the data half of the migration. On the EC2 box (where `bookstore.db` lives), run a
small Python exporter that reads SQLite and `put_item`s each row into DynamoDB. **It's
idempotent** — `put_item` overwrites by key, so re-running is safe.

On `bookstore-monolith` (it already has the data and an instance role; ensure that role can
write DynamoDB, or run this from your laptop after copying `bookstore.db` down):

```bash
python3 -m pip install --user boto3
```

```python
# migrate_data.py  — run once; reads SQLite, writes DynamoDB
import sqlite3, boto3
from decimal import Decimal

src = sqlite3.connect("bookstore.db")
src.row_factory = sqlite3.Row
ddb = boto3.resource("dynamodb", region_name="us-east-1")

books = ddb.Table("Books")
with books.batch_writer() as bw:
    for r in src.execute("SELECT * FROM books"):
        bw.put_item(Item={"id": r["id"], "title": r["title"],
                          "author": r["author"], "price": Decimal(str(r["price"]))})

orders = ddb.Table("Orders")
with orders.batch_writer() as bw:
    for r in src.execute("SELECT * FROM orders"):
        bw.put_item(Item={"id": r["id"], "book_id": r["book_id"],
                          "qty": int(r["qty"]), "status": r["status"]})

print("migrated:",
      books.scan(Select="COUNT")["Count"], "books,",
      orders.scan(Select="COUNT")["Count"], "orders")
```

```bash
python3 migrate_data.py
# migrated: 3 books, N orders
```

> **Why `Decimal` for price?** DynamoDB's number type maps to Python `Decimal`, not `float`.
> Passing a `float` raises `Inexact / Rounding` errors — converting via `str()` keeps it exact.

> **Why `batch_writer()`?** It batches and auto-retries throttled/unprocessed items. For three
> rows it's overkill — but it's the right habit for real migrations of thousands of rows.

---

## 2.4 Verify

```bash
aws dynamodb scan --table-name Books \
  --query "Items[].title.S" --output text
```

You should see the three book titles.

---

## Checkpoint

- [ ] `Books` and `Orders` tables exist, on-demand, partition key `id`
- [ ] `migrate_data.py` reported the row counts from SQLite
- [ ] A `scan` of `Books` shows the migrated titles
- [ ] You understand why each table is owned by exactly one future function

---

**Next:** [Step 3 — Per-Function IAM Roles](./03-iam-roles.md)
