# Challenges — Database Migration with AWS DMS

Extend the migration. Early ones deepen the DMS workflow; later ones tackle the harder
heterogeneous and zero-downtime cases.

---

## 1. Read and act on the DMS validation report
Enable detailed **data validation**, then deliberately corrupt one row on the target and watch
DMS flag a **validation failure**. Find the mismatched row in the validation table. *Skills: DMS
data validation, trust-but-verify.*

## 2. Pre-create the schema (control the target shape)
Instead of letting full load auto-create tables, pre-create `shopdb` on RDS with your own column
types/indexes and run the task in **Truncate** / **Do nothing** mode. Compare the result. *Skills:
schema control, target preparation modes.*

## 3. Transform during migration (table mappings)
Add a **transformation rule** to the table mappings — e.g. rename `orders` → `sales`, or add a
prefix to the schema. Prove the data lands under the new name. *Skills: DMS transformation rules.*

## 4. Drive the whole migration with Boto3
Recreate the endpoints, replication instance, and task with **Boto3** (`create_endpoint`,
`create_replication_task`, `start_replication_task`) and poll status until *replication ongoing*.
Compare to the console clicks. *Skills: Boto3, DMS API, automation.*

## 5. Heterogeneous migration with SCT (MySQL → PostgreSQL)
The hard one. Stand up an RDS **PostgreSQL** target and use the **AWS Schema Conversion Tool
(SCT)** to convert the MySQL schema, then run a DMS task across engines. Note what SCT *can't*
auto-convert (this is what makes heterogeneous a **Refactor**, not a Replatform). *Skills: SCT,
heterogeneous migration, the 6 R's boundary.*

## 6. Minimize RTO with a tighter cutover
Script the cutover: stop source writes, poll `describe-replication-tasks` until CDC latency = 0,
flip the connection string, and time the whole window. How low can you push the **RTO**? *Skills:
cutover automation, RPO/RTO measurement.*

## 7. Migrate to Aurora MySQL instead of RDS MySQL
Point the target endpoint at an **Aurora MySQL** cluster. Compare the managed-HA story
(Aurora's storage layer + replicas) against single-AZ RDS. *Skills: Aurora, target choice.*

---

> You migrated a **live** database with **full load + CDC** — the technique that lets the source
> stay open until the moment of cutover, keeping **RPO and RTO** low. That's a **Replatform**:
> same engine, managed home. Compare the two **Refactor** migrations in this repo —
> [serverless](../aws-monolith-to-serverless-migration/README.md) and
> [microservices](../../kubernetes/eks-monolith-to-microservices/README.md) — which change the architecture
> itself.
