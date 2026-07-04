#!/bin/bash
# EC2 user-data: runs once at first boot (as root) to bootstrap the web app.
# Paste this into the "User data" box when launching the instance (Step 04),
# or pass it with `aws ec2 run-instances --user-data file://user-data.sh`.
#
# It installs Python, the CloudWatch agent, and the app, then runs the app as a
# systemd service behind gunicorn on port 5000 so it survives reboots and crashes.
set -euxo pipefail

APP_DIR=/opt/webapp
APP_USER=webapp
LOG_FILE=/var/log/user-data.log
exec > >(tee -a "$LOG_FILE") 2>&1

# --- 1. System packages (Amazon Linux 2023) -------------------------------
dnf update -y
dnf install -y python3 python3-pip git amazon-cloudwatch-agent

# --- 2. Application user and directory ------------------------------------
id "$APP_USER" &>/dev/null || useradd --system --create-home --shell /usr/sbin/nologin "$APP_USER"
mkdir -p "$APP_DIR"

# --- 3. Application code ----------------------------------------------------
# For the workshop we write the app inline so the instance is self-contained.
# In Step 10 the GitHub Actions workflow replaces this with `git pull` deploys.
cat > "$APP_DIR/app.py" <<'PYEOF'
import os, time, socket, platform
from datetime import datetime, timezone
from flask import Flask, jsonify, request

app = Flask(__name__)
START_TIME = datetime.now(timezone.utc)

@app.route("/")
def index():
    return jsonify({"service": os.environ.get("SERVICE_NAME", "ec2-monitored-webapp"),
                    "message": "EC2 VPC Monitored Web App — Running",
                    "instance_id": socket.gethostname(),
                    "version": os.environ.get("APP_VERSION", "1.0.0")})

@app.route("/health")
def health():
    up = int((datetime.now(timezone.utc) - START_TIME).total_seconds())
    return jsonify({"status": "healthy", "uptime_seconds": up,
                    "instance_id": socket.gethostname()}), 200

@app.route("/api/info")
def info():
    return jsonify({"python_version": platform.python_version(),
                    "platform": platform.system(), "instance_id": socket.gethostname()})

@app.route("/api/load")
def load():
    seconds = request.args.get("seconds", "3")
    try:
        seconds = max(0.0, min(10.0, float(seconds)))
    except ValueError:
        return jsonify({"error": "seconds must be a number between 0 and 10"}), 400
    deadline = time.time() + seconds
    n = 0
    while time.time() < deadline:
        _ = sum(i * i for i in range(10000)); n += 1
    return jsonify({"message": f"Burned CPU for {seconds} seconds", "iterations": n})
PYEOF

cat > "$APP_DIR/requirements.txt" <<'REQEOF'
flask==3.1.0
gunicorn==23.0.0
REQEOF

python3 -m pip install -r "$APP_DIR/requirements.txt"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

# --- 4. systemd service (gunicorn, 2 workers, port 5000) -------------------
cat > /etc/systemd/system/webapp.service <<SVCEOF
[Unit]
Description=EC2 Monitored Web App
After=network.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment=APP_VERSION=1.0.0
ExecStart=/usr/local/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable --now webapp.service

# --- 5. CloudWatch agent (memory + disk metrics, app log shipping) ---------
# The agent config is uploaded separately in Step 07; if present, start it.
if [ -f /opt/aws/amazon-cloudwatch-agent/etc/cloudwatch-agent-config.json ]; then
  /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config -m ec2 -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/cloudwatch-agent-config.json
fi

echo "user-data bootstrap complete"
