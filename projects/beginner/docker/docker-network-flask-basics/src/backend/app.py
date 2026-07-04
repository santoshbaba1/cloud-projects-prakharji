"""backend service — a tiny JSON API that owns the data.

It knows nothing about the frontend. Other containers reach it by its container
name (`backend`) over a shared user-defined Docker network — that name only
resolves because Docker runs an embedded DNS server on user-defined networks.
"""

import os
import socket

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok", service="backend")


@app.get("/api/message")
def message():
    return jsonify(
        service="backend",
        container=socket.gethostname(),
        message="Hello from the backend service",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
