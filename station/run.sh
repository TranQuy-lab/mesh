#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
cd ..
python3 station/receiver.py "$@"
