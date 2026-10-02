"""Thí nghiệm H3 — "bóng ma đường" sau khi trạm sập và hồi phục.

H3 nói: sau khi trạm ngừng phát beacon, các nút **vẫn giữ hop cũ** và chuyển
tiếp theo tuyến đã chết; cần hết hạn tuyến để hội tụ lại. Đối thủ R3a nói mất
mát chủ yếu do mất gói, không do định tuyến cũ.

**Vì sao lần thiết kế đầu sai.** Cách đặt vấn đề ban đầu là so PDR giữa "trạm
sập + route expiry bật" và "trạm sập + route expiry tắt". Kết quả cho PDR = 0 ở
**cả hai** nhánh, vì trạm sập thì không gói nào tới đích bất kể tuyến còn hay
mất. Phép đo đó không phân biệt được gì — bản thân nó là một kết quả: H3
**không thể đo bằng PDR trong lúc trạm sập**.

**Cách đo đúng: cho trạm hồi phục.** Sau khi beacon trở lại, mạng phải học lại
tuyến. Nút giữ hop cũ sẽ chuyển tiếp theo hướng đã sai và từ chối relay vì
tưởng `my_hop` vẫn thấp. Chỉ số chính là **số SOS tới trạm trong cửa sổ ngay
sau khi trạm hồi phục** (khả năng phục vụ sớm), không phải PDR toàn phiên.

Bốn nhánh, cùng seed và topology:

===== ====================== ==================
Nhánh  Trạm                   Route expiry
===== ====================== ==================
A      luôn hoạt động         bật   (đường cơ sở)
B      luôn hoạt động         tắt   (đối chứng)
C      sập rồi hồi phục       bật   (thiết kế)
D      sập rồi hồi phục       tắt   (bóng ma)
===== ====================== ==================

``D − C`` là hiệu ứng bóng ma đường thuần: cùng beacon, cùng lịch hồi phục,
chỉ khác việc nút có quên tuyến cũ hay không.

Mọi kết quả mang nhãn ``SIM``: mô hình chưa hiệu chuẩn (cổng G3 chưa qua).
"""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

from sim_v2 import SimConfig, random_geometric_graph, simulate

AREA_M = 400.0
RANGE_BY_DENSITY = {20: 140.0, 50: 95.0, 100: 70.0, 200: 52.0}
DENSITIES = (50, 100, 200)
LOADS = (5, 20, 50)
BEACON_INTERVAL_S = 2.0
SEEDS = 30

# Lịch sự kiện (giây):
#   0–12          gradient hội tụ (beacon chạy)
#   12            trạm sập (ngừng phát beacon, ngừng nhận)
#   35            tuyến cũ đã hết hạn ở nhánh bật (3 × 2 s = 6 s kể từ t=12)
#   60            trạm hồi phục
#   70            SOS phát — SAU khi trạm hồi phục, để đo khả năng phục vụ sớm
STATION_DOWN_AFTER_S = 12.0
SOS_EMIT_AT_S = 70.0
STATION_RECOVER_AFTER_S = 60.0
HORIZON_S = 150.0


def run_branch(
    n_nodes: int,
    n_sos: int,
    station_fails: bool,
    expiry_on: bool,
    seed: int,
) -> dict[str, object]:
    cfg = SimConfig(
        n_nodes=n_nodes,
        n_sos=n_sos,
        link_pdr=0.95,
        area_m=AREA_M,
        range_m=RANGE_BY_DENSITY[n_nodes],
        horizon_s=HORIZON_S,
        collision_model=True,
        beacon_interval_s=BEACON_INTERVAL_S,
        route_expiry_beacons=3,
        route_expiry_enabled=expiry_on,
        station_down_after_s=STATION_DOWN_AFTER_S if station_fails else None,
        station_recover_after_s=STATION_RECOVER_AFTER_S if station_fails else None,
        warmup_s=SOS_EMIT_AT_S,
        measure_after_s=STATION_RECOVER_AFTER_S,
    )
    _, graph = random_geometric_graph(cfg, seed)
    result = simulate(cfg, "gradient", seed, graph=graph)

    return {
        "label": "SIM-UNCALIBRATED",
        "n_nodes": n_nodes,
        "n_sos": n_sos,
        "station": "fails_then_recovers" if station_fails else "always_up",
        "route_expiry": "on" if expiry_on else "off",
        "branch": _branch_name(station_fails, expiry_on),
        "seed": seed,
        "pdr": round(result.pdr, 6),
        "delivered_sources": result.delivered_sources,
        "delivered_after_recovery": result.delivered_after_recovery,
        "latency_p50_s": _fmt(result.latency_p50),
        "latency_p95_s": _fmt(result.latency_p95),
        "transmissions": result.transmissions,
        "beacon_transmissions": result.beacon_transmissions,
        "dropped_no_route": result.dropped_no_route,
        "dropped_duplicate": result.dropped_duplicate,
        "dropped_ttl": result.dropped_ttl,
        "collisions": result.collisions,
        "copies_per_sos": round(result.copies_per_sos, 4),
    }


def _branch_name(station_fails: bool, expiry_on: bool) -> str:
    if not station_fails and expiry_on:
        return "A_always_up_expiry_on"
    if not station_fails and not expiry_on:
        return "B_always_up_expiry_off"
    if station_fails and expiry_on:
        return "C_recovers_expiry_on"
    return "D_recovers_expiry_off"


def _fmt(value: float | None) -> str:
    return "" if value is None else f"{value:.6f}"


def summarize(rows: list[dict[str, object]], densities: tuple[int, ...] = DENSITIES) -> list[dict[str, object]]:
    keys = ("n_nodes", "branch")
    groups: dict[tuple, list[dict[str, object]]] = {}
    for row in rows:
        groups.setdefault(tuple(row[k] for k in keys), []).append(row)

    out: list[dict[str, object]] = []
    for key, items in sorted(groups.items(), key=lambda kv: (int(kv[0][0]), str(kv[0][1]))):
        out.append({
            "n_nodes": key[0],
            "branch": key[1],
            "n_seeds": len(items),
            "delivered_after_recovery_mean": round(
                statistics.fmean([float(r["delivered_after_recovery"]) for r in items]), 3),
            "delivered_after_recovery_sd": round(
                statistics.stdev([float(r["delivered_after_recovery"]) for r in items]), 3)
            if len(items) > 1 else 0.0,
            "pdr_mean": round(statistics.fmean([float(r["pdr"]) for r in items]), 6),
            "no_route_mean": round(
                statistics.fmean([float(r["dropped_no_route"]) for r in items]), 2),
        })
    return out


def ghost_effect(summary: list[dict[str, object]],
                 densities: tuple[int, ...] = DENSITIES) -> list[dict[str, object]]:
    """Tính ``D − C``: hiệu ứng bóng ma đường thuần theo từng mật độ."""
    idx = {(r["n_nodes"], r["branch"]): r for r in summary}
    out: list[dict[str, object]] = []
    for n_nodes in densities:
        a = idx.get((n_nodes, "A_always_up_expiry_on"))
        b = idx.get((n_nodes, "B_always_up_expiry_off"))
        c = idx.get((n_nodes, "C_recovers_expiry_on"))
        d = idx.get((n_nodes, "D_recovers_expiry_off"))
        if not (c and d):
            continue
        out.append({
            "n_nodes": n_nodes,
            "recover_C_expiry_on": c["delivered_after_recovery_mean"],
            "recover_D_expiry_off": d["delivered_after_recovery_mean"],
            "ghost_effect": round(
                float(c["delivered_after_recovery_mean"])
                - float(d["delivered_after_recovery_mean"]), 3),
            "no_route_C": c["no_route_mean"],
            "no_route_D": d["no_route_mean"],
            "baseline_A": a["delivered_after_recovery_mean"] if a else "",
            "baseline_B": b["delivered_after_recovery_mean"] if b else "",
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Thí nghiệm H3 bốn nhánh")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--quick", action="store_true", help="ít seed để kiểm tra")
    args = ap.parse_args()

    seeds = 3 if args.quick else SEEDS
    densities = (50, 100) if args.quick else DENSITIES

    root = Path(__file__).resolve().parent.parent
    out_dir = Path(args.out_dir) if args.out_dir else root / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    total = len(densities) * len(LOADS) * 4 * seeds
    done = 0
    for n_nodes in densities:
        for n_sos in LOADS:
            if n_sos >= n_nodes:
                continue  # không thể có nhiều nguồn hơn số nút
            for station_fails in (False, True):
                for expiry_on in (True, False):
                    for seed in range(seeds):
                        rows.append(run_branch(n_nodes, n_sos, station_fails, expiry_on, seed))
                        done += 1
                        if done % 60 == 0:
                            print(f"  {done}/{total}...", flush=True)

    raw = out_dir / "h3-ghost-raw.csv"
    with raw.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    summary = summarize(rows, densities)
    s_path = out_dir / "h3-ghost-summary.csv"
    with s_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)

    ghost = ghost_effect(summary, densities)
    g_path = out_dir / "h3-ghost-effect.csv"
    with g_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ghost[0]))
        w.writeheader()
        w.writerows(ghost)

    print(f"\n{len(rows)} dòng thô   -> {raw}")
    print(f"{len(summary)} ô tổng hợp -> {s_path}")
    print(f"{len(ghost)} ô hiệu ứng -> {g_path}")

    print("\nH3 — số SOS tới trạm SAU khi hồi phục (chỉ số chính):")
    print(f"{'n':>4}{'A: up+exp':>12}{'B: up+noexp':>13}"
          f"{'C: recov+exp':>14}{'D: recov+noexp':>16}{'C−D':>8}")
    for row in ghost:
        print(f"{row['n_nodes']:>4}{row['baseline_A']:>12}{row['baseline_B']:>13}"
              f"{row['recover_C_expiry_on']:>14}{row['recover_D_expiry_off']:>16}"
              f"{row['ghost_effect']:>8}")

    print("\nDiễn giải: C−D > 0 nghĩa là hết hạn tuyến GIÚP ích (H3 được xác nhận).")
    print("           C−D ≈ 0 nghĩa là tuyến cũ không gây hại (đối thủ R3a thắng).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
