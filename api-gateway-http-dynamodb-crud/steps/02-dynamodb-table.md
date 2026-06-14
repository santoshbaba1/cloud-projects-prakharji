# Step 2 — Create the DynamoDB Table

Our tasks need to survive cold starts, so we store them in **DynamoDB**, a fully managed
key-value/document store. We use **on-demand** billing: no capacity to provision, no hourly
charge, you pay per request. Perfect for a workshop and for spiky real workloads.

The table needs only a **partition key**: `id` (a string, a UUID our code generates). Every
other attribute (`title`, `done`) is **schemaless** — DynamoDB doesn't require you to declare
them.

---

## 2.1 Console — Create the Table

1. **DynamoDB → Tables → Create table**.
2. **Table name:** `tasks`.
3. **Partition key:** `id`, type **String**.
4. Leave **Sort key** empty.
5. **Table settings:** Customize → **Capacity mode: On-demand**.
6. **Create table**. Wait until status is **Active**.

---

## 2.2 AWS CLI (Alternative)

```bash
REGION=us-east-1
aws dynamodb create-table --table-name tasks \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST --region $REGION

aws dynamodb wait table-exists --table-name tasks --region $REGION
```

---

## 2.3 (Optional) Seed One Item

So `GET /tasks` returns something before you create any via the API:

```bash
aws dynamodb put-item --table-name tasks --region us-east-1 \
  --item '{"id":{"S":"seed-1"},"title":{"S":"learn DynamoDB"},"done":{"BOOL":false}}'
```

---

## Checkpoint

- [ ] Table `tasks` is **Active**
- [ ] Partition key is `id` (String); no sort key
- [ ] Billing mode is **on-demand** (PAY_PER_REQUEST)

---

**Next:** [Step 3 — Create the Lambda Function](./03-lambda-function.md)
