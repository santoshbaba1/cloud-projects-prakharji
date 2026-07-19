# Costs — GCP Event-Driven Functions

This lab is **effectively free** if you clean up the same day. Nothing here has a per-hour "always on"
charge — everything is per-use and scales to zero.

## Per-service breakdown

| Service | What you use | Free tier | Lab cost |
|---------|--------------|-----------|----------|
| **Cloud Functions (2nd gen)** | ~dozens of sub-second invocations | 2M invocations + 400k GB-sec/month | **$0** |
| **Cloud Build** | 2–3 buildpack builds (one per function per deploy) | 120 build-min/day | **$0** |
| **Cloud Run** | the functions' runtime | generous free grant; idle = $0 | **$0** |
| **Cloud Storage** | a few tiny JSON objects | 5 GB-months + free ops in-region | **$0** |
| **Eventarc** | event routing | no separate charge (rides Pub/Sub) | **$0** |
| **Pub/Sub** | a handful of small messages | first 10 GB/month | **$0** |
| **Firestore** | a few docs + increments | 1 GiB storage, 50k reads / 20k writes / 20k deletes per **day** | **$0** |
| **Cloud Logging** | a few KB | 50 GiB/month | **$0** |

**Typical session cost: $0.00.**

## Where charges *would* appear if you left it running

- **A retry/upload loop.** If a misconfigured client uploads in a tight loop, or a poison event
  without a dead-letter policy retries forever, you'd accrue Functions invocations and Firestore
  writes. The **max-instances** cap (5) and the DLQ from Step 6 bound this.
- **Large objects.** This lab uses tiny JSON files. Processing large media would add Storage egress
  and longer function runtime.
- **Firestore beyond the daily free quota.** High-volume writes exceed the 20k/day free writes.

## Cost hygiene

- Keep `--max-instances` set so a runaway trigger can't scale without bound.
- Delete the bucket in cleanup — a lingering inbox that something writes to keeps firing the pipeline.
- If you created a dedicated project, `gcloud projects delete` is the surest zero-cost outcome.
