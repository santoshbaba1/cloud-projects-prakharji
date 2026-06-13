# Step 6 — CloudTrail: Audit the Serverless Stack

CloudTrail works the same regardless of compute model. Here you confirm that every
serverless control-plane action — `CreateFunction`, `UpdateFunctionCode`, `CreateApi`,
`PutMetricAlarm` — is recorded for audit.

> If you already created a multi-Region trail in the
> [EC2 project's Step 9](../../ec2-vpc-monitored-webapp/steps/09-cloudtrail-audit.md), it's
> **already capturing** these serverless events too — a trail is account-wide. In that case
> just do 6.2 (read the events) and skip creating a second trail.

---

## 6.1 Console — Create the Trail (if you don't have one)

1. **CloudTrail → Trails → Create trail**.

   | Field | Value |
   |-------|-------|
   | Trail name | `serverless-audit-trail` |
   | Storage | **Create new S3 bucket** (`serverless-audit-<unique>`) |
   | Log file validation | Enabled |
   | Event types | **Management events**, Read + Write |

2. **Create trail.** Events appear in S3 within ~15 minutes.

---

## 6.2 Read the Audit Trail

**CloudTrail → Event history** and filter by **Event name**:

| Event name | What it tells you |
|------------|-------------------|
| `CreateFunction` | When/who created `serverless-webapp` and with which role |
| `UpdateFunctionCode` | Every deploy — including the GitHub Actions ones from Step 7 |
| `CreateApi` / `CreateStage` | The API Gateway setup |
| `PutMetricAlarm` | The alarms you created in Step 4 |
| `Subscribe` | The SNS email subscription |

Each record carries `userIdentity` (who), `sourceIPAddress` (from where), and `eventTime`.
After Step 7, the `UpdateFunctionCode` events will show the **assumed-role session** of your
GitHub Actions OIDC role — so you can trace a production deploy back to a specific workflow
run and commit.

---

## 6.3 Why It Matters for Serverless

People assume "serverless = nothing to audit." The opposite is true: because everything is
an API call, **CloudTrail captures the entire lifecycle** — who deployed code, who changed a
function's permissions, who modified an alarm. That's a complete, tamper-evident audit log
with zero agents to install.

---

## Checkpoint

- [ ] A management-events trail is logging (new or reused from the EC2 project)
- [ ] You found `CreateFunction` and `CreateApi` in Event history
- [ ] You understand a deploy via GitHub OIDC will appear as an assumed-role session here

---

**Next:** [Step 7 — GitHub Actions Deploy](./07-github-actions-deploy.md)
