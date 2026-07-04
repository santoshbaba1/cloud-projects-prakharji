import os

import boto3

sqs = boto3.client('sqs', region_name='us-east-1')
# Set QUEUE_URL to your own queue, e.g.
#   export QUEUE_URL="https://sqs.us-east-1.amazonaws.com/<ACCOUNT_ID>/testqueue"
QUEUE_URL = os.environ["QUEUE_URL"]

for i in range(1, 11):
    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=f'{{"test": "message {i}"}}'
    )
    print(f"Sent message {i}: {response['MessageId']}")
