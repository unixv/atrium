# Atrium: deploy main to Raspberry Pi Zero W

Push to `main` -> GitHub Actions tests/builds on a hosted runner -> publishes a public
`pi-<commit SHA>` release -> the Pi checks for new releases every two minutes over HTTPS.
No inbound SSH, Pi GitHub runner, or Node/TypeScript compiler is required.

## One-time Pi setup (run through SSH)

These commands install the updater. **Do not enable production releases until
Atrium has an ARMv6-compatible Python environment, a SQLite backend and an
`atrium.service` systemd unit.** The current `docker-compose.yml` uses MongoDB 7,
which cannot be hosted on the original Pi Zero W.

```bash
sudo mkdir -p /opt/atrium/releases
sudo curl -fsSL https://raw.githubusercontent.com/unixv/atrium/main/deploy/pi/update.sh -o /usr/local/sbin/atrium-update
sudo chmod 755 /usr/local/sbin/atrium-update
sudo curl -fsSL https://raw.githubusercontent.com/unixv/atrium/main/deploy/pi/atrium-update.service -o /etc/systemd/system/atrium-update.service
sudo curl -fsSL https://raw.githubusercontent.com/unixv/atrium/main/deploy/pi/atrium-update.timer -o /etc/systemd/system/atrium-update.timer
sudo systemctl daemon-reload
sudo systemctl enable --now atrium-update.timer
systemctl list-timers atrium-update.timer
```

## Atrium runtime prerequisites

- `atrium.service` must run the Atrium application, **not the existing Flask test**.
- `/opt/atrium/venv/bin/python` must exist with Atrium's supported Python dependencies installed.
- The service must run from `/opt/atrium/current/backend`, the symlink created
  by the updater, and listen on an address accessible through your existing Cloudflare route.
- Keep the SQLite database in `/var/lib/atrium/`, and keep JWT secrets and other
  credentials outside the release directory (e.g. a root-readable environment file).
- Provision and test any changed Python dependencies separately; releases do
  not build or install ARMv6 native modules.
- The updater verifies downloaded checksums and basic package layout and rolls
  back the symlink if the service fails immediately. Full functional health checks
  and safe database migration/rollback are separate future requirements.

Test an update manually after installing the application:

```bash
sudo systemctl start atrium-update.service
sudo journalctl -u atrium-update.service -n 50 --no-pager
```

Check build status in GitHub Actions and published versions on the repository's Releases page.
