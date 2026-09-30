# Pháp lý băng tần & bối cảnh bão lũ cho RescueMesh-LoRa (Việt Nam)

**Ngày truy cập toàn bộ nguồn: 2026-10-01** (trừ khi ghi khác).
**Đề tài:** mesh LoRa cứu hộ, ứng viên 920–923 MHz và 433,05–434,79 MHz.
**Tài liệu liên quan:** [xác minh nguồn & quyết định sóng](xac-minh-nguon-lora-va-quyet-dinh-song.md) ·
[thiết kế v2.0](thiet-ke-he-thong-lora-v2.md) · [phụ lục vệ tinh](nghien-cuu-ve-tinh-rescuemesh-ai.md)

## 0. Cách làm & cảnh báo công cụ

- `web_search` của harness **hỏng (HTTP 401)** trong suốt phiên. DuckDuckGo (`lite.` và `html.`) trả
  **captcha chặn bot**; Bing trả kết quả gần như ngẫu nhiên với truy vấn pháp lý tiếng Việt
  (ví dụ truy vấn `"08/2021/TT-BTTTT"` trả về đầu số điện thoại và mẫu thuế).
- Ba đường lấy nguồn **dùng được thật**, đã đóng gói thành công cụ tái sử dụng trong
  [research_tools/](research_tools/):
  1. **`congbao.py`** — API JSON công khai của **Công báo điện tử Chính phủ**:
     `POST https://api-searchcongbao.chinhphu.vn/search/van-ban`
     (endpoint tìm thấy trong JS `static.mediacdn.vn/CongBao/min/main-*.min.js`; trang
     `congbao.chinhphu.vn` render bằng JS nên GET thường trả shell rỗng). Mỗi bản ghi kèm
     `danh_sach_tep_van_ban[].duong_dan` = **PDF Công báo gốc**, đây là bản được ưu tiên trích.
  2. **`gnews.py`** — Google News RSS (`news.google.com/rss/search?...&hl=vi&gl=VN`) để *phát hiện*
     tin (tiêu đề + cơ quan + ngày). **Hạn chế đã kiểm chứng:** link bài là
     `news.google.com/rss/articles/...` chạy bằng JS, **không resolve được** (302 chỉ trả lại
     news.google.com; thanh `batchexecute`/`garturlreq` trả `null`; trang trả về là shell JS).
     ⇒ phải mở toàn văn tại toà soạn.
  3. **`psearch.py`** — tìm trên trang tìm kiếm **render phía máy chủ** của toà soạn:
     VietnamNet, Tuổi Trẻ, Thanh Niên, CafeF, VTV, Dân trí. **Mẹo bắt buộc:** dùng truy vấn
     **ngắn 1–3 từ**; truy vấn dài dạng câu thường trả 0 kết quả.
- **Chặn/không đọc được:** `thuvienphapluat.vn` 403; `vneconomy.vn`, `laodong.vn` trả trang rỗng
  (không render phía máy chủ); `vov.vn` 403; `baodautu.vn` 404; `baokhanhhoa.vn` 404;
  `mic.gov.vn` không kết nối (đầu mối tần số/viễn thông nay thuộc **Bộ KH&CN**).
- **Nguyên tắc:** mỗi số liệu kèm URL + ngày + loại nguồn. Số nào chỉ xác minh được ở mức **tiêu
  đề** (chưa mở toàn văn) đều bị đánh dấu và đưa vào §G. Không tìm thấy → ghi
  **KHÔNG TÌM THẤY NGUỒN**.

### Kết luận then chốt (đọc trước)

1. **Hai băng có điều kiện pháp lý GIỐNG HỆT NHAU** về công suất và duty cycle: **cùng ≤ 25 mW ERP**
   (≈ 13,98 dBm ≈ **14 dBm ERP**) và **cùng ≤ 10 % gateway / ≤ 1 % đầu cuối**.
2. **Không có QCVN riêng cho LPWAN ở 433 MHz.** Thông tư 08/2021/TT-BTTTT đặt điều kiện cho 433
   **trực tiếp trong Phụ lục 19**; QCVN duy nhất được viện dẫn cho 433 chỉ là **giới hạn phát xạ giả**
   (**QCVN 73:2013/BTTTT**). **QCVN 122:2020/BTTTT chỉ áp cho 920–923 MHz.**
3. **Ngày hiệu lực Thông tư 08/2021 là 28/11/2021** — mâu thuẫn "18/11 vs 28/11/2021" trước đây
   **đã được giải quyết** bằng bản Công báo gốc (Điều 8).
4. **Miễn giấy phép tần số ≠ miễn mọi nghĩa vụ**: thiết bị vẫn thuộc **danh mục nhóm 2** phải
   **chứng nhận/công bố hợp quy** (Thông tư 11/2020/TT-BTTTT); và một mạng tự lập có thể chạm
   **giấy phép thiết lập mạng viễn thông dùng riêng** (Luật Viễn thông 24/2023/QH15).

---

## A. Bảng pháp lý hai băng

| Băng | Văn bản áp dụng | Công suất | Duty cycle | Nghĩa vụ | Nguồn |
|---|---|---|---|---|---|
| **433,05 – 434,79 MHz** (LPWAN) | **Thông tư 08/2021/TT-BTTTT, Phụ lục 19** (bản hiện hành: **VBHN 01/VBHN-BKHCN**, Công báo 761+762 ngày 19-6-2025, hợp nhất theo **Thông tư 01/2025/TT-BKHCN**) | **≤ 25 mW ERP** | **≤ 10 %** (Gateway) / **≤ 1 %** (đầu cuối) | • Tuân thủ pháp luật viễn thông, an toàn thông tin, bảo vệ dữ liệu<br>• Chấp nhận nhiễu có hại từ thiết bị được cấp phép; **phải dừng ngay** nếu gây nhiễu có hại (Điều 6.2)<br>• **Không** có QCVN riêng; chỉ ràng buộc **phát xạ giả 3 = QCVN 73:2013/BTTTT** | [S1], [S2], [S3] |
| **920 – 923 MHz** (LPWAN) | **Thông tư 08/2021/TT-BTTTT, Phụ lục 19** + **QCVN 122:2020/BTTTT** (ban hành bởi **Thông tư 38/2020/TT-BTTTT**, hiệu lực 01/7/2021) | **≤ 25 mW ERP** (TT08); **QCVN 122 §2.4.3.2: ≤ 14 dBm e.r.p.** | **≤ 10 %** (Access station/Gateway) / **≤ 1 %** (Sensor/End-point) — **QCVN 122 §2.4.4.2**, chu kỳ quan sát **Tobs = 1 giờ** (§2.4.4.1) | Như trên, **cộng** phát xạ giả 9 = QCVN 122:2020; **Chú thích 6** ràng buộc đặc biệt khi đặt cùng vị trí trạm gốc 880–915 MHz (≤ −98 dBm/100 kHz, hoặc −98…−36 dBm/100 kHz nếu có thỏa thuận) | [S1], [S2], [S4] |

**Ba điểm cần đọc kèm bảng:**

1. **Danh mục SRD ở cùng băng 433 bị giới hạn thấp hơn LPWAN.** Phụ lục 1 mục 39 của Thông tư
   08/2021 gộp trong băng 433,05–434,79 MHz bốn loại thiết bị: RFID, điều khiển từ xa, đo từ xa →
   **≤ 10 mW ERP**; riêng LPWAN → **≤ 25 mW ERP** ([S1], bảng Phụ lục 1). ⇒ **Việc phân loại sản
   phẩm quyết định trần công suất**: nếu thiết kế bị coi là "thiết bị đo từ xa" thì chỉ còn 10 mW ERP
   (≈ 10 dBm), mất 4 dB so với LPWAN. Đây là rủi ro pháp lý cụ thể, không phải chi tiết hình thức.
2. **Vượt 25 mW thì phải xin giấy phép tần số.** Điều 5 khoản 2 Thông tư 08/2021: LPWAN ở
   433,05–434,79 MHz công suất **trên 25 mW ERP đến 100 mW ERP**, và ở 920–923 MHz **trên 25 mW
   ERP đến 306 mW ERP**, **không được dùng miễn giấy phép** nhưng **được dùng khi có giấy phép**
   ([S1]). ⇒ Nếu về sau muốn tăng công suất để tăng tầm, đó là **thủ tục cấp phép**, không phải khe
   hở.
3. **Băng thông kênh:**
   - **433 MHz — không có giới hạn băng thông kênh trong Thông tư 08/2021.** Phụ lục 19 không nêu
     băng thông kênh; chỉ có trần công suất, duty cycle và phát xạ giả. ⇒ Chọn BW tự do, miễn tôn
     trọng phát xạ giả (QCVN 73:2013/BTTTT) và duty cycle.
   - **920 MHz — không có con số băng thông cố định, nhưng có ràng buộc "kênh khai báo".**
     QCVN 122:2020 §2.4.5.2: *kênh hoạt động được khai báo và nằm hoàn toàn trong dải tần hoạt động;
     băng thông chiếm dụng tối đa ở mức 99 % nằm trong kênh hoạt động* ([S4]). ⇒ Nhà sản xuất **tự
     khai báo OCW**, OBW phải nằm trong OCW, OCW phải nằm trong 920–923 MHz. Thực tế với LoRa
     BW125/BW250 điều này thỏa mãn dễ dàng.
   - **Hệ quả cho so sánh:** luận điểm "433 rẻ vì không bị QCVN ràng buộc" đúng một nửa — nó không bị
     ràng buộc về băng thông, nhưng cũng **mất luôn con đường đo kiểm/đối chiếu chuẩn hoá** mà
     QCVN 122 mang lại cho 920.

**Bối cảnh quy hoạch tần số (để hiểu vì sao 433 phải "chấp nhận nhiễu"):**
**Quyết định 37/2025/QĐ-TTg ngày 03/10/2025** ban hành Quy hoạch phổ tần số vô tuyến điện quốc gia
([S5]) giữ **chú thích 5.138**: băng **433,05–434,79 MHz (tần số trung tâm 433,92 MHz) ở Khu vực 1**
được dành cho **ứng dụng Công nghiệp – Khoa học – Y tế (ISM)**, kèm điều kiện phải có phép đặc biệt
của cơ quan quản lý. Việt Nam ở **Khu vực 3**, và băng này **không xuất hiện như một phân chia chính
trong bảng phân chia cho LPWAN** — tức quyền dùng đến từ **danh mục miễn giấy phép**, không phải từ
phân chia quy hoạch. Đây là lý do gốc của nghĩa vụ "chấp nhận nhiễu".
*Ghi nhận một chi tiết đáng lưu ý:* Điều 6.3 Thông tư 08/2021 liệt kê các băng ISM mà thiết bị miễn
giấy phép phải chấp nhận nhiễu (13,553–13,567 MHz; 26,957–27,283 MHz; 40,66–40,70 MHz;
2400–2483,5 MHz; 5725–5875 MHz; 24000–24250 MHz) và **không có 433,05–434,79 MHz trong danh sách
đó** ([S1]). Tôi ghi nhận nguyên văn, không suy diễn hệ quả pháp lý.

---

## B. Quy định mesh ngoài trời / khai báo thiết bị

### B.1. Không có quy định riêng cho mesh/relay ngoài trời

**Thông tư 08/2021/TT-BTTTT quy định theo *thiết bị* và *băng tần*, không theo *kiến trúc mạng*.**
Tìm trong toàn văn bản Công báo **không có** từ khoá nào về mesh, relay, multi-hop, chuyển tiếp, hay
"mạng ngoài trời". Nghĩa vụ pháp lý gắn vào: (a) thiết bị có thuộc danh mục miễn giấy phép không,
(b) thiết bị có đáp ứng điều kiện kỹ thuật của phụ lục tương ứng không, (c) người dùng có gây nhiễu
có hại không.
⇒ **Kết luận:** một mạng mesh LoRa nhiều hop ngoài trời **không có giấy phép riêng cho "mesh"**; nó
được đánh giá qua từng thiết bị. Đây là điểm có lợi cho dự án, nhưng cũng là **khoảng trống pháp lý**
(xem §F).

### B.2. Miễn giấy phép tần số KHÔNG kèm thủ tục khai báo/đăng ký

Tìm toàn văn Thông tư 08/2021 (bản Công báo gốc và bản hợp nhất 2025): **không có** bất kỳ điều khoản
"khai báo", "đăng ký" nào đối với thiết bị được miễn giấy phép ([S1], [S2]). Nghĩa vụ duy nhất là
**điều kiện khai thác** (Điều 6): chấp nhận nhiễu; dừng ngay nếu gây nhiễu có hại; với thiết bị có thể
chạy nhiều mức công suất/nhiều băng, **phải cài đặt cố định thông số tần số và công suất** theo quy
định khi sử dụng, sản xuất, nhập khẩu tại Việt Nam (Điều 6.4) — chi tiết này áp dụng trực tiếp cho
board LoRa bán sẵn có thể chỉnh công suất/băng.

### B.3. NHƯNG: thiết bị vẫn phải chứng nhận / công bố hợp quy

Đây là nghĩa vụ thật, thường bị bỏ qua khi nói "miễn giấy phép":

- **Thông tư 11/2020/TT-BTTTT** quy định Danh mục sản phẩm, hàng hoá **nhóm 2** (có khả năng gây mất
  an toàn) thuộc trách nhiệm Bộ TT&TT ([S11]).
- Trong Danh mục, **mục 3 "Thiết bị phát, thu – phát vô tuyến cự ly ngắn"**; mục 3.1 "dùng cho mục
  đích chung" chỉ rõ: **cho thiết bị hoạt động tại dải tần 25 MHz – 1 GHz áp dụng
  QCVN 73:2013/BTTTT** (và QCVN 96:2015/BTTTT), còn 9 kHz – 25 MHz áp dụng QCVN 55:2011/BTTTT
  ([S11], phụ lục Danh mục).
- ⇒ **Băng 433,05–434,79 MHz nằm trong 25 MHz – 1 GHz**, nên thiết bị SRD/LPWAN ở 433 **thuộc đối
  tượng phải chứng nhận hợp quy và công bố hợp quy**, theo **QCVN 73:2013/BTTTT**.
- Với thiết bị 920–923 MHz: ngoài LPWAN còn có mã HS riêng trong **Phụ lục D QCVN 122:2020**, và
  Thông tư 38/2020 nêu rõ quy chuẩn áp dụng cho sản phẩm, hàng hoá LPWAN theo mã HS đó ([S4]).

**Lưu ý về độ chắc chắn:** tôi **đã đọc trực tiếp** bảng Danh mục của Thông tư 11/2020 nêu ánh xạ
dải tần → QCVN, nhưng **chưa mở trang bìa QCVN 73:2013/BTTTT** để đọc tên đầy đủ của nó. Tên/tiêu đề
đầy đủ của QCVN 73:2013/BTTTT: **KHÔNG TÌM THẤY NGUỒN trực tiếp trong phiên** (đã thử API Công báo,
các thông tư 2013 ban hành QCVN). Chỉ dùng **số hiệu** (đã có nguyên văn từ [S1], [S2], [S11]); không
phát biểu tên đầy đủ.

### B.4. Rủi ro lớn nhất khi mở rộng: giấy phép "mạng viễn thông dùng riêng"

Đây là phần **quan trọng nhất của §B** và là rủi ro mà tài liệu trước chưa nêu.

**Luật Viễn thông 24/2023/QH15** (Công báo 29+30 ngày 05-01-2024):

- **Điều 3 khoản 16** — "Mạng viễn thông dùng riêng là mạng viễn thông do **tổ chức** hoạt động tại
  Việt Nam thiết lập để cung cấp dịch vụ viễn thông, dịch vụ ứng dụng viễn thông cho **các thành viên
  của mạng** không nhằm mục đích sinh lợi trực tiếp từ hoạt động của mạng."
- **Điều 19 khoản 5** — trừ mạng phục vụ cơ quan Đảng/Nhà nước (k.3) và quốc phòng/an ninh (k.4),
  tổ chức thiết lập mạng viễn thông dùng riêng **phải có giấy phép thiết lập mạng viễn thông dùng
  riêng** nếu thuộc: (a) có **đường truyền dẫn hữu tuyến** do tổ chức xây dựng; (b) **thành viên của
  mạng là tổ chức, cá nhân có cùng mục đích, tính chất hoạt động và được liên kết với nhau bằng điều
  lệ hoặc hình thức khác**; (c) mạng vô tuyến dùng riêng cho tổ chức hưởng quyền ưu đãi, miễn trừ
  ngoại giao; **(d) các mạng viễn thông dùng riêng khác** (điều khoản "hứng" mở).
- **Điều 42 khoản 4** — **được MIỄN** giấy phép viễn thông, đăng ký, thông báo khi: "Mạng viễn thông
  dùng riêng mà **các thành viên mạng trực thuộc cùng một tổ chức** và **không tự thiết lập đường
  truyền dẫn viễn thông**."

**Suy luận (`SUY`, không phải nguyên văn luật — cần Cục Viễn thông xác nhận):**

| Mô hình triển khai RescueMesh | Khả năng chạm Điều 19.5 | Vì sao |
|---|---|---|
| Mạng vô tuyến **trong nội bộ một tổ chức** (ví dụ đội cứu hộ của một xã/phường, một trường), **không có tuyến hữu tuyến tự xây** | **Có thể thuộc diện miễn – Điều 42.4** | Thành viên cùng một tổ chức, không tự xây đường truyền hữu tuyến |
| Mạng **liên kết nhiều tổ chức/cá nhân** (ví dụ nhiều xã, nhiều hội, nhiều hộ dân) cùng mục đích, có điều lệ/thỏa thuận | **Nhiều khả năng thuộc Điều 19.5(b)** → cần giấy phép thiết lập mạng | Đúng mô tả "liên kết bằng điều lệ hoặc hình thức khác" |
| Mạng có **bất kỳ đoạn hữu tuyến nào tự xây** (cáp quang nối các gateway) | **Điều 19.5(a)** → cần giấy phép | "có đường truyền dẫn hữu tuyến do tổ chức xây dựng" |
| Bị coi là "mạng khác" | **Điều 19.5(d)** — điều khoản mở, không xác định trước được | Rủi ro diễn giải |

**Điểm mấu chốt cần nói thẳng:** **"miễn giấy phép sử dụng tần số" không đồng nghĩa "miễn giấy phép
viễn thông".** Hai chế độ pháp lý độc lập: tần số (Thông tư 08/2021) và thiết lập mạng (Luật Viễn
thông). Một mesh vô tuyến tự lập vẫn có thể phải xin **giấy phép thiết lập mạng viễn thông dùng
riêng** dù từng thiết bị đều hợp pháp về tần số. **KHÔNG TÌM THẤY NGUỒN** văn bản nào của cơ quan quản
lý hướng dẫn cụ thể trường hợp **mạng mesh cộng đồng/cứu hộ tình nguyện** — đây là khoảng trống §F.

---

## C. Bối cảnh bão lũ (có nguồn mở được)

### C.1. Bão Yagi (bão số 3), tháng 9/2024 — thiệt hại viễn thông

Nguồn **đã mở toàn văn**: [S15] CafeF (09-09-2024 09:47, dẫn nguồn markettimes.vn, số liệu từ
**Bộ Thông tin và Truyền thông**).

| Sự kiện | Số liệu | Nguồn | Đã mở toàn văn? |
|---|---|---|---|
| Cột viễn thông bị gãy đổ | **27 cột** | [S15] | ✅ có |
| Vị trí mất liên lạc di động do mất điện | **6.285 vị trí** (tiêu đề bài ghi "hơn 6.280") | [S15] | ✅ có (nêu **cả hai** con số) |
| Cáp quang liên tỉnh bị đứt | **7 tuyến** | [S15] | ✅ có |
| Truyền dẫn nội tỉnh bị đứt | **12 tuyến** | [S15] | ✅ có |
| Thuê bao nhận tin nhắn cảnh báo | **hơn 32 triệu thuê bao** | [S15] | ✅ có |
| Cán bộ ứng cứu thông tin | **gần 7.000 cán bộ**, trực 24/24 | [S15] | ✅ có |
| Máy phát điện bổ sung cho trạm BTS | **284 máy phát điện** + nhiên liệu dự trữ | [S15] | ✅ có |
| Roaming giữa các nhà mạng | Quảng Ninh, Hải Phòng, Thái Bình, Hải Dương, Hưng Yên, Bắc Giang, Bắc Ninh | [S15] | ✅ có |
| Thiệt hại về người trong ngành viễn thông | **không có** | [S15] | ✅ có |
| Thuê bao cố định gián đoạn | Hải Phòng và Quảng Ninh "nhiều thuê bao cố định bị gián đoạn" (định tính) | [S15] | ✅ có |

**Các số liệu Yagi KHÁC chỉ xác minh được ở mức tiêu đề — xem §G, KHÔNG dùng:**
"Cục Viễn thông: còn khoảng **8 %** số trạm phát sóng bị mất liên lạc vì bão" (VnEconomy,
14-09-2024); "**2/3** số trạm thu phát sóng bị ảnh hưởng đã được khôi phục" (VTV, 13-09-2024);
"Đã khôi phục **hơn 3000** trạm phát sóng di động sau bão Yagi" (VTV, 10-09-2024). Cả ba đến từ
Google News RSS [S23] và **toà soạn chưa mở được** (`vneconomy.vn` trả trang rỗng).

### C.2. Lũ miền Trung, tháng 11/2025 — số người chết/mất tích (số liệu **lệch nhau theo thời gian**)

Chuỗi số liệu **tăng dần** vì báo cáo nhanh cập nhật liên tục. **Nêu cả hai nguồn khi lệch.**

| Mốc | Số liệu | Cơ quan dẫn nguồn | Nguồn | Đã mở toàn văn? |
|---|---|---|---|---|
| 21-11-2025 | **50** người chết và mất tích; thiệt hại 3.000 tỷ đồng | (bài Báo Biên phòng) | [S23] (tiêu đề) | ❌ chưa |
| 22-11-2025 | **85** người chết và mất tích | **Cục Quản lý đê điều và Phòng, chống thiên tai** | [S18] Thanh Niên | ✅ có (tiêu đề + dẫn nguồn) |
| 23-11-2025 | **102** người chết và mất tích (riêng Đắk Lắk **63** người chết) | Cục Quản lý đê điều và PCTT | [S23]/Tuổi Trẻ (tiêu đề) | ❌ chưa |
| 24-11-2025 (6h) | **91 chết + 11 mất tích = 102**; Đắk Lắk 63 chết, 8 mất tích | **báo cáo nhanh của Cục Quản lý đê điều và PCTT** | [S17] Tuổi Trẻ | ✅ có (toàn văn) |
| 26-11-2025 | **108** người chết và mất tích | (bài Lao Động) | [S23] (tiêu đề) | ❌ chưa |
| Cả năm 2025 | **~480** người chết và mất tích; thiệt hại **~105.000 tỷ đồng** | (bài An ninh Thủ đô 01-04-2026) | [S23] (tiêu đề) | ❌ chưa |

> **Đọc bảng này thế nào:** con số **102** (91 chết + 11 mất tích, mốc 6h ngày 24-11) là số liệu
> **đầy đủ nhất tôi đã mở toàn văn và có cơ quan dẫn nguồn rõ**. Con số **85** (22-11) và **108**
> (26-11) là mốc trước/sau, **chỉ có tiêu đề**. Khi trích, nên ghi kèm **mốc thời gian**, vì cùng một
> sự kiện cho ba con số khác nhau ở ba thời điểm — đây là đặc điểm của báo cáo nhanh, không phải mâu
> thuẫn sai.

**Quy mô thiệt hại kèm theo (từ [S17], toàn văn, mốc 6h ngày 24-11-2025):**
221 nhà sập đổ, 933 nhà hư hỏng, **gần 201.000 nhà bị ngập** (Gia Lai 19.200; Đắk Lắk 150.000;
Khánh Hòa gần 37.000; Lâm Đồng hơn 1.100); 82.000 ha lúa/hoa màu, hơn 117.000 ha cây lâu năm,
1.157 ha thuỷ sản thiệt hại; hơn 3,3 triệu con gia súc/gia cầm chết, cuốn trôi; thiệt hại kinh tế
ước **13.078 tỷ đồng** (Đắk Lắk ~5.330 tỷ; Khánh Hòa ~5.000 tỷ); hỗ trợ khẩn cấp **1.100 tỷ đồng**
(ký ngày 23-11).

### C.3. "Không điện, không sóng" — số liệu định lượng mở được

| Sự kiện | Số liệu | Mốc | Nguồn | Đã mở toàn văn? |
|---|---|---|---|---|
| **Mất điện** vùng lũ miền Trung | **hơn 258.000 người** ở Gia Lai, Đắk Lắk, Khánh Hòa | 24-11-2025 | [S17] Tuổi Trẻ (dẫn Cục Quản lý đê điều & PCTT) | ✅ có |
| **Trạm BTS mất kết nối** | **343 trạm BTS** ở Đắk Lắk và Khánh Hòa | 24-11-2025 | [S17] | ✅ có |
| Cảnh "cách ly thông tin hoàn toàn" | định tính: "hàng loạt khu dân cư mất điện, mất sóng… nhiều người dân giữa vùng nguy hiểm rơi vào cảnh cách ly thông tin hoàn toàn" | 19–20/11/2025 | [S16] VietnamNet | ✅ có |
| Trạm BTS mất điện đồng loạt; cáp quang bị nước cuốn/sạt lở đứt | định tính (VNPT) | 19–20/11/2025 | [S16] | ✅ có |
| Khôi phục: "hơn 95 % trạm BTS bị ngập, phủ sóng di động đạt 98 %" | 95 % / 98 % | 25-11-2025 | Báo Khánh Hòa — [S23] tiêu đề | ❌ **chưa mở** |
| "Dải đất miền Trung không còn xã trắng sóng" | định tính | 03-11-2025 | Viettel Family — [S23] tiêu đề | ❌ chưa — **và thuộc đợt lũ ĐẦU tháng 11, KHÔNG phải đợt 19–24/11**; không được gộp |

**Thời gian mất liên lạc:** tôi **KHÔNG TÌM THẤY NGUỒN** nào công bố **thời lượng mất liên lạc** (số
giờ) cho một xã/điểm cụ thể trong đợt 11/2025. Các bài có mô tả định tính ("xuyên đêm", "trong hai
ngày 19 và 20/11") nhưng **không có số giờ đo được**. Với Yagi 2024 cũng vậy — "48 giờ cứu hộ viễn
thông sau bão Yagi" (Lao Động, 10-09-2024) là **tiêu đề chưa mở** ⇒ không dùng làm số liệu thời gian.

---

## D. Sáng kiến liên lạc khẩn cấp hiện có ở VN

### D.1. Khung pháp lý chính thức về liên lạc PCTT (mới, quan trọng)

**Thông tư 14/2025/TT-BKHCN ngày 08/8/2025**, hiệu lực **22/9/2025**, thay thế Thông tư
17/2012/TT-BTTTT và Thông tư 17/2019/TT-BTTTT ([S6], đọc toàn văn Công báo). Đây là **văn bản hiện
hành** cho "tổ chức và đảm bảo thông tin liên lạc phục vụ chỉ đạo, điều hành phòng, chống thiên tai".

| Nội dung | Nguyên văn / tóm tắt | Ý nghĩa với RescueMesh |
|---|---|---|
| **Điều 4.1 — nguyên tắc** | "Đảm bảo thông tin liên lạc phòng, chống thiên tai với **ưu tiên cao nhất**, an toàn, tin cậy, nhanh chóng. **Ưu tiên sử dụng mạng lưới tại chỗ** để triển khai hoạt động chỉ đạo, điều hành phòng, chống thiên tai." | **Đây là câu neo pháp lý mạnh nhất cho định hướng "mạng tại chỗ"** — nhưng "mạng lưới tại chỗ" trong thông tư được hiểu là mạng của địa phương/doanh nghiệp, không phải mesh dân sự tự phát |
| **Điều 3.2 — "mạng viễn thông dùng riêng" cho PCTT** | Mạng do Nhà nước đầu tư, thiết lập tại **Cục Bưu điện Trung ương** và **VNPT**, gồm: (a) hệ thống viễn thông **cố định vệ tinh**; (b) hệ thống viễn thông **di động vệ tinh**; (c) hệ thống viễn thông **vô tuyến điện**; (d) hệ thống truyền hình hội nghị; (đ) **xe ô tô chuyên dùng phục vụ thông tin** | Giải pháp nhà nước dựa trên **VSAT + vô tuyến chuyên dùng + xe thông tin**, không dựa trên mesh cộng đồng |
| **Điều 6.2 — khi mạng công cộng mất liên lạc** | Liên lạc từ trụ sở Chính phủ / Ban Chỉ đạo PTDS quốc gia tới **Ban Chỉ huy PTDS tỉnh, thành phố và địa phương cấp xã** được bảo đảm **chủ yếu bằng hệ thống viễn thông di động vệ tinh, cố định vệ tinh và hệ thống viễn thông vô tuyến điện**; khi di chuyển ra ngoài trụ sở dùng **di động vệ tinh + vô tuyến điện** | Cấp **xã** được nêu tường minh là điểm cần bảo đảm liên lạc |
| **Điều 12.6 — nghĩa vụ doanh nghiệp** | "Tại **mỗi xã** thuộc khu vực **thường xuyên xảy ra thiên tai**, căn cứ lịch sử thiên tai **5 năm** trở lại, các doanh nghiệp cần phối hợp triển khai **ít nhất 01 trạm BTS kiên cố chịu được rủi ro thiên tai cấp 4**… Cung cấp danh sách… trước **tháng 6 hàng năm**." | Chiến lược nhà nước = **gia cố BTS**, không phải mạng thay thế |
| **Điều 12.4–12.5** | Sẵn sàng phương án **nhắn tin** và **roaming** khi có yêu cầu của Thủ tướng / Ban Chỉ đạo PTDS quốc gia / Bộ KH&CN | Tin nhắn khẩn cấp và roaming là **công cụ chính thức** |

**Chú ý về "4 tại chỗ":** **Luật Phòng, chống thiên tai** (bản hợp nhất **21/VBHN-VPQH ngày
26/02/2025**), **Điều 4 khoản 3** quy định nguyên văn: *"Phòng, chống thiên tai được thực hiện theo
phương châm **bốn tại chỗ**: chỉ huy tại chỗ; lực lượng tại chỗ; phương tiện, vật tư tại chỗ; hậu cần
tại chỗ."* ([S8]) ⇒ **"thông tin liên lạc" KHÔNG phải một trong bốn "tại chỗ"**. Liên lạc xuất hiện ở
**Điều 7.2** (hệ thống thông tin phục vụ PCTT: hạ tầng thông tin công cộng + trang thiết bị chuyên
dùng cho chỉ đạo chỉ huy + quan trắc tự động truyền tin + hệ thống cảnh báo sớm) và ở **Điều 26**
(biện pháp ứng phó: *"Bảo đảm giao thông và thông tin liên lạc đáp ứng yêu cầu chỉ đạo, chỉ huy
phòng, chống thiên tai"*). ⇒ Nếu tài liệu dự án viết "4 tại chỗ gồm cả thông tin liên lạc" thì đó là
**sai so với luật**; cách viết đúng là "bốn tại chỗ theo luật **không** liệt kê liên lạc; liên lạc là
nghĩa vụ riêng tại Điều 7 và Điều 26".

**Số liệu khẩn cấp dùng chung:** **Quyết định 226/QĐ-TTg ngày 04/02/2016** phê duyệt Đề án "tổ chức
thông tin liên lạc khẩn cấp dùng chung cho các tình huống tìm kiếm, cứu nạn" ([S7], đọc toàn văn):
thiết lập **số 112** toàn quốc, **kết nối các hệ thống 113/114/115** và hệ thống thông tin tìm kiếm
cứu nạn trên biển.

### D.2. Viettel / VNPT / MobiFone khi mất sóng (số liệu mở được, đợt 19–20/11/2025)

Nguồn **đã mở toàn văn**: [S16] VietnamNet (20-11-2025 20:34, tác giả Thái Khang), dẫn đại diện ba
nhà mạng.

| Nhà mạng | Giải pháp | Số liệu cụ thể |
|---|---|---|
| **Viettel** | Máy phát điện cơ động; ắc quy dự phòng; **điện thoại vệ tinh**; **bộ đàm cầm tay**; **xe phát sóng cơ động**; **drone** vận tải + flycam tìm kiếm cứu nạn; roaming hai chiều; gói hỗ trợ liên lạc khẩn cấp | **gần 6.000** máy phát điện cơ động (Đắk Lắk, Gia Lai, Khánh Hòa); **hơn 1.900** bình ắc quy dự phòng; **17** điện thoại vệ tinh; **48** bộ đàm cầm tay; **9** xe phát sóng cơ động; **4** drone vận tải (riêng Khánh Hòa) |
| **VNPT** | Khắc phục sự cố xuyên đêm; **roaming hai chiều** tại Khánh Hòa, Đắk Lắk, Gia Lai; mở điểm giao dịch xuyên đêm cho dân trú mưa, **sạc điện thoại**, hỗ trợ liên lạc | định tính + "hàng trăm kỹ sư, vật tư, thiết bị" |
| **MobiFone** | Kích hoạt toàn bộ kịch bản ứng cứu; phối hợp **công an địa phương** tiếp cận trạm bị cô lập; **châm nhiên liệu** duy trì trạm; tặng tiền vào tài khoản khuyến mại | **30.000 đồng** vào tài khoản KM3T, dùng gọi/nhắn tin trong **3 ngày**, áp dụng cả khách roaming |

⇒ **Kết luận D.2:** bộ giải pháp hiện có của VN là **gia cố BTS + máy phát điện + ắc quy + roaming +
tin nhắn khẩn cấp + VSAT/điện thoại vệ tinh + xe phát sóng + drone**. Đây **chính là nhóm "liên lạc
chuyên dùng của nhà nước/doanh nghiệp"** mà Thông tư 14/2025 mô tả. **Không có** sáng kiến chính
thức nào dùng **mesh vô tuyến cộng đồng** hoặc **băng tần miễn giấy phép** cho vai trò này.

### D.3. Radio nghiệp dư (ham)

- **Tồn tại và được quản lý chặt, KHÔNG miễn giấy phép.** **Nghị định 63/2023/NĐ-CP** (18/8/2023,
  quy định chi tiết Luật Tần số VTĐ) quy định: **đài vô tuyến điện nghiệp dư** (Điều 3), **khai thác
  viên vô tuyến điện nghiệp dư** phải có **chứng chỉ vô tuyến điện nghiệp dư** (Điều 3 khoản 19),
  hồ sơ cấp giấy phép cho đài nghiệp dư (Điều 12, gồm bản sao chứng chỉ), thời hạn xử lý **14 ngày**,
  và **Điều 41** cho phép chủ sở hữu đài nghiệp dư **cho thuê, cho mượn** đài **đã được cấp giấy phép**
  ([S10], đọc toàn văn Công báo).
- **Nghiệp vụ Nghiệp dư được thừa nhận trong quy hoạch tần số.** **Quyết định 37/2025/QĐ-TTg** có
  định nghĩa "Nghiệp vụ Nghiệp dư (Amateur Service)", "Đài vô tuyến điện nghiệp dư", "Nghiệp dư qua
  vệ tinh", và **các băng phân chia cho NGHIỆP DƯ** trong bảng (ví dụ **47–47,2 MHz; 76–77,5 MHz;
  77,5–78 MHz; 134–136 MHz**) ([S5]).
- **KHÔNG TÌM THẤY NGUỒN** về **vai trò chính thức của radio nghiệp dư trong phòng chống thiên tai
  Việt Nam**: Thông tư 14/2025/TT-BKHCN **không** nhắc "nghiệp dư"; Luật Phòng, chống thiên tai
  **không** nhắc; không tìm thấy văn bản nào giao nhiệm vụ PCTT cho mạng nghiệp dư. (Có tin tiêu đề
  "Bộ trưởng Bộ KH&CN được thu hồi chứng chỉ vô tuyến điện viên nghiệp dư" — LuatVietnam 08-09-2026,
  [S24] — chỉ xác nhận **cơ chế chứng chỉ đang được sửa đổi**, không phải vai trò PCTT.)
- **Hệ quả cho dự án:** **không được** dựa vào ham radio như một kênh "miễn phí, sẵn có" — hợp pháp
  hay không phụ thuộc **giấy phép đài + chứng chỉ cá nhân**, khác hẳn băng LPWAN miễn giấy phép.

---

## E. Starlink: văn bản chính thức

Toàn bộ mục này **kế thừa từ phụ lục vệ tinh đã xác minh 2026-09-30** trong
[nghien-cuu-ve-tinh-rescuemesh-ai.md](nghien-cuu-ve-tinh-rescuemesh-ai.md) (§A.2, A15–A30), và tôi
**đã kiểm tra lại 4 URL chính thức trả HTTP 200 ngày 2026-10-01**.

| Mốc / nội dung | Văn bản / nguồn chính thức | Ngày | Trạng thái |
|---|---|---|---|
| **Thí điểm có kiểm soát** dịch vụ viễn thông dùng vệ tinh quỹ đạo tầm thấp, **không giới hạn tỉ lệ sở hữu nước ngoài** | **Quyết định số 659/QĐ-TTg** (Thủ tướng) | 26-03-2025 | ✅ chính thức (Báo Điện tử Chính phủ) |
| **Thời hạn thí điểm** | 5 năm kể từ ngày pháp nhân VN được cấp giấy phép kinh doanh dịch vụ viễn thông; **phải kết thúc trước 01-01-2031** | — | ✅ chính thức |
| **Giấy phép sử dụng tần số và thiết bị vô tuyến điện** cấp cho **Công ty TNHH Starlink Services Việt Nam** | **Cục Tần số vô tuyến điện** (Bộ KH&CN) | **13-02-2026** | ✅ chính thức — [S20] mst.gov.vn |
| **02 giấy phép viễn thông** (loại mạng viễn thông **cố định vệ tinh** và **di động vệ tinh**) | **Cục Viễn thông** | **13-02-2026** | ✅ chính thức — [S21] baochinhphu.vn |
| **Lễ trao giấy phép** tại Washington D.C. | Bộ KH&CN trao cho Starlink Services Việt Nam | tối **18-02-2026** | ✅ chính thức — [S21] |
| **Trần thiết bị / quy mô giai đoạn đầu** | **4 trạm cổng (gateway)** và **tối đa 600.000 thiết bị đầu cuối** | 2026 | ✅ chính thức — [S20]; lặp lại bởi Cục Viễn thông (báo chí) |
| **Thương mại hoá tại VN** | Starlink chính thức cung cấp dịch vụ | **13-08-2026** | ⚠️ **báo chí** (VietnamNet), không phải văn bản cấp phép |
| **Chủ trương: chỉ là giải pháp TẠM THỜI, sẽ điều chuyển thiết bị khi có sóng mặt đất** | "Starlink được xác định là **giải pháp kết nối tạm thời** trong thời gian chờ hoàn thiện hạ tầng viễn thông mặt đất. Sau khi các khu vực được phủ sóng di động, thiết bị sẽ được xem xét **điều chuyển** đến địa bàn khác" | 2026 | ✅ **báo Đảng** — [S22] dangcongsan.vn (Thanh Hóa, 28–29/09/2026 lắp 9 bộ Standard 4X) |
| **Quy mô "vùng lõm sóng"** | **273 thôn** và **117 điểm** lõm sóng/sóng yếu tại **13 tỉnh, thành**; cam kết hỗ trợ **1.000 bộ thiết bị + miễn phí 6 tháng** | 11-09-2026 | ⚠️ **báo chí dẫn Cục Viễn thông**, không phải văn bản |
| **Direct-to-Cell (D2C)** | **KHÔNG có tại Việt Nam** — giấy phép VN là mạng cố định/di động vệ tinh, không phải D2C tới thuê bao di động mặt đất; Apple Emergency SOS **không phủ VN** | — | ✅ (kiểm chứng phủ định) |

**Phần CHƯA XÁC MINH (đánh dấu rõ):**
- **Giá cước** (1.131.990 đ/tháng gói ~100 Mbps; 1.711.100 đ/tháng gói >400 Mbps; tổng đơn
  ~10.848.800 đ) — **báo chí dẫn trang Starlink**, không phải văn bản; trang `starlink.com` chỉ trả
  shell JS. **Không** dùng như số liệu chính thức.
- **Ngày thương mại 13-08-2026** — báo chí, chưa thấy quyết định/văn bản.
- **Số điều/khoản của Luật Viễn thông hoặc nghị định về VSAT** — **KHÔNG TÌM THẤY NGUỒN** ⇒ không
  trích số điều.
- **Dung lượng an toàn / ngẽn khi đông người dùng trên một terminal trong thảm họa** —
  **KHÔNG TÌM THẤY NGUỒN** cho cả nhà sản xuất và nghiên cứu.
- **Đo rain fade tại chính Việt Nam** — **KHÔNG TÌM THẤY NGUỒN**.

---

## F. Khoảng trống

**Khoảng trống pháp lý (mới phát hiện trong phiên này — quan trọng nhất):**

1. **Không có QCVN cho LPWAN ở 433,05–434,79 MHz.** Không có văn bản tương đương QCVN 122:2020 để
   đo kiểm/đối chiếu cho 433. Chỉ có ràng buộc phát xạ giả theo QCVN 73:2013/BTTTT. ⇒ Không có
   "đường hợp quy hoá" rõ ràng cho một sản phẩm LPWAN 433 mới.
2. **Không có hướng dẫn của cơ quan quản lý về mạng mesh/relay cộng đồng.** Ranh giới giữa **Điều
   42.4 Luật Viễn thông** (miễn giấy phép, nếu cùng một tổ chức và không tự xây đường truyền) và
   **Điều 19.5(b)/(d)** (phải có giấy phép thiết lập mạng dùng riêng) **chưa được làm rõ** cho trường
   hợp mạng cứu hộ tình nguyện nhiều xã. **KHÔNG TÌM THẤY NGUỒN** giải thích chính thức.
3. **Không có văn bản nào giao vai trò PCTT cho radio nghiệp dư hoặc cho băng tần miễn giấy phép**
   trong liên lạc khẩn cấp. Thông tư 14/2025 chỉ nói tới mạng dùng riêng của Nhà nước
   (Cục Bưu điện Trung ương + VNPT) và nghĩa vụ của doanh nghiệp viễn thông.
4. **Không có định nghĩa/ngưỡng nào cho "mạng lưới tại chỗ"** trong Thông tư 14/2025 (Điều 4.1) —
   thuật ngữ được dùng nhưng không giải thích tại Điều 3. ⇒ Không thể khẳng định mesh của dự án
   "thuộc mạng lưới tại chỗ" theo nghĩa của thông tư.

**Khoảng trống kỹ thuật / đo lường:**

5. **Chưa có công bố nào đo tầm xa LoRa tại chính Việt Nam** (xác nhận lại trong phiên này; cũng đã
   ghi ở tài liệu trước).
6. **Chưa có so sánh 433 MHz vs 920 MHz đo tại Việt Nam** (tầm, suy hao, nhiễu nền, tỉ lệ mất gói).
   **KHÔNG TÌM THẤY NGUỒN.**
7. **Chưa có đo LoRa trong điều kiện ngập thực tế** (đường truyền ngang/vắt qua vùng ngập, anten thấp).
8. **Chưa có số liệu độ đông đúc phổ tần thực đo ở 433,05–434,79 MHz tại Việt Nam** (mật độ thiết bị
   điều khiển từ xa, RFID, đo từ xa dùng chung băng) — đây là biến số quyết định chất lượng mesh 433
   nhưng **KHÔNG TÌM THẤY NGUỒN**.
9. **Chưa có số liệu thời lượng mất liên lạc** (giờ) của một xã/điểm cụ thể trong Yagi 2024 và lũ
   11/2025 — xem §C.
10. **Số xã/bản mất liên lạc hoàn toàn** trong Yagi 2024 — **KHÔNG TÌM THẤY NGUỒN** (chỉ có "vị trí mất
    liên lạc", "trạm mất kết nối").

---

## G. Số liệu KHÔNG được dùng

| Số liệu / khẳng định | Vì sao cấm |
|---|---|
| **"QCVN 122:2020/BTTTT áp dụng cho cả băng 433,05–434,79 MHz"** | **SAI.** QCVN 122 chỉ áp cho **920–923 MHz** ([S4]); điều kiện 433 nằm ở Phụ lục 19 Thông tư 08/2021 ([S1], [S2]) |
| **"Băng 433 được phát công suất cao hơn 920"** / "433 thoáng hơn về công suất" | **SAI.** Cả hai đều **≤ 25 mW ERP** và **cùng duty cycle 10 %/1 %** ([S1], [S2]) |
| **"Thông tư 08/2021 có hiệu lực 18/11/2021"** | **SAI.** Công báo gốc Điều 8: **28/11/2021** ([S1], [S2]); bài Vụ Pháp chế cũng ghi 28/11/2021 ([S13]) |
| **"4 tại chỗ gồm cả thông tin liên lạc"** | **SAI so với luật.** Điều 4.3 Luật PCTT chỉ có 4 nội dung: chỉ huy, lực lượng, phương tiện-vật tư, hậu cần ([S8]) |
| **"Thiết bị miễn giấy phép tần số thì không phải làm gì thêm"** | **SAI.** Vẫn phải **chứng nhận/công bố hợp quy** (Thông tư 11/2020) ([S11]) và có thể chạm **giấy phép thiết lập mạng viễn thông dùng riêng** ([S9]) |
| **"433 MHz nằm trong danh sách băng ISM mà Điều 6.3 TT08/2021 bắt phải chấp nhận nhiễu"** | **SAI.** Danh sách Điều 6.3 **không có** 433,05–434,79 MHz ([S1]). Chỉ dùng chú thích 5.138 của quy hoạch ([S5]) để nói về ISM |
| **"6.280 vị trí mất liên lạc"** (tiêu đề CafeF) | Chỉ dùng **6.285** theo **thân bài** [S15]; nếu trích cả hai thì phải ghi rõ "tiêu đề ghi hơn 6.280, thân bài ghi 6.285" |
| **"8 % số trạm phát sóng mất liên lạc do bão Yagi"** (VnEconomy 14-09-2024) | **Chỉ có tiêu đề** (Google News RSS), `vneconomy.vn` không đọc được ⇒ **chưa mở toàn văn** |
| **"2/3 số trạm bị ảnh hưởng đã khôi phục"** (VTV 13-09-2024); **"hơn 3000 trạm khôi phục"** (VTV 10-09-2024) | **Chỉ có tiêu đề** ⇒ chưa mở toàn văn |
| **"Khắc phục hơn 95 % trạm BTS bị ngập, phủ sóng 98 %"** (Báo Khánh Hòa 25-11-2025) | **Chỉ có tiêu đề**; `baokhanhhoa.vn` trả 404 ⇒ chưa mở |
| **"Dải đất miền Trung không còn xã trắng sóng"** (Viettel Family 03-11-2025) | **Chỉ có tiêu đề**, **và thuộc đợt lũ đầu tháng 11**, không phải đợt 19–26/11 ⇒ không gộp |
| **"108 người chết và mất tích"** (Lao Động 26-11-2025); **"50 người"** (Biên phòng 21-11-2025) | **Chỉ có tiêu đề**; nếu dùng phải ghi "theo tiêu đề, chưa mở toàn văn" |
| **"~480 người chết/mất tích cả năm 2025; thiệt hại ~105.000 tỷ đồng"** | **Chỉ có tiêu đề** (An ninh Thủ đô 01-04-2026) ⇒ chưa mở toàn văn |
| **"273 thôn + 117 điểm lõm sóng, 13 tỉnh"** | **Báo chí dẫn Cục Viễn thông**, không phải văn bản chính thức ⇒ chỉ dùng khi ghi rõ nguồn báo chí |
| **Tên đầy đủ của QCVN 73:2013/BTTTT** | **Chưa mở trang bìa QCVN**; tên suy ra từ ánh xạ dải tần trong Thông tư 11/2020 ⇒ **chỉ dùng số hiệu** |
| **Số điều/khoản Luật Viễn thông, nghị định về VSAT** liên quan Starlink | **KHÔNG TÌM THẤY NGUỒN** ⇒ không trích số điều |
| **Giá cước Starlink VN (1.131.990 / 1.711.100 / 10.848.800 đồng)**; **ngày thương mại 13-08-2026** | **Báo chí**, không phải văn bản cấp phép ⇒ không dùng như số liệu chính thức |
| **"Starlink Direct-to-Cell đã có ở Việt Nam"** | **SAI** — giấy phép VN là cố định/di động vệ tinh ([S21]) |
| **Mọi phép suy "khoảng cách LoRa"** từ mô hình không gian tự do | **Sai bản chất** cho thiết bị mặt đất (đã ghi ở tài liệu trước; giữ nguyên) |
| **Bất kỳ tầm xa LoRa đo ở nước ngoài suy ra cho Việt Nam** | Chưa có đo tại VN (§F.5–F.7) |
| **"Cục Viễn thông khuyến nghị mesh LoRa"** | **KHÔNG TÌM THẤY NGUỒN** — không có văn bản nào như vậy |

---

## H. Sổ tìm kiếm

### H.1. Công cụ & endpoint đã dùng

| Công cụ | Endpoint / cách dùng | Kết quả |
|---|---|---|
| `research_tools/congbao.py` | `POST https://api-searchcongbao.chinhphu.vn/search/van-ban` `{"filters":{},"page":1,"page_size":N,"query":"..."}` | **Tốt nhất** — trả bản ghi + PDF Công báo gốc. Lệnh: `congbao.py search "<q>" N`, `congbao.py doc "<số ký hiệu>"` |
| `research_tools/gnews.py` | `https://news.google.com/rss/search?q=<q>&hl=vi&gl=VN&ceid=VN:vi` | **Tốt để phát hiện** (tiêu đề/cơ quan/ngày). **Link bài không resolve được** |
| `research_tools/psearch.py` | Trang tìm kiếm render phía máy chủ: VietnamNet / Tuổi Trẻ / Thanh Niên / CafeF / VTV / Dân trí | **Dùng truy vấn ngắn**; đây là đường mở toàn văn |
| `pdftotext -layout` | Trích PDF Công báo | Bắt buộc để đọc điều khoản/annex |

### H.2. Truy vấn theo nhánh

**Nhánh pháp lý 433 / 920 MHz (Công báo API):**
`08/2021/TT-BTTTT`; `Thông tư 08/2021/TT-BTTTT`; `QCVN 55:2011/BTTTT`; `QCVN 73:2013/BTTTT`;
`QCVN 122:2020/BTTTT`; `38/2020/TT-BTTTT`; `hợp nhất Thông tư quy định Danh mục thiết bị vô tuyến
điện được miễn giấy phép`; `01/2025/TT-BKHCN`; `01/2013/TT-BTTTT`; `Quy chuẩn kỹ thuật quốc gia về
phổ tần và phát xạ vô tuyến điện thiết bị vô tuyến cự ly ngắn`; `Danh mục sản phẩm hàng hóa bắt buộc
chứng nhận hợp quy`; `11/2020/TT-BTTTT`; `mạng viễn thông dùng riêng`; `24/2023/QH15`;
`63/2023/NĐ-CP`; `phòng thủ dân sự`; `phòng, chống thiên tai`; `nghiệp dư`; `tần số vô tuyến điện
nghiệp dư`; `vô tuyến điện nghiệp dư`; `ứng cứu thông tin`; `bảo đảm thông tin liên lạc phòng chống
thiên tai`.

**Nhánh bão lũ (Google News RSS + trang toà soạn):**
`bão Yagi 2024 trạm BTS mất liên lạc Cục Viễn thông`; `bão Yagi 2024 thiệt hại viễn thông thuê bao
khôi phục`; `bão số 3 Yagi 2024 xã mất liên lạc`; `lũ miền Trung 2025 số người chết mất tích`;
`mất điện mất sóng lũ miền Trung 2025`; `Viettel trạm phát sóng lưu động ứng phó bão lũ`;
`VNPT VSAT tin nhắn khẩn cấp mất sóng`; `4 tại chỗ phòng chống thiên tai liên lạc thông tin`;
`radio nghiệp dư phòng chống thiên tai Việt Nam`. Trang toà soạn: `không điện không sóng`,
`mất liên lạc`, `trạm phát sóng`, `trạm BTS`, `6.280`, `viễn thông`, `gãy đổ`, `102 người chết`,
`85 người chết`, `người chết và mất tích`, `mất sóng`, `mưa lũ miền Trung`, `mưa lũ`,
`thiệt hại mưa lũ`.

**Nhánh Starlink:** kế thừa phụ lục vệ tinh ([nghien-cuu-ve-tinh-rescuemesh-ai.md](nghien-cuu-ve-tinh-rescuemesh-ai.md));
kiểm tra lại HTTP 200 cho 4 URL chính thức.

### H.3. Ghi chú chặn/giới hạn (tái lập được)

- DuckDuckGo `lite.` và `html.` → **captcha** ("Select all squares containing a duck").
- Bing HTML & RSS → kết quả **không liên quan** với truy vấn pháp lý tiếng Việt; **không** tôn trọng
  dấu ngoặc kép hay `site:`.
- `news.google.com/rss/articles/...` → **302 vòng về news.google.com**; không có redirect thật;
  `batchexecute` (`Fbv4je`/`garturlreq`) trả `null`.
- Toà soạn không đọc được: `vneconomy.vn` (trang rỗng), `laodong.vn` (177 byte),
  `vov.vn` (403), `baodautu.vn` (404), `baokhanhhoa.vn` (404), `hanoimoi.vn` (không render),
  `nhandan.vn` (không render), `dangcongsan.vn/tim-kiem` (không render), `vnexpress.net/tim-kiem` (406).
- `thuvienphapluat.vn` → 403. `mic.gov.vn` → không kết nối.
- Gemini-grounded search (`research_tools/gsearch2.py`, dùng `GEMINI_API_KEY`): **bị rate-limit** toàn
  bộ trong phiên này (3 truy vấn song song đều "rate limited after retries") ⇒ không dùng được.

---

## Nguồn (12+; ưu tiên văn bản chính thức)

**Văn bản quy phạm pháp luật — bản Công báo gốc `congbaocdn.chinhphu.vn` (ngày truy cập 2026-10-01):**

- **[S1]** Thông tư **08/2021/TT-BTTTT** ngày 14-10-2021 (Bộ trưởng Nguyễn Mạnh Hùng), Công báo số
  863+864 ngày 23-10-2021, 67 trang — *văn bản QPPL*.
  `https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2021/10/34578/37213-1-2021863-86408-2021-tt-btttt.pdf`
  (Đã đọc: Điều 4, 5, 6, 7, 8; Phụ lục 1 mục 39; Phụ lục 19; Phụ lục 2 mục 2.3.)
- **[S2]** **VBHN 01/VBHN-BKHCN** ngày 04-6-2025 — hợp nhất Thông tư 08/2021/TT-BTTTT (đã sửa bởi
  Thông tư 01/2025/TT-BKHCN), Công báo số 761+762 ngày 19-6-2025 — *văn bản hợp nhất, Văn phòng
  Chính phủ ký 20-6-2025*.
  `https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2025/6/45035/56681-1-2025761-7621-vbhn-bkhcn.pdf`
  (Đã đọc: lời nói đầu hiệu lực 28-11-2021 + sửa đổi bởi TT01/2025/TT-BKHCN hiệu lực 15-5-2025;
  Phụ lục 19 **không đổi** cho 433 và 920; Phụ lục 2 mục 2.1/2.3.)
- **[S3]** Thông tư **01/2025/TT-BKHCN** ngày 31-3-2025 (Bộ KH&CN) sửa đổi, bổ sung Phụ lục Thông tư
  08/2021/TT-BTTTT, hiệu lực 15-5-2025 — *văn bản QPPL*.
  `https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2025/3/44673/55932-1-2025633-63401-2025-tt-bkhcn.pdf`
- **[S4]** Thông tư **38/2020/TT-BTTTT** ngày 16-11-2020 ban hành **QCVN 122:2020/BTTTT**, hiệu lực
  01-7-2021, Công báo số 1115+1116 ngày 02-12-2020, 61 trang — *văn bản QPPL + quy chuẩn*.
  `https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2020/11/32513/33409-1-20201115-111638-2020-tt-btttt.pdf`
  (Đã đọc: §2.4.3.2 công suất ≤14 dBm e.r.p.; §2.4.4.1–2.4.4.3 duty cycle 10 %/1 %, Tobs = 1 h;
  §2.4.5.2 kênh hoạt động khai báo / OBW; Phụ lục D mã HS.)
- **[S5]** Quyết định **37/2025/QĐ-TTg** ngày 03-10-2025 ban hành Quy hoạch phổ tần số vô tuyến điện
  quốc gia, Công báo số 1453–1458 ngày 18-10-2025 — *văn bản QPPL*.
  `https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2025/10/46329/59226-1-20251453-145437-2025-qd-ttg.pdf`
  (+ phụ lục: `.../59229-1-20251455-145637-2025-qd-ttg.pdf`, `.../59232-1-20251457-145837-2025-qd-ttg.pdf`)
  (Đã đọc: chú thích **5.138** — 433,05–434,79 MHz ISM Khu vực 1, tần số trung tâm 433,92 MHz;
  định nghĩa Nghiệp vụ/Đài Nghiệp dư; bảng phân chia có băng NGHIỆP DƯ 47–47,2 / 76–77,5 / 77,5–78 /
  134–136 MHz.)
- **[S6]** Thông tư **14/2025/TT-BKHCN** ngày 08-8-2025 quy định việc tổ chức và đảm bảo thông tin
  liên lạc phục vụ chỉ đạo, điều hành phòng, chống thiên tai, **hiệu lực 22-9-2025** (thay thế TT
  17/2012/TT-BTTTT và TT 17/2019/TT-BTTTT), Công báo số 1249+1250 ngày 07-9-2025 — *văn bản QPPL*.
  `https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2025/8/45987/58557-1-20251249-125014-2025-tt-bkhcn.pdf`
  (Đã đọc: Điều 3, 4, 5, 6, 7, 12, 14.)
- **[S7]** Quyết định **226/QĐ-TTg** ngày 04-02-2016 phê duyệt Đề án tổ chức thông tin liên lạc khẩn
  cấp dùng chung cho các tình huống tìm kiếm, cứu nạn (số **112**), Công báo số 193+194 ngày
  19-02-2016 — *văn bản QPPL*.
  `https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2016/2/19069/13576-1-226qd-ttg13632pdf`
- **[S8]** **Luật Phòng, chống thiên tai** — bản hợp nhất **21/VBHN-VPQH** ngày 26-02-2025, Công báo
  số 537+538 ngày 18-3-2025 — *văn bản hợp nhất*.
  `https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2025/2/44459/55469-1-2025537-53821-vbhn-vpqh.pdf`
  (Đã đọc: Điều 4.3 "bốn tại chỗ"; Điều 7.2 hệ thống thông tin; Điều 26 "bảo đảm giao thông và thông
  tin liên lạc".)
- **[S9]** **Luật Viễn thông 24/2023/QH15** ngày 24-11-2023, Công báo số 29+30 ngày 05-01-2024 —
  *văn bản QPPL*.
  `https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2023/11/40834/47896-1-202429-3024-2023-qh15.pdf`
  (Đã đọc: Điều 3.16 định nghĩa mạng viễn thông dùng riêng; Điều 19.5 các trường hợp phải có giấy
  phép thiết lập mạng dùng riêng; Điều 42.4 trường hợp được miễn.)
- **[S10]** **Nghị định 63/2023/NĐ-CP** ngày 18-8-2023 quy định chi tiết Luật Tần số vô tuyến điện,
  Công báo số 963–968 — *văn bản QPPL*.
  `https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2023/8/40014/46253-1-2023963-96463-2023-nd-cp.pdf`
  (Đã đọc: Điều 3.19 khai thác viên nghiệp dư + chứng chỉ; hồ sơ cấp phép đài nghiệp dư; Điều 41
  cho thuê/cho mượn đài nghiệp dư.)
- **[S11]** Thông tư **11/2020/TT-BTTTT** ngày 14-5-2020 quy định Danh mục sản phẩm, hàng hoá nhóm 2
  thuộc trách nhiệm Bộ TT&TT, Công báo số 599+600 ngày 28-5-2020 — *văn bản QPPL*.
  `https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2020/5/31389/31279-1-2020599-60011-2020-tt-btttt.pdf`
  (Đã đọc: Điều 1 phạm vi; Danh mục mục 2 và mục 3.1 ánh xạ 25 MHz–1 GHz → **QCVN 73:2013/BTTTT**,
  9 kHz–25 MHz → QCVN 55:2011/BTTTT.)
- **[S12]** **Luật Phòng thủ dân sự 18/2023/QH15** ngày 20-6-2023 và **Nghị định 200/2025/NĐ-CP** ngày
  09-7-2025 — *văn bản QPPL* (xác minh sự tồn tại/ngày qua API Công báo; **chưa đọc toàn văn**
  điều khoản liên lạc).

**Cơ quan quản lý (trang của Bộ TT&TT — `cspl.mic.gov.vn`, Vụ Pháp chế):**

- **[S13]** "Ban hành Thông tư quy định danh mục thiết bị vô tuyến điện được miễn giấy phép sử dụng
  tần số…", 19-10-2021 — *báo cáo/giới thiệu của cơ quan quản lý*. Ghi rõ: TT08/2021 bổ sung **04
  chủng loại thiết bị mới**, trong đó có "thiết bị mạng diện rộng công suất thấp LPWAN (sử dụng
  **băng tần 433,05–434,79 MHz và 920–923 MHz**)", thay thế TT 46/2016 và TT 18/2018, **hiệu lực
  28/11/2021**.
  `https://cspl.mic.gov.vn/Pages/TinTuc/138298/x.html`
- **[S14]** "Thông tư số 38/2020/TT-BTTTT ban hành QCVN… LPWAN băng tần 920 MHz đến 923 MHz",
  17-11-2020 — *báo cáo/giới thiệu của cơ quan quản lý*. Nêu phạm vi QCVN 920–923, phổ tần dùng chung,
  hiệu lực 01-7-2021, và các tài liệu tham chiếu (ITU-R SM.2423-0, SM.329-12, ETSI EN 300 220-1/-2,
  tiêu chuẩn Indonesia/Malaysia/Singapore).
  `https://cspl.mic.gov.vn/Pages/TinTuc/138249/x.html`

**Báo chí chính thống / báo cáo (đã mở toàn văn):**

- **[S15]** CafeF, "Ảnh hưởng bão Yagi: Hiện có 27 cột viễn thông bị gãy đổ, hơn 6.280 vị trí mất
  liên lạc di động do mất điện", **09-09-2024 09:47**, tác giả Nguyệt Lượng, nguồn markettimes.vn,
  số liệu từ Bộ TT&TT — *báo chí chính thống*.
  `https://cafef.vn/anh-huong-bao-yagi-hien-co-27-cot-vien-thong-bi-gay-do-hon-6280-vi-tri-mat-lien-lac-di-dong-do-mat-dien-188240909090326452.chn`
- **[S16]** VietnamNet, "Người dân vùng lũ 'không điện, không sóng', nhà mạng xuyên đêm khắc phục sự
  cố", **20-11-2025 20:34**, tác giả Thái Khang — *báo chí chính thống*.
  `https://vietnamnet.vn/nguoi-dan-vung-lu-khong-dien-khong-song-nha-mang-xuyen-dem-khac-phuc-su-co-2464896.html`
- **[S17]** Tuổi Trẻ, "Cập nhật ngày 24-11: Mưa lũ miền Trung làm 102 người chết và mất tích, thiệt
  hại hơn 13.000 tỉ đồng", **24-11-2025 09:24** — dẫn báo cáo nhanh 6h ngày 24-11 của **Cục Quản lý
  đê điều và Phòng, chống thiên tai** — *báo chí chính thống dẫn báo cáo cơ quan*.
  `https://tuoitre.vn/cap-nhat-ngay-24-11-mua-lu-mien-trung-lam-102-nguoi-chet-va-mat-tich-thiet-hai-hon-13-000-ti-dong-20251124073115437.htm`
- **[S18]** Thanh Niên, "Cập nhật mưa lũ ở miền Trung: 85 người chết và mất tích", **22-11-2025
  19:08** — dẫn Cục Quản lý đê điều và Phòng, chống thiên tai — *báo chí chính thống*.
  `https://thanhnien.vn/cap-nhat-mua-lu-o-mien-trung-85-nguoi-chet-va-mat-tich-185251122175052491.htm`

**Starlink — nguồn chính thức / báo Đảng (kiểm tra lại HTTP 200 ngày 2026-10-01):**

- **[S19]** Báo Điện tử Chính phủ, "Starlink được cấp phép cung cấp dịch vụ tại Việt Nam" (Quyết định
  659/QĐ-TTg ngày 26-3-2025; thời hạn kết thúc trước 01-01-2031) — *báo Đảng/báo Chính phủ*.
  `https://baochinhphu.vn/starlink-duoc-cap-phep-cung-cap-dich-vu-tai-viet-nam-102260214200759337.htm`
- **[S20]** Bộ KH&CN, "Starlink được cấp phép triển khai dịch vụ internet vệ tinh tại Việt Nam"
  (Cục Tần số vô tuyến điện cấp giấy phép tần số 13-02-2026; 4 gateway; trần 600.000 thiết bị) —
  *nguồn chính thức của bộ quản lý*.
  `https://mst.gov.vn/starlink-duoc-cap-phep-trien-khai-dich-vu-internet-ve-tinh-tai-viet-nam-19726021500204438.htm`
- **[S21]** Báo Điện tử Chính phủ, "Bộ KH&CN trao giấy phép cung cấp dịch vụ viễn thông vệ tinh cho
  Starlink" (02 giấy phép: cố định vệ tinh + di động vệ tinh; trao tối 18-02-2026 tại Washington D.C.)
  — *báo Chính phủ*.
  `https://baochinhphu.vn/bo-khcn-trao-giay-phep-cung-cap-dich-vu-vien-thong-ve-tinh-cho-starlink-102260219204340964.htm`
- **[S22]** Báo Đảng Cộng sản Việt Nam, "Thanh Hóa lắp đặt thiết bị Starlink tại các vùng lõm sóng
  viễn thông" (lắp 9 bộ Standard 4X ngày 28–29/09/2026; khẳng định Starlink là **giải pháp kết nối
  tạm thời**, sẽ **điều chuyển thiết bị**) — *báo Đảng*.
  `https://dangcongsan.vn/bokhoahoccongnghe/tin-tuc-hoat-dong/thanh-hoa-lap-dat-thiet-bi-starlink-tai-cac-vung-lom-song-vien-thong.html`

**Nguồn phát hiện (chỉ tiêu đề — dùng để dẫn hướng, KHÔNG trích số liệu):**

- **[S23]** Google News RSS (`news.google.com/rss/search?hl=vi&gl=VN&ceid=VN:vi`), truy vấn ngày
  2026-10-01 — *nguồn phát hiện*. Các mục chưa mở toàn văn: VnEconomy 14-09-2024 ("Cục Viễn thông:
  còn khoảng 8 % số trạm phát sóng bị mất liên lạc vì bão"); VTV 10-09-2024 ("Đã khôi phục hơn 3000
  trạm phát sóng di động sau bão Yagi"); VTV 13-09-2024 ("2/3 số trạm thu phát sóng bị ảnh hưởng bởi
  bão số 3 đã được khôi phục"); Lao Động 10-09-2024 ("48 giờ cứu hộ viễn thông sau bão Yagi");
  Báo Biên phòng 21-11-2025 (50 người); Dân trí 23-11-2025 (102 người, 9.035 tỷ); Lao Động
  26-11-2025 (108 người); Báo Khánh Hòa 25-11-2025 (95 % trạm BTS, 98 % phủ sóng); Viettel Family
  03-11-2025 ("không còn xã trắng sóng" — đợt đầu tháng 11); An ninh Thủ đô 01-04-2026 (~480 người,
  ~105.000 tỷ cho cả năm 2025).
- **[S24]** LuatVietnam, "Bộ trưởng Bộ KH&CN được thu hồi chứng chỉ vô tuyến điện viên nghiệp dư",
  08-09-2026 — *báo chí pháp lý*, **chỉ tiêu đề** (chưa mở); xác nhận tồn tại cơ chế chứng chỉ
  nghiệp dư đang được sửa đổi.

**Ghi chú phủ định có kiểm chứng:** các tài liệu sau **không tìm thấy** và được ghi là
**KHÔNG TÌM THẤY NGUỒN**: tên đầy đủ QCVN 73:2013/BTTTT; hướng dẫn chính thức về mạng mesh cộng
đồng; vai trò PCTT của radio nghiệp dư; đo tầm xa LoRa tại Việt Nam; so sánh 433 vs 920 tại Việt Nam;
mật độ phổ tần thực đo ở 433,05–434,79 MHz; thời lượng mất liên lạc (giờ) của một xã cụ thể; số xã
mất liên lạc hoàn toàn trong Yagi 2024; dung lượng an toàn Starlink trong thảm họa; đo rain fade
tại Việt Nam.
