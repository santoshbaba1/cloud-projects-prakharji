# Step 4 — Endpoints + Test Connections

An **endpoint** is DMS's saved connection to one database: host, port, credentials, engine. You
create a **source endpoint** (the EC2 MySQL) and a **target endpoint** (the RDS MySQL), then
**test** each from the replication instance. Testing here — before any task runs — is the single
best habit in DMS: it isolates connectivity problems from migration problems.

---

## 4.1 Create the Source Endpoint

**DMS → Endpoints → Create endpoint → Source endpoint:**

| Field | Value |
|-------|-------|
| Identifier | `dms-source-endpoint` |
| Source engine | MySQL |
| Server name | source EC2 **private IP** |
| Port | 3306 |
| Username / password | `admin` / your source password |

```bash
aws dms create-endpoint \
  --endpoint-identifier dms-source-endpoint --endpoint-type source \
  --engine-name mysql --server-name <source-private-ip> --port 3306 \
  --username admin --password 'ChangeMe_Strong#1'
```

## 4.2 Create the Target Endpoint

**Create endpoint → Target endpoint:**

| Field | Value |
|-------|-------|
| Identifier | `dms-target-endpoint` |
| Target engine | MySQL |
| Server name | RDS **endpoint address** (Step 2) |
| Port | 3306 |
| Username / password | `admin` / your RDS password |

```bash
aws dms create-endpoint \
  --endpoint-identifier dms-target-endpoint --endpoint-type target \
  --engine-name mysql --server-name <rds-endpoint-address> --port 3306 \
  --username admin --password 'ChangeMe_Strong#1'
```

---

## 4.3 Test Both Connections

In the console, open each endpoint → **Connections → Test** → select `dms-repl-instance` → run.
Both must say **successful** before you go on.

```bash
aws dms test-connection \
  --replication-instance-arn <repl-instance-arn> \
  --endpoint-arn <source-endpoint-arn>
# repeat for the target endpoint; then:
aws dms describe-connections \
  --query 'Connections[].[EndpointIdentifier,Status]' --output table
```

> **If a test fails:** it's almost always the **network path** (security group, wrong
> IP/endpoint, or the DB not listening), not the task config. Source uses the EC2 **private
> IP**; target uses the **RDS endpoint hostname**. See [troubleshooting.md](../troubleshooting.md).

---

## Checkpoint

- [ ] `dms-source-endpoint` (MySQL, source EC2 private IP) created
- [ ] `dms-target-endpoint` (MySQL, RDS endpoint) created
- [ ] **Both** test connections return **successful** from `dms-repl-instance`
- [ ] You understand why source = private IP and target = RDS hostname

---

**Next:** [Step 5 — Full Load + CDC Migration Task](./05-migration-task.md)
