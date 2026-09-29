#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
cd ..
if [[ -x .venv/bin/python ]]; then
  .venv/bin/python station/receiver.py "$@"
else
  python3 station/receiver.py "$@"
fi
