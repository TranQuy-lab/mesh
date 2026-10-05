# AIforlife — RescueSOS-Phone

![Biểu tượng RescueMesh-AI](assets/rescuemesh-ai-icon.png)

Bộ tài liệu và mã tái lập cho đề tài **RescueSOS-Phone**: mạng SOS chạy **hoàn toàn
trên điện thoại thường** cho vùng bão lũ mất sóng — IMU tự phát hiện ngã/bất động,
tin SOS nhảy BLE từ điện thoại này sang điện thoại kia và **đi theo người di chuyển**
(lưu–mang–tiếp) tới điện thoại đầu tiên bắt lại được sóng, tự đẩy lên server bản đồ
(kèm SMS dự phòng) cho Ban chỉ huy PCTT/đội cứu hộ; cảnh báo chảy ngược lại qua đúng
con đường đó. **0 ₫ phần cứng.**

> ## ⚠️ Chuyển hướng 2026-10-05 (bản chốt D13)
>
> Ba vòng chốt trong cùng ngày: (1) không đủ kinh phí LoRa → hạ LoRa thành hướng dài
> hạn, đóng băng ở cổng G6, mọi kết quả giữ nguyên giá trị; (2) cảm biến CSI và chuỗi
> ESP-NOW bị phản biện (nhiễu thiên tai; mạch ngoài không hợp lý cho vùng cô lập) →
> hạ xuống tuỳ chọn; (3) chốt cuối: **mạng điện thoại thuần BLE, SOS đi theo người**.
> **Kế hoạch hiện hành:** [ke-hoach-rescue-sos-phone-2026-10-05.md](ke-hoach-rescue-sos-phone-2026-10-05.md).
> H7 (phát hiện chìm bằng barometer + IMU) **đã vào đề tài ở mức demo** trên máy có
> barometer (Pixel 6 — có, GSMArena 2026-10-05); hằng số vẫn `TK` chờ thí nghiệm bồn
> nước: [nghien-cuu-h7-2026-10-05.md](nghien-cuu-h7-2026-10-05.md).

## Đọc theo thứ tự

| # | Tệp | Nội dung |
|---|---|---|
| 0 | [ke-hoach-rescue-sos-phone-2026-10-05.md](ke-hoach-rescue-sos-phone-2026-10-05.md) | **⚠️ ĐỌC ĐẦU TIÊN — Kế hoạch hiện hành (chốt 2026-10-05):** RescueSOS-Phone — **SOS đi theo người trên mạng điện thoại thuần BLE, 0 ₫ phần cứng**: IMU phát hiện ngã → tin nhảy BLE theo người đi lại (lưu–mang–tiếp) → điện thoại đầu tiên có sóng đẩy lên server bản đồ + SMS → Ban chỉ huy xem web → cảnh báo tràn ngược. Sàng lọc ưu tiên thuật toán/mã có sẵn (bitchat, The ONE, Briar, Reticulum, Nordic); AI chỉ vào sau khi chuỗi đạt cổng; KPI hiệu quả cuối đặt trước ở §8 |
| 0b | [nghien-cuu-chuyen-huong-wifi-ve-tinh-2026-10-05.md](nghien-cuu-chuyen-huong-wifi-ve-tinh-2026-10-05.md) | Nhật ký chuyển hướng (bản 2): vì sao bỏ LoRa/CSI/ESP-NOW làm đường chuẩn, bằng chứng đã xác minh — nguồn của kế hoạch hiện hành |
| 1 | [ke-hoach-nghien-cuu-rescuemesh-lora.md](ke-hoach-nghien-cuu-rescuemesh-lora.md) | **Kế hoạch LoRa — ĐÓNG BĂNG ở cổng G6 (hướng dài hạn khi có kinh phí):** RQ1–RQ5, giả thuyết H1–H5 có đối thủ, kinh tế airtime, đặc tả khung, WP6–WP12, cổng G6–G11, BOM, pháp lý tần số. Kế hoạch hiện hành kế thừa nguyên trạng RQ1/T1–T3 và §10.1 (kho dữ liệu ngã) từ đây |
| 2 | [thiet-ke-he-thong-lora-v2.md](thiet-ke-he-thong-lora-v2.md) | **Thiết kế v2.0:** kiến trúc bốn vai trò, máy trạng thái nút, ba chính sách ngủ/nghe, đặc tả khung byte-by-byte, định tuyến một kênh, an ninh, bảng tham số có nhãn nguồn gốc |
| 3 | [cau-truc-de-tai-rescuemesh-lora.md](cau-truc-de-tai-rescuemesh-lora.md) | **Cấu trúc đề tài:** tên đề tài, sơ đồ trụ cột, chương mục chi tiết, danh mục bảng/hình, bản đồ RQ → bằng chứng → cổng, kế hoạch viết |
| 4 | [xac-minh-nguon-lora-va-quyet-dinh-song.md](xac-minh-nguon-lora-va-quyet-dinh-song.md) | **Nhật ký quyết định & sổ nguồn đã xác minh:** vì sao bỏ BLE, vì sao chọn LoRa, vì sao loại WiFi mesh / WiFi HaLow / vệ tinh, kèm DOI đã đối chiếu và danh sách số liệu **bị cấm dùng** |
| 5 | [nghien-cuu-ve-tinh-rescuemesh-ai.md](nghien-cuu-ve-tinh-rescuemesh-ai.md) | Phụ lục nghiên cứu vệ tinh (76 bằng chứng): Starlink tại Việt Nam, spec sheet, 3GPP NTN, rain fade nhiệt đới |
| 6 | [ket-qua-tong-hop-lora-mesh-2026-09-30.md](ket-qua-tong-hop-lora-mesh-2026-09-30.md) | Phụ lục định tuyến/DTN/hiệu chuẩn (đã xác minh DOI): dung lượng LoRaWAN có đo, DTN-over-LoRa thực địa, data mule, cạm bẫy mô phỏng |
| 7 | [nghien-cuu-beacon-suc-chua-2026-10-01.md](nghien-cuu-beacon-suc-chua-2026-10-01.md) | Phụ lục beacon & sức chứa: chu kỳ quảng bá thật (Meshtastic 3 h, MeshCore 12 h), Trickle RFC 6206, bản Bor đã sửa, hiệu chuẩn LoRaWANSim, đo năng lượng relay |
| 8 | [nghien-cuu-link-ca-nhan-ble-2026-10-01.md](nghien-cuu-link-ca-nhan-ble-2026-10-01.md) | Phụ lục link cá nhân BLE: connection interval AOSP, ràng buộc chạy nền định lượng, số đo độ trễ, khuyến nghị PHY 2M |
| 9 | [nghien-cuu-chuan-khan-cap-2026-10-01.md](nghien-cuu-chuan-khan-cap-2026-10-01.md) | Phụ lục chuẩn khẩn cấp: CAP v1.2, trường tối thiểu, 3GPP TS 23.032 xác nhận 24 bit/trục, khuyến nghị khung v2.1 |
| 10 | [nghien-cuu-du-lieu-nga-2026-10-01.md](nghien-cuu-du-lieu-nga-2026-10-01.md) | Phụ lục dữ liệu phát hiện ngã: DOI đúng của 9 kho, giấy phép, tầm đo ±2g vs ±16g, LOSO, số liệu ngã thực |
| 11 | [nghien-cuu-phap-ly-vn-2026-10-01.md](nghien-cuu-phap-ly-vn-2026-10-01.md) | Phụ lục pháp lý VN: hai băng có điều kiện giống hệt, không QCVN cho 433, Luật Viễn thông 19.5, **Thông tư 14/2025/TT-BKHCN**, số liệu bão lũ đã mở toàn văn |
| 12 | [xac-minh-nguon-va-tai-lieu-tham-khao.md](xac-minh-nguon-va-tai-lieu-tham-khao.md) | Sổ xác minh nguồn của giai đoạn BLE (còn hiệu lực về **phương pháp** xác minh) |
| 13 | [research_tools/README.md](research_tools/README.md) | Bộ công cụ tra cứu tái sử dụng (OpenAlex, Crossref, xác minh DOI) — kèm ghi chú rằng `web_search` của phiên bị lỗi 401 và cách đi vòng |
| 14 | [nghien-cuu-h7-2026-10-05.md](nghien-cuu-h7-2026-10-05.md) | **H7 chìm/bị cuốn — đã vào đề tài:** nguyên lý ~0,981 hPa/cm nước, detector + 8/8 test, máy tham chiếu Pixel 6 (barometer xác minh), quy trình thí nghiệm bồn nước |
| 15 | [ket-qua-chuoi-rescue-sos-phone-2026-10-05.md](ket-qua-chuoi-rescue-sos-phone-2026-10-05.md) | **Kết quả chuỗi đầu-cuối:** trạng thái từng khâu ①–⑤ (app + mesh + cổng ra + server + bản đồ/la bàn), RQ1 LOSO, H7, các việc `CẦN TAY NGƯỜI` |

### Tài liệu lịch sử

Ngày 2026-10-05 đã **loại khỏi working tree** các tài liệu thời BLE bị thay thế hoàn
toàn: kế hoạch BLE, cấu trúc đề tài BLE, lịch sàng lọc G0, bản đồ nguồn học tập, sổ
xác minh giai đoạn BLE, và `ccsds.html` — **khôi phục được qua lịch sử git**. Còn giữ:

| Tệp | Vì sao còn giữ |
|---|---|
| [thiet-ke-he-thong-chi-tiet.md](thiet-ke-he-thong-chi-tiet.md) | Thiết kế T1→T2→T3 và ngân sách khoá được kế thừa ở WP1 |
| [ket-qua-ra-soat-va-nghien-cuu-ban-dau.md](ket-qua-ra-soat-va-nghien-cuu-ban-dau.md) | Kết quả `ĐO` BLE thật trên Pixel 6 Pro và Redmi — bằng chứng nền cho hướng điện thoại |

## Mã nguồn

| Tệp | Nội dung | Trạng thái |
|---|---|---|
| [rescuemesh/lora.py](rescuemesh/lora.py) | Vật lý LoRa: airtime (công thức Semtech), bitrate, suy hao, tầm xa theo mô hình, **sức chứa gateway** (mô hình tách khung SOS/beacon), hằng số QCVN | 32/32 test xanh |
| [rescuemesh/test_lora.py](rescuemesh/test_lora.py) | Kiểm thử tính chất, ghìm hồi quy giá trị đã biết, đối chiếu công thức độc lập | — |
| [rescuemesh/node_power.py](rescuemesh/node_power.py) | Ngân sách năng lượng nút: dòng từng khối, tự xả pin, duty cycle, tuổi thọ, **chi phí mỗi SOS giao được** | 19/19 test xanh |
| [rescuemesh/test_node_power.py](rescuemesh/test_node_power.py) | Kiểm thử kế toán năng lượng và các bất biến | — |
| [rescuemesh/packets_lora.py](rescuemesh/packets_lora.py) | Codec khung **v2.0** (SOS 36 B, HEARTBEAT 14 B, BEACON 18 B, ACK 12 B) **và v2.1 tương thích ngược** (2 byte cuối mang trường ánh xạ CAP + lớp độ chính xác vị trí, version = 3); HMAC cắt ngắn; token ACK 24 bit | 43/43 test xanh |
| [rescuemesh/test_packets_lora.py](rescuemesh/test_packets_lora.py) | Round-trip, tamper, biên, fuzz, Monte Carlo va chạm token 16/24 bit | — |
| [rescuemesh/sim_lora.py](rescuemesh/sim_lora.py) | Simulator mesh LoRa: thời gian liên tục, airtime, collision, capture, duty cycle, 5 thuật toán, cold/warm start, courier, **3 chế độ mặt phẳng điều khiển**, **3 chính sách nghe**, **mô hình link cá nhân** | 41/41 test xanh |
| [rescuemesh/test_sim_lora.py](rescuemesh/test_sim_lora.py) | Kiểm soát âm bắt buộc, tái lập, kế toán airtime, và test cho các tính năng v2.1 | — |
| [rescuemesh/run_lora_experiments.py](rescuemesh/run_lora_experiments.py) | Năm thí nghiệm trọng tâm E1/E1b (H3-R3b, H5), E2/E2b (H6), E3 (RQ6) → `results/sim-lora-e*.csv` | — |
| [rescuemesh/analyze_sim_lora.py](rescuemesh/analyze_sim_lora.py) | Phân tích **ghép cặp theo seed**, **đường Pareto**, và **bảng theo ô** (chỗ sửa lại H2) | — |
| [rescuemesh/reproduce_all.sh](rescuemesh/reproduce_all.sh) | **Một lệnh tái lập (cổng G11):** mọi test + mọi bảng + mọi CSV + `results/REPRODUCE-REPORT.md` kèm hash | — |
| [rescuemesh/packets.py](rescuemesh/packets.py) | Codec BLE v1 (24 B) — **lịch sử**; helper mã hoá toạ độ 24 bit vẫn được v2.0 tái dùng | 15/15 test xanh |
| [rescuemesh/sim_v2.py](rescuemesh/sim_v2.py) · [run_wp3_matrix.py](rescuemesh/run_wp3_matrix.py) · [run_h3_experiment.py](rescuemesh/run_h3_experiment.py) · [run_r2a_beacon_sweep.py](rescuemesh/run_r2a_beacon_sweep.py) | Simulator và thí nghiệm BLE — **lịch sử**; kết quả `SIM` cũ **không được trích** cho hướng LoRa | — |
| [rescuemesh/generate_g0_schedule.py](rescuemesh/generate_g0_schedule.py) | Sinh lịch factorial có block và random hoá (tái dùng cho sàng lọc G0-S mới) | 4/4 test xanh |
| [results/](results/) | Kết quả `SIM`/`ĐO` kèm seed; mọi bảng mô phỏng phải có nhãn `evidence=SIM` | — |
| [android-g0/](android-g0/) | **App node SOS đầy đủ (kế hoạch hiện hành):** phát hiện ngã T1 (rơi tự do → va đập → bất động) + H7 barometer → SOS tự động có đếm ngược 30 s; GNSS thật ghi toạ độ vào khung; BLE quét + quảng bá nhiều khung, hàng đợi bền qua restart; cổng ra HTTP + SMS; la bàn chỉ hướng tới SOS đã nhận | 4/4 codec + 6/6 detector self-test; APK build đạt; **chạy thật trên Pixel 6 Pro (`ĐO` 2026-10-05)** |
| [console/](console/) | **App Console phía cứu hộ (Expo SDK 57 + React Native):** bản đồ MapLibre OSM không cần API key, la bàn chỉ đường, danh sách SOS, cấu hình server — chỉ đọc `/api/sos`, tách vai trò khỏi app node để giữ service BLE nền bền | tsc sạch; theo skill expo-ui/expo-design-system |
| [station/](station/) · [releases/](releases/) | Trạm/server khâu ④⑤: `server.py` — nhận SOS qua HTTP (app đẩy) + nghe BLE trực tiếp, `/map` bản đồ Leaflet + la bàn cho đội cứu hộ; APK phát hành | `ĐO`: POST/GET/map đã kiểm curl |
| [assets/rescuemesh-ai-icon.png](assets/rescuemesh-ai-icon.png) | Biểu tượng nhận diện của dự án | — |

Chạy kiểm thử (không cần thư viện ngoài):

```bash
cd rescuemesh
./reproduce_all.sh              # MỘT lệnh: mọi test + mọi bảng + mọi CSV + báo cáo hash

python3 test_lora.py            # 32/32
python3 test_node_power.py      # 19/19
python3 test_packets_lora.py    # 43/43 (gồm khung v2.1 ánh xạ CAP)
python3 test_sim_lora.py        # 41/41 (gồm 3 chế độ điều khiển, 3 chính sách nghe, link cá nhân)
python3 test_packets.py         # 15/15 (codec BLE lịch sử)

python3 lora.py                 # bảng đánh đổi SF + sức chứa gateway
python3 node_power.py           # tuổi thọ pin và chi phí mỗi SOS
python3 packets_lora.py         # bảng khung + airtime + va chạm token
python3 sim_lora.py             # ma trận chính
python3 run_lora_experiments.py all   # E1/E1b/E2/E2b/E3
python3 analyze_sim_lora.py     # ghép cặp + Pareto + theo ô
```

## Trạng thái

- **Cổng G6 (khung v2.0 **và v2.1**): ĐẠT.** Codec **43/43 test xanh**; mọi khung đúng
  kích thước; tamper bị chặn; đã có bảng airtime và bảng va chạm token; **v2.1** bổ sung
  trường ánh xạ CAP + lớp độ chính xác vị trí mà vẫn tương thích ngược với v2.0.
- **Mã thiết kế tái lập được:** `lora.py` 32/32 và `node_power.py` 19/19. Ba con số
  thiết kế chốt: SOS 36 B ở SF9 tốn **≈ 267 ms** airtime; một gateway đơn kênh ở
  SF9 phục vụ **≈ 242 nút** (beacon 60 s) tới **≈ 952 nút** (beacon 300 s) ở mức
  dùng 80 % kênh; nút cầu ngủ theo lịch sống **≈ 765 ngày** so với **≈ 9,6 ngày** khi
  nghe kênh liên tục.
- **Điều khiển là ĐÒN THIẾT KẾ, không phải hằng số của mạng** (đã tự sửa sau khảo sát
  hệ thống thật): ở chu kỳ 60–300 s thì beacon chiếm **73–95 %** airtime, nhưng
  Meshtastic NodeInfo mặc định **10.800 s** và MeshCore advert **12 h**, ở đó chi phí
  điều khiển rơi còn **0,32–1,36 khung/nút/giờ**. Vì vậy câu hỏi nghiên cứu là
  **"chu kỳ thưa nhất nào vẫn giữ được gradient"**, không phải "điều khiển có chiếm ưu
  thế không". Chế độ `adaptive_gateway` đã cài công thức giãn chu kỳ thật của Meshtastic
  `T×(1+0,075·(N−40))`. ⚠️ Không tìm thấy nguồn nào **đo** tỉ lệ beacon trong mesh LoRa
  một kênh — con số 73–95 % là **mô hình của đề tài**, không được trích như phát hiện
  về LoRa nói chung.
- **Kết quả `SIM` v2.1 (chưa hiệu chuẩn, không được trích như kết quả):** ma trận
  chính 2.400 lượt + **năm thí nghiệm trọng tâm**. Năm phát hiện đáng chú ý:
  1. **H2 sửa lại:** biến quyết định là **airtime mỗi khung**, không phải tải SOS.
     Ở SF7 gradient thắng **0/12 ô** (ΔPDR −0,246); ở SF9 gradient thắng **6/12 ô**
     (ΔPDR −0,020) và rẻ hơn ~8 lần về số lần phát. Trên biên Pareto chỉ còn
     `store_carry_forward` (0,741 PDR) và `gradient` (7,13 lần phát mỗi SOS giao được).
  2. **H3/R3b — kết quả phủ định:** **relay beacon tốn ~17 lần airtime điều khiển
     (1,9 % → 31,8 %) mà giao ít hơn** (0,762 → 0,719) ở vùng 1 km, và vẫn thua ở
     vùng 3 km ⇒ mặc định v1 là **chỉ gateway phát, không relay**.
  3. **H5 nặng hơn dự kiến:** `windowed` chỉ thức 1,5–7,4 % thời gian nhưng PDR rơi
     0,762 → 0,029; `tx_only` cho PDR = 0 — vì nút ngủ **không chuyển tiếp được dữ
     liệu của người khác**, không chỉ bỏ lỡ ACK.
  4. **H6 phụ thuộc kịch bản:** ở vùng 1 km/240 s courier gần như không giúp gì
     (0,463 → 0,500), nhưng ở 3 km/900 s với xe 10 m/s thì **+0,058 PDR và −25 %
     lần phát** ⇒ phải phát biểu H6 **có điều kiện kịch bản**, nếu không sẽ bác bỏ sai.
  5. **RQ6:** mất khung trên link cá nhân **chỉ làm tăng độ trễ, không làm mất SOS**
     (nhờ nút cầu đệm bền) — giả thuyết thiết kế được mô hình xác nhận.
  Xem §7.5 của kế hoạch và [results/](results/).
- **Tự sửa lỗi sau khảo sát (2026-10-01)** — quan trọng cho tính trung thực của tài liệu:
  1. **5 DOI kho dữ liệu ngã trong kế hoạch trước đây SAI** (UMAFall, KFall, FARSEEING,
     MobiFall, UniMiB-SHAR — Crossref trỏ sang bài khác) và **"SafeFall" không tồn tại**;
     DOI đúng đã ghi ở §10.1 của kế hoạch.
  2. **Ba số liệu ngã SAI**: "3–85 báo động giả/ngày" → thật là **22–85** và **27–84**;
     **"Kangas 2015" không tồn tại** → **Kangas 2012**; **"FARSEEING 143 ca"** thực ra
     thuộc **Palmerini 2020**.
  3. **Hai băng 433,05–434,79 MHz và 920–923 MHz có điều kiện pháp lý GIỐNG HỆT**
     (≤ 25 mW ERP; duty cycle 10 %/1 %) — không băng nào thoáng hơn; khác biệt duy nhất
     là **chỉ 920–923 có QCVN loại hình**. Ngày hiệu lực TT 08/2021 nay chốt:
     **28/11/2021**.
  4. **Văn bản neo cho định hướng dự án:** **Thông tư 14/2025/TT-BKHCN** (hiệu lực
     22-9-2025) Điều 4.1 *"ưu tiên sử dụng mạng lưới tại chỗ"*.
  5. **Khung v2.1 đã cài** (tương thích ngược): 2 byte cuối mang `net_id` + ba trục CAP
     + lớp độ chính xác vị trí; 3GPP **TS 23.032** xác nhận **24 bit/trục là đủ**
     (*"uncertainty of less than 3 metres"*).
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

Trình diễn BLE (hai điện thoại + laptop) **trở lại là lõi của WP1–WP2** trong kế
hoạch hiện hành; nền tảng đã có ở [android-g0/README.md](android-g0/README.md) và
[station/README.md](station/README.md) (kết quả `ĐO` cũ tái hiện được). Phần trình
diễn LoRa thuộc hướng đóng băng — chỉ khởi động lại khi có kinh phí và qua cổng G9.
