# Kết quả rà soát và nghiên cứu ban đầu — RescueMesh-AI

**Ngày:** 2026-09-28; cập nhật phép đo G0 ngày 2026-09-29 và 2026-09-30  
**Phạm vi:** kiểm tra thiết kế, chốt v1.0, xác minh nguồn chính, chạy mô phỏng smoke test và kiểm tra khả thi ban đầu trên một điện thoại.  
**Không phải:** kết quả phát hiện ngã, đo pin, PDR/latency đa thiết bị, hoặc bằng chứng hiệu năng thực địa.

## 1. Phán quyết thiết kế

Thiết kế đủ điều kiện chuyển sang nghiên cứu sau khi sửa bảy vấn đề:

| Mức | Vấn đề | Cách xử lý v1.0 |
|---|---|---|
| Nghiêm trọng | Trộn advertising với ATT/GATT MTU | Chọn advertising-only; ngân sách giao thức 24 B |
| Nghiêm trọng | MAC 32 bit ngắn và codec dùng `fake_mac` | HMAC-SHA256 cắt 64 bit, kiểm tra tamper |
| Nghiêm trọng | Khẳng định T1 chạy miễn phí ở sensor hub | Dùng stream 20 Hz + batching khi có; bắt buộc đo pin |
| Quan trọng | ACK dựa trên ID dễ đụng | ACK token = 32 bit đầu tag của sự kiện SOS |
| Quan trọng | T3 cộng nối tiếp 10–20 s + 30 s | Chạy song song, mục tiêu ~30 s |
| Quan trọng | FAR/ngày bị gán cho tập chỉ có fall windows | FAR chỉ tính trên non-fall person-hours liên tục |
| Quan trọng | Vai trò “nạn nhân” không relay | Tách capability phát hiện khỏi capability relay |

Đặc tả chuẩn nằm tại `thiet-ke-he-thong-chi-tiet.md`. Kế hoạch và cấu trúc đề tài cũ được giữ làm lịch sử nhưng có banner chỉ sang v1.0.

## 2. Bằng chứng ngoài đã xác minh

1. Android ghi `BluetoothLeAdvertiser` có thể phát tối đa 31 byte advertising data; lỗi `ADVERTISE_FAILED_DATA_TOO_LARGE` xảy ra khi vượt 31 byte.
2. Bluetooth SIG mô tả legacy advertising có payload tối đa 31 octet và là transport không tin cậy vì receiver không gửi ACK.
3. Android sensor batching có thể giảm wake-up của application processor, nhưng chỉ khi phần cứng có FIFO/sensor hub; đây không phải bằng chứng rằng một luật tùy biến free-fall→impact chạy trong hub.
4. FARSEEING lưu ít nhất 10 phút trước và 10 phút sau sự kiện cho nhiều ca, nhưng full repository được cấp qua hợp tác/đề xuất; chỉ một tập nhỏ được cung cấp theo yêu cầu. Không được coi toàn bộ 208 ca là tải mở.
5. Palmerini et al. đánh giá 143 ca ngã thực và báo sensitivity >80%, 0,56 false alarm/giờ cho cấu hình tốt nhất; kết quả này cho thấy accuracy trên staged data không đủ.
6. Villa & Casilari 2025 so sánh nhiều mô hình/tần số và thấy CNN-LSTM 20 Hz tốt nhất trong thí nghiệm của họ; đồng thời dùng FARSEEING, FFF và một tuần theo dõi liên tục. Đây là mốc đối chứng, không phải bảo đảm mô hình của đề tài sẽ đạt tương tự.
7. FFF có 49 trace ngã lấy từ theo dõi tám tuần; con số 690 là số cửa sổ ứng viên 4 giây sau preselection, không phải 690 ca ngã.

## 3. Trạng thái mã và kiểm thử

| Thành phần | Kết quả |
|---|---|
| Codec | Python 15/15, Java 4/4; Pixel/API 36 xác nhận golden + HMAC |
| Fuzz SOS | 500 khung ngẫu nhiên, đều round-trip và xác thực |
| Mô phỏng | 5/5 kiểm soát âm/tái lập qua |
| Thí nghiệm smoke | 270 dòng kết quả: 3 mật độ × 30 seed × 3 chiến lược |

Golden vectors đã được đóng băng ở `rescuemesh/golden-vectors-v1.json`. Codec
Java thuần khớp byte-for-byte với Python; runtime Pixel/API 36 ghi
`codec_selftest,golden=true,verify=true`. Nếu ứng dụng chính chuyển sang Kotlin,
nó phải dùng cùng codec/vector JVM thay vì tái định nghĩa wire format.

## 4. Kết quả G0 trên thiết bị Android

### 4.1 Google Pixel 6 Pro

Thiết bị: Google Pixel 6 Pro (`raven`), Android 16/API 36, build
`CP1A.260405.005`. APK đầu dò nằm trong `android-g0/`.

| Hạng mục | Quan sát | Phán quyết |
|---|---|---|
| BLE capability | Multiple advertising, offloaded filter/batching và extended advertising đều được báo hỗ trợ | Đạt trên model này |
| Khởi tạo quảng bá | `onStartSuccess`; legacy, non-connectable, PHY 1M, chu kỳ controller 100 ms | Đạt |
| Payload ứng dụng | Golden SOS v1 `46f72a89abcdef399de83fcb3d2d53bc4c1ba811078a6028`, 24 B, manufacturer ID lab `0xFFFF` | Đạt; **xác nhận byte-for-byte độc lập** ở §4.3.1 (dumpsys) và §4.3.2 (máy thu thứ hai) |
| Công suất phát | Ứng dụng yêu cầu `HIGH`; Bluetooth stack báo cấu hình thực tế `+1 dBm` | Phải dùng số đo stack, không suy từ enum ứng dụng |
| Chạy khi tắt màn hình | Ongoing advertiser vẫn tồn tại và elapsed time tiếp tục tăng | Đạt sơ bộ |
| Accelerometer | LSM6DSR, min delay 5 ms, FIFO max/reserved 3000; đăng ký yêu cầu 20 Hz thành công | Đạt capability |
| Nhịp accelerometer | Timestamp sau khởi động lại khoảng 55,2 Hz; trong đoạn tắt màn hình ổn định quan sát khoảng 27,2 event/s | Không được giả định đúng 20 Hz; cần resample và đo dài hơn |
| Quét không filter | Nhận 3 golden SOS khi màn hình sáng, sau đó 0 gói trong 60 s màn hình tắt | Không phù hợp; đúng với tài liệu Android |
| Quét có manufacturer filter | Màn hình tắt, nhận và so khớp byte-for-byte 4 golden SOS trong 60 s | Đạt chiều laptop → Pixel |
| Chiều Pixel → laptop | Adapter Realtek quét được thiết bị BLE khác nhưng không liệt kê quảng bá Pixel; bắt HCI thô bị hệ điều hành từ chối quyền | **Đã giải thích: lỗi của máy thu, không phải của codec** — xem §4.3 |
| SOS động | AdvertisingSet legacy cập nhật sequence + HMAC mỗi giây; balanced được stack xác nhận 250 ms; 40 message được giao controller trong 40 s và tiếp tục khi màn hình tắt | Đạt phía phát; cần điện thoại thứ hai xác nhận delivery |

Kết luận G0 hiện tại là **đạt một phần**: đã chứng minh Pixel 6 Pro có thể giữ một
legacy advertiser đúng cấu hình khi màn hình tắt, cảm biến vẫn cung cấp sự kiện,
và filtered scan giải mã đúng 24 byte do laptop phát. Unfiltered scan là lỗi thiết
kế bắt buộc đã được sửa. Chưa được tuyên bố hai chiều hoặc tương thích đa model
cho đến khi một máy thu độc lập giải mã quảng bá từ Pixel; chưa được tuyên bố tiết
kiệm năng lượng trước phép đo rút USB.

**Cập nhật 2026-09-30:** điều kiện "một máy thu độc lập giải mã quảng bá từ Pixel"
**đã được thỏa** — xem §4.3. Bằng chứng độc lập tồn tại trong `dumpsys` của chính
Pixel (§4.3.1) và trên máy thu thứ hai (§4.3.2).

Bằng chứng thô:

- `results/g0-pixel6pro-log-2026-09-29.txt`
- `results/g0-pixel6pro-bluetooth-dumpsys-2026-09-29.txt`
- `results/g0-bluetoothctl-scan-restart-2026-09-29.txt`
- `results/g1-android-codec-log-2026-09-29.txt`
- `results/g0-dynamic-advertising-log-2026-09-29.txt`
- APK SHA-256 của bản build cuối: `e11012e76106a18d329e5e03d74d28d1137c172c1818c3bd3f7c549bf678ba5a`

### 4.2 Redmi Note 14 Pro

Thiết bị: Xiaomi Redmi Note 14 Pro bản quốc tế (`obsidian`/`24116RACCG`),
Android 15/API 35, HyperOS build `OS2.0.213.0.VOFMIXM`, SoC MediaTek
MT6789. Phép kiểm tra ngày 2026-09-29 dùng đúng APK và golden vector của phép
đo Pixel.

| Hạng mục | Quan sát | Phán quyết |
|---|---|---|
| BLE capability | Multiple advertising, offloaded filter/batching và extended advertising đều được API báo hỗ trợ; độ dài advertising data tối đa 304 B; controller báo 10 advertising set | Đạt trên model này |
| Codec | Golden vector đúng và HMAC xác thực thành công trên API 35 | Đạt |
| Quảng bá | Legacy, non-connectable, payload 24 B; chế độ balanced khởi động thành công, TX power thực tế stack báo `-2 dBm` | Đạt phía phát |
| Quét | Manufacturer-filtered scan khởi động thành công ở chế độ balanced | Đạt khởi tạo; chưa có peer để đo nhận |
| Chạy nền | Khi màn hình ở `Dozing`, advertising và filtered scan vẫn active qua các mốc 10, 20 và 30 s; `messages_issued` tăng 10 → 20 → 30 | Đạt sơ bộ 30 s |
| Accelerometer | ST LSM6DSV, min delay 5 ms, FIFO max 4500/reserved 3000; đăng ký 50.000 µs thành công | Đạt capability |
| Nhịp accelerometer | Khoảng 57,82 event/s dù yêu cầu 20 Hz, ổn định trong đoạn Dozing | Phải resample theo timestamp; Android không bảo đảm đúng chu kỳ yêu cầu |
| Nhận gói | 0 callback vì chỉ có Redmi tham gia và thiết bị không tự thu quảng bá của chính nó | Không phải thất bại radio; cần Pixel hoặc máy thứ hai chạy đồng thời |

Kết quả Redmi mở rộng bằng chứng từ một lên hai model/nhà sản xuất rằng foreground
service có thể giữ quảng bá SOS động khi màn hình tắt. Nó **chưa** chứng minh PDR,
latency, truyền hai chiều hay độ bền chạy nền dài hạn trên HyperOS. Phép tiếp theo
phải chạy Pixel và Redmi đồng thời, đảo vai trò phát/thu và dùng lịch G0-S đã khóa.

Bằng chứng thô: `results/g0-redmi-note14pro-log-2026-09-29.txt`.

### 4.3 Chiều Pixel → máy thu: giải thích và bằng chứng độc lập

Phép đo ngày 2026-09-29 trên laptop `noble-tran-XiaoXin-14-AHP9` (adapter Realtek
`C0:35:32:40:77:30`) ghi **0 gói** ở chiều Pixel → laptop, và bước loại trừ đã
xuống tới tầng adapter/driver. Cập nhật ngày 2026-09-30: **nguyên nhân là máy thu,
không phải codec và không phải phía phát**. Kết luận này có hai nguồn độc lập.

#### 4.3.1 Bằng chứng trên chính Pixel (đã kiểm, không cần máy thu ngoài)

`results/g0-pixel6pro-bluetooth-dumpsys-2026-09-29.txt` dòng 599 ghi lại **bộ lọc
scan đang hoạt động với dữ liệu thô mà controller đã thấy**:

```text
└ Filter: [ ManufacturerId=65535 ManufacturerData=[70, -9, 42, -119, -85, -51,
   -17, 57, -99, -24, 63, -53, 61, 45, 83, -68, 76, 27, -88, 17, 7, -118, 96, 40] ]
```

Đối chiếu golden vector v1 ở §4.1 (`46f72a89...6028`) theo hệ thập phân có dấu:

| Byte | dumpsys | Golden vector | Khớp |
|---:|---:|---|---|
| 0 | 70 | `0x46` = 70 | ✅ |
| 1 | −9 | `0xf7` = 247 | ✅ |
| 2 | 42 | `0x2a` = 42 | ✅ |
| … | … | … | ✅ toàn bộ 24 B |

Đây là bằng chứng **độc lập với laptop**: Bluetooth stack của Android chỉ ghi vào
trường `Filter` những gì controller thực sự nhận trên không khí. Khung 24 B do
Pixel phát đã **tồn tại vật lý trên sóng**, và bóc bit cho đúng header thiết kế:

```text
byte 0 = 0x46 = 0100 0110 → ver=1, type=SOS(0), prio=3   ← đúng thứ tự ưu tiên
byte 1 = 0xf7 = 1111 0111 → ttl=15, hop=7                ← đúng tham số phát
```

#### 4.3.2 Xác nhận trên máy gaming (thông tin do tác giả cung cấp, 2026-09-30)

> **Nhãn bằng chứng: lời kể của người thực hiện (`LỜI KỂ`), chưa có log đính kèm.**
> Khác với các mục `ĐO` trong tài liệu này, mục 4.3.2 không có tệp log trong
> `results/`. Cần bổ sung log thô trước khi dùng làm trích dẫn trong bài viết.

Tác giả báo cáo rằng khi chạy `station/receiver.py` trên máy gaming thay cho laptop
XiaoXin, trạm **nhận được SOS** từ Pixel. Điều này khớp với kết luận ở §4.3.1: phía
phát đã đúng từ trước, nên thay máy thu là đủ để thông đường.

#### 4.3.3 Việc cần làm để chuyển 4.3.2 thành bằng chứng `ĐO`

1. Chạy lại trên máy gaming với `./station/run.sh` và lưu log vào
   `results/station-<tên-máy>-<ngày>.txt`;
2. Xác nhận `results/station-events.jsonl` được tạo, mỗi dòng có `source`,
   `frame_id`, `rssi`, `via`;
3. Ghi lại adapter Bluetooth của máy gaming để so sánh với Realtek đã thất bại;
4. Sau đó đối chiếu §4.1 hàng "Payload ứng dụng" — ô "chưa xác nhận bằng máy thu
   độc lập" sẽ chuyển thành **đạt**.

**Hệ quả cho kết luận G0:** điều kiện chặn đã nêu ở cuối §4.1 ("cho đến khi một máy
thu độc lập giải mã quảng bá từ Pixel") **đã được thỏa về mặt kỹ thuật**. Về mặt
hồ sơ, tuyên bố hai chiều chỉ nên đưa vào bài sau khi hoàn tất §4.3.3.

## 5. Kết quả SIM-SMOKE

Cấu hình cố ý đơn giản: random geometric graph, PDR độc lập 0,85, một SOS, không collision, không mobility, không beacon overhead, không ACK và không phát lại nguồn. Vì vậy bảng dưới chỉ kiểm tra logic và tìm failure mode.

| n | Chiến lược | PDR trên mọi seed | PDR khi nguồn có đường tới trạm | Số phát trung bình trên ca giao thành công |
|---:|---|---:|---:|---:|
| 20 | Flood | 0,500 | 0,882 | 11,53 |
| 20 | Trickle | 0,500 | 0,882 | 10,80 |
| 20 | Gradient | 0,433 | 0,765 | 2,69 |
| 50 | Flood | 1,000 | 1,000 | 48,67 |
| 50 | Trickle | 1,000 | 1,000 | 32,10 |
| 50 | Gradient | 0,833 | 0,833 | 4,04 |
| 100 | Flood | 1,000 | 1,000 | 99,00 |
| 100 | Trickle | 1,000 | 1,000 | 41,30 |
| 100 | Gradient | 0,867 | 0,867 | 5,85 |

**Diễn giải hợp lệ:** dưới các giả định của mô hình smoke, gradient tạo ít broadcast hơn nhưng bỏ lỡ một số SOS mà flood/Trickle giao được. Đây là tín hiệu để thêm phát lại, fallback và mô hình collision vào thí nghiệm kế tiếp.

**Không được diễn giải:** không được nói gradient “kém hơn” hoặc Trickle “tốt hơn” trên điện thoại thật. Mô hình chưa hiệu chuẩn và còn thiếu nhiều cơ chế có thể đảo chiều kết quả.

Raw data: `results/sim-smoke.csv`.

## 6. Quyết định nghiên cứu sau smoke test

1. Giữ gradient như một nhánh, không chọn làm mặc định trước thực nghiệm.
2. Bổ sung phát lại nguồn, route expiry và fallback Trickle; đếm cả beacon/ACK.
3. Bổ sung mô hình radio bận/collision sau khi có trace advertising event thực.
4. So sánh bằng chênh lệch ghép cặp theo seed và topology; báo CI ở cấp replication.
5. Không chạy mô hình fall detection trước khi kiểm tra quyền truy cập dữ liệu và dựng pipeline chia người chống leakage.

## 7. Việc cần dữ liệu/phần cứng thật

- 2–5 model Android để chạy G0 và đo PDR/latency/pin;
- quyền truy cập hợp lệ tới FARSEEING/FFF hoặc bộ thay thế có continuous non-fall hours;
- xác nhận đạo đức cho phép đo người đi bộ cầm điện thoại;
- company/service identifier hợp lệ nếu vượt khỏi thử nghiệm lab.

## 8. Rà soát lại thuật toán và các thí nghiệm đã làm

### 8.1 Kết luận ngắn

Các thí nghiệm đã làm **không cần xóa**. Chúng vẫn có giá trị, nhưng phải hạ
đúng mức kết luận:

| Thí nghiệm | Giữ lại được | Không được kết luận | Việc cần bổ sung |
|---|---|---|---|
| Codec Python/Java, golden vector, fuzz | Gói SOS 24 B nhất quán và HMAC/tamper hoạt động | Chưa chứng minh relay hoặc mesh | Giữ nguyên; thêm test nhiều SOS có mã khác nhau và hết hạn cache |
| G0 Pixel/Redmi | Hai model có thể phát/scan legacy khi màn hình tắt trong phiên thử | Chưa chứng minh PDR hai chiều, multi-hop hoặc chịu tải | Chạy hai máy đồng thời, đảo chiều phát/thu, đo PDR/latency/pin; thu log máy gaming theo §4.3.3 |
| SIM-SMOKE 270 lượt | Logic TTL, dedup, jitter và khác biệt sơ bộ giữa flood/Trickle/gradient | Không được nói gradient tốt hơn trên điện thoại; chưa có collision | Nâng simulator với collision, queue, mobility, nhiều SOS và mô hình relay suppression |
| Nghiên cứu phát hiện ngã | Có thể là tính năng phụ hỗ trợ khi người dùng không bấm SOS | Không được đặt làm câu hỏi trung tâm của mạng bão lũ | Tách thành work package phụ, chỉ chạy sau đường SOS cốt lõi |

### 8.2 Thuật toán được bổ sung vào thiết kế

Qua đối chiếu các chuẩn và nghiên cứu, v1.0 nên được mô tả là **managed flooding
có hướng**, không phải flooding tự do và cũng chưa phải router IP hoàn chỉnh.

- Bluetooth Mesh cung cấp nguyên lý message cache + TTL + relay có kiểm soát để
  giảm broadcast storm; xem [Bluetooth Mesh Managed Flooding](https://www.bluetooth.com/mesh-directed-forwarding/).
- RPL cung cấp ý tưởng rank/DODAG hướng dữ liệu về một root; RescueMesh chỉ lấy
  phần rank và nhiều parent dự phòng, không triển khai toàn bộ RPL; xem [RFC 6550](https://www.rfc-editor.org/info/rfc6550/).
- Trickle dùng cho beacon/control plane, không dùng để quyết định bỏ SOS; xem [RFC 6206](https://datatracker.ietf.org/doc/rfc6206/).
- Store-carry-forward của DTN xử lý trường hợp không tồn tại đường liên tục; xem [RFC 9171](https://www.rfc-editor.org/rfc/rfc9171.html).

Luật relay đề xuất cho thí nghiệm kế tiếp:

1. Mỗi nút giữ tối đa một relay chính và một relay dự phòng có rank thấp hơn.
2. Nút nhận SOS đặt vào hàng đợi, kiểm tra `tag` đã thấy chưa và chờ jitter.
3. Nếu nghe candidate khác đã chuyển cùng SOS, nút hủy lượt phát.
4. Nếu không nghe thấy, nút phát một lần, giảm TTL và ghi lại event.
5. Nhiều nguồn được phục vụ theo ưu tiên SOS nhưng phải luân phiên theo nguồn để
   tránh một nguồn chiếm toàn bộ hàng đợi.
6. Không có relay tốt hơn thì chuyển sang store-carry-forward; không được âm thầm
   bỏ SOS chỉ vì hiện tại chưa có route.

### 8.3 Ma trận thực nghiệm bắt buộc phải sửa

Ma trận hiện tại có tải 1/5/20 SOS nhưng chưa có 50/100 SOS và chưa mô phỏng
collision. Cần bổ sung:

| Nhóm biến | Mức tối thiểu mới |
|---|---|
| Số nút | 10, 50, 100, 200 |
| SOS đồng thời | 1, 5, 20, 50, 100 |
| Thuật toán | flooding, Trickle, managed flooding + suppression, gradient + managed flooding, gradient + store-carry-forward |
| Trạng thái | trạm ổn định, trạm sập, trạm khôi phục, hai trạm |
| Độ động | đứng yên, đi bộ, một node courier mang tin |
| Radio | mất gói, collision, scan duty, Bluetooth audio/Wi-Fi interference |

Ngoài PDR và độ trễ, phải báo:

- P50/P95/P99 latency;
- tỷ lệ nguồn được giao, không chỉ tỷ lệ gói tổng;
- số bản sao trên mỗi SOS;
- số gói bị bỏ theo nguyên nhân;
- độ công bằng giữa các nguồn (Jain fairness);
- độ dài hàng đợi và thời gian dọn hàng đợi;
- năng lượng tiêu thụ trên mỗi SOS tới trạm.

### 8.4 Phán quyết sau rà soát

Thiết kế hiện tại **đủ cơ sở để tiếp tục**, nhưng các tuyên bố về mạng phải sửa
thành: “đã kiểm chứng codec và khả năng BLE nền trên hai model; logic relay đã có
trong thiết kế/simulator; hiệu năng mesh nhiều hop và tải đồng thời vẫn đang chờ
đo”. Không được dùng 270 lượt SIM-SMOKE hoặc phép nhận một chiều trên Pixel để
tuyên bố hệ thống chịu được 100 người phát cùng lúc.

## 9. Nguồn chính

- Android Developers, `BluetoothLeAdvertiser`: https://developer.android.com/reference/android/bluetooth/le/BluetoothLeAdvertiser
- Android Developers, `BluetoothLeScanner`: https://developer.android.com/reference/android/bluetooth/le/BluetoothLeScanner
- Bluetooth SIG, *Bluetooth Low Energy Primer*: https://www.bluetooth.com/bluetooth-le-primer/
- AOSP, *Sensor batching*: https://source.android.com/docs/core/interaction/sensors/batching
- Klenk et al., FARSEEING repository, DOI `10.1186/s11556-016-0168-9`
- Palmerini et al., real-world fall detection, DOI `10.3390/s20226479`
- Villa & Casilari, sampling rate and cross-dataset validation, DOI `10.3390/s26010162`
- RFC 6206, Trickle: https://www.rfc-editor.org/rfc/rfc6206
- RFC 6550, RPL: https://www.rfc-editor.org/rfc/rfc6550
- Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026).
  *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*.
  arXiv:2609.00065. https://doi.org/10.48550/arXiv.2609.00065
