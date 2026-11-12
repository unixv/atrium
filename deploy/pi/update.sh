#!/usr/bin/env bash
# Runs on the Pi: pull a tested release via outbound HTTPS and atomically swap it.
set -euo pipefail
umask 022

ROOT="${ATRIUM_ROOT:-/opt/atrium}"
SERVICE="${ATRIUM_SERVICE:-atrium.service}"
REPO="unixv/atrium"

mkdir -p "$ROOT/releases"
exec 9>"$ROOT/.update.lock"
flock -n 9 || exit 0

# Do not replace the existing Flask test until Atrium's own service is installed.
if ! systemctl cat "$SERVICE" >/dev/null 2>&1; then
  echo "$SERVICE does not exist; Atrium must be ported/configured before deploying."
  exit 1
fi

json="$(curl -fsSL --connect-timeout 10 --max-time 30 --retry 2 -H 'Accept: application/vnd.github+json' "https://api.github.com/repos/$REPO/releases/latest")"
tag="$(printf '%s' "$json" | python3 -c 'import json,sys;print(json.load(sys.stdin)["tag_name"])')"
if [[ ! "$tag" =~ ^pi-[a-f0-9]{40}$ ]]; then
  echo "Unexpected release tag: $tag" >&2
  exit 1
fi

release="$ROOT/releases/$tag"
current="$(readlink -f "$ROOT/current" 2>/dev/null || true)"
if [[ "$current" == "$release" ]]; then
  exit 0
fi

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
mv "$stage/app" "$release"

# Python dependencies are provisioned separately in the Pi's shared virtualenv.
# Do not deploy an incompatible release if the runtime has not been provisioned.
if [[ ! -x "$ROOT/venv/bin/python" ]]; then
  echo "Missing $ROOT/venv; provision Atrium dependencies before enabling updates." >&2
  exit 1
fi

next_link="$ROOT/.current-next"
ln -sfn "$release" "$next_link"
mv -Tf "$next_link" "$ROOT/current"
systemctl restart "$SERVICE"
sleep 3
if ! systemctl is-active --quiet "$SERVICE"; then
  echo "New service failed; rolling back." >&2
  if [[ -n "$current" && -d "$current" ]]; then
    ln -sfn "$current" "$next_link"
    mv -Tf "$next_link" "$ROOT/current"
    systemctl restart "$SERVICE" || true
  else
    rm -f "$ROOT/current"
  fi
  exit 1
fi
echo "Deployed $tag"
