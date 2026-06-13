import os
import time
import socket
import platform
from datetime import datetime, timezone

from flask import Flask, jsonify, request

app = Flask(__name__)

START_TIME = datetime.now(timezone.utc)
SERVICE_NAME = os.environ.get("SERVICE_NAME", "ec2-monitored-webapp")
APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")


def instance_id():
    # On EC2 the hostname is the private DNS name; locally it is the machine name.
    # We avoid calling the metadata service here so the app also runs on a laptop.
    return os.environ.get("INSTANCE_ID", socket.gethostname())


@app.route("/")
def index():
    return jsonify({
        "service": SERVICE_NAME,
        "message": "EC2 VPC Monitored Web App — Running",
        "instance_id": instance_id(),
        "environment": ENVIRONMENT,
        "region": REGION,
        "version": APP_VERSION,
    })


@app.route("/health")
def health():
    uptime = int((datetime.now(timezone.utc) - START_TIME).total_seconds())
    return jsonify({
        "status": "healthy",
        "uptime_seconds": uptime,
        "instance_id": instance_id(),
    }), 200


@app.route("/api/info")
def info():
    return jsonify({
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "instance_id": instance_id(),
        "environment": ENVIRONMENT,
        "version": APP_VERSION,
    })


@app.route("/api/load")
def load():
    # Burns CPU for a short, bounded time so learners can deliberately trip the
    # CloudWatch CPU alarm (Step 07) and trigger the SNS email (Step 08) and
    # Auto Scaling (Step 06). Capped at 10s so a stray request can't hang a host.
    seconds = request.args.get("seconds", default="3")
    try:
        seconds = max(0.0, min(10.0, float(seconds)))
    except ValueError:
        return jsonify({"error": "seconds must be a number between 0 and 10"}), 400

    deadline = time.time() + seconds
    iterations = 0
    while time.time() < deadline:
        # Pure-Python busy loop: keeps one CPU core hot for `seconds`.
        _ = sum(i * i for i in range(10000))
        iterations += 1

    return jsonify({
        "message": f"Burned CPU for {seconds} seconds",
        "iterations": iterations,
        "instance_id": instance_id(),
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
