#!/usr/bin/env bash
# Raspberry Pi OS Lite (Trixie, ARMv6) first-time Atrium installer.
# Run as root: sudo bash deploy/pi/install.sh
set -euo pipefail
if [[ "$EUID" -ne 0 ]]; then
  echo "Run as root via sudo." >&2
  exit 1
fi
echo "Installing native Raspberry Pi OS packages (no Docker / MongoDB / Node.js)"
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  nginx python3 python3-websockets python3-jwt python3-bcrypt \
  curl ca-certificates util-linux
python3 - <<'PY'
import sys
import websockets, jwt, bcrypt, sqlite3
from websockets.asyncio.server import serve
from websockets.asyncio.client import connect
print("Python", sys.version.split()[0], "| websockets", websockets.__version__, "| SQLite", sqlite3.sqlite_version)
PY

if ! id -u atrium >/dev/null 2>&1; then
  useradd --system --home /var/lib/atrium --shell /usr/sbin/nologin atrium
fi
install -d -o atrium -g atrium -m 0750 /var/lib/atrium
install -d -o root -g root -m 0755 /opt/atrium /opt/atrium/releases /etc/atrium
if [[ ! -e /etc/atrium/atrium.env ]]; then
  secret="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
  cat > /etc/atrium/atrium.env <<EOF
ATRIUM_HOST=127.0.0.1
ATRIUM_PORT=8787
ATRIUM_DB_PATH=/var/lib/atrium/atrium.sqlite3
ATRIUM_JWT_SECRET=$secret
ATRIUM_LOG_LEVEL=INFO
ATRIUM_ENV=production
EOF
  chmod 600 /etc/atrium/atrium.env
fi

BASE="https://raw.githubusercontent.com/unixv/atrium/main/deploy/pi"
curl -fsSL --retry 3 "$BASE/update.sh" -o /usr/local/sbin/atrium-update
chmod 755 /usr/local/sbin/atrium-update
curl -fsSL --retry 3 "$BASE/atrium.service" -o /etc/systemd/system/atrium.service
curl -fsSL --retry 3 "$BASE/atrium-update.service" -o /etc/systemd/system/atrium-update.service
curl -fsSL --retry 3 "$BASE/atrium-update.timer" -o /etc/systemd/system/atrium-update.timer
curl -fsSL --retry 3 "$BASE/nginx.conf" -o /etc/nginx/sites-available/atrium

ln -sfn /etc/nginx/sites-available/atrium /etc/nginx/sites-enabled/atrium
# The earlier Flask test used port 5000; leave Cloudflare's origin unchanged.
if systemctl list-unit-files flask-test.service --no-legend 2>/dev/null | grep -q '^flask-test.service'; then
  systemctl disable --now flask-test.service
fi
if ss -ltn '( sport = :5000 )' | grep -q LISTEN; then
  echo "Port 5000 is already occupied; stop the old Flask process and rerun." >&2
  exit 1
fi
nginx -t
systemctl daemon-reload
# Enable the game for automatic startup after a power outage.
# The updater below performs the initial start after unpacking a release.
systemctl enable atrium.service
systemctl enable --now nginx
# nginx may already have started during apt installation; activate the new site.
systemctl reload nginx
systemctl enable --now atrium-update.timer

echo "Downloading latest tested Atrium release..."
systemctl start atrium-update.service || {
  echo "Release unavailable or failed. Review: journalctl -u atrium-update.service -n 80 --no-pager" >&2
  exit 1
}
echo "Local status:"
systemctl --no-pager --full status atrium.service | head -n 12 || true
curl -fsS --max-time 10 http://127.0.0.1:5000/health
echo "Atrium installed. Point Cloudflare Tunnel at http://<Pi-LAN-IP>:5000"
