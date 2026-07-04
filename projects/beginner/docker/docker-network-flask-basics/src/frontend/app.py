"""frontend service — calls the backend by name and shows the result.

It stores no data of its own. It resolves the backend at BACKEND_URL, which
defaults to http://backend:5000. The hostname `backend` only resolves when both
containers share a user-defined Docker network; on the default bridge the same
call fails to resolve — which is the whole lesson of this lab.
"""

import os

import requests
from flask import Flask, jsonify

BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:5000")
app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok", service="frontend")


@app.get("/")
def home():
    try:
        data = requests.get(f"{BACKEND_URL}/api/message", timeout=3).json()
    except requests.RequestException as exc:
        return (
            jsonify(error="backend unreachable", backend_url=BACKEND_URL, detail=str(exc)),
            503,
        )
    return jsonify(frontend="ok", backend_url=BACKEND_URL, backend_said=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
