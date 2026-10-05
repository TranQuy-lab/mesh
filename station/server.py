#!/usr/bin/env python3
"""RescueSOS-Phone — khâu ④ + ⑤: server bản đồ cho Ban chỉ huy / đội cứu hộ.

- POST /api/sos  : app đẩy hàng đợi SOS (khâu ③ cổng ra HTTP).
- GET  /api/sos  : danh sách SOS đang hoạt động (gộp theo máy gửi).
- GET  /map      : bản đồ Leaflet + bảng la bàn (cứu hộ mở trình duyệt).
- GET  /health   : kiểm tra sống.
- BLE: song song vẫn nghe quảng cáo BLE 0xFFFF trực tiếp (Station cũ),
  phục vụ demo trong phòng không Internet.

Chạy: python3 station/server.py [--port 8787] [--no-ble]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import threading
import time
from collections import defaultdict
from pathlib import Path

from flask import Flask, jsonify, request, Response

from receiver import Station  # noqa: E402  (cùng thư mục station/)

TRIGGER_NAMES = {1: "tay", 2: "ngã", 3: "chìm"}


class SosStore:
    """Gộp SOS theo máy gửi: bản mới nhất theo seq, đếm số lần nhận."""

    def __init__(self, output: Path):
        self.output = output
        self.lock = threading.Lock()
        self.events: dict[str, dict] = {}

    def ingest(self, record: dict, via: str) -> bool:
        fid = str(record.get("frame_id") or "")
        src = str(record.get("source") or "?")
        if not fid:
            return False
        now = int(time.time())
        rec = dict(record)
        rec["received_at"] = now
        rec["via"] = via
        with self.lock:
            prev = self.events.get(fid)
            if prev is not None:
                return False
            self.events[fid] = rec
            self.output.parent.mkdir(parents=True, exist_ok=True)
            with self.output.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            return True

    def active(self, max_age_s: int = 6 * 3600) -> list[dict]:
        now = int(time.time())
        per_src: dict[str, dict] = {}
        counts: dict[str, int] = defaultdict(int)
        with self.lock:
            for rec in self.events.values():
                src = rec["source"]
                counts[src] += 1
                cur = per_src.get(src)
                if cur is None or (rec.get("sequence", 0), rec["received_at"]) > \
                        (cur.get("sequence", 0), cur["received_at"]):
                    per_src[src] = rec
        out = []
        for src, rec in per_src.items():
            age = now - rec["received_at"]
            if age > max_age_s:
                continue
            out.append({
                "source": src,
                "latitude": rec.get("latitude"),
                "longitude": rec.get("longitude"),
                "trigger": rec.get("trigger", 1),
                "trigger_name": TRIGGER_NAMES.get(rec.get("trigger", 1), "?"),
                "people": rec.get("people"),
                "need": rec.get("need"),
                "battery": rec.get("battery"),
                "gps_fix": rec.get("gps_fix"),
                "hop": rec.get("hop"),
                "sequence": rec.get("sequence"),
                "first_seen": min(e["received_at"] for e in self.events.values()
                                  if e["source"] == src),
                "last_seen": rec["received_at"],
                "age_s": age,
                "frames": counts[src],
            })
        out.sort(key=lambda r: r["last_seen"], reverse=True)
        return out


app = Flask(__name__)
store: SosStore = None  # type: ignore[assignment]


@app.post("/api/sos")
def post_sos():
    body = request.get_json(silent=True) or {}
    frames = body.get("frames") or []
    accepted = 0
    for rec in frames:
        if isinstance(rec, dict) and store.ingest(rec, via="http"):
            accepted += 1
    return jsonify(ok=True, accepted=accepted)


@app.get("/api/sos")
def get_sos():
    return jsonify(server_time=int(time.time()), sos=store.active())


@app.get("/health")
def health():
    return jsonify(ok=True, events=len(store.events))


@app.get("/map")
def map_page() -> Response:
    return Response(MAP_HTML, mimetype="text/html")


MAP_HTML = """<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RescueSOS — Bản đồ SOS</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
  html,body,#map{height:100%;margin:0}
  #panel{position:absolute;top:8px;right:8px;z-index:1000;background:#fff;
    padding:10px 12px;border-radius:8px;box-shadow:0 2px 8px #0003;
    font:13px/1.5 system-ui;max-width:320px;max-height:70vh;overflow:auto}
  #panel h3{margin:0 0 6px;font-size:14px}
  .row{padding:4px 0;border-bottom:1px solid #eee;cursor:pointer}
  .muted{color:#666}
</style></head><body>
<div id="map"></div>
<div id="panel"><h3>SOS đang hoạt động (<span id="n">0</span>)</h3>
<div id="list" class="muted">Đang tải…</div></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const map = L.map('map').setView([16.0, 107.0], 6);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',
  {attribution:'© OpenStreetMap'}).addTo(map);
let markers = {};
let myPos = null;
navigator.geolocation && navigator.geolocation.watchPosition(
  p => { myPos = [p.coords.latitude, p.coords.longitude]; refresh(); },
  null, {enableHighAccuracy: true});

function bearing(a, b) {
  const toR = x => x * Math.PI / 180;
  const p1 = toR(a[0]), p2 = toR(b[0]), dl = toR(b[1] - a[1]);
  const y = Math.sin(dl) * Math.cos(p2);
  const x = Math.cos(p1)*Math.sin(p2) - Math.sin(p1)*Math.cos(p2)*Math.cos(dl);
  return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
}
function dist(a, b) {
  const R = 6371000, toR = x => x * Math.PI / 180;
  const dp = toR(b[0]-a[0]), dl = toR(b[1]-a[1]);
  const h = Math.sin(dp/2)**2 + Math.cos(toR(a[0]))*Math.cos(toR(b[0]))*Math.sin(dl/2)**2;
  return 2 * R * Math.atan2(Math.sqrt(h), Math.sqrt(1-h));
}
const OCT = ['B','ĐB','Đ','ĐN','N','TN','T','TB'];
const octant = d => OCT[Math.round(d/45) % 8];

async function refresh() {
  try {
    const r = await fetch('/api/sos'); const data = await r.json();
    document.getElementById('n').textContent = data.sos.length;
    const list = document.getElementById('list'); list.innerHTML = '';
    const seen = new Set();
    for (const s of data.sos) {
      seen.add(s.source);
      if (!markers[s.source]) {
        markers[s.source] = L.marker([s.latitude, s.longitude]).addTo(map);
      }
      markers[s.source].setLatLng([s.latitude, s.longitude])
        .bindPopup(`<b>SOS ${s.source}</b><br>${s.trigger_name} • hop ${s.hop} • pin ${s.battery}/15
          <br>${new Date(s.last_seen*1000).toLocaleTimeString()} (${s.age_s}s trước)`);
      let line = `<div class="row"><b>${s.source}</b> — ${s.trigger_name}`;
      if (myPos && s.latitude != null) {
        const d = dist(myPos, [s.latitude, s.longitude]);
        const b = bearing(myPos, [s.latitude, s.longitude]);
        line += `<br>${Math.round(d)} m • hướng ${octant(b)} (${Math.round(b)}°)`;
      }
      line += `<br><span class="muted">hop ${s.hop} • ${s.frames} khung • ${s.age_s}s trước</span></div>`;
      list.insertAdjacentHTML('beforeend', line);
    }
    for (const k of Object.keys(markers)) {
      if (!seen.has(k)) { map.removeLayer(markers[k]); delete markers[k]; }
    }
  } catch (e) { /* server tạm mất — thử lại chu kỳ sau */ }
}
refresh(); setInterval(refresh, 5000);
</script></body></html>"""


def ble_thread(key: bytes, output: Path, verbose: bool):
    """Nghe BLE trực tiếp (dự phòng khi app không đẩy được HTTP)."""
    try:
        asyncio.run(Station(key, output, verbose=verbose).run())
    except Exception as e:  # BLE lỗi không được giết server HTTP
        print(f"[BLE] dừng: {e}", flush=True)


def main() -> int:
    global store
    p = argparse.ArgumentParser(description="RescueSOS server bản đồ")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8787)
    p.add_argument("--key", default=None, help="khóa HMAC chữ/hex (mặc định key lab)")
    p.add_argument("--output", default="results/sos-received.jsonl")
    p.add_argument("--no-ble", action="store_true", help="tắt luồng nghe BLE")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    raw = args.key.encode() if args.key is not None else b"device-key-for-tests"
    if args.key and all(c in "0123456789abcdefABCDEF" for c in args.key) and len(args.key) % 2 == 0:
        raw = bytes.fromhex(args.key)

    out = Path(args.output)
    store = SosStore(out)
    if not args.no_ble:
        threading.Thread(target=ble_thread, args=(raw, out, args.verbose),
                         daemon=True, name="ble").start()
    print(f"Server bản đồ: http://{args.host}:{args.port}/map — lưu {out}", flush=True)
    app.run(host=args.host, port=args.port, threaded=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
