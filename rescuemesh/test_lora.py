"""Kiểm thử module vật lý LoRa.

Nguyên tắc: các test này kiểm **tính chất** (đơn điệu, biên, đối chiếu công
thức độc lập) và **ghim hồi quy** giá trị đã tính. Chúng KHÔNG chứng minh mô
hình đúng với thực tế — muốn vậy phải đối chiếu datasheet và đo thiết bị thật.
"""

from __future__ import annotations

import math

from lora import (
    BAND_VN_920_923_HZ,
    GatewayCapacity,
    LoraProfile,
    PATH_LOSS_EXPONENT,
    fspl_db,
    gateway_capacity,
    gateway_capacity_mixed,
    link_budget_db,
    link_margin_db,
    max_range_m,
    path_loss_log_distance_db,
    sf_tradeoff_table,
)


# --------------------------------------------------------------------------
# Modem
# --------------------------------------------------------------------------


def test_bitrate_known_values():
    """SF7/BW125/CR4-5 = 5468,75 bps; SF12/BW125/CR4-5 ≈ 292,97 bps."""
    assert abs(LoraProfile(7, 125_000, 1).bitrate_bps - 5468.75) < 0.01
    assert abs(LoraProfile(12, 125_000, 1).bitrate_bps - 292.96875) < 0.01


def test_bitrate_tang_theo_sf():
    rates = [LoraProfile(sf, 125_000, 1).bitrate_bps for sf in range(7, 13)]
    assert rates == sorted(rates, reverse=True)


def test_airtime_ghim_hoi_quy():
    """Giá trị đã biết: SF7 ≈ 56,6 ms và SF12 ≈ 1,48 s cho payload 24 B."""
    t7 = LoraProfile(7, 125_000, 1).airtime_s(24)
    t12 = LoraProfile(12, 125_000, 1).airtime_s(24)
    assert 0.050 < t7 < 0.065
    assert 1.40 < t12 < 1.55


def test_airtime_tang_theo_sf_va_payload():
    prev = 0.0
    for sf in range(7, 13):
        t = LoraProfile(sf, 125_000, 1).airtime_s(40)
        assert t > prev
        prev = t
    p = LoraProfile(9, 125_000, 1)
    assert p.airtime_s(40) > p.airtime_s(20) > p.airtime_s(1)


def test_airtime_giam_khi_tang_bang_thong():
    t125 = LoraProfile(9, 125_000, 1).airtime_s(40)
    t250 = LoraProfile(9, 250_000, 1).airtime_s(40)
    t500 = LoraProfile(9, 500_000, 1).airtime_s(40)
    assert t125 > t250 > t500


def test_airtime_tang_khi_coding_rate_thap():
    ts = [LoraProfile(9, 125_000, cr).airtime_s(40) for cr in (1, 2, 3, 4)]
    assert ts == sorted(ts)


def test_low_data_rate_optimize_bat_dung_luc():
    assert LoraProfile(11, 125_000, 1).low_data_rate_optimize == 1
    assert LoraProfile(12, 125_000, 1).low_data_rate_optimize == 1
    assert LoraProfile(10, 125_000, 1).low_data_rate_optimize == 0
    assert LoraProfile(12, 250_000, 1).low_data_rate_optimize == 0


def test_airtime_bang_cong_thuc_doc_lap():
    """Đối chiếu số ký tự payload với cách tính độc lập thứ hai."""
    sf, pl, cr = 9, 40, 1
    profile = LoraProfile(sf, 125_000, cr)
    tsym = (2 ** sf) / 125_000
    t_total = profile.airtime_s(pl)
    t_preamble = (8 + 4.25) * tsym
    n_sym = round((t_total - t_preamble) / tsym)
    # Công thức Semtech: n = 8 + ceil((8·PL − 4·SF + 28 + 16 − 0)/(4·(SF − 0)))·(CR+4)
    expected = 8 + math.ceil((8 * pl - 4 * sf + 44) / (4 * sf)) * (cr + 4)
    assert n_sym == expected


def test_kiem_tra_bien_va_loi():
    for bad in (0, -1):
        try:
            LoraProfile(9, bad, 1)
        except ValueError:
            continue
        raise AssertionError("băng thông không hợp lệ phải báo lỗi")
    try:
        LoraProfile(13, 125_000, 1)
    except ValueError:
        pass
    else:
        raise AssertionError("SF ngoài dải phải báo lỗi")
    try:
        LoraProfile(9, 125_000, 5)
    except ValueError:
        pass
    else:
        raise AssertionError("CR ngoài dải phải báo lỗi")


def test_energy_ti_le_voi_airtime():
    p = LoraProfile(9, 125_000, 1)
    e1 = p.energy_per_frame_j(20, tx_power_w=0.1)
    e2 = p.energy_per_frame_j(40, tx_power_w=0.1)
    assert e2 > e1 > 0
    assert abs(e1 - 0.1 * p.airtime_s(20)) < 1e-12


# --------------------------------------------------------------------------
# Lan truyền
# --------------------------------------------------------------------------


def test_fspl_gia_tri_da_biet():
    """1 km ở 868 MHz ≈ 91,2 dB; 1 m ở 868 MHz ≈ 31,2 dB."""
    assert abs(fspl_db(1000.0, 868e6) - 91.2) < 0.2
    assert abs(fspl_db(1.0, 868e6) - 31.2) < 0.2


def test_fspl_tang_6db_khi_gap_doi_khoang_cach():
    assert abs((fspl_db(2000.0, 868e6) - fspl_db(1000.0, 868e6)) - 6.02) < 0.05


def test_log_distance_bang_fspl_khi_n_bang_2():
    for d in (10.0, 100.0, 1000.0):
        a = path_loss_log_distance_db(d, 868e6, exponent=2.0)
        b = fspl_db(d, 868e6)
        assert abs(a - b) < 1e-9


def test_tam_xa_giam_khi_moi_truong_kho_khan_hon():
    kwargs = dict(
        freq_hz=BAND_VN_920_923_HZ, tx_dbm=14.0, sensitivity_dbm=-132.0
    )
    r_fs = max_range_m(exponent=PATH_LOSS_EXPONENT["free_space"], **kwargs)
    r_sub = max_range_m(exponent=PATH_LOSS_EXPONENT["suburban"], **kwargs)
    r_urb = max_range_m(exponent=PATH_LOSS_EXPONENT["urban"], **kwargs)
    assert r_fs > r_sub > r_urb > 0


def test_bien_du_trai_dau_hai_ben_gioi_han_tam_xa():
    kwargs = dict(
        freq_hz=BAND_VN_920_923_HZ,
        exponent=PATH_LOSS_EXPONENT["suburban"],
        tx_dbm=14.0,
        sensitivity_dbm=-132.0,
    )
    r = max_range_m(**kwargs)
    assert link_margin_db(distance_m=r * 0.9, **kwargs) > 0
    assert link_margin_db(distance_m=r * 1.1, **kwargs) < 0


def test_ngan_sach_duong_truyen_dung_cong_thuc():
    assert abs(link_budget_db(14.0, 2.0, 2.0, 2.0, -132.0) - 148.0) < 1e-9


def test_sensitivity_giam_theo_sf_va_bang_thong():
    """Bảng SX1276 đã xác minh từ datasheet: SF6 −118 … SF12 −136 dBm ở BW125."""
    sens = [LoraProfile(sf, 125_000, 1).sensitivity_dbm() for sf in range(6, 13)]
    assert sens == sorted(sens, reverse=True)
    assert sens[0] == -118.0 and sens[-1] == -136.0
    assert (
        LoraProfile(9, 500_000, 1).sensitivity_dbm()
        > LoraProfile(9, 125_000, 1).sensitivity_dbm()
    )


def test_sensitivity_tu_choi_sf_khong_co_trong_datasheet():
    """Không nội suy SF5: thà báo lỗi còn hơn tạo số liệu không nguồn."""
    try:
        LoraProfile(5, 125_000, 1).sensitivity_dbm()
    except ValueError:
        pass
    else:
        raise AssertionError("SF5 phải báo lỗi vì datasheet BW125 không có SF5")


# --------------------------------------------------------------------------
# Sức chứa
# --------------------------------------------------------------------------


def test_suc_chua_hon_hop_cong_dung_thanh_phan():
    c = gateway_capacity_mixed(
        LoraProfile(9, 125_000, 1),
        sos_bytes=36,
        beacon_bytes=18,
        n_nodes=100,
        sos_per_node_per_hour=1.0,
        beacon_interval_s=60.0,
        relay_multiplier=3.0,
    )
    assert abs(
        c.airtime_per_node_hour_s
        - (c.sos_airtime_per_node_hour_s + c.beacon_airtime_per_node_hour_s)
    ) < 1e-12
    assert abs(c.utilisation - 100 * c.airtime_per_node_hour_s / 3600.0) < 1e-12


def test_suc_chua_hon_hop_diem_bao_hoa_bang_mot_kenh():
    c = gateway_capacity_mixed(
        LoraProfile(9, 125_000, 1), 36, 18, 10, 1.0, 300.0, 1.0
    )
    assert abs(c.saturation_nodes * c.airtime_per_node_hour_s - 3600.0) < 1e-9
    assert c.max_nodes_at_target < c.saturation_nodes


def test_suc_chua_hon_hop_khong_beacon_thi_chi_con_sos():
    c = gateway_capacity_mixed(
        LoraProfile(9, 125_000, 1), 36, 18, 100, 1.0, None, 1.0
    )
    assert c.beacon_airtime_per_node_hour_s == 0.0
    assert c.airtime_per_node_hour_s == c.sos_airtime_per_node_hour_s


def test_suc_chua_hon_hop_payload_lon_hon_thi_it_nut_hon():
    small = gateway_capacity_mixed(
        LoraProfile(9, 125_000, 1), 20, 18, 100, 1.0, 300.0, 1.0
    )
    large = gateway_capacity_mixed(
        LoraProfile(9, 125_000, 1), 60, 18, 100, 1.0, 300.0, 1.0
    )
    assert large.utilisation > small.utilisation
    assert large.max_nodes_at_target < small.max_nodes_at_target


def test_suc_chua_hon_hop_beacon_chi_phoi_o_chu_ky_thuc_dung():
    """Ở beacon 60–300 s, điều khiển chiếm phần lớn airtime của nút (cơ sở H3)."""
    for interval in (60.0, 300.0):
        c = gateway_capacity_mixed(
            LoraProfile(9, 125_000, 1), 36, 18, 100, 1.0, interval, 3.0
        )
        share = c.beacon_airtime_per_node_hour_s / c.airtime_per_node_hour_s
        assert share > 0.7, f"beacon {interval}s chiếm {share:.2%}"


def test_suc_chua_hon_hop_kiem_tra_loi():
    try:
        gateway_capacity_mixed(LoraProfile(9, 125_000, 1), 36, 18, 0, 1.0, 60.0)
    except ValueError:
        pass
    else:
        raise AssertionError("n_nodes = 0 phải báo lỗi")


def test_suc_chua_giam_khi_airtime_dai_hon():
    caps = []
    for sf in (7, 9, 12):
        caps.append(
            gateway_capacity(
                LoraProfile(sf, 125_000, 1),
                payload_bytes=40,
                n_nodes=100,
                sos_per_node_per_hour=2.0,
                beacon_interval_s=60.0,
                relay_multiplier=3.0,
            )
        )
    assert caps[0].utilisation < caps[1].utilisation < caps[2].utilisation
    assert (
        caps[0].max_nodes_at_cap
        > caps[1].max_nodes_at_cap
        > caps[2].max_nodes_at_cap
    )


def test_suc_chua_ti_le_nghich_voi_so_khung():
    profile = LoraProfile(9, 125_000, 1)
    base = gateway_capacity(
        profile, 40, n_nodes=100, sos_per_node_per_hour=1.0,
        beacon_interval_s=None, relay_multiplier=1.0,
    )
    doubled = gateway_capacity(
        profile, 40, n_nodes=100, sos_per_node_per_hour=2.0,
        beacon_interval_s=None, relay_multiplier=1.0,
    )
    assert abs(doubled.utilisation - 2 * base.utilisation) < 1e-12


def test_khong_beacon_thi_tai_thap_hon():
    profile = LoraProfile(9, 125_000, 1)
    with_beacon = gateway_capacity(
        profile, 40, 100, 1.0, beacon_interval_s=60.0, relay_multiplier=1.0
    )
    without = gateway_capacity(
        profile, 40, 100, 1.0, beacon_interval_s=None, relay_multiplier=1.0
    )
    assert with_beacon.utilisation > without.utilisation


def test_beacon_day_dac_co_the_lam_bao_hoa():
    """Kiểm soát âm: beacon 1 s với SF12 phải làm gateway bão hoà."""
    cap = gateway_capacity(
        LoraProfile(12, 125_000, 1),
        payload_bytes=40,
        n_nodes=100,
        sos_per_node_per_hour=0.0,
        beacon_interval_s=1.0,
        relay_multiplier=3.0,
    )
    assert cap.utilisation > 1.0
    assert cap.saturated


def test_duty_cycle_la_gioi_han_chat_hon_bang_hoa():
    cap = gateway_capacity(
        LoraProfile(9, 125_000, 1), 40, 100, 1.0, 60.0, 3.0
    )
    assert cap.max_nodes_at_duty_cycle < cap.max_nodes_at_cap
    assert cap.violates_duty_cycle == (cap.utilisation > 0.01)


def test_kiem_tra_loi_suc_chua():
    profile = LoraProfile(9, 125_000, 1)
    for bad_nodes in (0, -5):
        try:
            gateway_capacity(profile, 40, bad_nodes, 1.0, 60.0)
        except ValueError:
            continue
        raise AssertionError("n_nodes không dương phải báo lỗi")


# --------------------------------------------------------------------------
# Bảng đánh đổi
# --------------------------------------------------------------------------


def test_bang_danh_doi_du_6_dong_va_don_dieu():
    rows = sf_tradeoff_table(payload_bytes=40)
    assert [r["sf"] for r in rows] == [7, 8, 9, 10, 11, 12]
    airtimes = [r["airtime_ms"] for r in rows]
    assert airtimes == sorted(airtimes)
    ranges = [r["range_km_urban"] for r in rows]
    assert ranges == sorted(ranges)
    for r in rows:
        assert r["range_km_free_space"] > r["range_km_suburban"] > r["range_km_urban"]


def test_bang_danh_doi_khong_am_va_hop_ly():
    for r in sf_tradeoff_table(payload_bytes=40):
        assert r["airtime_ms"] > 0
        assert r["bitrate_bps"] > 0
        assert r["max_frames_per_s"] > 0
        assert r["sensitivity_dbm"] < 0


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
