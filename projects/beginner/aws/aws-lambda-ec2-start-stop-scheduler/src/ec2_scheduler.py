"""
Lambda EC2 Start/Stop Scheduler - Lambda Automation Series, Project 2
Starts or stops EC2 instances that carry a specific tag, based on the action
passed in the event. Wire two EventBridge schedules to it:
  {"action": "stop"}  in the evening
  {"action": "start"} in the morning

Environment variables:
  TAG_KEY    - tag key that opts an instance in (default "AutoPower")
  TAG_VALUE  - required tag value (default "true")
  DRY_RUN    - "true" to log what would happen without changing anything
"""

import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client("ec2")

TAG_KEY = os.environ.get("TAG_KEY", "AutoPower")
TAG_VALUE = os.environ.get("TAG_VALUE", "true")
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"


def handler(event, context):
    action = (event.get("action") or "").lower()
    if action not in ("start", "stop"):
        raise ValueError(f"event['action'] must be 'start' or 'stop', got {action!r}")

    # "stop" only makes sense for running instances, "start" only for stopped ones.
    wanted_state = "running" if action == "stop" else "stopped"
    instance_ids = _find_instances(wanted_state)

    if not instance_ids:
        logger.info("No %s instances tagged %s=%s — nothing to %s",
                    wanted_state, TAG_KEY, TAG_VALUE, action)
        return {"action": action, "affected": [], "dry_run": DRY_RUN}

    logger.info("%s %d instance(s): %s", action, len(instance_ids), instance_ids)

    if DRY_RUN:
        logger.info("DRY_RUN=true — not calling EC2; would %s %s", action, instance_ids)
    elif action == "stop":
        ec2.stop_instances(InstanceIds=instance_ids)
    else:
        ec2.start_instances(InstanceIds=instance_ids)

    return {"action": action, "affected": instance_ids, "dry_run": DRY_RUN}


def _find_instances(state: str) -> list:
    response = ec2.describe_instances(
        Filters=[
            {"Name": f"tag:{TAG_KEY}", "Values": [TAG_VALUE]},
            {"Name": "instance-state-name", "Values": [state]},
        ]
    )
    return [
        inst["InstanceId"]
        for reservation in response["Reservations"]
        for inst in reservation["Instances"]
    ]
