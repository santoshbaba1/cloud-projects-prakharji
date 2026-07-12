"""Meridian Retail storefront — the same tiny Flask app, now shipped through a pipeline.

Routes:
  /         → greeting + which target/version/revision answered (as JSON)
  /healthz  → 200 for Cloud Run's health check

GREETING and APP_VERSION come from environment variables set per Cloud Deploy
*target* (staging vs. prod), so the very same image reports which stage it is
running in. Cloud Run injects PORT (8080) and K_REVISION.
"""
import os
import socket

from flask import Flask, jsonify

app = Flask(__name__)

GREETING = os.environ.get("GREETING", "Hello from Meridian Retail")
VERSION = os.environ.get("APP_VERSION", "1.0")
TARGET = os.environ.get("TARGET", "local")
REVISION = os.environ.get("K_REVISION", socket.gethostname())


@app.route("/")
def home():
    return jsonify(message=GREETING, version=VERSION, target=TARGET, revision=REVISION)


@app.route("/healthz")
def healthz():
    return "ok\n", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
