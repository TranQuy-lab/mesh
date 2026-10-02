#!/usr/bin/env python3
"""RescueMesh v1.0 station receiver for a Linux laptop.

Receives BLE legacy manufacturer advertisements (company 0xFFFF), decodes
24-byte SOS frames, verifies the HMAC, suppresses duplicates, and stores a
small JSONL event log.  It deliberately has no Internet dependency.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import signal
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rescuemesh.packets import SosPacket

COMPANY_ID = 0xFFFF
DEFAULT_KEY = b"device-key-for-tests"


def frame_id(data: bytes) -> str:
    # Source ID (bytes 3..6), sequence (byte 2), and tag make a stable id.
    return data[3:7].hex() + ":" + f"{data[2]:02x}" + ":" + data[-4:].hex()


class Station:
    def __init__(self, key: bytes, output: Path, verbose: bool = False):
        self.key = key
        self.output = output
        self.verbose = verbose
        self.seen: set[str] = set()
        self.count = 0
        self.valid = 0

    def handle(self, data: bytes, address: str = "unknown", rssi: int | None = None):
        if len(data) != 24:
            if self.verbose:
                print(f"[CẢNH BÁO] Nhận gói từ {address} có độ dài {len(data)} B (cần 24 B): {data.hex()}", file=sys.stderr)
            return
        if not SosPacket.verify(data, self.key):
            if self.verbose:
                print(f"[CẢNH BÁO] Nhận gói 24 B từ {address} nhưng SAI HMAC (kiểm tra lại --key)! Hex: {data.hex()}", file=sys.stderr)
            return
        fid = frame_id(data)
        if fid in self.seen:
            return
        self.seen.add(fid)
        pkt = SosPacket.unpack(data)
        event = {
            "received_at": int(time.time()),
            "source": f"0x{pkt.src_id:08x}",
            "sequence": pkt.seq,
            "hop": pkt.hop,
            "ttl": pkt.ttl,
            "latitude": round(pkt.lat, 6),
            "longitude": round(pkt.lon, 6),
            "trigger": pkt.trigger,
            "people": pkt.people,
            "need": pkt.need,
            "battery": pkt.bat,
            "rssi": rssi,
            "via": address,
            "frame_id": fid,
        }
        self.output.parent.mkdir(parents=True, exist_ok=True)
        with self.output.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        self.valid += 1
        print("SOS mới: " + json.dumps(event, ensure_ascii=False), flush=True)

    async def run(self):
        try:
            from bleak import BleakScanner
        except ImportError:
            print("Thiếu bleak. Cài một lần bằng: python3 -m pip install bleak", file=sys.stderr)
            return 2

        def detection(device, advertisement):
            if self.verbose and advertisement.manufacturer_data:
                print(f"[BLE-RAW] {device.address} (RSSI {advertisement.rssi}): MF={list(advertisement.manufacturer_data.keys())}")
            data = advertisement.manufacturer_data.get(COMPANY_ID)
            if data is not None:
                self.handle(bytes(data), device.address, advertisement.rssi)

        # Cấu hình active scan và DuplicateData=True để BlueZ không drop gói quảng bá liên tục
        scanner = BleakScanner(
            detection_callback=detection,
            scanning_mode="active",
            bluez=dict(filters=dict(DuplicateData=True, Transport="le")),
        )
        await scanner.start()
        print(f"Station đang nghe BLE (active scan, DuplicateData=True), lưu tại {self.output}. Nhấn Ctrl-C để dừng.", flush=True)
        try:
            while True:
                await asyncio.sleep(1)
        finally:
            await scanner.stop()
        return 0


def main() -> int:
    p = argparse.ArgumentParser(description="RescueMesh laptop station receiver")
    p.add_argument("--key", default=None, help="khóa HMAC dạng chữ hoặc hex")
    p.add_argument("--output", default="results/station-events.jsonl")
    p.add_argument("-v", "--verbose", action="store_true", help="in log chi tiết tất cả gói BLE nhận được")
    args = p.parse_args()
    raw = args.key.encode() if args.key is not None else DEFAULT_KEY
    if args.key and all(c in "0123456789abcdefABCDEF" for c in args.key) and len(args.key) % 2 == 0:
        raw = bytes.fromhex(args.key)
    return asyncio.run(Station(raw, Path(args.output), verbose=args.verbose).run())


if __name__ == "__main__":
    raise SystemExit(main())
