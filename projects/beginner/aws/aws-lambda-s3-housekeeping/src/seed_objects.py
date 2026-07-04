"""
Lambda S3 Housekeeping - Lambda Automation Series, Project 3
Upload a few sample objects under active/ so the housekeeper has something to
act on. You can't backdate an object's LastModified, so in the lab you set
RETENTION_DAYS=0 to make freshly-uploaded objects immediately eligible.

Usage:
    python src/seed_objects.py <bucket-name>

Prerequisites:
    pip install boto3
"""

import sys

import boto3

REGION = "us-east-1"
SAMPLE_KEYS = [
    "active/report-jan.txt",
    "active/report-feb.txt",
    "active/logs/app.log",
    "active/notes.md",
]


def main(bucket: str):
    s3 = boto3.client("s3", region_name=REGION)
    for key in SAMPLE_KEYS:
        s3.put_object(Bucket=bucket, Key=key, Body=f"sample content for {key}\n".encode())
        print(f"uploaded s3://{bucket}/{key}")
    print(f"\nDone. {len(SAMPLE_KEYS)} objects under active/.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python src/seed_objects.py <bucket-name>")
    main(sys.argv[1])
