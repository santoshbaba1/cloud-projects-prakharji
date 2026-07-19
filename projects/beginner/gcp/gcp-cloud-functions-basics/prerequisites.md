# Prerequisites — GCP Cloud Functions Basics

Everything you need before **Step 1**.

## Account & billing

- A **Google Cloud account** with a **billing account linked** to your project. Even though this lab
  stays inside the free tier, 2nd-gen functions build with Cloud Build and run on Cloud Run, which
  require billing to be enabled.

## Tools

| Tool | Version | Check | Install |
|------|---------|-------|---------|
| gcloud CLI | ≥ 470 | `gcloud version` | [`gcp-vpc-firewall-basics` Step 1](../../../beginner/gcp/gcp-vpc-firewall-basics/steps/01-install-gcloud.md) or [SETUP.md](../../../../SETUP.md) |
| Python | 3.12 | `python3 --version` | Only for the optional *run locally* part of Step 1 |
| curl | any | `curl --version` | Pre-installed on macOS/Linux; on Windows use `curl.exe` or PowerShell `irm` |

You do **not** need Docker — Google builds the container for you.

## Permissions

On the project you use, your account needs to create functions, schedules, and read logs. The
simplest is **Owner** or **Editor**. The least-privilege set is:

| Role | Why |
|------|-----|
| `roles/cloudfunctions.developer` | Create/update/delete functions |
| `roles/run.admin` | 2nd-gen functions are Cloud Run services under the hood |
| `roles/cloudscheduler.admin` | Create the scheduled job |
| `roles/iam.serviceAccountUser` | Deploy acts as the function's runtime service account |
| `roles/logging.viewer` | Read logs in Step 4 |
| `roles/serviceusage.serviceUsageAdmin` | Enable the APIs in Step 1 |

## Concepts assumed

- Basic command line (running `gcloud`, `curl`, setting an env var)
- You've read the one-paragraph intro to GCP projects/regions in
  [`gcp-vpc-firewall-basics`](../../../beginner/gcp/gcp-vpc-firewall-basics/README.md) — this project
  does **not** repeat the install walkthrough.

## Region

All commands use **`us-east1`** (zone `us-east1-b` where a zone is needed), matching the rest of the
GCP projects in this repo.
