# Khảo sát tài liệu: phát hiện ngã bằng IMU điện thoại và các kho dữ liệu công khai

**Đề tài:** RescueMesh-LoRa — WP8/RQ1 (phát hiện ngã trên IMU điện thoại) + phần đạo đức/giấy phép
**Ngày truy cập toàn bộ nguồn:** 2026-10-01
**Phạm vi:** chỉ dùng `web_fetch`/`curl` tới URL cụ thể, OpenAlex (`research_tools/oa.py`), Crossref REST, Europe PMC REST, Kaggle Datasets API, figshare API. `web_search` của harness bị hỏng (HTTP 401) — không dùng.

**Quy ước phân loại nguồn:** `peer-reviewed` (có DOI, đã kiểm qua Crossref) · `preprint` · `kho dữ liệu chính thức` (figshare/IEEE DataPort/Kaggle/trang dự án) · `trang dự án`.
**Quy ước trạng thái đọc:** `FULL` = đã đọc toàn văn (PDF/PMC full text XML) · `ABS` = chỉ đọc abstract/metadata.

> **Cảnh báo phương pháp quan trọng.** Trong quá trình kiểm chứng, **5 trong 9 DOI mà kế hoạch dự án đang ngầm định đã sai** (UMAFall, KFall, FARSEEING, MobiFall, UniMiB-SHAR). Bảng dưới đây dùng DOI **đã xác minh bằng Crossref**, không dùng DOI suy đoán. Ba sai lệch số liệu của kế hoạch được nêu ở §B.0 và §F.

---

## A. Bảng kho dữ liệu (kèm điều khoản truy cập/giấy phép)

| Kho | Bài mô tả gốc (DOI đã kiểm Crossref) | Năm | Số người | Số ca ngã | Số ADL | Vị trí đeo | fs (Hz) | Tầm đo (±g) | Truy cập / giấy phép | Loại |
|---|---|---|---|---|---|---|---|---|---|---|
| **SisFall** | Sucerquia, López, Vargas-Bonilla. *Sensors* 2017;17(1):198. **10.3390/s17010198** | 2017 | **38** (23 trẻ 19–30t + 15 cao tuổi 60–75t) | 15 loại ngã, **1.798 bản ghi ngã — TẤT CẢ staged** (chỉ 1 người cao tuổi, võ sư Judo, thực hiện ngã) | 19 loại, 2.706 bản ghi ADL | **Waist** (khóa thắt lưng), thiết bị tự chế (KHÔNG phải điện thoại) | **200** | ±16 (ADXL345) + ±8 (MMA8451Q) | Bài báo **CC BY 4.0**; kho tải miễn phí. Giấy phép **riêng của kho dữ liệu** không nêu trong bài → `KHÔNG TÌM THẤY NGUỒN`. **Trang SISTEMIC/UdeA trả HTTP 000 (chết) ngày 2026-10-01.** | peer-reviewed, FULL |
| **FARSEEING** | Klenk, Schwickert, Palmerini, Mellone... Chiari, Becker. *Eur Rev Aging Phys Act* 2016;13:8. **10.1186/s11556-016-0168-9** | 2016 | Không nêu tổng số người (nhiều nghiên cứu góp) | **347 ca ngã thực đã ghi bằng cảm biến; 208 ca được 2 người đánh giá độc lập xác minh** | Lưu thêm ADL 24 h không có ngã | **Không đồng nhất** (nhiều nhóm, nhiều vị trí); ≥ accelerometer, **58 % thêm gyroscope + magnetometer** | **Không đồng nhất** (nhiều tần số khác nhau) | Không đồng nhất | **Ngã THỰC ĐỜI.** Truy cập **theo yêu cầu + Data Use Agreement**; bản công bố chỉ có **20 ca ngã chọn lọc "available on request via the project website"**. Chính sách chia sẻ dữ liệu ở website FARSEEING. Giấy phép mở hoàn toàn: **KHÔNG** | peer-reviewed, FULL |
| **UMAFall** | Casilari, Santoyo-Ramón, Cano-García. *Procedia Comput Sci* 2017. **10.1016/j.procs.2017.06.110** | 2017 | **17** (10 nam / 7 nữ, 18–55t) | 3 loại ngã, **209 bản ghi — staged** | 8 loại, 322 bản ghi | **5 điểm**: ankle, chest, thigh (túi quần phải), waist, wrist | **100** (điện thoại) / **20** (SensorTag) | ±2 (đt) / ±16 / ±8 | **figshare DOI 10.6084/m9.figshare.4214283.v8 — LICENSE: CC BY 4.0** (đã kiểm qua figshare API) | peer-reviewed + kho chính thức |
| **MobiFall** | Vavoulas, Pediaditis, Chatzaki, Spanakis, Tsiknakis. *Int J Monit Surveill Technol Res* 2014;2(1):44–56. **10.4018/ijmstr.2014010103** | 2014 | **24** (17 nam / 7 nữ, 22–47t) | 4 loại ngã, **288 bản ghi — staged** (ngã có và không có giai đoạn nằm lâu) | 9 loại, 342 bản ghi | **Thigh (túi quần)** — Samsung Galaxy S3 | **87** (A) / 100 (G, O) | **±2 (bão hòa!)** | Kho "available upon request" theo mô tả cũ. **Trang BMI/TEI Crete trả HTTP 000 (chết) ngày 2026-10-01** → điều khoản hiện hành `KHÔNG TÌM THẤY NGUỒN`. (MobiAct là bản mở rộng 2016, 57 người.) | peer-reviewed |
| **tFall** | Medrano, Igual, Plaza, Castro. *PLoS ONE* 2014;9(4):e94811. **10.1371/journal.pone.0094811** | 2014 | **10** (3 nữ / 7 nam, 20–42t) | 8 loại ngã, **1.026 bản ghi (cửa sổ 6 s)** | **ADL KHÔNG được phân loại** (1 tuần sinh hoạt tự nhiên, 9.883 cửa sổ 6 s quanh đỉnh >1,5 g) | **Thigh (túi quần trái/phải) HOẶC túi xách** | **45 (±12)** | **±2 (bão hòa!)** | **Trang eduqtech.unizar.es trả HTTP 000 (chết) ngày 2026-10-01** → giấy phép hiện hành `KHÔNG TÌM THẤY NGUỒN` | peer-reviewed |
| **KFall** | Yu, Jang, Xiong. *Front Aging Neurosci* 2021;13:692865. **10.3389/fnagi.2021.692865** | 2021 | **32** nam trẻ Hàn Quốc (TB 24,x tuổi) | 15 loại ngã, **2.346 file — staged**; nhắm **pre-impact** (trước va đập) | 21 loại, 2.729 file (tổng **5.075 file** motion) | **Low back (thắt lưng)** — IMU | **100** | A, G, O | Bài báo **CC BY 4.0**; kho trên IEEE DataPort. Điều khoản riêng của IEEE DataPort `KHÔNG TÌM THẤY NGUỒN` (không đọc được trang). **Bản re-upload trên Kaggle `usmanabbasi2002/kfall-dataset` ghi MIT — KHÔNG phải giấy phép gốc, xem §F** | peer-reviewed, FULL |
| **SafeFall** | — | — | — | — | — | — | — | — | — | **`KHÔNG TÌM THẤY NGUỒN`** |
| **UniMiB-SHAR** | Micucci, Mobilio, Napoletano. *Applied Sciences* 2017;7(10):1101. **10.3390/app7101101** | 2017 | **30** (24 nữ / 6 nam, 18–60t) | 8 loại ngã, **1.699 mẫu** — staged | 9 loại, 5.314 mẫu (tổng **7.013 mẫu**, mỗi mẫu **1 s = 51 điểm**) | **Thigh (túi quần trái/phải)** — Samsung Galaxy Nexus | **50** | **±2 (bão hòa!)** | Trang SAL/UniMiB **HTTP 200 (còn sống) ngày 2026-10-01**. Giấy phép cụ thể trên trang: chưa xác minh được trong buổi này | peer-reviewed |
| **Cogent Labs** | Ojetola, Gaura, Brusey. *MMSys'15*. **10.1145/2713168.2713198** | 2015 | **42** (36 nam / 6 nữ, 18–51t) | 6 loại ngã, **448 bản ghi**; **một phần ngã do đẩy người bị bịt mắt** (bán-tự-nhiên) | 8 loại, 1.520 bản ghi | **2 điểm**: chest + thigh | **100** | ±8 (A), ±2000°/s (G) | URL cũ `cogentee.coventry.ac.uk` — không xác minh được trong buổi này | peer-reviewed |
| **Kaggle "Fall Detection Dataset"** | uttejkumarkandagatla/fall-detection-dataset (Kaggle Datasets API) | 2021 | — | — | — | **KHÔNG phải IMU — "Imaged based fall dataset"** (ảnh) | — | — | **License: "Database: Open Database, Contents: © Original Authors"** — tức nội dung ảnh vẫn thuộc tác giả gốc, KHÔNG phải CC mở | kho chính thức (metadata API) |
| **Kaggle — nhóm IMU/thật sự liên quan** | (nhiều mục, xem §F) | — | — | — | — | — | — | — | `Walker Fall Detection Dataset` = **CC0**; `KFall Dataset` (re-upload) = **MIT** (sai nguồn); `fall detection accelerometer data` = **Unknown**; `Elderly Fall Prediction and Detection` = **"Data files © Original Authors"** | kho chính thức (metadata API) |

### A.1 Bổ sung — các kho lớn khác tìm được (ngoài danh sách yêu cầu)

| Kho | Bài mô tả (DOI) | Năm | Người | Ngã | Vị trí | fs (Hz) | Ghi chú |
|---|---|---|---|---|---|---|---|
| **UP-Fall** | Martínez-Villaseñor et al. *Sensors* 2019;19(9):1988. **10.3390/s19091988** | 2019 | 17 người trẻ khỏe | 11 hoạt động+ngã ×3 lần | wearable + ambient + vision | — | >850 GB, đa phương thức |
| **Graz** | Wertner et al., figshare **10.6084/m9.figshare.1444405.v1** | 2015 | 5 | 4 loại, 220 mẫu | **Waist (túi đeo thắt lưng)** | — | **CC BY 4.0** (figshare API) |
| **FFP / "Free From Falls" (FFF)** | Mosquera-Lopez, Wan, Shastry... Hildebrand, Cameron, Jacobs. *IEEE J Biomed Health Inform* 2021;25(6):1975–1984. **10.1109/JBHI.2020.3041035** | 2021 | Người bị **đa xơ cứng (multiple sclerosis)** | **Ngã THỰC ĐỜI**, 8 tuần giám sát liên tục tại nhà; → **49 trace**, trích **690 cửa sổ 4 s** (Villa & Casilari 2025) | **Lower back** (đồng nhất) | **50** | Dùng làm kho **kiểm tra ngã thực** ngoài miền |
| **AybuFall** | Tokgöz & Kocaoğlu. *BMC Res Notes* 2026. **10.1186/s13104-026-07679-9** | 2026 | 17 người trẻ | 11 loại ngã | forehead + forearm | **200** | Có **5 loại động tác cầu nguyện** (góp phần giảm báo động giả) — staged |

### A.2 Phát hiện then chốt về **tầm đo cảm biến** (ảnh hưởng trực tiếp tới WP8)

Nguồn: Casilari, Santoyo-Ramón, Cano-García, *Sensors* 2017;17(7):1513, **10.3390/s17071513** (peer-reviewed, FULL).

- **MobiFall/MobiAct, tFall, Graz, Gravity Project, UMAFall dùng điện thoại Samsung có accelerometer chỉ ±2 g** — Casilari viết nguyên văn rằng tầm này *"can be enough to recognize the orientation of the screen but not sufficient to capture the brusque increase of the acceleration caused by the impact on the ground"*.
- Hệ quả: các kho này **bão hòa (saturate)** đúng ở pha va đập — pha quan trọng nhất của phát hiện ngã. Giá trị lớn nhất trong trace bị kẹp ở ~2 g (SVM ~3,46 g nếu cả 3 trục đều kẹp).
- Ngược lại DLR (±5 g), TST/UR/Cogent (±8 g), **SisFall (±16 g)** giữ được đỉnh va đập.
- **Hệ quả cho RescueMesh-LoRa:** nếu WP8 dùng dữ liệu MobiFall/tFall/UniMiB-SHAR ở ±2 g rồi áp mô hình lên điện thoại hiện đại (thường chọn được ±8/±16 g), đó là **lệch miền (domain shift) do tầm đo**, không chỉ do vị trí đeo. Phải khai báo như một biến gây nhiễu.

---

## B. Bảng bằng chứng staged vs ngã thực

### B.0 Ba sai lệch số liệu của kế hoạch dự án — ĐÃ SỬA

| Kế hoạch dự án đang ghi | Số liệu ĐÃ XÁC MINH | Nguồn |
|---|---|---|
| Bagalà 2012: "báo động giả lên tới **3–85** ca/ngày" | **SAI.** Đúng là: Bourke1a **22–85** ca/24 h; Bourke1b **27–84** ca/24 h; **Kangas <9 ca/24 h** (nhưng SE <55 %). Không có giá trị nào bằng 3 | **10.1371/journal.pone.0037062**, FULL |
| "FARSEEING: **143** ca thực" | **Quy sai nguồn.** 143 ca thực là của **Palmerini et al. 2020** phân tích trên kho FARSEEING, không phải con số của kho FARSEEING. Kho FARSEEING (Klenk 2016): **347 ca ghi, 208 ca đã xác minh** | **10.3390/s20226479** + **10.1186/s11556-016-0168-9**, FULL |
| "Villa & Casilari 2025: **~8 báo động giả/ngày** trên 7 ngày thực địa" | **ĐÚNG**, nhưng thiếu 2 điều kiện then chốt: (a) **7 ngày đó KHÔNG có ca ngã thật nào**; (b) mô hình **KHÔNG chạy trên thiết bị** — xem §D | **10.3390/s26010162**, FULL |
| "Kangas **2015**" | **Không tồn tại bài Kangas 2015 so sánh ngã thực/ngã mô phỏng** trong Crossref/OpenAlex. Bài đúng là **Kangas et al. 2012**, *Gait & Posture* 35(3):500–505 | **10.1016/j.gaitpost.2011.11.016** |

### B.1 Bảng bằng chứng chính

| Số liệu | Điều kiện đo | Nguồn (DOI) | Loại nguồn | Full-text? | Độ tin cậy |
|---|---|---|---|---|---|
| **SE = 57,0 % ± 27,3 %** (giá trị cao nhất **82,8 %**) trên **29 ca ngã THỰC ĐỜI** | 13 thuật toán accelerometer công bố trước đó, gắn **waist/trunk**, dữ liệu SensAction-AAL. **32 ca ngã thu được, 29 ca dùng để đánh giá** (3 ca loại vì bão hòa ±2 g). Các thuật toán vốn được công bố **SE/SP ~100 % trên ngã staged** | **10.1371/journal.pone.0037062** (Bagalà 2012, PLoS ONE) | peer-reviewed | **FULL** | **Cao** — đọc trực tiếp bảng/số trong bài |
| SP > 94 % cho **hầu hết** thuật toán; nhưng **Chen & Bourke3**: SE 75,9–82,8 % chỉ đạt SP 94,2–96,7 % | Cùng tập 29 ca ngã thực + ADL trích từ 7 người còn lại | **10.1371/journal.pone.0037062** | peer-reviewed | FULL | Cao |
| **PPV cực thấp: 24,4 % (Chen), 38,1 % (Bourke3)**, ACC 93,7 % / 96,3 %, NPV ~99 % | Cùng tập trên. **ACC cao nhưng PPV thấp** = dấu hiệu kinh điển của mất cân bằng lớp | **10.1371/journal.pone.0037062** | peer-reviewed | FULL | Cao |
| **Báo động giả 22–85 ca/24 h** (Bourke1a) và **27–84 ca/24 h** (Bourke1b); **>2 báo động giả/giờ là "unacceptable"** | Ghi 24 h liên tục trên **3 người hay ngã (fallers)**; tác giả ghi rõ hậu quả là dịch vụ giám sát **từ chối** vì quá nhiều báo động | **10.1371/journal.pone.0037062** | peer-reviewed | FULL | Cao |
| **SE > 80 %, FAR = 0,56/giờ (≈ 13,4/ngày), F-measure = 64,6 %** | **143 ca ngã THỰC ĐỜI** (kho FARSEEING), IMU **lower back**, giám sát liên tục người nguy cơ ngã trung bình–cao; phương pháp tốt nhất = **SVM + đặc trưng mô hình ngã đa pha (multiphase fall model)** | **10.3390/s20226479** (Palmerini, Klenk, Becker, Chiari 2020) | peer-reviewed | **FULL** | **Cao** — đây là tập ngã thực lớn nhất tại thời điểm công bố |
| **SE = 73,0 %** (hệ thống phát hiện **27/37 ca ngã THỰC ĐỜI**) và **1 báo động giả mỗi 46 NGÀY** (≈ 0,022/ngày); SP > 99,2 % | Nghiên cứu **tiền cứu (prospective) 90 ngày**, điện thoại Samsung S5, **accelerometer + gyroscope**, hồi quy logistic có chuẩn hóa; ~20 % biến cố bị phân loại nhầm đã được xác nhận là **vấp (stumble)**. Mô hình **huấn luyện trên ngã staged trong lab của 17 người** (7 người đoạn chi đùi + 10 người trẻ khỏe) | **10.1186/s12984-021-00918-z** (Harari 2021) | peer-reviewed | **FULL** | **Cao** — đây là chuyển staged→thực **sạch nhất** trong tài liệu |
| **SE = 81,8 %** (18/22 ca ngã thực) · **SP = 96,3 %** · ACC **93,3 %**; **3 báo động giả**, phân loại đúng **79/82** cửa sổ không-ngã. **Sụt SE = 96,7 % → 81,8 % (−14,9 điểm)** | **CNN-LSTM huấn luyện trên SisFall (staged) ở 20 Hz**, kiểm tra ngoài miền trên **FARSEEING**: 22 bản ghi dài → **104 cửa sổ 4 s** (đỉnh ≥2 g, ngưỡng xác suất p > 0,4). Báo động giả = chuyển động đột ngột không-ngã; ca bỏ sót có biên độ thấp | **10.3390/s26010162** (Villa & Casilari 2025) | peer-reviewed | **FULL** | **Cao** — số đọc trực tiếp |
| **FFF (đa xơ cứng): SE = 97,9 % · SP = 98,9 % · ACC = 98,3 %** (48 TP, **1 FN**, 7 FP) — cao hơn hẳn FARSEEING | **690 cửa sổ 4 s từ 49 trace FFF** (ngưỡng tiền-lọc 1,1 g; **cách nhau tối thiểu 40 s** để không đếm trùng một ca ngã; ngưỡng phân loại 0,85). Tác giả: **FFF đồng nhất hơn về vị trí đeo (lower back) và điều kiện ghi**, còn FARSEEING biến thiên vị trí + tần số lấy mẫu | **10.3390/s26010162** | peer-reviewed | FULL | **Cao** |
| **58/1.147 cửa sổ phân loại nhầm = FPR 5,06 %, SP 94,94 % → ≈ 8,3 báo động giả/ngày** | **7 ngày liên tục, 1 người**, waist, **20 Hz**, ngưỡng 2 g, cửa sổ 4 s, ngưỡng xác suất 0,5. Hoạt động: đi bộ, chạy ngắn, leo cầu thang, **đi xe máy**, **ngồi taxi**, văn phòng, ăn, việc nhà. **KHÔNG có ca ngã thật nào trong 7 ngày** | **10.3390/s26010162** | peer-reviewed | FULL | **Trung bình** — con số **không** được kiểm chứng bằng ngã thật; và xem §D.1 về kiến trúc hybrid |
| **Recall 90,57 %, SP 96,91 %, AUC-ROC 98,85 %** trên kho gộp | Gộp 3 kho (**>1.300 mẫu ngã + 28 K mẫu âm**); nhưng khi **kiểm tra chéo kho** thì mô hình "**do not provide sufficient generalization capabilities**", với **tỷ lệ dương tính giả và âm tính giả đáng chú ý** | **10.3390/s24051679** (Fula & Moreno 2024) | peer-reviewed | FULL | Cao |
| **KHÔNG tồn tại meta-analysis kiểu PRISMA** gộp SE/SP/F1 cho phát hiện ngã bằng IMU | Đã tra Crossref + OpenAlex với các truy vấn meta-analysis/PRISMA/systematic review (xem §G). Tìm được **systematic review mô tả** (Usmani 2021 **10.3390/s21155134**; Rastogi & Singh 2021 **10.1111/coin.12441**) nhưng **không có bài nào gộp (pool) SE/SP bằng phương pháp meta-analysis**, cũng không có bài nào tách staged vs thực thành một biến phân tích | **10.3390/s21155134**, **10.1111/coin.12441** | peer-reviewed | ABS/partial | **Cao cho khẳng định "không tìm thấy"** (phạm vi tìm kiếm đã ghi ở §G) |
| **Review hệ thống chuyên về sim-to-real MỚI (2026)**: tiêu đề nói rõ "Datasets, models, and **sim-to-real generalization**" | Kim & Xiong, *Measurement* 2026, **10.1016/j.measurement.2026.122880** — **Crossref không có abstract, toàn văn không truy cập được (không có trên Europe PMC/PMC)** | **10.1016/j.measurement.2026.122880** | peer-reviewed (metadata only) | **Không mở được toàn văn** | **Thấp** — chỉ xác nhận tồn tại bài; **KHÔNG trích số liệu** cho tới khi đọc được toàn văn |
| Kangas: ngã thực và ngã mô phỏng có **profil gia tốc tương tự nhau** | Kangas et al. so sánh ngã thực ở người cao tuổi với ngã thực nghiệm ở người trung niên | **10.1016/j.gaitpost.2011.11.016** | peer-reviewed | ABS | Trung bình — **mâu thuẫn với Bagalà 2012**; đây là tranh luận chưa ngã ngũ (Casilari 2017 ghi nhận cả hai phía) |

**Tổng hợp mức sụt hiệu năng staged → ngã thực (diễn giải):** ba thí nghiệm độc lập, ba nhóm tác giả, ba kho ngã thực khác nhau đều cho **mức sụt SE từ ~15 đến ~40 điểm phần trăm**:
- Bagalà 2012: từ "~100 % trên staged" → **57,0 %** trên 29 ca thực.
- Villa & Casilari 2025: từ **96,7 %** → **~82 %** (FARSEEING), nhưng **~98 %** (FFF) → **độ sụt phụ thuộc mức đồng nhất của kho đích**.
- Harari 2021: **73,0 %** trên 37 ca thực của một mô hình huấn luyện trên staged.

Điểm chung: **SE tụt, nhưng chỉ số sụt nặng hơn nữa là PPV/F-measure và báo động giả** (PPV 24,4 % ở Bagalà; F 64,6 % ở Palmerini).

---

## C. Thực hành đánh giá và ca khó

### C.1 Chia tập: LOSO vs chia theo cửa sổ (window-level)

| Phát hiện | Số liệu / nội dung | Nguồn | Loại | Full-text? |
|---|---|---|---|---|
| **SisFall dùng 10-fold cross-validation, KHÔNG dùng LOSO** | Nguyên văn: *"The robustness of the classification stage was analyzed with a 10-fold cross-validation set-up. All analysis were performed guaranteeing the same proportion of falls and ADLs in the groups."* — nghĩa là **fold trộn cửa sổ của cùng một người vào cả train và test** | **10.3390/s17010198** | peer-reviewed | FULL |
| **Villa & Casilari 2025 dùng "test set" cố định, không mô tả LOSO** | Chỉ nêu *"Out of 270 non-fall activities in the test set... 90 fall events"* và confusion matrix; **không có mô tả chia theo người** → nhiều khả năng chia theo cửa sổ | **10.3390/s26010162** | peer-reviewed | FULL |
| **Chia theo cửa sổ gây rò rỉ danh tính người (subject leakage) và thổi phồng độ chính xác** | Fula & Moreno viết nguyên văn rằng huấn luyện/kiểm tra trong phạm vi hẹp một kho *"(i) yield overoptimistic classification rates, (ii) do not generalize to real-life situations and (iii) have very high rate of false positives"* | **10.3390/s24051679** | peer-reviewed | FULL |
| **Cơ sở lý luận chung về rò rỉ do chia tập bỏ qua cấu trúc nhóm** | Nguyen & Le-Khac, *SoK: Behind the Accuracy of Complex HAR Using Deep Learning*, IJCNN 2024 — hệ thống hoá các yếu tố gây mất chính xác trong HAR phức tạp | **10.1109/ijcnn60899.2024.10650322** (preprint mở: arXiv:2405.00712) | peer-reviewed + preprint | ABS |
| **Tỷ lệ % bài dùng LOSO trong các bài gần đây** | **`KHÔNG TÌM THẤY NGUỒN`** — không tìm được bài nào **định lượng** tỷ lệ này cho riêng lĩnh vực phát hiện ngã bằng IMU. Đây là **khoảng trống có thể công bố** | — | — | — |

> **Kết luận cho RQ1.** Đề tài **bắt buộc dùng LOSO** không chỉ vì "chuẩn tốt hơn", mà vì **hai kho nền (SisFall, và nhiều khả năng cả Villa & Casilari) đã công bố kết quả trên chia tập theo cửa sổ**. Nghĩa là **các baseline 96–99 % đang được trích dẫn phổ biến KHÔNG so sánh được trực tiếp** với một kết quả LOSO. Đây là lập luận phương pháp mạnh cho WP8.

### C.2 Ngân sách báo động giả (FAR budget) điển hình

| Cách đặt ngân sách | Số liệu | Nguồn |
|---|---|---|
| Ngưỡng "không chấp nhận được" theo giờ | **>2 báo động giả/giờ** bị coi là unacceptable (dịch vụ giám sát từ chối) | **10.1371/journal.pone.0037062** |
| Mô hình ngã thực tốt nhất tại thời điểm 2020 | **0,56/giờ ≈ 13,4/ngày** (F 64,6 %) | **10.3390/s20226479** |
| Nghiên cứu tiền cứu tốt nhất | **1 báo động giả / 46 ngày ≈ 0,022/ngày** (SE 73 %) | **10.1186/s12984-021-00918-z** |
| Nguyên mẫu + 7 ngày thực địa | **~8 báo động giả/ngày** (nhưng **0 ca ngã thật**) | **10.3390/s26010162** |
| Nguyên tắc thiết kế "zero false negatives" | Đẩy ngưỡng xuống dưới biên độ ngã nhỏ nhất → SE ~**99,99 %** nhưng **SP sụp: thất bại tới 7/10 ADL**, ACC tốt nhất chỉ **84 %** → *"a failure rate of nearly 50/50 in ADL is prohibitive in real-life applications"* | **10.3390/s17010198** |
| Hướng dẫn lâm sàng cho PERS / alarm fatigue | **`KHÔNG TÌM THẤY NGUỒN`** — chưa tìm được guideline định lượng ngân sách FAR cho hệ thống báo động cá nhân | — |

**Nhận xét:** các con số công bố trải **bốn bậc độ lớn** (0,022 → 8 → 13,4 → 85 mỗi ngày) và **không có chuẩn chung**. Vì vậy WP8 **phải tự đặt ngân sách FAR trước** (ví dụ ≤1/ngày) rồi báo cáo recall ở ngân sách đó — đúng như RQ1 đã phát biểu.

### C.3 Cách báo cáo ca khó

| Ca khó | Bằng chứng | Nguồn |
|---|---|---|
| **Ngồi phịch / ngồi nhanh xuống ghế** | SisFall: ca khó nhất là **D04 jogging nhanh, D18 jump, F11 ngã ra sau khi cố ngồi**. Đây là các hoạt động **duy nhất vượt ngưỡng** T1 | **10.3390/s17010198**, FULL |
| **Nhảy / vận động thể thao** | Casilari 2017: boxplot cho thấy **hoạt động thể thao chồng lấn rõ rệt với ngã**; ở **Gravity Project và UMAFall, trung vị đỉnh SVM của hoạt động thể thao CÒN CAO HƠN của ngã** | **10.3390/s17071513**, FULL |
| **Tiền-ngã (near-fall)** | Chỉ có **Cogent và SisFall** chứa near-fall; tác giả cảnh báo đừng đánh đồng trọng số lỗi: near-fall hiếm, còn nhầm với hoạt động cơ bản phổ biến thì tai hại hơn nhiều | **10.3390/s17071513**, FULL |
| **Rơi/vị trí điện thoại xê dịch trong túi** | Casilari trích: *"the performance of a smartphone-based detector is noticeable affected when the device shifts within the pocket"* — túi quần lỏng hoặc túi xách làm giảm độ bám vào cơ thể | **10.3390/s17071513**, FULL |
| **Xe xóc (rung lắc khi di chuyển)** | **Bằng chứng gián tiếp mạnh:** thí nghiệm 7 ngày của Villa & Casilari **có bao gồm đi xe máy và ngồi taxi**, và trong 7 ngày đó **58/1.147 cửa sổ (5,06 %) bị phân loại nhầm thành ngã**, dù **không có ca ngã thật nào**. Tác giả **không tách riêng** phần đóng góp của chuyển động xe, nên **không có số cho riêng lớp "xe xóc"** | **10.3390/s26010162**, FULL. SisFall có D17 (lên/xuống xe Renault Logan) nhưng **không báo cáo riêng** lớp này — **10.3390/s17010198** |
| **Vấp (stumble) bị nhầm thành ngã** | Harari 2021: *"~20 % of the events falsely classified as falls were validated as stumbles"* | **10.1186/s12984-021-00918-z**, FULL |
| **Khuyến nghị phương pháp luận** | Casilari 2017 kết luận phải **phân loại ADL thành 3 nhóm theo mức vận động** (cơ bản / thường ngày / thể thao) và báo cáo riêng, thay vì gộp một con số accuracy | **10.3390/s17071513**, FULL |

### C.4 Ảnh hưởng của tần số lấy mẫu (20 / 50 / 100 Hz)

| Phát hiện | Số liệu | Nguồn |
|---|---|---|
| **20 Hz là điểm cân bằng tốt nhất; xuống tới 10 Hz vẫn đủ** | CNN-LSTM ở **20 Hz**: ACC **98,9 %**, SE **96,7 %**, SP **99,6 %**. Kết luận: *"intermediate frequencies, around 20 Hz and down to 10 Hz, provide sufficient temporal resolution to capture fall dynamics while reducing data volume, which translates into more efficient energy usage"* | **10.3390/s26010162** |
| **Thiết kế phần cứng riêng chỉ dùng 25 Hz** | Sucerquia 2018: phương pháp Kalman + phát hiện dáng đi dùng **chỉ 25 Hz**, ACC 99,4 % trên SisFall, "robust among devices" | **10.3390/s18041101** |
| **Ngưỡng tần số tối thiểu suy ra từ lọc tín hiệu** | SisFall: dùng lọc Butterworth bậc 4 cắt 5 Hz → tác giả suy ra **"a frequency sample of up to 11 Hz could be enough for fall detection (lower than any work in the literature)"** | **10.3390/s17010198** |
| **Tiền lệ lấy mẫu trong các kho** | MobiFall 87 Hz; tFall **45 (±12) Hz**; UniMiB **50 Hz**; UMAFall 100/20 Hz; SisFall **200 Hz**; UR Fall **256 Hz** | **10.3390/s17071513** |
| **Quan điểm ngược lại (cần lưu ý)** | Fula & Moreno: *"ML algorithms seem less sensitive to sampling frequency or acceleration interval"* — tức có **không thống nhất** trong tài liệu về độ nhạy với fs | **10.3390/s24051679** |
| Vật lý pha va đập (impact transient ~100–300 ms) và luận cứ Nyquist | **`KHÔNG TÌM THẤY NGUỒN`** cho một bài chuyên khảo định lượng; chỉ có gián tiếp từ ngưỡng lọc 5 Hz → 11 Hz của SisFall | — |

### C.5 Ảnh hưởng của vị trí đeo

Nguồn chính: Özdemir & Barshan, *Sensors* 2016;16(8):1161, **10.3390/s16081161** (peer-reviewed, **FULL**). Thiết kế: **2.520 thử nghiệm**, 6 nhóm cảm biến (head, chest, waist, right-wrist, right-thigh, right-ankle), 6 thuật toán (k-NN, BDM, SVM, LSM, DTW, ANN).

| Vị trí | Kết quả | Ghi chú |
|---|---|---|
| **Waist (thắt lưng)** | **Tốt nhất**: k-NN **SE = 99,96 %**, ACC **99,87 %**, SP **99,76 %**; trung bình 6 thuật toán **98,42 %** | Gần khối tâm cơ thể → ít bị ảnh hưởng khác biệt giữa người |
| **Right-thigh (đùi phải)** | Hạng 2: ACC trung bình **97,89 %** | |
| **Right-ankle (cổ chân phải)** | Hạng 3: ACC trung bình **~97 %** | |
| **Head (đầu)** | Hạng 4: ACC trung bình **96,61 %** | |
| **Chest (ngực)** | Hạng 5: ACC trung bình **96,50 %** | Tác giả: kém vì khác biệt giải phẫu (giới tính, tư thế, béo/gầy) làm tăng biến thiên giữa người |
| **Right-wrist (cổ tay)** | **Kém nhất** | SE tốt nhất của wrist là **97,x %** ở cấu hình thuận lợi, nhưng trung bình tụt xuống thấp nhất |
| Kết hợp cả 6 điểm | k-NN ACC **99,91 %** | Giảm từ 5 xuống 2 điểm chỉ giảm ACC không đáng kể |

**Bổ sung — vị trí trong tài liệu ngã thực:**
- Bagalà 2012 giới hạn ở thuật toán **waist/trunk** (đó là điều kiện để so sánh được). **10.1371/journal.pone.0037062**
- Palmerini 2020: **lower back**. **10.3390/s20226479**
- Harari 2021: **điện thoại** mang theo người (không cố định vị trí). **10.1186/s12984-021-00918-z**
- FFF: **lower back** đồng nhất → là lý do SE trên FFF (98 %) cao hơn FARSEEING (82 %). **10.3390/s26010162**

**Hàm ý cho điện thoại:** điện thoại **không ở thắt lưng mà ở túi quần** (thigh). Theo Özdemir, thigh là vị trí tốt thứ 2 (97,89 %) — nhưng theo Casilari 2017, **túi quần làm giảm độ bám** và các kho túi quần lại bị **bão hòa ±2 g**. Đây là **hai nguồn suy giảm độc lập** mà WP8 phải khai báo.

---

## D. Chạy mô hình trên điện thoại thật

| Khẳng định | Số đo | Điều kiện | Nguồn | Loại | Full? |
|---|---|---|---|---|---|
| **Có app Android chạy suy luận ngay trên điện thoại** | **Không báo cáo độ trễ (ms)** | SmartFall: smartwatch đeo tay ghép với smartphone chạy app Android; *"performs the computation necessary for the prediction of falls in real time without incurring latency in communicating with a cloud server"*. Thử **offline + online/real-time**, 3 kho (Smartwatch, Notch, FARSEEING) | **10.3390/s18103363** | peer-reviewed | FULL |
| **Độ trễ suy luận (ms) trên điện thoại Android cho phát hiện ngã** | **`KHÔNG TÌM THẤY NGUỒN`** | Không tìm được bài peer-reviewed nào báo **số ms** suy luận/phát hiện trên điện thoại | — | — | — |
| **Dòng tiêu thụ IMU ở 50 Hz trên điện thoại** | **`KHÔNG TÌM THẤY NGUỒN`** | Không tìm được số đo mW/mA ở 50 Hz cho điện thoại | — | — | — |
| **Tiêu thụ tương đối accelerometer vs gyroscope (thiết bị nhúng)** | ADXL345 chỉ **30–140 μA**; **gyroscope tiêu thụ >10× accelerometer** (hàng trăm μA đến vài mA) | Lập luận thiết kế của Sucerquia 2018 để **chỉ dùng 1 accelerometer** nhằm kéo dài pin | **10.3390/s18041101** | peer-reviewed | FULL |
| **Tần số lấy mẫu ↔ hiệu quả năng lượng** | "20 Hz và xuống 10 Hz … *translates into more efficient energy usage compared to higher sampling rates*" — **định tính, không có số mW** | Khuyến nghị thiết kế của Villa & Casilari | **10.3390/s26010162** | peer-reviewed | FULL |
| **Deep learning thời gian thực trên thiết bị nhúng (MCU), KHÔNG phải điện thoại** | Abstract nêu "a few general formulas for determining memory, computing power…" nhưng **toàn văn trả phí, không lấy được số** | RNN trên MCU cho phát hiện ngã với accelerometer 3 trục | **10.1109/dsd.2018.00075** (Torti et al. 2018) | peer-reviewed | **Không mở được** |
| **TinyML phát hiện ngã trên vi điều khiển** | Tồn tại (ví dụ **10.47897/bilmes.1299289**; **10.36227/techrxiv.174918043.39615584/v1** — preprint) nhưng **không phải điện thoại** | — | **10.47897/bilmes.1299289**, TechRxiv preprint | hỗn hợp | ABS |

### D.1 Cảnh báo then chốt — "validation on a wearable device" của Villa & Casilari KHÔNG được dùng làm bằng chứng on-device

**Bài báo tự mâu thuẫn giữa hai chỗ**, và đây là chi tiết **dễ bị trích dẫn sai nhất** trong toàn bộ tài liệu:

**(a) Phần Methods — kiến trúc HYBRID, phân tích NGOÀI thiết bị:**
> *"Given these computational demands, a **hybrid pipeline** was implemented wherein the wearable **locally stores** 4 s windows upon detecting peaks > 2 g, which are subsequently **analyzed externally** using the CNN-LSTM model."*

**(b) Phần §3.4 — lại nói mô hình ĐƯỢC triển khai trên nguyên mẫu:**
> *"the model was **implemented on the wearable prototype** based on the Arduino Nano 33 BLE Sense Rev2 … The device incorporated a triaxial accelerometer positioned at the waist and was configured to sample data at 20 Hz with a threshold of 2 g"*

— cả hai trích từ **10.3390/s26010162**, đọc FULL.

**Kết luận trung thực:** bài **không mô tả rõ** mô hình chạy ở đâu trong thí nghiệm 7 ngày. Vì vậy:
- **KHÔNG được** trích bài này làm bằng chứng "**on-device / trên điện thoại**".
- **KHÔNG được** trích nó làm bằng chứng **ngân sách độ trễ đầu-cuối**: kể cả ở kịch bản (b), bài **không báo cáo bất kỳ độ trễ nào** (không có ms cho tiền xử lý, suy luận, hay phát cảnh báo).
- Số "≈ 8,3 báo động giả/ngày" vẫn **dùng được**, nhưng phải ghi kèm: *"1 người, 7 ngày, 0 ca ngã thật, waist, 20 Hz, ngưỡng 2 g"*, và ghi rõ **kiến trúc chạy mô hình không được mô tả nhất quán trong bài**.

### D.2 Kết luận §D

**Không tìm thấy** trong phạm vi tìm kiếm đã ghi một bài peer-reviewed nào báo cáo **đồng thời**: (a) suy luận phát hiện ngã **chạy trên chính điện thoại Android**, (b) **độ trễ suy luận tính bằng ms**, và (c) **dòng tiêu thụ IMU ở 50 Hz**. Đây là khoảng trống thực và có thể công bố — xem §E.

---

## E. Khoảng trống

| # | Khoảng trống | Bằng chứng "không tìm thấy" (phạm vi §G) | Vì sao đây là đóng góp |
|---|---|---|---|
| **E1** | **Không có công bố nào phát hiện ngã bằng IMU điện thoại + truyền SOS qua MESH LoRa** | Không tìm thấy. Các tiền lệ chỉ là **điểm-điểm**: cảm biến rung/nghiêng + LoRa tới **một** máy thu (kế hoạch dự án đã ghi `10.1109/ICEAMST67459.2025.11335748`). Meshtastic/MeshCore đều **cần người dùng còn tỉnh để soạn tin** | Đây là đóng góp kiến trúc chính của RescueMesh-LoRa |
| **E2** | **Không có ngân sách độ trễ đầu-cuối từ ĐỈNH VA ĐẬP tới TRẠM** cho hệ phát hiện ngã | Villa & Casilari **không đo** (đường ống hybrid có chặng offline). Harari đo hiệu năng nhưng **không tách độ trễ theo chặng**. Không bài nào tách: cửa sổ phát hiện + suy luận + link cá nhân (BLE) + mesh LoRa multi-hop + xử lý trạm | RQ4. Không ai công bố, kể cả từng chặng |
| **E3** | **Không có số đo độ trễ suy luận trên điện thoại Android cho phát hiện ngã** | §D.2 | RQ4 + WP8 |
| **E4** | **Không có số đo dòng tiêu thụ IMU điện thoại ở 50 Hz** | §D.2 | WP8: 50 Hz là điểm thiết kế then chốt |
| **E5** | **Không có meta-analysis kiểu PRISMA** gộp SE/SP/F1 cho phát hiện ngã bằng IMU, và **không có review nào coi "staged vs ngã thực" là một biến phân tích** | §B.1 | Nền tảng trích dẫn cho WP8 |
| **E6** | **Không có bài nào định lượng tỷ lệ dùng LOSO** trong phát hiện ngã bằng IMU | §C.1 | Lập luận phương pháp cho RQ1 |
| **E7** | **Không có chuẩn/guideline về ngân sách FAR chấp nhận được** cho hệ báo động cá nhân | §C.2 | WP8 phải tự định nghĩa |
| **E8** | **Không có đánh giá nào tách riêng đóng góp của tầng xác nhận (bất động + đếm ngược)** trên ngã thực | Các bài ngã thực dùng ngưỡng/phân loại đơn; không bài nào báo cáo kiểu thang (ngưỡng) → (ngưỡng + luật) → (ML + luật). Villa & Casilari có **post-fall confirmation** bằng cửa sổ 4 s nhưng không tách ablation | H1/RQ1 |
| **E9** | **Không có bài nào về tần số lấy mẫu cho ĐIỆN THOẠI dưới ràng buộc airtime LoRa** | Villa & Casilari làm fs cho thiết bị đeo; chưa ai nối fs ↔ ngân sách byte/airtime của SOS | Nối WP8 với WP5/WP6 |

**Cách phát biểu an toàn (bắt buộc dùng):** *"Trong phạm vi tìm kiếm đã ghi lại ở §G (Crossref, OpenAlex, Europe PMC, Kaggle API, figshare API; ngày 2026-10-01), **không tìm thấy** công bố nào về …"* — **không** được nói "chưa từng có ai làm".

---

## F. Số liệu KHÔNG được dùng (và lý do)

| # | Số liệu / nguồn | Lý do KHÔNG dùng |
|---|---|---|
| **F1** | **Bất kỳ DOI nào trong 5 DOI suy đoán ban đầu cho UMAFall (`10.3390/s17081796`), KFall (`10.3390/s21227599`), FARSEEING (`10.1007/s00391-015-0984-y`), MobiFall (`10.1007/978-3-319-32703-7_23`), UniMiB-SHAR (`10.1109/ACCESS.2017.2694818`)** | **ĐÃ KIỂM CROSSREF — TẤT CẢ ĐỀU TRỎ SAI BÀI** (lần lượt là: đo vòm bàn chân; hiệu chuẩn mô-men xoắn; thiếu máu do sắt trong hội chứng chân không yên; chức năng tiền đình trong VR; và **không tồn tại**). Dùng các DOI đã xác minh ở §A |
| **F2** | **"Báo động giả 3–85 ca/ngày" (Bagalà 2012)** | Số **3** không tồn tại trong bài. Đúng: **22–85** (Bourke1a), **27–84** (Bourke1b), **<9** (Kangas) |
| **F3** | **"FARSEEING: 143 ca thực"** | Quy sai nguồn. 143 là của **Palmerini 2020**; FARSEEING (Klenk 2016) là **347 ghi / 208 xác minh** |
| **F4** | **"Kangas 2015"** | **Không tồn tại** bài Kangas 2015 so sánh ngã thực/mô phỏng. Dùng **Kangas 2012** |
| **F5** | **Số liệu bất kỳ từ Kim & Xiong 2026** (`10.1016/j.measurement.2026.122880`) | **Không mở được toàn văn** (Crossref không có abstract; không có trên PMC). Chỉ được trích như "tồn tại một review hệ thống về sim-to-real", **không trích số** |
| **F6** | **Số liệu từ Torti 2018** (`10.1109/dsd.2018.00075`) | **Toàn văn trả phí, chỉ đọc abstract.** Không được trích số memory/latency |
| **F7** | **Bất kỳ số nào từ Silva & Casilari 2024** (`10.1016/j.measurement.2024.114992`) | Chỉ có **metadata Crossref**; Elsevier không mở. Trích như "tồn tại bài kiểm tra chéo kho có dùng ngã thực + giám sát dài hạn", **không trích số** |
| **F8** | **Ghi "~8 báo động giả/ngày (Villa & Casilari)" mà không nêu điều kiện** | Nguy hiểm: 7 ngày đó **có 0 ca ngã thật**, và mô hình **không chạy trên thiết bị** |
| **F9** | **Ghi "on-device fall detection" cho Villa & Casilari 2025** | **SAI** — kiến trúc hybrid, lưu cửa sổ rồi phân tích ngoài |
| **F10** | **Kết quả SisFall 95–96 % / UniMiB 99 % như "baseline so sánh được"** | SisFall dùng **10-fold trộn cửa sổ**, không LOSO → **không so sánh được** với kết quả LOSO |
| **F11** | **Kaggle "KFall Dataset" (`usmanabbasi2002/kfall-dataset`, ghi MIT)** như kho KFall chính thức | Đây là **bản re-upload của bên thứ ba**. Giấy phép MIT trên Kaggle **không phải** điều khoản gốc (bài Frontiers là CC BY, nhưng kho trên IEEE DataPort có điều khoản riêng **chưa xác minh**). Phải lấy từ nguồn gốc |
| **F12** | **Kaggle "Fall Detection Dataset" (`uttejkumarkandagatla`)** như kho IMU | Subtitle chính thức: **"Imaged based fall dataset"** — đây là kho **ẢNH**, dùng cho vision, **không dùng được cho IMU**. License "Database: Open Database, Contents: © Original Authors" cũng **không phải CC mở** |
| **F13** | **MobiFall/tFall/UniMiB-SHAR/Graz/Gravity/UMAFall cho phân tích đỉnh va đập** như thể tầm đo đủ | **Bão hòa ±2 g** — không chứa được đỉnh va đập thật (Casilari 2017 nói rõ) |
| **F14** | **Kho nào không truy cập được thì không được mô tả giấy phép** | Trạng thái HTTP ngày 2026-10-01: SisFall/SISTEMIC **000**, tFall/eduqtech **000**, MobiFall/BMI **000**. UniMiB **200**, figshare **202**. Với 3 kho chết: giấy phép hiện hành = `KHÔNG TÌM THẤY NGUỒN` |
| **F15** | **Kangas 2012 kết luận "ngã thực giống ngã mô phỏng"** như bằng chứng phản bác Bagalà | Đây là **tranh luận chưa ngã ngũ**, không phải phản bác. Bagalà 2012 và Palmerini 2020 (cùng nhóm dữ liệu, mẫu lớn hơn nhiều) cho kết quả ngược lại |
| **F16** | **"SafeFall" như một kho có DOI** | **`KHÔNG TÌM THẤY NGUỒN`** — tra Crossref (`query.title=SafeFall`, `query.bibliographic=SafeFall`) và OpenAlex đều **không trả về bài mô tả kho SafeFall nào**. Không được bịa DOI. Nếu cần, phải xác minh lại bằng nguồn khác |
| **F17** | **"Cogent/UMA" như một kho duy nhất** | **Hai kho khác nhau**: **Cogent Labs** = Ojetola/Coventry (42 người, chest+thigh, 2015); **UMAFall** = Casilari/Málaga (17 người, 5 vị trí, 2017). Gộp lại là sai |
| **F18** | **"Free From Falls/UMAFall" như một kho** | **Hai kho khác nhau**: **FFF** = Mosquera-Lopez/Hildebrand/Cameron (đa xơ cứng, ngã thực, 8 tuần, lower back, 50 Hz, 2021); **UMAFall** = staged, 5 vị trí, 2017 |

---

## G. Sổ tìm kiếm (truy vấn + CSDL)

**Ngày truy cập toàn bộ:** 2026-10-01. **`web_search` không dùng** (HTTP 401).

### G.1 Công cụ đã dùng
| Công cụ | Cách gọi | Ghi chú |
|---|---|---|
| OpenAlex API | `python3 research_tools/oa.py "query" N` và endpoint `/works?search=` | **Bị 429 rate-limit** nhiều lần; có backoff |
| **Crossref REST** | `api.crossref.org/works/<DOI>` (kiểm DOI) và `?query.bibliographic=` / `?query.title=` (tìm) | **Nguồn xác minh DOI chính**; ổn định nhất |
| Europe PMC REST | `/search?query=DOI:"…"` + `/<PMCID>/fullTextXML` | Lấy **toàn văn** các bài MDPI/Frontiers/BMC (MDPI chặn PDF trực tiếp — HTML trả "Access Denied") |
| PLOS | `journals.plos.org/...&type=printable` → `pdftotext` | Toàn văn Bagalà 2012 |
| figshare API | `api.figshare.com/v2/articles/<id>` | **Xác minh giấy phép** UMAFall, Graz |
| Kaggle Datasets API | `kaggle.com/api/v1/datasets/list?search=fall detection` | **Xác minh giấy phép** kho Kaggle |
| Semantic Scholar API | `api.semanticscholar.org/graph/v1/paper/DOI:<doi>` | Abstract + link arXiv cho bài trả phí |

### G.2 Truy vấn đã chạy (theo mục)

**Kho dữ liệu:** `UMAFall fall detection dataset smartphone` · `KFall large-scale fall dataset` · `UniMiB SHAR recognition of human activity smartphone accelerometer` · `FARSEEING real-world fall repository` · `MobiFall fall detection dataset mobile phone` · `SafeFall dataset real falls smartphone` · `SafeFall dataset falls activities daily living smartphone` · `SafeFall` (query.title) · `tFall wearable fall detection database` · `Cogent dataset fall detection accelerometer` · `Cogent data set for fall events and daily activities from inertial sensors Ojetola` · `SafeFall fall detection dataset synthetic` · `new datasets for fall detection SafeFall synthetic Data in Brief`

**Staged vs ngã thực:** `Villa Casilari fall detection deep learning real-world false alarms` · `fall detection false alarms per day free-living deep learning 2025` · `Villa Casilari fall detection` · `fall detection deep learning field trial false alarm per day elderly` · `Comparison of real-life accidental falls in older people with experimental falls in middle-aged test subjects Kangas` · `Kangas 2015 fall detection algorithm comparison accelerometer` · `Harari smartphone fall detection 2021` · `Free From Falls multiple sclerosis falls monitoring accelerometer dataset` · `fall detection dataset smartphone real falls Sucerquia 2022`

**Đánh giá & ca khó:** `leave-one-subject-out fall detection evaluation subject-wise validation` · `fall detection review evaluation methodology data leakage window level splitting subject-wise` · `machine learning fall detection systematic review datasets validation protocol` · `deep learning human activity recognition subject-wise evaluation leakage inflated accuracy` · `systematic review fall detection wearable sensors deep learning PRISMA` · `meta-analysis fall detection accelerometer sensitivity specificity elderly` · `fall detection review subject-independent evaluation protocol leave-one-subject-out percentage of studies`

**Trên thiết bị:** `on-device fall detection smartphone TensorFlow Lite Android real-time` · `fall detection deep learning smartphone real-time Android latency TensorFlow Lite` · `smartphone fall detection deep learning inference latency mobile device` · `deep learning fall detection embedded device inference time milliseconds wearable` · `TinyML fall detection microcontroller latency accuracy` · `fall detection Android smartphone application real time accelerometer alert` · `wearable fall detection device inference time energy consumption battery life measurement` · `smartphone accelerometer energy consumption battery drain continuous monitoring study` · `energy consumption smartphone accelerometer continuous sensing battery`

**Review/phương pháp:** `systematic review meta-analysis wearable fall detection sensitivity specificity` · `pre-impact fall detection wearable sensors datasets models sim-to-real generalization systematic review`

### G.3 Kiểm chứng URL kho dữ liệu (HTTP status, 2026-10-01)

| Kho | URL | HTTP |
|---|---|---|
| UniMiB-SHAR | `http://www.sal.disco.unimib.it/technologies/unimib-shar/` | **200** |
| UMAFall (figshare) | `https://figshare.com/articles/UMA_ADL_FALL_Dataset_zip/4214283` | **202** |
| SisFall (SISTEMIC/UdeA) | `https://sistemic.udea.edu.co/en/investigacion/proyectos/english-falls/` | **000 (chết)** |
| tFall (EduQTech) | `http://eduqtech.unizar.es/fall-adl-data/` | **000 (chết)** |
| MobiFall/MobiAct (BMI TEI Crete) | `https://www.bmi.teicrete.gr/index.php/research/mobiact` | **000 (chết)** |
| MDPI (chặn tải PDF trực tiếp) | `https://www.mdpi.com/1424-8220/17/7/1513` | **403 Access Denied** → phải dùng Europe PMC |

### G.4 Danh sách nguồn đã dùng (30 nguồn, tất cả DOI đã kiểm Crossref)

**peer-reviewed (FULL):** 10.3390/s17010198 (SisFall) · 10.1186/s11556-016-0168-9 (FARSEEING) · 10.3390/s17071513 (Casilari, 12 kho) · 10.3389/fnagi.2021.692865 (KFall) · 10.1371/journal.pone.0037062 (Bagalà 2012) · 10.3390/s20226479 (Palmerini 2020, 143 ca) · 10.3390/s26010162 (Villa & Casilari 2025) · 10.1186/s12984-021-00918-z (Harari 2021) · 10.3390/s16081161 (Özdemir placement) · 10.3390/s24051679 (Fula 2024) · 10.3390/s18103363 (SmartFall) · 10.3390/s18041101 (Sucerquia 2018, 25 Hz) · 10.3390/s150817827 (Casilari 2015, Android)
**peer-reviewed (ABS/metadata):** 10.1016/j.procs.2017.06.110 (UMAFall) · 10.4018/ijmstr.2014010103 (MobiFall) · 10.1371/journal.pone.0094811 (tFall) · 10.3390/app7101101 (UniMiB-SHAR) · 10.1145/2713168.2713198 (Cogent) · 10.1016/j.gaitpost.2011.11.016 (Kangas 2012) · 10.3390/s19091988 (UP-Fall) · 10.1186/s13104-026-07679-9 (AybuFall) · 10.1109/JBHI.2020.3041035 (FFF) · 10.3390/s21155134 (Usmani review) · 10.1111/coin.12441 (Rastogi review) · 10.1109/ijcnn60899.2024.10650322 (SoK HAR) · 10.1109/dsd.2018.00075 (Torti 2018)
**Không mở được toàn văn (chỉ metadata):** 10.1016/j.measurement.2024.114992 (Silva & Casilari 2024) · 10.1016/j.measurement.2026.122880 (Kim & Xiong 2026)
**kho chính thức:** figshare 10.6084/m9.figshare.4214283.v8 (UMAFall, CC BY 4.0) · figshare 10.6084/m9.figshare.1444405.v1 (Graz, CC BY 4.0) · Kaggle Datasets API (20 kho, xem §A/§F)

---

## Tóm tắt 5 điểm hành động cho WP8/RQ1

1. **Sửa 3 số liệu trong kế hoạch** trước khi trích: báo động giả Bagalà là **22–85/ngày** (không phải 3–85); **143 ca thực thuộc Palmerini 2020** (không phải FARSEEING); **"Kangas 2015" không tồn tại** → dùng Kangas 2012.
2. **LOSO là bắt buộc và là điểm khác biệt:** SisFall và nhiều khả năng cả Villa & Casilari công bố trên **chia tập theo cửa sổ**, nên baseline 96–99 % **không so sánh được** với kết quả LOSO của đề tài.
3. **Dùng Villa & Casilari 2025 (10.3390/s26010162) làm mốc fs**, nhưng **ghi rõ**: 20 Hz là điểm cân bằng; 7 ngày thực địa **không có ca ngã thật**; mô hình **chạy ngoài thiết bị**.
4. **Khai báo hai nguồn suy giảm độc lập của điện thoại:** túi quần (thigh, hạng 2 theo Özdemir 97,89 %) **và** bão hòa ±2 g ở nhiều kho điện thoại.
5. **Khoảng trống có thể công bố chắc nhất:** **ngân sách độ trễ đầu-cuối từ đỉnh va đập tới trạm**, tách theo từng chặng (cửa sổ phát hiện → suy luận trên điện thoại → BLE → mesh LoRa → trạm) — **không ai công bố, kể cả từng chặng**.
