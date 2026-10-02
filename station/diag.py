#!/usr/bin/env python3
"""Công cụ chẩn đoán BLE thu nhận tín hiệu RescueMesh G0.
Kiểm tra card Bluetooth, quét tất cả thiết bị xung quanh và bóc tách gói 0xFFFF.
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rescuemesh.packets import SosPacket

COMPANY_ID = 0xFFFF
DEFAULT_KEY = b"device-key-for-tests"


async def run_diag(duration: int = 15, key: bytes = DEFAULT_KEY):
    try:
        from bleak import BleakScanner
    except ImportError:
        print("[LỖI] Chưa cài đặt bleak trong venv. Chạy: pip install bleak", file=sys.stderr)
        return 1

    devices_seen: dict[str, int] = {}
    sos_seen = 0

    print("=" * 65)
    print(" BẮT ĐẦU CHẨN ĐOÁN THU BLE RESCUEMESH")
    print(f" - Thời gian quét: {duration} giây")
    print(f" - Company ID mục tiêu: 0x{COMPANY_ID:04X} ({COMPANY_ID})")
    print(f" - Khóa HMAC kiểm tra: {key}")
    print("=" * 65)
    print("Đang quét... Hãy bật phát SOS trên điện thoại và đặt gần laptop.\n")

    def on_detect(device, adv):
        nonlocal sos_seen
        addr = device.address
        devices_seen[addr] = adv.rssi

        # Báo cáo mọi thiết bị có mang manufacturer data
        mfg = adv.manufacturer_data
        if not mfg:
            return

        for cid, data in mfg.items():
            raw = bytes(data)
            if cid == COMPANY_ID:
                sos_seen += 1
                print(f"\n>>> [PHÁT HIỆN GÓI 0xFFFF] từ {addr} (RSSI: {adv.rssi} dBm)")
                print(f"    Raw Hex ({len(raw)} bytes): {raw.hex()}")
                if len(raw) != 24:
                    print(f"    [!] Thất bại: Độ dài là {len(raw)} byte (yêu cầu đúng 24 byte).")
                    continue
                valid_hmac = SosPacket.verify(raw, key)
                if not valid_hmac:
                    print(f"    [!] Thất bại: SAI MÃ HMAC! (Kiểm tra xem khóa trên điện thoại có khớp không).")
                else:
                    pkt = SosPacket.unpack(raw)
                    print(f"    [✓] GIẢI MÃ THÀNH CÔNG:")
                    print(f"        + Nguồn (src_id): 0x{pkt.src_id:08x}")
                    print(f"        + Số thứ tự (seq): {pkt.seq}")
                    print(f"        + Tọa độ: lat={pkt.lat:.6f}, lon={pkt.lon:.6f}")
                    print(f"        + Mức độ / Nhu cầu: trigger={pkt.trigger}, need={pkt.need}, people={pkt.people}")
                    print(f"        + Pin: {pkt.bat}/15, TTL={pkt.ttl}, Hop={pkt.hop}")

    scanner = BleakScanner(
        detection_callback=on_detect,
        scanning_mode="active",
        bluez=dict(filters=dict(DuplicateData=True, Transport="le")),
    )

    await scanner.start()
    t_end = time.time() + duration
    try:
        while time.time() < t_end:
            remaining = int(t_end - time.time())
            print(f"\rĐang quét... Còn lại {remaining}s | Đã thấy {len(devices_seen)} thiết bị BLE | Gói SOS: {sos_seen}", end="", flush=True)
            await asyncio.sleep(1)
    finally:
        await scanner.stop()

    print("\n\n" + "=" * 65)
    print(" KẾT QUẢ CHẨN ĐOÁN:")
    print(f" - Tổng số thiết bị BLE phát hiện trong không gian: {len(devices_seen)}")
    print(f" - Tổng số gói RescueMesh (0xFFFF) bắt được: {sos_seen}")
    if sos_seen == 0:
        print("\n [KHUYẾN NGHỊ KHẮC PHỤC KHI KHÔNG BẮT ĐƯỢC GÓI]:")
        print(" 1. Trên điện thoại: Kiểm tra xem app đã bật 'Start Probe' / 'Bật phát SOS' chưa.")
        print(" 2. Khoảng cách: Đặt điện thoại sát cạnh bàn phím laptop (dưới 0.5m).")
        print(" 3. Wi-Fi: Tắt tạm Wi-Fi trên laptop hoặc chuyển sang băng tần 5GHz để tránh nhiễu 2.4GHz.")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    dur = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    asyncio.run(run_diag(duration=dur))
