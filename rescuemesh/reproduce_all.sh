#!/usr/bin/env bash
# Tái lập toàn bộ bằng MỘT lệnh (cổng G11 của kế hoạch RescueMesh-LoRa).
#
#   cd rescuemesh && ./reproduce_all.sh
#
# Việc script làm:
#   1. chạy mọi bộ kiểm thử;
#   2. in mọi bảng thiết kế tái lập được (vật lý, năng lượng, codec);
#   3. chạy ma trận mô phỏng chính và ba thí nghiệm trọng tâm;
#   4. chạy phân tích ghép cặp + đường Pareto;
#   5. ghi results/REPRODUCE-REPORT.md kèm phiên bản, thời điểm và hash tệp.
#
# MỌI số sinh ra là `SUY` (từ công thức) hoặc `SIM` (mô phỏng, chưa hiệu chuẩn).
# Không có `ĐO` nào trong script này; xem WP10 của kế hoạch.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
RESULTS="$ROOT/results"
REPORT="$RESULTS/REPRODUCE-REPORT.md"
PY=python3

mkdir -p "$RESULTS"
started="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
failed=0

{
  echo "# Báo cáo tái lập RescueMesh-LoRa"
  echo
  echo "- Thời điểm chạy (UTC): \`$started\`"
  echo "- Python: \`$($PY --version 2>&1)\`"
  echo "- Máy: \`$(uname -sm)\`"
  echo
  echo "## 1. Kiểm thử"
  echo
  echo '```'
} > "$REPORT"

run_test () {
  local t="$1"
  local out
  out="$($PY "$t" 2>&1 | tail -1)"
  if [ $? -ne 0 ]; then failed=1; fi
  printf '%-26s %s\n' "$t" "$out"
  printf '%-26s %s\n' "$t" "$out" >> "$REPORT"
}

cd "$HERE"
for t in test_lora.py test_node_power.py test_packets.py test_packets_lora.py \
         test_sim_lora.py test_g0_schedule.py; do
  [ -f "$t" ] && run_test "$t"
done

{
  echo '```'
  echo
  echo "## 2. Bảng thiết kế (nhãn SUY)"
  echo
  echo '```'
} >> "$REPORT"

for gen in lora.py node_power.py packets_lora.py; do
  echo "--- $gen ---"
  echo "--- $gen ---" >> "$REPORT"
  $PY "$gen" >> "$REPORT" 2>&1
done
{
  echo '```'
  echo
  echo "## 3. Ma trận mô phỏng chính (nhãn SIM)"
  echo
  echo '```'
} >> "$REPORT"
$PY sim_lora.py >> "$REPORT" 2>&1 || failed=1

{
  echo '```'
  echo
  echo "## 4. Thí nghiệm trọng tâm E1/E1b/E2/E2b/E3 (nhãn SIM)"
  echo
  echo '```'
} >> "$REPORT"
$PY run_lora_experiments.py all >> "$REPORT" 2>&1 || failed=1

{
  echo '```'
  echo
  echo "## 5. Phân tích ghép cặp + Pareto"
  echo
  echo '```'
} >> "$REPORT"
$PY analyze_sim_lora.py >> "$REPORT" 2>&1 || failed=1

{
  echo '```'
  echo
  echo "## 6. Tệp kết quả và hash SHA-256"
  echo
  echo '```'
  cd "$RESULTS"
  for f in sim-lora-*.csv; do
    [ -f "$f" ] && printf '%-42s %s\n' "$f" "$(sha256sum "$f" | cut -c1-16)"
  done
  echo '```'
  echo
  echo "> Nhắc lại: mọi số là \`SUY\` hoặc \`SIM\`, **chưa hiệu chuẩn** (cổng G9 chưa đạt)."
  echo "> Không được trích như kết quả thực nghiệm."
} >> "$REPORT"

echo
echo "Đã ghi $REPORT"
if [ "$failed" -ne 0 ]; then
  echo "CẢNH BÁO: có bước thất bại — xem báo cáo." >&2
  exit 1
fi
echo "Tất cả bước hoàn tất không lỗi."
