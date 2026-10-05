# H7 — phát hiện "chìm / bị cuốn" bằng barometer + IMU (2026-10-05)

**Chỉnh quyết định 2026-10-05 (người thực hiện):** H7 **đưa vào đề tài làm cảm biến luôn**
(không còn là "tuỳ chọn có điều kiện, bỏ được như cũ"). Mốc kiểm chứng hạ xuống mức
**demo trên một máy tham chiếu có barometer** — đề tài là dự án nhỏ chứng minh làm được,
không phải công bố. Khung trung thực (nhãn `TK`/`ĐO`) giữ nguyên: hằng số detector vẫn là
`TK` cho tới khi `ĐO` trong bồn nước.

## Nguyên lý (một câu)

Máy chìm xuống nước thì **áp suất tăng ~1 hPa mỗi 1 cm nước** (vật lý thủy tĩnh
9,8 kPa/m — `SUY` chắc), và người bị cuốn thì **IMU lộn xộn**, không phải dáng đi
tuần hoàn. Hai tín hiệu cùng lúc mới báo.

## Đã có trong kho

| File | Là gì |
|---|---|
| `research/h7/h7_detector.py` | Máy trạng thái NORMAL → SUSPECT → ALARM (dòng, 1 Hz barometer + IMU 20 Hz tổng hợp/giây); chỉ phụ thuộc numpy — chuyển Kotlin dễ |
| `research/h7/test_h7_detector.py` | 8 kịch bản — **8/8 đạt 2026-10-05**: chìm chậm/nhanh → báo; đi bộ, ngã đất khô, thang máy, mưa trong túi, lội nước trên mực → không báo |

Hằng số thiết kế (`TK`, chờ `ĐO`): tăng ≥2 hPa/s + churn gyro ≥80 °/s ⇒ nghi ngờ;
cộng dồn ≥+15 hPa (≈15 cm dưới nước) trong ≥3 s ⇒ báo động; thoát khi áp suất về
mốc gốc; cooldown 30 s.

## Máy tham chiếu: Pixel 6

**Pixel 6 (thường) CÓ barometer** — GSMArena, mở trang spec, HTTP 200, 2026-10-05:
"Fingerprint, accelerometer, gyro, proximity, compass, **barometer**". (Kế hoạch cũ chỉ
ghi "Pixel 6 Pro có" — cả hai đều có.) Không cần mua gì.

## Quy trình demo (bồn/tub, làm 1 buổi)

1. Máy Pixel 6 bọc **túi chống nước** ép khí hết, buộc dây (an toàn: điện thoại, không phải người).
2. Cài logger (thêm chế độ "H7 log" vào `android-g0/`: ghi CSV `t, áp suất hPa, |a| g, gyro °/s` 1 Hz).
3. **`ĐO` đáp ứng tĩnh:** hạ từng bước 10 → 20 → 30 → 50 cm dưới mặt nước, giữ 10 s/bước.
   Kiểm: Δp ghi được ≈ +10/+20/+30/+49 hPa (0,981 hPa/cm) — nếu đúng thì barometer phản ánh độ sâu.
4. **`ĐO` chữ ký động:** thả chìm nhanh (~30–50 cm/s), khuấy nước cho máy lộn.
5. Chạy logger qua `h7_detector.py` (offline trước, rồi Kotlin): chìm phải ALARM;
   các bước rửa máy dưới vòi (ngắn), để máy cạnh bồn (không chìm), mang đi bộ — không báo.
6. Ghi kết quả vào chính tài liệu này (bảng `TK` → `ĐO`), cập nhật hằng số nếu lệch.

## Biên trung thực

- Demo này **không** chứng minh phát hiện người chìm ngoài thực địa — chỉ chứng minh
  **cảm biến + chữ ký hoạt động trên máy thật** (đúng phạm vi "chứng minh làm được").
- Barometer điện thoại có drift nhiệt/độ cao — trong nhà ngang tầng là ổn; khi lũ theo
  xe/thang máy phải lọc thêm (test thang máy đã có trong unit test).
- Đối thủ cạnh (bài "người trôi trong lũ qua điện thoại") vẫn **không tồn tại** — khoảng
  trống giữ nguyên, nhưng ở chế độ demo ta không tuyên bố beyond "làm được".
