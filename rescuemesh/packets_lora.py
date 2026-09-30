"""Codec khung LoRa v2.0 cho RescueMesh-LoRa.

Bối cảnh chuyển hướng
---------------------
Bản v1 (`packets.py`) giả định BLE legacy advertising và có điện thoại trong
vòng lặp. Dự án đã CHUYỂN HƯỚNG: bỏ BLE, chỉ dùng **một loại sóng duy nhất là
LoRa**, và **không có điện thoại trong vòng lặp** (điện thoại không có LoRa).
Vì vậy ngân sách 24 byte của BLE không còn là ràng buộc; khung v2 dài hơn và
mang thêm trạng thái cứu hộ.

Khung v2.0 ở đây là ĐẶC TẢ ĐÓNG BĂNG của nhóm: cài đúng từng byte, không tự
ý đổi. Codec thuần Python chuẩn (`hashlib`, `hmac`, `struct`, `random`), không
phụ thuộc thư viện ngoài, để chạy được trên máy trạm lẫn về sau trên firmware.

Quy tắc bằng chứng
------------------
Mỗi hằng số đều ghi nhãn nguồn gốc ngay tại chỗ khai báo:

- ``ĐÓNG BĂNG``: con số do đặc tả v2.0 của nhóm chốt, không phải đo.
- ``SUY``: suy ra từ công thức/tài liệu chuẩn (ví dụ airtime Semtech).
- ``GIẢ ĐỊNH``: lựa chọn thiết kế chưa được kiểm chứng.
- ``ĐO``: chỉ dùng khi có số liệu đo trên thiết bị thật — trong tệp này KHÔNG
  có giá trị nào mang nhãn ``ĐO``.
- ``SIM``: kết quả mô phỏng Monte Carlo, chỉ dùng để ước lượng.

Không có số liệu đo hay DOI nào được bịa trong tệp này. Các nhận xét chỉ mang
tính kỹ thuật, không phải tuyên bố khoa học.

Ghi chú lịch sử bắt buộc
------------------------
ACK của v1 dùng token 16 bit và được chứng minh là sụp đổ ở quy mô ≥ 1000 nút
(xác suất va chạm gần 1). v2 dùng token **24 bit**; xem
`token_collision_probability`, `simulate_token_collision` và bảng in ở
``__main__`` (có cả cột 16 bit để so sánh trực tiếp).

Cách dùng
---------
    python3 packets_lora.py      # in bảng kích thước, bảng airtime, bảng va chạm
"""

from __future__ import annotations

import hashlib
import hmac
import math
import random
from dataclasses import dataclass, field

import lora
from packets import (
    coord_resolution_deg,
    coord_resolution_m,
    decode_lat,
    decode_lon,
    encode_lat,
    encode_lon,
    unwrap_time,
    wrap_time,
)

# --------------------------------------------------------------------------
# Hằng số khung — ĐÓNG BĂNG theo đặc tả v2.0
# --------------------------------------------------------------------------

#: Phiên bản giao thức nhét vào 4 bit cao của byte 0. ĐÓNG BĂNG.
VERSION = 2
#: Version cho khung SOS v2.1 (dùng 2 byte dự trữ cho trường ánh xạ CAP).
VERSION_CAP = 3

#: Ngân sách payload thiết kế cho LoRa (byte).
#: GIẢ ĐỊNH — kế thừa trần payload lớn nhất kiểu LoRaWAN (242 B), nhỏ hơn trần
#: header tường minh 255 B của SX1262. Đây là ngân sách thiết kế, KHÔNG phải
#: giới hạn đo được của modem.
MAX_PAYLOAD_BYTES = 242

#: Bảng ánh xạ tên khung → mã 4 bit thấp của byte 0. ĐÓNG BĂNG.
FRAME_TYPES = {
    "SOS": 1,
    "HEARTBEAT": 2,
    "BEACON": 3,
    "ACK": 4,
}

FRAME_NAMES = {v: k for k, v in FRAME_TYPES.items()}

#: Kích thước khung theo tên (byte). ĐÓNG BĂNG — mỗi khung đúng bằng con số
#: này, cả khi pack lẫn khi unpack.
FRAME_SIZES = {
    "SOS": 36,
    "HEARTBEAT": 14,
    "BEACON": 18,
    "ACK": 12,
}

#: Kích thước khung theo mã số, dùng cho `frame_size`.
_SIZE_BY_TYPE = {FRAME_TYPES[name]: size for name, size in FRAME_SIZES.items()}

#: Header chung 2 byte (version|type, flags). ĐÓNG BĂNG.
HEADER_SIZE = 2

SOS_SIZE = FRAME_SIZES["SOS"]
HEARTBEAT_SIZE = FRAME_SIZES["HEARTBEAT"]
BEACON_SIZE = FRAME_SIZES["BEACON"]
ACK_SIZE = FRAME_SIZES["ACK"]

#: Độ dài tag HMAC-SHA256 bị cắt cho từng loại khung (byte). ĐÓNG BĂNG.
SOS_TAG_BYTES = 8
HEARTBEAT_TAG_BYTES = 4
BEACON_TAG_BYTES = 8
ACK_TAG_BYTES = 5

#: Token ACK 24 bit. ĐÓNG BĂNG — v1 dùng 16 bit và sụp ở ≥ 1000 nút.
ACK_TOKEN_BITS = 24
ACK_TOKEN_BYTES = 3
ACK_TOKEN_MAX = (1 << ACK_TOKEN_BITS) - 1

#: 255 = "không biết" mức pin. ĐÓNG BĂNG.
BATTERY_UNKNOWN = 255

#: Thời gian dạng modulo 16 bit (phút). ĐÓNG BĂNG.
TIME_BITS = 16
TIME_WRAP_MINUTES = 1 << TIME_BITS

#: Vị trí bit trong byte `flags`. ĐÓNG BĂNG.
#: bit7 dự trữ: PHẢI bằng 0 khi pack, BỎ QUA khi unpack.
FLAG_BITS = {
    "fall_auto": 0,
    "manual_button": 1,
    "immobility_confirmed": 2,
    "low_battery": 3,
    "has_gps_fix": 4,
    "is_relay": 5,
    "ack_requested": 6,
    "rsv": 7,
}
FLAG_RESERVED_MASK = 1 << FLAG_BITS["rsv"]

#: KHOÁ LAB 32 BYTE — chỉ để chạy thử và kiểm thử, KHÔNG dùng hiện trường.
#: GIẢ ĐỊNH — khoá thật phải được nạp riêng trên thiết bị, không nằm trong mã.
LAB_KEY = b"rescuemesh-lora-v2-lab-key-00001"
assert len(LAB_KEY) == 32, "LAB_KEY phải đúng 32 byte"

#: Ngưỡng hợp lệ khi pack mức pin: 0..100 hoặc 255. GIẢ ĐỊNH — chọn từ chối
#: giá trị 101..254 để bắt lỗi mã hoá sớm; khi unpack không từ chối vì byte
#: nhận được từ không khí có thể do phiên bản khác.
BATTERY_VALID = tuple(range(0, 101)) + (BATTERY_UNKNOWN,)

#: Danh sách n và số vòng Monte Carlo cho bảng va chạm token.
#: GIẢ ĐỊNH — chọn để bảng chạy xong trong vài giây bằng Python thuần.
COLLISION_NODES = (10, 100, 1000, 10000)
COLLISION_TRIALS = {10: 2000, 100: 2000, 1000: 2000, 10000: 400}


# --------------------------------------------------------------------------
# Kiểm tra giá trị và helper byte
# --------------------------------------------------------------------------


def _check(value: int, bits: int, name: str) -> int:
    """Bảo đảm `value` là số nguyên không dấu vừa `bits` bit."""
    if not isinstance(value, int):
        raise TypeError(f"{name} phải là int, nhận {type(value).__name__}")
    if not 0 <= value < (1 << bits):
        raise ValueError(f"{name}={value} không vừa {bits} bit")
    return value


def _check_i16(value: int, name: str) -> int:
    """Bảo đảm `value` vừa int16 có dấu (làm tròn nếu là số thực)."""
    v = int(round(value))
    if not -32768 <= v <= 32767:
        raise ValueError(f"{name}={v} không vừa int16 có dấu")
    return v


def _check_battery(value: int, name: str = "battery_pct") -> int:
    """Kiểm tra mức pin khi pack: 0..100 hoặc 255 (không biết)."""
    v = _check(value, 8, name)
    if v not in BATTERY_VALID:
        raise ValueError(
            f"{name}={v} phải trong 0..100 hoặc {BATTERY_UNKNOWN} (không biết)"
        )
    return v


def _u24be(value: int, name: str) -> bytes:
    return _check(value, 24, name).to_bytes(3, "big")


def _read_u24be(data: bytes, off: int) -> int:
    if off + 3 > len(data):
        raise ValueError("thiếu dữ liệu u24")
    return int.from_bytes(data[off : off + 3], "big")


# --------------------------------------------------------------------------
# Header chung 2 byte và flags
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Flags:
    """Byte 1 của header: 7 cờ trạng thái, bit7 dự trữ."""

    fall_auto: bool = False
    manual_button: bool = False
    immobility_confirmed: bool = False
    low_battery: bool = False
    has_gps_fix: bool = False
    is_relay: bool = False
    ack_requested: bool = False
    rsv: bool = False

    def pack(self) -> int:
        """Đóng gói thành 1 byte; bit7 PHẢI bằng 0 (ĐÓNG BĂNG)."""
        if self.rsv:
            raise ValueError("bit7 của flags là dự trữ và phải bằng 0 khi pack")
        out = 0
        for name, bit in FLAG_BITS.items():
            if name == "rsv":
                continue
            if getattr(self, name):
                out |= 1 << bit
        return out

    @staticmethod
    def unpack(byte: int) -> "Flags":
        """Giải mã 1 byte; bit7 BỎ QUA (không báo lỗi) theo đặc tả."""
        _check(byte, 8, "flags")
        return Flags(
            fall_auto=bool(byte & (1 << FLAG_BITS["fall_auto"])),
            manual_button=bool(byte & (1 << FLAG_BITS["manual_button"])),
            immobility_confirmed=bool(byte & (1 << FLAG_BITS["immobility_confirmed"])),
            low_battery=bool(byte & (1 << FLAG_BITS["low_battery"])),
            has_gps_fix=bool(byte & (1 << FLAG_BITS["has_gps_fix"])),
            is_relay=bool(byte & (1 << FLAG_BITS["is_relay"])),
            ack_requested=bool(byte & (1 << FLAG_BITS["ack_requested"])),
            rsv=False,
        )


def _pack_header(frame_type: int, flags: Flags, version: int = VERSION) -> bytes:
    """Byte 0 = version 4 bit cao | frame_type 4 bit thấp; byte 1 = flags."""
    if not isinstance(flags, Flags):
        raise TypeError("flags phải là Flags")
    b0 = ((_check(version, 4, "version") << 4)
          | _check(frame_type, 4, "frame_type"))
    return bytes((b0, flags.pack()))


def _parse_header_any(
    data: bytes, expected_type: int, allowed_versions: tuple[int, ...]
) -> tuple[int, Flags]:
    """Đọc header, chấp nhận danh sách version; trả `(version, flags)`."""
    if len(data) < HEADER_SIZE:
        raise ValueError(f"cần ít nhất {HEADER_SIZE} byte header")
    ver = data[0] >> 4
    ftype = data[0] & 0x0F
    if ver not in allowed_versions:
        raise ValueError(f"version={ver} không thuộc {allowed_versions}")
    if ftype != expected_type:
        raise ValueError(
            f"frame_type={ftype} không phải {expected_type} "
            f"({FRAME_NAMES.get(expected_type, '?')})"
        )
    return ver, Flags.unpack(data[1])


def _parse_header(data: bytes, expected_type: int) -> tuple[int, Flags]:
    """Đọc và kiểm tra header cho các khung chỉ có một version."""
    _ver, flags = _parse_header_any(data, expected_type, (VERSION,))
    return expected_type, flags


def peek_type(data: bytes) -> int:
    """Đọc `frame_type` (4 bit thấp byte 0) mà không kiểm tra phần thân."""
    if len(data) < 1:
        raise ValueError("cần ít nhất 1 byte để đọc frame_type")
    return data[0] & 0x0F


def peek_version(data: bytes) -> int:
    """Đọc `version` (4 bit cao byte 0)."""
    if len(data) < 1:
        raise ValueError("cần ít nhất 1 byte để đọc version")
    return data[0] >> 4


def frame_size(frame_type: int | str) -> int:
    """Kích thước khung (byte) theo mã số hoặc tên; ném ValueError nếu lạ."""
    if isinstance(frame_type, str):
        name = frame_type.upper()
        if name not in FRAME_SIZES:
            raise ValueError(f"tên khung lạ: {frame_type!r}")
        return FRAME_SIZES[name]
    ftype = _check(frame_type, 4, "frame_type")
    if ftype not in _SIZE_BY_TYPE:
        raise ValueError(f"frame_type={ftype} không có trong đặc tả v2.0")
    return _SIZE_BY_TYPE[ftype]


def _valid_header(
    data: bytes, expected_type: int,
    allowed_versions: tuple[int, ...] = (VERSION,),
) -> bool:
    """Kiểm tra nhanh header (không ném lỗi) cho vùng xác thực."""
    return (
        len(data) >= HEADER_SIZE
        and (data[0] >> 4) in allowed_versions
        and (data[0] & 0x0F) == expected_type
    )


# --------------------------------------------------------------------------
# HMAC và vùng được xác thực
# --------------------------------------------------------------------------
#
# GIẢ ĐỊNH (kế thừa quy ước v1): byte định tuyến do relay sửa trên đường đi
# KHÔNG nằm trong MAC đầu-cuối, vì nếu nằm trong MAC thì mỗi bước chuyển tiếp
# đều phải ký lại và nút relay phải giữ khoá thiết bị. Cụ thể v2 bỏ qua:
#   - SOS:       hop_count (offset 8) và ttl (offset 9)
#   - HEARTBEAT: hop_count (offset 7)
#   - BEACON:    hop_limit (offset 5)
#   - ACK:       không có trường định tuyến
# Đây là giới hạn an ninh đã ghi trong đặc tả: kẻ tấn công có thể sửa hop/ttl
# mà không làm hỏng MAC. Bù lại, các trường còn lại (kể cả toàn bộ flags) đều
# được xác thực.


def _tag(key: bytes, authenticated: bytes, n_bytes: int) -> bytes:
    """HMAC-SHA256 rồi cắt còn `n_bytes` byte."""
    if not key:
        raise ValueError("cần khóa HMAC không rỗng")
    return hmac.new(key, authenticated, hashlib.sha256).digest()[:n_bytes]


def _sos_authenticated(prefix: bytes) -> bytes:
    """Bỏ hop_count (8) và ttl (9) khỏi vùng xác thực SOS."""
    return prefix[0:8] + prefix[10:]


def _heartbeat_authenticated(prefix: bytes) -> bytes:
    """Bỏ hop_count (7) khỏi vùng xác thực HEARTBEAT."""
    return prefix[0:7] + prefix[8:]


def _beacon_authenticated(prefix: bytes) -> bytes:
    """Bỏ hop_limit (5) khỏi vùng xác thực BEACON."""
    return prefix[0:5] + prefix[6:]


class _FlagView:
    """Tiện ích: đọc cờ trực tiếp trên khung (`frame.fall_auto`, ...)."""

    flags: Flags

    @property
    def fall_auto(self) -> bool:
        return self.flags.fall_auto

    @property
    def manual_button(self) -> bool:
        return self.flags.manual_button

    @property
    def immobility_confirmed(self) -> bool:
        return self.flags.immobility_confirmed

    @property
    def low_battery(self) -> bool:
        return self.flags.low_battery

    @property
    def has_gps_fix(self) -> bool:
        return self.flags.has_gps_fix

    @property
    def is_relay(self) -> bool:
        return self.flags.is_relay

    @property
    def ack_requested(self) -> bool:
        return self.flags.ack_requested


# --------------------------------------------------------------------------
# SOS — 36 byte
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class CapFields:
    """Trường ánh xạ CAP + lớp độ chính xác vị trí — khung SOS **v2.1**.

    16 bit tại offset 26–27 của SOS (trước đây là `reserved`)::

        bit 15–12  net_id              4 bit  (mã miền/triển khai)
        bit 11–9   cap_severity        3 bit  (0 Unknown, 1 Extreme, 2 Severe, 3 Moderate, 4 Minor)
        bit  8–6   cap_urgency         3 bit  (0 Unknown, 1 Immediate, 2 Expected, 3 Future, 4 Past)
        bit  5–3   cap_certainty       3 bit  (0 Unknown, 1 Observed, 2 Likely, 3 Possible, 4 Unlikely)
        bit  2–0   pos_accuracy_class  3 bit  (0 không biết … 6 < 3 km, 7 không có fix)

    Giá trị 5–7 của ba trục CAP được để dự trữ cho tương lai. Nguồn: CAP v1.2
    (OASIS Standard 01-07-2010) yêu cầu `sender` định danh toàn cầu (⇒ `net_id`),
    và 3GPP TS 23.032 yêu cầu mô tả sai số kèm điểm (⇒ `pos_accuracy_class`).
    """

    net_id: int = 0
    severity: int = 0
    urgency: int = 0
    certainty: int = 0
    pos_accuracy_class: int = 0

    def pack(self) -> int:
        """Đóng gói thành số nguyên 16 bit."""
        _check(self.net_id, 4, "net_id")
        _check(self.severity, 3, "cap_severity")
        _check(self.urgency, 3, "cap_urgency")
        _check(self.certainty, 3, "cap_certainty")
        _check(self.pos_accuracy_class, 3, "pos_accuracy_class")
        return ((self.net_id << 12) | (self.severity << 9) | (self.urgency << 6)
                | (self.certainty << 3) | self.pos_accuracy_class)

    @staticmethod
    def unpack(value: int) -> "CapFields":
        """Giải mã số nguyên 16 bit thành `CapFields`."""
        if not (0 <= value <= 0xFFFF):
            raise ValueError("CapFields phải nằm trong 16 bit")
        return CapFields(
            net_id=(value >> 12) & 0x0F,
            severity=(value >> 9) & 0x07,
            urgency=(value >> 6) & 0x07,
            certainty=(value >> 3) & 0x07,
            pos_accuracy_class=value & 0x07,
        )


@dataclass
class SosFrame(_FlagView):
    """SOS v2.0 (36 byte).

    Bố cục: header 2 | src_id 4 | seq 2 | hop_count 1 | ttl 1 | lat 3 | lon 3 |
    battery_pct 1 | severity 1 | time_offset_min 2 | impact_g_x100 2 |
    immobility_s 2 | node_temp_c_x10 2 | reserved 2 | tag 8.
    """

    src_id: int
    seq: int
    hop_count: int
    ttl: int
    lat: float
    lon: float
    battery_pct: int
    severity: int
    time_offset_min: int
    impact_g_x100: int
    immobility_s: int
    node_temp_c_x10: int
    flags: Flags = field(default_factory=Flags)
    reserved: int = 0
    cap: "CapFields | None" = None
    tag: bytes = b""

    SIZE = SOS_SIZE
    TYPE = FRAME_TYPES["SOS"]

    def _prefix(self) -> bytes:
        if _check(self.reserved, 16, "reserved") != 0:
            raise ValueError("SOS reserved là trường dự trữ và phải bằng 0")
        if len(self.tag) and len(self.tag) != SOS_TAG_BYTES:
            raise ValueError(f"tag SOS phải đúng {SOS_TAG_BYTES} byte")
        # `cap` khác None ⇒ khung v2.1: 2 byte cuối mang trường CAP.
        version = VERSION_CAP if self.cap is not None else VERSION
        tail = (self.cap.pack() if self.cap is not None else self.reserved)
        return (
            _pack_header(self.TYPE, self.flags, version)
            + _check(self.src_id, 32, "src_id").to_bytes(4, "big")
            + _check(self.seq, 16, "seq").to_bytes(2, "big")
            + bytes((_check(self.hop_count, 8, "hop_count"),
                     _check(self.ttl, 8, "ttl")))
            + _u24be(encode_lat(self.lat), "lat")
            + _u24be(encode_lon(self.lon), "lon")
            + bytes((_check_battery(self.battery_pct),
                     _check(self.severity, 8, "severity")))
            + wrap_time(self.time_offset_min, TIME_BITS).to_bytes(2, "big")
            + _check(self.impact_g_x100, 16, "impact_g_x100").to_bytes(2, "big")
            + _check(self.immobility_s, 16, "immobility_s").to_bytes(2, "big")
            + _check_i16(self.node_temp_c_x10, "node_temp_c_x10").to_bytes(
                2, "big", signed=True)
            + _check(tail, 16, "cap/reserved").to_bytes(2, "big")
        )

    def pack(self, key: bytes | None = None) -> bytes:
        """Đóng gói SOS. Cần `key` (tính tag) hoặc `self.tag` đã đặt sẵn."""
        prefix = self._prefix()
        tag = self.tag or (_tag(key, _sos_authenticated(prefix), SOS_TAG_BYTES)
                           if key else b"")
        if len(tag) != SOS_TAG_BYTES:
            raise ValueError(f"SOS cần khóa hoặc tag đúng {SOS_TAG_BYTES} byte")
        out = prefix + tag
        if len(out) != SOS_SIZE:
            raise AssertionError(f"SOS phải là {SOS_SIZE} byte, đang là {len(out)}")
        return out

    @staticmethod
    def unpack(data: bytes) -> "SosFrame":
        """Giải mã SOS đúng 36 byte; reserved khác 0 bị coi là lỗi."""
        if len(data) != SOS_SIZE:
            raise ValueError(f"SOS phải đúng {SOS_SIZE} byte, nhận {len(data)}")
        ver, flags = _parse_header_any(
            data, FRAME_TYPES["SOS"], (VERSION, VERSION_CAP))
        off = HEADER_SIZE
        src_id = int.from_bytes(data[off : off + 4], "big"); off += 4
        seq = int.from_bytes(data[off : off + 2], "big"); off += 2
        hop_count = data[off]; off += 1
        ttl = data[off]; off += 1
        lat_raw = _read_u24be(data, off); off += 3
        lon_raw = _read_u24be(data, off); off += 3
        battery_pct = data[off]; off += 1
        severity = data[off]; off += 1
        time_offset_min = int.from_bytes(data[off : off + 2], "big"); off += 2
        impact_g_x100 = int.from_bytes(data[off : off + 2], "big"); off += 2
        immobility_s = int.from_bytes(data[off : off + 2], "big"); off += 2
        node_temp_c_x10 = int.from_bytes(data[off : off + 2], "big", signed=True)
        off += 2
        tail = int.from_bytes(data[off : off + 2], "big"); off += 2
        cap: CapFields | None = None
        reserved = 0
        if ver == VERSION_CAP:
            # v2.1: hai byte cuối là trường CAP + lớp độ chính xác vị trí.
            cap = CapFields.unpack(tail)
        elif tail != 0:
            raise ValueError(f"SOS reserved phải bằng 0, nhận {tail}")
        return SosFrame(
            src_id=src_id, seq=seq, hop_count=hop_count, ttl=ttl,
            lat=decode_lat(lat_raw), lon=decode_lon(lon_raw),
            battery_pct=battery_pct, severity=severity,
            time_offset_min=time_offset_min, impact_g_x100=impact_g_x100,
            immobility_s=immobility_s, node_temp_c_x10=node_temp_c_x10,
            flags=flags, reserved=reserved, cap=cap,
            tag=data[off : off + SOS_TAG_BYTES],
        )

    @staticmethod
    def verify(data: bytes, key: bytes) -> bool:
        """Kiểm tra HMAC 64 bit. Khoá rỗng ⇒ False (không ném lỗi)."""
        if not key or len(data) != SOS_SIZE:
            return False
        if not _valid_header(data, FRAME_TYPES["SOS"], (VERSION, VERSION_CAP)):
            return False
        prefix = data[:-SOS_TAG_BYTES]
        # Ở v2.0 hai byte cuối là `reserved` (phải 0); ở v2.1 chúng mang trường CAP.
        if data[0] >> 4 == VERSION and int.from_bytes(prefix[26:28], "big") != 0:
            return False
        expected = _tag(key, _sos_authenticated(prefix), SOS_TAG_BYTES)
        return hmac.compare_digest(data[-SOS_TAG_BYTES:], expected)


# --------------------------------------------------------------------------
# HEARTBEAT — 14 byte
# --------------------------------------------------------------------------


@dataclass
class HeartbeatFrame(_FlagView):
    """HEARTBEAT v2.0 (14 byte).

    Bố cục: header 2 | src_id 4 | battery_pct 1 | hop_count 1 |
    time_offset_min 2 | tag 4.
    """

    src_id: int
    battery_pct: int
    hop_count: int
    time_offset_min: int
    flags: Flags = field(default_factory=Flags)
    tag: bytes = b""

    SIZE = HEARTBEAT_SIZE
    TYPE = FRAME_TYPES["HEARTBEAT"]

    def _prefix(self) -> bytes:
        if len(self.tag) and len(self.tag) != HEARTBEAT_TAG_BYTES:
            raise ValueError(f"tag HEARTBEAT phải đúng {HEARTBEAT_TAG_BYTES} byte")
        return (
            _pack_header(self.TYPE, self.flags)
            + _check(self.src_id, 32, "src_id").to_bytes(4, "big")
            + bytes((_check_battery(self.battery_pct),
                     _check(self.hop_count, 8, "hop_count")))
            + wrap_time(self.time_offset_min, TIME_BITS).to_bytes(2, "big")
        )

    def pack(self, key: bytes | None = None) -> bytes:
        prefix = self._prefix()
        tag = self.tag or (_tag(key, _heartbeat_authenticated(prefix),
                                HEARTBEAT_TAG_BYTES) if key else b"")
        if len(tag) != HEARTBEAT_TAG_BYTES:
            raise ValueError(
                f"HEARTBEAT cần khóa hoặc tag đúng {HEARTBEAT_TAG_BYTES} byte")
        out = prefix + tag
        if len(out) != HEARTBEAT_SIZE:
            raise AssertionError(
                f"HEARTBEAT phải là {HEARTBEAT_SIZE} byte, đang là {len(out)}")
        return out

    @staticmethod
    def unpack(data: bytes) -> "HeartbeatFrame":
        if len(data) != HEARTBEAT_SIZE:
            raise ValueError(
                f"HEARTBEAT phải đúng {HEARTBEAT_SIZE} byte, nhận {len(data)}")
        _ftype, flags = _parse_header(data, FRAME_TYPES["HEARTBEAT"])
        off = HEADER_SIZE
        src_id = int.from_bytes(data[off : off + 4], "big"); off += 4
        battery_pct = data[off]; off += 1
        hop_count = data[off]; off += 1
        time_offset_min = int.from_bytes(data[off : off + 2], "big"); off += 2
        return HeartbeatFrame(
            src_id=src_id, battery_pct=battery_pct, hop_count=hop_count,
            time_offset_min=time_offset_min, flags=flags,
            tag=data[off : off + HEARTBEAT_TAG_BYTES],
        )

    @staticmethod
    def verify(data: bytes, key: bytes) -> bool:
        if not key or len(data) != HEARTBEAT_SIZE:
            return False
        if not _valid_header(data, FRAME_TYPES["HEARTBEAT"]):
            return False
        prefix = data[:-HEARTBEAT_TAG_BYTES]
        expected = _tag(key, _heartbeat_authenticated(prefix), HEARTBEAT_TAG_BYTES)
        return hmac.compare_digest(data[-HEARTBEAT_TAG_BYTES:], expected)


# --------------------------------------------------------------------------
# BEACON — 18 byte
# --------------------------------------------------------------------------


@dataclass
class BeaconFrame(_FlagView):
    """BEACON v2.0 (18 byte).

    Bố cục: header 2 | gw_id 2 | bseq 1 | hop_limit 1 | time_offset_min 2 |
    load_pct 1 | reserved 1 | tag 8.
    """

    gw_id: int
    bseq: int
    hop_limit: int
    time_offset_min: int
    load_pct: int
    flags: Flags = field(default_factory=Flags)
    reserved: int = 0
    tag: bytes = b""

    SIZE = BEACON_SIZE
    TYPE = FRAME_TYPES["BEACON"]

    def _prefix(self) -> bytes:
        if _check(self.reserved, 8, "reserved") != 0:
            raise ValueError("BEACON reserved là trường dự trữ và phải bằng 0")
        if len(self.tag) and len(self.tag) != BEACON_TAG_BYTES:
            raise ValueError(f"tag BEACON phải đúng {BEACON_TAG_BYTES} byte")
        return (
            _pack_header(self.TYPE, self.flags)
            + _check(self.gw_id, 16, "gw_id").to_bytes(2, "big")
            + bytes((_check(self.bseq, 8, "bseq"),
                     _check(self.hop_limit, 8, "hop_limit")))
            + wrap_time(self.time_offset_min, TIME_BITS).to_bytes(2, "big")
            + bytes((_check(self.load_pct, 8, "load_pct"),
                     _check(self.reserved, 8, "reserved")))
        )

    def pack(self, key: bytes | None = None) -> bytes:
        prefix = self._prefix()
        tag = self.tag or (_tag(key, _beacon_authenticated(prefix),
                                BEACON_TAG_BYTES) if key else b"")
        if len(tag) != BEACON_TAG_BYTES:
            raise ValueError(f"BEACON cần khóa hoặc tag đúng {BEACON_TAG_BYTES} byte")
        out = prefix + tag
        if len(out) != BEACON_SIZE:
            raise AssertionError(
                f"BEACON phải là {BEACON_SIZE} byte, đang là {len(out)}")
        return out

    @staticmethod
    def unpack(data: bytes) -> "BeaconFrame":
        if len(data) != BEACON_SIZE:
            raise ValueError(f"BEACON phải đúng {BEACON_SIZE} byte, nhận {len(data)}")
        _ftype, flags = _parse_header(data, FRAME_TYPES["BEACON"])
        off = HEADER_SIZE
        gw_id = int.from_bytes(data[off : off + 2], "big"); off += 2
        bseq = data[off]; off += 1
        hop_limit = data[off]; off += 1
        time_offset_min = int.from_bytes(data[off : off + 2], "big"); off += 2
        load_pct = data[off]; off += 1
        reserved = data[off]; off += 1
        if reserved != 0:
            raise ValueError(f"BEACON reserved phải bằng 0, nhận {reserved}")
        return BeaconFrame(
            gw_id=gw_id, bseq=bseq, hop_limit=hop_limit,
            time_offset_min=time_offset_min, load_pct=load_pct,
            flags=flags, reserved=reserved, tag=data[off : off + BEACON_TAG_BYTES],
        )

    @staticmethod
    def verify(data: bytes, key: bytes) -> bool:
        if not key or len(data) != BEACON_SIZE:
            return False
        if not _valid_header(data, FRAME_TYPES["BEACON"]):
            return False
        prefix = data[:-BEACON_TAG_BYTES]
        if prefix[9] != 0:
            return False
        expected = _tag(key, _beacon_authenticated(prefix), BEACON_TAG_BYTES)
        return hmac.compare_digest(data[-BEACON_TAG_BYTES:], expected)


# --------------------------------------------------------------------------
# ACK — 12 byte, token 24 bit
# --------------------------------------------------------------------------


def ack_token(key: bytes, src_id: int, seq: int) -> int:
    """Token ACK 24 bit = 3 byte đầu của HMAC-SHA256(key, src_id‖seq).

    `src_id` là uint32 big-endian, `seq` là uint16 big-endian — cùng cách
    mã hoá như trên không khí. Trả về số nguyên 0..2**24-1.
    """
    material = (_check(src_id, 32, "src_id").to_bytes(4, "big")
                + _check(seq, 16, "seq").to_bytes(2, "big"))
    return int.from_bytes(
        _tag(key, material, ACK_TOKEN_BYTES), "big") & ACK_TOKEN_MAX


@dataclass
class AckFrame(_FlagView):
    """ACK v2.0 (12 byte).

    Bố cục: header 2 | bseq 1 | token 3 | reserved 1 | tag 5.
    Token là 24 bit — không phải 16 bit như v1.
    """

    bseq: int
    token: int
    flags: Flags = field(default_factory=Flags)
    reserved: int = 0
    tag: bytes = b""

    SIZE = ACK_SIZE
    TYPE = FRAME_TYPES["ACK"]

    @classmethod
    def for_event(cls, key: bytes, src_id: int, seq: int, bseq: int = 0,
                  flags: Flags | None = None) -> "AckFrame":
        """Tạo ACK cho một sự kiện SOS: token suy ra từ (src_id, seq)."""
        return cls(bseq=bseq, token=ack_token(key, src_id, seq),
                   flags=flags or Flags())

    def _prefix(self) -> bytes:
        if _check(self.reserved, 8, "reserved") != 0:
            raise ValueError("ACK reserved là trường dự trữ và phải bằng 0")
        if len(self.tag) and len(self.tag) != ACK_TAG_BYTES:
            raise ValueError(f"tag ACK phải đúng {ACK_TAG_BYTES} byte")
        return (
            _pack_header(self.TYPE, self.flags)
            + bytes((_check(self.bseq, 8, "bseq"),))
            + _check(self.token, ACK_TOKEN_BITS, "token").to_bytes(3, "big")
            + bytes((_check(self.reserved, 8, "reserved"),))
        )

    def pack(self, key: bytes | None = None) -> bytes:
        prefix = self._prefix()
        tag = self.tag or (_tag(key, prefix, ACK_TAG_BYTES) if key else b"")
        if len(tag) != ACK_TAG_BYTES:
            raise ValueError(f"ACK cần khóa hoặc tag đúng {ACK_TAG_BYTES} byte")
        out = prefix + tag
        if len(out) != ACK_SIZE:
            raise AssertionError(f"ACK phải là {ACK_SIZE} byte, đang là {len(out)}")
        return out

    @staticmethod
    def unpack(data: bytes) -> "AckFrame":
        if len(data) != ACK_SIZE:
            raise ValueError(f"ACK phải đúng {ACK_SIZE} byte, nhận {len(data)}")
        _ftype, flags = _parse_header(data, FRAME_TYPES["ACK"])
        off = HEADER_SIZE
        bseq = data[off]; off += 1
        token = _read_u24be(data, off); off += 3
        reserved = data[off]; off += 1
        if reserved != 0:
            raise ValueError(f"ACK reserved phải bằng 0, nhận {reserved}")
        return AckFrame(
            bseq=bseq, token=token, flags=flags, reserved=reserved,
            tag=data[off : off + ACK_TAG_BYTES],
        )

    @staticmethod
    def verify(data: bytes, key: bytes) -> bool:
        if not key or len(data) != ACK_SIZE:
            return False
        if not _valid_header(data, FRAME_TYPES["ACK"]):
            return False
        prefix = data[:-ACK_TAG_BYTES]
        if prefix[6] != 0:
            return False
        expected = _tag(key, prefix, ACK_TAG_BYTES)
        return hmac.compare_digest(data[-ACK_TAG_BYTES:], expected)


#: Bảng lớp khung theo tên — tiện cho vòng lặp kiểm thử / thống kê.
FRAME_CLASSES = {
    "SOS": SosFrame,
    "HEARTBEAT": HeartbeatFrame,
    "BEACON": BeaconFrame,
    "ACK": AckFrame,
}


# --------------------------------------------------------------------------
# Va chạm token ACK: giải tích + Monte Carlo (24 bit so với 16 bit v1)
# --------------------------------------------------------------------------


def token_collision_probability(n: int, bits: int = ACK_TOKEN_BITS) -> float:
    """Xác suất có ít nhất hai token trùng trong `n` token (bài toán sinh nhật).

    Công thức xấp xỉ p ≈ 1 - exp(-n(n-1) / (2·2**bits)). Nhãn SUY — đây là
    mô hình xác suất, không phải kết quả đo trên không khí.
    """
    if n < 2:
        return 0.0
    return 1.0 - math.exp(-n * (n - 1) / (2.0 * (1 << bits)))


def simulate_token_collision(n: int, bits: int = ACK_TOKEN_BITS,
                             trials: int = 2000, seed: int = 0) -> float:
    """Monte Carlo ước lượng xác suất va chạm token (nhãn SIM).

    Mỗi vòng rút `n` token trong `2**bits` giá trị; dừng sớm ngay khi gặp
    token trùng để giữ thời gian chạy thấp.
    """
    if n < 1:
        raise ValueError("n phải dương")
    if trials < 1:
        raise ValueError("trials phải dương")
    rng = random.Random(seed)
    hits = 0
    for _ in range(trials):
        seen = set()
        for _ in range(n):
            v = rng.getrandbits(bits)
            if v in seen:
                hits += 1
                break
            seen.add(v)
    return hits / trials


def collision_table(nodes: tuple[int, ...] = COLLISION_NODES,
                    trials: dict[int, int] | None = None,
                    seed: int = 20240) -> list[dict]:
    """Bảng so sánh va chạm token 24 bit (v2) với 16 bit (v1).

    Cột `*_analytic` nhãn SUY, cột `*_sim` nhãn SIM.
    """
    trials = trials or COLLISION_TRIALS
    rows: list[dict] = []
    for n in nodes:
        t = trials.get(n, 2000)
        rows.append({
            "n": n,
            "trials": t,
            "p24_analytic": token_collision_probability(n, 24),
            "p24_sim": simulate_token_collision(n, 24, t, seed),
            "p16_analytic": token_collision_probability(n, 16),
            "p16_sim": simulate_token_collision(n, 16, t, seed),
        })
    return rows


# --------------------------------------------------------------------------
# Airtime LoRa cho từng loại khung
# --------------------------------------------------------------------------


def airtime_table(
    sf_list: tuple[int, ...] = (7, 9, 12),
    bw_hz: float = 125_000,
    cr: int = 1,
) -> list[dict]:
    """Airtime từng loại khung theo SF, dùng `lora.LoraProfile`.

    Trả về list dict gồm: sf, frame_type, bytes, airtime_ms, frames_per_s.
    Mọi giá trị airtime mang nhãn SUY (công thức Semtech), KHÔNG phải ĐO.
    """
    rows: list[dict] = []
    for sf in sf_list:
        profile = lora.LoraProfile(sf=sf, bw_hz=bw_hz, cr=cr)
        for name in ("SOS", "HEARTBEAT", "BEACON", "ACK"):
            size = FRAME_SIZES[name]
            air = profile.airtime_s(size)
            rows.append({
                "sf": sf,
                "bw_hz": bw_hz,
                "cr": cr,
                "frame_type": name,
                "bytes": size,
                "airtime_ms": air * 1000.0,
                "frames_per_s": 1.0 / air,
                "evidence": "SUY",
            })
    return rows


def coord_table() -> dict[str, float]:
    """Độ phân giải toạ độ của codec (tái dùng helper từ `packets`)."""
    return {
        "lat_res_deg": coord_resolution_deg(-90.0, 90.0),
        "lon_res_deg": coord_resolution_deg(-180.0, 180.0),
        "lat_res_m": coord_resolution_m(-90.0, 90.0),
        "lon_res_m": coord_resolution_m(-180.0, 180.0),
    }


def resolve_time_offset(value: int, reference_min: int) -> int:
    """Khôi phục thời điểm thật từ trường 16 bit quanh `reference_min`.

    Cửa sổ 16 bit = 65536 phút ≈ 45,5 ngày; khung phải đến trong nửa cửa sổ
    quanh thời điểm nhận thì `unwrap_time` mới chọn đúng. ĐÓNG BĂNG.
    """
    return unwrap_time(value, reference_min, TIME_BITS)


# --------------------------------------------------------------------------
# In bảng
# --------------------------------------------------------------------------


def _print_size_table() -> None:
    print("=" * 78)
    print("BẢNG KÍCH THƯỚC KHUNG v2.0 (byte)")
    print("Nguồn: ĐÓNG BĂNG — con số do đặc tả v2.0 chốt, không phải đo.")
    print("=" * 78)
    header = f"{'khung':<10} | {'mã':>3} | {'byte':>5} | {'tag B':>5} | evidence"
    print(header)
    print("-" * len(header))
    tag_bytes = {
        "SOS": SOS_TAG_BYTES,
        "HEARTBEAT": HEARTBEAT_TAG_BYTES,
        "BEACON": BEACON_TAG_BYTES,
        "ACK": ACK_TAG_BYTES,
    }
    for name in ("SOS", "HEARTBEAT", "BEACON", "ACK"):
        print(f"{name:<10} | {FRAME_TYPES[name]:>3} | {FRAME_SIZES[name]:>5} | "
              f"{tag_bytes[name]:>5} | GIẢ ĐỊNH")
    print(f"{'MAX_PAYLOAD':<10} | {'-':>3} | {MAX_PAYLOAD_BYTES:>5} | "
          f"{'-':>5} | GIẢ ĐỊNH")


def _print_airtime_table() -> None:
    print()
    print("=" * 84)
    print("BẢNG AIRTIME LoRa — BW 125 kHz, CR 4/5 (Semtech), evidence=SUY")
    print("Là thời gian không khí suy ra từ công thức, KHÔNG phải số đo.")
    print("=" * 84)
    header = (f"{'SF':>3} | {'khung':<10} | {'byte':>5} | {'airtime ms':>11} | "
              f"{'khung/s':>8} | evidence")
    print(header)
    print("-" * len(header))
    for row in airtime_table():
        print(f"{row['sf']:>3} | {row['frame_type']:<10} | {row['bytes']:>5} | "
              f"{row['airtime_ms']:>9.1f} ms | {row['frames_per_s']:>8.2f} | "
              f"evidence={row['evidence']}")


def _print_collision_table() -> None:
    print()
    print("=" * 92)
    print("BẢNG VA CHẠM TOKEN ACK — 24 bit (v2) so với 16 bit (v1)")
    print("analytic = SUY (bài toán sinh nhật); MC = SIM (Monte Carlo).")
    print("Ghi chú lịch sử: token 16 bit của v1 được chứng minh là sụp ở ≥1000 nút.")
    print("=" * 92)
    header = (f"{'n nút':>6} | {'p24 SUY':>10} | {'p24 SIM':>10} | "
              f"{'p16 SUY':>10} | {'p16 SIM':>10} | {'vòng':>6}")
    print(header)
    print("-" * len(header))
    for row in collision_table():
        print(f"{row['n']:>6} | {row['p24_analytic']:>10.6f} | "
              f"{row['p24_sim']:>10.6f} | {row['p16_analytic']:>10.6f} | "
              f"{row['p16_sim']:>10.6f} | {row['trials']:>6}")


def main() -> None:
    _print_size_table()
    _print_airtime_table()
    _print_collision_table()
    print()
    print("LƯU Ý: p24 SIM ở n nhỏ có thể bằng 0 vì xác suất thật nhỏ hơn độ phân")
    print("giải của số vòng; cột SUY mới là ước lượng dùng để so sánh.")


if __name__ == "__main__":
    main()
