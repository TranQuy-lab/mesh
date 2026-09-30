"""Phân tích độ bền của kết luận định tuyến theo các GIẢ ĐỊNH của mô hình.

Đối thủ mạnh nhất còn lại của kế hoạch là **R2b**: *"lợi thế/bất lợi của gradient chỉ
là sản phẩm của mô hình mất gói thuận lợi nhân tạo"*. Cách trả lời đúng không phải
tranh luận, mà là **quét các giả định và xem dấu của kết luận có đổi không**.

Script quét:
- `path_loss_exponent` (2,5 → 4,0) — mô hình suy hao;
- `margin_slope_db` (3 → 12 dB) — độ dốc logistic biến biên thành PDR;
- `margin_50_db` (−6 → +6 dB) — điểm giữa của logistic;
- `duty_cycle` (1 % → 10 %) — ngân sách phát;
- `beacon_interval_s` (30 → 900 s) — chu kỳ điều khiển;
- `capture_enabled` (bật/tắt) — capture effect.

Với mỗi cấu hình, chạy **flood** và **gradient** trên cùng seed rồi báo
ΔPDR = gradient − flood. Nếu dấu ΔPDR lật trong phạm vi giả định hợp lý thì kết luận
**không bền** và phải nói rõ trong báo cáo.

Chạy::

    cd rescuemesh && python3 run_lora_sensitivity.py

Ghi `../results/sim-lora-sensitivity.csv` (nhãn `SIM`) và in bảng ra stdout.
"""

from __future__ import annotations

import csv
import statistics
from pathlib import Path

from sim_lora import LoraSimConfig, simulate_once

RESULTS = Path(__file__).resolve().parents[1] / "results"
SEEDS = range(10)
BASE = dict(n_nodes=100, n_sos=20, sf=9, warm_start=True, area_m=1000.0)


def scenarios() -> list[dict]:
    """Các cấu hình quét, mỗi cấu hình là một dict tham số ghi đè `BASE`."""
    out: list[dict] = [{"label": "baseline (n=4, slope 6, mid 0, duty 1 %, beacon 60 s)"}]
    for n in (2.5, 3.0, 3.5, 4.0):
        out.append({"label": f"n={n}", "path_loss_exponent": n})
    for slope in (3.0, 6.0, 12.0):
        out.append({"label": f"slope={slope} dB", "margin_slope_db": slope})
    for mid in (-6.0, 0.0, 6.0):
        out.append({"label": f"margin_50={mid:+.0f} dB", "margin_50_db": mid})
    for duty in (0.01, 0.10):
        out.append({"label": f"duty={duty:.0%}", "duty_cycle": duty})
    for bi in (30.0, 60.0, 900.0):
        out.append({"label": f"beacon={bi:.0f}s", "beacon_interval_s": bi})
    out.append({"label": "capture tắt", "capture_enabled": False})
    out.append({"label": "link PDR cố định 0,8", "link_pdr": 0.8})
    out.append({"label": "không beacon", "beacon_interval_s": None})
    return out


def run_scenario(params: dict) -> dict:
    """Chạy flood và gradient trên cùng seed cho một cấu hình."""
    cfg_kwargs = dict(BASE)
    kwargs = {k: v for k, v in params.items() if k != "label"}
    cfg_kwargs.update(kwargs)
    dpdr, dpdr_cold = [], []
    for seed in SEEDS:
        warm = {**cfg_kwargs, "warm_start": True}
        cold = {**cfg_kwargs, "warm_start": False}
        flood = simulate_once(LoraSimConfig(**warm), "flood", seed=seed)
        grad = simulate_once(LoraSimConfig(**warm), "gradient", seed=seed)
        dpdr.append(grad.pdr - flood.pdr)
        f_cold = simulate_once(LoraSimConfig(**cold), "flood", seed=seed)
        g_cold = simulate_once(LoraSimConfig(**cold), "gradient", seed=seed)
        dpdr_cold.append(g_cold.pdr - f_cold.pdr)
    return {
        "label": params["label"],
        "dpdr_warm": statistics.fmean(dpdr),
        "dpdr_warm_sd": statistics.pstdev(dpdr) if len(dpdr) > 1 else 0.0,
        "dpdr_cold": statistics.fmean(dpdr_cold),
        "sign_warm": "gradient thắng" if statistics.fmean(dpdr) > 0 else "flood thắng",
        "evidence": "SIM",
    }


def main() -> int:
    rows = [run_scenario(s) for s in scenarios()]
    out = RESULTS / "sim-lora-sensitivity.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("=" * 100)
    print("ĐỘ BỀN CỦA H2 THEO GIẢ ĐỊNH (nhãn SIM, CHƯA hiệu chuẩn)")
    print("ΔPDR = gradient − flood; dương = gradient thắng. 100 nút, 20 SOS, SF9, 1 km, 10 seed.")
    print("=" * 100)
    print(f"{'cấu hình':>42} | {'ΔPDR warm':>10} | {'±SD':>6} | {'ΔPDR cold':>10} | dấu")
    print("-" * 100)
    for r in rows:
        print(f"{r['label']:>42} | {r['dpdr_warm']:+10.3f} | {r['dpdr_warm_sd']:6.3f} "
              f"| {r['dpdr_cold']:+10.3f} | {r['sign_warm']}")
    signs = {r["sign_warm"] for r in rows}
    print()
    if len(signs) > 1:
        print("KẾT LUẬN: dấu của ΔPDR **LẬT** trong phạm vi giả định hợp lý ⇒ kết luận")
        print("định tuyến KHÔNG BỀN với giả định mô hình. Phải báo cáo là `SIM` phụ")
        print("thuộc giả định và không được dùng để chốt thiết kế trước khi hiệu chuẩn (G9).")
    else:
        print("KẾT LUẬN: dấu của ΔPDR giữ nguyên trên mọi cấu hình đã quét ⇒ kết luận")
        print("bền với các giả định này (vẫn còn R2b ở dạng cần hiệu chuẩn thực địa).")
    print(f"\nĐã ghi {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
