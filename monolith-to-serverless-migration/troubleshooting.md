# Troubleshooting — Monolith → Serverless Migration

Format: **Error → Cause → Fix.**

---

### Monolith: `curl http://<ip>:5000/books` times out

**Cause:** Security group doesn't allow port 5000 from your IP, or Flask is bound to
`127.0.0.1` instead of `0.0.0.0`.

**Fix:** Add an inbound rule `Custom TCP 5000` from **My IP** on the instance's security group.
Confirm the app prints `Running on http://0.0.0.0:5000` — `app.run(host="0.0.0.0", ...)` is set
in `app.py`. If you used SSM-only (no SSH), reach it via Session Manager + `curl localhost:5000`.

---

### Data migration: `Float types are not supported. Use Decimal types instead`

**Cause:** DynamoDB's number type maps to Python `Decimal`. The SQLite `price` comes back as a
`float`, which `put_item` rejects.

**Fix:** Convert via string — `Decimal(str(row["price"]))`, as the Step 2 script does. Never
`Decimal(float_value)` directly (that carries the float's imprecision).

---

### Lambda: `AccessDeniedException` on DynamoDB in the catalog/orders logs

**Cause:** The execution role's inline policy is missing, scoped to the wrong table ARN, or has
the wrong account id.

**Fix:** Re-check Step 3. `BookstoreCatalogRole` must allow `GetItem`/`Scan` on
`.../table/Books`; `BookstoreOrdersRole` must allow `GetItem`/`PutItem` on `.../table/Orders`
**and** `GetItem` on `.../table/Books`. No `Resource: "*"`.

---

### Lambda: `ResourceNotFoundException` (table)

**Cause:** The `BOOKS_TABLE`/`ORDERS_TABLE` env var doesn't match the real table name, or the
table is in another region.

**Fix:** Confirm env vars (`Books`, `Orders`) and that the tables live in `us-east-1`. Note
`update-function-configuration` **replaces** all env vars — re-setting one drops the others.

---

### Orders Lambda: every `POST /orders` returns `400 unknown book_id`

**Cause:** The orders function can't *read* `Books` (missing the second statement in its role),
so the validation lookup returns nothing — or you're posting an id that wasn't migrated.

**Fix:** Confirm `BookstoreOrdersRole` includes `GetItem` on the `Books` ARN. Confirm the
`book_id` you POST actually exists: `aws dynamodb get-item --table-name Books --key '{"id":{"S":"<id>"}}'`.

---

### API Gateway: `{"message":"Not Found"}` for a route that exists

**Cause:** Route key and integration don't match (e.g. route `GET /books/{id}` exists but no
integration is attached), or you're hitting the wrong stage path.

**Fix:** In **Develop → Routes**, verify each route shows an attached integration. HTTP APIs use
the `$default` stage, so the URL is `https://<api-id>.execute-api.us-east-1.amazonaws.com/books`
with **no** stage segment.

---

### API Gateway: `500 Internal Server Error` but the Lambda test worked

**Cause:** Payload shape mismatch — the function reads `event["requestContext"]["http"]["method"]`
(payload v2.0). A REST API or a v1.0 integration sends a different shape.

**Fix:** Ensure the integration is **payload format version 2.0** (the HTTP API default for
Lambda proxy). Check the function's CloudWatch logs for the actual `KeyError`.

---

### After cutover, an order placed on the monolith is missing in DynamoDB

**Cause:** It was created **after** your Step 2 export but **before** cutover — the classic
"data drift during migration" gap.

**Fix:** Re-run the idempotent exporter (Step 7 reconciliation) before terminating the monolith.
Counts must match. This is exactly why Step 7 reconciles twice.

---

### HTTP_PROXY catch-all to the monolith returns 502

**Cause:** The optional `$default` HTTP_PROXY integration points at an EC2 IP/port that's
unreachable (instance stopped, security group closed, or wrong port).

**Fix:** While the monolith should still serve un-migrated routes, keep it running with port
5000 open to API Gateway. Once all routes are migrated, **delete the catch-all** instead of
fixing it — that's the cutover completing.
