"""Kiểm thử bộ mô phỏng mạng LoRa `sim_lora.py` (chỉ thư viện chuẩn).

Chạy::

    cd rescuemesh && python3 -m unittest -v test_sim_lora

Mọi khẳng định ở đây kiểm tra **cơ chế của mô hình** (SIM), không kiểm chứng
số liệu thực địa. Các bất biến được chọn để không phụ thuộc hằng số hiệu chuẩn.
"""

from __future__ import annotations

import math
import unittest

from sim_lora import STRATEGIES, LoraSimConfig, run_matrix, simulate_once


def _cfg(**kw) -> LoraSimConfig:
    """Cấu hình nhỏ, tắt beacon khi cần để test nhanh và tất định."""
    base = dict(
        n_nodes=20,
        area_m=1000.0,
        sf=9,
        n_sos=5,
        sos_interval_s=8.0,
        duration_s=200.0,
        n_gateways=1,
        beacon_interval_s=30.0,
        duty_cycle_enabled=False,
    )
    base.update(kw)
    return LoraSimConfig(**base)


class TestReproducibility(unittest.TestCase):
    """1. Cùng seed + cùng cấu hình phải cho kết quả bằng nhau từng trường."""

    def test_same_seed_same_result(self) -> None:
        cfg = _cfg()
        a = simulate_once(cfg, "flood", seed=11)
        b = simulate_once(cfg, "flood", seed=11)
        self.assertEqual(a.as_row(), b.as_row())

    def test_same_seed_all_strategies(self) -> None:
        for strategy in STRATEGIES:
            cfg = _cfg(n_couriers=3 if strategy == "store_carry_forward" else 0)
            a = simulate_once(cfg, strategy, seed=5)
            b = simulate_once(cfg, strategy, seed=5)
            self.assertEqual(a.as_row(), b.as_row(), msg=strategy)

    def test_seed_field_recorded(self) -> None:
        res = simulate_once(_cfg(), "flood", seed=99)
        self.assertEqual(res.seed, 99)


class TestControls(unittest.TestCase):
    """2. Kiểm soát âm: các cấu hình phải cho kết quả suy biến đúng như mong đợi."""

    def test_zero_gateways_gives_zero_pdr(self) -> None:
        cfg = _cfg(n_gateways=0, link_pdr=1.0, beacon_interval_s=None)
        res = simulate_once(cfg, "flood", seed=1)
        self.assertEqual(res.delivered, 0)
        self.assertEqual(res.pdr, 0.0)

    def test_ttl_one_means_source_only(self) -> None:
        cfg = _cfg(
            n_nodes=15,
            n_sos=4,
            ttl=1,
            link_pdr=1.0,
            beacon_interval_s=None,
            sos_interval_s=20.0,
            duration_s=200.0,
        )
        res = simulate_once(cfg, "flood", seed=3)
        self.assertEqual(res.delivered, 4)
        # Chỉ nguồn phát: mỗi tin đúng một khung dữ liệu.
        self.assertEqual(res.data_transmissions, 4)
        self.assertAlmostEqual(res.transmissions_per_delivered, 1.0, places=9)

    def test_ttl_two_allows_one_hop(self) -> None:
        # Cùng cấu hình: ttl=2 cho phép một chặng chuyển tiếp, ttl=1 thì không.
        common = dict(
            n_nodes=15, n_sos=4, link_pdr=1.0, beacon_interval_s=None,
            sos_interval_s=20.0, duration_s=200.0, flood_jitter_s=1.0,
        )
        res1 = simulate_once(_cfg(ttl=1, **common), "flood", seed=3)
        res2 = simulate_once(_cfg(ttl=2, **common), "flood", seed=3)
        self.assertGreater(res2.data_transmissions, res1.data_transmissions)
        self.assertGreater(res2.total_transmissions, res1.total_transmissions)

    def test_duty_cycle_zero_blocks_everything(self) -> None:
        cfg = _cfg(duty_cycle=0.0, duty_cycle_enabled=True)
        res = simulate_once(cfg, "flood", seed=2)
        self.assertEqual(res.total_transmissions, 0)
        self.assertGreater(res.deferred_count, 0)
        self.assertEqual(res.pdr, 0.0)


class TestCollisionAndDutyCycle(unittest.TestCase):
    """3–5. Va chạm tăng theo mật độ; duty cycle làm giảm số lần phát."""

    def test_collisions_increase_with_density(self) -> None:
        common = dict(
            n_sos=10, sos_interval_s=1.0, duration_s=150.0,
            beacon_interval_s=10.0, duty_cycle_enabled=False, sf=9,
        )
        low = simulate_once(_cfg(n_nodes=15, **common), "flood", seed=4)
        high = simulate_once(_cfg(n_nodes=70, **common), "flood", seed=4)
        self.assertGreaterEqual(high.collisions, low.collisions)
        self.assertGreater(high.collisions, 0)

    def test_duty_cycle_reduces_transmissions(self) -> None:
        common = dict(
            n_nodes=25, n_sos=5, duration_s=120.0, beacon_interval_s=5.0,
            flood_jitter_s=1.0,
        )
        off = simulate_once(_cfg(duty_cycle_enabled=False, **common), "flood", seed=6)
        on = simulate_once(
            _cfg(duty_cycle_enabled=True, duty_cycle=0.0005, **common), "flood", seed=6
        )
        self.assertLess(on.total_transmissions, off.total_transmissions)
        self.assertGreater(on.deferred_count, 0)


class TestAirtimeAccounting(unittest.TestCase):
    """4. Airtime tổng phải bằng airtime điều khiển cộng airtime dữ liệu."""

    def test_sum_is_exact(self) -> None:
        for kwargs in (
            {},
            {"duty_cycle_enabled": True, "duty_cycle": 0.01},
            {"beacon_interval_s": None},
            {"capture_enabled": False},
        ):
            res = simulate_once(_cfg(**kwargs), "managed_flood", seed=8)
            self.assertAlmostEqual(
                res.airtime_total_s,
                res.airtime_control_s + res.airtime_data_s,
                places=12,
            )

    def test_zero_when_blocked(self) -> None:
        res = simulate_once(_cfg(duty_cycle=0.0, duty_cycle_enabled=True), "flood", seed=8)
        self.assertEqual(res.airtime_total_s, 0.0)
        self.assertEqual(res.airtime_control_s, 0.0)
        self.assertEqual(res.airtime_data_s, 0.0)
        self.assertEqual(res.control_airtime_ratio, 0.0)

    def test_control_counts_beacons(self) -> None:
        res = simulate_once(_cfg(beacon_interval_s=10.0), "gradient", seed=8)
        self.assertGreater(res.airtime_control_s, 0.0)
        self.assertGreater(res.control_transmissions, 0)


class TestPhyAndBeaconEffects(unittest.TestCase):
    """6–7. SF cao hơn không tốt hơn; beacon dày hơn làm tăng tỉ lệ airtime điều khiển."""

    def test_sf9_not_better_than_sf7(self) -> None:
        common = dict(
            n_nodes=60, n_sos=10, sos_interval_s=2.0, duration_s=180.0,
            beacon_interval_s=30.0, duty_cycle_enabled=False,
        )
        r7 = simulate_once(_cfg(sf=7, **common), "flood", seed=9)
        r9 = simulate_once(_cfg(sf=9, **common), "flood", seed=9)
        self.assertTrue(
            r9.pdr <= r7.pdr + 1e-12
            or r9.transmissions_per_delivered >= r7.transmissions_per_delivered - 1e-12
        )

    def test_more_beacons_more_control_ratio(self) -> None:
        common = dict(n_nodes=20, n_sos=3, duration_s=120.0, sf=9)
        sparse = simulate_once(_cfg(beacon_interval_s=60.0, **common), "flood", seed=12)
        dense = simulate_once(_cfg(beacon_interval_s=5.0, **common), "flood", seed=12)
        self.assertGreater(dense.control_airtime_ratio, sparse.control_airtime_ratio)


class TestFairnessAndDelivery(unittest.TestCase):
    """8. Jain trong [0, 1] và bằng 1 khi mọi nguồn đều được giao như nhau."""

    def test_jain_in_range(self) -> None:
        for strategy in STRATEGIES:
            for n_nodes in (15, 50):
                cfg = _cfg(n_nodes=n_nodes, n_couriers=3 if strategy == "store_carry_forward" else 0)
                res = simulate_once(cfg, strategy, seed=13)
                self.assertGreaterEqual(res.jain_fairness, 0.0)
                self.assertLessEqual(res.jain_fairness, 1.0)

    def test_jain_one_when_uniform(self) -> None:
        cfg = _cfg(
            n_nodes=25, n_sos=5, link_pdr=1.0, beacon_interval_s=None,
            sos_interval_s=20.0, duration_s=200.0,
        )
        res = simulate_once(cfg, "flood", seed=14)
        self.assertEqual(res.delivered, 5)
        self.assertAlmostEqual(res.jain_fairness, 1.0, places=12)

    def test_per_source_sums_to_delivered(self) -> None:
        res = simulate_once(_cfg(), "trickle", seed=15)
        self.assertEqual(len(res.per_source_delivered), res.total_sos)
        self.assertEqual(sum(res.per_source_delivered.values()), res.delivered)
        self.assertLessEqual(res.delivered, res.total_sos)
        self.assertGreaterEqual(res.pdr, 0.0)
        self.assertLessEqual(res.pdr, 1.0)

    def test_latency_ordered_and_finite(self) -> None:
        res = simulate_once(_cfg(), "managed_flood", seed=16)
        self.assertGreaterEqual(res.latency_p50, 0.0)
        self.assertLessEqual(res.latency_p50, res.latency_p95 + 1e-12)
        for value in res.as_row().values():
            if isinstance(value, float):
                self.assertFalse(math.isnan(value), msg=str(value))


class TestComparisons(unittest.TestCase):
    """9–10. Cold/warm phải khác nhau; tham số sai phải ném ValueError."""

    def test_cold_and_warm_differ(self) -> None:
        common = dict(
            n_nodes=40, n_sos=5, sf=9, sos_interval_s=6.0, duration_s=240.0,
            beacon_interval_s=30.0, duty_cycle_enabled=False,
        )
        warm = simulate_once(_cfg(warm_start=True, **common), "gradient", seed=2)
        cold = simulate_once(_cfg(warm_start=False, **common), "gradient", seed=2)
        # Bất biến: chỉ khẳng định KHÁC, không khẳng định chiều.
        self.assertNotEqual(warm.as_row(), cold.as_row())

    def test_invalid_n_nodes(self) -> None:
        with self.assertRaises(ValueError):
            LoraSimConfig(n_nodes=0)
        with self.assertRaises(ValueError):
            LoraSimConfig(n_nodes=-5)

    def test_invalid_ttl(self) -> None:
        with self.assertRaises(ValueError):
            LoraSimConfig(ttl=0)
        with self.assertRaises(ValueError):
            LoraSimConfig(ttl=-1)

    def test_invalid_sf(self) -> None:
        with self.assertRaises(ValueError):
            LoraSimConfig(sf=4)
        with self.assertRaises(ValueError):
            LoraSimConfig(sf=13)

    def test_invalid_strategy(self) -> None:
        with self.assertRaises(ValueError):
            simulate_once(_cfg(), "khong_ton_tai", seed=1)

    def test_invalid_other_params(self) -> None:
        for kwargs in (
            {"n_gateways": 3},
            {"duty_cycle": 2.0},
            {"area_m": 0.0},
            {"duration_s": -1.0},
            {"link_pdr": 1.5},
            {"n_couriers": -1},
        ):
            with self.assertRaises(ValueError, msg=str(kwargs)):
                LoraSimConfig(**kwargs)


class TestCaptureAndFeatures(unittest.TestCase):
    """Capture, courier, gateway outage và ma trận."""

    def test_huge_capture_db_equals_disabled(self) -> None:
        common = dict(n_nodes=40, n_sos=8, sos_interval_s=2.0, duration_s=150.0, sf=9)
        off = simulate_once(_cfg(capture_enabled=False, **common), "flood", seed=17)
        huge = simulate_once(
            _cfg(capture_enabled=True, capture_db=1e9, **common), "flood", seed=17
        )
        self.assertEqual(off.collisions, huge.collisions)
        self.assertEqual(off.as_row(), huge.as_row())

    def test_store_carry_forward_runs_and_delivers(self) -> None:
        cfg = _cfg(n_nodes=30, n_sos=5, n_couriers=3, link_pdr=1.0,
                   beacon_interval_s=None)
        res = simulate_once(cfg, "store_carry_forward", seed=18)
        self.assertGreater(res.delivered, 0)

    def test_gateway_outage_reconvergence(self) -> None:
        no_outage = simulate_once(_cfg(gateway_outage=None), "flood", seed=19)
        self.assertEqual(no_outage.reconvergence_s, 0.0)
        with_outage = simulate_once(
            _cfg(gateway_outage=(40.0, 90.0), n_sos=8, sos_interval_s=10.0,
                 duration_s=240.0),
            "flood",
            seed=19,
        )
        self.assertGreaterEqual(with_outage.reconvergence_s, 0.0)
        self.assertLessEqual(with_outage.reconvergence_s, 240.0)

    def test_run_matrix_small(self) -> None:
        cells = [
            {"strategy": "flood", "n_nodes": 12, "n_sos": 3, "sf": 7, "warm_start": False},
            {"strategy": "gradient", "n_nodes": 12, "n_sos": 3, "sf": 7, "warm_start": True},
        ]
        raw, summary = run_matrix(seeds=range(2), cells=cells)
        self.assertEqual(len(raw), 4)
        self.assertEqual(len(summary), 2)
        self.assertTrue(all(row["evidence"] == "SIM" for row in raw))
        self.assertTrue(all(row["evidence"] == "SIM" for row in summary))
        self.assertEqual(summary[0]["n_seeds"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
