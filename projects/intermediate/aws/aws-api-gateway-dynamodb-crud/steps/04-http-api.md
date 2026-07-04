# Step 4 — Build the HTTP API (and Point It at an Alias)

The **HTTP API** is API Gateway's newer, cheaper, lower-latency front door. Where the REST
API (Project 1) made you build a resource tree, an HTTP API is just a flat list of **routes**
(`METHOD /path`) each pointing at an **integration**. We'll route every CRUD verb to our one
Lambda.

As in Project 1, we point the integration at a Lambda **alias**, not the bare function. The
alias is where all the deployment action happens in steps 5–7.

---

## 4.1 Publish Version 1 + the `live` Alias

```bash
REGION=us-east-1
aws lambda publish-version --function-name tasks-api --region $REGION \
  --query 'Version' --output text          # prints: 1
aws lambda create-alias --function-name tasks-api \
  --name live --function-version 1 --region $REGION
```

Console: **Lambda → tasks-api → Versions → Publish new version**, then **Aliases → Create
alias** `live` → version `1`.

---

## 4.2 Console — Create the HTTP API

1. **API Gateway → Create API → HTTP API → Build**.
2. **Integrations → Add integration → Lambda** → choose the **alias**: `tasks-api:live`
   (the dropdown lists aliases below the function).
3. **API name:** `tasks-http-api` → Next.
4. **Configure routes** — add one per line, all to the `tasks-api:live` integration:

   | Method | Path |
   |--------|------|
   | GET | `/tasks` |
   | POST | `/tasks` |
   | GET | `/tasks/{id}` |
   | PUT | `/tasks/{id}` |
   | DELETE | `/tasks/{id}` |
   | GET | `/version` |

5. **Stages:** keep the default `$default` with **auto-deploy ON** → Next → **Create**.
6. Copy the **Invoke URL** (e.g. `https://abc123.execute-api.us-east-1.amazonaws.com`).

> Selecting the **alias** as the integration target makes API Gateway add invoke permission
> on that alias automatically. When you add new aliases by hand later (`blue`, `green`), you
> grant their permission yourself — see steps 6 and 7.

---

## 4.3 Test the Live API

```bash
API=https://abc123.execute-api.us-east-1.amazonaws.com
curl -s $API/tasks                                   # list, "version":"1.0.0"
ID=$(curl -s -X POST $API/tasks -H 'Content-Type: application/json' \
       -d '{"title":"call mom"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
curl -s $API/tasks/$ID                               # the new task
curl -s -X PUT $API/tasks/$ID -H 'Content-Type: application/json' -d '{"done":true}'
curl -s -X DELETE $API/tasks/$ID -o /dev/null -w "%{http_code}\n"   # 204
curl -s $API/version                                 # {"version":"1.0.0"}
```

All five CRUD verbs plus `/version` should work. `GET /version` returning `1.0.0` confirms the
route → `live` alias → version 1 chain — your probe for the deployment steps.

---

## 4.4 AWS CLI (Alternative — quick create)

```bash
REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ALIAS_ARN=$(aws lambda get-alias --function-name tasks-api --name live \
  --query 'AliasArn' --output text --region $REGION)

API_ID=$(aws apigatewayv2 create-api --name tasks-http-api \
  --protocol-type HTTP --target $ALIAS_ARN \
  --query 'ApiId' --output text --region $REGION)

aws lambda add-permission --function-name tasks-api --qualifier live \
  --statement-id apigw-invoke-live --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*" --region $REGION

echo "API_ID=$API_ID"   # SAVE THIS
```

> The `--target <alias-arn>` shortcut makes a catch-all `$default` route to the alias; the
> handler routes internally, so all verbs work. For named routes, use `create-route` +
> `create-integration` per row. **Save `API_ID`.**

---

## Checkpoint

- [ ] Lambda **version 1** published; alias **`live`** → version 1
- [ ] HTTP API `tasks-http-api` exists; integration target is the **`live` alias**
- [ ] All CRUD routes respond; `DELETE` returns `204`
- [ ] `curl $API/version` returns `{"version":"1.0.0"}`
- [ ] You saved the **Invoke URL** and **API_ID**

---

**Next:** [Step 5 — Rolling Deployment](./05-rolling-deployment.md)
