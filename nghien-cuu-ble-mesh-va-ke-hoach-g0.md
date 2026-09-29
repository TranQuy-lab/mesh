# Nghiên cứu BLE mesh trên điện thoại và kế hoạch G0

**Ngày:** 2026-09-29  
**Mục tiêu:** chuyển bằng chứng BLE trên smartphone thành quyết định thiết kế và
thí nghiệm có thể bác bỏ; không dùng kết quả trên board BLE để thay cho Android.

## 1. Bằng chứng trực tiếp

| Nguồn | Hệ thống/thiết kế | Kết quả dùng được | Giới hạn khi áp dụng |
|---|---|---|---|
| Siva, Yang & Poellabauer 2019, DOI `10.1016/j.procs.2019.08.011` | Android 7/BLE 4.2; quảng bá–quét không kết nối; 10 phút, lặp ≥5 | PDR phụ thuộc mạnh scan mode; Wi-Fi làm xấu latency/PDR; công suất thực lệch mô hình SoC | Android và phần cứng cũ; tác giả thừa nhận phép đo năng lượng có thể sai |
| Tsai et al. 2021, DOI `10.1109/ACCESS.2021.3129251` | Năm smartphone, legacy advertising, phát và quét đồng thời | Scan low-power duty 0,1 làm PLR 0,957–0,995; Bluetooth audio ở scanner xấu hơn ở advertiser; 250 ms được chọn để cân bằng pin/latency | Truyền thông điệp phân mảnh khác SOS 24 B; không phải multi-hop |
| Rathje & Landsiedel 2022, DOI `10.1109/LCN53696.2022.9843509` | Store-and-forward BLE/DTN; pedestrian scenario | Chứng minh kiến trúc opportunistic BLE khả thi; broadcast báo người đi bộ khoảng 7,1 s trong đánh giá của họ | Implementation mở hiện chỉ xác nhận trên nRF52/Zephyr, không phải Android |
| Rondón et al. 2020, DOI `10.1109/JIOT.2019.2960248` | Mô phỏng Bluetooth Mesh + trace WLAN | Timing scan/advertise tương tác mạnh; randomization giảm nhược điểm flooding; mạng dày dễ broadcast storm | Bluetooth Mesh chuẩn và mô phỏng, không phải API Android advertising-only của đề tài |
| De Leon & Nabi 2020, DOI `10.1109/WCNC45663.2020.9120762` | Testbed 33 nút trong văn phòng 500 m² | Relay giới hạn delivery khi tải tăng; phù hợp hơn với tải thấp/event-driven | Board BLE, không phải smartphone |
| Android `BluetoothLeScanner` | API Android chính thức | Unfiltered scan bị dừng khi màn hình tắt; phải dùng `ScanFilter` | Không bảo đảm mọi OEM có cùng PDR hoặc năng lượng |

Nguồn tổng quan 2026 (`10.1007/s12083-026-02295-7`) được dùng để tìm bài gốc,
không dùng thay cho phép đo. Nó cũng kết luận chưa có một mô hình connectionless
BLE chung cho mọi smartphone/SoC.

## 2. Quyết định thiết kế sau rà soát

1. Giữ legacy advertising 24 B làm đường chuẩn; extended advertising không phải
   điều kiện hoạt động.
2. Bắt buộc filtered scan. Foreground service không đủ để duy trì unfiltered scan
   khi màn hình tắt.
3. Không đóng băng một scan/advertise mode cho mọi điện thoại. So sánh 100 ms với
   250 ms và low-latency với balanced trên từng cặp model.
4. Đếm gói theo sequence duy nhất. Callback lặp của cùng gói không được tính là
   delivery độc lập.
5. Mô hình kênh phải tách ít nhất ba thành phần: radio/OS có đang nghe, xác suất
   thu vật lý, và collision/tải đồng kênh. Một `link_pdr` độc lập duy nhất chỉ còn
   là smoke model.
6. Đường cứu hộ là tải sự kiện thấp; không ngoại suy kết quả từ monitoring tải
   cao, nhưng vẫn phải stress-test nhiều SOS đồng thời vì broadcast storm.
7. Không tái sử dụng trực tiếp DisruptaBLE: code BSD-3-Clause có giá trị tham khảo
   cho store-carry-forward/spray-and-wait, nhưng adapter nRF52/Zephyr không giải
   quyết hạn chế nền của Android.

### Đối chiếu implementation DisruptaBLE

Đã kiểm tra repository tại commit
`4b42f48df316bd53fd27e6f13326cbcc4d2eda49` (2024-06-12):

- mỗi bundle được biểu diễn trong summary vector bằng hash 64 bit;
- hai phía trao đổi `offer`/`request` để chỉ gửi bundle bên kia chưa có;
- epidemic dùng số replica vô hạn; direct/spray-and-wait giới hạn số lần chuyển
  và hop rồi chờ gặp đích;
- bundle có lifetime, priority và được lưu cho đến contact sau.

Cơ chế này cần contact hai chiều và metadata summary vector, trong khi RescueMesh
v1 chỉ có quảng bá 24 B một chiều. Vì vậy chỉ đưa **limited-copy/spray-and-wait**
vào làm comparator ở mô phỏng mobility/store-carry-forward; không gọi nó là drop-in
replacement cho gradient hoặc Trickle tĩnh.

## 3. Screening G0-S — factorial 2⁴

### Câu hỏi

Trong điều kiện màn hình tắt và quét có filter, bốn yếu tố `advertise_mode`,
`scan_mode`, khoảng cách và tải Wi-Fi ảnh hưởng thế nào đến delivery theo message,
P95 latency và pin trên các cặp điện thoại?

### Thiết kế

- Bốn yếu tố hai mức: advertising 100/250 ms; scan low-latency/balanced;
  khoảng cách 1/5 m; Wi-Fi off/UDP active.
- Full factorial 16 điều kiện; ba replication cho mỗi cặp thiết bị.
- Block = cặp thiết bị × replication; cả 16 điều kiện xuất hiện một lần trong mỗi
  block, thứ tự random hóa với seed `20260929`.
- Ba cặp ban đầu tạo 144 phiên × 180 s. Đây là screening; cấu hình hứa hẹn mới
  được xác nhận bằng phiên 10 phút, ít nhất năm replication.
- Hai máy phát và quét đồng thời để ước lượng riêng A→B và B→A trong cùng phiên.
- Giữ vị trí, hướng máy và nguồn điện như nhau trong block; ghi nhiệt độ, phiên
  Android, Bluetooth audio và số thiết bị BLE/Wi-Fi quan sát được.

Lịch tái lập: `results/g0-screening-schedule.csv`. Sinh lại bằng:

```bash
python3 rescuemesh/generate_g0_schedule.py
```

### Chỉ số và đơn vị phân tích

| Chỉ số | Định nghĩa |
|---|---|
| Delivery theo message | số sequence ứng dụng duy nhất nhận / số sequence ứng dụng đã phát |
| Reception efficiency | callback hợp lệ / advertising event theo cấu hình; chỉ là proxy nếu không có HCI/sniffer xác nhận event thật |
| Discovery latency | từ lúc advertiser xác nhận start đến gói hợp lệ đầu tiên |
| P50/P95 inter-arrival | tính trong từng phiên rồi mới tổng hợp qua phiên |
| Nhiệt/pin | đổi nhiệt độ và mAh hoặc %/giờ sau baseline cùng thiết bị |
| Failure | không start, service chết, Bluetooth reset hoặc 0 gói cả phiên |

Packet không phải replication. Phân tích chính dùng phiên đo; mô hình sau này có
fixed effects cho bốn yếu tố và tương tác được đăng ký trước, random intercept cho
cặp thiết bị/session. Báo effect size và CI, không chỉ p-value.

Đầu dò hiện đã phát sequence ứng dụng thay đổi mỗi giây, tạo HMAC bằng codec Java
đối chiếu với Python và ghi `messages_issued`. Pixel xác nhận rotation tiếp tục từ
10 lên 40 message trong khi màn hình tắt. Còn phải xác nhận receiver thứ hai đếm
đúng `unique_messages`. Nếu chưa có sniffer/HCI log, không gọi
`callbacks / events lý thuyết` là PDR tuyệt đối.

### Kiểm soát

- Positive control: màn hình sáng + filter + 1 m + Wi-Fi off phải nhận golden SOS.
- Negative control: manufacturer ID sai phải có 0 golden match.
- Android behavior control: unfiltered scan màn hình tắt được ghi một lần/model,
  không lặp như một treatment vì API đã quy định nó sẽ dừng.
- Phiên có cuộc gọi, cập nhật hệ thống hoặc thermal throttling bị gắn cờ; không âm
  thầm xóa mà chạy lại theo quy tắc đã định.

## 4. Cổng quyết định

- Một model được hỗ trợ chỉ khi mọi hướng của cặp xác nhận đều start được, nhận
  payload đúng và foreground service sống hết phiên màn hình tắt.
- Chưa chọn cấu hình mặc định trước khi có ít nhất hai model Android khác hãng.
- Chỉ đưa PDR/latency đo được vào simulator sau khi giữ riêng train/calibration
  runs và validation runs; báo sai số dự đoán ngoài mẫu.
- Spray-and-wait chỉ so sánh trong kịch bản mobility/contact; flood/Trickle/gradient
  vẫn là comparator của mạng đồng thời nhiều hop.
- Nếu balanced scan không đạt ngưỡng latency cứu hộ, ưu tiên quét theo chu kỳ thích
  ứng hoặc low-latency trong cửa sổ SOS; không giữ low-latency vĩnh viễn theo quán tính.

## 5. Nguồn

- https://doi.org/10.1016/j.procs.2019.08.011
- https://doi.org/10.1109/ACCESS.2021.3129251
- https://doi.org/10.1109/LCN53696.2022.9843509
- https://doi.org/10.1109/JIOT.2019.2960248
- https://doi.org/10.1109/WCNC45663.2020.9120762
- https://developer.android.com/reference/android/bluetooth/le/BluetoothLeScanner
- https://github.com/prathje/DisruptaBLE
- https://doi.org/10.1007/s12083-026-02295-7
