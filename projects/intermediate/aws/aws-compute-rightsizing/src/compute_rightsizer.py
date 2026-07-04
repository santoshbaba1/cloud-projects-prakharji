"""
AWS Compute Rightsizing - Optimization & Recovery Series, Project 1
Runs on a schedule. For each tagged EC2 instance it pulls recent CPU utilization
from CloudWatch, classifies the instance (idle / over-provisioned / right-sized),
and proposes a smaller instance type. It reports the findings to SNS and can
optionally apply a resize (stop -> modify type -> start) when explicitly enabled.

Environment variables:
  TAG_KEY          - only consider instances with this tag key (default "Rightsize")
  TAG_VALUE        - ...and this tag value (default "true")
  LOOKBACK_DAYS    - days of CloudWatch CPU history to inspect (default "1")
  IDLE_THRESHOLD   - max CPU % below this => "idle" / stop candidate (default "5")
  LOW_THRESHOLD    - max CPU % below this => "over-provisioned" (default "40")
  APPLY            - "true" to allow resizing (still gated by DRY_RUN) (default "false")
  DRY_RUN          - "true" to log what would happen without changing anything (default "true")
  SNS_TOPIC_ARN    - if set, publish a summary report to this topic (optional)
"""

import datetime
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client("ec2")
cw = boto3.client("cloudwatch")
sns = boto3.client("sns")

TAG_KEY = os.environ.get("TAG_KEY", "Rightsize")
TAG_VALUE = os.environ.get("TAG_VALUE", "true")
LOOKBACK_DAYS = int(os.environ.get("LOOKBACK_DAYS", "1"))
IDLE_THRESHOLD = float(os.environ.get("IDLE_THRESHOLD", "5"))
LOW_THRESHOLD = float(os.environ.get("LOW_THRESHOLD", "40"))
APPLY = os.environ.get("APPLY", "false").lower() == "true"
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

# One step down within the same family. Only families a beginner is likely to launch.
# Burstable (t2/t3) families are what the free tier and this lab use.
DOWNSIZE = {
    "t3.large": "t3.medium",
    "t3.medium": "t3.small",
    "t3.small": "t3.micro",
    "t2.large": "t2.medium",
    "t2.medium": "t2.small",
    "t2.small": "t2.micro",
}


def handler(event, context):
    instances = _tagged_running_instances()
    logger.info("Inspecting %d instance(s) tagged %s=%s", len(instances), TAG_KEY, TAG_VALUE)

    findings = []
    for inst in instances:
        instance_id = inst["InstanceId"]
        current_type = inst["InstanceType"]
        max_cpu, avg_cpu = _cpu_stats(instance_id)
        finding, recommended = _classify(current_type, max_cpu)

        logger.info(
            "%s type=%s maxCPU=%.1f%% avgCPU=%.1f%% -> %s (recommend %s)",
            instance_id, current_type, max_cpu, avg_cpu, finding, recommended or "-",
        )

        applied = False
        if APPLY and not DRY_RUN and recommended and recommended != current_type:
            _resize(instance_id, recommended)
            applied = True

        findings.append({
            "instance_id": instance_id,
            "current_type": current_type,
            "max_cpu": round(max_cpu, 1),
            "avg_cpu": round(avg_cpu, 1),
            "finding": finding,
            "recommended_type": recommended,
            "applied": applied,
        })

    report = _format_report(findings)
    logger.info(report)
    if SNS_TOPIC_ARN:
        sns.publish(TopicArn=SNS_TOPIC_ARN, Subject="EC2 Rightsizing Report", Message=report)

    return {"dry_run": DRY_RUN, "apply": APPLY, "count": len(findings), "findings": findings}


def _tagged_running_instances():
    paginator = ec2.get_paginator("describe_instances")
    pages = paginator.paginate(Filters=[
        {"Name": f"tag:{TAG_KEY}", "Values": [TAG_VALUE]},
        {"Name": "instance-state-name", "Values": ["running"]},
    ])
    out = []
    for page in pages:
        for reservation in page["Reservations"]:
            out.extend(reservation["Instances"])
    return out


def _cpu_stats(instance_id: str):
    end = datetime.datetime.now(datetime.timezone.utc)
    start = end - datetime.timedelta(days=LOOKBACK_DAYS)
    resp = cw.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start,
        EndTime=end,
        Period=3600,
        Statistics=["Average", "Maximum"],
    )
    points = resp.get("Datapoints", [])
    if not points:
        # No metrics yet (brand-new instance). Treat as unknown, not idle.
        return (float("nan"), float("nan"))
    max_cpu = max(p["Maximum"] for p in points)
    avg_cpu = sum(p["Average"] for p in points) / len(points)
    return (max_cpu, avg_cpu)


def _classify(current_type: str, max_cpu: float):
    if max_cpu != max_cpu:  # NaN => no data
        return ("no-data", None)
    if max_cpu < IDLE_THRESHOLD:
        # Idle: the win is to stop the instance, not just shrink it.
        return ("idle", _down(current_type))
    if max_cpu < LOW_THRESHOLD:
        return ("over-provisioned", _down(current_type))
    return ("right-sized", None)


def _down(current_type: str):
    # Returns the next smaller type in the same family, or None if already smallest
    # / family not in the table (we don't guess across families).
    return DOWNSIZE.get(current_type)


def _resize(instance_id: str, new_type: str):
    logger.info("Resizing %s -> %s (stop, modify, start)", instance_id, new_type)
    ec2.stop_instances(InstanceIds=[instance_id])
    ec2.get_waiter("instance_stopped").wait(InstanceIds=[instance_id])
    ec2.modify_instance_attribute(InstanceId=instance_id, InstanceType={"Value": new_type})
    ec2.start_instances(InstanceIds=[instance_id])
    logger.info("Resize of %s submitted", instance_id)


def _format_report(findings):
    if not findings:
        return f"No running instances tagged {TAG_KEY}={TAG_VALUE}. Nothing to review."
    lines = [
        f"EC2 Rightsizing Report ({'DRY RUN' if DRY_RUN else 'LIVE'}, apply={APPLY})",
        f"Window: last {LOOKBACK_DAYS} day(s). idle<{IDLE_THRESHOLD}% over-prov<{LOW_THRESHOLD}%",
        "",
    ]
    for f in findings:
        rec = f["recommended_type"] or "keep"
        note = " [APPLIED]" if f["applied"] else ""
        lines.append(
            f"- {f['instance_id']} {f['current_type']} "
            f"(maxCPU {f['max_cpu']}%) -> {f['finding']}, recommend: {rec}{note}"
        )
    return "\n".join(lines)
