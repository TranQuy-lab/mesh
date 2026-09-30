# Nhật ký quyết định & sổ nguồn đã xác minh — chọn một loại sóng (2026-10-01)

**Mục đích:** ghi lại **vì sao** RescueMesh chuyển từ BLE sang **một loại sóng duy
nhất là LoRa**, và **vì sao** ba phương án WiFi mesh / WiFi HaLow / WiFi vệ tinh bị
loại — kèm nguồn đã mở, DOI đã đối chiếu, và danh sách số liệu **bị cấm dùng**.

**Tài liệu liên quan:** [Kế hoạch nghiên cứu](ke-hoach-nghien-cuu-rescuemesh-lora.md) ·
[Thiết kế v2.0](thiet-ke-he-thong-lora-v2.md) ·
[Phụ lục nghiên cứu vệ tinh](nghien-cuu-ve-tinh-rescuemesh-ai.md) ·
[Kế hoạch BLE lịch sử](ke-hoach-nghien-cuu-rescuemesh-ai.md)

**Ngày truy cập toàn bộ nguồn:** 2026-09-30, trừ khi ghi khác.
**Hạn chế công cụ của phiên:** `web_search` của harness trả lỗi HTTP 401 trong suốt
phiên; các nhánh nghiên cứu dùng `web_fetch` + DuckDuckGo/Bing RSS, xác minh metadata
qua **Crossref / OpenAlex / Unpaywall**, và đọc PDF gốc bằng `pdftotext`. Vì vậy mọi
DOI dưới đây đã được đối chiếu tự động, không lấy từ trí nhớ.

---

## 0. Kết luận

| Mã | Quyết định | Trạng thái bằng chứng |
|---|---|---|
| **D1** | Loại BLE vì tầm quá ngắn | Quyết định của người thực hiện + lớp tầm của công nghệ; dự án **chưa** chạy quét tầm xa BLE có hệ thống |
| **D2** | Dùng **một loại sóng duy nhất: LoRa**, băng 920–923 MHz | Băng tần **được miễn giấy phép** (nguồn chính thức); tầm/thông lượng theo lớp công nghệ + mô hình tái lập |
| **D3** | **Giữ điện thoại làm đầu cuối**, thêm **nút cầu LoRa cá nhân** nối bằng link cá nhân 1–2 m (BLE; dự phòng dây USB-C) | Người dùng chốt 2026-10-01: ai cũng mang điện thoại, nhồi chip LoRa vào điện thoại là khó thực hiện. Ràng buộc "một sóng" được hiểu là **một loại sóng cho MẠNG cứu hộ** |
| **D4** | Nút cầu **không cần GNSS/IMU/màn hình** (điện thoại đã có) → BOM thấp hơn nút đầy đủ | Hệ quả của D3; xem thiết kế §2 |
| **D5** | Loại WiFi mesh, WiFi HaLow và vệ tinh khỏi đường chuẩn | Có nguồn cho cả ba (§4–§6) |
| **D6** | Link cá nhân mặc định **BLE**, dự phòng **dây USB-C** | Cự ly 1–2 m nên lý do "tầm ngắn" đã loại BLE khỏi vai trò mạng **không áp dụng**; đây là điểm cần nói thẳng trong phần giới hạn (§1.3 kế hoạch) |
| **D7** | **Băng chuẩn: 920–923 MHz** (module SX1262, ví dụ Ra-01SH ~135.000 ₫); **băng 433,05–434,79 MHz là nhánh so sánh**, mua thêm nếu ngân sách cho phép | Người dùng giao toàn quyền 2026-10-01. **Lý do đã sửa sau khảo sát pháp lý:** hai băng có **điều kiện pháp lý giống hệt nhau** (≤ 25 mW ERP; duty cycle 10 %/1 % — Thông tư 08/2021 Phụ lục 19), nên **không phải vì 433 chặt hơn**. Khác biệt thật là: (i) **chỉ 920–923 MHz mới có QCVN loại hình** (QCVN 122:2020) để thiết kế và kiểm nghiệm đối chiếu, còn 433 chỉ có quy chuẩn phát xạ giả; (ii) anten 920 nhỏ gọn hơn (λ/4 ≈ 8 cm so với ≈ 17 cm); (iii) băng 433 đông đúc hơn. Nhánh 433 vẫn nên mua để trả lời bằng đo thực câu "băng nào tốt hơn ở Việt Nam" — một khoảng trống, vì **chưa có đo LoRa nào tại VN** |

**Ba quyết định khác của người dùng trong cùng ngày 2026-10-01:**

| Nội dung | Quyết định | Cách tôi đã xử lý |
|---|---|---|
| Ngày hiệu lực Thông tư 08/2021 (18/11 hay 28/11/2021) | "kệ nó đi" — **không theo đuổi** | Ghi nhận mâu thuẫn nguồn, **bỏ** khỏi danh sách việc cần làm, không chặn tiến độ. Các **giới hạn kỹ thuật** của QCVN 122:2020 (14 dBm e.r.p., duty cycle 1 %/10 %) vẫn giữ vì chúng ảnh hưởng trực tiếp tới thiết kế |
| Giá linh kiện | Dùng **mức giá tham khảo** do người dùng cung cấp | Đã đưa vào BOM, ghi rõ **"do người dùng cung cấp 2026-10-01, chưa xác minh độc lập"**, kèm cảnh báo **sai băng** cho hai module SX1278 433 MHz |

Nguyên tắc áp dụng: **mỗi quyết định phải hoặc có bằng chứng mở được, hoặc được
ghi rõ là quyết định thiết kế (`TK`) / suy luận (`SUY`) / giả định (`GIẢ ĐỊNH`).**

---

## 1. Câu hỏi quyết định và tiêu chí đặt trước

Câu hỏi: *sóng nào làm đường liên lạc duy nhất cho một mạng cứu hộ hoạt động khi
hạ tầng di động mất hoàn toàn, ở vùng bão lũ nông thôn Việt Nam?*

Tiêu chí, đặt trước khi so:

| # | Tiêu chí | Vì sao quan trọng |
|---|---|---|
| C1 | **Tầm mỗi hop** | Tiêu chí đã loại BLE; quyết định số nút cần để phủ vùng |
| C2 | **Chạy được khi mất hoàn toàn hạ tầng** | Không phụ thuộc trạm gốc, Internet, điện lưới |
| C3 | **Số nút/hạ tầng cần để phủ một xã** | Chi phí và tính khả thi triển khai |
| C4 | **Điện năng và tuổi thọ** | Nút phải sống qua nhiều ngày không sạc |
| C5 | **Chi phí mỗi nút** | Quyết định quy mô cấp phát |
| C6 | **Pháp lý tần số tại Việt Nam** | Không có băng hợp pháp thì không triển khai được |
| C7 | **Băng thông đủ cho SOS** | SOS chỉ cần vài chục byte, nhưng phải đủ chở vị trí + xác thực |
| C8 | **Khả năng xác thực** | Chống tin giả và phát lại |

**C1 và C2 là điều kiện tiên quyết**: phương án không đạt hai tiêu chí này bị loại
trước khi so các tiêu chí còn lại.

---

## 2. D1 — Vì sao loại BLE

| Nội dung | Ghi nhận |
|---|---|
| Lớp tầm của công nghệ | BLE là công nghệ **cự ly ngắn**; trong thực tế giữa hai thiết bị cầm tay, tầm hữu dụng thường ở mức hàng chục mét, và giảm mạnh khi có vật cản, cơ thể người, hoặc khi thiết bị ở trong túi |
| Bằng chứng trong dự án | Trạm laptop đã nhận đúng khung 24 byte từ Pixel 6 Pro và Redmi Note 14 Pro, nhưng **các buổi đo hiện có không phải là quét tầm xa có hệ thống**; tài liệu ghi rõ phần còn thiếu là đo khoảng cách và đo pin. Xem [kết quả rà soát ban đầu](ket-qua-ra-soat-va-nghien-cuu-ban-dau.md) |
| Hệ quả mật độ (`SUY`) | Để phủ một vùng 5 km × 5 km với tầm hữu dụng hàng chục mét cần **hàng nghìn tới hàng chục nghìn** nút trung gian đặt đúng chỗ — không khả thi khi hạ tầng đã mất |
| Kết luận | **Loại** (D1). Ghi trung thực: đây là quyết định của người thực hiện dựa trên lớp tầm của công nghệ, **không** phải kết quả của một thí nghiệm quét tầm xa đã hoàn tất |

**Việc nên làm để đóng dấu vết này (nếu bị phản biện):** một buổi đo tầm BLE theo
khoảng cách có log, để câu "tầm quá ngắn" có số `ĐO` thay vì `SUY`. Đây là việc
nhỏ và nên đưa vào phụ lục.

---

## 3. D2 — Vì sao LoRa

### 3.1 Băng tần hợp pháp tại Việt Nam (đã xác minh)

| Nội dung | Kết luận | Nguồn |
|---|---|---|
| Thiết bị LPWAN ở băng 920–923 MHz (và 433,05–434,79 MHz) có phải xin giấy phép tần số? | **Không** — được bổ sung vào **danh mục thiết bị vô tuyến điện được miễn giấy phép sử dụng tần số**, kèm điều kiện kỹ thuật và khai thác | Thông tư **08/2021/TT-BTTTT** ngày 14/10/2021; cổng thông tin pháp luật (nay thuộc Bộ KH&CN), `cspl.mic.gov.vn` bản tin 19/10/2021. **Ngày hiệu lực mâu thuẫn giữa hai nguồn: 18/11/2021** (trang Cục Tần số VTĐ `rfd.gov.vn`) **so với 28/11/2021** (bản tin cổng pháp luật) — phải tra bản công báo gốc trước khi trích |
| Điều kiện kỹ thuật là gì? | **QCVN 122:2020/BTTTT** quy định chỉ tiêu phổ tần, điều kiện kỹ thuật và phương pháp đo cho thiết bị LPWAN 920–923 MHz; xây dựng trên ITU-R SM.2423-0/SM.329-12, ETSI EN 300 220-1/-2 và tiêu chuẩn ASEAN | Thông tư **38/2020/TT-BTTTT** ngày 16/11/2020, hiệu lực 01/07/2021; cùng cổng, bản tin 17/11/2020 |
| **Giới hạn công suất** | **≤ 14 dBm e.r.p.** (≈ 25 mW e.r.p.; ≈ 16,2 dBm EIRP) | **Đã đọc bản công báo gốc 61 trang** — QCVN 122:2020/BTTTT mục 2.4.3.2 (`congbaocdn.chinhphu.vn/.../33409-1-20201115-111638-2020-tt-btttt.pdf`) |
| **Giới hạn duty cycle** | Đầu cuối/cảm biến **≤ 1 %**; gateway/access station **≤ 10 %**; chu kỳ quan sát `Tobs` = 1 giờ | Đã đọc bản công báo gốc — QCVN 122:2020/BTTTT mục 2.4.4.2 |
| **Hệ quả bắt buộc cho thiết kế** | Board Meshtastic/Heltec bán sẵn phát **+20/+22 dBm → vượt QCVN**; cấu hình **SF12 + beacon 60 s (2,36 %) không hợp quy** (vượt 1 %). Phải hạ công suất phát và giãn beacon | QCVN 122:2020 + mô hình `SUY` của đề tài |
| Phổ tần dùng chung? | Có — quy chuẩn nêu rõ thiết bị LPWAN **dùng chung phổ tần** 920–923 MHz với các thiết bị vô tuyến cự ly ngắn khác | Thông tư 38/2020/TT-BTTTT |
| **Băng 433,05–434,79 MHz thì sao?** | **Điều kiện GIỐNG HỆT 920–923**: ≤ 25 mW ERP; duty cycle **≤ 10 % gateway / ≤ 1 % đầu cuối** — do chính Thông tư 08/2021 đặt tại **Phụ lục 19**, không đổi trong bản hợp nhất 2025 (sửa bởi Thông tư 01/2025/TT-BKHCN). **Không có QCVN loại hình cho 433**; QCVN 122:2020 **chỉ** áp cho 920–923 | Bản công báo gốc TT 08/2021 + bản hợp nhất 2025 |
| **Ngày hiệu lực TT 08/2021** | **28/11/2021** (Điều 8 bản công báo gốc) — **mâu thuẫn 18/11 vs 28/11 nay đã hết** | Bản công báo gốc |
| **Rủi ro pháp lý mới** | "Miễn giấy phép tần số" **≠** miễn mọi nghĩa vụ: vẫn phải **chứng nhận/công bố hợp quy nhóm 2** (TT 11/2020/TT-BTTTT); và **Luật Viễn thông 24/2023/QH15 Điều 19.5** có thể buộc **giấy phép thiết lập mạng viễn thông dùng riêng** cho mesh liên xã (Điều 42.4 miễn nếu cùng một tổ chức và không tự xây đường truyền) | Luật Viễn thông 24/2023/QH15 |
| Nghĩa vụ kèm theo | Thiết bị miễn giấy phép **phải dừng sử dụng** nếu gây nhiễu có hại cho thiết bị được cấp phép | Thông tư 08/2021/TT-BTTTT |
| Cơ quan quản lý | Hai thông tư trên do **Bộ TT&TT** ban hành; từ 2025 đầu mối tần số/viễn thông chuyển về **Bộ KH&CN** (Cục Tần số VTĐ, Cục Viễn thông). **Không** gán văn bản 2026 cho Bộ TT&TT | Cổng pháp luật hiện thuộc Bộ KH&CN; văn bản cấp phép vệ tinh 2026 |

### 3.2 Các lý do kỹ thuật, kèm mức tin cậy

| Tiêu chí | Đánh giá cho LoRa | Nhãn |
|---|---|---|
| C1 Tầm mỗi hop | Lớp tầm **km** (sub-GHz, trải phổ); tầm thực phụ thuộc địa hình, độ cao anten, SF | `SUY` + phải `ĐO` |
| C2 Không cần hạ tầng | Nút ↔ nút trực tiếp trên một kênh; không cần trạm gốc hay Internet | Thiết kế |
| C3 Số nút để phủ | Nút trung gian chỉ cần ở nơi khuất; gateway là nút thắt, không phải mật độ nút | `SUY` (`lora.py`) |
| C4 Năng lượng | Nút cầu ngủ theo lịch: ≈ 765 ngày trên pin 18650; **nghe liên tục chỉ ≈ 9,6 ngày** | `SUY` (`node_power.py`, dòng Rx/Tx là `NC` từ datasheet SX1276) |
| C5 Chi phí mỗi nút | Cần module MCU + SX1262 + IMU + GNSS; **giá chưa xác minh trong đợt này** | Còn thiếu |
| C6 Pháp lý | Băng 920–923 MHz **miễn giấy phép tần số** | `NC` (§3.1) |
| C7 Băng thông đủ SOS | Khung SOS 36 byte; airtime SF9 ≈ **267 ms**; bitrate 293–5.469 bps theo SF | `SUY` |
| C8 Xác thực | HMAC-SHA256 cắt 64 bit vừa ngân sách airtime; chữ ký số 64 B thì không | Thiết kế |
| C9 Suy hao do mưa (câu hỏi riêng cho bão lũ) | **≈ 0 dB ở 923 MHz** với mưa nhiệt đới 12–180 mm/h; mọi gói nhận được ở 916 m | `NC` — Elijah et al. 2021, `10.1109/ACCESS.2021.3080317` (đọc PDF nguồn). **Còn thiếu:** đo trong điều kiện **ngập thực tế** |

### 3.3 Ràng buộc phải chấp nhận khi chọn LoRa (ghi vào phần giới hạn)

1. **Airtime là tài nguyên chung.** Một kênh; nút phát nhiều làm mọi nút mất gói.
2. **Sức chứa hữu hạn:** một gateway đơn kênh ở SF9 phục vụ ≈ **242 nút** (beacon
   60 s) tới ≈ **952 nút** (beacon 300 s) ở mức dùng 80 % kênh (`SUY`).
3. **Điều khiển chiếm ưu thế:** beacon chiếm **73–93 %** airtime của mỗi nút ở chu
   kỳ 60–300 s (`SUY`) — hệ quả là phải thiết kế beacon thích ứng.
4. **Nghịch lý ngủ/nghe:** ngủ để giữ pin thì không nhận được lệnh xuống.
5. **Điện thoại ở lại, nhưng phần vô tuyến của nó thì đổi.** App Android giữ vai trò
   cảm biến + giao diện; BLE bị bỏ ở vai trò **mạng chuyển tiếp**, chỉ còn là **link
   cá nhân 1–2 m** tới nút cầu. Hệ quả: kho dữ liệu IMU công khai (thu bằng điện
   thoại) **áp dụng trực tiếp**, không còn bài toán chuyển miền do cách gắn.
6. **Quy mô bị chặn bởi token ACK:** token 24 bit chỉ đủ tới ≈ **1.000 nút**
   (Monte Carlo `SIM`: ở 10.000 nút xác suất khớp sai ≈ 94 %).
7. **Công suất bị luật chặn ở 14 dBm e.r.p.** — thấp hơn mức +20/+22 dBm của phần
   cứng Meshtastic/Heltec bán sẵn. Hệ quả: phải hạ công suất, và mọi kết quả đo tầm
   xa phải ghi rõ công suất thực dùng.
8. **Duty cycle ≤ 1 % cho đầu cuối chặn cấu hình SF12 + beacon dày**: SF12 với
   beacon 60 s là 2,36 % → **không hợp quy**; SF7 (0,09 %) và SF9 (0,33 %) thì hợp quy.

---

## 4. D5a — Vì sao loại WiFi mesh 2.4/5 GHz

| Bằng chứng | Số liệu | Loại nguồn | Nguồn |
|---|---|---|---|
| Mesh 802.11s/BATMAN-adv **không chạy trên Android không root** — cần OpenWrt hoặc thiết bị có root | Định tính | Tài liệu nền tảng | `source.android.com/docs/core/connect/wifi-aware`, `developer.android.com/.../wifi-aware` |
| Wi-Fi Direct chỉ là **hình sao** (Group Owner), không phải mesh đa hop | Định tính; không có tài liệu chính thức về số client tối đa | Tài liệu nền tảng | `source.android.com/docs/core/connect/wifi-direct` |
| Wi-Fi Aware (NAN) là **1 hop**, và có thể **không khả dụng** nếu Wi-Fi Direct/SoftAP/tethering đang bật | Định tính | Tài liệu nền tảng | `developer.android.com/develop/connectivity/wifi/wifi-aware` |
| Thông lượng mesh đa hop suy giảm rất mạnh theo số hop | TCP: ≈ n⁻¹ (Google WiFi, 802.11ac) và ≈ n⁻¹·⁵ (open80211s, 802.11g); độ trễ ≈ tuyến tính theo hop | Bài báo testbed bình duyệt | `doi:10.12720/jcm.14.12.1218-1223` |
| PDR của BATMAN-adv sụp khi mạng lớn dần | 100 % → **42,8 %**; OLSR ngoài trời chỉ **2,9 Mbps**; jitter OLSR 0,281 → 2,58 ms ở 11 nút (Raspberry Pi 4) | Bài báo testbed bình duyệt | `doi:10.3390/telecom5040051` |
| Mesh quy mô lớn cần **hạ tầng cố định** | Freifunk Paderborn ≈ **800 nút** BATMAN IV, control ≈ **25 GB/tháng/nút**; Guifi.net > **27.000 nút** (2015) | Bài báo bình duyệt | `doi:10.1109/netsys.2017.7903954`; `doi:10.1016/j.comnet.2015.09.023` |
| EasyMesh chỉ dành cho **nhiều AP**, không cho điện thoại | Định tính | Hiệp hội chuẩn | `wi-fi.org/discover-wi-fi/wi-fi-easymesh` |
| Không có số đo nào cho mesh WiFi giữa **điện thoại Android thật trong bão lũ** | **Không tìm thấy nguồn** | — | Khoảng trống, không phải bằng chứng ủng hộ |

**Kết luận:** WiFi mesh 2.4/5 GHz **không đạt C1 và C2**: nó cần hạ tầng dày (router
OpenWrt cố định), đa hop suy giảm mạnh, và trên điện thoại không root thì chỉ có
kết nối 1 hop/hình sao. Đây đúng là loại vấn đề đã khiến BLE bị loại.

---

## 5. D5b — Vì sao loại (nhưng giữ dự phòng) WiFi HaLow 802.11ah

| Bằng chứng | Số liệu | Loại nguồn | Nguồn |
|---|---|---|---|
| HaLow là biến thể WiFi **duy nhất** có tầm xa; chuẩn nhắm ~1 km và ≥ 100 kbps ở biên; tối đa 8.191 station/AP (AID 13 bit, lý thuyết) | ~1 km; 8.191 | Bài báo phân tích chuẩn | `doi:10.13052/jicts2245-800x.125` |
| Số đo thực địa tốt nhất hiện có là **preprint chưa bình duyệt** | NLoS biên ≈ 120 m; 1 hop **814 m @ 0,15 Mbps**; 2 relay **901 m @ 0,73 Mbps**; 3 relay **1.110 m @ 0,47 Mbps** | Preprint arXiv | `arXiv:2605.17349` |
| **Không có hỗ trợ HaLow native trên Android** | **Không tìm thấy nguồn** — không được giả định là có | — | — |
| Module đang sản xuất nhưng **giá chưa xác minh** | Vendor: 33 Mbps (MM6108), 43,3 Mbps và "1 km" (MM8108) | **Quảng cáo nhà sản xuất** — không dùng làm cơ sở thiết kế | `morsemicro.com/products/chips` |

**Kết luận:** HaLow là phương án **dự phòng hợp lý** nếu về sau cần băng thông cao
hơn mà vẫn giữ tầm xa, nhưng hiện **không đủ bằng chứng** (chưa có hỗ trợ nền tảng,
số đo tốt nhất chưa bình duyệt, giá chưa xác minh) để làm đường chuẩn.

---

## 6. D5c — Vì sao loại vệ tinh khỏi vai trò "sóng của mạng"

Chi tiết đầy đủ (76 bằng chứng) ở [phụ lục nghiên cứu vệ tinh](nghien-cuu-ve-tinh-rescuemesh-ai.md).

| Bằng chứng | Số liệu | Loại nguồn | Nguồn |
|---|---|---|---|
| Vệ tinh **không phải mesh**: một terminal là một điểm truy cập | Định tính | Spec sheet chính thức | `starlink.com/public-files/specification_sheet_mini.pdf`, `..._standard.pdf` |
| Năng lực phục vụ của một terminal | Mini: WiFi 5, **112 m², 128 thiết bị, 25–40 W**, cần nguồn USB-PD **100 W**; Standard 4X + Router 3: WiFi 6, **297 m², 235 thiết bị, 75–100 W** | Spec sheet chính thức | như trên |
| **Không ghép được với mesh bên thứ ba** | "Not compatible with 3rd party mesh systems"; chỉ mesh được với tối đa 3 Starlink Mesh Node | Spec sheet chính thức | như trên |
| Tại Việt Nam, dịch vụ đã thương mại nhưng nằm trong **thí điểm có trần** | Thương mại từ **13/8/2026**; giấy phép tần số 13/02/2026; **trần 600.000 thiết bị**, 4 gateway; thí điểm **kết thúc trước 1/1/2031** | Văn bản/quyết định + báo chí chính thống | Quyết định 659/QĐ-TTg (26/3/2025); cổng Bộ KH&CN; báo Đảng |
| Chính phủ coi đây là giải pháp **tạm thời**, sẽ **điều chuyển thiết bị** khi có sóng mặt đất | Định tính | Báo Đảng | Xem phụ lục §1 |
| Direct-to-Cell **chưa có** ở Việt Nam; Apple Emergency SOS **không phủ** Việt Nam | Định tính | Trang availability của Apple; hồ sơ cấp phép VN | `support.apple.com/en-us/101573` |
| **Chưa có đo rain fade tại chính Việt Nam** (chỉ có Malaysia/Indonesia/Singapore/Thái Lan) | **Không tìm thấy nguồn** cho VN | Bài báo bình duyệt cho các nước khác | `doi:10.1109/micc.2011.6150306`; `doi:10.11591/ijece.v8i4.pp2608-2613` |

**Kết luận:** vệ tinh **không đạt C2 và C3** ở vai trò sóng của mạng (một điểm, không
ghép vào mesh, phụ thuộc chính sách thí điểm có trần). Vệ tinh vẫn là hướng mở rộng
hợp lý cho **backhaul của trạm** — nhưng khi đó hệ thống có **hai sóng**, trái với
ràng buộc hiện tại, nên phải tách thành đề xuất riêng.

---

## 7. Ma trận quyết định

| Tiêu chí | BLE | **LoRa** | WiFi mesh 2.4/5 | WiFi HaLow | Vệ tinh |
|---|---|---|---|---|---|
| C1 Tầm mỗi hop | hàng chục m (`SUY`) | **km** (`SUY`, phải `ĐO`) | ~100–300 m, suy giảm n⁻¹·⁵ (`NC`) | ~814 m @0,15 Mbps (preprint) | toàn cầu |
| C2 Mất hạ tầng hoàn toàn | có | **có** | chỉ khi có router OpenWrt/root | cần gateway | có, nhưng 1 điểm |
| C3 Nút cần để phủ | hàng nghìn | **thấp** | cao, cần hạ tầng cố định | trung bình | 1 terminal |
| C4 Điện năng | thấp | **thấp** (≈ 765 ngày nếu ngủ; ≈ 9,6 ngày nếu nghe liên tục) | cao (AP) | chưa rõ | 25–100 W |
| C5 Chi phí mỗi nút | thấp | trung bình (**giá chưa xác minh**) | thấp nhưng cần nhiều | **chưa xác minh** | rất cao |
| C6 Pháp lý VN | miễn phép | **miễn phép tần số** (`NC`) | miễn phép, EIRP giới hạn (`QCVN 54:2011`) | chưa rõ | thí điểm có trần |
| C7 Băng thông cho SOS | đủ | **đủ** (36 B, 267 ms) | thừa | thừa | đủ |
| C8 Xác thực | HMAC 64 bit | **HMAC 64 bit** | có | có | có |
| **Kết luận** | **loại** | **chọn** | loại | dự phòng | loại khỏi vai trò sóng mạng |

---

## 8. Hệ quả của quyết định (đã phản ánh vào kế hoạch và thiết kế)

1. **Điện thoại ở lại, phần mạng thì đổi.** APK Android được **kế thừa và phát triển
   tiếp** (IMU 20 Hz, phát hiện ngã, UI, GNSS). Thành **lịch sử** chỉ có: BLE
   advertising/scanning trong vai trò *mạng* và trạm thu BLE. Đầu cuối nay là
   **điện thoại + nút cầu LoRa đeo kèm**, nối bằng link cá nhân 1–2 m.
2. **Bài toán cấp phát nhẹ đi nhưng không biến mất:** chỉ cần **một nút cầu nhỏ cho
   mỗi người hoặc mỗi hộ** (không GNSS, không IMU, không màn hình), thay vì một nút
   đầy đủ cho từng người. Vẫn phải cấp phát **trước** thảm họa — đã ghi vào phạm vi
   và đạo đức của kế hoạch.
3. **Thêm một chặng vào ngân sách độ trễ** (điện thoại → link cá nhân → nút cầu →
   mesh → gateway → trạm), kéo theo **RQ6** mới về độ tin cậy của link cá nhân.
4. **Chỉ số trung tâm đổi từ byte sang airtime**, kéo theo: sức chứa gateway, tỉ lệ
   điều khiển, nghịch lý ngủ/nghe, và ngân sách độ trễ mới.
5. **Kết quả `SIM` của hướng BLE không được trích** như kết quả của hướng LoRa; chỉ
   dùng làm **giả thuyết cần kiểm lại** (H2, H3, H4 đều là bản chuyển thể).
6. **Phát hiện định hình đề tài:** điều khiển (beacon) chiếm 73–93 % airtime
   (`SUY`) — biến "tối ưu beacon" thành nội dung nghiên cứu, không phải chi tiết phụ.

---

## 9. Sổ tìm kiếm (tóm tắt)

**Nhánh WiFi mesh — truy vấn chính:** IEEE 802.11s HWMP mesh multi-hop throughput
measurement; BATMAN-adv vs 802.11s performance; Android WifiAwareManager limits;
WifiP2pManager max clients; IEEE 802.11ah survey sub-1GHz; HaLow field
characterization relays; Guifi.net/Freifunk node statistics; Puerto Rico/Nepal/Haiti
disaster mesh; Serval Project evaluation; ESP-WIFI-MESH limits; EasyMesh;
QCVN 54:2011/BTTTT 2,4 GHz EIRP; QCVN 65:2013/BTTTT 5 GHz EIRP; Thông tư
08/2021/TT-BTTTT.
**CSDL/website:** DuckDuckGo (html/lite), Bing RSS, **Crossref API**, **OpenAlex API**,
**Unpaywall API**, Semantic Scholar (bị rate-limit 429), arXiv, IEEE Xplore, MDPI,
ScienceDirect, ETSI, developer.android.com, source.android.com, docs.espressif.com,
morsemicro.com, wi-fi.org, cspl.mic.gov.vn, vanban.chinhphu.vn, rfd.gov.vn.

**Nhánh vệ tinh — truy vấn chính:** Starlink Việt Nam cấp phép/giá; Starlink Mini
specification; Starlink Direct to Cell; AST SpaceMobile; Skylo NB-IoT NTN; Iridium
SBD; 3GPP NTN Rel-17/18/19; rain fade tropical Ku-band; ITU-R P.618-14.
**CSDL/website:** Bing News RSS, trang spec sheet của Starlink, 3gpp.org, itu.int,
cổng Bộ KH&CN, báo Đảng và báo chính thống Việt Nam, Crossref.

**Nhánh LoRa/LoRaWAN, định tuyến và DTN — truy vấn chính:** LoRa range measurement
field test; LoRa flood monitoring; LoRa rain attenuation; LoRa over water; LoRa mesh
multi-hop routing; LoRaWAN capacity nodes per gateway; LoRa energy consumption
battery lifetime; LoRa disaster management; Bundle Protocol over LoRa; data mule
LoRa; hidden node LoRa listen-before-talk; LoRaWAN simulation calibration.
**Nguồn:** OpenAlex API, Crossref API, arXiv, Semantic Scholar, Europe PMC, GitHub
API; fetch trực tiếp `congbao.chinhphu.vn` (bản công báo gốc QCVN 122:2020),
`rfd.gov.vn`, `meshtastic.org`, `resources.lora-alliance.org`, `heltec.org`,
`seeedstudio.com`, `cdn-shop.adafruit.com` (datasheet SX1276), `cc.oulu.fi`
(Petäjäjärvi 2015), `eprints.lancs.ac.uk` (Bor 2016 bản sửa), `etsi.org`.
**Công cụ tái sử dụng:** bộ script trong [research_tools/](research_tools/) do nhánh
nghiên cứu tạo (`oa.py` tra OpenAlex, `gsearch.py`/`gsearch2.py`, `README.md` ghi
cách dùng) — dùng được cho các đợt khảo sát sau.

**Nhánh pháp lý 920–923 MHz (tự xác minh trong phiên, không qua subagent):**
truy vấn "Việt Nam băng tần 920-923 MHz LoRa IoT quy hoạch thông tư" và
"QCVN 122:2020/BTTTT LPWAN"; nguồn: `cspl.mic.gov.vn` (tintucid=138298 và 138249),
`lite.duckduckgo.com`, `bing.com/search`. **Ghi chú:** DuckDuckGo chặn bot sau ~10
truy vấn; trang `thuvienphapluat.vn` và một số trang MDPI chặn `curl` (403).

---

## 10. Số liệu bị CẤM dùng (chưa xác minh hoặc sai nguồn)

| Số liệu / khẳng định | Vì sao cấm |
|---|---|
| "Wi-Fi mesh đạt 10–50 km" | Không có nguồn đo bình duyệt |
| "Wi-Fi Direct tối đa 254 client" | Chỉ có trên diễn đàn, không phải tài liệu chính thức |
| "Throughput giảm đúng một nửa mỗi hop" | Không tìm thấy nguồn; số đo bình duyệt còn suy giảm mạnh hơn (n⁻¹·⁵) |
| Giá và công suất tiêu thụ của module HaLow/router/hotspot điện thoại (trong nhánh WiFi) | Không xác minh được trong phiên |
| EIRP 5 GHz theo QCVN 65:2013/BTTTT | Chỉ suy từ ETSI EN 301 893; **chưa đọc bản gốc QCVN** |
| "Wi-Fi HaLow chạy được trên Android" | Không tìm thấy nguồn — không được giả định |
| goTenna "23,1 dặm" | Là **LoRa**, không phải WiFi, và là số marketing |
| Morse Micro "33 Mbps / 43,3 Mbps / 1 km" | Quảng cáo nhà sản xuất, không phải số đo độc lập |
| Giá USD toàn cầu / gói Roam / kit Mini của Starlink; "~25–60 ms" | Trang chính thức chỉ trả về shell JS; các mức giá đó đến từ trang affiliate |
| "Giá trị lớn nhất của Iridium SBD = 340 byte" | Không tìm thấy tài liệu chính thức |
| "TR 38.821 là chuẩn Rel-17" | **Sai**: TR 38.821 thuộc **Rel-16** (`3gpp.org/DynaReport/38821.htm`) |
| "Apple Emergency SOS hoạt động ở Việt Nam" | **Sai**: trang availability không có Việt Nam |
| "Starlink Direct-to-Cell đã có ở Việt Nam" | **Sai**: giấy phép VN là mạng cố định/di động vệ tinh, không phải D2C |
| "Starlink phủ 100 % nhu cầu cứu hộ" | Chính phủ gọi đây là giải pháp **tạm thời** và sẽ điều chuyển thiết bị |
| Số liệu thiệt hại bão Yagi/lũ 2025 chưa mở toàn văn | Chỉ xác minh được tiêu đề; phải mở bài gốc trước khi trích |
| Bất kỳ tầm xa LoRa nào lấy từ mô hình không gian tự do | Mô hình free-space cho ra hàng trăm km; **sai về bản chất** cho thiết bị mặt đất. Mọi tầm xa phải là `ĐO` hoặc ghi rõ mô hình + hệ số suy hao |

**Bổ sung từ nhánh nghiên cứu LoRa (quan trọng — đã bắt được một số liệu sai đang lưu hành):**

| Số liệu / khẳng định | Vì sao cấm |
|---|---|
| **"SX1262 độ nhạy −148 dBm @ SF12/BW125"** | **Sai bản chất**: −148 dBm là của **SX1276 ở BW 7,8 kHz**. Giá trị SX1262 ở BW125 theo datasheet chip khoảng −137 dBm nhưng **chưa xác minh được** (datasheet Semtech bị login-gate) → không dùng số nào của SX1262. Bảng trong `lora.py` dùng **SX1276 đã đọc datasheet** |
| Semtech "3 mile urban / 30 mile outdoor" | Quảng cáo nhà sản xuất, không phải đo lường |
| "LoRa tới 200 dặm / 300 km" | Không có nguồn bình duyệt |
| "Pin LoRa 10 năm" (nói chung) | Không có nguồn đo; chỉ dùng khi kèm điều kiện duty cycle cụ thể — mô hình của đề tài cho ≈ 765 ngày ở chế độ ngủ (SF9) |
| LR-FHSS "11 triệu gói/ngày" | Con số lý thuyết/quảng cáo, không phải đo thực địa |
| Công thức airtime AN1200.13 "trích nguyên văn" | Tài liệu có thật nhưng **bị login-gate**; công thức trong `lora.py` được kiểm bằng giá trị đã biết (SF7/24 B ≈ 57 ms, SF12/24 B ≈ 1,48 s) chứ không trích nguyên văn |
| Đặc tả "1 % duty cycle EU868" theo ETSI | Không tìm thấy nguồn trong phiên; **ngưỡng 1 % dùng trong tài liệu này là của QCVN 122:2020/BTTTT (Việt Nam)**, đã đọc bản gốc |
| Mọi mức giá linh kiện (LilyGO, RAK, Heltec, anten) | Trang nhà bán trả 429; các mức giá thu được là nguồn thứ cấp, **chưa xác minh** |
| Chi tiết Starlink Việt Nam (ngày, giá VND) | Nguồn là báo chí, **không phải văn bản cấp phép**; dùng để lập luận loại phương án thì được, **không** trích như số liệu chính thức |

**Bổ sung từ nhánh nghiên cứu định tuyến/DTN (đã bắt thêm bốn lỗi hay gặp):**

| Số liệu / khẳng định | Vì sao cấm |
|---|---|
| **"RFC 9177 = Contact Graph Routing"** | **Sai**: RFC 9177 là *CoAP Block-Wise Transfer Options*. CGR **không có RFC riêng** (nằm ở CCSDS + bài nghiên cứu) |
| **"LoRaWAN mặc định chỉ 120 nút/3,8 ha"** | Bản MSWiM gốc ghi 120 nút **do lỗi simulator**; bản đã sửa ghi **64 nút / 3,8 ha với DER > 0,9**. Phải trích bản đã sửa và **ghi rõ phiên bản** |
| Chuyển "64 nút/3,8 ha" thành năng lực của **mesh một sóng** | Con số đó thuộc LoRaWAN, dựa trên **trực giao SF** — thứ **không tồn tại** trong mesh một kênh một SF |
| BPoL "~80 % median" | Thuộc **kịch bản 20 nút khác** (Meshtasticator); kịch bản Darmstadt 17 nút là **40–60 %** |
| "LoRaWAN Relay (TS011) là mesh" | **Không phải** — relay hai chiều device ↔ gateway, không phải định tuyến nhiều hop giữa các nút |
| Số sao GitHub | **Không phải thước đo khoa học**; chỉ dùng như chỉ dấu mức hoạt động |
| "LBT vô dụng" | Phóng đại. Bằng chứng chỉ nói **không đáng tin khi có nút ẩn** |
| DOI `10.1109/90.929850` cho Floyd & Paxson | **Sai** — đó là bài khác (Feldmann et al. về traffic demands). Đúng là `10.1109/90.944338` |
| Giá trị mặc định `Node Info Broadcast Seconds` của Meshtastic | **Chưa xác minh** — không trích. *(Giá trị **đã** xác minh sau đó: 10.800 s — xem kế hoạch §7.3)* |
| **"QCVN 122:2020 áp cho băng 433"** | **Sai** — QCVN 122 chỉ áp cho 920–923 MHz; điều kiện 433 nằm ở Phụ lục 19 Thông tư 08/2021 |
| **"Băng 433 thoáng hơn 920 về pháp lý"** | **Sai** — hai băng có điều kiện **giống hệt nhau** (25 mW ERP; 10 %/1 %) |
| **"Thông tư 08/2021 hiệu lực 18/11/2021"** | **Sai** — Điều 8 bản công báo gốc ghi **28/11/2021** |
| **"'4 tại chỗ' gồm thông tin liên lạc"** | **Sai** — Điều 4.3 Luật PCTT chỉ gồm chỉ huy / lực lượng / phương tiện-vật tư / hậu cần; liên lạc ở Điều 7.2 và 26 |
| **Thời lượng mất liên lạc (giờ) của một xã trong Yagi 2024 / lũ 11/2025** | **Không tìm thấy nguồn** |
| **Năm DOI kho dữ liệu ngã đang lưu hành** (UMAFall, KFall, FARSEEING, MobiFall, UniMiB-SHAR) | **Sai** — Crossref trỏ sang bài khác. DOI đúng: UMAFall `10.1016/j.procs.2017.06.110`; KFall `10.3389/fnagi.2021.692865`; FARSEEING `10.1186/s11556-016-0168-9`; MobiFall `10.4018/ijmstr.2014010103`; UniMiB-SHAR `10.3390/app7101101` |
| **Kho "SafeFall"** | **Không tìm thấy nguồn** mô tả kho này — **không được bịa DOI** |
| **"Bagalà 2012: 3–85 báo động giả/ngày"** | **Sai** — đúng là **22–85/24 h** và **27–84/24 h** (hai nghiên cứu con), Kangas **< 9/24 h** |
| **"Kangas 2015"** | **Không tồn tại** — bài đúng là **Kangas 2012**, `10.1016/j.gaitpost.2011.11.016` |
| **"FARSEEING có 143 ca ngã thực"** | **Sai nguồn** — FARSEEING (Klenk 2016) có 347 ghi / **208 xác minh**; **143 ca** thuộc **Palmerini 2020**, `10.3390/s20226479` |
| **Villa & Casilari 2025 như bằng chứng "on-device"** | **Không được trích** — 7 ngày thực địa có **0 ca ngã thật**, và bài **tự mâu thuẫn** về nơi chạy mô hình |
| Kaggle "Fall Detection Dataset" như dữ liệu IMU | **Sai** — đó là kho **ảnh**; và bản re-upload "KFall" trên Kaggle ghi MIT **trái giấy phép gốc** |
| "Meshtastic dùng duty cycle 1 %" | **Sai**: cấu hình EU của Meshtastic dùng **10 %/giờ**. Mức **1 %** trong tài liệu này là của **QCVN 122:2020 cho đầu cuối Việt Nam** — không lẫn hai nguồn |

---

## 11. Việc còn thiếu phải làm trước khi trích (bắt buộc)

1. ~~**Đọc bản gốc QCVN 122:2020/BTTTT**~~ → **ĐÃ XONG (2026-10-01)**: giới hạn
   **14 dBm e.r.p.** và **duty cycle 1 % (đầu cuối) / 10 % (gateway)** đã lấy từ
   bản công báo gốc và đã đưa vào kế hoạch + thiết kế.
   ~~Ngày hiệu lực của Thông tư 08/2021~~ → **ĐÃ GIẢI QUYẾT: 28/11/2021** (Điều 8 bản
   công báo gốc, đọc ngày 2026-10-01). Mâu thuẫn trước đây đã hết.
2. **Đối chiếu datasheet SX1276** → **ĐÃ XONG**: bảng độ nhạy SF6–SF12 và dòng
   Rx/Tx đã thay bằng giá trị datasheet, nhãn `GIẢ ĐỊNH` được gỡ khỏi `lora.py` và
   `node_power.py`. **Việc còn lại:** lấy datasheet **SX1262** (bị login-gate) nếu
   chọn chip này cho phần cứng — hiện bảng chỉ đúng cho SX1276.
3. **Lấy giá linh kiện 2026 có ngày + nguồn** → hoàn thiện bảng BOM. **VẪN CÒN THIẾU**
   (lilygo.cc, store.rakwireless.com, seeedstudio trả 429).
4. **Đo tầm BLE có log** (việc nhỏ) → biến lý do loại BLE từ `SUY` thành `ĐO`.
5. **Mở toàn văn các bài báo thiệt hại bão/lũ** nếu muốn trích số liệu thiệt hại.
6. **Kiểm tra điều khoản sử dụng** của các kho dữ liệu IMU (FARSEEING, "Free From
   Falls") trước khi dùng cho kiểm tra ngã thực.
7. **Đọc toàn văn 10 công trình ở §3.1 của kế hoạch** trước khi trích số liệu từ chúng
   (hiện mới chỉ xác minh tồn tại qua Crossref; riêng Petäjäjärvi 2015 và Elijah 2021
   đã được nhánh nghiên cứu đọc PDF và ghi lại số liệu).
