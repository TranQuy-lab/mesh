# RescueMesh v1.0 — nút mạng Android

Ứng dụng chạy dưới dạng foreground service và đồng thời:

- phát SOS v1 dài 24 byte trong manufacturer data `0xFFFF`; sequence và HMAC
  được cập nhật mỗi giây, khởi đầu bằng golden vector;
- quét BLE với filter manufacturer + protocol version, xác thực HMAC, bỏ gói
  trùng và chuyển tiếp gói mới về phía trạm;
- đăng ký accelerometer với chu kỳ yêu cầu 50 ms và batching tối đa 2 s;
- ghi một dòng trạng thái mỗi 10 s bằng tag `RescueMeshG0`.

`0xFFFF` chỉ dành cho thử nghiệm trong phòng. Không dùng mã này cho sản phẩm hoặc thử nghiệm công cộng.

## Build

SDK cục bộ được đặt ở `../.android-sdk`. Chạy:

```bash
./build.sh
```

APK đã ký debug được tạo tại `build/rescuemesh-g0.apk` và tự chép vào
`../releases/rescuemesh-g0.apk`.

Codec SOS Java dùng chung golden vector với Python. Kiểm tra độc lập:

```bash
./test-codec.sh
```

## Cài và chạy

```bash
adb install -r ../releases/rescuemesh-g0.apk
adb shell pm grant org.rescuemesh.g0 android.permission.BLUETOOTH_SCAN
adb shell pm grant org.rescuemesh.g0 android.permission.BLUETOOTH_ADVERTISE
adb shell pm grant org.rescuemesh.g0 android.permission.BLUETOOTH_CONNECT
adb shell pm grant org.rescuemesh.g0 android.permission.POST_NOTIFICATIONS
adb shell am start-foreground-service -n org.rescuemesh.g0/.ProbeService
adb logcat -s RescueMeshG0:I '*:S'
```

Chọn cấu hình G0-S (mặc định đều là `low_latency`):

```bash
adb shell am start-foreground-service \
  -n org.rescuemesh.g0/.ProbeService \
  --es advertise_mode balanced \
  --es scan_mode balanced
```

`balanced` tương ứng advertising interval 250 ms trên Pixel thử nghiệm; giá trị
thực phải lấy từ `dumpsys bluetooth_manager`, không suy từ tên enum.

Dừng phép đo nhưng giữ ứng dụng để dùng lại:

```bash
adb shell am stopservice org.rescuemesh.g0/.ProbeService
```

## Giới hạn hiện tại

- Callback `onStartSuccess` và `dumpsys bluetooth_manager` xác nhận controller đã nhận cấu hình phát, nhưng laptop hiện chưa giải mã được chiều Pixel → laptop.
- Chiều laptop → Pixel đã so khớp byte-for-byte. Unfiltered scan dừng khi màn hình tắt theo quy định Android; vì vậy đầu dò dùng `ScanFilter`.
- `sensor_hz` được tính từ timestamp sự kiện Android. Chu kỳ truyền vào `registerListener` chỉ là yêu cầu; phần cứng/hệ điều hành có thể chọn nhịp khác.
- `messages_issued` là số message ứng dụng đã giao cho controller, không phải bằng
  chứng mọi advertising event đã phát trên không khí.
- Đây vẫn là nguyên mẫu phòng lab: dùng khóa thử nghiệm chung, tọa độ mẫu và
  chưa có bản đồ hoặc beacon/ACK ngược từ trạm.
