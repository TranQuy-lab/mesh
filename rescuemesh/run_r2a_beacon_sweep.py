"""Quét beacon interval — kiểm chứng đối thủ R2a của H2.

R2a nói: "khác biệt giữa gradient và flooding chỉ do beacon overhead bị tính
sai". Kết quả WP3 ban đầu cho thấy beacon chiếm tới ~80 % tổng lưu lượng ở
interval 2 s, nên mối lo này là **có cơ sở thật**, không phải hình thức.

Đặc tả §4.4 nói beacon 30 s khi rỗi và 5 s khi hàng ACK không rỗng. Thí nghiệm
này quét interval từ 1 s tới 30 s để xem kết luận H2 có đảo hay không.

**Câu hỏi kiểm chứng:** lợi thế của gradient so với flooding có tồn tại ở
interval thực tế (30 s), hay nó chỉ là sản phẩm của việc beacon phát quá dày
trong mô phỏng?

Mọi kết quả mang nhãn ``SIM`` chưa hiệu chuẩn.
"""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

from sim_v2 import SimConfig, random_geometric_graph, simulate

AREA_M = 400.0
RANGE_BY_DENSITY = {50: 95.0, 100: 70.0, 200: 52.0}
DENSITIES = (50, 100, 200)
LOADS = (5, 20)
# 1 s và 2 s = mô phỏng dày; 5 s = chính sách khi hàng ACK bận;
# 30 s = chính sách rỗi theo §4.4.
BEACON_INTERVALS = (1.0, 2.0, 5.0, 30.0)
STRATEGIES = ("flood", "gradient")
SEEDS = 30
WARMUP_S = 10.0
HORIZON_S = 90.0


def run_cell(n_nodes: int, n_sos: int, beacon_interval_s: float,
             strategy: str, seed: int) -> dict[str, object]:
    cfg = SimConfig(
        n_nodes=n_nodes,
        n_sos=n_sos,
        link_pdr=0.95,
        area_m=AREA_M,
        range_m=RANGE_BY_DENSITY[n_nodes],
        horizon_s=HORIZON_S,
        collision_model=True,
        beacon_interval_s=beacon_interval_s,
        route_expiry_beacons=3,
        warmup_s=WARMUP_S,
    )
    _, graph = random_geometric_graph(cfg, seed)
    r = simulate(cfg, strategy, seed, graph=graph)

    data_share = (r.transmissions - r.beacon_transmissions) / r.transmissions if r.transmissions else 0.0
    return {
        "label": "SIM-UNCALIBRATED",
        "n_nodes": n_nodes,
        "n_sos": n_sos,
        "beacon_interval_s": beacon_interval_s,
        "strategy": strategy,
        "seed": seed,
        "pdr": round(r.pdr, 6),
        "transmissions": r.transmissions,
        "beacon_transmissions": r.beacon_transmissions,
        "data_transmissions": r.transmissions - r.beacon_transmissions,
        "beacon_share": round(1.0 - data_share, 4),
        "tx_per_delivered_sos": _fmt(r.tx_per_delivered_sos),
        "jain_fairness": round(r.jain_fairness, 4),
    }


def _fmt(v: float | None) -> str:
    import math
    if v is None or (isinstance(v, float) and math.isinf(v)):
        return ""
    return f"{v:.4f}"


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    keys = ("n_nodes", "n_sos", "beacon_interval_s", "strategy")
    groups: dict[tuple, list[dict[str, object]]] = {}
    for row in rows:
        groups.setdefault(tuple(row[k] for k in keys), []).append(row)

    out: list[dict[str, object]] = []
    for key, items in sorted(groups.items(), key=lambda kv: tuple(map(str, kv[0]))):
        tx = [float(r["tx_per_delivered_sos"]) for r in items if r["tx_per_delivered_sos"] != ""]
        out.append({
            "n_nodes": key[0],
            "n_sos": key[1],
            "beacon_interval_s": key[2],
            "strategy": key[3],
            "n_seeds": len(items),
            "pdr_mean": round(statistics.fmean([float(r["pdr"]) for r in items]), 6),
            "beacon_share_mean": round(
                statistics.fmean([float(r["beacon_share"]) for r in items]), 4),
            "tx_per_delivered_mean": round(statistics.fmean(tx), 4) if tx else "",
            "fairness_mean": round(
                statistics.fmean([float(r["jain_fairness"]) for r in items]), 4),
        })
    return out


def paired_advantage(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    """So ghép cặp gradient vs flood trong cùng ô, theo từng beacon interval."""
    idx = {(r["n_nodes"], r["n_sos"], r["beacon_interval_s"], r["strategy"]): r
           for r in summary}
    out: list[dict[str, object]] = []
    for n_nodes in DENSITIES:
        for n_sos in LOADS:
            for interval in BEACON_INTERVALS:
                f = idx.get((n_nodes, n_sos, interval, "flood"))
                g = idx.get((n_nodes, n_sos, interval, "gradient"))
                if not (f and g):
                    continue
                d_pdr = float(g["pdr_mean"]) - float(f["pdr_mean"])
                f_tx, g_tx = f["tx_per_delivered_mean"], g["tx_per_delivered_mean"]
                d_tx = (float(g_tx) - float(f_tx)) if (f_tx != "" and g_tx != "") else None
                out.append({
                    "n_nodes": n_nodes,
                    "n_sos": n_sos,
                    "beacon_interval_s": interval,
                    "pdr_flood": f["pdr_mean"],
                    "pdr_gradient": g["pdr_mean"],
                    "pdr_gain": round(d_pdr, 6),
                    "tx_flood": f_tx,
                    "tx_gradient": g_tx,
                    "tx_saving": "" if d_tx is None else round(-d_tx, 4),
                    "beacon_share_flood": f["beacon_share_mean"],
                    "beacon_share_gradient": g["beacon_share_mean"],
                })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Quét beacon interval cho R2a")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    seeds = 3 if args.quick else SEEDS
    densities = (50,) if args.quick else DENSITIES

    root = Path(__file__).resolve().parent.parent
    out_dir = Path(args.out_dir) if args.out_dir else root / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    for n_nodes in densities:
        for n_sos in LOADS:
            for interval in BEACON_INTERVALS:
                for strategy in STRATEGIES:
                    for seed in range(seeds):
                        rows.append(run_cell(n_nodes, n_sos, interval, strategy, seed))
        print(f"  xong n={n_nodes}", flush=True)

    raw = out_dir / "r2a-beacon-sweep-raw.csv"
    with raw.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    summary = summarize(rows)
    s_path = out_dir / "r2a-beacon-sweep-summary.csv"
    with s_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)

    adv = paired_advantage(summary)
    a_path = out_dir / "r2a-beacon-sweep-advantage.csv"
    with a_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(adv[0]))
        w.writeheader()
        w.writerows(adv)

    print(f"\n{len(rows)} dòng thô -> {raw}")
    print(f"lợi thế ghép cặp  -> {a_path}")

    print("\nR2a — lợi thế của gradient có sống sót khi beacon thưa dần?")
    print(f"{'n':>4}{'SOS':>5}{'interval':>10}{'PDR flood':>11}{'PDR grad':>10}"
          f"{'ΔPDR':>9}{'Δtx tiết kiệm':>15}{'beacon%':>9}")
    for row in adv:
        print(f"{row['n_nodes']:>4}{row['n_sos']:>5}{row['beacon_interval_s']:>10}"
              f"{row['pdr_flood']:>11}{row['pdr_gradient']:>10}{row['pdr_gain']:>9}"
              f"{row['tx_saving']!s:>15}{row['beacon_share_gradient']:>9}")

    if adv:
        gains = [float(r["pdr_gain"]) for r in adv]
        at_30 = [float(r["pdr_gain"]) for r in adv if r["beacon_interval_s"] == 30.0]
        print(f"\nΔPDR trung bình mọi interval: {statistics.fmean(gains):+.4f}")
        if at_30:
            print(f"ΔPDR trung bình ở interval 30 s (chính sách rỗi §4.4): "
                  f"{statistics.fmean(at_30):+.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
