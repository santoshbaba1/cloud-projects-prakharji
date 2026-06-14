# Troubleshooting — API Gateway HTTP API + Lambda + DynamoDB

Format: **Error → Cause → Fix.**

---

### `500 Internal Server Error` from the API, logs show `AccessDeniedException` for DynamoDB

**Cause:** The execution role's DynamoDB policy is missing, or scoped to the wrong table ARN
(typo, wrong account id, or `Resource: "*"` was replaced with a bad value).

**Fix:** Confirm the inline policy on `TasksApiExecutionRole` lists the 5 DynamoDB actions on
`arn:aws:dynamodb:us-east-1:<account>:table/tasks`. Re-run Step 1's `put-role-policy`.

---

### `500 Internal Server Error`, logs show `ResourceNotFoundException` (table)

**Cause:** The `TABLE_NAME` env var doesn't match the real table, or the table is in a
different region.

**Fix:** Check `Configuration → Environment variables` → `TABLE_NAME=tasks`, and that the
table exists in `us-east-1`. Remember `update-function-configuration` **replaces** all env
vars — re-adding only `APP_VERSION` would drop `TABLE_NAME`.

---

### `502 Bad Gateway` / `Internal Server Error` right after switching aliases

**Cause:** API Gateway tried to invoke an alias (`blue`/`green`) it has no permission for. The
console only auto-grants invoke on the alias you pick at creation.

**Fix:** Add invoke permission for each new alias:

```bash
aws lambda add-permission --function-name tasks-api --qualifier green \
  --statement-id apigw-invoke-green --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:<account>:<api-id>/*/*"
```

---

### `DELETE` returns `204` but the task is still listed

**Cause:** You deleted by a different `id` than the item's key, or `GET /tasks` is reading a
cached response. DynamoDB deletes are idempotent — deleting a non-existent key still returns
`204`.

**Fix:** Confirm the `id` in the path matches the item's `id` exactly (UUIDs are
case-sensitive). Re-list with `GET /tasks`.

---

### `PUT /tasks/{id}` returns 404 for an id you just created

**Cause:** Eventual consistency is **not** the issue for `GetItem` (it's strongly consistent by
default on the same key) — more likely the id in the URL is wrong or url-encoded oddly.

**Fix:** Capture the id from the `POST` response and reuse it verbatim. Avoid spaces/encoding
surprises by quoting the URL.

---

### `/version` never shows v2 during a rolling/canary deploy

**Cause:** Weight too low to see in a few requests, or version published before the env-var
update landed.

**Fix:** Loop 30+ probes to see the split. If v2 never appears, ensure `publish-version` ran
*after* `aws lambda wait function-updated` following the config update — then publish again.

---

### Local `python3 test_app.py` fails with `NoRegionError`

**Cause:** `boto3.resource("dynamodb")` runs at import and wants a region.

**Fix:** The test sets `AWS_DEFAULT_REGION` before importing `app` — run it as
`python3 test_app.py` from the `src/` dir. (No AWS calls happen; the table is faked.)

---

### After blue-green rollback, some tasks look broken

**Cause:** Green's release changed the **data schema** (renamed/removed an attribute) and wrote
items blue can't interpret. Blue and green share one table.

**Fix:** Make schema changes backward-compatible (add new attributes, don't repurpose old
ones) during any blue-green window. See the caveat in
[Step 7](steps/07-blue-green-deployment.md).
