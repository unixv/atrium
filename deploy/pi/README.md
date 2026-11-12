# Atrium Raspberry Pi Zero W deployment

Atrium uses SQLite, Python WebSockets and static TypeScript/Vite assets.
On the original Pi Zero W (ARMv6/512 MB RAM), apt supplies ARMv6-compatible
`python3-websockets`, `python3-jwt`, `python3-bcrypt`, and Nginx.
The Raspberry Pi does **not** build the frontend or run MongoDB.

## Architecture

GitHub Actions tests and builds on every push to `main`, publishing a
`pi-<40-character commit SHA>` release. The Pi's `atrium-update.timer` polls
the latest release using outbound HTTPS every ~2 minutes. It validates a
SHA-256 checksum, unpacks the release, switches `/opt/atrium/current`
atomically, restarts the WebSocket server and performs a WebSocket readiness
check. If readiness fails, it restores the last working release.

Nginx serves static frontend files from the current release and forwards
`/ws` to the Python server. The site listens on **port 5000** on all interfaces,
which is compatible with a Cloudflare Tunnel targeting
`http://<Pi-LAN-IP>:5000`. The Python server listens only on
`127.0.0.1:8787`.

## Fresh Pi setup

Use Raspberry Pi OS Lite 32-bit (Trixie). On the Pi over SSH:

```bash
curl -fsSLo /tmp/atrium-install.sh \
  https://raw.githubusercontent.com/unixv/atrium/main/deploy/pi/install.sh
less /tmp/atrium-install.sh
sudo bash /tmp/atrium-install.sh
```

This installs apt packages, creates a dedicated `atrium` system user, generates
a per-device JWT signing key, installs systemd units and Nginx, enables the
release poll timer, and deploys the newest successfully published release.
It leaves the existing `cloudflared` service unchanged.

The installer stops the earlier `flask-test.service` if present. If Flask was
launched manually, stop it first so port 5000 becomes available.

## Operational commands

```bash
curl http://127.0.0.1:5000/health
systemctl status atrium cloudflared nginx atrium-update.timer --no-pager
journalctl -u atrium -n 50 --no-pager
journalctl -u atrium-update.service -n 80 --no-pager
sudo systemctl start atrium-update.service  # check immediately
```

Persistence: `/var/lib/atrium/atrium.sqlite3` (WAL mode).
Secrets: `/etc/atrium/atrium.env`, root-readable only. Do not store either
in GitHub or the release directory. Back up the database with the SQLite
online backup API or `sqlite3 .backup` before risky upgrades.

No MongoDB data migration tool is provided. If an existing MongoDB deployment
contains important users or rooms, export/migrate that data before switching.

## Caveats

The updater detects startup and WebSocket handshake failures but doesn't
validate every gameplay behavior. A new release can also change the database
schema in ways that simple code rollback cannot reverse. Avoid automatic
destructive migrations, and back up user data. This is an alpha game on a
single low-power, residential-network host; do not assume high availability.
