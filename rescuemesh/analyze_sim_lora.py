"""Phân tích ghép cặp cho kết quả simulator LoRa (`SIM`, chưa hiệu chuẩn).

Mục đích: trả lời câu hỏi H2 của kế hoạch — **gradient thắng flooding ở mức tải
nào** — bằng so sánh ghép cặp theo seed, thay vì so trung bình gộp.

Đầu vào:  ../results/sim-lora-raw.csv
Đầu ra:   ../results/sim-lora-h2-paired.csv  (mỗi dòng = một ô, đã ghép cặp)
          bảng in ra stdout

QUAN TRỌNG: mọi con số ở đây là `SIM` từ mô hình **chưa hiệu chuẩn**. Không được
dùng để kết luận hiệu năng thực; cổng G9 của kế hoạch phải đạt trước.
"""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path

RESULTS = Path(__file__).resolve().parents[1] / "results"
RAW = RESULTS / "sim-lora-raw.csv"
OUT = RESULTS / "sim-lora-h2-paired.csv"

BASELINE = "flood"
RIVALS = ("managed_flood", "gradient", "trickle", "store_carry_forward")

CELL_KEYS = ("n_nodes", "n_sos", "sf", "start_mode")


def load_raw() -> dict[tuple, dict]:
    """Đọc raw CSV, đánh khoá theo (strategy, ô thí nghiệm, seed)."""
    rows: dict[tuple, dict] = {}
    with RAW.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("evidence") != "SIM":
                raise SystemExit("CSV thiếu nhãn evidence=SIM — dừng để tránh lẫn nhãn")
            key = (
                row["strategy"],
                *(row[k] for k in CELL_KEYS),
                int(row["seed"]),
            )
            rows[key] = {
                "pdr": float(row["pdr"]),
                "tx_per_delivered": float(row["transmissions_per_delivered"]),
                "control_ratio": float(row["control_airtime_ratio"]),
                "collisions": float(row["collisions"]),
            }
    return rows


def paired_differences(rows: dict[tuple, dict]) -> list[dict]:
    """Ghép cặp từng seed giữa baseline và từng đối thủ."""
    out: list[dict] = []
    for rival in RIVALS:
        for n_nodes in ("25", "50", "100"):
            for n_sos in ("5", "20"):
                for sf in ("7", "9"):
                    for mode in ("cold", "warm"):
                        cell = (n_nodes, n_sos, sf, mode)
                        dpdr, dtx, dctl, dcol, n = [], [], [], [], 0
                        for seed in range(20):
                            a = rows.get((BASELINE, *cell, seed))
                            b = rows.get((rival, *cell, seed))
                            if a is None or b is None:
                                continue
                            n += 1
                            dpdr.append(b["pdr"] - a["pdr"])
                            dtx.append(b["tx_per_delivered"] - a["tx_per_delivered"])
                            dctl.append(b["control_ratio"] - a["control_ratio"])
                            dcol.append(b["collisions"] - a["collisions"])
                        if not n:
                            continue
                        out.append(
                            {
                                "rival": rival,
                                "n_nodes": n_nodes,
                                "n_sos": n_sos,
                                "sf": sf,
                                "start_mode": mode,
                                "n_pairs": n,
                                "mean_dpdr": statistics.fmean(dpdr),
                                "sd_dpdr": statistics.stdev(dpdr) if n > 1 else 0.0,
                                "pdr_wins": sum(1 for d in dpdr if d > 0),
                                "pdr_losses": sum(1 for d in dpdr if d < 0),
                                "mean_dtx": statistics.fmean(dtx),
                                "mean_dcontrol_ratio": statistics.fmean(dctl),
                                "mean_dcollisions": statistics.fmean(dcol),
                            }
                        )
    return out


def summarise(paired: list[dict]) -> None:
    print("=" * 100)
    print("H2 — GHÉP CẶP THEO SEED, đối thủ so với flooding (nhãn SIM, CHƯA HIỆU CHUẨN)")
    print("=" * 100)
    header = (
        f"{'đối thủ':>20} | {'tải':>4} | {'ô':>4} | {'thắng':>6} | {'thua':>5} | "
        f"{'ΔPDR':>8} | {'Δphát/giao':>11} | {'Δđiều khiển':>11}"
    )
    print(header)
    print("-" * len(header))
    for rival in RIVALS:
        for n_sos in ("5", "20"):
            sel = [p for p in paired if p["rival"] == rival and p["n_sos"] == n_sos]
            if not sel:
                continue
            wins = sum(p["pdr_wins"] for p in sel)
            losses = sum(p["pdr_losses"] for p in sel)
            total_pairs = sum(p["n_pairs"] for p in sel)
            dpdr = statistics.fmean(p["mean_dpdr"] for p in sel)
            dtx = statistics.fmean(p["mean_dtx"] for p in sel)
            dctl = statistics.fmean(p["mean_dcontrol_ratio"] for p in sel)
            print(
                f"{rival:>20} | {n_sos:>4} | {len(sel):>4} | {wins:>6} | {losses:>5} | "
                f"{dpdr:>+8.3f} | {dtx:>+11.2f} | {dctl:>+10.1%}"
            )
    print()
    print("Diễn giải: 'thắng/thua' đếm theo từng cặp seed (cùng ô). ΔPDR dương nghĩa")
    print("là đối thủ giao nhiều hơn flooding. Δphát/giao dương nghĩa là tốn hơn.")
    print("Không được trích các số này như kết quả: mô hình chưa hiệu chuẩn (cổng G9).")


def write_paired(paired: list[dict]) -> None:
    fields = list(paired[0].keys())
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in paired:
            writer.writerow(row)
    print(f"\nĐã ghi {OUT} ({len(paired)} dòng, mọi dòng suy ra từ dữ liệu evidence=SIM)")


def pareto_summary(rows: dict[tuple, dict]) -> None:
    """Đường Pareto PDR ↔ số lần phát mỗi SOS giao được (từ ma trận chính).

    Không có "người thắng duy nhất": trên LoRa, thuật toán giao nhiều hơn thường
    tốn nhiều airtime hơn. Hàm này in từng thuật toán kèm dấu `*` cho những thuật
    toán **không bị trội** (không có thuật toán nào vừa giao ≥ vừa rẻ hơn).
    """
    agg: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for (strategy, *_rest, _seed), vals in rows.items():
        agg[strategy].append((vals["pdr"], vals["tx_per_delivered"]))
    stats = {
        s: (statistics.fmean(p for p, _ in v), statistics.fmean(t for _, t in v))
        for s, v in agg.items()
    }
    print()
    print("=" * 92)
    print("ĐƯỜNG PARETO — PDR vs số lần phát mỗi SOS giao được (nhãn SIM, CHƯA hiệu chuẩn)")
    print("=" * 92)
    print(f"{'thuật toán':>20} | {'PDR':>7} | {'phát/giao':>10} | {'trên biên Pareto':>17}")
    print("-" * 92)
    for s, (pdr, tx) in sorted(stats.items(), key=lambda kv: -kv[1][0]):
        dominated = any(
            (p2 >= pdr and t2 <= tx and (p2 > pdr or t2 < tx))
            for o, (p2, t2) in stats.items() if o != s
        )
        print(f"{s:>20} | {pdr:7.3f} | {tx:10.2f} | {'KHÔNG' if dominated else 'CÓ *':>17}")
    print()
    print("Đọc bảng: đây là đánh đổi, không phải xếp hạng. Mọi số là `SIM` chưa hiệu")
    print("chuẩn; cổng G9 phải đạt trước khi dùng để kết luận.")


def per_cell_and_sf_table(rows: dict[tuple, dict]) -> None:
    """Bảng theo ô (mật độ × tải × SF × khởi động) và tổng hợp theo SF.

    Đây là chỗ **sửa lại H2**: biến quyết định không phải tải mà là **airtime mỗi
    khung** (tức SF). Ở SF7 (airtime ngắn) flooding thắng ở mọi ô; ở SF9 (airtime
    dài gấp ~3,5 lần) gradient ngang bằng hoặc nhỉnh hơn.
    """
    agg: dict[tuple, list[float]] = defaultdict(list)
    for (strategy, n_nodes, n_sos, sf, mode, _seed), vals in rows.items():
        agg[(strategy, n_nodes, n_sos, sf, mode)].append(vals["pdr"])
    print()
    print("=" * 92)
    print("H2 SỬA LẠI — PDR theo ô: flood vs gradient (nhãn SIM, CHƯA hiệu chuẩn)")
    print("=" * 92)
    header = (f"{'n':>4} {'tải':>4} {'SF':>3} {'start':>5} | {'flood':>7} "
              f"{'gradient':>9} {'ΔPDR':>8}")
    print(header)
    print("-" * len(header))
    by_sf: dict[str, list[float]] = defaultdict(list)
    for n_nodes in ("25", "50", "100"):
        for n_sos in ("5", "20"):
            for sf in ("7", "9"):
                for mode in ("warm", "cold"):
                    f_key = ("flood", n_nodes, n_sos, sf, mode)
                    g_key = ("gradient", n_nodes, n_sos, sf, mode)
                    if f_key not in agg or g_key not in agg:
                        continue
                    f = statistics.fmean(agg[f_key])
                    g = statistics.fmean(agg[g_key])
                    by_sf[sf].append(g - f)
                    print(f"{n_nodes:>4} {n_sos:>4} {sf:>3} {mode:>5} | {f:7.3f} "
                          f"{g:9.3f} {g - f:+8.3f}")
    print()
    print("Tổng hợp theo SF (ΔPDR = gradient − flood, trung bình mọi ô cùng SF):")
    for sf in sorted(by_sf):
        deltas = by_sf[sf]
        wins = sum(1 for d in deltas if d > 0)
        print(f"  SF{sf}: ΔPDR = {statistics.fmean(deltas):+.3f} | "
              f"gradient thắng {wins}/{len(deltas)} ô")
    print()
    print("Kết luận SIM (chưa hiệu chuẩn): biến quyết định là AIRTIME MỖI KHUNG, không")
    print("phải tải SOS. Muốn phát biểu H2 phải nêu rõ SF/BW.")


def main() -> None:
    rows = load_raw()
    paired = paired_differences(rows)
    summarise(paired)
    write_paired(paired)
    pareto_summary(rows)
    per_cell_and_sf_table(rows)


if __name__ == "__main__":
    main()
