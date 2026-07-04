# Architecture Template

Where a project's Mermaid diagrams live when they're too detailed for the README. All diagrams stay
as **Mermaid code blocks inside Markdown** — no exported images, no `assets/`.

## Which diagrams to include (by level)

| Diagram | Beginner | Intermediate | Advanced |
|---------|:--------:|:------------:|:--------:|
| High-level architecture | ✅ | ✅ | ✅ |
| Request flow | ✅ | ✅ | ✅ |
| Network flow | — | ✅ | ✅ |
| Deployment flow | — | ✅ | ✅ |
| Monitoring flow | — | ✅ | ✅ |
| Security / IAM flow | if relevant | ✅ | ✅ |
| CI/CD flow | — | if relevant | ✅ |
| Failure / recovery flow | — | — | ✅ |
| Scaling flow | — | — | ✅ |
| Cost / cleanup flow | — | — | if relevant |

Each diagram gets **one sentence before** (what it shows) and **one takeaway after** (what to
remember when building it).

---

# Architecture — <Project Title>

## High-level architecture

What it shows: the major components and how traffic moves between them.

```mermaid
flowchart LR
    User((User)) --> LB[Load Balancer]
    LB --> App[Compute tier]
    App --> DB[(Database)]
    App --> Obs[Logs / Metrics]
```

Takeaway: …

## Network flow

What it shows: subnets, gateways, and what can reach what.

```mermaid
flowchart TB
    subgraph VPC
      subgraph Public
        ALB[ALB]
        NAT[NAT Gateway]
      end
      subgraph Private
        EC2[App instances]
      end
    end
    Internet((Internet)) --> ALB --> EC2
    EC2 --> NAT --> Internet
```

Takeaway: …

## Deployment flow

What it shows: how a new version reaches production.

```mermaid
flowchart LR
    Dev[Push to main] --> CI[CI build]
    CI --> Deploy[Deploy]
    Deploy --> Canary[Canary %]
    Canary -->|healthy| Full[100%]
    Canary -->|errors| Rollback[Rollback]
```

Takeaway: …

## Monitoring flow

What it shows: how signals become alerts.

```mermaid
flowchart LR
    App --> Metrics[CloudWatch Metrics]
    Metrics --> Alarm[Alarm]
    Alarm --> SNS[SNS topic]
    SNS --> Email[Email/Slack]
```

Takeaway: …

## Failure / recovery flow (advanced)

What it shows: what happens when a component dies and how the system heals.

```mermaid
flowchart TD
    Healthy[Healthy] -->|instance fails| Detect[Health check fails]
    Detect --> Replace[ASG/MIG replaces instance]
    Replace --> Healthy
```

Takeaway: …

## Cleanup flow

What it shows: the safe teardown order (usually front-to-back).

```mermaid
flowchart LR
    A[Delete forwarding rule / LB] --> B[Delete compute / ASG]
    B --> C[Delete network] --> D[Delete IAM roles]
```

Takeaway: delete in reverse-dependency order so nothing is left orphaned and billing stops.
