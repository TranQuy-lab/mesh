#!/usr/bin/env bash
# Server bản đồ RescueSOS (khâu ④+⑤) — HTTP nhận SOS từ app + nghe BLE trực tiếp.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 station/server.py "$@"
