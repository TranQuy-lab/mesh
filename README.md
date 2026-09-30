# AIforlife — RescueMesh-LoRa

![Biểu tượng RescueMesh-AI](assets/rescuemesh-ai-icon.png)

Bộ tài liệu và mã tái lập cho đề tài **RescueMesh-LoRa**: mạng **mesh LoRa một
loại sóng duy nhất** ở băng 920–923 MHz cho vùng bão lũ mất sóng. **Điện thoại của
người dân là đầu cuối** — tự phát hiện ngã/bất động rồi gửi SOS qua một **nút cầu
LoRa nhỏ đeo kèm** (link cá nhân BLE 1–2 m), từ đó trở đi mạng thuần LoRa, chuyển
tiếp có kiểm soát về trạm cứu hộ.

> ## ⚠️ Chuyển hướng 2026-10-01
>
> Bản **BLE** trước đây đã bị loại bỏ vì **tầm gửi gói quá ngắn** ở vai trò *mạng
> chuyển tiếp*. Dự án nay dùng **một loại sóng duy nhất là LoRa cho mạng cứu hộ**;
> **điện thoại vẫn là đầu cuối** vì ai cũng đã có sẵn (giải quyết bài toán cấp phát),
> và nhồi chip LoRa vào điện thoại là việc không khả thi trong phạm vi đề tài.
>
> Ba hệ quả: (i) mỗi người mang thêm một **nút cầu LoRa** nhỏ — chỉ MCU + chip LoRa
> + pin, vì GNSS/IMU/màn hình đã có trong điện thoại; (ii) **BLE chỉ còn là link cá
> nhân 1–2 m** giữa điện thoại và nút cầu của chính nó, không tham gia chuyển tiếp,
> nên lý do "tầm ngắn" không còn áp dụng; (iii) tài nguyên khan hiếm của mạng đổi từ
> **byte** sang **airtime** trên một kênh dùng chung.

## Đọc theo thứ tự

| # | Tệp | Nội dung |
|---|---|---|
| 1 | [ke-hoach-nghien-cuu-rescuemesh-lora.md](ke-hoach-nghien-cuu-rescuemesh-lora.md) | **Kế hoạch hiện hành:** chuyển hướng, RQ1–RQ5, giả thuyết H1–H5 có đối thủ, kinh tế airtime, đặc tả khung, WP6–WP12, cổng G6–G11, lộ trình 14 tuần, BOM, pháp lý tần số |
| 2 | [thiet-ke-he-thong-lora-v2.md](thiet-ke-he-thong-lora-v2.md) | **Thiết kế v2.0:** kiến trúc bốn vai trò, máy trạng thái nút, ba chính sách ngủ/nghe, đặc tả khung byte-by-byte, định tuyến một kênh, an ninh, bảng tham số có nhãn nguồn gốc |
| 3 | [cau-truc-de-tai-rescuemesh-lora.md](cau-truc-de-tai-rescuemesh-lora.md) | **Cấu trúc đề tài:** tên đề tài, sơ đồ trụ cột, chương mục chi tiết, danh mục bảng/hình, bản đồ RQ → bằng chứng → cổng, kế hoạch viết |
| 4 | [xac-minh-nguon-lora-va-quyet-dinh-song.md](xac-minh-nguon-lora-va-quyet-dinh-song.md) | **Nhật ký quyết định & sổ nguồn đã xác minh:** vì sao bỏ BLE, vì sao chọn LoRa, vì sao loại WiFi mesh / WiFi HaLow / vệ tinh, kèm DOI đã đối chiếu và danh sách số liệu **bị cấm dùng** |
| 5 | [nghien-cuu-ve-tinh-rescuemesh-ai.md](nghien-cuu-ve-tinh-rescuemesh-ai.md) | Phụ lục nghiên cứu vệ tinh (76 bằng chứng): Starlink tại Việt Nam, spec sheet, 3GPP NTN, rain fade nhiệt đới |
| 6 | [ket-qua-tong-hop-lora-mesh-2026-09-30.md](ket-qua-tong-hop-lora-mesh-2026-09-30.md) | Phụ lục định tuyến/DTN/hiệu chuẩn (đã xác minh DOI): dung lượng LoRaWAN có đo, DTN-over-LoRa thực địa, data mule, cạm bẫy mô phỏng |
| 7 | [xac-minh-nguon-va-tai-lieu-tham-khao.md](xac-minh-nguon-va-tai-lieu-tham-khao.md) | Sổ xác minh nguồn của giai đoạn BLE (còn hiệu lực về **phương pháp** xác minh) |
| 8 | [research_tools/README.md](research_tools/README.md) | Bộ công cụ tra cứu tái sử dụng (OpenAlex, Crossref, xác minh DOI) — kèm ghi chú rằng `web_search` của phiên bị lỗi 401 và cách đi vòng |

### Tài liệu lịch sử (hướng BLE đã loại)

| Tệp | Vì sao còn giữ |
|---|---|
| [ke-hoach-nghien-cuu-rescuemesh-ai.md](ke-hoach-nghien-cuu-rescuemesh-ai.md) | Nguồn gốc các quyết định phương pháp luận, thang bằng chứng, thiết kế phát hiện ngã |
| [thiet-ke-he-thong-chi-tiet.md](thiet-ke-he-thong-chi-tiet.md) | Thiết kế T1→T2→T3 và ngân sách khoá được kế thừa |
| [cau-truc-de-tai-rescuemesh-ai.md](cau-truc-de-tai-rescuemesh-ai.md) | Cách đặt tên đề tài và bản đồ RQ → chương |
| [ket-qua-ra-soat-va-nghien-cuu-ban-dau.md](ket-qua-ra-soat-va-nghien-cuu-ban-dau.md) · [nghien-cuu-ble-mesh-va-ke-hoach-g0.md](nghien-cuu-ble-mesh-va-ke-hoach-g0.md) | Kết quả `ĐO` trên Pixel 6 Pro và lịch sàng lọc G0 |
| [nguon-hoc-tap-va-tai-su-dung.md](nguon-hoc-tap-va-tai-su-dung.md) | Bản đồ nguồn để dùng và 10 quy tắc tối ưu |

## Mã nguồn

| Tệp | Nội dung | Trạng thái |
|---|---|---|
| [rescuemesh/lora.py](rescuemesh/lora.py) | Vật lý LoRa: airtime (công thức Semtech), bitrate, suy hao, tầm xa theo mô hình, **sức chứa gateway** (mô hình tách khung SOS/beacon), hằng số QCVN | 32/32 test xanh |
| [rescuemesh/test_lora.py](rescuemesh/test_lora.py) | Kiểm thử tính chất, ghìm hồi quy giá trị đã biết, đối chiếu công thức độc lập | — |
| [rescuemesh/node_power.py](rescuemesh/node_power.py) | Ngân sách năng lượng nút: dòng từng khối, tự xả pin, duty cycle, tuổi thọ, **chi phí mỗi SOS giao được** | 19/19 test xanh |
| [rescuemesh/test_node_power.py](rescuemesh/test_node_power.py) | Kiểm thử kế toán năng lượng và các bất biến | — |
| [rescuemesh/packets_lora.py](rescuemesh/packets_lora.py) | Codec **khung v2.0**: SOS 36 B, HEARTBEAT 14 B, BEACON 18 B, ACK 12 B; HMAC cắt ngắn; token ACK 24 bit; bảng airtime và va chạm token | 36/36 test xanh |
| [rescuemesh/test_packets_lora.py](rescuemesh/test_packets_lora.py) | Round-trip, tamper, biên, fuzz, Monte Carlo va chạm token 16/24 bit | — |
| [rescuemesh/sim_lora.py](rescuemesh/sim_lora.py) | Simulator mesh LoRa: thời gian liên tục, airtime, collision, capture, duty cycle, 5 thuật toán, cold/warm start, courier | 28/28 test xanh |
| [rescuemesh/test_sim_lora.py](rescuemesh/test_sim_lora.py) | Kiểm soát âm bắt buộc, tái lập, kế toán airtime | — |
| [rescuemesh/analyze_sim_lora.py](rescuemesh/analyze_sim_lora.py) | Phân tích **ghép cặp theo seed** cho H2 (thuật toán nào thắng ở mức tải nào) → `results/sim-lora-h2-paired.csv` | — |
| [rescuemesh/packets.py](rescuemesh/packets.py) | Codec BLE v1 (24 B) — **lịch sử**; helper mã hoá toạ độ 24 bit vẫn được v2.0 tái dùng | 15/15 test xanh |
| [rescuemesh/sim_v2.py](rescuemesh/sim_v2.py) · [run_wp3_matrix.py](rescuemesh/run_wp3_matrix.py) · [run_h3_experiment.py](rescuemesh/run_h3_experiment.py) · [run_r2a_beacon_sweep.py](rescuemesh/run_r2a_beacon_sweep.py) | Simulator và thí nghiệm BLE — **lịch sử**; kết quả `SIM` cũ **không được trích** cho hướng LoRa | — |
| [rescuemesh/generate_g0_schedule.py](rescuemesh/generate_g0_schedule.py) | Sinh lịch factorial có block và random hoá (tái dùng cho sàng lọc G0-S mới) | 4/4 test xanh |
| [results/](results/) | Kết quả `SIM`/`ĐO` kèm seed; mọi bảng mô phỏng phải có nhãn `evidence=SIM` | — |
| [android-g0/](android-g0/) | APK Android — **được kế thừa**: đọc IMU 20 Hz, foreground service, UI (đã chạy trên Pixel 6 Pro và Redmi). Phần BLE advertising/scanning trong vai trò *mạng* là lịch sử; app nay gửi SOS sang nút cầu qua link cá nhân | 4/4 test codec |
| [station/](station/) · [releases/](releases/) | Trạm thu BLE và APK phát hành — **lịch sử**; trạm sẽ được thay bằng cầu nối gateway LoRa | — |
| [assets/rescuemesh-ai-icon.png](assets/rescuemesh-ai-icon.png) | Biểu tượng nhận diện của dự án | — |

Chạy kiểm thử (không cần thư viện ngoài):

```bash
cd rescuemesh
python3 test_lora.py            # 31/31
python3 test_node_power.py      # 19/19
python3 test_packets_lora.py    # 36/36
python3 test_packets.py         # 15/15 (codec BLE lịch sử)

python3 lora.py                 # bảng đánh đổi SF + sức chứa gateway
python3 node_power.py           # tuổi thọ pin và chi phí mỗi SOS
python3 packets_lora.py         # bảng khung + airtime + va chạm token
```

## Trạng thái

- **Cổng G6 (khung v2.0): ĐẠT.** Codec 36/36 test xanh; mọi khung đúng kích thước;
  tamper bị chặn; đã có bảng airtime và bảng va chạm token.
- **Mã thiết kế tái lập được:** `lora.py` 32/32 và `node_power.py` 19/19. Ba con số
  thiết kế chốt: SOS 36 B ở SF9 tốn **≈ 267 ms** airtime; một gateway đơn kênh ở
  SF9 phục vụ **≈ 242 nút** (beacon 60 s) tới **≈ 952 nút** (beacon 300 s) ở mức
  dùng 80 % kênh; nút cầu ngủ theo lịch sống **≈ 765 ngày** so với **≈ 9,6 ngày** khi
  nghe kênh liên tục.
- **Phát hiện định hình đề tài:** beacon chiếm **73–93 %** airtime của mỗi nút
  (SF9/beacon 60 s: **93,3 %**) — điều khiển, không phải dữ liệu, là chi phí trội.
  Đây là giả thuyết H3 và là dự đoán có thể bị bác ở WP9.
- **Kết quả `SIM` đầu tiên (chưa hiệu chuẩn, không được trích như kết quả):**
  2.400 lượt mô phỏng, 5 thuật toán × 3 mật độ × 2 tải × 2 SF × cold/warm, 20 seed
  mỗi ô. Ghép cặp theo seed cho thấy **gradient thua flooding về PDR ở cả hai mức
  tải** (−0,141 và −0,126) nhưng chỉ tốn ≈ **8 lần phát** mỗi SOS giao được thay vì
  ≈ 60; **`store_carry_forward` vừa giao nhiều hơn vừa tốn ít hơn flooding**. Nghĩa
  là đánh đổi thật trên LoRa là **PDR ↔ airtime**, không phải "gradient thắng khi
  tải cao" như quan sát trên BLE. Xem §7.5 của kế hoạch và
  [results/sim-lora-h2-paired.csv](results/sim-lora-h2-paired.csv).
- **Chưa có kết quả `ĐO` nào.** Mọi số hiện tại là `SUY` (từ mô hình) hoặc `SIM`
  (từ mô phỏng chưa hiệu chuẩn). Không được viết như kết quả thực nghiệm.
- **Pháp lý và thông số đã xác minh từ bản gốc:** băng **920–923 MHz được miễn giấy
  phép sử dụng tần số** (Thông tư 08/2021/TT-BTTTT); QCVN 122:2020/BTTTT giới hạn
  **14 dBm e.r.p.** và **duty cycle 1 % cho đầu cuối / 10 % cho gateway** (đọc bản
  công báo gốc). **Hệ quả:** board Meshtastic/Heltec (+20/+22 dBm) **vượt giới hạn**;
  và cấu hình **SF12 + beacon 60 s (2,36 %) không hợp quy**. Bảng độ nhạy và dòng
  tiêu thụ trong mã nay lấy từ **datasheet SX1276** (`NC`) thay cho `GIẢ ĐỊNH`.
- **Ràng buộc quy mô:** token ACK 24 bit chỉ đủ tới khoảng **1.000 nút** (ở 10.000
  nút xác suất khớp sai ≈ 94 %); muốn lớn hơn phải nâng lên 32 bit.

## Chạy bản trình diễn

Bản trình diễn BLE (hai điện thoại + laptop) thuộc hướng **lịch sử**; xem
[android-g0/README.md](android-g0/README.md) và [station/README.md](station/README.md)
nếu cần tái hiện kết quả `ĐO` cũ. Bản trình diễn LoRa sẽ được bổ sung ở WP10–WP11
sau khi có phần cứng và sau khi qua cổng hiệu chuẩn G9.
