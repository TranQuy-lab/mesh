# AIforlife — RescueMesh-AI

![Biểu tượng RescueMesh-AI](assets/rescuemesh-ai-icon.png)

Bộ tài liệu kế hoạch cho đề tài **RescueMesh-AI**: mạng liên lạc cứu hộ BLE ngoại tuyến cho vùng bão lũ mất sóng, có managed flooding/gradient/store-carry-forward và AI hỗ trợ tạo SOS khi người dùng không thể thao tác.

## Đọc theo thứ tự

| # | Tệp | Nội dung |
|---|---|---|
| 1 | [ke-hoach-nghien-cuu-rescuemesh-ai.md](ke-hoach-nghien-cuu-rescuemesh-ai.md) | Kế hoạch: định vị, khoảng trống, RQ/giả thuyết, phạm vi, sửa lỗi gói tin, work package, thiết kế thực nghiệm, thống kê, cổng quyết định, rủi ro, đạo đức |
| 2 | [cau-truc-de-tai-rescuemesh-ai.md](cau-truc-de-tai-rescuemesh-ai.md) | Cấu trúc chủ đề chốt: tên đề tài, sơ đồ trụ cột, cấu trúc chương mục chi tiết, danh mục bảng/hình, bản đồ RQ → bằng chứng |
| 3 | [thiet-ke-he-thong-chi-tiet.md](thiet-ke-he-thong-chi-tiet.md) | **Đặc tả thiết kế:** kiến trúc 3 vai trò, gói tin byte-by-byte (SOS/HEARTBEAT/BEACON), thuật toán T1–T3, gradient/Trickle/ACK, trạng thái máy, bảng tham số có nhãn nguồn gốc (`NC`/`TK`/`ĐO`), phép thử bác bỏ |
| 4 | [xac-minh-nguon-va-tai-lieu-tham-khao.md](xac-minh-nguon-va-tai-lieu-tham-khao.md) | Xác minh từng nguồn trong đoạn hội thoại do AI tổng hợp + thư mục tài liệu tham khảo đã kiểm |
| 5 | [nguon-hoc-tap-va-tai-su-dung.md](nguon-hoc-tap-va-tai-su-dung.md) | Bản đồ nguồn **để dùng**: tái sử dụng repo nào (kèm giấy phép), đọc gì theo thứ tự nào, 10 quy tắc tối ưu/hiệu quả, lộ trình "học để làm" 10 ngày, bản đồ khả năng truy cập mạng |
| 6 | [verify/rescuemesh-source-verification.md](verify/rescuemesh-source-verification.md) | Báo cáo xác minh gốc (tiếng Anh) kèm bằng chứng thô: lệnh truy vấn GitHub API, DOI, phán quyết từng mục |

**Kết quả xác minh đáng chú ý:** 5/6 nguồn trong đoạn hội thoại tồn tại thật nhưng 4/6 bị mô tả sai; bài báo ResearchGate được nêu là "nghiên cứu bình duyệt" thực chất là bài trên tạp chí thu tiền để đăng, **không có đánh giá**, và chứa **trích dẫn bịa** — đã loại khỏi mọi bản viết. Xem §2 của tài liệu số 3.

## Mã nguồn

| Tệp | Nội dung |
|---|---|
| [rescuemesh/packets.py](rescuemesh/packets.py) | Codec v1 cho BLE legacy advertising: SOS 24 B, ID 32 bit, HMAC 64 bit, ACK token 32 bit |
| [rescuemesh/test_packets.py](rescuemesh/test_packets.py) | 15 test codec (golden vectors, round-trip, HMAC/tamper, biên 24 B, fuzz 500 mẫu) |
| [rescuemesh/sim.py](rescuemesh/sim.py) | Simulator rời rạc tối thiểu cho flood/Trickle/gradient; hiện chỉ là `SIM-SMOKE` chưa hiệu chuẩn, chưa mô phỏng collision hoặc tải nhiều SOS |
| [rescuemesh/test_sim.py](rescuemesh/test_sim.py) | 5 kiểm soát âm/tái lập cho simulator |
| [rescuemesh/generate_g0_schedule.py](rescuemesh/generate_g0_schedule.py) | Sinh lịch factorial G0-S có block và random hóa |
| [rescuemesh/test_g0_schedule.py](rescuemesh/test_g0_schedule.py) | 4 kiểm thử cân bằng, full factorial và tái lập lịch G0-S |
| [results/sim-smoke.csv](results/sim-smoke.csv) | 270 lượt smoke test, không dùng để kết luận hiệu năng thực |
| [android-g0/](android-g0/) | APK nút mạng Android: phát SOS, quét BLE và chuyển tiếp gói mới |
| [station/](station/) | Trạm thu trên laptop: nhận BLE, kiểm tra HMAC, chống trùng và lưu SOS |
| [releases/rescuemesh-g0.apk](releases/rescuemesh-g0.apk) | APK cài trực tiếp lên điện thoại |
| [assets/rescuemesh-ai-icon.png](assets/rescuemesh-ai-icon.png) | Biểu tượng nhận diện của dự án |
| [android-g0/src/org/rescuemesh/g0/SosCodec.java](android-g0/src/org/rescuemesh/g0/SosCodec.java) | Codec SOS Java đối chiếu byte-for-byte với golden vector Python |
| [ket-qua-ra-soat-va-nghien-cuu-ban-dau.md](ket-qua-ra-soat-va-nghien-cuu-ban-dau.md) | Phán quyết thiết kế, SIM-SMOKE và kết quả G0 trên Pixel 6 Pro |
| [nghien-cuu-ble-mesh-va-ke-hoach-g0.md](nghien-cuu-ble-mesh-va-ke-hoach-g0.md) | Bằng chứng BLE/DTN trên smartphone và factorial screening G0-S |
| [results/g0-screening-schedule.csv](results/g0-screening-schedule.csv) | Lịch 144 phiên G0-S được block và random hóa, seed cố định |

Chạy kiểm thử:

```bash
cd rescuemesh && python3 test_packets.py     # không cần thư viện ngoài
# hoặc: python3 -m pytest test_packets.py -q
python3 test_g0_schedule.py
cd .. && .venv/bin/python rescuemesh/test_sim.py
```

In bảng kích thước gói, đụng độ ID và độ phân giải toạ độ:

```bash
cd rescuemesh && python3 packets.py
```

## Trạng thái

- Cổng **G0 (khóa phạm vi)**: biến thể byte mặc định đã chốt; yêu cầu đạo đức cho thu dữ liệu người tham gia vẫn phải xác nhận trước WP3.
- Cổng **G1 (codec)**: Python 15/15 và Java 4/4 test xanh; Pixel/API 36 tự kiểm tra `golden=true, verify=true`. Kotlin chỉ còn là lựa chọn ngôn ngữ ứng dụng, không còn là blocker interoperability JVM.
- Cổng **G0 (BLE advertising)**: đạt một phần trên Pixel 6 Pro — controller giữ legacy advertising khi tắt màn hình và filtered scan nhận đúng 24 byte từ laptop; còn thiếu xác nhận chiều Pixel → máy thu, đa model và đo pin khi rút USB.
- **Khảo sát tài liệu**: đã xong cho phần phát hiện ngã (bằng chứng mạnh); phần BLE mesh/DTN cho thảm họa **chưa xác minh được số liệu** → phải tự đo, không được trích (xem tài liệu số 3, §4.4).

## Chạy bản trình diễn với hai điện thoại và laptop

1. Trên laptop cài thư viện Bluetooth một lần: `python3 -m pip install -r station/requirements.txt`.
2. Cắm hoặc bật Bluetooth trên laptop rồi chạy `./station/run.sh`. Cửa sổ này là trạm; SOS hợp lệ được in ra và lưu vào `results/station-events.jsonl`.
3. Cài file [rescuemesh-g0.apk](releases/rescuemesh-g0.apk) lên từng điện thoại, mở biểu tượng **RescueMesh** và cấp các quyền Bluetooth/thông báo.
4. Sau khi cấp quyền, ứng dụng tự chạy: một máy phát SOS, cả hai máy đều quét; gói mới được chuyển tiếp với số bước tăng lên và thời gian sống giảm đi. Nút **Bật nút mạng** chỉ cần dùng để bật lại sau khi đã tắt.

Bản hiện tại dùng khóa thử nghiệm có sẵn trong mã để trình diễn trong phòng lab. Khi chuyển sang triển khai thật, thay khóa bằng khóa riêng của mạng cứu hộ.
- WP2–WP5: chưa bắt đầu. Mọi con số trong tài liệu hiện là **phân tích thiết kế**, chưa phải kết quả thực nghiệm.
