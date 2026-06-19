"""
A tiny Flask app for the Kubernetes optimization & recovery lab.

Endpoints:
  GET /          - hello + which pod served you (proves load spreads across replicas)
  GET /healthz   - liveness/readiness probe target (always 200 once started)
  GET /burn      - burns CPU for ~`ms` milliseconds (default 200) to drive the HPA
  GET /data      - returns a value read from a mounted ConfigMap-backed file (for backup demo)
"""

import os
import socket
import time

from flask import Flask, jsonify, request

app = Flask(__name__)
POD = os.environ.get("HOSTNAME", socket.gethostname())
DATA_FILE = os.environ.get("DATA_FILE", "/data/message.txt")


@app.get("/")
def index():
    return jsonify(message="hello from the optimization & recovery lab", pod=POD)


@app.get("/healthz")
def healthz():
    return jsonify(status="ok", pod=POD)


@app.get("/burn")
def burn():
    ms = int(request.args.get("ms", "200"))
    end = time.time() + ms / 1000.0
    x = 0
    while time.time() < end:
        x = (x * x + 1) % 2147483647
    return jsonify(burned_ms=ms, pod=POD)


@app.get("/data")
def data():
    try:
        with open(DATA_FILE) as f:
            return jsonify(message=f.read().strip(), pod=POD)
    except FileNotFoundError:
        return jsonify(message="(no data file mounted)", pod=POD)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
