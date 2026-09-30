"""Ba thí nghiệm trọng tâm của RescueMesh-LoRa v2.1 (nhãn `SIM`, chưa hiệu chuẩn).

Chạy::

    cd rescuemesh && python3 run_lora_experiments.py

Sinh ra (thư mục `../results/`):

- `sim-lora-e1-control-raw.csv` / `-summary.csv` — **E1 (H3/R3b)**: ba chế độ mặt
  phẳng điều khiển × ba chính sách nghe × hai thuật toán × ba mật độ.
- `sim-lora-e2-courier-raw.csv` / `-summary.csv` — **E2 (H6)**: số nút di động
  0/1/3/10 cho `store_carry_forward`.
- `sim-lora-e3-link-raw.csv` / `-summary.csv` — **E3 (RQ6)**: độ trễ và tỉ lệ mất
  của link cá nhân điện thoại → nút cầu.

MỌI dòng CSV mang nhãn `evidence=SIM`. Không con số nào ở đây là `ĐO`, và mô hình
chưa được hiệu chuẩn với đo thực (cổng G9 của kế hoạch chưa đạt). Không được trích
các bảng này như kết quả hiệu năng thực.
"""

from __future__ import annotations

import csv
from pathlib import Path

from sim_lora import run_matrix

RESULTS = Path(__file__).resolve().parents[1] / "results"
SEEDS = range(20)

CONTROL_MODES = ("node_hello", "gateway_beacon", "gateway_beacon_relay")
RX_POLICIES = ("continuous", "windowed", "tx_only")
DENSITIES = (25, 50, 100)
STRATEGIES = ("flood", "gradient")


def e1_cells() -> list[dict]:
    """E1 — H3/R3b: chi phí điều khiển và hệ quả lên giao hàng."""
    return [
        {
            "strategy": strategy,
            "control_plane_mode": mode,
            "rx_policy": policy,
            "n_nodes": density,
            "n_sos": 20,
            "sf": 9,
            "warm_start": True,
            # Ghi khoá ô để CSV summary tách được từng chế độ.
            "cell_label": f"{mode}|{policy}|{strategy}|{density}",
        }
        for mode in CONTROL_MODES
        for policy in RX_POLICIES
        for strategy in STRATEGIES
        for density in DENSITIES
    ]


def e2_cells() -> list[dict]:
    """E2 — H6: lợi ích của lưu-chuyển-tiếp có đến từ nút di động không."""
    return [
        {
            "strategy": "store_carry_forward",
            "n_couriers": n_couriers,
            "n_nodes": density,
            "n_sos": 20,
            "sf": 9,
            "warm_start": True,
            "cell_label": f"courier{n_couriers}|{density}",
        }
        for n_couriers in (0, 1, 3, 10)
        for density in (50, 100)
    ]


def e3_cells() -> list[dict]:
    """E3 — RQ6: link cá nhân thêm độ trễ và mất mát.

    Độ trễ **suy ra có nguồn**, không phải trí nhớ:
    - `0,015 s` ≈ 1 connection event ở mức HIGH của AOSP (11,25–15 ms) khi MTU đã
      thương lượng (AOSP `Bluetooth/.../config.xml`; Core Spec 6.0);
    - `0,045 s` ≈ 3 gói ATT khi MTU mặc định 23 B (khung 36 B không vừa 1 gói);
    - `0,160 s` = **đuôi trễ** trong đám đông 44 piconet ở CCDF 10⁻⁴ (IEEE VTC2023).
    Mất khung: 0 · 1 % (đo được < 1 % khi có nhiễu — Biosensors 2021) · 10 % (xấu).
    """
    return [
        {
            "strategy": "flood",
            "link_delay_s": delay,
            "link_drop_prob": drop,
            "n_nodes": 50,
            "n_sos": 20,
            "sf": 9,
            "warm_start": True,
            "cell_label": f"delay{delay:.3f}|drop{drop:.2f}",
        }
        for delay in (0.0, 0.015, 0.045, 0.160)
        for drop in (0.0, 0.01, 0.10)
    ]


def e1b_cells() -> list[dict]:
    """E1b — R3b có phụ thuộc kịch bản? Vùng rộng 3 km (ít nút nghe trực tiếp gateway)."""
    return [
        {
            "strategy": strategy,
            "control_plane_mode": mode,
            "n_nodes": 100,
            "n_sos": 20,
            "sf": 9,
            "warm_start": True,
            "area_m": 3000.0,
            "cell_label": f"{mode}|{strategy}|3km",
        }
        for mode in CONTROL_MODES
        for strategy in STRATEGIES
    ]


def e2b_cells() -> list[dict]:
    """E2b — H6 với điều kiện CÓ LỢI cho courier: vùng 3 km, 15 phút, xe 10 m/s."""
    return [
        {
            "strategy": "store_carry_forward",
            "n_couriers": n_couriers,
            "n_nodes": 100,
            "n_sos": 20,
            "sf": 9,
            "warm_start": True,
            "area_m": 3000.0,
            "duration_s": 900.0,
            "courier_speed_m_s": 10.0,
            "courier_step_s": 5.0,
            "cell_label": f"courier{n_couriers}|3km|900s|xe",
        }
        for n_couriers in (0, 1, 3, 10)
    ]


def e4_cells() -> list[dict]:
    """E4 — H3 sửa lại: chi phí điều khiển theo chu kỳ quảng bá **thật**.

    Hệ thống thật dùng chu kỳ rất thưa (Meshtastic NodeInfo mặc định **10800 s**,
    MeshCore flood advert **12 h**), không phải 60–300 s. Ô dùng `beacon_phase_s`
    xác định và thời lượng ≥ 2× chu kỳ để phép đo có nghĩa.
    """
    cells = []
    for interval, duration in ((60.0, 300.0), (300.0, 1000.0),
                               (3600.0, 8000.0), (10800.0, 23000.0)):
        for mode in ("node_hello", "gateway_beacon", "adaptive_gateway"):
            cells.append({
                "strategy": "gradient",
                "control_plane_mode": mode,
                "beacon_interval_s": interval,
                "beacon_phase_s": interval * 0.2,
                "duration_s": duration,
                "n_nodes": 100,
                "n_sos": 20,
                "sf": 9,
                "warm_start": True,
                "cell_label": f"beacon{interval:.0f}s|{mode}",
            })
    return cells


def _print_e4(summary: list[dict]) -> None:
    print("\nE4 — chi phí điều khiển theo chu kỳ quảng bá (H3 sửa lại), SIM")
    print(f"{'ô':>28} {'ctl%':>7} {'PDR':>6} {'hop%':>6} "
          f"{'ctl mỗi nút/giờ':>16} {'bcn/nút/giờ':>12}")
    for row in summary:
        dur = row["duration_s"] if "duration_s" in row else 0.0
        n = row["n_nodes"]
        ctl_tx = row["mean_control_transmissions"]
        per_node_hour = ctl_tx / max(n, 1) * 3600.0 / dur if dur else 0.0
        print(f"{row['cell_label']:>28} {row['mean_control_airtime_ratio']:7.1%} "
              f"{row['mean_pdr']:6.3f} {row['mean_hop_learned_fraction']:6.1%} "
              f"{per_node_hour:16.2f} {per_node_hour:12.2f}")


def _write(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"  đã ghi {path.name}: {len(rows)} dòng")


def _run(name: str, cells: list[dict]) -> tuple[list[dict], list[dict]]:
    print(f"\n=== {name}: {len(cells)} ô × {len(list(SEEDS))} seed ===")
    raw, summary = run_matrix(seeds=SEEDS, cells=cells)
    assert all(r["evidence"] == "SIM" for r in raw), "raw thiếu nhãn SIM"
    assert all(r["evidence"] == "SIM" for r in summary), "summary thiếu nhãn SIM"
    _write(RESULTS / f"sim-lora-{name}-raw.csv", raw)
    _write(RESULTS / f"sim-lora-{name}-summary.csv", summary)
    return raw, summary


def _print_e1(summary: list[dict]) -> None:
    print("\nE1 — mặt phẳng điều khiển × chính sách nghe (trung bình 20 seed, SIM)")
    print(f"{'chế độ':22} {'chính sách':11} {'PDR':>6} {'điều khiển%':>12} "
          f"{'hop%':>6} {'thức%':>7} {'bỏ vì ngủ':>10}")
    for mode in CONTROL_MODES:
        for policy in RX_POLICIES:
            sel = [r for r in summary if r["cell_label"].startswith(f"{mode}|{policy}|")]
            if not sel:
                continue
            pdr = sum(r["mean_pdr"] for r in sel) / len(sel)
            ctl = sum(r["mean_control_airtime_ratio"] for r in sel) / len(sel)
            hop = sum(r["mean_hop_learned_fraction"] for r in sel) / len(sel)
            awake = sum(r["mean_mean_awake_fraction"] for r in sel) / len(sel)
            miss = sum(r["mean_missed_due_to_sleep"] for r in sel) / len(sel)
            print(f"{mode:22} {policy:11} {pdr:6.3f} {ctl:12.1%} {hop:6.1%} "
                  f"{awake:7.2%} {miss:10.0f}")


def _print_e1b(summary: list[dict]) -> None:
    print("\nE1b — vùng rộng 3 km, 100 nút (R3b có phụ thuộc kịch bản?), SIM")
    print(f"{'ô':>34} {'PDR':>7} {'điều khiển%':>12} {'hop%':>7} {'phát/giao':>10}")
    for row in summary:
        print(f"{row['cell_label']:>34} {row['mean_pdr']:7.3f} "
              f"{row['mean_control_airtime_ratio']:12.1%} "
              f"{row['mean_hop_learned_fraction']:7.1%} "
              f"{row['mean_transmissions_per_delivered']:10.2f}")


def _print_e2(summary: list[dict]) -> None:
    print("\nE2 — số nút di động (H6), trung bình 20 seed, SIM")
    print(f"{'ô':>16} {'PDR':>7} {'p95 (s)':>9} {'phát/giao':>10}")
    for row in summary:
        print(f"{row['cell_label']:>16} {row['mean_pdr']:7.3f} "
              f"{row['mean_latency_p95']:9.2f} "
              f"{row['mean_transmissions_per_delivered']:10.2f}")


def _print_e3(summary: list[dict]) -> None:
    print("\nE3 — link cá nhân (RQ6), trung bình 20 seed, SIM")
    print(f"{'ô':>18} {'PDR':>7} {'p50 (s)':>9} {'trễ link (s)':>13} {'mất link':>9}")
    for row in summary:
        print(f"{row['cell_label']:>18} {row['mean_pdr']:7.3f} "
              f"{row['mean_latency_p50']:9.3f} {row['mean_mean_link_delay_s']:13.3f} "
              f"{row['mean_link_failures']:9.2f}")


def main() -> int:
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    print("=" * 100)
    print("THÍ NGHIỆM TRỌNG TÂM v2.1 — nhãn SIM, CHƯA hiệu chuẩn (cổng G9 chưa đạt)")
    print("=" * 100)
    if which in ("all", "e1"):
        _, s1 = _run("e1-control", e1_cells())
        _print_e1(s1)
    if which in ("all", "e1b"):
        _, s1b = _run("e1b-wide", e1b_cells())
        _print_e1b(s1b)
    if which in ("all", "e2"):
        _, s2 = _run("e2-courier", e2_cells())
        _print_e2(s2)
    if which in ("all", "e2b"):
        _, s2b = _run("e2b-courier-fair", e2b_cells())
        _print_e2(s2b)
    if which in ("all", "e3"):
        _, s3 = _run("e3-link", e3_cells())
        _print_e3(s3)
    if which in ("all", "e4"):
        _, s4 = _run("e4-beacon-interval", e4_cells())
        _print_e4(s4)
    print("\nGHI CHÚ: mọi số là mô hình (SIM); không dùng để kết luận hiệu năng thực.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
