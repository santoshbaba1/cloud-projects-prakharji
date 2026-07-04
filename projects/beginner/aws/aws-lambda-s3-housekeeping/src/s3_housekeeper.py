"""
Lambda S3 Housekeeping - Lambda Automation Series, Project 3
Runs on a schedule. Scans a bucket prefix for objects older than a retention
window and either archives them (moves to an archive/ prefix) or deletes them.

Environment variables:
  BUCKET          - bucket to clean (required)
  PREFIX          - only scan keys under this prefix (default "active/")
  ARCHIVE_PREFIX  - destination prefix when ACTION=archive (default "archive/")
  ACTION          - "archive" (move) or "delete" (default "archive")
  RETENTION_DAYS  - act on objects older than this many days (default "30")
  DRY_RUN         - "true" to log what would happen without changing anything
"""

import datetime
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

BUCKET = os.environ["BUCKET"]
PREFIX = os.environ.get("PREFIX", "active/")
ARCHIVE_PREFIX = os.environ.get("ARCHIVE_PREFIX", "archive/")
ACTION = os.environ.get("ACTION", "archive").lower()
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "30"))
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"


def handler(event, context):
    if ACTION not in ("archive", "delete"):
        raise ValueError(f"ACTION must be 'archive' or 'delete', got {ACTION!r}")

    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        days=RETENTION_DAYS
    )
    logger.info("Scanning s3://%s/%s for objects older than %s (action=%s, dry_run=%s)",
                BUCKET, PREFIX, cutoff.isoformat(), ACTION, DRY_RUN)

    processed = []
    for obj in _iter_objects(PREFIX):
        key = obj["Key"]
        # An archive run must not re-process what it already moved into ARCHIVE_PREFIX.
        if ACTION == "archive" and key.startswith(ARCHIVE_PREFIX):
            continue
        if obj["LastModified"] >= cutoff:
            continue

        logger.info("%s qualifies (LastModified=%s)", key, obj["LastModified"].isoformat())
        if not DRY_RUN:
            _apply(key)
        processed.append(key)

    logger.info("Done. %d object(s) %sed%s",
                len(processed), ACTION, " (dry run)" if DRY_RUN else "")
    return {"action": ACTION, "dry_run": DRY_RUN, "count": len(processed),
            "keys": processed}


def _iter_objects(prefix: str):
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix):
        for obj in page.get("Contents", []):
            yield obj


def _apply(key: str):
    if ACTION == "delete":
        s3.delete_object(Bucket=BUCKET, Key=key)
        return
    # archive = copy to ARCHIVE_PREFIX (preserving the path after PREFIX), then delete original
    relative = key[len(PREFIX):] if key.startswith(PREFIX) else key
    dest_key = f"{ARCHIVE_PREFIX}{relative}"
    s3.copy_object(Bucket=BUCKET, CopySource={"Bucket": BUCKET, "Key": key}, Key=dest_key)
    s3.delete_object(Bucket=BUCKET, Key=key)
    logger.info("Moved %s -> %s", key, dest_key)
