"""Kiểm thử codec khung LoRa v2.0 (`packets_lora.py`).

Chạy:  python3 test_packets_lora.py
Không dùng pytest/numpy — chỉ thư viện chuẩn Python 3.12.

Nhãn bằng chứng dùng trong tệp: ĐÓNG BĂNG (đặc tả v2.0), SUY (công thức),
GIẢ ĐỊNH (lựa chọn thiết kế), SIM (Monte Carlo). Không có giá trị ĐO nào.
"""

from __future__ import annotations

import hashlib
import hmac
import random
import struct

import lora
from packets_lora import (
    ACK_SIZE,
    ACK_TAG_BYTES,
    ACK_TOKEN_BITS,
    ACK_TOKEN_MAX,
    BATTERY_UNKNOWN,
    BEACON_SIZE,
    BEACON_TAG_BYTES,
    FLAG_BITS,
    FRAME_SIZES,
    FRAME_TYPES,
    HEARTBEAT_SIZE,
    HEARTBEAT_TAG_BYTES,
    LAB_KEY,
    MAX_PAYLOAD_BYTES,
    SOS_SIZE,
    SOS_TAG_BYTES,
    TIME_BITS,
    VERSION,
    AckFrame,
    BeaconFrame,
    Flags,
    HeartbeatFrame,
    SosFrame,
    ack_token,
    airtime_table,
    coord_table,
    encode_lat,
    encode_lon,
    frame_size,
    peek_type,
    peek_version,
    resolve_time_offset,
    simulate_token_collision,
    token_collision_probability,
    unwrap_time,
    wrap_time,
)

OTHER_KEY = b"rescuemesh-lora-wrong-key-00002"
ALLOWED_UNPACK_ERRORS = (ValueError, struct.error)


# --------------------------------------------------------------------------
# Mẫu cố định
# --------------------------------------------------------------------------


def sample_flags() -> Flags:
    return Flags(fall_auto=True, has_gps_fix=True, ack_requested=True)


def sample_sos(**overrides) -> SosFrame:
    args = dict(
        src_id=0x89ABCDEF, seq=0x1234, hop_count=7, ttl=15,
        lat=21.028511, lon=105.804817, battery_pct=87, severity=200,
        time_offset_min=12345, impact_g_x100=1234, immobility_s=300,
        node_temp_c_x10=-125, flags=sample_flags(),
    )
    args.update(overrides)
    return SosFrame(**args)


def sample_heartbeat(**overrides) -> HeartbeatFrame:
    args = dict(src_id=0x12345678, battery_pct=100, hop_count=4,
                time_offset_min=60000, flags=Flags(manual_button=True))
    args.update(overrides)
    return HeartbeatFrame(**args)


def sample_beacon(**overrides) -> BeaconFrame:
    args = dict(gw_id=0x00A1, bseq=200, hop_limit=3, time_offset_min=9999,
                load_pct=42, flags=Flags(is_relay=True))
    args.update(overrides)
    return BeaconFrame(**args)


def sample_ack(**overrides) -> AckFrame:
    args = dict(bseq=77, token=ack_token(LAB_KEY, 0x89ABCDEF, 0x1234),
                flags=Flags(ack_requested=True))
    args.update(overrides)
    return AckFrame(**args)


# --------------------------------------------------------------------------
# Hằng số và header
# --------------------------------------------------------------------------


def test_constants_frozen():
    assert VERSION == 2
    assert MAX_PAYLOAD_BYTES == 242
    assert FRAME_TYPES == {"SOS": 1, "HEARTBEAT": 2, "BEACON": 3, "ACK": 4}
    assert FRAME_SIZES == {"SOS": 36, "HEARTBEAT": 14, "BEACON": 18, "ACK": 12}
    assert (SOS_SIZE, HEARTBEAT_SIZE, BEACON_SIZE, ACK_SIZE) == (36, 14, 18, 12)
    assert (SOS_TAG_BYTES, HEARTBEAT_TAG_BYTES, BEACON_TAG_BYTES,
            ACK_TAG_BYTES) == (8, 4, 8, 5)
    assert ACK_TOKEN_BITS == 24 and ACK_TOKEN_MAX == 0xFFFFFF
    assert TIME_BITS == 16 and BATTERY_UNKNOWN == 255
    assert len(LAB_KEY) == 32


def test_flags_bit_positions_and_reserved():
    """Bit 0..6 đúng vị trí; bit7 dự trữ phải bằng 0 khi pack."""
    assert FLAG_BITS == {
        "fall_auto": 0, "manual_button": 1, "immobility_confirmed": 2,
        "low_battery": 3, "has_gps_fix": 4, "is_relay": 5,
        "ack_requested": 6, "rsv": 7,
    }
    for i, name in enumerate(("fall_auto", "manual_button",
                              "immobility_confirmed", "low_battery",
                              "has_gps_fix", "is_relay", "ack_requested")):
        assert Flags(**{name: True}).pack() == (1 << i)
    assert Flags().pack() == 0
    try:
        Flags(rsv=True).pack()
        raise AssertionError("bit7 dự trữ phải bị từ chối khi pack")
    except ValueError:
        pass
    # Bit7 đến từ không khí được BỎ QUA khi unpack (đặc tả v2.0).
    assert Flags.unpack(0xFF).rsv is False
    assert Flags.unpack(0x81).pack() == 0x01


def test_header_bits_peek_and_frame_size():
    for name, code in FRAME_TYPES.items():
        blob = None
        if name == "SOS":
            blob = sample_sos().pack(LAB_KEY)
        elif name == "HEARTBEAT":
            blob = sample_heartbeat().pack(LAB_KEY)
        elif name == "BEACON":
            blob = sample_beacon().pack(LAB_KEY)
        else:
            blob = sample_ack().pack(LAB_KEY)
        assert peek_version(blob) == 2
        assert peek_type(blob) == code
        assert blob[0] == (2 << 4) | code
        assert len(blob) == FRAME_SIZES[name]
        assert frame_size(code) == FRAME_SIZES[name]
        assert frame_size(name) == FRAME_SIZES[name]
        assert frame_size(name.lower()) == FRAME_SIZES[name]


# --------------------------------------------------------------------------
# SOS
# --------------------------------------------------------------------------


def test_sos_size_and_roundtrip():
    pkt = sample_sos()
    blob = pkt.pack(LAB_KEY)
    assert len(blob) == SOS_SIZE == FRAME_SIZES["SOS"] == pkt.SIZE
    assert SosFrame.verify(blob, LAB_KEY)
    back = SosFrame.unpack(blob)
    assert (back.src_id, back.seq, back.hop_count, back.ttl) == (
        pkt.src_id, pkt.seq, pkt.hop_count, pkt.ttl)
    assert (back.battery_pct, back.severity) == (pkt.battery_pct, pkt.severity)
    assert back.time_offset_min == pkt.time_offset_min
    assert back.impact_g_x100 == pkt.impact_g_x100
    assert back.immobility_s == pkt.immobility_s
    assert back.node_temp_c_x10 == pkt.node_temp_c_x10
    assert back.flags == pkt.flags and back.tag == blob[-8:]


def test_sos_golden_vector():
    """Vector vàng ĐÓNG BĂNG: mọi thay đổi codec phải làm test này đỏ lên."""
    blob = sample_sos().pack(LAB_KEY)
    assert blob.hex() == (
        "215189abcdef1234070f9de83fcb3d2d57c8303904d2012cff830000e0a0d5d059d27311")
    assert len(blob) == 36
    assert SosFrame.verify(blob, LAB_KEY)
    back = SosFrame.unpack(blob)
    assert back.src_id == 0x89ABCDEF and back.seq == 0x1234
    assert abs(back.lat - 21.028511) <= coord_table()["lat_res_deg"]
    assert abs(back.lon - 105.804817) <= coord_table()["lon_res_deg"]
    assert back.tag == bytes.fromhex("e0a0d5d059d27311")


def test_sos_canonical_field_offsets():
    """Kiểm tra trực tiếp từng offset theo bảng đặc tả."""
    blob = sample_sos().pack(LAB_KEY)
    assert blob[0] == 0x21                      # version 2 | SOS 1
    assert blob[1] == sample_flags().pack()     # flags
    assert blob[2:6] == bytes.fromhex("89abcdef")
    assert blob[6:8] == bytes.fromhex("1234")
    assert blob[8] == 7 and blob[9] == 15
    assert blob[10:13] == encode_lat(21.028511).to_bytes(3, "big")
    assert blob[13:16] == encode_lon(105.804817).to_bytes(3, "big")
    assert blob[16] == 87 and blob[17] == 200
    assert blob[18:20] == (12345).to_bytes(2, "big")
    assert blob[20:22] == (1234).to_bytes(2, "big")
    assert blob[22:24] == (300).to_bytes(2, "big")
    assert blob[24:26] == (-125).to_bytes(2, "big", signed=True)
    assert blob[26:28] == b"\x00\x00"
    assert blob[28:36] == blob[-8:]


def test_sos_battery_boundaries():
    for value in (0, 1, 50, 100, BATTERY_UNKNOWN):
        back = SosFrame.unpack(sample_sos(battery_pct=value).pack(LAB_KEY))
        assert back.battery_pct == value


def test_sos_battery_rejects_gap_and_overflow():
    for value in (101, 200, 254, 256, -1):
        try:
            sample_sos(battery_pct=value).pack(LAB_KEY)
            raise AssertionError(f"battery_pct={value} phải bị từ chối")
        except ValueError:
            pass


def test_sos_severity_boundaries():
    for value in (0, 1, 128, 255):
        back = SosFrame.unpack(sample_sos(severity=value).pack(LAB_KEY))
        assert back.severity == value
    try:
        sample_sos(severity=256).pack(LAB_KEY)
        raise AssertionError("severity=256 phải bị từ chối")
    except ValueError:
        pass


def test_sos_coordinate_boundaries():
    res = coord_table()
    cases = ((90.0, 180.0), (-90.0, -180.0), (0.0, 0.0), (90.0, -180.0),
             (-90.0, 180.0), (21.028511, 105.804817))
    for lat, lon in cases:
        back = SosFrame.unpack(sample_sos(lat=lat, lon=lon).pack(LAB_KEY))
        assert abs(back.lat - lat) <= res["lat_res_deg"]
        assert abs(back.lon - lon) <= res["lon_res_deg"]
    for bad_lat, bad_lon in ((90.1, 0.0), (-90.1, 0.0), (0.0, 180.1),
                             (0.0, -180.1), (float("nan"), 0.0)):
        try:
            sample_sos(lat=bad_lat, lon=bad_lon).pack(LAB_KEY)
            raise AssertionError(f"toạ độ ({bad_lat},{bad_lon}) phải bị từ chối")
        except ValueError:
            pass


def test_sos_impact_and_immobility_max():
    for value in (0, 1, 32768, 65535):
        back = SosFrame.unpack(sample_sos(
            impact_g_x100=value, immobility_s=value).pack(LAB_KEY))
        assert back.impact_g_x100 == value
        assert back.immobility_s == value
    try:
        sample_sos(impact_g_x100=65536).pack(LAB_KEY)
        raise AssertionError("impact_g_x100=65536 phải bị từ chối")
    except ValueError:
        pass


def test_sos_temperature_signed_int16():
    for value in (-32768, -125, -1, 0, 1, 250, 32767):
        back = SosFrame.unpack(
            sample_sos(node_temp_c_x10=value).pack(LAB_KEY))
        assert back.node_temp_c_x10 == value
    for value in (-32769, 32768):
        try:
            sample_sos(node_temp_c_x10=value).pack(LAB_KEY)
            raise AssertionError(f"node_temp_c_x10={value} phải bị từ chối")
        except ValueError:
            pass


def test_sos_time_wrap_16bit():
    ref = 5_000_000
    for delta in (-600, -1, 0, 1, 600):
        assert unwrap_time(wrap_time(ref + delta, TIME_BITS), ref,
                           TIME_BITS) == ref + delta
    back = SosFrame.unpack(sample_sos(time_offset_min=70000).pack(LAB_KEY))
    assert back.time_offset_min == 70000 % (1 << TIME_BITS) == 4464
    back = SosFrame.unpack(sample_sos(time_offset_min=65535).pack(LAB_KEY))
    assert back.time_offset_min == 65535
    for delta in (-5000, 0, 5000):
        ref = 1_000_000 + delta
        assert resolve_time_offset(wrap_time(ref, TIME_BITS), ref) == ref


def test_sos_reserved_must_be_zero():
    try:
        sample_sos(reserved=1).pack(LAB_KEY)
        raise AssertionError("reserved=1 phải bị từ chối khi pack")
    except ValueError:
        pass
    blob = bytearray(sample_sos().pack(LAB_KEY))
    blob[27] = 1
    try:
        SosFrame.unpack(bytes(blob))
        raise AssertionError("reserved khác 0 phải bị từ chối khi unpack")
    except ValueError:
        pass
    assert not SosFrame.verify(bytes(blob), LAB_KEY)


def test_sos_rejects_bad_version_and_type():
    blob = bytearray(sample_sos().pack(LAB_KEY))
    blob[0] = (1 << 4) | 1        # version 1
    try:
        SosFrame.unpack(bytes(blob))
        raise AssertionError("version 1 phải bị từ chối")
    except ValueError:
        pass
    blob = bytearray(sample_sos().pack(LAB_KEY))
    blob[0] = (2 << 4) | 2        # type HEARTBEAT
    try:
        SosFrame.unpack(bytes(blob))
        raise AssertionError("frame_type không khớp phải bị từ chối")
    except ValueError:
        pass


def test_sos_truncated_and_oversized():
    blob = sample_sos().pack(LAB_KEY)
    for length in (0, 1, 2, 8, 28, 35, 37, 64):
        try:
            SosFrame.unpack(blob[:length] if length < 36 else blob + b"\x00")
            raise AssertionError(f"độ dài {length} phải bị từ chối")
        except ValueError:
            pass


# --------------------------------------------------------------------------
# HEARTBEAT / BEACON / ACK
# --------------------------------------------------------------------------


def test_heartbeat_roundtrip_and_golden():
    pkt = sample_heartbeat()
    blob = pkt.pack(LAB_KEY)
    assert len(blob) == HEARTBEAT_SIZE == 14
    assert blob.hex() == "2202123456786404ea60e1bade5d"
    assert HeartbeatFrame.verify(blob, LAB_KEY)
    back = HeartbeatFrame.unpack(blob)
    assert (back.src_id, back.battery_pct, back.hop_count,
            back.time_offset_min) == (pkt.src_id, pkt.battery_pct,
                                      pkt.hop_count, pkt.time_offset_min)
    assert back.flags == pkt.flags and back.tag == blob[-4:]


def test_heartbeat_boundaries():
    for bat in (0, 100, BATTERY_UNKNOWN):
        back = HeartbeatFrame.unpack(sample_heartbeat(
            src_id=0xFFFFFFFF, hop_count=255, battery_pct=bat,
            time_offset_min=65535).pack(LAB_KEY))
        assert (back.src_id, back.hop_count, back.battery_pct,
                back.time_offset_min) == (0xFFFFFFFF, 255, bat, 65535)
    try:
        sample_heartbeat(battery_pct=101).pack(LAB_KEY)
        raise AssertionError("battery_pct=101 phải bị từ chối")
    except ValueError:
        pass


def test_beacon_roundtrip_and_golden():
    pkt = sample_beacon()
    blob = pkt.pack(LAB_KEY)
    assert len(blob) == BEACON_SIZE == 18
    assert blob.hex() == "232000a1c803270f2a00791c08e7005a6477"
    assert BeaconFrame.verify(blob, LAB_KEY)
    back = BeaconFrame.unpack(blob)
    assert (back.gw_id, back.bseq, back.hop_limit, back.time_offset_min,
            back.load_pct) == (pkt.gw_id, pkt.bseq, pkt.hop_limit,
                               pkt.time_offset_min, pkt.load_pct)
    assert back.flags == pkt.flags and back.tag == blob[-8:]
    assert blob[9] == 0 and blob[2:4] == b"\x00\xa1"


def test_beacon_reserved_and_limits():
    try:
        sample_beacon(reserved=1).pack(LAB_KEY)
        raise AssertionError("BEACON reserved=1 phải bị từ chối")
    except ValueError:
        pass
    blob = bytearray(sample_beacon().pack(LAB_KEY))
    blob[9] = 7
    try:
        BeaconFrame.unpack(bytes(blob))
        raise AssertionError("BEACON reserved khác 0 phải bị từ chối")
    except ValueError:
        pass
    for value in (0, 255):
        back = BeaconFrame.unpack(sample_beacon(
            gw_id=0xFFFF, bseq=value, hop_limit=value,
            load_pct=value, time_offset_min=65535).pack(LAB_KEY))
        assert (back.bseq, back.hop_limit, back.load_pct) == (value, value, value)
    for bad in (256, -1):
        try:
            sample_beacon(bseq=bad).pack(LAB_KEY)
            raise AssertionError(f"bseq={bad} phải bị từ chối")
        except ValueError:
            pass


def test_ack_token_is_24bit_hmac_prefix():
    material = (0x89ABCDEF).to_bytes(4, "big") + (0x1234).to_bytes(2, "big")
    expected = int.from_bytes(
        hmac.new(LAB_KEY, material, hashlib.sha256).digest()[:3], "big")
    token = ack_token(LAB_KEY, 0x89ABCDEF, 0x1234)
    assert token == expected == 0xF95595
    assert 0 <= token <= ACK_TOKEN_MAX
    for src, seq in ((0, 0), (0xFFFFFFFF, 0xFFFF), (1, 1)):
        t = ack_token(LAB_KEY, src, seq)
        assert 0 <= t <= ACK_TOKEN_MAX and t == ack_token(LAB_KEY, src, seq)
    try:
        ack_token(LAB_KEY, 1 << 32, 0)
        raise AssertionError("src_id quá 32 bit phải bị từ chối")
    except ValueError:
        pass


def test_ack_roundtrip_golden_and_for_event():
    pkt = sample_ack()
    blob = pkt.pack(LAB_KEY)
    assert len(blob) == ACK_SIZE == 12
    assert blob.hex() == "24404df9559500ba8036d14f"
    assert blob[3:6] == b"\xf9\x55\x95"
    assert AckFrame.verify(blob, LAB_KEY)
    back = AckFrame.unpack(blob)
    assert back.token == pkt.token == 0xF95595
    assert back.bseq == 77 and back.flags == pkt.flags and back.tag == blob[-5:]
    auto = AckFrame.for_event(LAB_KEY, 0x89ABCDEF, 0x1234, bseq=77,
                              flags=Flags(ack_requested=True))
    assert auto.pack(LAB_KEY) == blob


def test_ack_reserved_and_token_range():
    try:
        sample_ack(reserved=1).pack(LAB_KEY)
        raise AssertionError("ACK reserved=1 phải bị từ chối")
    except ValueError:
        pass
    blob = bytearray(sample_ack().pack(LAB_KEY))
    blob[6] = 1
    try:
        AckFrame.unpack(bytes(blob))
        raise AssertionError("ACK reserved khác 0 phải bị từ chối")
    except ValueError:
        pass
    assert len(sample_ack(token=0).pack(LAB_KEY)) == 12
    assert len(sample_ack(token=ACK_TOKEN_MAX).pack(LAB_KEY)) == 12
    try:
        sample_ack(token=1 << 24).pack(LAB_KEY)
        raise AssertionError("token quá 24 bit phải bị từ chối")
    except ValueError:
        pass


# --------------------------------------------------------------------------
# Tamper, khoá, tag
# --------------------------------------------------------------------------


def test_tamper_header_src_coord_tag_detected():
    base = sample_sos().pack(LAB_KEY)
    for off, mask, label in ((0, 0x01, "version"), (0, 0x0F, "frame_type"),
                             (1, 0x01, "flags/fall_auto"),
                             (1, 0x80, "flags bit7"),
                             (2, 0x80, "src_id"), (6, 0x01, "seq"),
                             (10, 0x01, "lat"), (13, 0x01, "lon"),
                             (17, 0x01, "severity"), (20, 0x01, "impact"),
                             (22, 0x01, "immobility"), (24, 0x01, "temp"),
                             (35, 0x01, "tag")):
        blob = bytearray(base)
        blob[off] ^= mask
        assert not SosFrame.verify(bytes(blob), LAB_KEY), label


def test_route_bytes_excluded_from_mac_documented():
    """GIẢ ĐỊNH kế thừa v1: hop/ttl do relay sửa nên không nằm trong MAC.

    Đây là quyết định thiết kế có ghi trong đặc tả; test này khoá hành vi đó
    lại để không vô tình thay đổi.
    """
    sos = bytearray(sample_sos().pack(LAB_KEY))
    sos[8] ^= 0xFF   # hop_count
    sos[9] ^= 0xFF   # ttl
    assert SosFrame.verify(bytes(sos), LAB_KEY)
    hb = bytearray(sample_heartbeat().pack(LAB_KEY))
    hb[7] ^= 0xFF    # hop_count
    assert HeartbeatFrame.verify(bytes(hb), LAB_KEY)
    bc = bytearray(sample_beacon().pack(LAB_KEY))
    bc[5] ^= 0xFF    # hop_limit
    assert BeaconFrame.verify(bytes(bc), LAB_KEY)


def test_wrong_key_fails_all_types():
    cases = ((SosFrame, sample_sos()), (HeartbeatFrame, sample_heartbeat()),
             (BeaconFrame, sample_beacon()), (AckFrame, sample_ack()))
    for cls, pkt in cases:
        blob = pkt.pack(LAB_KEY)
        assert cls.verify(blob, LAB_KEY)
        assert not cls.verify(blob, OTHER_KEY)
        assert not cls.verify(blob, OTHER_KEY + b"x")


def test_empty_key_and_missing_tag():
    blob = sample_sos().pack(LAB_KEY)
    assert SosFrame.verify(blob, b"") is False
    assert HeartbeatFrame.verify(sample_heartbeat().pack(LAB_KEY), b"") is False
    assert BeaconFrame.verify(sample_beacon().pack(LAB_KEY), b"") is False
    assert AckFrame.verify(sample_ack().pack(LAB_KEY), b"") is False
    for pkt in (sample_sos(), sample_heartbeat(), sample_beacon(), sample_ack()):
        try:
            pkt.pack()
            raise AssertionError("pack() không khoá, không tag phải bị từ chối")
        except ValueError:
            pass


def test_explicit_tag_roundtrip():
    """Tag tính sẵn (ví dụ nhận từ phần cứng) phải pack ra đúng khung cũ."""
    for pkt, tag_len in ((sample_sos(), SOS_TAG_BYTES),
                         (sample_heartbeat(), HEARTBEAT_TAG_BYTES),
                         (sample_beacon(), BEACON_TAG_BYTES),
                         (sample_ack(), ACK_TAG_BYTES)):
        blob = pkt.pack(LAB_KEY)
        pkt.tag = blob[-tag_len:]
        assert pkt.pack() == blob
        assert pkt.pack(None) == blob


def test_peek_rejects_empty_and_unknown_type():
    try:
        peek_type(b"")
        raise AssertionError("peek_type(b'') phải bị từ chối")
    except ValueError:
        pass
    try:
        peek_version(b"")
        raise AssertionError("peek_version(b'') phải bị từ chối")
    except ValueError:
        pass
    assert peek_type(bytes((0x2A,))) == 10
    for bad in (0, 5, 15):
        try:
            frame_size(bad)
            raise AssertionError(f"frame_size({bad}) phải bị từ chối")
        except ValueError:
            pass
    try:
        frame_size("KHONG-CO")
        raise AssertionError("tên khung lạ phải bị từ chối")
    except ValueError:
        pass


# --------------------------------------------------------------------------
# Airtime LoRa (SUY)
# --------------------------------------------------------------------------


def test_lora_airtime_sos_sf9_under_400ms():
    """SUY: airtime Semtech, không phải số đo. SF9/BW125/36 B ≈ 267 ms."""
    seconds = lora.LoraProfile(sf=9, bw_hz=125_000, cr=1).airtime_s(SOS_SIZE)
    assert seconds < 0.400
    assert seconds > 0.100


def test_airtime_table_shape_and_evidence():
    rows = airtime_table()
    assert len(rows) == 3 * 4
    for row in rows:
        assert row["evidence"] == "SUY"
        assert row["bytes"] == FRAME_SIZES[row["frame_type"]]
        assert row["airtime_ms"] > 0
        assert abs(row["frames_per_s"] - 1000.0 / row["airtime_ms"]) < 1e-9
    sf9_sos = [r for r in rows if r["sf"] == 9 and r["frame_type"] == "SOS"][0]
    assert sf9_sos["airtime_ms"] < 400
    # Airtime phải tăng theo kích thước khung trong cùng một SF.
    for sf in (7, 9, 12):
        group = {r["frame_type"]: r["airtime_ms"] for r in rows if r["sf"] == sf}
        assert group["ACK"] <= group["HEARTBEAT"] <= group["BEACON"] <= group["SOS"]


# --------------------------------------------------------------------------
# Va chạm token 24 bit so với 16 bit
# --------------------------------------------------------------------------


def test_token_collision_analytic_monotone_and_scale():
    probs = [token_collision_probability(n, 24)
             for n in (10, 100, 1000, 10000)]
    assert all(a < b for a, b in zip(probs, probs[1:])), probs
    assert probs[0] < 1e-5
    assert probs[2] < 0.05          # n = 1000, token 24 bit
    assert token_collision_probability(1000, 16) > 0.9   # v1 sụp
    assert probs[2] < token_collision_probability(1000, 16) / 10.0
    assert token_collision_probability(1, 24) == 0.0
    assert token_collision_probability(0, 24) == 0.0


def test_token_collision_monte_carlo_24_vs_16():
    """SIM (Monte Carlo) — chỉ là ước lượng, không phải số đo."""
    n = 1000
    p24 = token_collision_probability(n, 24)
    mc24 = simulate_token_collision(n, 24, trials=400, seed=7)
    mc16 = simulate_token_collision(n, 16, trials=400, seed=7)
    assert 0.0 <= mc24 < 0.10
    assert abs(mc24 - p24) < 0.03
    assert mc16 > 0.9
    assert mc24 < mc16 * 0.5
    # Tăng n thì xác suất MC không giảm (24 bit).
    small = simulate_token_collision(100, 24, trials=1000, seed=3)
    big = simulate_token_collision(10000, 24, trials=200, seed=3)
    assert big > small


# --------------------------------------------------------------------------
# Fuzz
# --------------------------------------------------------------------------


def test_fuzz_500_roundtrip_all_types():
    rng = random.Random(20240)
    res = coord_table()
    for _ in range(500):
        flags = Flags(
            fall_auto=bool(rng.getrandbits(1)),
            manual_button=bool(rng.getrandbits(1)),
            immobility_confirmed=bool(rng.getrandbits(1)),
            low_battery=bool(rng.getrandbits(1)),
            has_gps_fix=bool(rng.getrandbits(1)),
            is_relay=bool(rng.getrandbits(1)),
            ack_requested=bool(rng.getrandbits(1)),
        )
        bat = rng.choice((rng.randrange(101), BATTERY_UNKNOWN))
        sos = SosFrame(
            src_id=rng.randrange(1 << 32), seq=rng.randrange(1 << 16),
            hop_count=rng.randrange(256), ttl=rng.randrange(256),
            lat=rng.uniform(-90, 90), lon=rng.uniform(-180, 180),
            battery_pct=bat, severity=rng.randrange(256),
            time_offset_min=rng.randrange(1 << 20),
            impact_g_x100=rng.randrange(1 << 16),
            immobility_s=rng.randrange(1 << 16),
            node_temp_c_x10=rng.randrange(-32768, 32768),
            flags=flags,
        )
        blob = sos.pack(LAB_KEY)
        back = SosFrame.unpack(blob)
        assert len(blob) == SOS_SIZE and SosFrame.verify(blob, LAB_KEY)
        assert back.src_id == sos.src_id and back.seq == sos.seq
        assert back.impact_g_x100 == sos.impact_g_x100
        assert back.immobility_s == sos.immobility_s
        assert back.node_temp_c_x10 == sos.node_temp_c_x10
        assert back.severity == sos.severity and back.battery_pct == bat
        assert back.time_offset_min == wrap_time(sos.time_offset_min, TIME_BITS)
        assert abs(back.lat - sos.lat) <= res["lat_res_deg"]
        assert abs(back.lon - sos.lon) <= res["lon_res_deg"]
        assert back.flags == flags

        hb = HeartbeatFrame(rng.randrange(1 << 32), bat, rng.randrange(256),
                            rng.randrange(1 << 20), flags)
        hblob = hb.pack(LAB_KEY)
        assert len(hblob) == HEARTBEAT_SIZE and HeartbeatFrame.verify(hblob, LAB_KEY)
        assert HeartbeatFrame.unpack(hblob).src_id == hb.src_id

        bc = BeaconFrame(rng.randrange(1 << 16), rng.randrange(256),
                         rng.randrange(256), rng.randrange(1 << 20),
                         rng.randrange(256), flags)
        bblob = bc.pack(LAB_KEY)
        assert len(bblob) == BEACON_SIZE and BeaconFrame.verify(bblob, LAB_KEY)
        assert BeaconFrame.unpack(bblob).gw_id == bc.gw_id

        ack = AckFrame(rng.randrange(256), rng.randrange(1 << 24), flags)
        ablob = ack.pack(LAB_KEY)
        assert len(ablob) == ACK_SIZE and AckFrame.verify(ablob, LAB_KEY)
        assert AckFrame.unpack(ablob).token == ack.token


def test_fuzz_unpack_never_raises_unexpected():
    """500+ mẫu ngẫu nhiên: chỉ ValueError/struct.error được phép thoát ra."""
    rng = random.Random(99)
    classes = (SosFrame, HeartbeatFrame, BeaconFrame, AckFrame)
    sizes = (SOS_SIZE, HEARTBEAT_SIZE, BEACON_SIZE, ACK_SIZE)
    for _ in range(600):
        n = rng.choice(sizes + (rng.randrange(0, 64),))
        data = bytes(rng.getrandbits(8) for _ in range(n))
        for cls in classes:
            try:
                cls.unpack(data)
            except ALLOWED_UNPACK_ERRORS:
                pass
            assert cls.verify(data, LAB_KEY) in (True, False)
        if data:
            assert peek_type(data) == (data[0] & 0x0F)


def test_max_payload_budget_covers_all_frames():
    assert all(size <= MAX_PAYLOAD_BYTES for size in FRAME_SIZES.values())
    assert max(FRAME_SIZES.values()) == SOS_SIZE == 36


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------

if __name__ == "__main__":
    import traceback

    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} test qua")
    raise SystemExit(bool(failed))
