"""
Lambda S3 Housekeeping - Lambda Automation Series, Project 3
Manually invoke the housekeeper before wiring up the schedule.

Usage:
    python src/test_invoke.py

Prerequisites:
    pip install boto3
"""

import json

import boto3

FUNCTION_NAME = "s3-housekeeper"
REGION = "us-east-1"

client = boto3.client("lambda", region_name=REGION)


def invoke() -> dict:
    response = client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=b"{}",
    )
    return {
        "http_status": response["StatusCode"],
        "function_error": response.get("FunctionError"),
        "response": json.loads(response["Payload"].read()),
    }


if __name__ == "__main__":
    result = invoke()
    print(f"HTTP status   : {result['http_status']}")
    print(f"Function error: {result['function_error']}")
    print(f"Response      : {json.dumps(result['response'], indent=2)}")
