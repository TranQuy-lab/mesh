# Nghiên cứu chuyển hướng (bản 2 — 2026-10-05): RescueSOS — gửi SOS khi mất sóng trên mạch giá rẻ

**Mục đích:** trả lời ràng buộc mới của người thực hiện — **không đủ kinh phí cho
phần cứng LoRa** (2026-10-05) — và **mục tiêu cốt lõi được chốt lại rõ** cùng ngày:
*một dự án gửi SOS được khi mất sóng, bị cô lập*. Không mở rộng sang bài toán khác.

**Tài liệu liên quan:** [Nhật ký quyết định chọn sóng 2026-10-01](xac-minh-nguon-lora-va-quyet-dinh-song.md)
· [Kế hoạch LoRa](ke-hoach-nghien-cuu-rescuemesh-lora.md) ·
[Phụ lục vệ tinh](nghien-cuu-ve-tinh-rescuemesh-ai.md)

> **Lịch sử bản:** Bản 1 (cùng ngày) đề xuất "WiFi CSI cảm biến người" làm hướng
> chính; người thực hiện phản biện (nhiễu thiên tai: động vật, mái tôn, dòng nước,
> mưa) → Bản 2 đưa "chuỗi SOS ESP-NOW trên ESP32" làm đường chuẩn. **Cùng ngày, bản
> chốt cuối (D13): người thực hiện chọn "làm thật qua điện thoại" — mọi phần cứng
> loại bỏ, đường chuẩn là mạng điện thoại thuần BLE.** Kế hoạch chi tiết chuyển sang
> [ke-hoach-rescue-sos-phone-2026-10-05.md](ke-hoach-rescue-sos-phone-2026-10-05.md);
> phần ESP-NOW (§2–§3) của bản này hạ xuống **mở rộng tuỳ chọn sau WP6** (nút nút đỏ
> cố định cho hộ không có smartphone). Các bằng chứng §6 vẫn hiệu lực.

**Ngày truy cập nguồn:** 2026-10-05. Công cụ: `oa.py` (OpenAlex), Crossref,
`curl` tới raw.githubusercontent.com (HTTP 200 cho các repo ghi ở §6).

---

## 0. Kết luận

| Mã | Quyết định | Trạng thái bằng chứng |
|---|---|---|
| **C0** | Ngân sách phần cứng ≈ 0–800.000 ₫; **LoRa không mua được trong giai đoạn này** | Người thực hiện 2026-10-05 |
| **D8** | KHÔNG đảo ngược D5a/D5c cũ: mesh giữa các **điện thoại** và vệ tinh-làm-sóng-mạng vẫn loại với đúng lý do cũ | Suy luận từ nhật ký 2026-10-01 |
| **D9r** | **Đường chuẩn mới: chuỗi SOS trên ESP32 chạy ESP-NOW** — cùng kiến trúc của kế hoạch LoRa (điện thoại → link cá nhân → nút cầu → chuyển tiếp đa hop → gateway → trạm), chỉ **đổi sóng**: LoRa 920 MHz → **ESP-NOW 2,4 GHz**, vì ESP32 là loại mạch duy nhất vừa ngân sách | Phân tích §2–§3; giới hạn trung thực ghi đủ |
| **D10r** | **Vệ tinh EO (Sentinel-1/VIIRS) giữ ở vai trò tuỳ chọn, 0 đồng, phía trạm** — bản đồ ngập/mất điện là công cụ tình huống cho trạm cứu hộ, **không** là nội dung chính | Người thực hiện 2026-10-05: trọng tâm là SOS |
| **D11r** | **CSI cảm biến người → phụ lục tuỳ chọn (lab, trong nhà tĩnh)**. Lý do hạ: nhiễu môi trường thiên tai (động vật, mái tôn rung, dòng nước, mưa) làm mọi khẳng định phát hiện ngoài lab thành viễn vông nếu chưa đo; và nó không phục vụ mục tiêu SOS | Phản biện của người thực hiện 2026-10-05 — ghi lại như mối đe dọa tính hợp lệ chính thức |
| **D12** | Hướng LoRa **không bị huỷ**: đóng băng ở G6, khi có kinh phí thì tái khởi động; simulator chỉ cần đổi profile PHY để mô hình lại cho cả hai sóng | Quyết định thiết kế `TK` |

**Một câu định vị:** *giữ nguyên kiến trúc và phương pháp luận của RescueMesh-LoRa,
đổi sóng sang ESP-NOW để vừa ngân sách — sản phẩm là một chuỗi nút SOS giá rẻ cho
người bị cô lập, đánh giá bằng mô phỏng chuyển đổi trực tiếp từ simulator hiện có
và demo thực trên 3–4 mạch.*

---

## 1. Bài toán cốt lõi: tin đi từ đâu tới đâu

Khi mất hoàn toàn hạ tầng di động, một tin SOS chỉ đi được bằng một trong ba đường
(vật lý, không có phép màu):

| Đường | Cần gì | Trạng thái |
|---|---|---|
| **(a) Radio mỗi hop + chuỗi nút trung gian** tới điểm có người/nơi cao | Mỗi nút một mạch radio | Đây là đường của dự án; LoRa vừa ngân sách nhất về *tầm*, ESP-NOW vừa ngân sách nhất về *giá* |
| **(b) Người mang tin ra** (đi tới nơi còn sóng) | Cơ chế lưu-và-chuyển-tiếp | Đã có trong simulator (`store_carry_forward`, courier — H6) |
| **(c) Vệ tinh liên lạc** | Terminal 2–100 W | Vượt ngân sách — D5c giữ nguyên |

C0 loại (c); dự án = (a) + (b) ghép nhau: **nút nào không gửi được thì giữ tin, chờ
nút/courier tiếp theo** — đúng cơ chế đã mô phỏng.

---

## 2. Vì sao ESP-NOW trở thành đường chuẩn (sửa D11 bản 1)

Bản 1 loại ESP-NOW vì ba lý do: tầm ngắn, điện năng, và "lặp lại câu hỏi nghiên cứu
cũ không có tiền hiệu chuẩn". Cả ba phải xét lại khi người thực hiện chốt mục tiêu:

| Lý do cũ | Xét lại ở bản 2 |
|---|---|
| Tầm 1 hop ngắn (~100–300 m ngoài trời, số đã `NC` ở D5a; thực địa phải `ĐO`) | Vẫn đúng — nhưng bài toán đã được định nghĩa lại thành **chuỗi nút ngắn giữa những người bị cô lập ở gần nhau** (tổ dân phố, xóm, điểm sơ tán), không phải phủ 5×5 km. LoRa vẫn sẽ là lựa chọn khi có tiền; đây là **bản demo/prototyping của cùng kiến trúc** |
| Điện năng kém (Rx trăm mA — `GIẢ ĐỊNH`, phải đối chiếu datasheet ESP32) | Vẫn đúng cho triển khai dài ngày; giai đoạn demo dùng sạc dự phòng USB, không phải bài toán. Bài học H5 (nút ngủ không chuyển tiếp được) chuyển thẳng sang đây và là một giả thuyết của bản mới |
| "Lặp câu hỏi cũ" | Đảo lại: simulator airtime hiện có (41/41 test) là **tài sản dùng được ngay** — thêm profile PHY ESP-NOW là mô hình lại toàn bộ H2–H6 trên sóng mới mà không tốn đồng nào. Câu hỏi "kinh tế airtime trên kênh 2,4 GHz đông đúc" là câu hỏi *khác* LoRa (nhiễu WiFi nhà dân), không phải câu hỏi cũ |

**Giá trị nghiên cứu còn đứng vững ở C0 ≈ 0:** chưa có đo hệ thống nào công bố về
chuỗi SOS ESP-NOW đa hop trong điều kiện mất hạ tầng (khoảng trống — phải kiểm lại
bằng sổ tìm kiếm §7 trước khi tuyên bố).

---

## 3. Kiến trúc đề xuất (mỗi vai trò một dòng)

```
ĐIỆN THOẠI (người dân)          NÚT CẦU ESP32 (đeo kèm)          CHUỖI ESP-NOW            GATEWAY + TRẠM
app IMU 20 Hz + nút SOS   BLE   thu SOS từ điện thoại,    ESP-NOW  nút trung gian giữ tin   ESP32 nối laptop (USB serial)
phát hiện ngã tự động  ──────►  phát ESP-NOW đi các hướng ──────►  + chuyển tiếp, ngủ theo  ──► danh sách SOS + bản đồ
                              (kế thừa khung 36 B ý tưởng)       lịch (bài học H5)        ──► người mang tin ra nơi còn sóng
```

- **Điện thoại:** đầu cuối của người dân — cảm biến IMU, nút SOS, vị trí GNSS, giao
  diện huỷ báo động. **Không đổi gì so với kế hoạch LoRa** (D3/D6 giữ nguyên: link
  cá nhân BLE 1–2 m). App `android-g0/` đã chạy trên Pixel 6 Pro và Redmi.
- **Nút cầu ESP32:** mạch nhỏ duy nhất người dân phải có — BLE nhận SOS từ điện
  thoại + WiFi ESP-NOW chuyển tiếp. ESP32 chạy đồng thời BLE + WiFi được (ghi ràng
  buộc共存/hiệu năng vào thiết kế). Không cần GNSS/IMU/màn hình.
- **Nút trung gian:** cùng loại mạch, đặt ở nhà không bị ngập/ngã ba — giữ tin khi
  chưa gửi được (store-carry-forward), chuyển tiếp theo chính sách gradient/flooding
  đã mô phỏng.
- **Gateway + trạm:** một ESP32 nối laptop bằng USB (trạm v1.0 có sẵn logic thu +
  hiển thị, đổi BLE scan thành đọc serial). Ở điểm cao/nhà văn hoá xã.
- **Sóng:** ESP-NOW 2,4 GHz — không cần router, không cần Internet, phát trực tiếp
  ESP32 ↔ ESP32, miễn giấy phép (ràng buộc EIRP 2,4 GHz — QCVN 54:2011 **phải đọc
  bản gốc** trước khi đo, hiện `chưa xác minh`).

**Vì sao cách này không viễn vông:** mọi thứ trong chuỗi trên đều là *vận chuyển tin
đã kiểm soát* — không có khẳng định nào về "đọc môi trường qua sóng". Các giả thuyết
H2 (airtime quyết định, không phải tải), H3 (ai phát beacon), H5 (ngủ thì không
chuyển tiếp), H6 (courier có điều kiện) **mượn nguyên từ kế hoạch LoRa** và được chạy
lại trong simulator với profile ESP-NOW, nhãn `SIM` như cũ; demo thực trả lời câu
"tầm 1 hop thực địa là bao nhiêu" bằng `ĐO` — con số đang thiếu nhất của cả hai hướng.

---

## 4. AI nằm ở đâu (đúng cuộc thi, không phóng đại)

| # | AI | Vai trò | Vì sao không viễn vông |
|---|---|---|---|
| 1 | **Phát hiện ngã/bất động trên IMU của chính điện thoại** (T1→T3, LOSO, ngân sách FAR — thiết kế sẵn trong kế hoạch §3.3, RQ1) | Bộ não quyết "khi nào phát SOS" | Cảm biến nằm **trên người**, không dính nhiễu môi trường như cảm biến từ xa; dữ liệu công khai có sẵn; 0 đồng |
| 2 | *(Tuỳ chọn)* Chính sách thích ứng (beacon/định tuyến học theo tải) chạy **trong simulator**, so sánh với 5 thuật toán cố định, nhãn `SIM` | Nội dung AI của phần mạng | Có so sánh có kiểm soát thì mới được nêu — đúng quy tắc báo cáo hiện hành |
| 3 | *(Tuỳ chọn, phía trạm)* Gom/trọng số SOS trùng lặp cùng vị trí | Giảm nhiễu cho người cứu hộ | Việc nhỏ, có thật, không hứa trước khi làm |

**CSI cảm biến người (phụ lục D11r):** chỉ làm nếu còn thời gian và chỉ trong nhà
tĩnh (phòng lab), với các mối đe dọa ghi sẵn: động vật, mái tôn, dòng nước, mưa —
bất kỳ kết quả nào cũng nhãn `ĐO` trong lab và **cấm** suy ra môi trường thiên tai.
Bằng chứng văn học đã xác minh của bản 1 giữ ở §6.2 làm tài liệu tham khảo.

---

## 5. BOM và lộ trình cổng

| Khối | Số lượng | Ghi chú |
|---|---|---|
| ESP32 DevKit (WROOM-32) | 3 (demo tối thiểu) – 4 | Giá VN **`GIẢ ĐỊNH` ~150–250k ₫/mạch — phải lấy giá có ngày + nguồn khi mua** (quy tắc BOM) |
| Sạc dự phòng / sạc USB | 3 | Tận dụng đồ có sẵn |
| Laptop trạm | 1 | Đã có |
| **Tổng** | **≈ 500–800k ₫ cho demo 3 nút** | Mua **sau** cổng G0-S |

| Cổng | Điều kiện | Vì sao đặt trước |
|---|---|---|
| **G0-S (mô phỏng, 0 đồng)** | Simulator có profile ESP-NOW (airtime/bitrate/tầm theo datasheet `NC`), chạy lại H2/H5/H6, xuất bảng so sánh LoRa↔ESP-NOW | Không đạt thì không mua mạch |
| **G6-S (khung)** | Codec SOS/ACK chạy trên ESP32, BLE link điện thoại ↔ nút hoạt động | Kế thừa G6 cũ |
| **G9-S (đo)** | Đo tầm 1 hop thực địa theo khoảng cách có log (đúng việc còn thiếu đã ghi trong nhật ký D1/D2); đo dòng điện ngủ/nghe | Biến `GIẢ ĐỊNH` thành `ĐO` |

---

## 6. Bằng chứng đã xác minh (giữ từ bản 1, vai trò mới)

### 6.1 Cho phần SOS

| Nội dung | Nguồn | Loại |
|---|---|---|
| Mesh giữa điện thoại Android không root chỉ 1 hop (loại mesh-điện thoại) | `developer.android.com` Wifi Aware/WiFi Direct (đã xác minh 2026-09-30) | Tài liệu nền tảng |
| ESP-NOW hoạt động không hạ tầng giữa ESP32 | repo chính thức `espressif/esp-csi` cấu trúc + tài liệu ESP-IDF — **số đo tầm/dòng điện chưa xác minh, phải datasheet + `ĐO`** | Nhà sản xuất |
| Store-carry-forward/courier trong cứu hộ | Simulator đề tài (H6 đã chạy, nhãn `SIM`) | Nội bộ |
| Pháp lý 2,4 GHz | QCVN 54:2011/BTTTT — **chưa đọc bản gốc, chưa được trích số** | Việc còn thiếu |

### 6.2 Cho phụ lục CSI (hạ cấp — chỉ tham khảo lab)

Survey nền `10.1145/3310194`; survey hành vi `10.1109/access.2019.2949123`; ngã CSI
`10.1109/access.2023.3300726`, `10.1007/s42486-020-00027-1`, `10.1016/j.dibe.2025.100745`;
hô hấp `10.1109/icca54724.2022.9831898`, `10.1109/jtehm.2022.3218638`, `10.1109/jsen.2020.2989780`;
kho UT-HAR/NTU-Fi qua `10.48550/arxiv.2506.11165` (preprint); repo `espressif/esp-csi`
(HTTP 200). **Ghi chú trung thực mới:** các bài này đa số đo trong nhà tĩnh — đúng
lý do D11r hạ hướng này xuống phụ lục.

### 6.3 Cho phần vệ tinh EO tuỳ chọn (D10r)

Sen1Floods11 (repo `cloudtostreet/Sen1Floods11`, HTTP 200) + CNN flood benchmark
`10.1109/jstars.2022.3152127`; VN: `10.1080/2150704x.2024.2388846` (An Giang),
`10.3390/rs15082001` (Mekong), `10.1007/978-3-031-17808-5_26` (miền Trung),
`10.3390/rs17132171` (bão Talas); VIIRS outage `10.3390/rs12193194`, `10.3390/rs9030286`,
`10.1038/s44304-026-00270-z`. Vai trò: bản đồ tình huống cho trạm — **không** là
nội dung chính, không được tuyên bố "lần đầu AI phát hiện lũ VN" (đã có ≥ 4 bài).

---

## 7. Sổ tìm kiếm và số liệu cấm (bản 2)

**Đã dùng:** OpenAlex qua `research_tools/oa.py` (10 truy vấn, xem bản 1), Crossref,
raw.githubusercontent.com. **Cần bổ sung trước khi viết báo cáo:** datasheet ESP32
(dòng Rx/Tx, chế độ modem-sleep), số đo tầm ESP-NOW công bố độc lập, trạng thái chuẩn
IEEE 802.11bf, bản gốc QCVN 54:2011.

| Số liệu / khẳng định | Vì sao cấm |
|---|---|
| Bất kỳ giá ESP32 nào không có ngày + nguồn mở được | Quy tắc BOM; mức ~150–250k ₫ là `GIẢ ĐỊNH` |
| Tầm ESP-NOW "500 m / 1 km" từ blog/diễn đàn | Chỉ nhận `ĐO` của chính đề tài hoặc nguồn bình duyệt |
| "ESP32 sống bằng pin vài tháng" | Chưa đối chiếu datasheet dòng điện — bắt buộc `GIẢ ĐỊNH` tới khi có số |
| Accuracy 95–99 % của bài CSI-HAR | Không theo LOSO/FAR budget — không trích làm kỳ vọng (kể cả ở phụ lục) |
| "CSI phát hiện người trong bão lũ/ngập" | Không có bằng chứng; các mối đe dọa (động vật, mái tôn, dòng nước, mưa) chưa ai kiểm định |
| "ESP32 chạy đồng thời BLE+WiFi không hao năng lượng thêm" | Chưa xác minh coexistence — phải đo |
| Tuyên bố "AI định tuyến thông minh hơn" không kèm so sánh simulator | Quy tắc báo cáo hiện hành của dự án |

---

## 8. Bản đồ cập nhật với tài liệu cũ

| Tài liệu cũ | Trạng thái |
|---|---|
| Kế hoạch LoRa + thiết kế v2 + codec/simulator | Giữ nguyên; simulator thêm **profile PHY ESP-NOW** (G0-S) |
| `android-g0/` + thiết kế phát hiện ngã T1–T3 | **Kế thừa nguyên trạng** — vẫn là đầu cuối + AI #1 |
| Phụ lục vệ tinh (Starlink backhaul) | Giữ nguyên, dài hạn; EO data là phần tuỳ chọn phía trạm |
| Nhật ký 2026-10-01 | D1–D7 đứng nguyên; bản 2 bổ sung C0/D8/D9r/D10r/D11r/D12 |
| README | Mục đọc đầu tiên trỏ tới tài liệu này |
