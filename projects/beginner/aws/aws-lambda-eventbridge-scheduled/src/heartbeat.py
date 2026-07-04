"""
Lambda EventBridge Scheduled - Lambda Automation Series, Project 1
Runs on a schedule (an EventBridge rule). Logs each run and, if an SNS topic
is configured, publishes a small heartbeat message.

Environment variables:
  SNS_TOPIC_ARN  - (optional) if set, publish the heartbeat here
  ENVIRONMENT    - (optional) label included in the message (default "dev")
"""

import datetime
import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client("sns")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")


def handler(event, context):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # Scheduled invocations carry "source": "aws.events"; manual tests usually won't.
    trigger = event.get("source", "manual")
    logger.info("Heartbeat at %s (trigger=%s, env=%s)", now, trigger, ENVIRONMENT)

    message = {
        "service": "scheduled-heartbeat",
        "environment": ENVIRONMENT,
        "ran_at": now,
        "trigger": trigger,
        "request_id": context.aws_request_id,
    }

    if SNS_TOPIC_ARN:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"[{ENVIRONMENT}] Scheduled heartbeat",
            Message=json.dumps(message, indent=2),
        )
        logger.info("Published heartbeat to SNS topic %s", SNS_TOPIC_ARN)
    else:
        logger.info("SNS_TOPIC_ARN not set — skipping publish")

    return message
