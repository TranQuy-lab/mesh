"""Kiểm thử codec quảng bá RescueMesh-AI v1."""

from __future__ import annotations

import random

from packets import (
    ACK_BYTES, BEACON_BASE, HEARTBEAT_BASE, HOP_UNKNOWN, MAX_ACKS,
    MAX_ADV_APP_BYTES, MAX_NEIGHBORS, NEIGHBOR_BYTES, SOS_SIZE, TAG_BYTES,
    Beacon, Header, Heartbeat, SosPacket, ack_token, collision_probability,
    decode_lat, decode_lon, encode_lat, encode_lon, latlon_table, rewrite_route,
    should_forward, simulate_collision, unwrap_time, wrap_time,
)

DEVICE_KEY = b"device-key-for-tests"
NETWORK_KEY = b"network-key-for-tests"


def sample_sos(**overrides):
    args = dict(src_id=0x89ABCDEF, time_min=12345, lat=21.028511, lon=105.804817,
                trigger=1, people=2, need=3, bat=11, gps_fix=3, moving=0,
                hop=7, ttl=15, seq=42)
    args.update(overrides)
    return SosPacket(**args)


def test_header_roundtrip():
    h = Header(ver=1, type=2, prio=2, rsv=1, ttl=15, hop=3, seq=200)
    assert Header.unpack(h.pack()) == h


def test_coordinate_roundtrip_and_resolution():
    for value in (-90.0, 0.0, 21.028511, 90.0):
        assert abs(decode_lat(encode_lat(value)) - value) <= latlon_table()["lat_res_deg"]
    for value in (-180.0, 0.0, 105.804817, 180.0):
        assert abs(decode_lon(encode_lon(value)) - value) <= latlon_table()["lon_res_deg"]
    assert 1.0 < latlon_table()["lat_res_m"] < 1.5
    assert 2.0 < latlon_table()["lon_res_m"] < 3.0


def test_time8_unwrap_within_sos_lifetime():
    ref = 1_000_000
    for delta in (-60, -1, 0, 1, 60):
        assert unwrap_time(wrap_time(ref + delta), ref) == ref + delta


def test_sos_is_24_bytes_and_verifies():
    blob = sample_sos().pack(DEVICE_KEY)
    assert len(blob) == SOS_SIZE == MAX_ADV_APP_BYTES
    assert SosPacket.verify(blob, DEVICE_KEY)
    assert not SosPacket.verify(blob, b"wrong-key")


def test_golden_vectors_v1():
    sos = sample_sos().pack(DEVICE_KEY)
    assert sos.hex() == "46f72a89abcdef399de83fcb3d2d53bc4c1ba811078a6028"
    heartbeat = Heartbeat(0x12345678, 0xABCD, 12, ((0x87654321, 201),), hop=4, seq=9)
    assert heartbeat.pack(DEVICE_KEY).hex() == "4af40912345678abcdc187654321c9a6ca07915a349947"
    beacon = Beacon(7, 9999, 1, (ack_token(sos), b"wxyz"), hop=0, seq=23)
    assert beacon.pack(NETWORK_KEY).hex() == "54f01700070f01024c1ba8117778797ad84f481e90c03499"


def test_sos_roundtrip():
    pkt = sample_sos()
    back = SosPacket.unpack(pkt.pack(DEVICE_KEY))
    assert (back.src_id, back.seq, back.trigger, back.people, back.need) == (
        pkt.src_id, pkt.seq, pkt.trigger, pkt.people, pkt.need)
    assert back.tag and len(back.tag) == TAG_BYTES


def test_sos_tamper_is_detected_except_documented_route_byte():
    blob = sample_sos().pack(DEVICE_KEY)
    tampered = bytearray(blob)
    tampered[8] ^= 1
    assert not SosPacket.verify(bytes(tampered), DEVICE_KEY)
    relayed = rewrite_route(blob, ttl=14, hop=6)
    assert SosPacket.verify(relayed, DEVICE_KEY)
    assert Header.unpack(relayed).ttl == 14 and Header.unpack(relayed).hop == 6


def test_ack_token_comes_from_sos_tag():
    blob = sample_sos().pack(DEVICE_KEY)
    token = ack_token(blob)
    assert len(token) == ACK_BYTES and token == blob[-TAG_BYTES:-TAG_BYTES + ACK_BYTES]


def test_heartbeat_budget_and_roundtrip():
    assert HEARTBEAT_BASE == 18 and MAX_NEIGHBORS == 1
    pkt = Heartbeat(0x12345678, 0xABCD, 12, ((0x87654321, 201),), hop=4, seq=9)
    blob = pkt.pack(DEVICE_KEY)
    assert len(blob) == HEARTBEAT_BASE + NEIGHBOR_BYTES == 23 <= MAX_ADV_APP_BYTES
    back = Heartbeat.unpack(blob)
    assert back.neighbors == pkt.neighbors and back.src_id == pkt.src_id


def test_heartbeat_rejects_two_neighbors():
    pkt = Heartbeat(1, 2, 3, ((4, 5), (6, 7)))
    try:
        pkt.pack(DEVICE_KEY)
        raise AssertionError("phải từ chối hơn một hàng xóm")
    except ValueError:
        pass


def test_beacon_budget_verify_and_roundtrip():
    assert MAX_ACKS == 2 and BEACON_BASE == 16
    acks = (b"abcd", b"wxyz")
    pkt = Beacon(station_id=7, time_min=9999, flags=1, acks=acks, hop=0, seq=23)
    blob = pkt.pack(NETWORK_KEY)
    assert len(blob) == BEACON_BASE + 2 * ACK_BYTES == 24 <= MAX_ADV_APP_BYTES
    assert Beacon.verify(blob, NETWORK_KEY)
    back = Beacon.unpack(blob)
    assert back.acks == acks and back.seq == 23 and back.flags == 1


def test_beacon_route_change_requires_network_resign():
    blob = Beacon(1, 100, acks=(b"1234",), seq=2).pack(NETWORK_KEY)
    assert not Beacon.verify(rewrite_route(blob, 14, 1), NETWORK_KEY)


def test_forward_rule():
    assert should_forward(5, 3, 10)
    assert not should_forward(3, 3, 10)
    assert not should_forward(3, HOP_UNKNOWN, 10)
    assert not should_forward(5, 3, 0)


def test_collision_analysis():
    assert collision_probability(200, 32) < 0.00001
    assert 0.01 < collision_probability(10_000, 32) < 0.02
    analytic = collision_probability(1000, 16)
    assert abs(analytic - simulate_collision(1000, 16, 300, 7)) < 0.05


def test_random_sos_fuzz_roundtrip():
    rng = random.Random(1234)
    for _ in range(500):
        pkt = SosPacket(
            src_id=rng.randrange(1 << 32), time_min=rng.randrange(1 << 20),
            lat=rng.uniform(-90, 90), lon=rng.uniform(-180, 180),
            trigger=rng.randrange(4), people=rng.randrange(8), need=rng.randrange(8),
            bat=rng.randrange(16), gps_fix=rng.randrange(4), moving=rng.randrange(2),
            hop=rng.randrange(16), ttl=rng.randrange(16), seq=rng.randrange(256),
        )
        blob = pkt.pack(DEVICE_KEY)
        back = SosPacket.unpack(blob)
        assert len(blob) == 24 and SosPacket.verify(blob, DEVICE_KEY)
        assert back.src_id == pkt.src_id and back.seq == pkt.seq


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
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
