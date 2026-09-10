#!/usr/bin/env bash
#
# ResearchConclave — one-shot EC2 setup.
#
# Run this ON the EC2 instance (Ubuntu 24.04), as the default `ubuntu` user:
#
#     bash deploy/setup-ec2.sh
#
# Do NOT run it with `sudo|bash` — it uses sudo internally where needed.
#
# It installs Python + git, adds a swap file, clones/pulls the repo, creates a
# virtualenv, installs requirements, and runs the Streamlit app as a systemd
# service on PORT. Re-running is safe (updates code, restarts the service).
#
# Override any of these env vars if needed:
#   REPO_URL  git URL to clone    (default: the project repo)
#   APP_DIR   where the code lives (default: this repo, else $HOME/multi-agent-resource-system)
#   PORT      Streamlit port      (default: 8501)

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/ankit8405/multi-agent-resource-system.git}"
PORT="${PORT:-8501}"
RUN_USER="${SUDO_USER:-$USER}"

# If this script lives inside a cloned copy of the repo (…/deploy/setup-ec2.sh),
# reuse that repo as APP_DIR instead of cloning a second time.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
if [ -z "${APP_DIR:-}" ]; then
  if [ -d "$REPO_ROOT/.git" ]; then APP_DIR="$REPO_ROOT"; else APP_DIR="$HOME/multi-agent-resource-system"; fi
fi

if [ "$RUN_USER" = "root" ]; then
  echo "!! Run this as a normal user (the 'ubuntu' user), not root/sudo. Aborting." >&2
  exit 1
fi

echo "==> Checking Python (need >= 3.11; Ubuntu 24.04 ships 3.12)"
python3 --version
python3 - <<'PY'
import sys
assert sys.version_info >= (3, 11), "Python 3.11+ required — use Ubuntu 24.04 or install 3.11"
print("    Python OK")
PY

echo "==> Installing system packages"
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip git

echo "==> Ensuring a 2 GiB swap file (t3.micro has only 1 GiB RAM)"
if ! swapon --show | grep -q '/swapfile'; then
  sudo fallocate -l 2G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
  echo "    Swap enabled"
else
  echo "    Swap already present"
fi

echo "==> Fetching code into $APP_DIR"
if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" pull --ff-only
else
  git clone "$REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"

echo "==> Creating virtualenv and installing dependencies"
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

if [ ! -f .env ]; then
  echo
  echo "!! No .env found. Create $APP_DIR/.env with your keys, then re-run this script:"
  echo "     printf 'OPENAI_API_KEY=sk-...\\nTAVILY_API_KEY=tvly-...\\n' > $APP_DIR/.env"
  echo "     chmod 600 $APP_DIR/.env"
  echo
fi

echo "==> Writing systemd service (researchconclave.service)"
sudo tee /etc/systemd/system/researchconclave.service >/dev/null <<UNIT
[Unit]
Description=ResearchConclave (Streamlit multi-agent research app)
After=network-online.target
Wants=network-online.target

[Service]
User=$RUN_USER
WorkingDirectory=$APP_DIR
EnvironmentFile=-$APP_DIR/.env
ExecStart=$APP_DIR/.venv/bin/streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.fileWatcherType none
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

echo "==> Enabling and starting the service"
sudo systemctl daemon-reload
sudo systemctl enable --now researchconclave
sleep 2
sudo systemctl --no-pager --lines=5 status researchconclave || true

echo
echo "==> Done."
echo "    Health : curl http://localhost:$PORT/_stcore/health   (expect: ok)"
echo "    Logs   : journalctl -u researchconclave -f"
echo "    Update : cd $APP_DIR && git pull && sudo systemctl restart researchconclave"
echo
echo "    Make sure TCP port $PORT is open in the EC2 security group, then visit:"
echo "      http://<ec2-public-ip>:$PORT"
