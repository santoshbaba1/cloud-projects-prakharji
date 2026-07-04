"""
Lambda EventBridge Scheduled - Lambda Automation Series, Project 1
Manually invoke the scheduled function to confirm it works before wiring up
the EventBridge rule.

Usage:
    python src/test_invoke.py

Prerequisites:
    pip install boto3
    AWS credentials configured (aws configure or env vars)
"""

import json

import boto3

FUNCTION_NAME = "scheduled-heartbeat"
REGION = "us-east-1"

client = boto3.client("lambda", region_name=REGION)


def invoke(payload: dict) -> dict:
    response = client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode(),
    )
    return {
        "http_status": response["StatusCode"],
        "function_error": response.get("FunctionError"),
        "response": json.loads(response["Payload"].read()),
    }


if __name__ == "__main__":
    result = invoke({})  # empty payload mimics a manual run
    print(f"HTTP status   : {result['http_status']}")
    print(f"Function error: {result['function_error']}")
    print(f"Response      : {json.dumps(result['response'], indent=2)}")
