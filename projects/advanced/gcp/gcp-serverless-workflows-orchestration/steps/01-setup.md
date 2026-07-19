# Step 1 — Setup: APIs and Service Accounts

This project has the repo's most involved identity chain. You'll create all four service accounts up
front so the later steps can just reference them. Keep [architecture.md §2](../architecture.md) open —
it names every SA and grant.

---

## 1.1 Project and Region

```bash
export PROJECT_ID="$(gcloud config get-value project)"
export REGION=us-east1
gcloud config set project "$PROJECT_ID"
gcloud config set run/region "$REGION"
gcloud config set functions/region "$REGION"
export PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
echo "Project $PROJECT_ID ($PROJECT_NUMBER) / $REGION"
```

---

## 1.2 Enable the APIs

```bash
gcloud services enable \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  workflows.googleapis.com \
  workflowexecutions.googleapis.com \
  cloudtasks.googleapis.com \
  apigateway.googleapis.com \
  servicemanagement.googleapis.com \
  servicecontrol.googleapis.com \
  logging.googleapis.com
```

| API | Why |
|-----|-----|
| `workflows` / `workflowexecutions` | Define and run the orchestrator |
| `cloudtasks` | The async shipping queue |
| `apigateway` / `servicemanagement` / `servicecontrol` | API Gateway needs all three |

Enabling API Gateway's trio for the first time takes a minute.

---

## 1.3 Create the Four Service Accounts

```bash
gcloud iam service-accounts create order-workflow-sa \
  --display-name "Workflow identity: calls step functions + enqueues tasks"
gcloud iam service-accounts create tasks-invoker-sa \
  --display-name "Cloud Tasks identity: invokes shipping-worker"
gcloud iam service-accounts create order-intake-sa \
  --display-name "order-intake identity: starts workflow executions"
gcloud iam service-accounts create gateway-invoker-sa \
  --display-name "API Gateway identity: invokes order-intake"

# Convenience exports used throughout the project.
export WF_SA="order-workflow-sa@${PROJECT_ID}.iam.gserviceaccount.com"
export TASKS_SA="tasks-invoker-sa@${PROJECT_ID}.iam.gserviceaccount.com"
export INTAKE_SA="order-intake-sa@${PROJECT_ID}.iam.gserviceaccount.com"
export GW_SA="gateway-invoker-sa@${PROJECT_ID}.iam.gserviceaccount.com"
```

| Service account | Purpose |
|-----------------|---------|
| `order-workflow-sa` | The workflow runs as this; calls validate/charge/refund and enqueues tasks |
| `tasks-invoker-sa` | Cloud Tasks uses this to call `shipping-worker` |
| `order-intake-sa` | The intake function uses this to start workflow executions |
| `gateway-invoker-sa` | API Gateway uses this to invoke `order-intake` |

Grants that attach these SAs to specific resources happen in the step where that resource is created
(functions → Step 2, queue → Step 3, workflow → Step 4, gateway → Step 6). This keeps each grant next
to the thing it protects.

> **Tip:** keep these four `export`s handy — re-run this block if you open a new shell. Everything
> downstream references `$WF_SA`, `$TASKS_SA`, `$INTAKE_SA`, `$GW_SA`.

---

## Checkpoint

- [ ] All listed APIs are enabled
- [ ] Four service accounts exist (`gcloud iam service-accounts list`)
- [ ] `$WF_SA`, `$TASKS_SA`, `$INTAKE_SA`, `$GW_SA`, `$PROJECT_NUMBER` are exported

---

**Next:** [Step 2 — Deploy the Step Functions](./02-deploy-step-functions.md)
