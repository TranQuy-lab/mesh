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
