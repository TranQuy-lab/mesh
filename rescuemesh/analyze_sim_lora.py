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


def main() -> None:
    rows = load_raw()
    paired = paired_differences(rows)
    summarise(paired)
    write_paired(paired)


if __name__ == "__main__":
    main()
