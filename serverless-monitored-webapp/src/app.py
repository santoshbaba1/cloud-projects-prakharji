"""Serverless version of the monitored web app.

One Lambda function behind an API Gateway HTTP API. It mirrors the four endpoints
of the EC2 project (/, /health, /api/info, /api/load) so you can compare the two
architectures request-for-request. No web framework needed — API Gateway does the
HTTP, this handler does the routing.

Designed for the API Gateway **HTTP API** payload format v2.0.
"""
import os
import json
import time
import platform
from datetime import datetime, timezone

COLD_START = datetime.now(timezone.utc)
SERVICE_NAME = os.environ.get("SERVICE_NAME", "serverless-monitored-webapp")
APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")
REGION = os.environ.get("AWS_REGION", "us-east-1")


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _path(event):
    # HTTP API v2 puts the path here; fall back to REST API / direct invokes.
    ctx = event.get("requestContext", {})
    return (
        event.get("rawPath")
        or ctx.get("http", {}).get("path")
        or event.get("path")
        or "/"
    )


def _query(event, key, default=None):
    params = event.get("queryStringParameters") or {}
    return params.get(key, default)


def index():
    return _response(200, {
        "service": SERVICE_NAME,
        "message": "Serverless Monitored Web App — Running",
        "compute": "AWS Lambda",
        "region": REGION,
        "version": APP_VERSION,
    })


def health():
    uptime = int((datetime.now(timezone.utc) - COLD_START).total_seconds())
    return _response(200, {
        "status": "healthy",
        "seconds_since_cold_start": uptime,
    })


def info():
    return _response(200, {
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "runtime": "lambda",
        "version": APP_VERSION,
    })


def load(event):
    raw = _query(event, "seconds", "3")
    try:
        seconds = max(0.0, min(10.0, float(raw)))
    except (TypeError, ValueError):
        return _response(400, {"error": "seconds must be a number between 0 and 10"})

    deadline = time.time() + seconds
    iterations = 0
    while time.time() < deadline:
        _ = sum(i * i for i in range(10000))
        iterations += 1

    return _response(200, {
        "message": f"Burned CPU for {seconds} seconds",
        "iterations": iterations,
    })


ROUTES = {
    "/": index,
    "/health": health,
    "/api/info": info,
}


def handler(event, context):
    path = _path(event)
    if path == "/api/load":
        return load(event)
    fn = ROUTES.get(path)
    if fn is None:
        return _response(404, {"error": f"no route for {path}"})
    return fn()
