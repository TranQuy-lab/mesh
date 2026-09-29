# Xác minh nguồn và tài liệu tham khảo — RescueMesh-AI

**Tài liệu liên quan:** [Kế hoạch nghiên cứu](ke-hoach-nghien-cuu-rescuemesh-ai.md) · [Cấu trúc đề tài](cau-truc-de-tai-rescuemesh-ai.md)
**Ngày xác minh:** 2026-09-28 · **Trạng thái:** đang hoàn thiện (mục §2.2 và §4 chờ kết quả tìm kiếm)

Tài liệu này tồn tại vì một lý do cụ thể: đoạn hội thoại đầu vào có dấu hiệu do AI tổng hợp, và trong dự án này **không được trích một nguồn nào chưa mở**. Mỗi dòng dưới đây ghi rõ đã kiểm bằng cách nào.

---

## 1. Phương pháp xác minh

| Bước | Cách làm |
|---|---|
| 1 | Mở URL gốc, không dựa vào mô tả trong đoạn hội thoại |
| 2 | Với kho GitHub: truy vấn GitHub API (`/repos/{owner}/{repo}`) để lấy chủ sở hữu thật, ngôn ngữ, giấy phép, số sao, ngày tạo, cờ `fork`, và theo dõi chuyển hướng |
| 3 | Phân biệt "có trong README" với "có trong mã": chỉ coi là đã triển khai khi thấy mã/kiểm thử, không tính mô tả quảng cáo |
| 4 | Ghi ngày truy cập; số liệu sao/ngày sẽ trôi theo thời gian nên phải ghi kèm ngày |
| 5 | Mục không xác minh được thì ghi "chưa xác minh", **không** suy diễn |

**Giới hạn của việc xác minh này:** đã kiểm *sự tồn tại và thuộc tính* của nguồn, chưa đánh giá chất lượng khoa học của từng công trình. Đánh giá chất lượng là bước riêng, ghi ở cột "chất lượng".

---

## 2. Xác minh các mục trong đoạn hội thoại

**Kết quả tổng hợp:** 5/6 mục tồn tại thật nhưng **mô tả trong đoạn hội thoại sai ở 4/6 mục**, và 1 mục là công trình không đáng trích nhưng lại chứa **trích dẫn bịa**. Báo cáo xác minh đầy đủ (kèm lệnh truy vấn) ở [verify/rescuemesh-source-verification.md](verify/rescuemesh-source-verification.md).

### 2.1 Bảng phán quyết

| # | Nguồn theo đoạn hội thoại | Phán quyết | Sai lệch so với mô tả |
|---|---|---|---|
| 1 | `AleksPlekhov/ai-mesh-emergency-communication-platform` ("ResQMesh AI Platform") | **Có thật, phần lớn đã triển khai** — Kotlin, GPL-3.0, 90★/32 fork, tạo 2026-03-03, đẩy cuối 2026-09-14, 469 commit, 3 bản alpha | **Là fork** của `permissionlesstech/bitchat-android` (7.661★, GPL-3.0). Phần thêm thật: module `:resqmesh-ai` với 2 mô hình TFLite (1,16 MB text / 2,68 MB vision), `TFLiteMessageClassifier.kt`, `VoskManager.kt` (STT offline), `ICS213ReportGenerator.kt` (báo cáo kiểu FEMA ICS-213), 31 KB test. **Nhưng "priority routing" bị nói quá**: `services/MessageRouter.kt` không có logic ưu tiên; phân loại chỉ đổi giao diện và có một benchmark hàng đợi. **Các chỉ số trong README (F1 0,92; macro-F1 0,98; "+16–57% khả năng sống sót") chưa được kiểm toán → không được trích** |
| 2 | `njhyousha/ResqLink-…` (BLE mesh + Gemini triage) | **Có thật nhưng gán sai chủ sở hữu** — URL 301 sang `ShadowVoid-T-T/…`; `/users/njhyousha` → **404, chủ gốc đã biến mất**. TypeScript, **không giấy phép**, 37★, tạo và đẩy cuối cùng cùng ngày 2026-07-30, **2 commit** | `meshEngine.ts` tự ghi là *"Mesh Networking Simulator"*, `simulateEncrypt`, không có plugin BLE → **mesh chỉ là mô phỏng trong trình duyệt**. **"Gemini on-device" là SAI**: `aiEngine.ts` = chấm điểm bằng `includes()` từ khóa + proxy Gemini phía máy chủ cần `GEMINI_API_KEY`. → Chỉ được gọi là "nguyên mẫu hackathon", **không** phải bằng chứng cho BLE mesh hay AI trên thiết bị |
| 3 | "MeshGemma" (giải lớn, Kaggle, iOS, đọc ảnh chấn thương) | **Có thật** — app `JasperG134/MeshGemma` (Expo/RN iOS, tạo 2026-05-17, **1 commit**, 4★, CC BY 4.0). **Gemma 4 là thật** (model card chính thức: E2B/E4B/12B/26B-A4B/31B). **Hội thi có thật**: "The Gemma 4 Good Hackathon" trên Kaggle trả HTTP 200 | **"Đạt giải thưởng lớn" chưa xác minh** (bảng xếp hạng render bằng JS). Suy luận trên thiết bị **là thật** (Gemma 4 E2B GGUF 2,29 GB + mmproj qua llama.rn/Metal, phân tích ảnh offline). **Nhưng chính README ghi "The BLE transport is presence-only"** — dữ liệu đi qua TCP/mDNS, phần phát radio là hoạt ảnh mô phỏng → **không được** dùng làm bằng chứng cho mesh BLE |
| 4 | `raviprasad794063/disaster_mesh` (Bluetooth + Wi-Fi Direct) | **Có thật, mã thật, độ chín thấp** — Kotlin, **MIT**, **2★**, tạo 2025-10-02, đẩy cuối 2026-02-05, **10 commit, 0 release**, ~90 tệp | Cả hai radio **được code thật**: `WiFiDirectManager.kt` (13,9 KB, `WifiP2pManager`, `ServerSocket:8888`), `BluetoothLeManager.kt`, `MeshService.kt` (20,7 KB). Nhưng không CI, không thư mục test, không tag → chỉ dùng làm ví dụ "có tiền lệ kỹ thuật", không phải đối chứng chất lượng |
| 5 | "Crisis Mesh Messenger" | **Có thật** — `FundacjaHospicjum/crisis-mesh-messenger`, Dart/Flutter, MIT, 197★/22 fork, tạo 2025-10-12, **cả 6 commit trong cùng một ngày**, không cập nhật sau đó | `mesh_network_service.dart` có `// TODO: Implement platform-specific discovery` và `_simulatePeerDiscovery()` → **mesh là khung rỗng**; chỉ màn hình SOS/UI là code thật. → Không được trích như một hệ mesh hoạt động |
| 6 | ResearchGate `publication/398912234` "Disaster-Resilient Mesh Network with AI Load Balancing" (Decision Tree/RF/XGBoost) | **Có thật nhưng không đáng trích** — bản ghi chuẩn: **DOI 10.17148/ijarcce.2025.141297**, IJARCCE 14(12), 12/2025, Tejass Publishers, ISSN 2278-1021. Crossref: **0 tài liệu tham chiếu, 0 trích dẫn** | Tạp chí thu tiền để đăng, tự công bố "Impact Factor 8.471" → coi là **predatory/không bình duyệt**. Nội dung: **"Decision Tree" xuất hiện 0 lần** (mô tả trong hội thoại sai); từ khóa ghi "Reinforcement Learning" nhưng không có RL; **không có dữ liệu, không đánh giá, không kết quả**. **Tài liệu tham chiếu [2] bị bịa**: bài viết dẫn "BLUEMERGENCY… arXiv:1905.02465", nhưng arXiv:1905.02465 là bài *"Photometry… of comet C/2014 A4 (SONEAR)"*. → **Loại hoàn toàn khỏi bài** |
| 7 | BitChat + "courier card rotation" | **Có thật** — `permissionlesstech/bitchat` (Swift, **Unlicense**, 36.288★, BLE mesh, tối đa 7 chặng, mã hóa Noise) và `permissionlesstech/bitchat-android` (Kotlin, GPL-3.0, 7.661★) | **"Courier card rotation" không phải thuật ngữ chính thức ở đâu cả.** Cơ chế thật là **§6.2 "Couriers" trong WHITEPAPER.md**: phong bì courier niêm phong với **thẻ người nhận 16 byte xoay vòng = HMAC(khóa tĩnh, ngày UTC)**, tối đa 3 courier, ngân sách spray-and-wait 4→8. Lưu ý: chính README nói mesh BLE dùng **ID thiết bị cố định** — ngược với xoay vòng. → Phải trích whitepaper và gọi đúng tên cơ chế |
| 8 | SisFall / MobiFall / UP-Fall; Trickle; RPL | **Có thật** — SisFall: Sensors 2017, DOI 10.3390/s17010198; MobiFall: IEEE BIBE 2013, DOI 10.1109/bibe.2013.6701629; UP-Fall: Sensors 2019, DOI 10.3390/s19091988; Trickle: RFC 6206 (2011); RPL: RFC 6550 (2012) | Phải trích **bản gốc**, không trích qua đoạn hội thoại. Số liệu chi tiết của từng kho dữ liệu nằm ở §4.2 |

### 2.2 Các dự án so sánh được mà đoạn hội thoại bỏ sót

Danh sách này quan trọng hơn bảng trên, vì nó là cơ sở để định vị đóng góp:

| Dự án | Giấy phép | BLE | Lưu-và-chuyển tiếp | SOS tự động do cảm biến | Mức trưởng thành |
|---|---|---|---|---|---|
| bitchat / bitchat-android | Unlicense / GPL-3.0 | Có | Có (courier) | **Không** | 36k★ / 7,7k★ |
| Meshtastic firmware | GPL-3.0 | Chỉ làm link | Có (flood) | **Không** | 8,3k★, 2020– |
| MeshCore | MIT | Không (LoRa) | Có (hybrid) | **Không** | 3,7k★, 2025– |
| Briar | GPL-3.0 | Có | Có (Tor) | **Không** | cao, có bình duyệt |
| Serval batphone | GPL-3.0 | Có | Có | **Không** | **ngừng 2018** |
| qaul.net | AGPL-3.0 | Có | Có | **Không** | 727★, 2014– |
| Sideband/Reticulum | Reticulum | Có | Có | **Không** | 1,8k★, đang hoạt động |
| Bridgefy SDK | độc quyền | Có | Một phần | **Không** | thương mại |
| disaster.radio | không có | Không (LoRa) | Có | **Không** | tạm dừng |
| ATAK-CIV | — | qua plugin | qua plugin | **Không** | 494★, dừng 2024 |

**Khoảng trống cốt lõi (dùng được để định vị):** trong 11 dự án so sánh được, **không dự án nào phát SOS tự động do cảm biến kích hoạt**. Đây là chỗ đóng góp C1 + C2 của RescueMesh-AI đứng vững — với điều kiện phải kèm bộ phân loại được đánh giá theo chuẩn (LOSO, ngân sách FAR), chứ không chỉ là ngưỡng gia tốc.

### 2.3 Giới hạn của lần xác minh này

- `web_search` **hỏng trong phiên này (HTTP 401)**; phải thay bằng GitHub Search API, Crossref/OpenAlex/arXiv, RFC Editor và HTML của DuckDuckGo/Bing. Vì vậy kết quả tìm kiếm web tổng quát **chưa đầy đủ** và phải chạy lại khi công cụ hoạt động.
- ResearchGate trả 403, Semantic Scholar trả 429 → không đọc được trực tiếp; kết luận về mục #6 dựa trên bản ghi Crossref và PDF của nhà xuất bản.
- Bảng xếp hạng Kaggle render bằng JS → **không** xác minh được giải thưởng.
- Đã xác minh *sự tồn tại và thuộc tính* của nguồn, **chưa** đánh giá chất lượng khoa học từng công trình.

### 2.4 Quy tắc rút ra

1. **Loại mục #6 khỏi mọi bản viết.** Ngoài việc không đáng trích, nó còn chứa trích dẫn bịa — trích lại là lan truyền lỗi.
2. **Hạ mục #2 và #5 xuống "nguyên mẫu hackathon",** không dùng làm bằng chứng.
3. **Mục #1 là đối chứng chính, nhưng chỉ dùng định tính**: nêu bản chất fork, module AI trên thiết bị, và **không** trích bất kỳ chỉ số nào từ README.
4. **Mục #7 phải gọi đúng tên**: cơ chế "Couriers" trong whitepaper, không dùng cụm "courier card rotation".
5. **Nêu khoảng trống đúng mức:** "trong phạm vi 11 dự án đã kiểm, không dự án nào có SOS tự động do cảm biến" — không nói "chưa từng có ai làm".

## 3. Bằng chứng do dự án tự tạo (không phải trích dẫn)

> **Lịch sử thiết kế:** bảng cũ 20/21 byte dựa trên ATT MTU đã bị thay thế khi
> rà soát lại lớp liên kết. Đường SOS v1 dùng legacy advertising, không dùng GATT.

Các con số sau do chính dự án tính và **kiểm chứng bằng code** (`rescuemesh/packets.py`, 21 test qua). Chúng là bằng chứng cho C4/H4, không phải trích từ tài liệu:

| Phát hiện | Số | Cách kiểm |
|---|---|---|
| SOS v1 vừa ngân sách ứng dụng advertising | 24 byte | `test_sos_is_24_bytes_and_verifies` |
| HMAC SOS phát hiện sửa body; cho phép relay sửa route byte đã khai báo | 64 bit tag | `test_sos_tamper_is_detected_except_documented_route_byte` |
| Đụng độ `srcID` 32 bit ở 10.000 nút | 1,16 % | Nghịch lý ngày sinh; dedup v1 dùng thêm tag 64 bit |
| ACK token | 32 bit đầu của tag SOS | `test_ack_token_comes_from_sos_tag`; collision tính theo SOS đồng thời |
| Độ phân giải toạ độ 24 bit | vĩ độ 1,19 m; kinh độ 2,39 m | `test_latlon_resolution_is_metre_scale` |
| Kích thước gói v1 | SOS 24 B; HEARTBEAT 18/23 B; BEACON 16/20/24 B | 14/14 test codec |

**Cách ghi trong bài:** đây là kết quả phân tích thiết kế của nhóm, nhãn `SUY` (suy ra từ spec + phân tích) — không được trình bày như phát hiện đo được.

---

## 4. Thư mục tài liệu tham khảo

Mỗi mục dưới đây đã được **mở và đối chiếu định danh** (DOI hoặc số RFC) trong lần xác minh 2026-09-28, qua Europe PMC REST, Crossref REST, OpenAlex, trang tìm kiếm arXiv, rfc-editor.org và GitHub API. Khi viết bài, **sao chép danh sách tác giả từ bản ghi chuẩn** — bảng này cố ý chỉ ghi định danh đã kiểm, không chép tác giả từ trí nhớ. Mục nào ghi **"chưa xác minh"** thì không được dùng làm chỗ dựa cho khẳng định.

### 4.1 Phát hiện ngã từ IMU — nền bằng chứng mạnh nhất của đề tài

| Nguồn (định danh đã kiểm) | Con số dùng được |
|---|---|
| Bagalà et al. 2012, *PLoS ONE* 7(5):e37062, `10.1371/journal.pone.0037062` | 13 thuật toán trên **29 ca ngã thực**: sensitivity trung bình **57,0 % ± 27,3 %** (cao nhất 82,8 %), specificity 83,0 %; **3–85 báo động giả/ngày** → kết quả trên ngã staged cao hơn hẳn ngã thực |
| Kangas et al. 2015, *Gerontology*, `10.1159/000362720` | 15.500 giờ, 16 người cao tuổi: **SE 80,0 %**, 0,049 báo động/giờ; tinh chỉnh còn 0,025/giờ ≈ **1 báo động giả/40 giờ** |
| Harari et al. 2021, *J NeuroEng Rehabil*, `10.1186/s12984-021-00918-z` | 23 người, 2.070 ngày, 14,9 triệu sự kiện: **SE 73,0 %**, **1 báo động giả/46 ngày**, SP > 99,9 %, precision 37,5 % |
| Palmerini et al. 2020, *Sensors* 20(22):6479, `10.3390/s20226479` | 143 ca ngã **thực** (FARSEEING), SVM + nhiều pha: **SE > 80 %, 0,56 báo động giả/giờ**, F-measure 64,6 % |
| Alizadeh et al. 2021, *Sensors* 21(21):7166, `10.3390/s21217166` | Huấn luyện SisFall (staged) → kiểm tra FARSEEING (thực): SVM tuyến tính **93 % accuracy** → tiền lệ cho kiểm tra chuyển miền |
| **Villa & Casilari 2025, *Sensors* 26(1):162, `10.3390/s26010162`** | **Bài so sánh cổ điển vs sâu trên cùng dữ liệu:** SisFall ở 10/20/50/100 Hz; **CNN-LSTM @20 Hz = 98,9 % acc, 96,7 % SE, 99,6 % SP**, và **mô hình sâu luôn hơn mô hình cổ điển**; cửa sổ 4 giây đặt giữa đỉnh va đập. Trên **ngã thực FARSEEING: SE 81,8 % (18/22)**; trên 7 ngày thực địa: **~8 báo động giả/ngày, SP ~95 %** |
| Guo & Nakayama 2025, *Sensors* 25(20):6500, `10.3390/s25206500` | KNN/SVM: LOSO trên UniMiB **98,45 %**, MobiAct 99,89 %; FARSEEING SE 95,35 %/SP 98,12 % |
| Casilari et al. 2017, *Sensors* 17(7):1513, `10.3390/s17071513` | Chuẩn tham số: các kho dữ liệu trải **5–256 Hz**, **50 Hz là đủ**; bốn mức lấy mẫu của Android thực tế cho **7–200 Hz**; cửa sổ từ 1 giây trượt (đặc trưng ngưỡng) tới **4 giây đặt giữa đỉnh va đập 2 g** |

**Cảnh báo quan trọng:** **không tồn tại meta-analysis gộp thật cho phát hiện ngã bằng IMU** (Europe PMC chỉ trả về một meta-analysis về vòng đeo theo dõi sức khỏe, `10.2196/56972`). Mọi câu kiểu "sensitivity gộp là X %" là **chưa xác minh** và không được viết.

### 4.2 Kho dữ liệu công khai

Tất cả đều là **ngã staged** trừ khi ghi rõ (Casilari 2017: "in most cases, both falls and ADLs were simulated and scheduled according to predefined types").

| Kho | Quy mô | Cảm biến / tần số | Ghi chú |
|---|---|---|---|
| **SisFall** — `10.3390/s17010198` | 38 người (23 trẻ 19–30, 15 cao tuổi 60–75; 19 nữ/19 nam); 15 kiểu ngã / 19 ADL; 4.510 thử nghiệm | Thắt lưng; **200 Hz** | Nguồn mở `sistemic.udea.edu.co`. Baseline tốt nhất đã kiểm: 98,9 % (Villa 2025) |
| **MobiFall / MobiAct** | 24 người (17 nam/7 nữ); 4 kiểu ngã / 9 ADL; 630 mẫu | Túi quần; **tần số chưa xác minh** | `bmi.teicrete.gr` |
| **UP-Fall** — `10.3390/s19091988` | 17 người trẻ; 6 ADL + 5 kiểu ngã × 3 | Thắt lưng/cổ tay/cổ/chân/túi + cảm biến môi trường + camera; **18 Hz** | 850+ GB |
| **UniMiB SHAR** — `10.3390/app7101101` | 30 người (24 nữ/6 nam); 8 kiểu ngã / 9 ADL | Túi quần; tần số chưa xác minh | Baseline LOSO 98,45 % |
| **KFall** — `10.3389/fnagi.2021.692865` | 32 người; **21 ADL + 15 kiểu ngã mô phỏng** | IMU lưng dưới; **100 Hz** | Baseline của tác giả 99,32 % acc / 99,01 % SE |
| **UMAFall** — `10.1016/j.procs.2017.06.110` | 17 người (10 nam/7 nữ); 3 kiểu ngã / 8 ADL; 531 mẫu | 5 cảm biến trên người + điện thoại | figshare 4214283 |
| **tFall** | 10 người (7 nam/3 nữ); số mẫu chưa xác minh | — | `eduqtech.unizar.es` |
| **FallAllD** — `10.1109/JSEN.2020.3018335` | **Số người/số lớp và giấy phép chưa xác minh** | Điện thoại + đồng hồ | Chỉ xác minh được trích dẫn |
| **Ngã THỰC** | FARSEEING (`farseeingresearch.eu`): **143 ca ngã thực** (Palmerini 2020); "Free From Falls": 49 chuỗi / 690 cửa sổ 4 giây | — | Đây là hai nguồn **bắt buộc** để kiểm tra độ bền ngoài phòng thí nghiệm |

**Giấy phép:** chưa xác minh từng kho; bài dữ liệu của MDPI thường là CC-BY, nhưng **phải kiểm trước khi phát hành lại dữ liệu**.

### 4.3 Triển khai trên thiết bị / TinyML

| Nguồn | Con số |
|---|---|
| TinyFallNet — `10.3390/s23208459` | **0,70 MB, 98,00 % acc** (so với ConvLSTM 1,58 MB / 97,37 %) |
| Độ trễ int8-TFLite, mJ mỗi lần suy luận, dòng tiêu thụ accelerometer luôn bật, quy định chạy nền của Android/iOS | **Chưa xác minh** — `developer.android.com` render bằng JS, không lấy được văn bản. Đây là lỗ hổng phải tự đo ở WP4, không được suy đoán |

### 4.4 BLE mesh / DTN cho thảm họa

Đợt quét thứ hai lấy được các nguồn nền tảng sau (định danh từ Crossref/OpenAlex):

| Nguồn | Dùng cho |
|---|---|
| "Bluetooth Low Energy Mesh: Applications, Considerations and Current State-of-the-Art", *Sensors* 2023, `10.3390/s23041826` (Natgunanathan, Fernando, Loke, Weerasuriya — tác giả lấy từ Crossref) | Khảo sát chính cho Ch. 2.1; đối chiếu Bluetooth Mesh chuẩn (relay/proxy) với mesh điện thoại tự chế |
| "A Survey on Multihop Ad Hoc Networks for Disaster Response Scenarios", 2015, `10.1155/2015/647037` | **Thay thế khảo sát AI tổng hợp** về mạng nhiều chặng cho cứu hộ |
| "Analysis of Latency Performance of Bluetooth Low Energy (BLE) Networks", *Sensors* 2015, `10.3390/s150100059` | Mốc độ trễ BLE để kiểm tra ngân sách độ trễ |
| "Data Transmission Efficiency in Bluetooth Low Energy Versions", *Sensors* 2019, `10.3390/s19173746` | Hiệu suất truyền theo phiên bản BLE |
| "Security and Privacy Threats for BLE in IoT and Wearable Devices", *IEEE OJ-COMS* 2022, `10.1109/ojcoms.2022.3149732` | Mô hình mối đe dọa cho §8.6 |
| "From Sensors to Safety: IoES for Emergency Response and Disaster", *JSAN* 2023, `10.3390/jsan12030041` | Bối cảnh Ch. 1.1 |
| "CodeBlue: An Ad Hoc Sensor Network Infrastructure for Emergency Medical Care", 2004 (không DOI) | **Chưa xác minh** — chỉ trích nếu mở được toàn văn |

**Vẫn còn khoảng trống:** chưa có **số PDR/độ trễ/năng lượng đo trên điện thoại thật** cho BLE mesh, và chưa có số về BLE 5 coded PHY / extended advertising. **Không được trích số ở phần này** — phải tự đo ở WP4.

### 4.5 Định tuyến

| Nguồn | Nội dung dùng được |
|---|---|
| **RFC 6206 — Trickle** (2011), https://www.rfc-editor.org/rfc/rfc6206 | Cơ chế triệt tiêu gói dư thừa; tốc độ truyền **co giãn theo logarit**; thiết kế cho tiết kiệm năng lượng |
| **RFC 6550 — RPL** (2012), `10.17487/rfc6550` | Định tuyến distance-vector IPv6 cho LLN qua DODAG; Objective Function quyết định DAG |
| **RFC 6687** — đánh giá hiệu năng RPL, `10.17487/rfc6687` | Tiêu chí đo cho RPL |
| **RFC 6693 — PRoPHET**, `10.17487/rfc6693` | Đặc tả chuẩn cho định tuyến DTN xác suất |
| Spray-and-Wait — Spyropoulos, Psounis, Raghavendra 2005, WDTN'05, `10.1145/1080139.1080143` | Cơ chế giới hạn bản sao |
| PROPHET — Lindgren, Doria, Schelén 2003, *ACM SIGMOBILE CCR*, `10.1145/961268.961272` | Bài gốc định tuyến xác suất |
| **The ONE simulator** — "The ONE simulator for DTN protocol evaluation", SIMUTools 2009, `10.4108/icst.simutools2009.5674` (1.741 trích dẫn) + "Simulating Mobility and DTNs with the ONE", *JCM* 2010, `10.4304/jcm.5.2.92-105` | **Công cụ đối chứng chéo cho WP3** — có sẵn epidemic / Spray-and-Wait / PROPHET. Xem [Nguồn học tập](nguon-hoc-tap-va-tai-su-dung.md) §3 về giấy phép GPL-3.0 |
| "Optimizing the Trickle Algorithm", *IEEE Comm. Letters* 2015, `10.1109/lcomm.2015.2408339` | Cách chỉnh tham số Trickle — cơ sở cho "flooding có kiểm soát" |
| "A Novel Adaptive and Efficient Routing Update Scheme for Low-Power Lossy Networks in IoT", *IEEE IoT-J* 2018, `10.1109/jiot.2018.2862364` | Ví dụ cải tiến Trickle/RPL — dùng để đặt ngưỡng kỳ vọng thực tế cho gradient |
| Epidemic routing — Vahdat & Becker 2000, Duke CS-2000-06 | **Chưa xác minh** (không DOI, chưa mở) |
| So sánh **flooding vs gradient/tree** trong mạng công suất thấp, có số PDR **và** năng lượng | **Không tìm thấy nguồn nào đã xác minh** — đây là *khoảng trống thật*, không phải kết quả phủ định. Tăng giá trị cho H2/C3 |
| Lợi ích của định tuyến bằng ML | **Chưa đánh giá trong phiên này** |

### 4.6 Gói tin và an ninh

**Sửa phân lớp quan trọng:** ATT MTU 23/517 dưới đây chỉ áp dụng khi dùng GATT.
Nó không phải giới hạn cho đường quảng bá SOS v1. Android `BluetoothLeAdvertiser`
ghi rõ legacy advertiser phát tối đa 31 byte advertising data; Bluetooth LE Primer
cũng xác nhận payload legacy tối đa 31 octet và advertising không có ACK. Với
manufacturer-specific AD structure, thiết kế dành ngân sách bảo thủ 24 byte dữ liệu
giao thức và bắt buộc kiểm trên máy thật. Nguồn chính thức:
https://developer.android.com/reference/android/bluetooth/le/BluetoothLeAdvertiser
và https://www.bluetooth.com/bluetooth-le-primer/.

Android sensor batching chỉ tiết kiệm pin khi thiết bị có FIFO/sensor hub phù hợp;
không có API công khai phổ quát để nạp luật free-fall→impact vào hub. Vì vậy T1 v1
được coi là xử lý ứng dụng trên stream accelerometer và phải đo pin. Nguồn:
https://source.android.com/docs/core/interaction/sensors/batching.

| Nguồn | Con số dùng được |
|---|---|
| **RFC 8032 — EdDSA/Ed25519** | Chữ ký = R (32 octet) + S (32 octet) = **64 octet**; khóa riêng 32 octet → xác nhận con số 64 byte đã dùng trong phân tích §8 |
| **RFC 2104 §5 — HMAC** | Cho phép **cắt ngắn đầu ra HMAC** và bàn về đánh đổi; **con số "tối thiểu 80 bit" chưa xác minh** (bản fetch bị cắt) → không trích con số đó |
| **ATT MTU mặc định = 23** — BlueZ (ngăn xếp Bluetooth tham chiếu của Linux), `src/shared/att-types.h:28`: `#define BT_ATT_DEFAULT_LE_MTU 23`; hằng số này là **sàn** khi thương lượng MTU (`src/shared/gatt-server.c:1540`, `att.c:1263`) | **ĐÃ CÓ NGUỒN SƠ CẤP** cho con số 23. Cộng 3 byte header ATT → payload 20 byte, đúng bằng ràng buộc dùng trong codec và §8. Nguồn: https://raw.githubusercontent.com/bluez/bluez/master/src/shared/att-types.h |
| **MTU tối đa = 517 trên Android** — AOSP (ngăn xếp Bluetooth), `android/app/src/com/android/bluetooth/gatt/GattService.java:145`: `private static final Integer GATT_MTU_MAX = 517;` (đọc qua bản sao LineageOS của AOSP) | **ĐÃ CÓ NGUỒN SƠ CẤP** cho trần 517. Nguồn: https://raw.githubusercontent.com/LineageOS/android_packages_modules_Bluetooth/lineage-22.1/android/app/src/com/android/bluetooth/gatt/GattService.java |
| **Android bóp quét khi tắt màn hình** — cùng ngăn xếp AOSP, `le_scan/AppScanStats.java`: chú thích *"Weight is the duty cycle of the scan mode"*, các hằng `SCREEN_OFF_LOW_POWER_WEIGHT = 5`, `LOW_POWER_WEIGHT = 10`, `AMBIENT_DISCOVERY_WEIGHT = 25`, `BALANCED_WEIGHT = 25`, `LOW_LATENCY_WEIGHT = 100`, `LARGE_SCAN_TIME_GAP_MS = 24000`, và các chế độ `SCAN_MODE_SCREEN_OFF` / `SCAN_MODE_SCREEN_OFF_BALANCED` | **ĐÃ CÓ NGUỒN SƠ CẤP** cho giới hạn chạy nền: đây là lý do kỹ thuật khiến bản Android phải dùng foreground service, và là việc phải **đo** ở WP4 |
| Bluetooth Mesh dùng relay + hạ tầng kiểu flooding — BlueZ `doc/mesh-api.txt` (thuộc tính `Relay`; *"flooding key update phase"*) và `mesh/net.c` (enum `_relay_advice`: `RELAY_NONE/ALLOWED/DISALLOWED/ALWAYS`) | Xác minh được **relay + flooding key**, nhưng **cụm chính xác "managed flooding" vẫn cần Mesh Profile spec** (PDF) — chưa lấy được trong phiên này |
| LE privacy/RPA, whitepaper BitChat | **Chưa xác minh qua nguồn sơ cấp** (whitepaper BitChat thì tác nhân khác đã mở được; phần RPA thì chưa) |

### 4.7 Năm khoảng trống đã kiểm chứng (dùng để định vị đóng góp)

1. **Không có meta-analysis kiểu PRISMA** gộp sensitivity/specificity/F1 cho phát hiện ngã bằng IMU.
2. **Tỉ lệ báo động giả ngoài đời chỉ có vài nhóm công bố** (Bagalà 29 ca; Kangas 15 ca; Harari 37 ca; FARSEEING 143 ca) → tầng xác nhận của đề tài có thể được đối chiếu trực tiếp với các con số này.
3. **Không có nghiên cứu đo BLE mesh trên điện thoại thật** công bố tỉ lệ giao/độ trễ/năng lượng theo số nút và độ di động.
4. **Không có so sánh flooding vs gradient có số năng lượng** trong đúng bối cảnh BLE mesh.
5. **Không có phân tích giao thức/an ninh có bình duyệt cho BitChat**, và **không có kho dữ liệu ngã thực đời thường 2022–2026** nào xác minh được.

### 4.8 Bối cảnh chính sách và báo chí (nhãn `BÁO` — chỉ dùng cho Ch. 1)

| Nguồn | Trạng thái | Dùng để nói gì |
|---|---|---|
| **ITU, *Emergency telecommunications* (backgrounder)**, https://www.itu.int/en/mediacentre/backgrounders/Pages/emergency-telecommunications.aspx | **Đã mở toàn văn (200)** | ICT chống chịu là điều kiện của ứng phó kịp thời; ITU lo **NETP + cảnh báo sớm (EW4All)** = kênh *xuống* → khoảng trống còn lại là kênh *lên* (SOS tự động) |
| **PreventionWeb (UNDRR)**, *Why disaster risk management needs an offline-first communication layer*, 2026-07-17 | Có tiêu đề + ngày qua Google News RSS; **chưa mở toàn văn** | Xác nhận độc lập cho định vị "offline-first" |
| Tin tiếng Việt (Thanh Niên, VietNamNet, VnExpress, VNPT, Đà Nẵng, Sức khỏe & Đời sống, 2024-09 → 2026-07) | Có tiêu đề + ngày + nguồn; **chưa mở toàn văn** | Nhu cầu "SOS vì mất liên lạc" ở Việt Nam là thật; mất điện đi kèm mất sóng |
| Tin quốc tế (Tech Review Africa 2026-09-10; The Guardian Nigeria 2026-09-27; Panama City News Herald 2026-07-14) | Có tiêu đề + ngày; **chưa mở toàn văn** | Đối chứng "đã có người làm" và mức độ lan của mạng mesh phi thương mại |
| **GSMA Disaster Response** | **Không truy cập được** (Cloudflare 403) | Sẽ bổ sung sau nếu cần |

**Quy tắc:** mọi mục trong bảng này chỉ được viết dưới dạng *"theo [báo], ngày [X]…"* và **không** chống đỡ khẳng định kỹ thuật. Riêng ITU thì được trích như nguồn chính sách (không phải nguồn kỹ thuật).

**Quy tắc chung:** không đưa vào bảng bất kỳ mục nào chỉ biết qua đoạn hội thoại, chỉ biết qua tóm tắt của công cụ tìm kiếm, hoặc không mở được toàn văn khi con số là trọng yếu.
## 5. Sổ tìm kiếm (search boundary)

Phải ghi lại để tuyên bố "khoảng trống" là có thể kiểm tra:

| Trường | Giá trị |
|---|---|
| Ngày tìm | 2026-09-28 |
| CSDL/chỉ mục dự kiến | OpenAlex, Crossref, arXiv, Semantic Scholar, GitHub API, tìm kiếm web |
| Giới hạn ngôn ngữ | Không giới hạn (Anh + Việt) |
| Giới hạn thời gian | Ưu tiên 2018–2026 cho mạng/BLE; 2015–2026 cho phát hiện ngã |
| Truy vấn theo nhóm | (a) `fall detection IMU smartphone machine learning systematic review`; (b) `SisFall MobiFall UP-Fall dataset benchmark`; (c) `TinyML on-device fall detection battery phone`; (d) `BLE mesh disaster response store-and-forward survey`; (e) `Trickle RPL flooding comparison delivery ratio energy`; (f) `BLE ATT MTU 517 authentication truncated HMAC rotating identifier` |
| Tiêu chí nhận | Có bản ghi truy cập được; có số liệu dùng được; ưu tiên có dữ liệu/mã công khai |
| Tiêu chí loại | Không có URL/DOI; chỉ là mô tả dự án không có mã; nội dung không mở được mà con số là trọng yếu |
| Tuyên bố novelty | **not_assessed** — chỉ được nói "không tìm thấy trong phạm vi tìm kiếm đã ghi lại" |

---

## 6. Những gì không được trích trong bài

1. Mọi mục ở §2.2 chưa xác minh xong.
2. Bất kỳ con số nào đến từ đoạn tóm tắt AI tổng hợp mà chưa mở nguồn gốc.
3. Các câu kiểu "AI giúp định tuyến thông minh hơn" khi chưa có so sánh định lượng.
4. Số sao GitHub như một thước đo chất lượng khoa học.
5. Tên hội thi, giải thưởng, hoặc chức danh trong đoạn hội thoại (ví dụ "đạt giải thưởng lớn") khi chưa có nguồn chính thức.
6. Dữ liệu/mã của các kho ở Bảng 2.1 khi chưa kiểm giấy phép — lưu ý mục #2 **không có giấy phép**.
