#!/usr/bin/env python3
"""Phân tích nhật ký drill từ events.jsonl của app (kéo về bằng adb pull).

Dùng cho drill kế hoạch §5.2:
  D2 — truyền đứng yên : PDR + trễ P50/P95 từ cặp "sos_issued" ↔ "frame_rx".
  D5 — cổng ra         : trễ từ "frame_rx"/"sos_issued" ↔ "gateway_sent".
  Khác: đếm fall_suspected / h7_alarm / gateway lỗi.

Mỗi máy ghi events.jsonl riêng (adb pull /sdcard/Android/data/org.rescuemesh.g0/files/events.jsonl).
Gộp nhiều file: python3 analyze_drill.py out.log event.jsonl máy-B/... 

Tin SOS khớp nhau bằng frame_id (hex khung — ổn vì byte route không nằm trong
cùng một khung phát lại? Không: relay đổi byte TTL/hop ⇒ frame_id đổi giữa
các hop. Vì vậy khớp theo (source, sequence) — cặp định danh e2e ổn định).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def load_events(paths: list[str]) -> list[dict]:
    out = []
    for p in paths:
        for line in Path(p).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                rec["_file"] = Path(p).name
                out.append(rec)
            except json.JSONDecodeError:
                print(f"[bỏ qua] dòng JSON lỗi ở {p}", file=sys.stderr)
    out.sort(key=lambda r: r.get("wall_ms", 0))
    return out


def analyze(events: list[dict]) -> dict:
    issued = [e for e in events if e.get("event") == "sos_issued"]
    received = [e for e in events if e.get("event") == "frame_rx"]
    sent = [e for e in events if e.get("event") == "gateway_sent"]

    def key(e: dict) -> tuple:
        return (str(e.get("source")), e.get("sequence"))

    rx_keys = {key(e) for e in received}
    tx_keys = {key(e) for e in issued if key(e)[0] != "None"}

    # PDR: số SOS phát ra khác nguồn đã thấy ở máy thu (D2, tối thiểu 2 máy)
    pdr = None
    if tx_keys and rx_keys:
        pdr = len(tx_keys & rx_keys) / max(1, len(tx_keys))

    # Trễ: (source, sequence) trùng nhau giữa hai máy — lấy min|Δt|
    lags_ms = []
    rx_by_key: dict[tuple, list[int]] = {}
    for e in received:
        rx_by_key.setdefault(key(e), []).append(e.get("wall_ms", 0))
    for e in issued:
        k = key(e)
        for t_rx in rx_by_key.get(k, []):
            d = abs(t_rx - e.get("wall_ms", 0))
            if 0 < d < 10 * 60_000:  # trễ hợp lý < 10 phút
                lags_ms.append(d)
    lags_ms.sort()

    def pct(p: float) -> float | None:
        return float(lags_ms[min(len(lags_ms) - 1, int(p * len(lags_ms) + 0.999) - 1)]) if lags_ms else None

    gw_lags = []
    for e in sent:
        # gateway_sent không mang frame_id riêng — dùng khoảng tới SOS trước đó cùng máy
        prev = [x for x in events if x.get("event") in ("sos_issued", "frame_rx")
                and x.get("wall_ms", 0) <= e.get("wall_ms", 0)]
        if prev:
            gw_lags.append(e.get("wall_ms", 0) - prev[-1].get("wall_ms", 0))

    counts: dict[str, int] = {}
    for e in events:
        counts[e.get("event", "?")] = counts.get(e.get("event", "?"), 0) + 1

    return {
        "n_files": len({e["_file"] for e in events}),
        "events": counts,
        "D2_pdr": round(pdr, 3) if pdr is not None else None,
        "D2_latency_ms_p50": pct(0.50),
        "D2_latency_ms_p95": pct(0.95),
        "D5_gateway_gap_ms_p50": (sorted(gw_lags)[len(gw_lags) // 2] if gw_lags else None),
        "fall_suspected": counts.get("fall_suspected", 0),
        "h7_alarm": counts.get("h7_alarm", 0),
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    events = load_events(sys.argv[1:])
    print(json.dumps(analyze(events), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
