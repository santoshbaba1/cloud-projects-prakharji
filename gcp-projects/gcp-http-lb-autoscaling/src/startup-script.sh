#!/bin/bash
# Runs automatically the first time each VM boots (set as the instance template's
# startup-script). It installs Flask and starts the app on port 80.
#
# Kept minimal on purpose — install, fetch the app, run it. Nothing fancy.
set -e

# 1. Install Python's pip and the Flask web framework
apt-get update
apt-get install -y python3-pip
pip3 install --break-system-packages flask==3.1.0

# 2. Write the app to disk. In a real setup you'd pull from a repo or artifact
#    store; here we inline it so the template is fully self-contained.
cat > /opt/app.py <<'PY'
import socket, time
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
    end = time.time() + 15
    while time.time() < end:
        _ = 12345 * 6789
    return f"{HOSTNAME} burned CPU for 15s\n"

app.run(host="0.0.0.0", port=80)
PY

# 3. Start the app in the background so the VM boot completes.
nohup python3 /opt/app.py > /var/log/app.log 2>&1 &
