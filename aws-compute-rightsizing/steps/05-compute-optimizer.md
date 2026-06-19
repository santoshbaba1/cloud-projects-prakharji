# Step 5 — Enable & Compare AWS Compute Optimizer

You just built a rightsizer from raw CloudWatch metrics. AWS sells a managed version of exactly
this: **Compute Optimizer**. It studies up to **14 days** of metrics with ML models, accounts for
memory and network (not just CPU), and proposes specific instance types with projected savings —
no Lambda required.

This step has you enable it and contrast the two approaches. (Recommendations need ~14 days of
history, so a fresh lab account may show "no recommendations yet" — that's expected, and the
comparison of *approaches* is the real lesson.)

---

## 5.1 Opt In

1. **Compute Optimizer** → **Get started** → **Opt in**.
   - Choose **this account only** (not the whole org) for the lab.
2. AWS begins ingesting metrics. Findings for existing instances appear within hours; full
   rightsizing recommendations need ~14 days of data.

```bash
aws compute-optimizer update-enrollment-status --status Active --region us-east-1
aws compute-optimizer get-enrollment-status --region us-east-1
```

---

## 5.2 Read EC2 Recommendations

Once data exists:

1. **Compute Optimizer** → **EC2 instances**. Each instance gets a **finding**:
   `Under-provisioned`, `Over-provisioned`, `Optimized`, or `None`.
2. Open one to see **up to 3 recommended options** with projected CPU/memory headroom and an
   **estimated monthly savings** figure.

```bash
aws compute-optimizer get-ec2-instance-recommendations --region us-east-1 \
  --query 'instanceRecommendations[].{id:instanceArn,finding:finding,current:currentInstanceType,rec:recommendationOptions[0].instanceType}'
```

---

## 5.3 Compare

| Dimension | Your Lambda (Step 3) | Compute Optimizer |
|-----------|----------------------|-------------------|
| Signals used | CPU max/avg only | CPU, memory*, network, EBS, disk |
| History needed | minutes | ~14 days |
| Recommendation | "one size down in family" | specific types across families, ranked |
| Savings estimate | none | dollar figure per option |
| Cost | a few cents (Lambda) | **free** |
| Customizable logic | fully (it's your code) | limited to its knobs |
| Acts on its own | yes (it can resize) | no — recommendations only |

\* memory needs the CloudWatch agent on the instance; without it, Optimizer infers conservatively.

**Takeaway:** Compute Optimizer is the better *recommender* — broader signals, real savings math,
zero code. Your Lambda is the better *actuator* and *teacher* — it shows what's under the hood and
can actually perform the change on a schedule. The production pattern is to **combine** them: let
Compute Optimizer decide, let a Lambda apply (see [Challenge 2](../challenges.md)).

---

## Checkpoint

- [ ] Compute Optimizer enrollment status is **Active**
- [ ] You viewed the EC2 findings page (even if "no recommendations yet")
- [ ] You can state one thing Optimizer sees that your CPU-only Lambda misses (memory/network)
- [ ] You understand why the production pattern is *Optimizer recommends, Lambda applies*

---

**Next:** [Step 6 — Flip the Switch and Resize for Real](./06-apply-rightsizing.md)
