# Trạm RescueMesh trên laptop

Trạm dùng Bluetooth của laptop để nghe quảng cáo BLE, kiểm tra chữ ký SOS,
bỏ gói trùng và lưu từng bản tin vào `results/station-events.jsonl`.

```bash
cd /home/noble-tran/AIforlife
python3 -m pip install -r station/requirements.txt
./station/run.sh
```

Trạm hiện là bộ thu và nhật ký phòng lab. Bản đồ, beacon/ACK ngược và khóa
sản xuất sẽ được làm sau khi kiểm tra được đường truyền hai chiều trên thiết bị
thật.

## Phần cứng máy thu — kinh nghiệm G0

Không phải adapter Bluetooth nào cũng dùng được. Trong phép đo 2026-09-29, laptop
XiaoXin 14 AHP9 (adapter Realtek `C0:35:32:40:77:30`, BlueZ + Bleak 3.0.2) quét
được thiết bị BLE khác nhưng **không hề liệt kê quảng bá legacy của Pixel 6 Pro**,
kể cả khi quét không filter bằng `bluetoothctl scan le`; `btmon` cũng bị từ chối
quyền. Cùng APK đó, chạy trạm trên **máy gaming thì nhận được SOS**.

Trước khi kết luận codec hay phía phát sai, hãy kiểm tra theo thứ tự:

1. `python3 station/diag.py 15` — quét không filter, in mọi manufacturer ID thấy được;
2. Nếu diag thấy thiết bị BLE khác nhưng không thấy `0xFFFF`, nghi ngờ adapter/driver;
3. Đổi sang adapter hoặc máy khác rồi lặp lại — đây là bước đã thông được đường thu.

Log kết quả nên lưu vào `results/station-<tên-máy>-<ngày>.txt` và giữ cả
`results/station-events.jsonl` làm bằng chứng thô.
