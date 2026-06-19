# Challenges — EC2 Compute Rightsizing

Extend the optimizer. These build on what you deployed.

---

## Challenge 1 — Stop the Idle, Don't Just Shrink It

Right now `idle` instances get a "shrink one size" recommendation, but the real win is to **stop**
them. Add an `IDLE_ACTION` env var (`report` / `stop`) so that when an instance is `idle` and
`APPLY`/`DRY_RUN` allow it, the function **stops** (not resizes) it. Reuse the tag gate. Compare
the savings: stopping a `t3.large` saves 100% of compute; shrinking to `t3.medium` saves ~50%.

---

## Challenge 2 — Let Compute Optimizer Decide, Lambda Apply

Replace the CPU-only `_classify` logic with a call to
`compute-optimizer get-ec2-instance-recommendations`. Read each instance's `finding` and top
`recommendationOptions[0].instanceType`, then apply it with the same stop→modify→start path. Now
you have the production pattern from [Step 5](steps/05-compute-optimizer.md): managed
recommendations, your automation. Add `compute-optimizer:GetEC2InstanceRecommendations` to the
role.

---

## Challenge 3 — Memory-Aware Rightsizing

CPU alone misses memory-bound workloads. Install the **CloudWatch agent** on an instance to emit
`mem_used_percent`, then factor memory into `_classify` (don't downsize if memory is hot even when
CPU is cold). Discuss why memory is the metric Compute Optimizer most often needs the agent for.

---

## Challenge 4 — Savings Estimate in the Report

Add a rough **monthly savings** column to the SNS report. Hard-code an on-demand hourly price map
(or call the Pricing API) and compute `(current_price - recommended_price) * 730` per instance.
Sum it for a headline number: *"Rightsizing these 4 instances saves ~$112/month."* Numbers move
managers more than findings.

---

## Challenge 5 — Approval Workflow Instead of Auto-Apply

Auto-applying resizes on a schedule scares most teams. Re-wire it: the scheduled run only
*reports* and publishes each recommendation to an SNS topic; a human approves by invoking a second
"apply" Lambda with the instance ID. Bonus: drive the approval from an email link via API Gateway.

---

## Challenge 6 — Multi-Region Sweep

Today the function only sees `us-east-1`. Make it loop over a `REGIONS` list, creating a regional
EC2/CloudWatch client per region, and aggregate one combined report. Discuss the IAM and rate
implications of an account-wide sweep.

---

## Challenge 7 — Right-Sizing Decision Guide (No Code)

Write a one-page guide: *when do you shrink, when do you stop, when do you switch families (e.g.
`m5` → `t3` for bursty workloads), and when do you move to Graviton (`t4g`/`m7g`)?* Cover the
trade-offs of burstable credits, Savings Plans, and the operational risk of changing types under
live traffic.
