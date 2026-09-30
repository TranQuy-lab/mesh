"""Kiểm thử ngân sách năng lượng nút LoRa.

Các test kiểm **tính chất và kế toán**, không kiểm giá trị tuyệt đối — vì mọi
dòng điện trong `node_power.py` đang là `GIẢ ĐỊNH` chờ đối chiếu datasheet.
"""

from __future__ import annotations

import math

from lora import LoraProfile
from node_power import (
    NodeDutyCycle,
    NodePowerParams,
    battery_life_days,
    charge_per_day_mah,
    duty_cycle_fraction,
    energy_cost_per_delivered_sos_mah,
    frames_per_day,
)

PROFILE = LoraProfile(9, 125_000, 1)


def test_airtime_beacon_ti_le_voi_so_beacon():
    a = frames_per_day(PROFILE, NodeDutyCycle(beacon_interval_s=300.0))
    b = frames_per_day(PROFILE, NodeDutyCycle(beacon_interval_s=150.0))
    assert abs(b["beacons_per_day"] - 2 * a["beacons_per_day"]) < 1e-9
    assert abs(b["airtime_beacon_s"] - 2 * a["airtime_beacon_s"]) < 1e-9


def test_khong_beacon_thi_airtime_beacon_bang_khong():
    f = frames_per_day(PROFILE, NodeDutyCycle(beacon_interval_s=None))
    assert f["beacons_per_day"] == 0.0
    assert f["airtime_beacon_s"] == 0.0


def test_tong_airtime_bang_tong_thanh_phan():
    f = frames_per_day(PROFILE, NodeDutyCycle())
    assert (
        abs(f["airtime_total_s"] - (f["airtime_beacon_s"] + f["airtime_sos_s"]))
        < 1e-12
    )


def test_ke_toan_nang_luong_tong_bang_tong_thanh_phan():
    parts = charge_per_day_mah(NodePowerParams(), PROFILE, NodeDutyCycle())
    keys = [
        "baseline",
        "imu",
        "tx_beacon",
        "tx_sos",
        "rx",
        "gnss",
        "self_discharge",
    ]
    assert abs(sum(parts[k] for k in keys) - parts["total"]) < 1e-9


def test_tu_xa_pin_tang_dien_luong_moi_ngay():
    low = NodePowerParams(self_discharge_percent_per_month=0.0)
    high = NodePowerParams(self_discharge_percent_per_month=5.0)
    a = charge_per_day_mah(low, PROFILE, NodeDutyCycle())["total"]
    b = charge_per_day_mah(high, PROFILE, NodeDutyCycle())["total"]
    assert b > a


def test_nghe_lien_tuc_lam_can_pin_nhanh_hon_hang_chuc_lan():
    quiet = NodeDutyCycle(rx_fraction=0.0)
    listening = NodeDutyCycle(rx_fraction=1.0)
    a = battery_life_days(NodePowerParams(), PROFILE, quiet)
    b = battery_life_days(NodePowerParams(), PROFILE, listening)
    assert a > 10 * b


def test_gnss_nhieu_lan_bat_lam_giam_tuoi_tho():
    few = NodeDutyCycle(gnss_fixes_per_day=1.0)
    many = NodeDutyCycle(gnss_fixes_per_day=48.0)
    assert battery_life_days(NodePowerParams(), PROFILE, few) > battery_life_days(
        NodePowerParams(), PROFILE, many
    )


def test_beacon_day_hon_lam_giam_tuoi_tho():
    slow = NodeDutyCycle(beacon_interval_s=600.0)
    fast = NodeDutyCycle(beacon_interval_s=30.0)
    assert battery_life_days(NodePowerParams(), PROFILE, slow) > battery_life_days(
        NodePowerParams(), PROFILE, fast
    )


def test_sf_cao_hon_ton_nhieu_dien_hon():
    duty = NodeDutyCycle(beacon_interval_s=60.0)
    totals = [
        charge_per_day_mah(NodePowerParams(), LoraProfile(sf, 125_000, 1), duty)[
            "total"
        ]
        for sf in (7, 9, 12)
    ]
    assert totals == sorted(totals)


def test_duty_cycle_ti_le_nghich_voi_chu_ky_beacon():
    """Chỉ so phần airtime beacon: cùng cấu hình SOS, gấp đôi chu kỳ → chia đôi."""
    a = duty_cycle_fraction(
        PROFILE, NodeDutyCycle(beacon_interval_s=300.0, sos_per_day=0.0)
    )
    b = duty_cycle_fraction(
        PROFILE, NodeDutyCycle(beacon_interval_s=600.0, sos_per_day=0.0)
    )
    assert abs(a - 2 * b) < 1e-12
    assert 0.0 < b < a < 1.0


def test_duty_cycle_beacon_5_phut_nho_hon_1_phan_tram():
    """Beacon 5 phút ở SF9 chỉ chiếm dưới 1 % thời gian — chưa phải nút thắt."""
    assert duty_cycle_fraction(PROFILE, NodeDutyCycle(beacon_interval_s=300.0)) < 0.01


def test_chi_phi_moi_sos_vo_han_khi_khong_co_sos():
    duty = NodeDutyCycle(sos_per_day=0.0)
    assert math.isinf(
        energy_cost_per_delivered_sos_mah(NodePowerParams(), PROFILE, duty)
    )


def test_chi_phi_moi_sos_giam_khi_co_nhieu_sos():
    few = NodeDutyCycle(sos_per_day=1.0)
    many = NodeDutyCycle(sos_per_day=100.0)
    a = energy_cost_per_delivered_sos_mah(NodePowerParams(), PROFILE, few)
    b = energy_cost_per_delivered_sos_mah(NodePowerParams(), PROFILE, many)
    assert b < a


def test_lap_lai_trong_mesh_lam_tang_chi_phi_vo_tuyen():
    duty = NodeDutyCycle(beacon_interval_s=None)
    one = NodeDutyCycle(beacon_interval_s=None, relays_per_sos=0.0)
    many = NodeDutyCycle(beacon_interval_s=None, relays_per_sos=10.0)
    assert (
        charge_per_day_mah(NodePowerParams(), PROFILE, many)["tx_sos"]
        > charge_per_day_mah(NodePowerParams(), PROFILE, one)["tx_sos"]
    )
    assert one.sos_bytes == duty.sos_bytes


def test_pin_lon_hon_thi_tuoi_tho_dai_hon():
    small = NodePowerParams(battery_mah=1000.0)
    big = NodePowerParams(battery_mah=10000.0)
    assert battery_life_days(big, PROFILE, NodeDutyCycle()) > battery_life_days(
        small, PROFILE, NodeDutyCycle()
    )


def test_kiem_tra_loi_tham_so():
    for kwargs in (
        {"battery_mah": 0.0},
        {"sleep_current_ma": -1.0},
        {"usable_fraction": 0.0},
        {"usable_fraction": 1.5},
    ):
        try:
            NodePowerParams(**kwargs)
        except ValueError:
            continue
        raise AssertionError(f"tham số không hợp lệ phải báo lỗi: {kwargs}")


def test_voi_che_do_ngu_thi_chi_phi_vo_tuyen_khong_chi_phoi():
    """Trên nút một sóng, phát LoRa không phải khối chi phối khi nút ngủ theo lịch."""
    parts = charge_per_day_mah(NodePowerParams(), LoraProfile(7, 125_000, 1), NodeDutyCycle())
    assert parts["tx_beacon"] < parts["self_discharge"]
    assert parts["tx_sos"] < parts["baseline"]


def test_moi_thanh_phan_dien_luong_deu_khong_am():
    parts = charge_per_day_mah(
        NodePowerParams(),
        PROFILE,
        NodeDutyCycle(rx_fraction=0.3, imu_active_hours_per_day=2.0),
    )
    assert all(v >= 0 for v in parts.values())


def test_imu_lay_mau_cao_lam_tang_dien_luong():
    idle = NodeDutyCycle(imu_active_hours_per_day=0.0)
    active = NodeDutyCycle(imu_active_hours_per_day=24.0)
    a = charge_per_day_mah(NodePowerParams(), PROFILE, idle)["imu"]
    b = charge_per_day_mah(NodePowerParams(), PROFILE, active)["imu"]
    assert b > a


if __name__ == "__main__":
    import traceback

    tests = [
        v
        for k, v in sorted(globals().items())
        if k.startswith("test_") and callable(v)
    ]
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
