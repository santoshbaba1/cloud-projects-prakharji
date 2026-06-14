# Step 6 — Canary Deployment (Hold a Small Weight, Watch, Promote)

**Goal:** release v2 to a *small, steady* fraction of traffic and **leave it there** while you
watch its CloudWatch metrics. Only when the canary looks healthy do you promote it to 100%. A
canary is really "a rolling deploy that pauses at a low percentage and waits for a signal."

**Mechanism (native):** the same weighted alias as Step 5 — the difference is *intent and
duration*. Rolling marches to 100%; canary holds at (say) 10% long enough to compare error
rate and latency between v1 and v2, then promotes or aborts.

> The HTTP API has no gateway-level canary (Project 1's REST API did). So this is alias
> weighting used deliberately. Start clean: `live → version 1`
> (`aws lambda update-alias --function-name tasks-api --name live --function-version 1 --routing-config '{}'`).

---

## 6.1 Start the Canary (10%, held)

```bash
REGION=us-east-1
aws lambda update-alias --function-name tasks-api --name live \
  --function-version 1 --routing-config '{"AdditionalVersionWeights":{"2":0.10}}' --region $REGION
```

Now drive some traffic so there are metrics to read:

```bash
API=https://abc123.execute-api.us-east-1.amazonaws.com
for i in $(seq 1 50); do curl -s $API/tasks -o /dev/null; done
```

---

## 6.2 Compare the Two Versions' Metrics

Lambda publishes metrics **per version** when you use a qualified resource. Compare `Errors`
and `Duration` for `:1` vs `:2` over the canary window:

```bash
REGION=us-east-1
START=$(date -u -d '15 min ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-15M +%Y-%m-%dT%H:%M:%SZ)
END=$(date -u +%Y-%m-%dT%H:%M:%SZ)

for V in 1 2; do
  echo "version $V errors:"
  aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Errors \
    --dimensions Name=FunctionName,Value=tasks-api Name=Resource,Value=tasks-api:$V \
    --start-time $START --end-time $END --period 300 --statistics Sum \
    --query 'Datapoints[].Sum' --output text --region $REGION
done
```

Console: **CloudWatch → Metrics → Lambda → By Resource** → filter `tasks-api:2` and compare
its `Errors`/`Duration` to `tasks-api:1`. (Also watch **DynamoDB** metrics if v2 changed data
access.)

> This is the whole value of a canary: real production traffic on v2, but only a little of it,
> with a side-by-side metric comparison before you commit.

---

## 6.3 Promote or Abort

**Promote** — v2 healthy, make it primary at 100%:

```bash
aws lambda update-alias --function-name tasks-api --name live \
  --function-version 2 --routing-config '{}' --region $REGION
```

**Abort** — v2 looks bad, send everything back to v1:

```bash
aws lambda update-alias --function-name tasks-api --name live \
  --function-version 1 --routing-config '{}' --region $REGION
```

Either way it's one command and takes effect on the next request.

---

## Rolling vs Canary — same tool, different discipline

| | Rolling (Step 5) | Canary (this step) |
|---|---|---|
| Weight progression | Marches 10→50→100 | Holds at ~10% |
| Decision driver | Time / your patience | A **metric comparison** (v1 vs v2) |
| Mechanism | Weighted alias | Weighted alias (identical) |
| Outcome | Promote by reaching 100% | Promote *or* abort based on the signal |

> Automating "watch the canary metric, then promote or abort" is exactly what AWS CodeDeploy's
> canary hooks do. Challenge 4 has you script it with Boto3.

---

## Checkpoint

- [ ] Held a 10% canary on v2 and drove traffic through it
- [ ] Compared `Errors`/`Duration` for `tasks-api:2` vs `tasks-api:1`
- [ ] Promoted (live → v2) **or** aborted (live → v1)
- [ ] Reset to `live → version 1` before the next step

---

**Next:** [Step 7 — Blue-Green Deployment](./07-blue-green-deployment.md)
