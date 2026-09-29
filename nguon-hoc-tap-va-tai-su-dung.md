# Nguồn học tập — tái sử dụng và tối ưu — RescueMesh-AI

**Tài liệu liên quan:** [Kế hoạch nghiên cứu](ke-hoach-nghien-cuu-rescuemesh-ai.md) · [Cấu trúc đề tài](cau-truc-de-tai-rescuemesh-ai.md) · [Xác minh nguồn & tài liệu tham khảo](xac-minh-nguon-va-tai-lieu-tham-khao.md)
**Ngày quét:** 2026-09-28 · **Trạng thái:** đã xác minh danh tính nguồn; chưa đọc toàn văn các bài mới

Mục đích của tài liệu này: với **mỗi** nguồn, trả lời ba câu — *lấy gì*, *không lấy gì*, *tiết kiệm được bao nhiêu thời gian*. Nguồn không ánh xạ được tới một work package thì không đọc.

---

## 1. Ba nguyên tắc chọn nguồn

1. **Học để làm, không học để biết.** Mỗi nguồn phải gắn với một artifact cụ thể (một bảng, một đoạn code, một thí nghiệm). Đọc xong mà không tạo ra artifact nào thì đã đọc sai.
2. **Tái sử dụng trước, tự viết sau.** Chỉ tự viết thứ (a) không tồn tại, (b) tồn tại nhưng không dùng được vì giấy phép/độ chín, hoặc (c) chính là đóng góp của đề tài. Simulator BLE, bộ trích đặc trưng, bộ chia tập, công cụ tính power: **không tự viết**.
3. **Giấy phép là ràng buộc thiết kế, không phải thủ tục.** Copy mã GPL-3.0 vào dự án là **buộc cả dự án thành GPL-3.0**. Xem §3 trước khi dán bất kỳ dòng mã nào.

---

## 2. Nguồn học thuật đã xác minh trong đợt quét này

Bổ sung cho [Xác minh nguồn](xac-minh-nguon-va-tai-lieu-tham-khao.md) §4. Mọi định danh dưới đây lấy từ Crossref/OpenAlex, không chép từ trí nhớ.

### 2.1 Nền tảng mô phỏng và định tuyến (dùng cho WP3)

| Nguồn | Dùng để làm gì |
|---|---|
| **The ONE simulator** — "The ONE simulator for DTN protocol evaluation", SIMUTools 2009, DOI `10.4108/icst.simutools2009.5674` (Crossref: 1.741 trích dẫn; OpenAlex: 2.323) | **Đòn tiết kiệm thời gian lớn nhất của cả dự án.** Simulator DTN trưởng thành có sẵn epidemic / Spray-and-Wait / PROPHET, sinh vết di động, đo được tỉ lệ giao và độ trễ. Dùng làm **đối chứng chéo** cho simulator tự viết, không dùng để mô phỏng BLE |
| "Simulating Mobility and DTNs with the ONE" — *JCM* 2010, DOI `10.4304/jcm.5.2.92-105` | Hướng dẫn dùng The ONE: cấu hình vết di động, chạy kịch bản, đọc báo cáo |
| **Trickle** — RFC 6206; "Optimizing the Trickle Algorithm", *IEEE Comm. Letters* 2015, DOI `10.1109/lcomm.2015.2408339` | Tham số Trickle (k, Imin, Imax) và cách chỉnh; cơ sở cho "flooding có kiểm soát" ở WP3 |
| **RPL** — RFC 6550; đánh giá hiệu năng RFC 6687 | Cơ sở khái niệm cho gradient |
| "A Novel Adaptive and Efficient Routing Update Scheme for Low-Power Lossy Networks in IoT", *IEEE IoT-J* 2018, DOI `10.1109/jiot.2018.2862364` | Ví dụ về cải tiến Trickle/RPL — dùng để **đặt ngưỡng kỳ vọng**, tránh kỳ vọng phi thực tế vào gradient |

### 2.2 BLE — số liệu và giới hạn (dùng cho Ch. 2.1 và WP4)

| Nguồn | Dùng để làm gì |
|---|---|
| "Bluetooth Low Energy Mesh: Applications, Considerations and Current State-of-the-Art", *Sensors* 2023, DOI `10.3390/s23041826` (Natgunanathan, Fernando, Loke, Weerasuriya) | Khảo sát chuẩn nhất cho chương nền tảng; đối chiếu với Bluetooth Mesh chính thức (relay/proxy, mô hình flooding có quản lý) so với mesh điện thoại tự chế |
| "Analysis of Latency Performance of Bluetooth Low Energy (BLE) Networks", *Sensors* 2015, DOI `10.3390/s150100059` | Số đo độ trễ BLE — mốc để kiểm tra ngân sách độ trễ của mình có hợp lý không |
| "Data Transmission Efficiency in Bluetooth Low Energy Versions", *Sensors* 2019, DOI `10.3390/s19173746` | Hiệu suất truyền theo phiên bản BLE — dùng cho phần "vì sao 20 byte là ràng buộc thật" |
| "Security and Privacy Threats for Bluetooth Low Energy in IoT and Wearable Devices: A Comprehensive Survey", *IEEE OJ-COMS* 2022, DOI `10.1109/ojcoms.2022.3149732` | Mô hình mối đe dọa ở §8.6 của kế hoạch; dùng để viết phần an ninh có căn cứ thay vì suy đoán |
| "A Survey on Multihop Ad Hoc Networks for Disaster Response Scenarios", 2015, DOI `10.1155/2015/647037` | **Thay thế cho đoạn tài liệu AI tổng hợp**: khảo sát học thuật thật về mạng nhiều chặng cho cứu hộ |
| "From Sensors to Safety: Internet of Emergency Services (IoES)…", *JSAN* 2023, DOI `10.3390/jsan12030041` | Bối cảnh ứng dụng; dùng cho Chương 1.1 |
| "CodeBlue: An Ad Hoc Sensor Network Infrastructure for Emergency Medical Care", 2004 (không DOI — **chưa xác minh**) | Tiền lệ kinh điển; chỉ trích nếu mở được toàn văn |

### 2.3 Phát hiện ngã — bổ sung quan trọng cho H1

| Nguồn | Dùng để làm gì |
|---|---|
| **"A Low-Power Fall Detector Balancing Sensitivity and False Alarm Rate", *IEEE JBHI* 2017, DOI `10.1109/jbhi.2017.2778271`** | **Đúng bài toán của tầng 3**: đánh đổi sensitivity ↔ báo động giả trong điều kiện công suất thấp. Đây là bài phải đọc kỹ nhất cho H1 |
| "Detecting Falls with Wearable Sensors Using Machine Learning Techniques", *Sensors* 2014, DOI `10.3390/s140610691` | Baseline ML kinh điển |
| "Human Activity Recognition Using Inertial Sensors in a Smartphone: An Overview", *Sensors* 2019, DOI `10.3390/s19143213` | Chuẩn hoá trích đặc trưng và cửa sổ trượt |
| "AI Benchmark: All About Deep Learning on Smartphones in 2019", *ICCVW* 2019, DOI `10.1109/iccvw.2019.00447` | Số đo độ trễ/năng lượng suy luận trên điện thoại — lấp phần "TinyML chưa xác minh" ở tài liệu xác minh §4.3 |
| "World guidelines for falls prevention and management for older adults", *Age and Ageing* 2022, DOI `10.1093/ageing/afac205` | Một câu bối cảnh y tế ở Chương 1 — vì sao phát hiện ngã quan trọng |

### 2.4 Hai khoảng trống vẫn đứng vững sau đợt quét này

- **Không tìm thấy so sánh flooding vs gradient có kèm cả tỉ lệ giao và năng lượng** trong mạng công suất thấp — đã tìm thêm ở 4 truy vấn khác nhau (Trickle optimization, RPL vs flooding, gossip vs tree) và chỉ ra các bài *cải tiến* Trickle/RPL, không phải so sánh có số năng lượng.
- **Không tìm thấy nghiên cứu đo BLE mesh trên điện thoại thật.** Vẫn phải tự đo ở WP4.

---

## 3. Repo git — bản đồ tái sử dụng

Đã xác minh qua GitHub API / tệp LICENSE thô ngày 2026-09-28.

| Repo | Giấy phép | Lấy gì | **KHÔNG** lấy gì |
|---|---|---|---|
| `akeranen/the-one` (246★, Java, cập nhật 2024-12) | **GPL-3.0** (đã đọc `LICENSE.txt`) | Chạy như **công cụ ngoài** để đối chứng định tuyến; đọc thiết kế vết di động & báo cáo | Không copy mã vào dự án (GPL lây). Chỉ dùng ở mức chạy lệnh + trích kết quả |
| `contiki-ng/contiki-ng` (1.531★, C, BSD-3-Clause) | BSD-3-Clause | Tham chiếu **cách cài Trickle và RPL** (rpl-lite, trickle timer) để viết đúng ngữ nghĩa; mượn ý tưởng tham số | Không copy toàn bộ OS; không cố đưa Contiki vào điện thoại |
| `nsnam/ns-3-dev-git` (562★, C++) | API báo NOASSERTION (**cần xác minh**, ns-3 vốn GPL-2.0) | Chỉ để đối chiếu khái niệm mô hình kênh BLE nếu cần | Không dựng ns-3 cho dự án này — chi phí học lớn hơn lợi ích (xem §5, quy tắc 1) |
| `tensorflow/tflite-micro` (3.096★, Apache-2.0) · `tensorflow/tensorflow` (200.586★, Apache-2.0) | Apache-2.0 | Xuất mô hình int8 và chạy suy luận; **Apache-2.0 dùng thoải mái** | Không cần TFLite Micro cho bản Python; chỉ dùng khi làm app Android |
| `scikit-learn/scikit-learn` (67.407★, BSD-3-Clause) | BSD-3-Clause | RF/GBDT, chia tập `GroupKFold` theo người (chống rò rỉ), `cross_val_predict` | Không tự viết lại chia tập theo người |
| `networkx/networkx` (17.294★) | API báo NOASSERTION (**cần xác minh**; thực tế BSD-3) | Dựng topology, kiểm tra bậc/liên thông, vẽ đồ thị | Không dùng để mô phỏng thời gian (NetworkX không có hàng đợi sự kiện) |
| `simpy/simpy` (PyPI) | **Cần xác minh** (pypi.org không truy cập được từ môi trường này) | Khung mô phỏng rời rạc theo sự kiện cho simulator tự viết (WP1) | Nếu không xác minh được giấy phép, thay bằng vòng lặp sự kiện tự viết (~100 dòng) |
| `Soodok/MeshChat` (6★, Kotlin, **MIT** — đã đọc LICENSE) | MIT | Tham chiếu kiến trúc **BLE mesh + Wi-Fi Direct + ECDH P-256 + AES-256-GCM** cho phần an ninh; MIT nên đọc thoải mái | Độ chín thấp (6★) — không coi là chuẩn, không copy UI |
| `permissionlesstech/bitchat` (36.288★, Unlicense) | Unlicense | Đọc **WHITEPAPER.md §6.2 Couriers** (thẻ người nhận 16 byte xoay vòng) và format gói để so sánh | Unlicense **không** miễn trừ bằng sáng chế/nhãn hiệu; không copy nhãn hiệu hay UI |
| `permissionlesstech/bitchat-android` (7.661★) + `AleksPlekhov/…` (fork của nó) | **GPL-3.0** | Chỉ **đọc để học** cách tổ chức BLE mesh, dedup, TTL | **Không copy mã** trừ khi chấp nhận cả dự án thành GPL-3.0. Cũng **không** trích chỉ số README |
| `meshtastic/firmware` (8.3k★, GPL-3.0) | GPL-3.0 | Hiểu mô hình flooding của một hệ thống đã triển khai thực tế | Không copy; Meshtastic dùng LoRa, khác bài toán |
| `jionbiju/ResQMesh` (1★, không giấy phép) · `betarcomms/project-mesh` (1★, AGPL-3.0) | none / AGPL-3.0 | Chỉ để biết "đã có người làm ý tưởng tương tự" trong Bảng định vị 1.1 | Không copy: **không giấy phép = không có quyền dùng**, AGPL còn chặt hơn GPL |

**Quy tắc một dòng:** muốn giữ dự án ở giấy phép tự chọn (ví dụ MIT) thì chỉ dùng **Apache-2.0 / MIT / BSD**; mọi thứ GPL/AGPL chỉ được **đọc**, không được **dán**.

---

## 4. Nguồn "báo" — công nghiệp, chuẩn, báo chí

Nhóm này dùng cho **bối cảnh và động lực**, mang nhãn `BÁO`, và **không bao giờ** dùng để chống đỡ một khẳng định kỹ thuật.

| Nhóm | Nguồn | Dùng cho | Trạng thái truy cập |
|---|---|---|---|
| Tính năng thương mại | Apple Watch Fall Detection; Google Pixel/Wear OS fall & crash detection | Chương 1.2: "bài toán đã được công nghiệp thừa nhận", và §giới hạn: khác biệt của ta là **chạy trong mesh ngoại tuyến** | `support.apple.com` trả về content-type lạ, trang JS → **chưa lấy được nội dung, cần xác minh** |
| Chuẩn ngành | Bluetooth SIG: Bluetooth Mesh (relay/proxy, mô hình flooding có quản lý); Bluetooth Core spec (ATT MTU, PHY) | Chương 2.1: vì sao thiết kế của ta bám ràng buộc thật; và **đối chứng quan trọng**: chuẩn công nghiệp chọn *managed flooding*, nên muốn nói gradient tốt hơn thì phải đo | `bluetooth.com` trả 200 nhưng chỉ lấy được tiêu đề (JS) → **phải lấy spec PDF** |
| Chuẩn viễn thông | 3GPP PWS/ETWS (cảnh báo công cộng), ITU-T khuyến nghị cứu hộ khẩn cấp | Chương 1.1: khoảng trống giữa cảnh báo một chiều và SOS hai chiều | **Chưa xác minh** |
| Tổ chức | ITU, GSMA Disaster Response, FEMA/NIMS (ICS-213) | Bối cảnh và định dạng báo cáo tình huống | ICS-213 đã xác minh qua mã của ResQMesh (A); các báo cáo ITU/GSMA **chưa xác minh** |
| Báo chí & cộng đồng | Tin về BitChat/Meshtastic trong các đợt mất Internet diện rộng | Phần "tính thời sự" của mở đầu — **chỉ trích như hiện tượng**, không như số liệu kỹ thuật | **Đã lấy được** qua GDELT + Hacker News Algolia (vì `web_search` hỏng) → xem §4.1 |

### 4.1 Tin báo và thảo luận cộng đồng đã lấy được (2026-09-28)

Lấy bằng **GDELT** (báo chí toàn cầu) và **Hacker News Algolia** (thảo luận kỹ thuật, có số điểm) — hai nguồn này **không** render bằng JS nên vẫn dùng được khi `web_search` hỏng.

| Ngày | Nguồn | Tiêu đề / nội dung | Ý nghĩa cho đề tài |
|---|---|---|---|
| 2025-07-07 | HN, 795 điểm | *Bitchat – A decentralized messaging app that works over Bluetooth mesh networks* | Cộng đồng kỹ thuật quan tâm ở quy mô lớn |
| 2025-11-14 | HN, 517 điểm | *Bitchat for Gaza – messaging without internet* | **Tình huống thật** mất Internet hoàn toàn → động lực mở đầu |
| 2026-07-24 | HN, 543 điểm | *Government orders GitHub to remove Bluetooth-based chat app Bitchat* | Rủi ro pháp lý/phân phối của ứng dụng mesh — một câu cho phần thảo luận |
| 2026-07-25 | HN, 270 điểm | *Bitchat is now on Radicle* | Cách dự án né kiểm duyệt hạ tầng |
| 2026-07-25/26 | hindustantimes.com; siasat.com | *Delhi sees its longest internet shutdown…*; *You cannot delete Bluetooth: India war on Bitchat code* | **Ngắt mạng diện rộng do chính quyền** là kịch bản thật, không chỉ thảm họa thiên nhiên |
| 2026-07-25 | newsx.com | *No Mobile Internet? Here Are The Apps That Still Work Offline* | Nhu cầu người dùng cuối đã được báo chí phổ thông ghi nhận |
| 2026-08-01 | tribuneindia.com | *Bitchat & the challenge of Internet-free messaging* | Tổng quan báo chí để dẫn ở Chương 1 |
| 2021-01-31 → 2026-05-27 | HN, 301–524 điểm | 5 bài về Meshtastic (giới thiệu; so sánh Meshtastic/MeshCore/Reticulum) | Đối chứng "hệ đã triển khai thật" |

**Cách dùng:** chỉ viết ở Chương 1 dạng *"đã có hiện tượng thực tế…"* kèm ngày và URL. **Không** dùng số điểm HN hay tiêu đề báo để chống đỡ khẳng định kỹ thuật.

### 4.2 Bối cảnh chính sách: ITU (đã lấy được toàn văn)

Nguồn: ITU, *Emergency telecommunications* (backgrounder), https://www.itu.int/en/mediacentre/backgrounders/Pages/emergency-telecommunications.aspx — nhãn `BÁO`/chính sách, dùng cho Chương 1.1, **không** dùng cho khẳng định kỹ thuật.

Nguyên văn dùng được:

- *"Climate change is causing an increase in extreme weather events and disasters. Coupled with population growth and rapid urbanization, these events expose more and more people to risk of death, injury, and displacement. Extreme weather also endangers communities, livelihoods, and information and communication technology (ICT) infrastructure."*
- *"Resilient ICT infrastructure is essential for managing disasters and reducing risks. It assures a timely disaster response by allowing governments, organizations, and other responders to exchange information. Resilient ICTs enable communities to receive early warnings and disaster alerts **in seconds**."*
- ITU hỗ trợ các nước xây dựng **National Emergency Telecommunication Plans (NETP)** và là đối tác chính của sáng kiến **Early Warnings for All (EW4All)** của Tổng thư ký LHQ.
- *"The UN World Population Prospects Report predicts an increase of 2 billion people by 2050."*

**Câu định vị rút ra được từ nguồn này (rất hữu ích cho phần mở đầu):** trọng tâm của ITU/NETP là **cảnh báo sớm và điều phối** — tức kênh *xuống*. Khoảng trống còn lại đúng là kênh *lên*: **SOS tự động từ người không còn khả năng thao tác**. Đây là cách định vị đề tài dựa trên một nguồn chính sách thật, thay vì suy đoán.

### 4.3 Tin tiếng Việt (đã lấy được qua Google News RSS)

| Ngày | Nguồn | Tiêu đề | Dùng để nói gì |
|---|---|---|---|
| 2025-11-20 | Báo Thanh Niên | *'SOS' khắp mạng xã hội vì mất liên lạc với người thân vùng lũ* | **Nhu cầu SOS là thật và đang phải bù bằng mạng xã hội** — đúng bài toán đề tài |
| 2026-07-18 | Sức khỏe & Đời sống | *Mưa lũ ở Lai Châu: 1 người tử vong, 5 người mất liên lạc, nhiều khu vực bị cô lập* | Khu vực bị cô lập = mất kết nối, không chỉ mất thoại |
| 2025-11-20 | VietNamNet | *Người dân vùng lũ "không điện, không sóng", nhà mạng xuyên đêm khắc phục sự cố* | Mất điện kéo theo mất sạc pin — ràng buộc năng lượng |
| 2025-11-07 | Báo Thanh Niên | *Gia Lai: Hàng trăm mái nhà bị 'vò' nát, mất điện, mất sóng sau bão số 13 Kalmaegi* | Sự cố lặp lại nhiều mùa bão, không phải cá biệt |
| 2025-11-01 | Báo Đà Nẵng | *Nhiều khách hàng MobiFone bị mất sóng kéo dài trong mưa lũ* | Mất sóng kéo dài theo ngày |
| 2024-09-17 | VnExpress | *Vì sao Lào Cai, Cao Bằng, Yên Bái hứng chịu sạt lở, lũ quét?* | Địa hình gây cô lập — lý do mesh không có trạm gốc |
| 2024-09-17 | VNPT | *Gian nan vượt ngàn, lên non "Nối sóng"* | Ứng phó của nhà mạng sau bão Yagi (đối chứng "cách hiện tại") |

**Quốc tế cùng chủ đề (đáng chú ý nhất):**

| Ngày | Nguồn | Tiêu đề | Vì sao quan trọng |
|---|---|---|---|
| 2026-07-17 | **PreventionWeb (nền tảng của UNDRR)** | *Why disaster risk management needs an offline-first communication layer* | **Xác nhận độc lập cho định vị "offline-first"** từ một nền tảng LHQ — nên trích ở Chương 1 |
| 2026-09-10 | Tech Review Africa | *ITU calls for stronger emergency telecommunications to protect lives during disasters* | ITU đang thúc đẩy đúng hướng này (2026) |
| 2026-09-27 | The Guardian Nigeria | *18-Year-old Nigerian-German unveils SafeLink app for offline emergency rescue* | Đối chứng "đã có người làm" → phải nêu trong Bảng định vị 1.1 |
| 2026-07-14 | Panama City News Herald | *The little-known communications network spreading across Bay County* | Ví dụ một mạng mesh phi thương mại lan ra cộng đồng thật |

### 4.4 Còn thiếu

- **GSMA**: `gsma.com` bị Cloudflare chặn (403 "Just a moment...") và `itu.int` trang ITU-D trả **"Request Rejected"** (WAF) → hai nguồn này **không lấy được** trong phiên; nếu cần trích GSMA thì phải mở bằng trình duyệt thật.
- Tin về **Meshtastic trong một thảm họa cụ thể có tên** (ví dụ sau một cơn bão ở Mỹ) để làm ví dụ triển khai — hiện chỉ có bài Bay County.

---

## 5. Làm sao để tối ưu và hiệu quả nhất

### 5.1 Mười quy tắc (thứ tự quan trọng giảm dần)

1. **Không viết simulator BLE từ đầu.** Viết vòng lặp sự kiện nhỏ (hoặc SimPy) + mô hình PDR **đo được**, rồi **đối chứng chéo bằng The ONE** cho phần định tuyến. Chỉ mô phỏng thứ không thể đo: mật độ 200 nút, trạm sập, 30 seed.
2. **Không tự thu dữ liệu ngã.** SisFall + FARSEEING là đủ; tự thu là 4–6 tuần và không so sánh được với công bố.
3. **Bắt đầu từ baseline đã công bố, không từ trực giác.** Villa & Casilari 2025: CNN-LSTM, cửa sổ 4 giây giữa đỉnh 2 g, 20 Hz. Chạy lại đúng cấu hình đó trước, rồi mới ablation.
4. **Khóa ngân sách FAR trước khi huấn luyện.** Nếu không, mọi "cải tiến" sau đó đều là tối ưu trên tập đã nhìn.
5. **Đo trước, tối ưu sau.** Với mỗi thứ định tối ưu (kích thước gói, tần suất beacon, kích thước mô hình), phải có một số đo trước — nếu không thì đang tối ưu cảm giác.
6. **Một lệnh tái lập từ ngày đầu.** `make tables` sinh mọi bảng/hình từ config + seed. Chi phí làm sớm: 1 ngày. Chi phí làm muộn: 2 tuần.
7. **Timebox theo cổng.** Mỗi WP có cổng Gx; hết thời gian mà chưa qua cổng thì **thu hẹp phạm vi và ghi rõ**, không gia hạn vô hạn.
8. **Tối ưu hệ thống bằng bốn đòn bẩy có số đo** (thay vì đoán): (a) *không khí* — giảm số lần phát bằng Trickle/TTL và gộp beacon; (b) *năng lượng* — đẩy tầng 1 xuống sensor hub, tầng 2 chỉ chạy khi có ngưỡng; (c) *mô hình* — 20 Hz + int8 + cửa sổ 4 giây (TinyFallNet: 0,70 MB, 98,00 % acc); (d) *độ tin cậy* — tầng 3 và ACK, đo bằng số lần phát lại.
9. **Dùng công cụ đo có sẵn** (`dumpsys batterystats` / Battery Historian cho pin; `perfetto` cho thời gian BLE) thay vì tự viết logger.
10. **Mỗi tuần một artifact.** Nếu cuối tuần không có bảng/hình/log mới thì tuần đó đã trôi.

### 5.2 Điều KHÔNG nên làm (đã tốn thời gian của người khác)

- Đọc 20 survey trước khi viết dòng code đầu tiên → đọc **1** survey (BLE mesh 2023) + **1** bài sát bài toán (JBHI 2017).
- Dựng app Android đầy đủ trước khi qua G1/G2 → codec Python + test trước, app sau.
- Tự viết lại giao thức thay vì bám một thiết kế tham chiếu (BitChat) → sẽ mất 3–4 tuần và không so sánh được.
- Tối ưu mô hình (kiến trúc, siêu tham số) trước khi khóa ngân sách FAR → tối ưu nhầm mục tiêu.
- Viết lại phần đã có thư viện chuẩn (chia tập theo người, trích 20 đặc trưng, tính power) → dùng `sklearn`/`tsfresh`.
- Trích bài predatory hoặc chỉ số README → đã có tiền lệ trong chính dự án này (một bài chứa trích dẫn bịa).

### 5.3 Lộ trình "học để làm" 10 ngày

Mỗi ngày đọc **tối đa 2 giờ**, phần còn lại làm artifact. Ngày nào không ra artifact thì dừng đọc.

| Ngày | Đọc | Artifact phải có |
|---|---|---|
| 1 | BLE mesh survey 2023 (tóm tắt + phần kiến trúc) | Bảng 2.1 ràng buộc nền tảng; xác nhận lại payload 20 byte từ **spec** |
| 2 | RFC 6206 + "Optimizing the Trickle" | Bảng tham số Trickle cho WP3 |
| 3 | The ONE: README + một kịch bản mẫu | Chạy được 1 kịch bản The ONE, xuất CSV tỉ lệ giao |
| 4 | JBHI 2017 (đánh đổi SE ↔ FAR) | Ghi chú 1 trang: ngân sách FAR và cách đo |
| 5 | Villa & Casilari 2025 (baseline) | Script nạp SisFall + chia `GroupKFold` theo người chạy được |
| 6 | Casilari 2017 (cửa sổ, tần số) | Pipeline đặc trưng 4 giây/20 Hz, xuất ma trận đặc trưng |
| 7 | Số liệu BLE latency + data efficiency | Bảng ngân sách độ trễ lý thuyết (trước khi đo) |
| 8 | OJ-COMS 2022 (an ninh BLE) | Mô hình mối đe dọa 1 trang, chốt phương án khóa |
| 9 | AI Benchmark 2019 (độ trễ/năng lượng trên máy) | Kế hoạch đo pin/TFLite cho WP4 |
| 10 | The ONE: kết quả đối chứng | Simulator tự viết chạy song song và khớp xu hướng với The ONE |

---

## 6. Bản đồ khả năng truy cập mạng (để lần sau không mất thời gian)

| Đích | Kết quả trong phiên này |
|---|---|
| `raw.githubusercontent.com` | **Tốt, không tính hạn mức** — cách tốt nhất để lấy mã nguồn/hằng số sơ cấp |
| `api.github.com` | Tốt nhưng **cạn 60 request/giờ** rất nhanh → ưu tiên `raw` khi biết đường dẫn |
| `api.crossref.org`, `api.openalex.org`, Europe PMC REST | **Tốt** (Crossref/OpenAlex có lúc 429 → chèn 1,5–2 giây giữa các truy vấn) |
| **`api.gdeltproject.org`** (tin báo toàn cầu) | **Tốt** cho 2–3 truy vấn đầu rồi **429** → chạy rải ra |
| **`hn.algolia.com`** (Hacker News) | **Tốt, không hạn chế** — có ngày và số điểm |
| **`news.google.com/rss/search`** (Google News RSS) | **Rất tốt, không cần khoá, không JS** — chạy được cả tiếng Việt (`hl=vi&gl=VN&ceid=VN:vi`) và tiếng Anh. **Đây là nguồn tin báo tốt nhất khi `web_search` hỏng** |
| ITU backgrounder (`mediacentre/backgrounders`) | **200, đọc được toàn văn** — nguồn chính sách dùng được |
| `gsma.com`, `itu.int/en/ITU-D/...` | **403 Cloudflare** / **"Request Rejected"** (WAF) → cần trình duyệt thật |
| **Bản sao AOSP của LineageOS** (`LineageOS/android_packages_modules_Bluetooth`) | **Tốt** — thay `developer.android.com` bị JS; cho hằng số thật (`GATT_MTU_MAX = 517`, trọng số quét nền) |
| **BlueZ** (`bluez/bluez`) | **Tốt** — nguồn sơ cấp cho `BT_ATT_DEFAULT_LE_MTU 23` và hạ tầng relay/flooding của Bluetooth Mesh |
| `rfc-editor.org` | **Tốt** |
| `android.googlesource.com` (`?format=TEXT`) | **Trả về rỗng** trong phiên này → dùng bản sao LineageOS |
| `docs.zephyrproject.org`, `bluetooth.com` | Chỉ trả tiêu đề/vỏ JS |
| `pypi.org` | **Không truy cập được** (treo) → không kiểm được giấy phép thư viện Python |
| `developer.android.com`, `support.apple.com`, `bluetooth.com`, `kaggle.com` | **Chỉ trả tiêu đề** (render bằng JS) hoặc content-type lạ |
| `researchgate.net` | 403 |
| `mdpi.com` | 403 (nhưng bài MDPI lấy được **tóm tắt qua Crossref**) |
| `api.semanticscholar.org` | 429 |
| API arXiv (`export.arxiv.org/api`) | 406 toàn phiên → dùng trang tìm kiếm arXiv thay thế |
| `web_search` của harness | **Vẫn hỏng: HTTP 401.** Chẩn đoán: plugin `packages/web/web-search-deepseek` có endpoint **riêng** (`baseURL` trong namespace `web-search-deepseek`, ghi đè bằng `DEEPSEEK_SEARCH_BASE_URL`; `/messages` được nối thêm) nhưng **dùng chung khoá với adapter hội thoại** (`provider.ts`: *"Both providers share the API key"*). Hội thoại đi qua `https://opencode.ai/zen/go/v1`, còn search trỏ vào `https://api.deepseek.com/anthropic/v1/messages` → khoá hiện có không hợp lệ ở đích thứ hai. **Chỉ người dùng chọn được đích:** cần base URL kiểu Anthropic-Messages hợp lệ + khoá tương ứng, sửa ở **Settings → Plugins → Plugin configuration → Web search** hoặc đặt `DEEPSEEK_SEARCH_BASE_URL`. Tệp liên quan: `~/.dsh/profiles/web/cordis.patch.yml` |

**Hệ quả — và tin tốt:** ba trong bốn nhóm tưởng như cần `web_search` **đã lấy được bằng đường vòng** (§4.1 cho tin báo; AOSP/BlueZ cho MTU và giới hạn quét nền). Chỉ còn **báo cáo ITU/GSMA** và **tin tiếng Việt** thực sự chờ công cụ, vì GDELT đã hết hạn mức.

---

## 7. Việc cần làm trong 48 giờ

| # | Việc | Kết quả kiểm tra được |
|---|---|---|
| 1 | ~~Chạy lại 4 truy vấn~~ → **XONG 4/4**: tin báo quốc tế (§4.1), ITU + tin tiếng Việt (§4.2–4.3), AOSP (giới hạn nền), BlueZ+AOSP (MTU). Chỉ GSMA là không lấy được (Cloudflare) | Đã ghi vào tài liệu; câu định vị "ITU lo kênh xuống, ta lo kênh lên" |
| 2 | Tải The ONE, chạy 1 kịch bản mẫu | CSV tỉ lệ giao/độ trễ của epidemic và Spray-and-Wait |
| 3 | Kiểm giấy phép `simpy` và `networkx` (thủ công, vì pypi.org chết) | Một dòng ghi giấy phép + quyết định dùng/không |
| 4 | ~~Lấy nguồn cho **ATT MTU**~~ → **đã xong** (BlueZ `att-types.h:28` = 23; AOSP `GattService.java:145` = 517). Còn lại: **Mesh Profile spec** cho cụm "managed flooding" | Một trích dẫn sơ cấp nữa để bỏ hẳn nhãn `SUY` ở Ch. 2.1 |
| 5 | Đọc JBHI 2017, viết 1 trang về ngân sách FAR | Đoạn phương pháp cho §7 của kế hoạch, đóng băng trước khi chạy |
| 6 | Nạp SisFall + `GroupKFold` theo người chạy được | Log chia tập + số người mỗi fold |
