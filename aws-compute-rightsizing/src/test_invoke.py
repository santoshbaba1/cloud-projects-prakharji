"""Manually invoke the compute-rightsizer Lambda and pretty-print the response."""

import json

import boto3

lambda_client = boto3.client("lambda", region_name="us-east-1")

resp = lambda_client.invoke(
    FunctionName="compute-rightsizer",
    InvocationType="RequestResponse",
    Payload=b"{}",
)

payload = json.loads(resp["Payload"].read())
print("Status :", resp["StatusCode"])
print("Response:", json.dumps(payload, indent=2))
