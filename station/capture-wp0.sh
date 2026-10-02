#!/usr/bin/env bash
# Thu log WP0 — chiều điện thoại -> trạm, có mốc thời gian và metadata máy thu.
#
# Mục đích: chuyển kết quả "máy gaming nhận được SOS" từ nhãn LỜI KỂ thành ĐO,
# theo §4.3.3 của ket-qua-ra-soat-va-nghien-cuu-ban-dau.md.
#
# Cách dùng:
#     ./station/capture-wp0.sh [thời-gian-giây] [tên-máy]
#     ./station/capture-wp0.sh 60 gaming-rtx
#
# Kết quả:
#     results/station-<tên-máy>-<ngày>.txt   (log phiên + metadata adapter)
#     results/station-events.jsonl           (sự kiện SOS do receiver.py ghi)

set -uo pipefail

DURATION="${1:-60}"
LABEL="${2:-$(hostname -s)}"
DATE="$(date +%Y-%m-%d)"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="${ROOT}/results/station-${LABEL}-${DATE}.txt"
EVENTS="${ROOT}/results/station-events.jsonl"

mkdir -p "${ROOT}/results"

# Ghi lại trạng thái trước khi đo để loại trừ nguyên nhân về sau.
{
  echo "# Kiểm tra trạm — ${LABEL}"
  echo
  echo "- Ngày: ${DATE} $(date +%H:%M:%S)"
  echo "- Máy thu: $(hostname) ($(uname -srm))"
  echo "- Thời gian nghe: ${DURATION} giây"
  echo "- Python: $(python3 --version 2>&1)"
  echo "- Bleak: $(python3 -c 'import bleak; print(bleak.__version__)' 2>&1)"
  echo
  echo "## Adapter Bluetooth"
  echo '```'
  if command -v bluetoothctl >/dev/null 2>&1; then
    bluetoothctl list 2>&1 | sed 's/^/  /'
    bluetoothctl show 2>&1 | grep -Ei 'controller|powered|discovering|address' | sed 's/^/  /'
  else
    echo "  bluetoothctl không có"
  fi
  if command -v hciconfig >/dev/null 2>&1; then
    hciconfig -a 2>&1 | head -20 | sed 's/^/  /'
  fi
  lsusb 2>/dev/null | grep -i blue | sed 's/^/  /' || true
  echo '```'
  echo
  echo "## Số dòng station-events.jsonl trước khi đo"
  if [[ -f "${EVENTS}" ]]; then
    echo "- $(wc -l < "${EVENTS}") dòng"
  else
    echo "- chưa có tệp"
  fi
  echo
  echo "## Phiên đo"
  echo '```'
} > "${LOG}"

BEFORE=0
[[ -f "${EVENTS}" ]] && BEFORE=$(wc -l < "${EVENTS}")

echo "Đang nghe ${DURATION}s; log -> ${LOG}"
echo "Bật app RescueMesh trên điện thoại và để gần máy thu."

# Trạm có timeout cứng để không treo script.
timeout "${DURATION}" "${ROOT}/station/run.sh" 2>&1 | tee -a "${LOG}"
STATUS=$?

{
  echo '```'
  echo
  echo "## Kết quả"
  AFTER=0
  [[ -f "${EVENTS}" ]] && AFTER=$(wc -l < "${EVENTS}")
  NEW=$((AFTER - BEFORE))
  echo "- Sự kiện SOS mới: **${NEW}**"
  echo "- Tổng dòng trong station-events.jsonl: ${AFTER}"
  echo "- Mã thoát của run.sh: ${STATUS} (124 = hết thời gian, bình thường)"
  echo
  if [[ "${NEW}" -gt 0 ]]; then
    echo "### Sự kiện nhận được"
    echo '```json'
    tail -n "${NEW}" "${EVENTS}"
    echo '```'
    echo
    echo "**Kết luận:** chiều điện thoại → trạm hoạt động trên ${LABEL}."
    echo "Nhãn bằng chứng: \`ĐO\` (§4.3.3 đã hoàn tất)."
  else
    echo "**Kết luận:** KHÔNG nhận được SOS trong ${DURATION}s."
    echo "Kiểm tra theo thứ tự ở \`station/README.md\` mục 'Phần cứng máy thu':"
    echo "1. \`python3 station/diag.py 15\` — có thấy thiết bị BLE nào không?"
    echo "2. Nếu thấy thiết bị khác nhưng không thấy \`0xFFFF\` → nghi adapter/driver."
    echo "3. Đổi adapter hoặc máy khác rồi lặp lại."
  fi
} >> "${LOG}"

echo
echo "Đã ghi ${LOG}"
exit 0
