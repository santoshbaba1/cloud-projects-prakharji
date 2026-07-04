# Core Concepts — Designing Architecture

---

## Architecture Design Principles

Each principle is given technically, in plain language, with a real-world analogy and an
architecture example. These are the vocabulary of every design review.

| Principle | Technical | Layman | Real-world analogy | Architecture example |
| --- | --- | --- | --- | --- |
| **Simplicity** | Prefer the least complex design that meets the requirements; complexity is a cost you pay forever. | Don't build a maze when a hallway will do. | A house with sensible rooms, not 40 secret passages. | One service and one database for a small app — not 12 microservices. |
| **Scalability** | Ability to handle more load by adding resources. | It grows to meet demand. | A stadium that opens more gates at rush. | Add app instances behind a load balancer as traffic rises. |
| **Reliability** | Performs correctly and consistently, and recovers from failure. | You can count on it. | A car that starts every morning. | Retries, health checks, and automatic replacement of failed nodes. |
| **Availability** | The share of time the system is up and reachable (e.g. 99.95%). | How rarely it's down. | A 24/7 pharmacy. | Run across ≥2 failure zones so one outage doesn't take you down. |
| **Fault tolerance** | Keeps working *correctly* despite component failures, often with zero impact. | Nothing breaks even when something breaks. | A plane that flies on one engine. | Redundant instances; a failed one is simply not routed to. |
| **Resilience** | Absorbs disruption and recovers, possibly in a degraded mode. | It bends instead of snapping. | A shop staying open on one till. | If recommendations fail, the page still loads without them. |
| **Security** | Protects confidentiality, integrity, availability of data and systems. | Keeps the bad guys out and the data safe. | A bank with guards, vaults, and cameras. | Least privilege, encryption, segmentation (Module 10). |
| **Performance** | Meets latency/throughput targets efficiently. | It's fast enough, using resources well. | Express lanes at rush hour. | Cache hot data; put a CDN in front; size resources to the workload. |
| **Cost optimization** | Delivers value at the lowest sustainable price. | Don't pay for what you don't use. | Turning off lights in empty rooms. | Elastic scaling, right-sizing, cheaper storage tiers for cold data. |
| **Maintainability** | Easy to understand, change, and operate safely. | Easy to fix and improve. | A car designed so the mechanic can reach the parts. | Clear boundaries, IaC, good logs, small reversible changes. |
| **Extensibility** | New capabilities can be added without rewrites. | Room to grow and add features. | A house pre-plumbed for a future extension. | Add a new consumer to an event stream without touching producers. |
| **Observability** | You can understand internal state from outputs (metrics, logs, traces). | You can see what's going on inside. | A dashboard of dials in a cockpit. | Metrics + structured logs + distributed traces on every service. |
| **Recoverability** | Can be restored to a good state after failure or corruption. | You can get back up after disaster. | Fireproof safe with copies of documents. | Tested backups, DR plan, defined RTO/RPO (Module 8). |
| **Automation** | Provision and operate via code, not manual steps. | Robots do the repetitive work, the same way every time. | A factory line, not hand assembly. | IaC builds environments; alarms trigger auto-remediation. |
| **Loose coupling** | Components interact via stable interfaces/queues so one's failure doesn't cascade. | Parts talk via an inbox, not by leaning on each other. | Departments using internal mail. | A queue between web tier and workers; workers can be down, orders still queue. |
| **High cohesion** | Each component has one clear, focused responsibility. | One thing, done well, in one place. | A kitchen where the cook cooks and the cashier takes money. | A "payments" service owns *only* payments and its data. |
| **Stateless design** | App instances keep no local session state; any instance serves any request. | Any cashier can serve any customer. | Hot-desking — no fixed desks. | Sessions in a shared cache/DB, so instances are interchangeable. |
| **Idempotency** | Doing the same operation twice has the same effect as once. | Pressing the lift button twice doesn't summon two lifts. | A door that's already locked stays locked when you lock it again. | A payment with an idempotency key won't double-charge on retry. |
| **Event-driven design** | Components react to events asynchronously rather than calling each other directly. | Things happen by reacting to notifications. | A restaurant order rail the kitchen works through. | "Order placed" event fans out to inventory, email, and analytics. |

> **Principles interact — why it works this way:**
> - Statelessness *enables* horizontal scaling; loose coupling *enables* resilience and
>   independent deploys; idempotency *makes* retries (hence reliability) safe.
> - They reinforce one another — *which is why* violating one quietly breaks others: keep
>   session state on the instance and you can no longer scale or replace instances freely.

---

## Architecture Building Blocks

Almost every system, anywhere, is assembled from the same generic blocks. Learn the *roles*;
the vendor product is just an implementation.

| Block | Role (technical) | Layman | Where it fits | AWS / Azure / GCP / K8s example |
| --- | --- | --- | --- | --- |
| **Users** | The actors and clients that generate demand and define requirements. | The people the system is for. | The source of every request and requirement. | Browsers, mobile apps, partner systems. |
| **Applications** | The code implementing business logic. | The thing that does the work. | The core; everything else supports it. | A service running on VMs, containers, or functions. |
| **APIs** | Stable contracts through which components/clients interact. | The menu of what you can ask for. | Boundary between clients and services, and between services. | REST/gRPC; API Gateway / APIM / Apigee; K8s Service. |
| **Compute** | Where code runs. | The engines. | Runs the applications. | EC2 / VMs / Compute Engine; containers; Lambda / Functions / Cloud Functions. |
| **Storage** | Durable storage for files/objects/blocks. | The warehouse and the disks. | Holds files, backups, artifacts, data lakes. | S3 / Blob / GCS; EBS / Managed Disks / PD; EFS / Files / Filestore. |
| **Databases** | Structured, queryable data with integrity guarantees. | The organised filing cabinets. | The system of record. | RDS/Aurora / SQL DB / Cloud SQL; DynamoDB / Cosmos / Firestore. |
| **Networks** | Connectivity, isolation, and routing. | The roads, gates, and walls. | Connects and isolates everything. | VPC/VNet/VPC; subnets; firewalls/security groups; peering. |
| **Security** | Identity, access, encryption, and protection controls. | The ID cards, guards, and vaults. | Cross-cutting, at every layer. | IAM / Entra ID / Cloud IAM; KMS; secrets managers; WAF. |
| **Monitoring** | Metrics and alerting on health and performance. | The dials and the alarm bell. | Cross-cutting; feeds operations. | CloudWatch / Monitor / Cloud Monitoring; Prometheus. |
| **Logging** | Recording events for debugging, audit, and analysis. | The diary of everything that happened. | Cross-cutting; feeds troubleshooting and audit. | CloudWatch Logs / Log Analytics / Cloud Logging; ELK; Loki. |
| **Messaging** | Asynchronous communication between components. | The internal postal/queue system. | Decouples producers from consumers. | SQS/SNS / Service Bus / Pub-Sub; Kafka; RabbitMQ. |
| **Caching** | Fast storage of frequently used data to cut latency/load. | A notepad of answers you reuse. | In front of databases and services; at the edge. | ElastiCache / Cache for Redis / Memorystore; CDN edge cache. |
| **DNS** | Maps names to addresses; entry point and routing/failover control. | The phone book and the switchboard. | The front door; enables failover and global routing. | Route 53 / Azure DNS / Cloud DNS. |
| **Load balancing** | Distributes traffic across healthy instances. | A greeter sending you to a free counter. | In front of every horizontally-scaled tier. | ALB/NLB / Load Balancer / Cloud LB; K8s Service + Ingress. |

**Layman:** these blocks are like the standard parts of *any* building — doors, walls,
wiring, plumbing, a reception desk. Whether it's a cottage or a hospital, you compose the
same kinds of parts; architecture is choosing *which*, *how many*, and *how they connect*.

---

## Architecture Patterns

For each pattern: a one-line **what**, **benefits**, **drawbacks**, **use cases**, and
crucially **when NOT to use it**.

### Monolithic
**What:** the whole application is one deployable unit sharing one codebase and usually one
database.

| Benefits | Drawbacks | Use cases | When NOT to use |
| --- | --- | --- | --- |
| Simple to build, test, deploy; fast locally; no network between parts | Scales as one block; one bug can sink all of it; large teams step on each other | New products, small teams, MVPs, most apps at the start | Very large teams needing independent deploys; parts with wildly different scaling |

### Layered
**What:** code organised into horizontal layers (e.g. presentation → business → data), each
only talking to the layer below.

| Benefits | Drawbacks | Use cases | When NOT to use |
| --- | --- | --- | --- |
| Clear separation of concerns; easy to understand and test | Can become rigid; a request often traverses every layer | Most business applications; default internal structure of a monolith | Ultra-low-latency paths where extra layers cost too much |

### N-Tier
**What:** layers deployed as separate *physical* tiers (web tier, application tier, database
tier), each independently scalable.

| Benefits | Drawbacks | Use cases | When NOT to use |
| --- | --- | --- | --- |
| Each tier scales/secures independently; classic HA shape | Network hops between tiers; more infrastructure to run | Traditional web apps; the canonical HA web app | Tiny apps where one box suffices; pure event/serverless workloads |

### Service-Oriented (SOA)
**What:** business capabilities exposed as coarse-grained, reusable services, classically
integrated via an enterprise service bus (ESB).

| Benefits | Drawbacks | Use cases | When NOT to use |
| --- | --- | --- | --- |
| Reuse across the enterprise; integrates heterogeneous systems | The ESB can become a bottleneck/SPOF; heavyweight governance | Large enterprises integrating many legacy systems | Small/greenfield apps; teams wanting lightweight, independent services (prefer microservices) |

### Microservices
**What:** the app is split into small, independently deployable services, each owning its
data, usually communicating over the network.

| Benefits | Drawbacks | Use cases | When NOT to use |
| --- | --- | --- | --- |
| Independent deploy/scale; team autonomy; fault isolation; tech freedom | Distributed-systems complexity; network latency; data consistency; heavy ops/observability needs | Large apps and orgs; parts with very different scaling needs | Small teams/apps; early-stage products (premature microservices kill startups) |

### Event-Driven
**What:** components communicate by emitting and reacting to **events**, asynchronously,
through a broker or queue.

| Benefits | Drawbacks | Use cases | When NOT to use |
| --- | --- | --- | --- |
| Loose coupling; absorbs spikes; easy to add consumers; resilient | Eventual consistency; harder end-to-end tracing/debugging | Order/notification pipelines, IoT, decoupling slow work | Simple request/response flows needing an immediate, consistent answer |

### Serverless
**What:** run functions/managed services with no servers to provision; scales to zero and to
massive automatically.

| Benefits | Drawbacks | Use cases | When NOT to use |
| --- | --- | --- | --- |
| No servers/patching; pay-per-use; auto-scale incl. to zero | Cold starts; runtime limits; potential lock-in; pricey at very high steady volume | Spiky/low traffic, glue, event processing, fast-moving teams | Sustained high-throughput, long-running, or latency-critical hot paths |

### Container
**What:** package each app with its dependencies into a portable container; run many per
host.

| Benefits | Drawbacks | Use cases | When NOT to use |
| --- | --- | --- | --- |
| Consistent across environments; dense, fast startup; portable | You still need orchestration/networking/storage solved | Almost any modern service; the unit microservices ship in | Trivial scripts; cases where managed serverless is simpler |

### Kubernetes
**What:** a declarative orchestration platform that runs containers across a cluster,
keeping the actual state matching your desired state (Module 7).

| Benefits | Drawbacks | Use cases | When NOT to use |
| --- | --- | --- | --- |
| Self-healing, scaling, rollout/rollback; portable; huge ecosystem | Steep learning curve; real operational overhead; easy to over-adopt | Many services, platform teams, multi-cloud portability | Small apps/teams where managed PaaS or serverless is cheaper to run |

### Hybrid
**What:** workloads span on-premises/data-centre **and** cloud, connected as one system.

| Benefits | Drawbacks | Use cases | When NOT to use |
| --- | --- | --- | --- |
| Use existing data-centre investment; keep sensitive data on-prem; gradual migration | Network complexity/latency; two operating models; harder security | Regulated industries; mid-migration; data-gravity constraints | Greenfield with no on-prem need (added complexity for nothing) |

### Multi-Cloud
**What:** workloads deliberately spread across two or more cloud providers.

| Benefits | Drawbacks | Use cases | When NOT to use |
| --- | --- | --- | --- |
| Avoid lock-in; provider-outage resilience; use each cloud's strengths; leverage in negotiation | Lowest-common-denominator designs; double the expertise/tooling; data egress costs | Strict resilience/regulatory mandates; very large orgs | Most teams — the complexity rarely pays for itself; prefer portability over active multi-cloud |

> **Pattern selection is itself a trade-off — why it works this way:**
> - The honest default for a new system is the **simplest pattern** that meets the
>   requirements — often a well-structured monolith.
> - You earn your way to microservices / Kubernetes / multi-cloud only when concrete
>   requirements demand them — *because* each adds complexity you pay for forever.

---

## Cloud Architecture Principles

Cloud changes *economics and capabilities*, which unlocks principles that are hard on-prem.

| Principle | Technical | Layman | AWS / Azure / GCP realisation |
| --- | --- | --- | --- |
| **Elasticity** | Capacity grows and shrinks automatically with demand. | Hire staff for the lunch rush, send them home after. | Auto Scaling groups / VM Scale Sets / Managed Instance Groups; serverless scale-to-zero. |
| **On-demand infrastructure** | Provision resources in minutes via API; pay as you go. | Rent tools by the hour instead of buying a workshop. | Self-service APIs/CLIs across all three; no capacity purchase up front. |
| **Shared responsibility** | The provider secures *of* the cloud; you secure *in* the cloud. The line shifts with how managed the service is. | Landlord secures the building; you lock your flat and decide who gets a key. | AWS / Azure / GCP shared-responsibility models — all the same shape. |
| **Immutable infrastructure** | Never modify running servers; replace them with new versions built from images. | Don't repair the appliance — swap in a new identical one. | Bake AMIs / managed images / instance templates; redeploy rather than patch in place. |
| **Infrastructure as Code (IaC)** | Define infrastructure in version-controlled code; provisioning is reproducible. | The blueprint *is* the build instructions, kept in version control. | CloudFormation / Terraform / Bicep / Deployment Manager; Terraform spans all three. |
| **Automation first** | Prefer automated provisioning, deployment, and remediation over manual steps. | Robots do the repetitive work, the same way every time. | Pipelines + IaC + auto-remediation across all providers. |
| **Design for failure** | Assume every component will fail; make recovery automatic. | Build assuming storms come. | Multi-AZ/zone deployments, health checks, auto-replacement everywhere. |
| **Distributed systems** | Components run on many machines/zones and communicate over an unreliable network. | A team spread across buildings who must coordinate by message. | Multi-AZ data stores, quorum/replication, retries with backoff. |

**Layman:** the cloud's superpower is that **infrastructure becomes software** — you can
create, destroy, and duplicate it with code in minutes. That makes elasticity,
immutability, and "design for failure" *practical* instead of aspirational. The three big
clouds implement the same principles with different product names; an architect who knows
the principles reads any of them quickly.

> **Distributed-systems reality (the fallacies) — why it works this way:**
> - The network is *not* reliable, latency is *not* zero, bandwidth is *not* infinite, and
>   topology *changes*.
> - Cloud designs that ignore this fail in production.
> - So retries, timeouts, idempotency, and loose coupling are not optional extras — they are
>   how distributed systems survive an unreliable network.

---

## Kubernetes Architecture Principles

Concepts, not `kubectl`. Kubernetes is the canonical example of **declarative, desired-state,
self-healing** architecture — worth understanding even if you never run it yourself.

| Concept | Technical | Layman |
| --- | --- | --- |
| **Control plane** | The brain: API server (front door), scheduler (placement), controller manager (drives actual→desired), etcd (the state store). | The air-traffic control tower deciding what runs where. |
| **Worker nodes** | Machines that actually run workloads; each runs a kubelet (agent) and a container runtime. | The runways and gates where planes (containers) actually sit. |
| **Pods** | The smallest deployable unit — one or more tightly-coupled containers sharing network/storage. | A crew that always travels together. |
| **Services** | A stable virtual address and load balancer over a changing set of pods. | A front desk phone number that always reaches *a* free agent. |
| **Ingress** | Rules routing external HTTP(S) traffic to services (host/path based). | The building's main entrance and signage directing visitors. |
| **Scheduling** | The scheduler places pods on nodes by resource needs, affinity, and constraints. | Seating guests by table size and special requests. |
| **Self-healing** | Controllers continuously replace failed pods/nodes to maintain desired state. | If a crew calls in sick, a replacement is dispatched automatically. |
| **Horizontal scaling** | The HPA adds/removes pod replicas based on metrics like CPU or custom signals. | Open more counters when the queue grows. |
| **Declarative configuration** | You declare the *desired* end state (YAML), not the steps to get there. | Order "a table for four by the window," not "pull out chair, then…". |
| **Desired-state management** | The system constantly reconciles actual state toward the declared desired state. | A thermostat: set 21°C and it keeps adjusting to hold it. |
| **GitOps** | Git is the single source of truth for desired state; an agent reconciles the cluster to match Git. | The master plan lives in one binder; the building is kept matching the binder. |

**Layman:** the big idea is the **thermostat, not the light switch**. A light switch is
imperative — *you* turn it on, and if it trips you must flip it again. A thermostat is
declarative — you state the goal (21°C) and the system *keeps* achieving it despite
disturbances. Kubernetes (and GitOps) apply the thermostat model to whole systems: declare
"5 healthy replicas of this service," and the platform relentlessly makes it true. The
architectural lesson generalises far beyond Kubernetes: **prefer declaring desired state and
letting the system reconcile, over scripting fragile step-by-step procedures.**

---

## Reliability Engineering

Designing so the system stays up and recovers.

| Concept | Technical | Layman |
| --- | --- | --- |
| **Single Point of Failure (SPOF)** | A component whose failure takes the whole system down. | The one weak link that breaks everything. |
| **Redundancy** | Duplicate components so the system survives losing one. | A spare tyre. |
| **Active/Passive** | One node serves; a standby waits and takes over on failure (failover). | A backup generator that starts when the grid fails. |
| **Active/Active** | All nodes serve simultaneously; losing one just removes capacity. | Two tills both open — if one breaks, the other keeps serving. |
| **Health checks** | Periodic probes that decide if a target is healthy enough to receive traffic. | A pulse check before sending customers to a counter. |
| **Auto-healing** | Automatic replacement of failed components to restore desired state. | A sick worker is automatically replaced. |
| **Backup** | Periodic copies of data to restore after loss/corruption. | Photocopies in a fireproof safe. |
| **Disaster Recovery (DR)** | The plan/strategy to recover after a major outage (e.g. a region failure). | The "everything's on fire" playbook. |
| **RTO** | Recovery Time Objective — max acceptable downtime. | How long until the lights come back on. |
| **RPO** | Recovery Point Objective — max acceptable data loss, in time. | How many minutes of work you'd redo. |

**Active/Passive vs Active/Active (a core decision) — why it works this way:**
- Passive is cheaper and simpler but wastes the standby and recovers more slowly (failover
  time).
- Active/active uses all capacity and recovers near-instantly but is harder — *because* data
  must stay consistent across all actives.
- Choose by what an hour of downtime costs the business.

**DR strategies on a spectrum (cheap/slow → costly/instant) — why it works this way:**
- The four strategies sit on one axis of cost versus recovery speed:
  - **Backup & Restore** — rebuild from backups, RTO hours.
  - **Pilot Light** — core kept warm, scale up on disaster, RTO tens of minutes.
  - **Warm Standby** — small live copy, scale up, RTO minutes.
  - **Multi-Site Active/Active** — full duplicate serving traffic, RTO near-zero.
- Each step buys faster recovery and less data loss *because* it pays to keep more
  idle/duplicated capacity running before disaster.
- Match the strategy to RTO/RPO targets, which the business sets from cost-of-downtime.

---

## Scalability Design

Designing so the system handles more load. Real-world examples throughout.

| Technique | Technical | Layman | Real-world example |
| --- | --- | --- | --- |
| **Vertical scaling (scale up)** | Give one node more CPU/RAM. | A bigger machine. | Move the database to a larger instance — quick, but there's a ceiling and it's a SPOF. |
| **Horizontal scaling (scale out)** | Add more nodes and share load. | More machines, more lanes. | Add web servers behind a load balancer as traffic grows — near-limitless if stateless. |
| **Auto scaling** | Add/remove capacity automatically on metrics. | Open and close counters as the queue changes. | Scale out for a flash sale, back down overnight to save money. |
| **Caching** | Store hot data in fast memory to avoid recomputing/refetching. | A notepad of answers you reuse. | Cache product details so 90% of reads never hit the database. |
| **Load balancing** | Spread requests across healthy instances. | A greeter routing you to a free counter. | An LB across instances in two zones; unhealthy ones get no traffic. |
| **Database scaling** | Scale the data tier (often the hardest part). | Make the filing system keep up. | Combine read replicas, caching, and sharding (below). |
| **Read replicas** | Read-only copies of the database serve read traffic. | Extra reference copies of the ledger for lookups. | Send reporting/read queries to replicas; keep writes on the primary. |
| **Sharding** | Partition data across multiple databases by a key. | Split the phone book A–M and N–Z into two cabinets. | Shard users by user-id so no single database holds all of them. |

**Why the database is usually the bottleneck — why it works this way:**
- The stateless app tier scales out easily — just add instances.
- The **stateful** database does not — *because* all that data has to live *somewhere
  consistent*.
- So scalable designs push work *off* the database: **cache** reads, offload reads to
  **replicas**, and only when those aren't enough, **shard** writes (which adds cross-shard
  queries and rebalancing).
- The ordered playbook is **cache → replicas → shard** — in that order *because* each later
  step costs more complexity.

**Layman:** scaling a system is like scaling a restaurant. Adding waiters (app servers) is
easy. The bottleneck is the single kitchen (the database): first you add a prep notepad
(cache), then a second reference kitchen for lookups only (read replicas), and only if truly
necessary do you build separate kitchens each handling different tables (sharding).

---

## Security by Design

Security is **designed in, not bolted on** — and it is everyone's concern, at every layer.

| Concept | Technical | Layman | Architecture example |
| --- | --- | --- | --- |
| **Least privilege** | Grant only the permissions actually needed, nothing more. | Only the keys you truly need. | A service can read *its* bucket only — not every bucket. |
| **Defence in depth** | Multiple independent layers of control, so one breach isn't game over. | Moat *and* walls *and* guards *and* a vault. | WAF + network segmentation + auth + encryption + least-privilege IAM. |
| **Authentication (authn)** | Verifying *who* a caller is. | Checking ID at the door. | OIDC/SAML login; service identities for machine-to-machine. |
| **Authorization (authz)** | Deciding *what* an authenticated caller may do. | Which doors that ID opens. | Role-based / attribute-based access control on every API. |
| **Encryption** | Protect data at rest (on disk) and in transit (TLS). | Locked safe + sealed armoured truck. | TLS everywhere; managed keys (KMS) for storage and databases. |
| **Secrets management** | Store/rotate credentials securely, never in code. | A locked key cabinet that also changes the locks on schedule. | Secrets manager + automatic rotation; no passwords in Git. |
| **Network segmentation** | Isolate components into zones so traffic is limited and contained. | Internal walls so a fire in one room doesn't spread. | Public subnet for the LB only; app and DB in private subnets. |
| **Zero trust** | Trust nothing by default; verify every request regardless of network location. | Check everyone's badge at *every* door, even insiders. | Authn+authz on internal service-to-service calls; no "trusted network." |

**Blast radius is the unifying idea — why it works this way:**
- Assume any single layer *will* be breached, and design so the damage is *contained*.
- Least privilege shrinks what a stolen credential can touch; segmentation stops lateral
  movement; defence in depth means no single failure is fatal.

**Layman:** old-style security was a hard shell around a soft centre — get past the front
gate and you own everything (the "trusted internal network"). **Zero trust** says: there is
no soft centre; check everyone's badge at every door, even staff, because attackers who get
inside should still be stopped at the next door. Combined with least privilege and
segmentation, a single compromise becomes a contained incident instead of a catastrophe.

---
