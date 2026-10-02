"""Chạy ma trận thí nghiệm mesh WP3 — simulator v2.

Sinh bảng kết quả có seed, phục vụ H2/H3 và RQ2. Mọi dòng mang nhãn ``SIM``:
mô hình **chưa hiệu chuẩn** với PDR đo thực (cổng G3 chưa qua), nên **không**
được dùng để tuyên bố gradient tốt hơn flooding trên thiết bị thật.

Cách dùng::

    ../.venv/bin/python run_wp3_matrix.py            # ma trận đầy đủ
    ../.venv/bin/python run_wp3_matrix.py --quick    # rút gọn để kiểm tra
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from pathlib import Path

from sim_v2 import ALL_STRATEGIES, SimConfig, random_geometric_graph, simulate

# Ma trận theo ke-hoach-nghien-cuu-rescuemesh-ai.md §10.2
DENSITIES_FULL = (10, 50, 100, 200)
DENSITIES_QUICK = (20, 60)
LOADS_FULL = (1, 5, 20, 50, 100)
LOADS_QUICK = (1, 5, 20)
MOBILITY_FULL = ("static", "walking", "courier")
MOBILITY_QUICK = ("static",)
STATION_FULL = ("up", "down", "recovered")
STATION_QUICK = ("up", "down")
PDR_LEVELS_FULL = (0.95, 0.85, 0.70)
PDR_LEVELS_QUICK = (0.90,)
SEEDS_FULL = 30
SEEDS_QUICK = 6

# Beacon 2 s: đủ nhanh để gradient hội tụ trong horizon, vẫn thấy được chi phí.
BEACON_INTERVAL_S = 2.0

# Chế độ khởi động. Cold = SOS phát ngay khi beacon bắt đầu (gradient chưa có).
# Warm = chờ 10 s cho gradient hội tụ rồi mới phát SOS.
WARMUP_FULL = (0.0, 10.0)
WARMUP_QUICK = (10.0,)

# Bán kính liên kết theo mật độ để giữ mạng liên thông ở mọi mức.
AREA_M = 400.0
RANGE_BY_DENSITY = {10: 190.0, 20: 140.0, 50: 95.0, 60: 90.0, 100: 70.0, 200: 52.0}


def _mobility_note(nodes_alive_fraction: float) -> float:
    """Mobility được mô hình hoá gián tiếp: đi bộ/courier làm mất liên kết tạm thời.

    Mô hình v2 chưa có chuyển động liên tục; ta biểu diễn độ động bằng cách hạ
    PDR hiệu dụng và tăng jitter, và ghi rõ đây là **xấp xỉ** cho tới khi có
    mô hình di động thật.
    """
    return nodes_alive_fraction


def mobility_adjust(mobility: str) -> tuple[float, float]:
    """Trả về (hệ số PDR, hệ số jitter) cho từng mức độ động."""
    if mobility == "static":
        return 1.0, 1.0
    if mobility == "walking":
        return 0.90, 1.5
    if mobility == "courier":
        return 0.75, 2.5
    raise ValueError(mobility)


def run_cell(
    n_nodes: int,
    n_sos: int,
    mobility: str,
    station_state: str,
    link_pdr: float,
    strategy: str,
    seed: int,
    warmup_s: float = 0.0,
) -> dict[str, object]:
    pdr_factor, jitter_factor = mobility_adjust(mobility)
    effective_pdr = link_pdr * pdr_factor

    horizon = 30.0 if n_sos <= 20 else 60.0
    cfg = SimConfig(
        n_nodes=n_nodes,
        n_sos=n_sos,
        link_pdr=effective_pdr,
        area_m=AREA_M,
        range_m=RANGE_BY_DENSITY[n_nodes],
        jitter_min_s=0.010 * jitter_factor,
        jitter_max_s=0.220 * jitter_factor,
        horizon_s=horizon + warmup_s,
        collision_model=True,
        beacon_interval_s=BEACON_INTERVAL_S,
        station_down_after_s=None if station_state == "up" else 1.0,
        warmup_s=warmup_s,
    )
    _, graph = random_geometric_graph(cfg, seed)
    result = simulate(cfg, strategy, seed, graph=graph)

    return {
        "label": "SIM-UNCALIBRATED",
        "n_nodes": n_nodes,
        "n_sos": n_sos,
        "mobility": mobility,
        "station": station_state,
        "link_pdr_nominal": link_pdr,
        "link_pdr_effective": round(effective_pdr, 4),
        "strategy": strategy,
        "warmup_s": warmup_s,
        "seed": seed,
        "pdr": round(result.pdr, 6),
        "delivered_sources": result.delivered_sources,
        "latency_p50_s": _fmt(result.latency_p50),
        "latency_p95_s": _fmt(result.latency_p95),
        "latency_p99_s": _fmt(result.latency_p99),
        "transmissions": result.transmissions,
        "beacon_transmissions": result.beacon_transmissions,
        "receptions": result.receptions,
        "collisions": result.collisions,
        "tx_per_delivered_sos": _fmt(result.tx_per_delivered_sos),
        "copies_per_sos": round(result.copies_per_sos, 4),
        "jain_fairness": round(result.jain_fairness, 4),
        "max_queue_occupancy": result.max_queue_occupancy,
        "dropped_duplicate": result.dropped_duplicate,
        "dropped_ttl": result.dropped_ttl,
        "dropped_no_route": result.dropped_no_route,
        "dropped_queue_full": result.dropped_queue_full,
    }


def _fmt(value: float | None) -> str:
    if value is None or (isinstance(value, float) and math.isinf(value)):
        return ""
    return f"{value:.6f}"


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Tổng hợp theo ô (strategy × mật độ × tải × động × trạm × PDR).

    Đơn vị là seed, nên so sánh phải **ghép cặp theo seed** (Wilcoxon ở bước sau).
    """
    keys = ("n_nodes", "n_sos", "mobility", "station", "link_pdr_nominal",
            "strategy", "warmup_s")
    groups: dict[tuple, list[dict[str, object]]] = {}
    for row in rows:
        groups.setdefault(tuple(row[k] for k in keys), []).append(row)

    out: list[dict[str, object]] = []
    for key, items in sorted(groups.items(), key=lambda kv: tuple(map(str, kv[0]))):
        pdrs = [float(r["pdr"]) for r in items]
        lat = [float(r["latency_p95_s"]) for r in items if r["latency_p95_s"] != ""]
        tx = [float(r["tx_per_delivered_sos"]) for r in items if r["tx_per_delivered_sos"] != ""]
        out.append({
            "n_nodes": key[0],
            "n_sos": key[1],
            "mobility": key[2],
            "station": key[3],
            "link_pdr_nominal": key[4],
            "strategy": key[5],
            "warmup_s": key[6],
            "n_seeds": len(items),
            "pdr_mean": round(statistics.fmean(pdrs), 6),
            "pdr_sd": round(statistics.stdev(pdrs), 6) if len(pdrs) > 1 else 0.0,
            "pdr_min": round(min(pdrs), 6),
            "pdr_max": round(max(pdrs), 6),
            "latency_p95_mean": round(statistics.fmean(lat), 6) if lat else "",
            "tx_per_delivered_mean": round(statistics.fmean(tx), 6) if tx else "",
            "fairness_mean": round(statistics.fmean([float(r["jain_fairness"]) for r in items]), 4),
            "collisions_mean": round(statistics.fmean([float(r["collisions"]) for r in items]), 2),
            "beacon_tx_mean": round(statistics.fmean([float(r["beacon_transmissions"]) for r in items]), 2),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Ma trận thí nghiệm mesh WP3")
    ap.add_argument("--quick", action="store_true", help="ma trận rút gọn")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    if args.quick:
        densities, loads = DENSITIES_QUICK, LOADS_QUICK
        mobility, station, pdrs = MOBILITY_QUICK, STATION_QUICK, PDR_LEVELS_QUICK
        seeds, warmups = SEEDS_QUICK, WARMUP_QUICK
    else:
        densities, loads = DENSITIES_FULL, LOADS_FULL
        mobility, station, pdrs = MOBILITY_FULL, STATION_FULL, PDR_LEVELS_FULL
        seeds, warmups = SEEDS_FULL, WARMUP_FULL

    root = Path(__file__).resolve().parent.parent
    out_dir = Path(args.out_dir) if args.out_dir else root / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    total = (len(densities) * len(loads) * len(mobility) * len(station)
             * len(pdrs) * len(ALL_STRATEGIES) * seeds * len(warmups))
    done = 0
    for n_nodes in densities:
        for n_sos in loads:
            if n_sos >= n_nodes:
                continue  # không thể có nhiều nguồn hơn số nút
            for mob in mobility:
                for st in station:
                    for pdr in pdrs:
                        for warm in warmups:
                            for strategy in ALL_STRATEGIES:
                                for seed in range(seeds):
                                    rows.append(run_cell(n_nodes, n_sos, mob, st, pdr,
                                                         strategy, seed, warmup_s=warm))
                                    done += 1
                                    if done % 200 == 0:
                                        print(f"  {done}/{total} ô...", flush=True)

    raw_path = out_dir / "wp3-matrix-raw.csv"
    with raw_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = summarize(rows)
    sum_path = out_dir / "wp3-matrix-summary.csv"
    with sum_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    print(f"\n{len(rows)} dòng thô  -> {raw_path}")
    print(f"{len(summary)} ô tổng hợp -> {sum_path}")
    _print_headline(summary)
    return 0


def _print_headline(summary: list[dict[str, object]]) -> None:
    """In so sánh gradient vs flooding ở trạm ổn định, tĩnh."""
    print("\nH2 — gradient so với flooding (trạm ổn định, tĩnh):")
    print(f"{'n':>4} {'SOS':>4} {'PDR flood':>10} {'PDR grad':>10} "
          f"{'tx flood':>10} {'tx grad':>10} {'fair flood':>10} {'fair grad':>10}")

    idx = {(r["n_nodes"], r["n_sos"], r["strategy"]): r for r in summary
           if r["mobility"] == "static" and r["station"] == "up"}
    for n_nodes in sorted({r["n_nodes"] for r in summary}):
        for n_sos in sorted({r["n_sos"] for r in summary}):
            flood = idx.get((n_nodes, n_sos, "flood"))
            grad = idx.get((n_nodes, n_sos, "gradient"))
            if not flood or not grad:
                continue
            print(
                f"{n_nodes:>4} {n_sos:>4} "
                f"{flood['pdr_mean']:>10} {grad['pdr_mean']:>10} "
                f"{flood['tx_per_delivered_mean']!s:>10} {grad['tx_per_delivered_mean']!s:>10} "
                f"{flood['fairness_mean']:>10} {grad['fairness_mean']:>10}"
            )


if __name__ == "__main__":
    raise SystemExit(main())
