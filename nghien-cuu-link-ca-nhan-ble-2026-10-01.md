# Khảo sát link cá nhân BLE (điện thoại Android ↔ nút cầu đeo) cho RescueMesh-LoRa — RQ6

**Phạm vi:** chặng BLE cự ly 1–2 m giữa điện thoại Android (phát hiện ngã → gửi khung SOS ~36 byte) và nút cầu LoRa đeo kèm. Từ nút cầu trở đi là mesh LoRa 920–923 MHz (không thuộc tài liệu này).
**Ngày truy cập toàn bộ nguồn:** 2026-10-01.
**Quy ước loại nguồn:** `TIÊU CHUẨN` (Bluetooth SIG / USB-IF) · `NỀN TẢNG CHÍNH THỨC` (developer.android.com, source.android.com) · `MÃ NGUỒN` (AOSP / Linux kernel) · `BÀI BÌNH DUYỆT` (có DOI, kiểm chứng qua Crossref) · `ĐO ĐỘC LẬP` (bên thứ ba tự đo, không bình duyệt) · `BLOG/ tiếp thị`.
**Quy ước mức số liệu:** `FIELD-MEASURED` (đo thực tế, có thiết bị) · `SIM/ANALYTIC` (mô phỏng/giải tích) · `SPEC` (giá trị quy định trong tiêu chuẩn) · `SOURCE-CODE` (hằng số trong mã nguồn, có thể bị OEM/ROM ghi đè) · `VENDOR-CLAIMED`.

---

## A. Bảng tham số BLE và ảnh hưởng độ trễ (kèm nguồn)

### A.1 Tham số tầng Link Layer / ATT

| Tham số | Giá trị (SPEC) | Nguồn | Ảnh hưởng tới độ trễ chặng BLE |
|---|---|---|---|
| `connInterval` (connection interval) | bội số 1,25 ms, **7,5 ms → 4,0 s** | Bluetooth Core Spec 6.0, Vol 6 Part B §4.5.1 — https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-60/out/en/low-energy-controller/link-layer-specification.html (2026-10-01, `TIÊU CHUẨN`, SPEC) | Trần cứng của độ trễ chờ gói: gói gửi ngay sau một connection event phải chờ tới anchor point kế tiếp → trễ một chiều tối thiểu ≈ `connInterval` (nếu bỏ lỡ event) |
| `connPeripheralLatency` (slave latency) | số nguyên; ràng buộc `connSubrateFactor × (latency+1) ≤ 500` và `connInterval × subrate × (latency+1) < ½ connSupervisionTimeout` | Core Spec 6.0 Vol 6 Part B §4.5.1 (nt) (`TIÊU CHUẨN`) | Latency **cộng thẳng** vào worst-case: bỏ qua `latency` event ⇒ trễ tăng theo bội số connection interval |
| `connSupervisionTimeout` | bội số 10 ms, **100 ms → 32,0 s**, và phải `> 2 × (1+latency) × subrate × connInterval` | Core Spec 6.0 Vol 6 Part B §4.5.2 (nt) (`TIÊU CHUẨN`) | Quyết định thời gian phát hiện mất link (fail-over sang LoRa/retry). Timeout dài ⇒ phát hiện đứt chậm |
| `connSubrateFactor` / continuation | 1…500 (Connection Subrating, BT 5.3+) | Core Spec 6.0 Vol 6 Part B §4.5.1 (nt) (`TIÊU CHUẨN`) | Giảm số event ⇒ tiết kiệm pin nhưng tăng trễ giống slave latency |
| Kích thước payload LL (DLE) | Payload Data PDU **≤ 251 octet**, Length field 0–255 | Core Spec 6.0 Vol 6 Part B §2.4 (nt) (`TIÊU CHUẨN`) | Khung SOS 36 byte nằm gọn trong **1 PDU**; không cần phân mảnh ⇒ không phát sinh trễ do nhiều event |
| `ATT_MTU` mặc định (LE) | **23 octet** (Table 5.1) | Core Spec 6.0, Vol 3 Part G §5.2.1 — https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-60/out/en/host/generic-attribute-profile--gatt-.html (2026-10-01, `TIÊU CHUẨN`, SPEC) | MTU 23 là đủ cho payload 36 byte nếu tách 2 gói ATT; 1 gói cần MTU ≥ 39 |
| `ATT_MTU` thực dụng tối đa | **247** (251 LL − 4 octet L2CAP header) — giá trị dùng trong thí nghiệm nRF52840 | Sensors 2019, DOI [10.3390/s19173746](https://doi.org/10.3390/s19173746) (2026-10-01, `BÀI BÌNH DUYỆT`, FIELD-MEASURED) | 1 notification = 1 event ⇒ giảm trễ và jitter |
| ATT_EXCHANGE_MTU | bắt buộc ≥ default; client/server lấy min hai phía | Core Spec 6.0 Vol 3 Part F §3.2.8 — https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-60/out/en/host/attribute-protocol--att-.html (2026-10-01, `TIÊU CHUẨN`) | 1 vòng trao đổi MTU lúc kết nối ⇒ trễ thiết lập |
| Số gói mỗi connection event | Spec **không đặt trần cứng**; event chỉ bị đóng theo luật §4.5.6, kéo dài tới sát anchor point kế tiếp | Core Spec 6.0 Vol 6 Part B §4.5.1/§4.5.6 (nt) (`TIÊU CHUẨN`) | Nhiều gói/event ⇒ giảm trễ cho burst; nhưng cần DLE + MTU lớn |
| Số gói/event thực tế | 6 gói/event (Nexus 4 & 6P, CI 7,5 ms); ví dụ cấu hình 12 gói (6 mỗi chiều) | Punch Through — https://punchthrough.com/maximizing-ble-throughput-on-ios-and-android/ (2026-10-01, `ĐO ĐỘC LẬP`, FIELD-MEASURED, thiết bị 2015) | Trần thực tế do stack/HAL điện thoại, không chỉ do spec |
| Thời gian thiết lập (connection setup) | Event đầu tiên rơi vào cửa sổ `transmitWindowDelay + offset … + size`, `size` ≤ min(10 ms, connInterval−1,25 ms) | Core Spec 6.0 Vol 6 Part B §4.5.3 (nt) (`TIÊU CHUẨN`) | Trễ cố định khi (tái) kết nối, cộng thêm vào cold-start |

### A.2 Giá trị **Android thực tế** cho phép đặt (đã xác minh trong AOSP)

`BluetoothGatt.requestConnectionPriority(int)` chỉ nhận 4 hằng số; tài liệu Android **không** nêu ms. Nhưng AOSP `android/app/res/values/config.xml` định nghĩa giá trị cụ thể (đơn vị **bội số 1,25 ms**, nguyên văn trong file):

| Mức ưu tiên Android | Hằng số API | `min_interval` | `max_interval` | `latency` | Quy đổi |
|---|---|---|---|---|---|
| `CONNECTION_PRIORITY_HIGH` | 1 | 9 | 12 | 0 | **11,25 ms → 15 ms**, latency 0 |
| `CONNECTION_PRIORITY_BALANCED` (mặc định) | 0 | 24 | 40 | 0 | **30 ms → 50 ms** (comment: "Default specs recommended interval is 30–50 ms") |
| `CONNECTION_PRIORITY_LOW_POWER` | 2 | 80 | 100 | 2 | **100 ms → 125 ms**, latency 2 |
| `CONNECTION_PRIORITY_DCK` (Digital Car Key) | 3 | 24 | 24 | 0 | 30 ms |
| Companion device — *primary* (HIGH) | — | 6 | 8 | 45 | **7,5 ms → 10 ms**, latency 45 |
| Companion device — *secondary* (HIGH) | — | 6 | 6 | 0 | 7,5 ms |

Nguồn: AOSP `packages/modules/Bluetooth/android/app/res/values/config.xml` — https://android.googlesource.com/platform/packages/modules/Bluetooth/+/refs/heads/main/android/app/res/values/config.xml (2026-10-01, `MÃ NGUỒN`, SOURCE-CODE — **có thể bị OEM ghi đè**, xem mục G).
Hằng số API và mô tả: https://developer.android.com/reference/android/bluetooth/BluetoothGatt (2026-10-01, `NỀN TẢNG CHÍNH THỨC`) — `CONNECTION_PRIORITY_BALANCED=0`, `HIGH=1`, `LOW_POWER=2`, `DCK=3`; `requestConnectionPriority` cần `BLUETOOTH_CONNECT`.
Supervision timeout mà Android dùng khi gửi Connection Parameter Update: `int timeout = 500; // 5s. Link supervision timeout is measured in N * 10ms` — AOSP `GattService.java` — https://android.googlesource.com/platform/packages/modules/Bluetooth/+/refs/heads/main/android/app/src/com/android/bluetooth/gatt/GattService.java (2026-10-01, `MÃ NGUỒN`).

**Các API Android liên quan trực tiếp tới RQ6** (nguồn: BluetoothGatt ref, `NỀN TẢNG CHÍNH THỨC`):
- `requestMtu(int)` (API 21) — đặt ATT_MTU.
- `setPreferredPhy(int txPhy, int rxPhy, int phyOptions)` — chọn PHY.
- `requestConnectionPriority(int)` (API 21) — đổi connection interval về phía stack; **là "request", không phải lệnh** — peripheral có thể từ chối/bão hoà.
- `requestSubrateMode(int)` (**API 36.1**, Android 16) — cần `BLUETOOTH_PRIVILEGED` **hoặc** đã liên kết qua Companion Device Manager; dùng kèm `requestConnectionPriority` để cân bằng latency/pin.
- `connectGatt(Context, boolean autoConnect, …)` — `autoConnect=true` = tự kết nối lại khi thiết bị xuất hiện: https://developer.android.com/reference/android/bluetooth/BluetoothDevice (2026-10-01, `NỀN TẢNG CHÍNH THỨC`). Nhiều overload `connectGatt` bị **deprecated ở API 37** (thay bằng `connectGatt(BluetoothGattConnectionSettings, …)`) → lưu ý vòng đời API khi thiết kế nút cầu.

---

## B. Số đo độ trễ/độ tin cậy đã công bố

| # | Nguồn | Kịch bản | Số đo | Loại |
|---|---|---|---|---|
| B1 | Gomez et al., *Overview and Evaluation of BLE*, Sensors 2012 — DOI [10.3390/s120911734](https://doi.org/10.3390/s120911734) (`BÀI BÌNH DUYỆT`) | CC2540 slave, khoảng cách 0,5 m, TX 0 dBm, đo bằng power analyzer Agilent N6705A | **676,7 µs** cho 1 ATT exchange một chiều không lỗi (đo thực); mô phỏng 10 triệu trao đổi: round-trip **< 2 ms**, one-way **< 1 ms** ở BER 10⁻⁶ | FIELD-MEASURED + SIM |
| B2 | Gomez et al. (nt) | Cùng mô hình, BER cao | Ở **BER 10⁻³**, độ trễ trung bình **tăng tới ~3 bậc độ lớn** (tới ~1–2 s) vì phải dùng nhiều connection event cho 1 ATT message | SIM/ANALYTIC |
| B3 | *Measurement-Based Latency Evaluation … Using BLE*, IEEE VTC2023-Spring — DOI [10.1109/vtc2023-spring57618.2023.10200332](https://doi.org/10.1109/vtc2023-spring57618.2023.10200332) (`BÀI BÌNH DUYỆT`) | 2 bảng pin, **44 CMU (peripheral) + 4 BMU (master)**, môi trường đa đường, nhiều piconet | **Độ trễ 140–160 ms tại CCDF = 10⁻⁴** cho mỗi master | FIELD-MEASURED (bối cảnh đông thiết bị) |
| B4 | *Mitigation of Data Packet Loss in BLE-Based Wearable Healthcare Ecosystem*, Biosensors 2021 — DOI [10.3390/bios11100350](https://doi.org/10.3390/bios11100350) (`BÀI BÌNH DUYỆT`) | Wearable ↔ smartphone Android/iOS thật; có nhiễu lò vi sóng gia dụng | **Mất gói < 1 %** khi lò vi sóng bật; giảm tần suất truyền + gom gói đưa mất gói **xuống < 1 %**; protocol hàng đợi + re-request **loại bỏ mất gói còn lại** | FIELD-MEASURED |
| B5 | Rondón, Gidlund & Landernäs, IJWIN 2017 — DOI [10.1007/s10776-017-0357-0](https://doi.org/10.1007/s10776-017-0357-0) (`BÀI BÌNH DUYỆT`) — số liệu dẫn lại nguyên văn trong B4 | BLE cho truyền thông time-critical công nghiệp, 3 sơ đồ retransmission có giới hạn | **Trễ tối đa < 46 ms**, **tỉ lệ mất gói ~10⁻⁵** | FIELD-MEASURED (qua bài bình duyệt thứ cấp; **chưa đọc được toàn văn gốc** — nhà xuất bản chặn) |
| B6 | Tosi et al., *Performance Evaluation of BLE: A Systematic Review*, Sensors 2017 — DOI [10.3390/s17122898](https://doi.org/10.3390/s17122898) (`BÀI BÌNH DUYỆT`, review) | Tổng hợp literature | **Discovery latency trung bình 1–30 s** khi thay advInterval/scanInterval/scanWindow; throughput lý thuyết ~230 kbps nhưng ứng dụng thực tế chỉ ~100 kbps; số node/piconet thường < 10 | SIM + FIELD (tổng hợp) |
| B7 | *Analysis of Latency Performance of BLE Networks*, Sensors 2014 — DOI [10.3390/s150100059](https://doi.org/10.3390/s150100059) (`BÀI BÌNH DUYỆT`) | Mô hình giải tích discovery M:N | Discovery latency giảm rất chậm khi scan window < 100 ms và gần như bão hoà khi > 100 ms; **không đo được** trễ kết nối RTT | SIM/ANALYTIC |
| B8 | *Measurement-based evaluation of Google/Apple Exposure Notification API …*, PLOS ONE 2021 — DOI [10.1371/journal.pone.0250826](https://doi.org/10.1371/journal.pone.0250826) (`BÀI BÌNH DUYỆT`) | **60 cặp vị trí điện thoại Android trên xe bus 2 tầng** (môi trường kim loại, đông người) | Đổi người ngồi ⇒ suy hao GAEN biến thiên **±10 dB**; với luật của app Thụy Sĩ **không có cảnh báo nào được kích hoạt dù mọi cặp đều trong 2 m ≥ 15 phút**; luật ngưỡng thay thế đạt **detection rate ≤ 5 %** (ngưỡng 15 phút) và **8 %** (ngưỡng 10 phút) | FIELD-MEASURED (**cảnh báo**: đây là độ tin cậy của *phát hiện tiệm cận theo RSSI*, KHÔNG phải độ tin cậy của kết nối — xem mục G) |
| B9 | *A model of packet loss in the BLE component of a wearable BAN caused by interference from microwave ovens*, IEEE HIC 2014 — DOI [10.1109/hic.2014.7038881](https://doi.org/10.1109/hic.2014.7038881) (`BÀI BÌNH DUYỆT`) | BLE body-area network gần lò vi sóng | Có mô hình mất gói; **KHÔNG TÌM THẤY SỐ LIỆU ĐỊNH LƯỢNG** trong phần truy cập được | — |
| B10 | *Coexistence and interference tests on a BLE front-end*, IEEE SAI 2014 — DOI [10.1109/sai.2014.6918312](https://doi.org/10.1109/sai.2014.6918312) (`BÀI BÌNH DUYỆT`) | Miền 2,4 GHz đông thiết bị | Bài tồn tại và đúng chủ đề; **KHÔNG TÌM THẤY SỐ LIỆU ĐỊNH LƯỢNG** (không có bản OA) | — |
| B11 | Punch Through, *Maximizing BLE Throughput* — https://punchthrough.com/maximizing-ble-throughput-on-ios-and-android/ (2026-10-01, `ĐO ĐỘC LẬP`) | Nexus 4 / Nexus 6P, iPhone 6/6S, MacBook Pro | Android: **CI tối thiểu 7,5 ms, 6 gói/event, ~16.000 byte/s**; iPhone: CI 30 ms → 2.667 byte/s, khi có HID over GATT **CI 11,25 ms → 7.111 byte/s** | FIELD-MEASURED (blog, thiết bị ~2015) |

**Nhận xét cho RQ6:** tôi **KHÔNG TÌM THẤY NGUỒN** nào đo round-trip latency / jitter / tỉ lệ mất gói của **link BLE điện thoại ↔ một thiết bị đeo trong tầm 1–2 m trong môi trường đông người** (kiểu hội trường/đám đông) theo đúng nghĩa RQ6. Các số gần nhất là B1–B5 (2 node, tầm ngắn, có/không nhiễu cục bộ) và B3 (đông piconet nhưng 44 node trên bảng pin, không phải điện thoại–wearable). B8 là bằng chứng mạnh rằng **tầng vô tuyến 2,4 GHz trong không gian đông người/kim loại rất khó đoán**, nhưng nó đo *RSSI proximity*, không đo *kết nối*.

---

## C. Ràng buộc chạy nền Android + cách duy trì kết nối

### C.1 Doze / App Standby (chính thức)
Nguồn: https://developer.android.com/training/monitoring-device-state/doze-standby (2026-10-01, `NỀN TẢNG CHÍNH THỨC`).
Danh sách hạn chế **nguyên văn** khi vào Doze: *"Suspends network access. Ignores wake locks. Defers… jobs, syncs, alarms. Doesn't perform Wi-Fi scans. Doesn't let sync adapters run. Doesn't let JobScheduler run."*
→ **Lưu ý quan trọng:** tài liệu Doze **không** liệt kê BLE/Bluetooth là bị ngắt; nhưng cũng **không** có bất kỳ bảo đảm nào. **KHÔNG TÌM THẤY SỐ LIỆU** định lượng của Google/AOSP về ảnh hưởng của Doze lên một kết nối BLE thường trực.
→ App Standby: app idle bị hoãn job/sync; được cấp mạng "khoảng một lần/ngày"; có danh sách app **partially exempt** (dùng được network + partial wake lock trong Doze) — có thể xin exemption (`REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`) hoặc app được người dùng bật thủ công.

### C.2 Foreground service (FGS) — Android 14+ bắt buộc `connectedDevice`
Nguồn: https://developer.android.com/about/versions/14/changes/fgs-types-required (2026-10-01, `NỀN TẢNG CHÍNH THỨC`).
- App targetSdk 34 phải khai báo `android:foregroundServiceType`. Loại phù hợp: **`connectedDevice`**, quyền `FOREGROUND_SERVICE_CONNECTED_DEVICE`, hằng `FOREGROUND_SERVICE_TYPE_CONNECTED_DEVICE`.
- **Điều kiện runtime tiên quyết (nguyên văn)**: phải đúng **một trong** các điều kiện — khai `CHANGE_NETWORK_STATE` / `CHANGE_WIFI_STATE` / `CHANGE_WIFI_MULTICAST_STATE` / `NFC` / `TRANSMIT_IR`; **hoặc** được cấp runtime một trong `BLUETOOTH_CONNECT`, `BLUETOOTH_ADVERTISE`, `BLUETOOTH_SCAN`, `UWB_RANGING`; **hoặc** *"Call `UsbManager.requestPermission()`"*.
→ Với RescueMesh: đường BLE dùng `BLUETOOTH_CONNECT`; đường dây USB dùng `UsbManager.requestPermission()` — cùng một loại FGS.
- Giới hạn khởi động FGS từ background từ **Android 12**: https://developer.android.com/develop/background-work/services/fgs/restrictions-bg-start (2026-10-01, `NỀN TẢNG CHÍNH THỨC`) — có danh sách miễn trừ; đây là rủi ro thật khi app bị hệ thống kill rồi cần tự dựng lại service trong lúc màn hình tắt.
- **Android 15**: timeout **6 giờ / 24 giờ** chỉ áp cho `dataSync` (và `mediaProcessing`) — nguồn: https://developer.android.com/about/versions/15/behavior-changes-15 (2026-10-01, `NỀN TẢNG CHÍNH THỨC`). **`connectedDevice` KHÔNG nằm trong danh sách timeout này** ⇒ chọn `connectedDevice` là đúng cho link SOS thường trực.
- Quyền `BLUETOOTH_CONNECT` (runtime, Android 12+): https://developer.android.com/develop/connectivity/bluetooth/bt-permissions (2026-10-01, `NỀN TẢNG CHÍNH THỨC`).

### C.3 Giới hạn tần suất scan / advertise — có định lượng trong AOSP
Nguồn: AOSP `AdapterService.java` (`MÃ NGUỒN`), nhánh `main`, `android13-release`, `android14-release`, `android15-release`:
- https://android.googlesource.com/platform/packages/modules/Bluetooth/+/refs/heads/main/android/app/src/com/android/bluetooth/btservice/AdapterService.java
- https://android.googlesource.com/platform/packages/modules/Bluetooth/+/refs/heads/android13-release/android/app/src/com/android/bluetooth/btservice/AdapterService.java
- https://android.googlesource.com/platform/packages/modules/Bluetooth/+/refs/heads/android14-release/android/app/src/com/android/bluetooth/btservice/AdapterService.java
- https://android.googlesource.com/platform/packages/modules/Bluetooth/+/refs/heads/android15-release/android/app/src/com/android/bluetooth/btservice/AdapterService.java

| Hằng số | Android 13 | Android 14/15 & `main` |
|---|---|---|
| `DEFAULT_SCAN_QUOTA_COUNT` | 5 | 5 |
| `DEFAULT_SCAN_QUOTA_WINDOW_MILLIS` | 30 s | 30 s |
| `DEFAULT_SCAN_TIMEOUT_MILLIS` | **30 phút** | **10 phút** |

→ Nghĩa là: **quá 5 lần startScan trong 30 giây** bị coi là "quét quá thường xuyên" (`isScanningTooFrequently()` trong `AppScanStats.java`), và **một scan bị dừng sau 10 phút** (`isScanningTooLong()`). Cả 3 giá trị **có thể bị ghi đè qua DeviceConfig** namespace `bluetooth` (`scan_quota_count`, `scan_quota_window_millis`, `scan_timeout_millis`).

### C.4 Hành vi khi tắt màn hình — duty cycle bị bóp (định lượng)
Nguồn: AOSP `ScanManager.java` và `AppScanStats.java` (`MÃ NGUỒN`):
- https://android.googlesource.com/platform/packages/modules/Bluetooth/+/refs/heads/main/android/app/src/com/android/bluetooth/le_scan/ScanManager.java
- https://android.googlesource.com/platform/packages/modules/Bluetooth/+/refs/heads/main/android/app/src/com/android/bluetooth/le_scan/AppScanStats.java

| Scan mode | Scan window | Scan interval | Duty cycle | Nguồn |
|---|---|---|---|---|
| `SCAN_MODE_LOW_LATENCY` | 100 ms | 100 ms | **100 %** | `ScanManager.java` |
| `SCAN_MODE_BALANCED` | 183 ms | 730 ms | ~25 % (`BALANCED_WEIGHT = 25`) | `ScanManager.java` + `AppScanStats.java` |
| `SCAN_MODE_LOW_POWER` | 140 ms | 1.400 ms | **10 %** (`LOW_POWER_WEIGHT = 10`) | `ScanManager.java` + `AppScanStats.java` |
| `SCAN_MODE_SCREEN_OFF` (màn hình tắt, low power) | 512 ms | 10.240 ms | **5 %** (`SCREEN_OFF_LOW_POWER_WEIGHT = 5`) | `ScanManager.java` + `AppScanStats.java` |
| `SCAN_MODE_SCREEN_OFF_BALANCED` | 183 ms | 730 ms | ~25 % | `ScanManager.java` |

Logic chuyển đổi (`ScanManager.updateScanModeScreenOff`): khi **app không ở foreground** hoặc bị force-downgrade → scan bị hạ về `SCAN_MODE_SCREEN_OFF` (5 % duty cycle). `ScanSettings.SCAN_MODE_SCREEN_OFF` / `SCAN_MODE_SCREEN_OFF_BALANCED` là hằng số **hidden** của AOSP (không có trong SDK công khai).
→ **Hệ quả cho RQ6:** nếu nút cầu chỉ *advertise* để điện thoại scan tìm lại, việc tắt màn hình làm giảm 20× cơ hội bắt advertisement ở mode LOW_POWER (10 % → 5 %) và thêm trần 10 phút/lần scan. Vì vậy nên **duy trì kết nối (connection) thay vì scan lại**, hoặc để nút cầu chủ động reconnect.

### C.5 Cơ chế duy trì kết nối BLE khi màn hình tắt — và giới hạn thực tế
Nguồn chính: https://developer.android.com/develop/connectivity/bluetooth/ble/background (2026-10-01, `NỀN TẢNG CHÍNH THỨC`) — "Communicate in the background".

| Cơ chế | Nền tảng chính thức nói gì | Giới hạn thực tế |
|---|---|---|
| FGS `connectedDevice` | *"If the connection needs to be kept alive as long as possible… start a foreground service with the connectedDevice type."* | Phải được start khi app còn foreground (hoặc trong miễn trừ); Android 12+ chặn start FGS từ background |
| `CompanionDeviceService` + `REQUEST_COMPANION_RUN_IN_BACKGROUND` + `CompanionDeviceManager.startObservingDevicePresence()` | Được nêu là giải pháp cho app cần lắng nghe lâu dài; có thể start service từ background | Cần luồng pairing/association với người dùng; xem https://developer.android.com/develop/connectivity/bluetooth/companion-device-pairing (2026-10-01, `NỀN TẢNG CHÍNH THỨC`) |
| `connectGatt(..., autoConnect=true, ...)` | Android tự kết nối lại khi thiết bị xuất hiện | Không có bảo đảm thời gian; phụ thuộc stack/OEM; overload bị deprecated API 37 |
| Bond (`createBond()`) | Ghép đôi để tái kết nối nhanh, dùng IRK/resolvable address | Cần tương tác người dùng lần đầu; bond hỏng ⇒ phải xoá và ghép lại |
| `WorkManager` (PeriodicWorkRequest/OneTimeWorkRequest) | *"app restrictions might apply"* — dùng cho tác vụ ngắn | Bị JobScheduler/Doze hoãn; không phù hợp cho link SOS "phải sống" |
| `BLUETOOTH_CONNECT` | Bắt buộc cho mọi thao tác GATT | Runtime permission; người dùng có thể thu hồi ⇒ link chết |
| **Process bị kill** | Nguyên văn: *"although the connection is closed if your process is killed"* | Không có cách nào giữ kết nối nếu process chết — phải thiết kế auto-reconnect + retry SOS ở phía firmware nút cầu |

→ **KHÔNG TÌM THẤY NGUỒN** nào (AOSP doc hay bài bình duyệt) định lượng được **xác suất duy trì kết nối BLE qua một đêm màn hình tắt** trên Android. Đây là khoảng trống đo lường trực tiếp cho RQ6.

---

## D. PHY và năng lượng

### D.1 Bảng PHY (Bluetooth Core Spec 6.0, Table 4.2 và §4.1–4.2)
Nguồn: https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-60/out/en/low-energy-controller/physical-layer-specification.html (2026-10-01, `TIÊU CHUẨN`, SPEC).

| PHY | Tốc độ | Độ nhạy yêu cầu tối thiểu (Table 4.2) | Nhận xét cho link 1–2 m |
|---|---|---|---|
| LE Uncoded 1M | 1 Mb/s | **≤ −70 dBm** | Đủ dư link budget ở 1–2 m; an toàn/robust nhất |
| LE Uncoded 2M | 2 Mb/s | **≤ −70 dBm** (cùng nhóm Uncoded) | **Nửa thời gian trên không mỗi gói** ⇒ ít năng lượng/gói hơn ở cự ly ngắn |
| LE Coded S=2 | 500 kb/s | **≤ −75 dBm** | Thừa ở 1–2 m; gấp ~2× airtime |
| LE Coded S=8 | 125 kb/s | **≤ −82 dBm** | Chỉ để đi xa; gấp ~8× airtime ⇒ **tốn pin hơn** ở 1–2 m |

BER mục tiêu theo Table 4.1: 0,1 % (payload 1–37 B), 0,064 % (38–63 B), 0,034 % (64–127 B), 0,017 % (128–255 B).
**Khuyến nghị cho RescueMesh (1–2 m):** dùng **LE 2M PHY** cho đường thường (giảm airtime/energy mỗi gói SOS 36 byte), giữ **LE 1M** làm fallback khi 2M không thương lượng được hoặc chất lượng link xấu; **không** dùng Coded PHY cho chặng này (Coded để dành cho mesh LoRa/thiết bị xa).
Phân tích đánh đổi Bluetooth 5 (2M vs Coded vs khoảng cách) trong bối cảnh kết nối thực tế: *Bluetooth 5 performance analysis for inter-vehicular communications*, Wireless Networks 2021 — DOI [10.1007/s11276-021-02830-9](https://doi.org/10.1007/s11276-021-02830-9) (2026-10-01, `BÀI BÌNH DUYỆT`; bối cảnh xe cộ, không phải đeo người — chỉ dùng cho phần PHY).

### D.2 Năng lượng — số đo đã công bố
| Nguồn | Số đo | Loại |
|---|---|---|
| Sensors 2019, DOI [10.3390/s19173746](https://doi.org/10.3390/s19173746) (`BÀI BÌNH DUYỆT`) — nRF52840 DK ×2, đo bằng **Nordic Power Profiler Kit**, có bảng CI 7,5/30/75/150/400/1000 ms, ATT_MTU 23/247 | *"Here, we can see that the 2 Mb/s PHY used in BLE 5 **consumes more power**. On the other hand, it also nets significantly higher throughput (**roughly 1.7× increase**)."* Năng lượng để truyền một lượng dữ liệu **giảm dần** qua BLE 4.1 → 4.2 → 5; dòng nhàn rỗi của module ~**70 µA**, dòng đỉnh TX **1–70 mA** (Bảng 2 của bài) | FIELD-MEASURED |
| Sensors 2012, DOI [10.3390/s120911734](https://doi.org/10.3390/s120911734) (`BÀI BÌNH DUYỆT`) | Đo bằng Agilent N6705A; pin coin 220 mAh/3 V; khoảng cách 0,5 m; 0 dBm; đánh giá tuổi thọ pin theo `connInterval`/`connSlaveLatency` | FIELD-MEASURED |
| Android Doze/background docs | **KHÔNG TÌM THẤY SỐ LIỆU** pin (mA/mW) cho một kết nối BLE thường trực trên điện thoại | — |
| MEMSTECH 2018, DOI [10.1109/memstech.2018.8365745](https://doi.org/10.1109/memstech.2018.8365745) (`BÀI BÌNH DUYỆT`) | "Ảnh hưởng của BLE tới tiêu thụ năng lượng trên Android OS" — abstract **không có số**; bản toàn văn không OA ⇒ **KHÔNG TÌM THẤY SỐ LIỆU** | — |

→ **Kết luận D.2:** mọi số năng lượng BLE **đo được** trong tài liệu tôi truy cập đều ở **phía module nRF/CC2540**, không phải phía điện thoại. **KHÔNG TÌM THẤY NGUỒN** đo dòng tiêu thụ tăng thêm của **điện thoại Android** khi duy trì 1 kết nối BLE thường trực (một ngày). Đây là gap đo lường cần thực nghiệm riêng.

---

## E. So với phương án dây USB-C (USB CDC/OTG)

### E.1 Ràng buộc nền tảng (chính thức)
| Vấn đề | Nội dung | Nguồn |
|---|---|---|
| Chế độ host | *"When your Android-powered device is in USB host mode, it acts as the USB host, **powers the bus**, and enumerates connected USB devices. USB host mode is supported in Android 3.1 and higher."* | https://developer.android.com/develop/connectivity/usb/host (2026-10-01, `NỀN TẢNG CHÍNH THỨC`) |
| Quyền | `UsbManager.requestPermission()` hiện **dialog cho người dùng** theo từng thiết bị; cần broadcast receiver cho intent kết quả; nếu bị từ chối → lỗi runtime | https://developer.android.com/reference/android/hardware/usb/UsbManager + usb/host (nt, `NỀN TẢNG CHÍNH THỨC`) |
| Phát hiện cắm | Cần `<uses-feature android:name="android.hardware.usb.host">`, minSdk ≥ 12, và cặp `<intent-filter>`/`<meta-data>` cho `android.hardware.usb.action.USB_DEVICE_ATTACHED` + file XML `<usb-device>` | usb/host (nt) |
| FGS | Đường USB cũng thoả tiên quyết FGS `connectedDevice` qua `UsbManager.requestPermission()` | https://developer.android.com/about/versions/14/changes/fgs-types-required (nt, `NỀN TẢNG CHÍNH THỨC`) |
| Sạc đồng thời | Tài liệu Android nói điện thoại **cấp nguồn cho bus** ⇒ theo mô hình host chuẩn, cùng một cổng không thể vừa host vừa nhận sạc; cần hub có nguồn/PD pass-through. **Đây là suy luận từ câu chữ trên, KHÔNG phải câu khẳng định trực tiếp của Google** | — |

### E.2 Độ trễ — nguồn nền tảng
| Vấn đề | Số/Quy định | Nguồn |
|---|---|---|
| Chu kỳ khung full-speed | frame 1 ms (high-speed dùng microframe 125 µs) | USB 2.0 Specification (USB-IF) — https://www.usb.org/sites/default/files/usb_20_20250603.zip (2026-10-01, `TIÊU CHUẨN`, SPEC) |
| Interrupt endpoint `bInterval` | Full-speed: **1–255 ms**; Low-speed: 10–255 ms; High-speed: `(2^(bInterval−1)) × 125 µs`, bInterval 1–16 | USB 2.0 Spec, §9.6.6 (nt, `TIÊU CHUẨN`) |
| Polling thực tế | *"the endpoint is only polled when the software client has an IRP for an interrupt transfer pending"* ⇒ trễ phụ thuộc app/host, không chỉ phần cứng | USB 2.0 Spec (nt) |
| Latency timer FTDI (chip USB-UART phổ biến) | `priv->latency = 16;` (16 ms) khi không đọc được EEPROM; chip NDI đặt `latency = 1` ms | Linux kernel `drivers/usb/serial/ftdi_sio.c` — https://raw.githubusercontent.com/torvalds/linux/master/drivers/usb/serial/ftdi_sio.c (2026-10-01, `MÃ NGUỒN`) |
| CDC-ACM notification endpoint `bInterval` | Tôi **KHÔNG TÌM THẤY** quy định số cụ thể trong CDC 1.2 | USB CDC 1.2 class spec — https://www.usb.org/document-library/class-definitions-communication-devices-12 (2026-10-01, `TIÊU CHUẨN`) |
| Đo độ trễ/độ tin cậy USB-C CDC/OTG **trên điện thoại Android** | **KHÔNG TÌM THẤY NGUỒN** (không có bài bình duyệt nào đo; các kết quả Crossref tìm được chỉ là datasheet/chuẩn chung) | — |

### E.3 So sánh định tính cho RQ6
| Tiêu chí | BLE (link cá nhân) | USB-C CDC/OTG |
|---|---|---|
| Trễ điển hình | 1 connection interval: **11,25–15 ms** nếu `CONNECTION_PRIORITY_HIGH` (AOSP config) + airtime | Phụ thuộc driver: **+16 ms** nếu chip FTDI mặc định; CDC-ACM trên Android phụ thuộc `bulkTransfer` và lịch frame 1 ms |
| Yếu tố bất định | Nhiễu 2,4 GHz, Wi-Fi/đám đông, hành vi ROM/OEM | Cắm/rút cơ học, quyền USB theo từng thiết bị, hub |
| Năng lượng điện thoại | Có tiêu thụ radio liên tục (**chưa có số đo trên điện thoại** — mục D) | Không tốn radio; nhưng tiêu thụ để cấp VBUS cho nút cầu |
| Sạc đồng thời | Có (cổng USB-C còn trống để sạc) | Khó/biến dạng cấu hình (hub có nguồn) |
| Ràng buộc người dùng | 1 lần cấp quyền, tự động | Cắm dây mỗi lần; dễ tuột khi vận động/cứu hộ |
| Trạng thái bằng chứng cho RQ6 | Có số đo 2-node tầm ngắn (B1–B5) và bối cảnh Android (mục C) | **Gần như không có số liệu bình duyệt trên Android** |

---

## F. Khoảng trống (chưa ai công bố gì)

1. **KHÔNG TÌM THẤY NGUỒN**: không có công bố nào đo **độ trễ/độ tin cậy của link BLE điện thoại ↔ nút cầu (bridge)** trong bối cảnh cứu hộ/thảm họa, với khung SOS nhỏ (~36 byte), tầm 1–2 m, nút cầu **đeo trên người nạn nhân**. Đã tìm Crossref/OpenAlex/Europe PMC với các truy vấn ở mục H.
2. Các công trình gần nhất (đều **khác** RQ6):
   - IEEE Access 2026 — *Long-Range BLE Detection via Drone-Based LoRa Relays for Search and Rescue* — DOI [10.1109/access.2026.3731317](https://doi.org/10.1109/access.2026.3731317) (`BÀI BÌNH DUYỆT`): dùng **BLE advertising** của thiết bị cá nhân làm tín hiệu cơ hội, **drone quét BLE rồi relay qua LoRa**. → Điện thoại là *mục tiêu bị tìm*, không phải bên gửi SOS; không có link kết nối BLE phone↔bridge.
   - IEEE Access 2022 — *BLE for Close Detection in Search and Rescue Missions With Robotic Platforms: An Experimental Evaluation* — DOI [10.1109/access.2022.3204272](https://doi.org/10.1109/access.2022.3204272) (`BÀI BÌNH DUYỆT`): robot/UAV quét BLE để phát hiện nạn nhân.
   - IEEE THS 2017 — *Disaster response: Victims' localization using Bluetooth Low Energy sensors* — DOI [10.1109/ths.2017.7943504](https://doi.org/10.1109/ths.2017.7943504) (`BÀI BÌNH DUYỆT`).
   - Computer Communications 2022 — *LoRa support for long-range real-time inter-cluster communications over BLE industrial networks* — DOI [10.1016/j.comcom.2022.05.026](https://doi.org/10.1016/j.comcom.2022.05.026) (`BÀI BÌNH DUYỆT`): BLE + LoRa, nhưng cho mạng công nghiệp giữa các cluster BLE, **không** có chặng điện thoại↔bridge và không có ngữ cảnh cứu hộ.
3. **KHÔNG TÌM THẤY NGUỒN** định lượng hành vi của một FGS `connectedDevice` giữ kết nối BLE qua **màn hình tắt/Doze kéo dài** trên ROM thực tế (mục C.5) — kể cả trong tài liệu AOSP.
4. **KHÔNG TÌM THẤY NGUỒN** đo **dòng tiêu thụ tăng thêm trên điện thoại** khi duy trì một kết nối BLE thường trực (mục D.2).
5. **KHÔNG TÌM THẤY NGUỒN** so sánh **BLE vs USB-C CDC/OTG trên điện thoại Android** về độ trễ/độ tin cậy (mục E.2).
6. **KHÔNG TÌM THẤY NGUỒN** đo BLE 2-node trong **môi trường đông người thật** (hội trường/đám đông/tòa nhà đổ) — chỉ có bối cảnh bus (B8, đo RSSI) và bảng pin 44 node (B3).
→ Đây là cơ sở để RQ6 tự thực nghiệm: đo RTT, jitter, PDR, reconnect-time trên chính link phone↔bridge, ở 1–2 m, màn hình tắt, có/không nhiễu 2,4 GHz.

---

## G. Số liệu KHÔNG được dùng (và lý do)

| Số liệu | Nguồn | Lý do không dùng cho RQ6 |
|---|---|---|
| "Tầm xa gấp 4 lần", "hơn 1 km", "độ nhạy −103 dBm" của LE Coded | Bluetooth SIG, https://www.bluetooth.com/learn-about-bluetooth/key-attributes/range/ (2026-10-01, `VENDOR-CLAIMED`) | Là **tiếp thị/best-case**, không phải phép đo có đối chứng; Core Spec chỉ yêu cầu **≤ −82 dBm cho S=8** (Table 4.2) |
| "Throughput lý thuyết ~230 kbps" | Tosi 2017 (nt) | Là **trần lý thuyết**; chính bài đó nói ứng dụng thực tế chỉ ~100 kbps. Không dùng làm throughput thiết kế |
| "11,25 ms" như **bảo đảm của API Android** | AOSP `config.xml` | Đúng là 9×1,25 ms trong AOSP, nhưng là **giá trị resource có thể bị OEM/ROM ghi đè**, và `requestConnectionPriority` chỉ là *request* — không phải cam kết. Dùng để **kỳ vọng**, không dùng để **khẳng định** |
| "Discovery latency 1–30 s" | Tosi 2017 / Sensors 2014 | Là trễ **tìm thấy nhau (advertising/scanning)**, không phải trễ **kết nối**. RQ6 nói về link đã kết nối ⇒ không áp dụng |
| "Detection rate 5–8 %" của GAEN | PLOS ONE 2021 (nt) | Đo **phát hiện tiệm cận theo RSSI** trên bus, không đo kết nối/kết nối lại. Không suy ra được PDR của link SOS |
| "140–160 ms @ CCDF 10⁻⁴" | VTC 2023 (nt) | Bối cảnh **44 peripheral/4 master** trên bảng pin ⇒ không đại diện cho link 2 node ở 1–2 m. Chỉ dùng làm **biên trên tham khảo** cho kịch bản đông piconet |
| "7.111 byte/s @ 11,25 ms" và "30 ms → 2.667 byte/s" | Punch Through (nt) | Số của **iPhone/iOS** (2015) — Apple quản lý connection interval khác Android. Không áp cho Android |
| "676 µs" | Gomez 2012 (nt) | Là 1 ATT exchange một chiều ở **tầng link/CC2540**, đã loại trừ tầng app Android. **Không** được trích như "độ trễ end-to-end của SOS" |
| "16 ms latency timer" | Linux `ftdi_sio.c` | Chỉ đúng cho **chip FTDI** với EEPROM mặc định. Không áp cho CDC-ACM native hay CH340/CP210x |
| "36 byte" và "1–2 m" | Thiết kế RescueMesh-LoRa của nhóm | Là **giả định thiết kế**, không phải số đo từ tài liệu. Khi viết báo cáo phải ghi rõ là giả định |
| "10 phút scan timeout" | AOSP (nt) | Là timeout của **scan**, không phải của connection. Kết nối BLE có thể sống lâu hơn 10 phút; đừng nhầm để kết luận "link chỉ sống 10 phút" |
| Số liệu "ảnh hưởng BLE tới pin Android" | MEMSTECH 2018 (nt) | Abstract không có số; toàn văn không truy cập được ⇒ **không có số nào để dùng** |
| "ATT_MTU tối đa 517 octet" | Tài liệu phổ biến trên mạng | Tôi **KHÔNG** tìm thấy câu chữ xác nhận cho ATT_MTU trong Core Spec 6.0 đã đọc (chỉ có default 23 và LL payload ≤ 251). Không dùng cho tới khi có nguồn |
| Giá trị `gatt_*_priority_*_primary/secondary` (latency 45/120/150) | AOSP `config.xml` | Là cấu hình cho **companion device** (primary/secondary) trong ngữ cảnh LE Audio/thiết bị đồng hành; **không** phải giá trị mà `requestConnectionPriority` áp cho app thường |

---

## H. Sổ tìm kiếm (search log)

**Công cụ dùng được:** `web_fetch` + `curl` (URL cụ thể), OpenAlex API, Crossref REST, Europe PMC REST (search + fullTextXML), Unpaywall API, `oa.py`, AOSP gitiles (`?format=TEXT`), raw.githubusercontent.com.
**Công cụ hỏng/chặn:** `web_search` của harness (HTTP 401); API `api.semanticscholar.org` (HTTP 429); MDPI PDF/HTML (**403**, phải lấy qua Europe PMC); IEEE Xplore PDF (**404/bot-block**); link.springer.com PDF (**bot challenge**, 3.038 byte HTML); ftdichip.com PDF (**403**); Bing/Mojeek/DDG (captcha — theo README của nhóm).

**Truy vấn OpenAlex (`oa.py`)**: BLE latency measurement smartphone round-trip · BLE connection interval latency evaluation · BLE packet loss interference crowded 2.4 GHz · BLE energy consumption smartphone battery measurement · Bluetooth 5 coded PHY 2M PHY range throughput comparison · BLE reliability wearable sensor dense deployment · USB CDC latency measurement Android USB OTG · BLE disaster rescue victim detection smartphone · Android background restrictions BLE background execution · BLE scanning latency discovery time smartphone · experimental evaluation BLE latency Android smartphone measurement · BLE WiFi coexistence interference packet error rate measurement · digital contact tracing BLE performance crowd · Bluetooth 5 long range coded PHY experimental evaluation.

**Truy vấn Crossref (`query.bibliographic`)**: BLE latency measurement smartphone connection interval · BLE packet loss interference WiFi 2.4 GHz coexistence measurement · BLE smartphone energy consumption measurement power Android · USB CDC serial latency measurement data acquisition comparison wireless · BLE search and rescue disaster victims smartphone detection · Bluetooth 5 coded PHY 2M PHY range throughput experimental measurement · Measurement-Based Latency Evaluation Theoretical Analysis Massive IoT BLE · Long-Range BLE Detection Drone-Based LoRa Relays SAR · phone BLE bridge relay LoRa disaster SOS emergency link reliability · smartphone to LoRa gateway Bluetooth tethering disaster mesh SOS.

**Truy vấn Europe PMC (full-text)**: `"Bluetooth Low Energy" AND "connection interval" AND latency` (50 hits) · `"Bluetooth Low Energy" AND interference AND "packet error rate"` (37 hits) · `"round-trip" AND "Bluetooth Low Energy" AND latency` (76 hits) · `"Bluetooth Low Energy" AND "connection interval" AND Android` (15 hits) · `"exposure notification" AND Bluetooth AND performance AND measurement` (74 hits).

**Toàn văn đã đọc/khai thác:** PMC3478807 (Gomez 2012), PMC4327007 (latency 2014), PMC6749335 (Sensors 2019), PMC8533907 (Biosensors 2021), PMC5751532 (Tosi 2017), PMC8084251 (PLOS ONE 2021) — tải qua `https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML`.

**Kiểm chứng DOI:** toàn bộ DOI trong tài liệu này (16) đã tra `https://api.crossref.org/works/<DOI>` ngày 2026-10-01 và **tồn tại** — 16/16 trả về bản ghi hợp lệ (tiêu đề, năm, tạp chí). DOI nào không truy cập được toàn văn thì đã ghi rõ là số liệu lấy qua nguồn thứ cấp (B5).

**Nguồn chính thức lấy trực tiếp:** developer.android.com (BluetoothGatt, BluetoothDevice, ble/background, doze-standby, fgs-types-required, behavior-changes-15, bt-permissions, companion-device-pairing, restrictions-bg-start, usb/host, UsbManager) · AOSP gitiles nhánh `main`, `android13-release`, `android14-release`, `android15-release` (config.xml, AdapterService.java, ScanManager.java, AppScanStats.java, GattService.java, CompanionManager.java) · Bluetooth SIG Core 6.0 HTML (Vol 3 Part F/G, Vol 6 Part B) · USB-IF (USB 2.0 spec zip, CDC 1.2 zip) · Linux kernel `ftdi_sio.c`.

---

### Tóm tắt 5 điểm cho RQ6
1. **Trần trễ do tham số, không do phần cứng:** với `CONNECTION_PRIORITY_HIGH` (AOSP: 11,25–15 ms, latency 0), một gói SOS 36 byte nằm gọn trong 1 LL PDU (≤ 251 octet) → trễ một chiều kỳ vọng **< 20 ms** trong điều kiện sạch; worst-case khi bỏ event ≈ 2–3 × connection interval.
2. **Độ tin cậy là ẩn số thực nghiệm:** mọi số PDR/latency đã công bố đều ở tầm 2 node hoặc bối cảnh khác; chưa có số cho link phone↔bridge trong đám đông (mục F).
3. **Ràng buộc Android mới là rủi ro lớn nhất:** FGS `connectedDevice` (bắt buộc `BLUETOOTH_CONNECT`), chặn start FGS từ background (Android 12+), scan bị bóp duty cycle khi tắt màn hình (5 %), trần scan 10 phút và quota 5 lần/30 s, và **kết nối đóng khi process bị kill**.
4. **PHY:** dùng **LE 2M** cho chặng 1–2 m (giảm airtime/energy), giữ 1M làm fallback; **không** dùng Coded.
5. **USB-C không phải phương án thay thế miễn phí:** ưu điểm về trễ/nhiễu nhưng thiếu số liệu bình duyệt trên Android, cần quyền USB theo từng thiết bị, điện thoại phải cấp nguồn bus ⇒ khó sạc đồng thời, và cắm dây là điểm hỏng cơ học trong cứu hộ.
