"""
Lambda EC2 Start/Stop Scheduler - Lambda Automation Series, Project 2
Manually invoke the scheduler with a chosen action before wiring up schedules.

Usage:
    python src/test_invoke.py stop
    python src/test_invoke.py start

Prerequisites:
    pip install boto3
    AWS credentials configured (aws configure or env vars)
"""

import json
import sys

import boto3

FUNCTION_NAME = "ec2-scheduler"
REGION = "us-east-1"

client = boto3.client("lambda", region_name=REGION)


def invoke(action: str) -> dict:
    response = client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps({"action": action}).encode(),
    )
    return {
        "http_status": response["StatusCode"],
        "function_error": response.get("FunctionError"),
        "response": json.loads(response["Payload"].read()),
    }


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "stop"
    print(f"Invoking {FUNCTION_NAME} with action={action!r}")
    result = invoke(action)
    print(f"HTTP status   : {result['http_status']}")
    print(f"Function error: {result['function_error']}")
    print(f"Response      : {json.dumps(result['response'], indent=2)}")
