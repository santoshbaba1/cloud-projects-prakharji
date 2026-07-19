# Challenges — GCP Serverless Orchestration

Extend the orchestration. Each is a realistic capability real fulfillment workflows grow.

---

### 1. Parallel steps

The current workflow is strictly sequential. Use a workflow **`parallel`** branch to run
`validate-order` and a new `check-fraud` function **at the same time**, joining before `charge`. Note
how the workflow language expresses fan-out/fan-in and where shared variables must be declared.

---

### 2. A clean fault-injection switch

Step 5.4 forced a post-charge failure by editing the queue name. Do it properly: add a
`"fail_shipping": true` field the workflow checks, and `raise` before the enqueue when set — so you
can trigger **compensation** deterministically with a sample file (`order-fail-ship.json`) and watch
`refund-payment` fire, no YAML edits.

---

### 3. Human-in-the-loop approval (callback)

Insert an approval gate before shipping high-value orders using a Workflows **callback**
(`events.create_callback_endpoint`). The workflow pauses, exposes a callback URL, and resumes when a
manager POSTs approval — the serverless equivalent of a manual approval stage.

---

### 4. Require an API key on the gateway

The public `/orders` endpoint is wide open. Add a `security` definition to `openapi.yaml` requiring an
API key (`x-google-api-key`), create a key, and prove unauthenticated calls now get **401**. This is
the minimum bar for a real public endpoint.

---

### 5. Start the workflow from an event instead of HTTP

Combine this with the [intermediate project](../../../intermediate/gcp/gcp-event-driven-functions-pubsub/README.md):
trigger `order-fulfillment` from a **Pub/Sub message** or a **GCS upload** via Eventarc, instead of
API Gateway. Now you have choreography *into* orchestration — reflect on when that composition makes
sense.

---

### 6. Persist order state in Firestore

Have each step write its progress (`validated`, `charged`, `shipped`, `refunded`) to a Firestore
`orders/{id}` document, so the current state of every order is queryable independent of the workflow
execution history. Reuse the Firestore setup from the intermediate project.

---

### 7. Add a timeout and dead-letter for stuck shipments

Give `shipping-worker` an artificial delay and configure the Cloud Tasks queue's `maxAttempts` +
worker timeout so a permanently-failing shipment is abandoned cleanly. Add alerting (a log-based
metric + Monitoring alert) for tasks that exhaust their retries.
