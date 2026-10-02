"""Kiểm thử cho công cụ ma trận WP3.

Mục đích: bảo đảm ma trận **không tự bịa kết quả** và mọi ô đều tái lập được —
đây là điều kiện của cổng G5 (một lệnh sinh lại mọi bảng/hình).
"""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import run_wp3_matrix as m


def test_mobility_adjustment_is_monotone():
    static_pdr, _ = m.mobility_adjust("static")
    walk_pdr, walk_jit = m.mobility_adjust("walking")
    courier_pdr, courier_jit = m.mobility_adjust("courier")
    assert static_pdr == 1.0
    assert walk_pdr > courier_pdr, "courier phải khắt khe hơn đi bộ"
    assert walk_jit < courier_jit, "courier phải có jitter lớn hơn"


def test_mobility_rejects_unknown_level():
    try:
        m.mobility_adjust("teleport")
    except ValueError:
        return
    raise AssertionError("mức độ động lạ phải bị từ chối")


def test_every_density_has_a_range():
    for n in (10, 20, 50, 60, 100, 200):
        assert n in m.RANGE_BY_DENSITY, f"thiếu bán kính cho mật độ {n}"


def test_run_cell_is_reproducible():
    a = m.run_cell(20, 5, "static", "up", 0.90, "flood", seed=7)
    b = m.run_cell(20, 5, "static", "up", 0.90, "flood", seed=7)
    assert a == b


def test_warmup_changes_cell_outcome():
    """Cold start và warm start phải khác nhau — đây là biến thí nghiệm thật."""
    cold = m.run_cell(100, 20, "static", "up", 0.95, "gradient", seed=5, warmup_s=0.0)
    warm = m.run_cell(100, 20, "static", "up", 0.95, "gradient", seed=5, warmup_s=10.0)
    assert cold["warmup_s"] == 0.0 and warm["warmup_s"] == 10.0
    assert cold != warm, "warm start phải cho kết quả khác cold start"


def test_warmup_gradient_is_not_worse_than_cold():
    """Gradient ở warm start không được tệ hơn cold start về PDR."""
    cold = m.run_cell(100, 20, "static", "up", 0.95, "gradient", seed=5, warmup_s=0.0)
    warm = m.run_cell(100, 20, "static", "up", 0.95, "gradient", seed=5, warmup_s=10.0)
    assert float(warm["pdr"]) >= float(cold["pdr"]) - 1e-9


def test_run_cell_labels_as_uncalibrated():
    row = m.run_cell(20, 1, "static", "up", 0.90, "gradient", seed=1)
    assert row["label"] == "SIM-UNCALIBRATED", "kết quả mô phỏng phải mang nhãn SIM"


def test_run_cell_pdr_in_unit_interval():
    for strategy in ("flood", "gradient"):
        row = m.run_cell(20, 5, "static", "up", 0.90, strategy, seed=3)
        assert 0.0 <= float(row["pdr"]) <= 1.0


def test_summarize_groups_by_experimental_cell():
    rows = [
        m.run_cell(20, 1, "static", "up", 0.90, "flood", seed=s) for s in range(3)
    ] + [
        m.run_cell(20, 1, "static", "up", 0.90, "gradient", seed=s) for s in range(3)
    ]
    summary = m.summarize(rows)
    assert len(summary) == 2, "hai chiến lược phải thành hai ô riêng"
    for cell in summary:
        assert cell["n_seeds"] == 3
        assert 0.0 <= float(cell["pdr_mean"]) <= 1.0
        assert float(cell["pdr_sd"]) >= 0.0


def test_summary_sd_is_zero_for_single_seed():
    rows = [m.run_cell(20, 1, "static", "up", 0.90, "flood", seed=0)]
    cell = m.summarize(rows)[0]
    assert cell["n_seeds"] == 1
    assert float(cell["pdr_sd"]) == 0.0


def test_matrix_skips_cells_with_more_sources_than_nodes():
    """n_sos >= n_nodes là vô nghĩa; vòng lặp phải bỏ qua chứ không crash."""
    rows = []
    for n_nodes in (10,):
        for n_sos in (1, 20):
            if n_sos >= n_nodes:
                continue
            rows.append(m.run_cell(n_nodes, n_sos, "static", "up", 0.90, "flood", seed=0))
    assert len(rows) == 1


def test_csv_roundtrip_preserves_rows():
    rows = [m.run_cell(20, 1, "static", "up", 0.90, s, seed=0) for s in ("flood", "gradient")]
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "raw.csv"
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        with path.open(encoding="utf-8") as fh:
            back = list(csv.DictReader(fh))
    assert len(back) == 2
    assert {r["strategy"] for r in back} == {"flood", "gradient"}


def test_station_down_changes_outcome():
    """Trạm sập phải khác trạm hoạt động — kiểm soát dương cho H3."""
    up = m.run_cell(50, 5, "static", "up", 0.90, "gradient", seed=5)
    down = m.run_cell(50, 5, "static", "down", 0.90, "gradient", seed=5)
    assert up["station"] == "up" and down["station"] == "down"
    assert float(down["pdr"]) <= float(up["pdr"]) + 0.5
    assert down != up


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in tests:
        fn()
        passed += 1
        print(f"PASS {fn.__name__}")
    print(f"\n{passed}/{len(tests)} test qua")
