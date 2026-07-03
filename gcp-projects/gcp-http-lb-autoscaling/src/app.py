"""A small Flask app that runs on every VM in the managed instance group.

Three routes:
  /          → shows which VM answered (proves the load balancer spreads traffic)
  /healthz   → returns 200 so the load balancer's health check marks the VM healthy
  /load      → burns CPU for a few seconds so you can trigger autoscaling on demand

Kept deliberately simple: no database, no external calls.
"""
import socket
import time

from flask import Flask

app = Flask(__name__)

HOSTNAME = socket.gethostname()


@app.route("/")
def home():
    return f"Hello from {HOSTNAME}\n"


@app.route("/healthz")
def healthz():
    return "ok\n", 200


@app.route("/load")
def load():
    # Busy-loop for ~15 seconds to push CPU up. Hit this on several VMs at once
    # (or in a loop) to make the autoscaler add instances.
    end = time.time() + 15
    while time.time() < end:
        _ = 12345 * 6789
    return f"{HOSTNAME} burned CPU for 15s\n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
