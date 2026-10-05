# RQ1 — Đường ống huấn luyện phát hiện ngã (SisFall, LOSO + FAR budget)

**Trạng thái:** sẵn sàng đẩy lên Kaggle, chờ token API. Chạy local cũng được.

## Cấu trúc

| File | Vai trò |
|---|---|
| `train_fall_loso.py` | Kernel/script chính: nạp SisFall → cửa sổ 2 s @ 20 Hz → GRU nhỏ → **LOSO 38 người** → chọn ngưỡng đóng băng theo FAR → `metrics_loso.json` |
| `check_scale.py` | Kiểm hệ số cảm biến thực nghiệm (ADXL345 **256 LSB/g** — đã xác minh: trọng lực ≈1,03 g, đỉnh ngã F04 ≈4–7 g) |
| `kernel-metadata.json` | Metadata `kaggle kernels push` — **thay `THE-USERNAME` bằng username Kaggle của bạn** |
| `dataset-metadata.json` | Metadata để tạo dataset Kaggle từ mirror (nếu không tìm thấy mirror có sẵn bằng `kaggle datasets list -s sisfall`) |
| `fall-detect-loso-far.py` | Bản sao của `train_fall_loso.py` để push — **chạy lại `cp` sau khi sửa script chính** |

## Dữ liệu

- Nguồn đã dùng được ngay: mirror GitHub **`Fall-Prevention-Team/sisfallData`** — đã clone tại
  `../fall_dataset_sisfall/` (SA01–SA23 + SE01–SE15, 4.506 file, 931 MB). Site gốc SisFall
  (sistemic.udea.edu.co) đã chết (HTTP 000 từ 2026-10-01).
- Đầu tiên thử `kaggle datasets list -s sisfall` (khi đã có token) — nếu có mirror Kaggle thì
  dùng slug đó thay vì upload; nếu không thì bước 2 dưới đây.

## Ba bước khi có token Kaggle (kaggle.json → ~/.kaggle/)

```bash
# 0) thay THE-USERNAME trong kernel-metadata.json + dataset-metadata.json
cd research/fall_model
# 1) tạo dataset (upload mirror; chỉ cần làm 1 lần, ~10 phút)
kaggle datasets create -p ../fall_dataset_sisfall -r zip --dir-mode zip
# 2) đẩy kernel (chạy LOSO 38 người, CPU, ~1–2 giờ)
cp train_fall_loso.py fall-detect-loso-far.py
kaggle kernels push -p .
# 3) xem tiến độ / tải kết quả
kaggle kernels status THE-USERNAME/fall-detect-loso-far
kaggle kernels output THE-USERNAME/fall-detect-loso-far -p out_kaggle
```

## Chạy local (không cần Kaggle)

```bash
# smoke test 2 người × 2 epoch (~vài phút, cần tensorflow-cpu)
python3 train_fall_loso.py --data ../fall_dataset_sisfall --folds 2 --epochs 2
```

## Chạy thật trên máy (Pixel 6 — RQ1 phần "ĐO")

Khi kernel cho model `.h5`: chuyển sang TFLite, cài vào `android-g0/` (IMU 20 Hz,
cửa sổ 2 s), drill: ngã diễn tập + 24 h sinh hoạt → đối chiếu FAR đo được với
KPI §8 (≤1 báo động giả/ngày/người).

## Chuẩn đánh giá (móc vào kế hoạch §2/§6)

- **LOSO bắt buộc** — baseline 96–99 % trích lan man đều là chia theo cửa sổ, không so sánh được.
- **Ngưỡng đóng băng:** chọn trên tập train của từng fold để đạt FAR mục tiêu, áp nguyên lên người test.
- **FAR → ngày:** 172 800 cửa sổ/ngày (20 Hz, stride 0,5 s). Báo cáo recall tại ≤1 FA/ngày (KPI §8) và ≤9 FA/ngày (Kangas 2012).
- Cửa sổ ngã = ±1 s quanh đỉnh va đập; phần đứng/ngồi trước ngã trong file ngã tính là không-ngã (không thổi phồng recall).
