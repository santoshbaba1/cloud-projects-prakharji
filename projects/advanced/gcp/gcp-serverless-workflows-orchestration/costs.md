# Costs — GCP Serverless Orchestration

This is the **one serverless project in the track with a non-free component**: **API Gateway has no
free tier**. The cost is still tiny for a lab (pennies), but unlike the beginner/intermediate
projects it isn't strictly $0.

## Per-service breakdown

| Service | What you use | Free tier | Lab cost |
|---------|--------------|-----------|----------|
| **Cloud Workflows** | ~dozens of executions, a few steps each | 5,000 internal steps/month | **$0** |
| **Cloud Functions (2nd gen)** | five functions, sub-second invocations | 2M invocations/month | **$0** |
| **Cloud Tasks** | a handful of shipping tasks | 1M operations/month | **$0** |
| **API Gateway** | a few `POST /orders` calls | **none** — ~$3.00 per **million** calls | **< $0.01** for the lab |
| **Cloud Build** | buildpack builds (one per function per deploy) | 120 build-min/day | **$0** |
| **Cloud Run** | the functions' runtime | generous free grant; idle = $0 | **$0** |
| **Cloud Logging** | structured logs | 50 GiB/month | **$0** |

**Typical session cost: under $0.50**, dominated by nothing in particular — API Gateway per-call
charges are fractions of a cent for a handful of test requests.

## Where charges *would* appear if you left it running

- **API Gateway** bills per call. A left-running gateway that something hammers (a bot finding the
  public URL, a stuck client retry loop) is the realistic cost risk here — another reason the
  cleanup step deletes it and Challenge 4 adds an API key.
- **Cloud Workflows** beyond 5,000 steps/month bills per step — only relevant at real volume.
- **Cloud Tasks** beyond 1M ops/month — not reachable in a lab.

## Cost hygiene

- **Delete the gateway** (Step 8.1) — it's the only no-free-tier resource.
- Keep `--max-instances` on every function so a runaway can't scale without bound.
- Don't leave the public `/orders` endpoint open long; add auth (Challenge 4) if you keep it.
- If you created a dedicated project, `gcloud projects delete` guarantees a zero-cost end state.
