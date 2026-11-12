#!/usr/bin/env bash
# Poll latest tested Atrium release and deploy via a symlink. Outbound HTTPS only.
set -euo pipefail
umask 022
ROOT="${ATRIUM_ROOT:-/opt/atrium}"
SERVICE="${ATRIUM_SERVICE:-atrium.service}"
REPO="unixv/atrium"

mkdir -p "$ROOT/releases"
exec 9>"$ROOT/.update.lock"
flock -n 9 || exit 0
if ! systemctl cat "$SERVICE" >/dev/null 2>&1; then
  echo "Missing $SERVICE. Run the Pi install script first." >&2
  exit 1
fi

json="$(curl -fsSL --connect-timeout 10 --max-time 30 --retry 2 \
  -H 'Accept: application/vnd.github+json' \
  "https://api.github.com/repos/$REPO/releases/latest")"
tag="$(printf '%s' "$json" | python3 -c 'import json,sys;print(json.load(sys.stdin)["tag_name"])')"
if [[ ! "$tag" =~ ^pi-[a-f0-9]{40}$ ]]; then
  echo "Invalid Atrium release tag: $tag" >&2
  exit 1
fi

release="$ROOT/releases/$tag"
current="$(readlink -f "$ROOT/current" 2>/dev/null || true)"
[[ "$current" == "$release" ]] && exit 0

stage="$(mktemp -d "$ROOT/releases/.incoming.XXXXXXXX")"
trap 'rm -rf "$stage"' EXIT
base="https://github.com/$REPO/releases/download/$tag"
curl -fsSL --retry 3 --connect-timeout 10 -o "$stage/atrium-pi.tar.gz" "$base/atrium-pi.tar.gz"
curl -fsSL --retry 3 --connect-timeout 10 -o "$stage/atrium-pi.tar.gz.sha256" "$base/atrium-pi.tar.gz.sha256"
(cd "$stage" && sha256sum -c atrium-pi.tar.gz.sha256)

mkdir "$stage/app"
tar -xzf "$stage/atrium-pi.tar.gz" -C "$stage/app" --no-same-owner --no-same-permissions
test -f "$stage/app/backend/atrium/main.py"
test -f "$stage/app/frontend/dist/index.html"
python3 -m compileall -q "$stage/app/backend/atrium"

python3 -c 'import websockets, jwt, bcrypt, sqlite3' || {
  echo "Missing Pi Python runtime; run deploy/pi/install.sh" >&2
  exit 1
}
if [[ -d "$release" ]]; then
  # A previous failed first attempt may leave this unpacked directory.
  rm -rf -- "$release"
fi
mv "$stage/app" "$release"

next_link="$ROOT/.current-next"
ln -sfn "$release" "$next_link"
mv -Tf "$next_link" "$ROOT/current"
systemctl restart "$SERVICE"

# A successful TCP listen isn't sufficient: verify that the game is answering WebSockets.
if ! python3 - <<'PY'
import asyncio, json
from websockets.asyncio.client import connect

async def verify():
    for _ in range(10):
        try:
            async with connect("ws://127.0.0.1:8787/ws", open_timeout=2) as ws:
                raw = await asyncio.wait_for(ws.recv(), timeout=3)
                if json.loads(raw).get("type") == "server.ready":
                    return
        except (OSError, TimeoutError, ValueError, Exception):
            await asyncio.sleep(1)
    raise SystemExit("Atrium did not pass WebSocket readiness check")

asyncio.run(verify())
PY
then
  echo "New release failed readiness; rolling back." >&2
  if [[ -n "$current" && -d "$current" ]]; then
    ln -sfn "$current" "$next_link"
    mv -Tf "$next_link" "$ROOT/current"
    systemctl restart "$SERVICE" || true
  else
    rm -f "$ROOT/current"
    systemctl stop "$SERVICE" || true
  fi
  exit 1
fi
echo "Deployed $tag"
