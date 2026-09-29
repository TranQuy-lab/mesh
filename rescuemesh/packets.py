"""Codec tham chiếu RescueMesh-AI v1.0.

Đường truyền chuẩn là BLE legacy advertising không kết nối. Một AD structure
manufacturer-specific có tối đa 24 byte dữ liệu ứng dụng khi dành 3 byte cho
Flags và 4 byte cho length/type/company ID trong ngân sách 31 byte.

GATT/ATT MTU không phải ràng buộc của codec này. Extended advertising và GATT
chỉ là tối ưu tùy chọn, không phải điều kiện để SOS hoạt động.

Khung SOS dùng đủ 24 byte: ID 32 bit, thời gian modulo 256 phút, tọa độ 24 bit
mỗi trục và HMAC-SHA256 cắt 64 bit. Byte route (TTL/hop) được relay thay đổi nên
không nằm trong MAC đầu-cuối; đây là giới hạn an ninh được ghi trong đặc tả.
"""

from __future__ import annotations

import hashlib
import hmac
import math
import random
from dataclasses import dataclass, field
from typing import Sequence

VER = 1
TYPE_SOS = 0
TYPE_HEARTBEAT = 1
TYPE_BEACON = 2

PRIO_SOS = 3
PRIO_ACK_BEACON = 2
PRIO_HEARTBEAT = 1

TTL_DEFAULT = 15
HOP_UNKNOWN = 0xF
MAX_ADV_APP_BYTES = 24

SRCID_BITS = 32
LATLON_BITS = 24
LATLON_MAX = (1 << LATLON_BITS) - 1
LAT_RANGE = (-90.0, 90.0)
LON_RANGE = (-180.0, 180.0)

TIME_BITS = 8
TIME_WRAP_MINUTES = 1 << TIME_BITS
TAG_BYTES = 8
ACK_BYTES = 4
NEIGHBOR_BYTES = 5
MAX_NEIGHBORS = 1

SOS_SIZE = 24
HEARTBEAT_BASE = 3 + 4 + 2 + 1 + TAG_BYTES
BEACON_BASE = 3 + 2 + 1 + 1 + 1 + TAG_BYTES
MAX_ACKS = (MAX_ADV_APP_BYTES - BEACON_BASE) // ACK_BYTES


def _check(value: int, bits: int, name: str) -> int:
    if not 0 <= value < (1 << bits):
        raise ValueError(f"{name}={value} không vừa {bits} bit")
    return value


def _u24be(value: int) -> bytes:
    return _check(value, 24, "u24").to_bytes(3, "big")


def _read_u24be(data: bytes, off: int) -> int:
    if off + 3 > len(data):
        raise ValueError("thiếu dữ liệu u24")
    return int.from_bytes(data[off : off + 3], "big")


def encode_coord(degrees: float, vmin: float, vmax: float) -> int:
    if not vmin <= degrees <= vmax:
        raise ValueError(f"tọa độ {degrees} ngoài [{vmin}, {vmax}]")
    return int(round((degrees - vmin) / (vmax - vmin) * LATLON_MAX))


def decode_coord(raw: int, vmin: float, vmax: float) -> float:
    return vmin + (vmax - vmin) * ((raw & LATLON_MAX) / LATLON_MAX)


def encode_lat(deg: float) -> int:
    return encode_coord(deg, *LAT_RANGE)


def encode_lon(deg: float) -> int:
    return encode_coord(deg, *LON_RANGE)


def decode_lat(raw: int) -> float:
    return decode_coord(raw, *LAT_RANGE)


def decode_lon(raw: int) -> float:
    return decode_coord(raw, *LON_RANGE)


def coord_resolution_deg(vmin: float, vmax: float) -> float:
    return (vmax - vmin) / LATLON_MAX


def coord_resolution_m(vmin: float, vmax: float) -> float:
    return coord_resolution_deg(vmin, vmax) * 111_320.0


def latlon_table() -> dict[str, float]:
    return {
        "lat_res_deg": coord_resolution_deg(*LAT_RANGE),
        "lon_res_deg": coord_resolution_deg(*LON_RANGE),
        "lat_res_m": coord_resolution_m(*LAT_RANGE),
        "lon_res_m": coord_resolution_m(*LON_RANGE),
    }


def wrap_time(minutes: int, bits: int = TIME_BITS) -> int:
    return minutes % (1 << bits)


def unwrap_time(value: int, reference: int, bits: int = TIME_BITS) -> int:
    """Khôi phục thời điểm gần nhất quanh thời điểm nhận ở trạm."""
    mod = 1 << bits
    base = reference - reference % mod + value
    return min((base - mod, base, base + mod), key=lambda x: abs(x - reference))


def _tag(key: bytes, authenticated: bytes) -> bytes:
    if not key:
        raise ValueError("cần khóa HMAC không rỗng")
    return hmac.new(key, authenticated, hashlib.sha256).digest()[:TAG_BYTES]


@dataclass(frozen=True)
class Header:
    ver: int = VER
    type: int = TYPE_SOS
    prio: int = PRIO_SOS
    rsv: int = 0
    ttl: int = TTL_DEFAULT
    hop: int = HOP_UNKNOWN
    seq: int = 0

    def pack(self) -> bytes:
        b0 = (_check(self.ver, 2, "ver") << 6) | (_check(self.type, 3, "type") << 3)
        b0 |= (_check(self.prio, 2, "prio") << 1) | _check(self.rsv, 1, "rsv")
        b1 = (_check(self.ttl, 4, "ttl") << 4) | _check(self.hop, 4, "hop")
        return bytes((b0, b1, _check(self.seq, 8, "seq")))

    @staticmethod
    def unpack(data: bytes) -> "Header":
        if len(data) < 3:
            raise ValueError("header cần 3 byte")
        b0, b1, b2 = data[:3]
        return Header((b0 >> 6) & 3, (b0 >> 3) & 7, (b0 >> 1) & 3, b0 & 1,
                      (b1 >> 4) & 15, b1 & 15, b2)


def _e2e_authenticated(frame_without_tag: bytes) -> bytes:
    """Xác thực B0, B2 và body; loại B1 vì relay sửa TTL/hop."""
    return frame_without_tag[0:1] + frame_without_tag[2:]


@dataclass
class SosPacket:
    src_id: int
    time_min: int
    lat: float
    lon: float
    trigger: int
    people: int
    need: int
    bat: int
    gps_fix: int
    moving: int
    hop: int = HOP_UNKNOWN
    ttl: int = TTL_DEFAULT
    seq: int = 0
    tag: bytes = b""

    SIZE = SOS_SIZE

    def _prefix(self) -> bytes:
        hdr = Header(type=TYPE_SOS, prio=PRIO_SOS, ttl=self.ttl, hop=self.hop, seq=self.seq).pack()
        need_byte = (_check(self.trigger, 2, "trigger") << 6) | (_check(self.people, 3, "people") << 3)
        need_byte |= _check(self.need, 3, "need")
        state = (_check(self.bat, 4, "bat") << 4) | (_check(self.gps_fix, 2, "gps_fix") << 2)
        state |= _check(self.moving, 1, "moving") << 1
        return (hdr + _check(self.src_id, 32, "srcID").to_bytes(4, "big")
                + bytes((wrap_time(self.time_min),)) + _u24be(encode_lat(self.lat))
                + _u24be(encode_lon(self.lon)) + bytes((need_byte, state)))

    def pack(self, key: bytes | None = None) -> bytes:
        prefix = self._prefix()
        tag = self.tag or (_tag(key, _e2e_authenticated(prefix)) if key else b"")
        if len(tag) != TAG_BYTES:
            raise ValueError("SOS cần khóa hoặc tag đúng 8 byte")
        out = prefix + tag
        if len(out) != self.SIZE:
            raise AssertionError(f"SOS phải là {self.SIZE} byte, đang là {len(out)}")
        return out

    @staticmethod
    def unpack(data: bytes) -> "SosPacket":
        if len(data) != SOS_SIZE:
            raise ValueError(f"SOS phải đúng {SOS_SIZE} byte")
        hdr = Header.unpack(data)
        if hdr.ver != VER or hdr.type != TYPE_SOS:
            raise ValueError("phiên bản/type SOS không hợp lệ")
        off = 3
        src = int.from_bytes(data[off : off + 4], "big"); off += 4
        t = data[off]; off += 1
        lat = decode_lat(_read_u24be(data, off)); off += 3
        lon = decode_lon(_read_u24be(data, off)); off += 3
        nb, sb = data[off], data[off + 1]; off += 2
        return SosPacket(src, t, lat, lon, (nb >> 6) & 3, (nb >> 3) & 7, nb & 7,
                         (sb >> 4) & 15, (sb >> 2) & 3, (sb >> 1) & 1,
                         hdr.hop, hdr.ttl, hdr.seq, data[off : off + TAG_BYTES])

    @staticmethod
    def verify(data: bytes, key: bytes) -> bool:
        if len(data) != SOS_SIZE:
            return False
        return hmac.compare_digest(data[-TAG_BYTES:], _tag(key, _e2e_authenticated(data[:-TAG_BYTES])))


@dataclass
class Heartbeat:
    src_id: int
    cell: int
    bat: int
    neighbors: Sequence[tuple[int, int]] = field(default_factory=tuple)
    hop: int = HOP_UNKNOWN
    ttl: int = TTL_DEFAULT
    seq: int = 0
    tag: bytes = b""

    def _prefix(self) -> bytes:
        k = len(self.neighbors)
        if k > MAX_NEIGHBORS:
            raise ValueError(f"mỗi HEARTBEAT chỉ mang tối đa {MAX_NEIGHBORS} hàng xóm")
        hdr = Header(type=TYPE_HEARTBEAT, prio=PRIO_HEARTBEAT, ttl=self.ttl, hop=self.hop, seq=self.seq).pack()
        status = (_check(self.bat, 4, "bat") << 4) | _check(k, 4, "k")
        return (hdr + _check(self.src_id, 32, "srcID").to_bytes(4, "big")
                + _check(self.cell, 16, "cell").to_bytes(2, "big") + bytes((status,))
                + b"".join(_check(n, 32, "neighborID").to_bytes(4, "big")
                           + bytes((_check(r, 8, "rssi"),)) for n, r in self.neighbors))

    def pack(self, key: bytes | None = None) -> bytes:
        prefix = self._prefix()
        tag = self.tag or (_tag(key, _e2e_authenticated(prefix)) if key else b"")
        if len(tag) != TAG_BYTES:
            raise ValueError("HEARTBEAT cần khóa hoặc tag đúng 8 byte")
        out = prefix + tag
        if len(out) > MAX_ADV_APP_BYTES:
            raise ValueError("HEARTBEAT vượt ngân sách quảng bá 24 byte")
        return out

    @staticmethod
    def unpack(data: bytes) -> "Heartbeat":
        if len(data) < HEARTBEAT_BASE or len(data) > MAX_ADV_APP_BYTES:
            raise ValueError("độ dài HEARTBEAT không hợp lệ")
        hdr = Header.unpack(data)
        if hdr.ver != VER or hdr.type != TYPE_HEARTBEAT:
            raise ValueError("phiên bản/type HEARTBEAT không hợp lệ")
        off = 3
        src = int.from_bytes(data[off : off + 4], "big"); off += 4
        cell = int.from_bytes(data[off : off + 2], "big"); off += 2
        status = data[off]; off += 1
        k = status & 15
        if k > MAX_NEIGHBORS or len(data) != HEARTBEAT_BASE + k * NEIGHBOR_BYTES:
            raise ValueError("k/độ dài HEARTBEAT không khớp")
        nbrs = []
        for _ in range(k):
            nid = int.from_bytes(data[off : off + 4], "big"); off += 4
            nbrs.append((nid, data[off])); off += 1
        return Heartbeat(src, cell, (status >> 4) & 15, tuple(nbrs), hdr.hop,
                         hdr.ttl, hdr.seq, data[off : off + TAG_BYTES])


@dataclass
class Beacon:
    station_id: int
    time_min: int
    flags: int = 0
    acks: Sequence[bytes] = field(default_factory=tuple)
    hop: int = 0
    ttl: int = TTL_DEFAULT
    seq: int = 0
    tag: bytes = b""

    def _prefix(self) -> bytes:
        if len(self.acks) > MAX_ACKS:
            raise ValueError(f"tối đa {MAX_ACKS} ACK mỗi beacon legacy")
        if any(len(a) != ACK_BYTES for a in self.acks):
            raise ValueError("mỗi ACK token phải đúng 4 byte")
        hdr = Header(type=TYPE_BEACON, prio=PRIO_ACK_BEACON, ttl=self.ttl, hop=self.hop, seq=self.seq).pack()
        return (hdr + _check(self.station_id, 16, "stationID").to_bytes(2, "big")
                + bytes((wrap_time(self.time_min), _check(self.flags, 8, "flags"), len(self.acks)))
                + b"".join(self.acks))

    def pack(self, key: bytes | None = None) -> bytes:
        prefix = self._prefix()
        tag = self.tag or (_tag(key, prefix) if key else b"")
        if len(tag) != TAG_BYTES:
            raise ValueError("BEACON cần khóa mạng hoặc tag đúng 8 byte")
        out = prefix + tag
        if len(out) > MAX_ADV_APP_BYTES:
            raise ValueError("BEACON vượt ngân sách quảng bá 24 byte")
        return out

    @staticmethod
    def unpack(data: bytes) -> "Beacon":
        if len(data) < BEACON_BASE or len(data) > MAX_ADV_APP_BYTES:
            raise ValueError("độ dài BEACON không hợp lệ")
        hdr = Header.unpack(data)
        if hdr.ver != VER or hdr.type != TYPE_BEACON:
            raise ValueError("phiên bản/type BEACON không hợp lệ")
        off = 3
        station = int.from_bytes(data[off : off + 2], "big"); off += 2
        t, flags, n = data[off], data[off + 1], data[off + 2]; off += 3
        if n > MAX_ACKS or len(data) != BEACON_BASE + n * ACK_BYTES:
            raise ValueError("nAck/độ dài BEACON không khớp")
        acks = tuple(data[off + i * ACK_BYTES : off + (i + 1) * ACK_BYTES] for i in range(n))
        off += n * ACK_BYTES
        return Beacon(station, t, flags, acks, hdr.hop, hdr.ttl, hdr.seq,
                      data[off : off + TAG_BYTES])

    @staticmethod
    def verify(data: bytes, key: bytes) -> bool:
        if not BEACON_BASE <= len(data) <= MAX_ADV_APP_BYTES:
            return False
        return hmac.compare_digest(data[-TAG_BYTES:], _tag(key, data[:-TAG_BYTES]))


def ack_token(sos_frame: bytes) -> bytes:
    """ACK định danh sự kiện bằng 32 bit đầu của tag SOS đã thấy trên không khí."""
    if len(sos_frame) != SOS_SIZE:
        raise ValueError("cần khung SOS 24 byte")
    return sos_frame[-TAG_BYTES : -TAG_BYTES + ACK_BYTES]


def rewrite_route(frame: bytes, ttl: int, hop: int) -> bytes:
    if len(frame) < 3:
        raise ValueError("khung quá ngắn")
    out = bytearray(frame)
    out[1] = (_check(ttl, 4, "ttl") << 4) | _check(hop, 4, "hop")
    return bytes(out)


def should_forward(pkt_hop: int, my_hop: int, ttl: int) -> bool:
    return ttl > 0 and my_hop < HOP_UNKNOWN and my_hop < pkt_hop


def collision_probability(n: int, bits: int) -> float:
    if n < 2:
        return 0.0
    space = 1 << bits
    return 1.0 - math.exp(-n * (n - 1) / (2 * space))


def simulate_collision(n: int, bits: int, trials: int = 2000, seed: int = 0) -> float:
    rng = random.Random(seed)
    space = 1 << bits
    hits = 0
    for _ in range(trials):
        values = [rng.randrange(space) for _ in range(n)]
        hits += len(set(values)) != n
    return hits / trials


SIZE_TABLE = {
    "BLE legacy advertising data": 31,
    "Dữ liệu ứng dụng trong manufacturer AD": MAX_ADV_APP_BYTES,
    "SOS v1": SOS_SIZE,
    "HEARTBEAT k=0": HEARTBEAT_BASE,
    "HEARTBEAT k=1": HEARTBEAT_BASE + NEIGHBOR_BYTES,
    "BEACON nAck=0": BEACON_BASE,
    "BEACON nAck=2": BEACON_BASE + ACK_BYTES * 2,
}


def main() -> None:
    print("Kích thước khung RescueMesh-AI v1 (byte):")
    for name, size in SIZE_TABLE.items():
        print(f"  {name:<44} {size:>3}")
    print("\nĐụng srcID 32 bit (dedup thực dùng thêm tag 64 bit):")
    for n in (200, 1_000, 10_000):
        print(f"  n={n:>5}: {collision_probability(n, 32) * 100:.4f}%")


if __name__ == "__main__":
    main()
