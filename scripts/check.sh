#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
cd frontend
npm install
npm run build
cd ../backend
python -m compileall atrium
