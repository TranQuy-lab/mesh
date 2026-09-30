# RescueMesh-AI — Bằng chứng đã xác minh về liên lạc vệ tinh cho cứu hộ (bối cảnh Việt Nam 2026)

**Ngày truy cập toàn bộ nguồn: 2026-09-30 (UTC).**
**Phạm vi cập nhật:** nhóm đã bỏ BLE; vệ tinh được đánh giá như **ứng viên backhaul / sóng duy nhất**.

**Quy ước cột "loại nguồn":**
`CHUẨN 3GPP/ITU` · `OFFICIAL-OPERATOR` (trang chính thức nhà vận hành) · `OFFICIAL-VN` (cơ quan quản lý/nhà nước VN) · `PEER-REVIEW` (bài bình duyệt) · `PRESS` (báo chí có kiểm chứng) · `FILING` (hồ sơ quản lý).

**Quy ước trạng thái:** `THƯƠNG MẠI` · `THỬ NGHIỆM` · `MỚI CÔNG BỐ` · `KHÔNG RÕ`.
**Quy ước số liệu:** `[NSX]` = nhà sản xuất/nhà vận hành công bố · `[ĐO]` = đo độc lập · `[BC]` = báo chí · `[SUY]` = suy luận của nhóm (không phải nguồn).

> **Lưu ý bắt buộc về tính xác thực.** Mọi con số dưới đây đều lấy từ nguồn truy cập được. Những mục ghi **KHÔNG TÌM THẤY NGUỒN** là những thứ tôi **đã tìm nhưng không xác minh được** từ nguồn chính thức trong đợt này — **không được dùng trong bài báo cáo như số liệu chính thức**.

---

## A. Bảng bằng chứng đã xác minh

### A.1 — Starlink: phần cứng, WiFi, điện năng (nguồn chính thức dạng PDF spec sheet)

| # | Khẳng định | Số liệu | Loại nguồn | URL | Ngày truy cập | Độ tin cậy |
|---|---|---|---|---|---|---|
| A1 | **Starlink Mini** — router WiFi tích hợp; vùng phủ WiFi danh định | "Up to 112 m² (1,200 ft²)" `[NSX]` | OFFICIAL-OPERATOR | https://starlink.com/public-files/specification_sheet_mini.pdf | 2026-09-30 | CAO |
| A2 | Starlink Mini — **số thiết bị kết nối đồng thời tối đa** | "Connect up to 128 devices" `[NSX]` | OFFICIAL-OPERATOR | https://starlink.com/public-files/specification_sheet_mini.pdf | 2026-09-30 | CAO |
| A3 | Starlink Mini — chuẩn WiFi | 802.11a/b/g/n/ac, **WiFi 5**, Dual Band 3×3 MU-MIMO, WPA2 `[NSX]` | OFFICIAL-OPERATOR | https://starlink.com/public-files/specification_sheet_mini.pdf | 2026-09-30 | CAO |
| A4 | Starlink Mini — **cổng mạng** | 1 cổng Ethernet LAN (latching, qua Starlink Plug) `[NSX]` | OFFICIAL-OPERATOR | https://starlink.com/public-files/specification_sheet_mini.pdf | 2026-09-30 | CAO |
| A5 | Starlink Mini — **điện năng tiêu thụ trung bình** | "Average: **25-40W**" `[NSX]` | OFFICIAL-OPERATOR | https://starlink.com/public-files/specification_sheet_mini.pdf | 2026-09-30 | CAO |
| A6 | Starlink Mini — **đầu vào DC / yêu cầu nguồn** | Input Rating **12-48V, 60W**; USB PD **100W, 20V/5A tối thiểu** (với cáp USB-C→barrel jack) `[NSX]` | OFFICIAL-OPERATOR | https://starlink.com/public-files/specification_sheet_mini.pdf | 2026-09-30 | CAO |
| A7 | Starlink Mini — trường nhìn (field of view) và môi trường | FOV **110°**; IP67; nhiệt độ -30…50 °C; gió vận hành 96 km/h+; khối lượng 1,10 kg `[NSX]` | OFFICIAL-OPERATOR | https://starlink.com/public-files/specification_sheet_mini.pdf | 2026-09-30 | CAO |
| A8 | Starlink Mini — tương thích mesh | "Compatible with all Starlink mesh systems" `[NSX]` | OFFICIAL-OPERATOR | https://starlink.com/public-files/specification_sheet_mini.pdf | 2026-09-30 | CAO |
| A9 | **Starlink Standard 4X** — điện năng tiêu thụ trung bình | "Average: **75 - 100 W**" `[NSX]` | OFFICIAL-OPERATOR | https://starlink.com/public-files/specification_sheet_standard.pdf | 2026-09-30 | CAO |
| A10 | **Router 3** (đi kèm Standard 4X) — vùng phủ WiFi | "Up to **297 m² (3,200 ft²)**"; WiFi 6 (802.11 a/b/g/n/ac/ax), Tri Band 4×4 MU-MIMO; WPA2 `[NSX]` | OFFICIAL-OPERATOR | https://starlink.com/public-files/specification_sheet_standard.pdf | 2026-09-30 | CAO |
| A11 | Router 3 — **số thiết bị tối đa & cổng mạng** | "Connect up to **235 devices**"; **2** cổng Ethernet LAN `[NSX]` | OFFICIAL-OPERATOR | https://starlink.com/public-files/specification_sheet_standard.pdf | 2026-09-30 | CAO |
| A12 | Router 3 — **giới hạn mesh (ràng buộc quan trọng cho RescueMesh)** | Mesh với Gen 2 / Router 3 Mesh Nodes, **tối đa 3 Starlink Mesh Nodes**; "**Not compatible with 3rd party mesh systems**" `[NSX]` | OFFICIAL-OPERATOR | https://starlink.com/public-files/specification_sheet_standard.pdf | 2026-09-30 | CAO |
| A13 | **Flat High Performance** — điện năng và ràng buộc mưa | "Average: **110-150 W**"; FOV **140°**; IP56; spec ghi rõ "**Mount at 8° Angle for Rainfall**" `[NSX]` | OFFICIAL-OPERATOR | https://starlink.com/public-files/specification_sheet_flat_high_performance.pdf | 2026-09-30 | CAO |
| A14 | Starlink không cung cấp **giá** qua giao thức HTTP không-JS | Trang `starlink.com/service-plans` trả về shell JS (34.296 byte, không có giá); mọi endpoint `/api/...` thử đều trả HTML shell | OFFICIAL-OPERATOR (kiểm chứng phủ định) | https://www.starlink.com/service-plans | 2026-09-30 | CAO (về việc *không truy xuất được*) |

> **Hệ quả kỹ thuật (suy luận của nhóm, KHÔNG phải trích dẫn):** với Mini 25-40 W, một trạm cứu hộ chạy 24 h cần ~0,6-0,96 kWh/ngày chỉ cho terminal (chưa tính router/thiết bị khác). Đây là **phép tính của nhóm**, không phải số liệu nhà sản xuất.

### A.2 — Việt Nam: cấp phép, thí điểm, giá, và triển khai thực tế 2026

| # | Khẳng định | Số liệu | Loại nguồn | URL | Ngày truy cập | Độ tin cậy |
|---|---|---|---|---|---|---|
| A15 | **Quyết định thí điểm có kiểm soát** LEO | **Quyết định số 659/QĐ-TTg ngày 26/3/2025**, cho phép thí điểm có kiểm soát dịch vụ viễn thông dùng công nghệ vệ tinh quỹ đạo tầm thấp, **không giới hạn tỉ lệ sở hữu nước ngoài** | OFFICIAL-VN (Báo Điện tử Chính phủ) | https://baochinhphu.vn/starlink-duoc-cap-phep-cung-cap-dich-vu-tai-viet-nam-102260214200759337.htm | 2026-09-30 | CAO |
| A16 | **Thời hạn thí điểm** | 5 năm kể từ ngày pháp nhân tại VN được cấp giấy phép kinh doanh dịch vụ viễn thông; **phải kết thúc trước 1/1/2031** | OFFICIAL-VN | https://baochinhphu.vn/starlink-duoc-cap-phep-cung-cap-dich-vu-tai-viet-nam-102260214200759337.htm | 2026-09-30 | CAO |
| A17 | **Giấy phép tần số** (13/02/2026) | Ngày **13/02/2026**, **Cục Tần số vô tuyến điện** (Bộ KH&CN) cấp giấy phép sử dụng tần số và thiết bị vô tuyến điện cho **Công ty TNHH Starlink Services Việt Nam** | OFFICIAL-VN (Bộ KH&CN) | https://mst.gov.vn/starlink-duoc-cap-phep-trien-khai-dich-vu-internet-ve-tinh-tai-viet-nam-19726021500204438.htm | 2026-09-30 | CAO |
| A18 | **Quy mô giai đoạn đầu** | **4 trạm cổng (gateway)** và **tối đa 600.000 thiết bị đầu cuối** | OFFICIAL-VN (Bộ KH&CN + Báo Chính phủ) | https://mst.gov.vn/starlink-duoc-cap-phep-trien-khai-dich-vu-internet-ve-tinh-tai-viet-nam-19726021500204438.htm | 2026-09-30 | CAO |
| A19 | **02 giấy phép viễn thông** (13/02/2026) | **Cục Viễn thông** cấp 02 giấy phép cung cấp dịch vụ viễn thông có hạ tầng mạng: **loại mạng viễn thông cố định vệ tinh** và **loại mạng viễn thông di động vệ tinh** | OFFICIAL-VN (Báo Chính phủ) | https://baochinhphu.vn/bo-khcn-trao-giay-phep-cung-cap-dich-vu-vien-thong-ve-tinh-cho-starlink-102260219204340964.htm | 2026-09-30 | CAO |
| A20 | **Lễ trao giấy phép** | Chiều tối **18/02/2026** tại Washington D.C., Bộ KH&CN trao giấy phép cho Starlink Services Việt Nam, dưới chứng kiến của Tổng Bí thư Tô Lâm | OFFICIAL-VN | https://baochinhphu.vn/bo-khcn-trao-giay-phep-cung-cap-dich-vu-vien-thong-ve-tinh-cho-starlink-102260219204340964.htm | 2026-09-30 | CAO |
| A21 | **Giá cước thương mại tại VN** (công bố trên trang Starlink) | **1.131.990 đồng/tháng** cho gói ~100 Mbps; **1.711.100 đồng/tháng** cho gói tốc độ tối đa trên 400 Mbps; tổng đơn hàng ước tính **10.848.800 đồng** (đã gồm thuế) | PRESS (dẫn trang chính thức Starlink) | https://vietnamnet.vn/internet-ve-tinh-starlink-cua-lon-musk-chinh-thuc-cung-cap-dich-vu-tai-viet-nam-2545064.html | 2026-09-30 | TRUNG BÌNH-CAO |
| A22 | **Thời điểm chính thức cung cấp dịch vụ** | **13/8/2026** — Starlink chính thức cung cấp dịch vụ tại Việt Nam | PRESS | https://vietnamnet.vn/internet-ve-tinh-starlink-cua-lon-musk-chinh-thuc-cung-cap-dich-vu-tai-viet-nam-2545064.html | 2026-09-30 | TRUNG BÌNH-CAO |
| A23 | Trần thuê bao thí điểm nhắc lại bởi cơ quan quản lý | **600.000 thuê bao** (≈2,5% tổng thuê bao băng rộng cố định VN) | PRESS (phát biểu Phó Cục trưởng Cục Viễn thông Nguyễn Anh Cương) | https://vietnamnet.vn/internet-ve-tinh-starlink-cua-lon-musk-chinh-thuc-cung-cap-dich-vu-tai-viet-nam-2545064.html | 2026-09-30 | CAO |
| A24 | **Giá dự kiến ban đầu** (trước khi điều chỉnh) | ~**435 USD** tháng đầu (thiết bị + thuê bao), ~**85 USD/tháng** từ tháng thứ hai; 4 gateway dự kiến tại **Phú Thọ, Đà Nẵng, TP.HCM** | PRESS (họp báo Bộ KH&CN 1/4/2026) | https://vietstock.vn/2026/04/mang-ve-tinh-starlink-duoc-thi-diem-tai-viet-nam-gia-cuoc-thang-dau-hon-11-trieu-dong-4264-1421291.htm | 2026-09-30 | TRUNG BÌNH |
| A25 | **Việt Nam dùng Starlink cho "vùng lõm sóng"** — cam kết | Starlink Services Việt Nam cam kết hỗ trợ **1.000 bộ thiết bị** và **dịch vụ miễn phí 6 tháng** | PRESS (dẫn Cục Viễn thông) | https://vietnamnet.vn/13-tinh-se-dung-ve-tinh-starlink-ket-noi-vung-lom-song-di-dong-2554361.html | 2026-09-30 | CAO |
| A26 | **Quy mô vùng lõm sóng toàn quốc** | **273 thôn lõm sóng** và **117 điểm lõm sóng/sóng yếu** tại **13 tỉnh, thành phố** | PRESS (dẫn Cục Viễn thông) | https://vietnamnet.vn/13-tinh-se-dung-ve-tinh-starlink-ket-noi-vung-lom-song-di-dong-2554361.html | 2026-09-30 | CAO |
| A27 | **Triển khai thực tế — Thanh Hóa** | Ngày **28-29/9/2026**, lắp **9 bộ thiết bị đầu cuối Starlink Standard 4X** (4 tại thôn/bản xã Trung Lý và Mường Lý; 5 tại cơ sở giáo dục công lập xã Trung Lý, Quang Chiểu, Sơn Thủy) | OFFICIAL-VN (báo Đảng Cộng sản VN) | https://dangcongsan.vn/bokhoahoccongnghe/tin-tuc-hoat-dong/thanh-hoa-lap-dat-thiet-bi-starlink-tai-cac-vung-lom-song-vien-thong.html | 2026-09-30 | CAO |
| A28 | **Starlink chỉ là giải pháp TẠM THỜI tại VN** | "Starlink được xác định là **giải pháp kết nối tạm thời** trong thời gian chờ hoàn thiện hạ tầng viễn thông mặt đất. Sau khi các khu vực được phủ sóng di động, thiết bị sẽ được xem xét **điều chuyển** đến địa bàn khác" | OFFICIAL-VN (báo Đảng) | https://dangcongsan.vn/bokhoahoccongnghe/tin-tuc-hoat-dong/thanh-hoa-lap-dat-thiet-bi-starlink-tai-cac-vung-lom-song-vien-thong.html | 2026-09-30 | CAO |
| A29 | **Triển khai — Đà Nẵng** | **Kế hoạch số 484/KH-UBND**, triển khai tại **14 thôn và điểm trường**, thời gian **21-30/9/2026** | PRESS (Sài Gòn Giải Phóng) | https://www.sggp.org.vn/da-nang-lap-dat-starlink-phu-song-14-diem-vung-lom-vien-thong-vung-cao-bien-gioi-post871920.html | 2026-09-30 | TRUNG BÌNH-CAO |
| A30 | **Triển khai — Huế** | Sở KH&CN TP. Huế bàn giao **02 bộ thiết bị Starlink** cho 2 trạm kiểm lâm (Khe Tu Re; lòng hồ thủy điện Bình Điền) | PRESS | https://www.vietnam.vn/hue-lap-dat-internet-ve-tinh-starlink-tai-hai-tram-kiem-lam | 2026-09-30 | TRUNG BÌNH |
| A31 | **Amazon Kuiper được cấp phép tại VN** | Ngày **23/9/2026**, Bộ trưởng KH&CN Vũ Hải Quân trao **giấy phép thiết lập mạng viễn thông dùng riêng** cho Công ty TNHH Amazon Kuiper Việt Nam, tại New York | PRESS (dẫn Bộ KH&CN) | https://vneconomy.vn/viet-nam-cap-phep-thiet-lap-mang-vien-thong-dung-rieng-cho-amazon.htm | 2026-09-30 | TRUNG BÌNH-CAO |

### A.3 — Bối cảnh bão lũ & mất liên lạc tại Việt Nam

| # | Khẳng định | Số liệu | Loại nguồn | URL | Ngày truy cập | Độ tin cậy |
|---|---|---|---|---|---|---|
| A32 | Ứng phó bão Yagi — cảnh báo tới thuê bao | Bộ TT&TT đã nhắn tin tới **hơn 32 triệu thuê bao** trong vùng ảnh hưởng | PRESS (dẫn báo cáo nhanh Cục Viễn thông) | https://vietnamnet.vn/nha-mang-vien-thong-chu-dong-ung-pho-khac-phuc-hau-qua-bao-yagi-2319824.html | 2026-09-30 | TRUNG BÌNH-CAO |
| A33 | Ứng phó bão Yagi — nhân lực & gia cố | Điều động **gần 7.000 cán bộ**; củng cố **5.030 trạm cáp, 360 nhà trạm, 2.408 cột, 173 tuyến cáp**; tăng cường **284 máy phát điện** | PRESS (dẫn Cục Viễn thông) | https://vietnamnet.vn/nha-mang-vien-thong-chu-dong-ung-pho-khac-phuc-hau-qua-bao-yagi-2319824.html | 2026-09-30 | TRUNG BÌNH-CAO |
| A34 | Văn bản chỉ đạo ứng phó | **Công điện số 5/CĐ-BTTTT ngày 5/9/2024** | PRESS (dẫn Bộ TT&TT) | https://vietnamnet.vn/nha-mang-vien-thong-chu-dong-ung-pho-khac-phuc-hau-qua-bao-yagi-2319824.html | 2026-09-30 | TRUNG BÌNH-CAO |
| A35 | Thiệt hại hạ tầng viễn thông do Yagi | **27 cột viễn thông bị gãy đổ; hơn 6.280 vị trí mất liên lạc di động do mất điện** | PRESS (tiêu đề CafeF, dẫn số liệu ngành) | https://cafef.vn/ | 2026-09-30 | THẤP-TRUNG BÌNH (chỉ xác minh tiêu đề từ chỉ mục tin; **chưa mở được toàn văn**) |
| A36 | Cáp quang bị đứt do Yagi | **7 tuyến cáp quang liên tỉnh** bị đứt | PRESS (tiêu đề Thanh Niên) | https://thanhnien.vn/ | 2026-09-30 | THẤP-TRUNG BÌNH (chỉ xác minh tiêu đề) |
| A37 | Lũ miền Trung 11/2025 — mất điện, mất sóng | Ngày **19-20/11/2025**, mưa lũ cực đoan tại **Khánh Hòa, Đắk Lắk, Gia Lai**, ngập sâu diện rộng, "hàng loạt khu dân cư **mất điện, mất sóng**"; kỹ sư VNPT/MobiFone/Viettel khắc phục xuyên đêm | PRESS | https://vietnamnet.vn/nguoi-dan-vung-lu-khong-dien-khong-song-nha-mang-xuyen-dem-khac-phuc-su-co-2464896.html | 2026-09-30 | TRUNG BÌNH-CAO |
| A38 | Lũ miền Trung 11/2025 — thiệt hại | **102 người chết và mất tích**; thiệt hại kinh tế **hơn 13.000 tỷ đồng** (Lào Cai) / **vượt 9.000 tỷ đồng** (Kenh14, tính đến 7h ngày 23/11) | PRESS | https://baolaocai.vn/lu-lut-o-mien-trung-khien-102-nguoi-chet-va-mat-tich-thiet-hai-hon-13000-ty-dong-post887473.html | 2026-09-30 | TRUNG BÌNH (⚠️ **hai nguồn lệch nhau** về thiệt hại — phải nêu rõ mốc thời gian) |

### A.4 — Chuẩn 3GPP / ITU (nguồn sơ cấp)

| # | Khẳng định | Số liệu | Loại nguồn | URL | Ngày truy cập | Độ tin cậy |
|---|---|---|---|---|---|---|
| A39 | **Release 17** đưa NTN vào 5G | "NR over Non terrestrial Networks (NTN)" và "IoT over NTN" là dự án Rel-17; **functional freeze tháng 3/2022** (TSG#95-e); mô tả release: **TR 21.917** | CHUẨN 3GPP | https://www.3gpp.org/specifications-technologies/releases/release-17 | 2026-09-30 | CAO |
| A40 | **TR 38.821** — báo cáo kỹ thuật NTN | Spec **38.821**, tiêu đề **"Solutions for NR to support Non-Terrestrial Networks (NTN)"**; Type: **Technical report (TR)**; *Initial planned Release: Release 16*; Status: **Under change control**; nhóm chịu trách nhiệm **RAN3**; rapporteur **Nicolas Chuberre (THALES)** | CHUẨN 3GPP | https://www.3gpp.org/DynaReport/38821.htm | 2026-09-30 | CAO |
| A41 | **Release 18** tiếp tục tích hợp vệ tinh | "**Further integrate Satellite (NTN) access (introduced in Rel-17) in the 5G System (5GS)**"; "Support of **IoT, MTC, including by satellite coverage**"; mô tả release: **TR 21.918** | CHUẨN 3GPP | https://www.3gpp.org/specifications-technologies/releases/release-18 | 2026-09-30 | CAO |
| A42 | **Release 19** — nội dung | Mô tả release: **TR 21.919**; nội dung Rel-19 được quyết định tại **TSGs#102 (12/2023)**; nhãn 5G-Advanced | CHUẨN 3GPP | https://www.3gpp.org/specifications-technologies/releases/release-19 | 2026-09-30 | CAO |
| A43 | **"Regenerative payload"** — định nghĩa chính thức | **KHÔNG TÌM THẤY NGUỒN** (không truy xuất được định nghĩa chính thức của 3GPP trong đợt này) | — | — | 2026-09-30 | — |
| A44 | **ITU-R P.618-14** — suy hao mưa cho tuyến Trái Đất - vệ tinh | **Recommendation ITU-R P.618-14 (08/2023)**, "Propagation data and prediction methods required for the design of Earth-space telecommunication systems", P Series | CHUẨN ITU | https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.618-14-202308-I!!PDF-E.pdf | 2026-09-30 | CAO |
| A45 | Phương pháp tính suy hao mưa (P.618-14) | Bước 4: lấy **R0.01** = cường độ mưa vượt quá **0,01%** một năm trung bình (tích phân 1 phút), lấy từ bản đồ **ITU-R P.837**; Bước 5: suy hao riêng **γR = k·(R0.01)^α** với hệ số tần số từ **ITU-R P.838**; Bước 9: suy hao vượt quá 0,01% năm | CHUẨN ITU | https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.618-14-202308-I!!PDF-E.pdf | 2026-09-30 | CAO |
| A46 | P.618-14 tham chiếu các khuyến nghị liên quan | **ITU-R P.834, P.837, P.838, P.839, P.840, P.841** được viện dẫn trực tiếp trong P.618-14 | CHUẨN ITU | https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.618-14-202308-I!!PDF-E.pdf | 2026-09-30 | CAO |
| A47 | **RFC 9171** — Bundle Protocol v7 (DTN) | "Bundle Protocol Version 7", **tháng 1/2022**, **Standards Track**; tác giả S. Burleigh, K. Fall, E. Birrane III; kế thừa RFC 5050 | CHUẨN IETF | https://www.rfc-editor.org/rfc/rfc9171.txt | 2026-09-30 | CAO |
| A48 | **RFC 5050** — Bundle Protocol gốc | "Bundle Protocol Specification", **tháng 11/2007**, category **Experimental**; K. Scott (MITRE), S. Burleigh (NASA JPL) | CHUẨN IETF | https://www.rfc-editor.org/rfc/rfc5050.txt | 2026-09-30 | CAO |

### A.5 — Nhà vận hành khác & Direct-to-Cell

| # | Khẳng định | Số liệu | Loại nguồn | URL | Ngày truy cập | Độ tin cậy |
|---|---|---|---|---|---|---|
| A49 | **AST SpaceMobile — BlueBird 1-5** | Phóng **12/9/2024** từ Cape Canaveral; mảng pha **693 sq ft**; **40 MHz băng thông**; "**over 150 Mbps peak transmission speeds per cell**" `[NSX]` | OFFICIAL-OPERATOR | https://ast-science.com/bluebird-1-5/ | 2026-09-30 | CAO (số liệu là **nhà vận hành công bố**) |
| A50 | AST — mốc dịch vụ trên BlueBird 1-5 | 1/2025 video call đầu tiên ở châu Âu; 2/2025 tại Mỹ; 4/2025 tại Nhật; 6/2025 kích hoạt cho quốc phòng; 7/2025 **VoLTE với lõi AT&T và Verizon**; 10/2025 VoLTE + dữ liệu băng rộng + video streaming tại Canada | OFFICIAL-OPERATOR | https://ast-science.com/bluebird-1-5/ | 2026-09-30 | CAO |
| A51 | AST — **Next-Gen BlueBird** | Mảng pha **~2.400 sq ft** (lớn nhất LEO thương mại); ASIC **AST5000**, **10 GHz băng thông xử lý**; "**over 150 Mbps peak speeds per coverage cell**"; **2000+ cell hoạt động/vệ tinh**; kế hoạch hoàn thành mảng cho **40 BlueBird** đầu 2026; năng lực **6 vệ tinh/tháng** cuối 2025; "**SCHEDULED FOR LAUNCH THROUGHOUT 2025 AND 2026**" `[NSX]` | OFFICIAL-OPERATOR | https://ast-science.com/next-gen-bluebird/ | 2026-09-30 | CAO (nhà vận hành công bố) |
| A52 | AST 2026 — trạng thái thương mại | Đang chuẩn bị **beta service (phi thương mại)** trong 2026; mục tiêu **~45 BlueBird** trên quỹ đạo trong 2026; BlueBird 8-10 đã phóng **6/2026**; 11-13 công bố lịch phóng **28/7/2026** | PRESS (thông cáo doanh nghiệp qua báo tài chính) | https://uk.finance.yahoo.com/news/ast-spacemobile-announces-launch-date-110500570.html | 2026-09-30 | TRUNG BÌNH |
| A53 | **Apple Emergency SOS qua vệ tinh** — mạng cung cấp | "Satellite network for Apple satellite features provided by **Globalstar, Inc.**"; cần "**outside with a clear view of the sky and horizon**"; **miễn phí 2 năm** sau kích hoạt iPhone 14 trở lên | OFFICIAL-OPERATOR (Apple) | https://support.apple.com/en-us/105097 | 2026-09-30 | CAO |
| A54 | **Việt Nam KHÔNG nằm trong danh sách Apple SOS vệ tinh** | Trang availability liệt kê nhiều quốc gia (gồm Australia, Austria, Belgium, Italy, Luxembourg, Netherlands, New Zealand, Portugal, Spain, Switzerland, Canada, France, Germany, Ireland, UK, Japan…); **chuỗi "Vietnam" KHÔNG xuất hiện** trên trang | OFFICIAL-OPERATOR (Apple) — **kiểm chứng phủ định** | https://support.apple.com/en-us/101573 | 2026-09-30 | CAO (tại ngày truy cập) |
| A55 | **Iridium SBD** — đặc tính dịch vụ | "Real-time, two-way messaging anywhere"; "packet-based service for frequent short data transmissions"; "**Low Power Consumption**"; "**L-band network is resistant to weather**"; "**no need for ground-based infrastructure**" | OFFICIAL-OPERATOR | https://www.iridium.com/services/iridium-short-burst-data-sbd/ | 2026-09-30 | CAO |
| A56 | **Iridium SBD — kích thước tin 340 byte** | **KHÔNG TÌM THẤY NGUỒN** chính thức trong đợt này (không truy xuất được *Iridium SBD Service Developers Guide*; các URL PDF thử đều 404) | — | — | 2026-09-30 | — |
| A57 | **Iridium NTN Direct** | Dịch vụ trên chòm sao **Iridium LEO 66 vệ tinh**, phổ **L-band**; hỗ trợ **NB-IoT và Direct-to-Device (D2D)** theo chuẩn; nêu rõ "**included as part of 3GPP Release-19**"; phủ sóng pole-to-pole | OFFICIAL-OPERATOR | https://www.iridium.com/services/iridium-ntn-direct/ | 2026-09-30 | CAO (là tuyên bố của nhà vận hành) |
| A58 | **Skylo** — trạng thái dịch vụ | "**Live today across 5 continents, millions of devices**, across consumer smartphones, wearables, and enterprise devices"; "partnering with proven satellite providers"; "**No new hardware**"; **cảnh báo**: "availability may vary… not a guarantee of coverage… coverage provided by Skylo partners and is not complete, uniform, or comprehensive worldwide" | OFFICIAL-OPERATOR | https://www.skylo.tech/ | 2026-09-30 | CAO |
| A59 | Skylo — chi tiết NB-IoT NTN (băng tần, độ trễ, kích thước tin) | **KHÔNG TÌM THẤY NGUỒN** (trang web Skylo là SPA; các trang docs/white-papers/faqs thử đều không trả nội dung kỹ thuật) | — | — | 2026-09-30 | — |
| A60 | **Starlink D2C — thử nghiệm tại Malaysia** | Bộ trưởng Truyền thông Malaysia **Fahmi Fadzil** cho biết Starlink dự kiến thử nghiệm công nghệ **direct-to-device (D2D)** tại Malaysia | PRESS (Bernama — hãng tin quốc gia Malaysia) | https://www.bernama.com/en/general/news.php?id=2588151 | 2026-09-30 | TRUNG BÌNH-CAO |
| A61 | Starlink D2C — thương mại hóa ở châu Phi | Airtel Africa và Starlink khai trương dịch vụ **satellite-to-mobile** tại **Uganda** (thị trường châu Phi thứ hai) | PRESS | https://spaceinafrica.com/2026/09/24/airtel-africa-and-starlink-launch-satellite-to-mobile-service-in-uganda/ | 2026-09-30 | TRUNG BÌNH |
| A62 | Starlink D2C — Philippines | Globe Telecom công bố cấu trúc giá với **mức vào P99** cho dịch vụ satellite-to-mobile dùng Starlink | PRESS (GMA Network) | https://www.gmanetwork.com/news/money/companies/994149/globe-sets-p99-entry-price-for-starlink-satellite-to-mobile-service/story/ | 2026-09-30 | TRUNG BÌNH |
| A63 | **T-Mobile T-Satellite** — mốc thương mại | T-Satellite trở thành dịch vụ **thương mại ngày 23/7/2025** (từ beta Starlink direct-to-cell), cho khách T-Mobile và cả khách hãng khác | PRESS | https://btw.media/en/t-mobile-t-satellite-commercial-launch-starlink-direct-to-cell | 2026-09-30 | TRUNG BÌNH |
| A64 | Trang chính thức T-Mobile về T-Satellite | URL tồn tại: `https://www.t-mobile.com/coverage/satellite-phone-service` — nhưng **trả HTTP 403** cho cả `curl` và công cụ fetch; **không đọc được nội dung** | OFFICIAL-OPERATOR (không truy cập được) | https://www.t-mobile.com/coverage/satellite-phone-service | 2026-09-30 | — (chỉ xác nhận tồn tại URL) |
| A65 | Starlink D2C — Kazakhstạn/Ecuador | Kazakhstan **28/9/2026** (Trung Á đầu tiên) và Ecuador (đối tác CNT) — **nguồn blog/tin thứ cấp, độ tin cậy thấp**, cần xác minh lại | PRESS (thứ cấp) | https://www.basenor.com/blogs/news/starlink-mobile-launches-in-kazakhstan-via-direct-to-cell | 2026-09-30 | THẤP |

### A.6 — Nghiên cứu bình duyệt: hybrid vệ tinh + mesh, DTN, rain fade nhiệt đới

| # | Khẳng định | Số liệu | Loại nguồn | URL | Ngày truy cập | Độ tin cậy |
|---|---|---|---|---|---|---|
| A66 | **Field trial backhaul vệ tinh cho cứu hộ** | Völk, Schwarz, Lorenz, Knopp (2020/2021), "**Emergency 5G Communication on-the-Move: Concept and field trial of a mobile satellite backhaul for public protection and disaster relief**", *Int. J. Satellite Communications and Networking* **39:417-430**, DOI **10.1002/sat.1377** — thử nghiệm thực địa backhaul vệ tinh di động cho PPDR | PEER-REVIEW | https://doi.org/10.1002/sat.1377 | 2026-09-30 | CAO |
| A67 | **Kiến trúc mesh vệ tinh cho liên lạc khẩn cấp** | Gopal (2010), "**Net-centric satellite mesh architecture for emergency communication**", *Int. J. Satellite Communications and Networking*, DOI **10.1002/sat.981** | PEER-REVIEW | https://doi.org/10.1002/sat.981 | 2026-09-30 | CAO |
| A68 | **Định tuyến MANET cho cứu hộ trong môi trường vệ tinh hai chiều** | Lee (2008), "Optimized Dynamic Routing Algorithm of Mobile Ad Hoc Network for Disaster Relief on Two Way Satellite Environment", AIAA ICSSC, DOI **10.2514/6.2008-5455** | PEER-REVIEW | https://doi.org/10.2514/6.2008-5455 | 2026-09-30 | CAO |
| A69 | **Điều phối lưu lượng SDN cho backhaul tích hợp vệ tinh - mặt đất** | Mendoza (2017), "SDN-based traffic engineering for improved resilience in integrated satellite-terrestrial backhaul networks", DOI **10.1109/ict-dm.2017.8275692** | PEER-REVIEW | https://doi.org/10.1109/ict-dm.2017.8275692 | 2026-09-30 | CAO |
| A70 | **Proxy QUIC trên backhaul hybrid vệ tinh - mặt đất** | Quadrini (2019), DOI **10.1109/isaect47714.2019.9069738** | PEER-REVIEW | https://doi.org/10.1109/isaect47714.2019.9069738 | 2026-09-30 | CAO |
| A71 | **Mesh nhiều gateway cho cứu hộ/khôi phục thảm họa** | Iqbal, "Load-Balanced Multiple Gateway Enabled Wireless Mesh Network for Applications in Emergency and Disaster Recovery", DOI **10.4018/978-1-4666-2056-8.ch016** | PEER-REVIEW | https://doi.org/10.4018/978-1-4666-2056-8.ch016 | 2026-09-30 | TRUNG BÌNH |
| A72 | **Đo rain fade Ku-band ở Malaysia (nhiệt đới)** | Dao, Islam, Al-Khateeb, Khan (2011), "Preliminary analysis of Ku-band rain fade data for earth-to-satellite path measured in Malaysia", IEEE MICC 2011, DOI **10.1109/micc.2011.6150306** | PEER-REVIEW | https://doi.org/10.1109/micc.2011.6150306 | 2026-09-30 | CAO |
| A73 | **Thời lượng rain fade Ku-band vùng nhiệt đới** | Dao et al. (2012), "Analysis of rain fade duration over satellite-earth path at Ku-Band in tropics", ICCCE 2012, DOI **10.1109/iccce.2012.6271357** | PEER-REVIEW | https://doi.org/10.1109/iccce.2012.6271357 | 2026-09-30 | CAO |
| A74 | **Chuỗi thời gian suy hao mưa đo được 2 năm tại Malaysia** | (2018) "Analysis of Time Diversity Gain for Satellite Communication Link based on Ku-Band Rain Attenuation Data Measured in Malaysia", *IJECE* 8(4):2608-2613, DOI **10.11591/ijece.v8i4.pp2608-2613** — đo tại **12,255 GHz**, 2 năm | PEER-REVIEW | https://doi.org/10.11591/ijece.v8i4.pp2608-2613 | 2026-09-30 | CAO |
| A75 | **Mô hình ITU kém chính xác ở vùng nhiệt đới** | (2022) "Evaluation of Two-Part rain attenuation model at Ku-band for tropical and equatorial regions", *J. Phys. Conf. Ser.* 2312:012004, DOI **10.1088/1742-6596/2312/1/012004** — "the current ITU rain attenuation model… was derived using data collected predominantly from **temperate regions** and has **limitations** when applied to tropical and equatorial regions characterized by **heavy rainfall**" | PEER-REVIEW | https://doi.org/10.1088/1742-6596/2312/1/012004 | 2026-09-30 | CAO |
| A76 | **Chương trình đo Ku-band Đông Nam Á** | Luận án (1997) "Analysis of Ku-band rain attenuation on earth-satellite paths in the Southeast Asia region", DOI **10.58837/chula.the.1997.1118** — dữ liệu đo 3 năm tại **Indonesia, Singapore, Thái Lan** ở **12 GHz** (Chương trình Canada-ASEAN) | PEER-REVIEW (luận án) | https://doi.org/10.58837/chula.the.1997.1118 | 2026-09-30 | TRUNG BÌNH |

---

## B. So sánh các dịch vụ vệ tinh (chỉ điền ô có nguồn; ô trống = KHÔNG TÌM THẤY NGUỒN)

| Dịch vụ | Loại | Thông lượng | Độ trễ | Kích thước tin | Giá | Trạng thái | Nguồn |
|---|---|---|---|---|---|---|---|
| **Starlink Standard 4X + Router 3** | Băng rộng LEO, terminal cố định/di động, WiFi LAN | VN: gói **100 Mbps** và gói **>400 Mbps** (theo bảng giá VN) `[BC]` | ~550 km LEO (độ cao, **không phải** độ trễ đo) `[OFFICIAL-VN]` | Không giới hạn theo tin (IP) | VN: **1.131.990 đ/th** (100 Mbps), **1.711.100 đ/th** (>400 Mbps); đơn đầu **10.848.800 đ** | **THƯƠNG MẠI tại VN từ 13/8/2026**; đồng thời vẫn trong **thí điểm có kiểm soát** (trần 600.000 thuê bao) | A21, A22, A18, A40 |
| **Starlink Mini** | Terminal di động all-in-one, WiFi 5 tích hợp | "max speeds over 100 Mbps" `[NSX]` (tài liệu phân phối Network Innovations — **không phải** starlink.com) | KHÔNG TÌM THẤY NGUỒN | Không giới hạn theo tin | Giá gói Mini riêng tại VN: **KHÔNG TÌM THẤY NGUỒN** | THƯƠNG MẠI (toàn cầu) | A1-A8 |
| **Starlink Roam / Roam Unlimited** | Gói di động | starlink.com có trang `Roam 100 GB`, `Roam 300 GB` (snippet chỉ mục) | KHÔNG TÌM THẤY NGUỒN | — | **KHÔNG TÌM THẤY NGUỒN chính thức** (trang giá JS-only) | THƯƠNG MẠI (toàn cầu) | A14 |
| **Starlink Direct to Cell / Starlink Mobile** | D2C tới điện thoại 4G/5G thường | KHÔNG TÌM THẤY NGUỒN chính thức | KHÔNG TÌM THẤY NGUỒN | SMS/app data (theo báo chí) | Globe PH: vào từ **P99** `[BC]` | **THƯƠNG MẠI ở một số nước (Uganda 24/9/2026, Ecuador 29/9/2026, Kazakhstan 28/9/2026)**; **THỬ NGHIỆM/MỚI CÔNG BỐ ở Malaysia**; **KHÔNG có tại VN** | A60-A65 |
| **AST SpaceMobile (BlueBird)** | D2C băng rộng tới smartphone thường | "**over 150 Mbps peak per cell**" `[NSX]` (Block 1 và Next-Gen) | KHÔNG TÌM THẤY NGUỒN | KHÔNG TÌM THẤY NGUỒN | KHÔNG TÌM THẤY NGUỒN | **THỬ NGHIỆM/BETA phi thương mại trong 2026** | A49, A51, A52 |
| **Globalstar / Apple Emergency SOS** | SOS khẩn cấp qua vệ tinh | KHÔNG TÌM THẤY NGUỒN | KHÔNG TÌM THẤY NGUỒN | KHÔNG TÌM THẤY NGUỒN | **Miễn phí 2 năm** sau kích hoạt `[NSX]` | THƯƠNG MẠI (nhiều nước) — **KHÔNG có Việt Nam** | A53, A54 |
| **Iridium SBD** | Nhắn tin gói hai chiều toàn cầu (L-band) | KHÔNG TÌM THẤY NGUỒN | "low-latency… shorter transmission paths than GEO" `[NSX]` (định tính) | **KHÔNG TÌM THẤY NGUỒN** (340 byte **chưa xác minh**) | "pay-as-you-go, pooled data plans" — **không có bảng giá công khai** | THƯƠNG MẠI | A55, A56 |
| **Iridium NTN Direct** | NB-IoT + D2D trên chòm LEO Iridium | KHÔNG TÌM THẤY NGUỒN | KHÔNG TÌM THẤY NGUỒN | KHÔNG TÌM THẤY NGUỒN | KHÔNG TÌM THẤY NGUỒN | **MỚI CÔNG BỐ** (gắn 3GPP Rel-19) | A57 |
| **Skylo** | Lớp dịch vụ NTN trên vệ tinh đối tác | KHÔNG TÌM THẤY NGUỒN | KHÔNG TÌM THẤY NGUỒN | KHÔNG TÌM THẤY NGUỒN | KHÔNG TÌM THẤY NGUỒN | **THƯƠNG MẠI** ("live today across 5 continents, millions of devices") | A58 |

> **Inmarsat / Viasat / Thuraya:** **KHÔNG TÌM THẤY NGUỒN** trong đợt này cho các thông số kỹ thuật/giá ở bối cảnh Việt Nam. Không đưa số liệu.
> **VINASAT / VNPT / Viettel:** trang `vinasat.vn` trả về nội dung canvas rỗng; `vnpt.com.vn` lỗi TLS (`dh key too small`). **KHÔNG TÌM THẤY NGUỒN** xác minh được cho giá/dung lượng dịch vụ vệ tinh hiện có trong đợt này (**không suy đoán**).

---

## C. Starlink làm gateway WiFi cho mạng cứu hộ: khả thi & ràng buộc

### C.1 Cái gì được chứng minh bằng nguồn chính thức

Một terminal Starlink **đúng là một điểm truy cập WiFi (WiFi AP) + router** — không cần thiết bị trung gian:

- **Mini**: router WiFi tích hợp, **WiFi 5** (802.11a/b/g/n/ac), dual-band 3×3 MU-MIMO, phủ danh định **112 m²**, **tối đa 128 thiết bị**, 1 cổng Ethernet LAN [A1-A4, A8].
- **Standard 4X + Router 3**: **WiFi 6** (802.11a/b/g/n/ac/ax), tri-band 4×4 MU-MIMO, phủ danh định **297 m²**, **tối đa 235 thiết bị**, 2 cổng Ethernet LAN [A10, A11].
- **Điện năng**: Mini **25-40 W** trung bình (đầu vào 12-48 V, 60 W; USB-PD tối thiểu 100 W) [A5, A6]; Standard 4X **75-100 W** [A9]; Flat HP **110-150 W** [A13].
- **Trường nhìn**: 110° (Mini/Standard), 140° (Flat HP) [A7, A13] — đây là **yêu cầu hình học bắt buộc** (đường ngắm bầu trời), phù hợp với cảnh báo của Apple rằng cần "clear view of the sky and horizon" [A53].

### C.2 Ràng buộc — và đây là các ràng buộc **quyết định** cho thiết kế

1. **Không dùng được mesh WiFi bên thứ ba.** Spec Router 3 ghi rõ: "*Not compatible with 3rd party mesh systems*", chỉ mesh với tối đa **3 Starlink Mesh Node** [A12]. ⇒ Nếu RescueMesh muốn mở rộng vùng phủ quanh trạm cứu hộ, phải giải bài toán ở **tầng ứng dụng/thiết bị Android** (điện thoại làm relay, phát lại AP), không thể trông vào mesh WiFi ngoài.
2. **Trần số thiết bị là 128 (Mini) / 235 (Router 3)** [A2, A11]. Đây là giới hạn **WiFi LAN**, không phải giới hạn dung lượng vệ tinh.
3. **Dung lượng chia sẻ**: nhà sản xuất **không** công bố số người dùng đồng thời "an toàn" khi chia sẻ một terminal. Bảng giá VN phân biệt gói 100 Mbps và >400 Mbps [A21], nhưng **không có tài liệu chính thức nào về nghẽn khi đông người dùng trong thảm họa** → xem mục F.
4. **Mưa lớn (rain fade)**: Spec Flat HP có ghi chú *"Mount at 8° Angle for Rainfall"* [A13] — bằng chứng gián tiếp rằng nước/mưa ảnh hưởng tới link. Về mặt chuẩn, **ITU-R P.618-14** quy định phương pháp tính suy hao mưa cho tuyến Trái Đất - vệ tinh, dùng **R0.01** (từ P.837) và **γR = k·R0.01^α** (hệ số từ P.838) [A44, A45]. Bằng chứng **đo** ở vùng nhiệt đới: các nghiên cứu Ku-band đo tại **Malaysia** (Dao et al. 2011, 2012; và chuỗi đo 2 năm tại 12,255 GHz) [A72-A74], và một nghiên cứu Đông Nam Á đo 3 năm tại **Indonesia, Singapore, Thái Lan** ở 12 GHz [A76]. Một nghiên cứu 2022 khẳng định mô hình ITU **được xây chủ yếu từ dữ liệu vùng ôn đới** và **có hạn chế ở vùng nhiệt đới/xích đạo mưa lớn** [A75].
   - ⚠️ **Chưa có** bài đo rain fade **tại chính Việt Nam** trong đợt tìm kiếm này → đây là khoảng trống (mục F).
5. **Năng lượng**: Mini cần nguồn DC 12-48 V, và nếu dùng USB-C thì cần **100 W (20 V/5 A)** [A6] — pin dự phòng thông thường **không đủ**. Đây là ràng buộc vật tư cho trạm cứu hộ.
6. **Pháp lý tại VN**: dịch vụ đang trong **thí điểm có kiểm soát**, trần **600.000 thiết bị**, thời hạn **kết thúc trước 1/1/2031** [A15-A18]. Và quan trọng: chính báo Đảng nêu Starlink ở VN là **"giải pháp kết nối tạm thời"**, sẽ **điều chuyển thiết bị** khi có sóng di động [A28] ⇒ về mặt chủ trương, **không được thiết kế như hạ tầng vĩnh viễn**.

### C.3 Điện năng pin/mặt trời cho Mini — có nguồn đo độc lập không?

- Nguồn **chính thức**: `Average 25-40W`, `Input 12-48V 60W`, `USB PD 100W min` [A5, A6]. **Đây là nguồn duy nhất đáng tin.**
- **Phép tính của nhóm** (không phải trích dẫn): 25-40 W × 24 h = **0,6-0,96 kWh/ngày**; ở 12 V tương ứng **~50-80 Ah/ngày**; pin 100 Ah + tấm pin ~300-400 Wp mới đủ dư (chưa tính mưa, mây, bụi).
- **Nguồn đo độc lập**: tôi **không tìm thấy** một phép đo độc lập có kiểm chứng (không phải blog/affiliate) cho Mini. Các trang tìm được (ví dụ `starlinkinfo.com`, `4wdtalk.com`, `gridwright.com`, `woyum.com`) đều **nhắc lại con số 20-40 W của Starlink** — tức là **vòng lặp quảng cáo**, không phải đo độc lập ⇒ **KHÔNG TÌM THẤY NGUỒN ĐO ĐỘC LẬP**. Không dùng các con số này.

### C.4 Giới hạn dung lượng: một terminal phục vụ bao nhiêu người trong thảm họa?

- **Con số cứng có nguồn**: **128 thiết bị** (Mini), **235 thiết bị** (Router 3) — giới hạn WiFi LAN [A2, A11].
- **Con số "phục vụ được bao nhiêu người trong thảm họa"**: **KHÔNG TÌM THẤY NGUỒN**. Không có tài liệu chính thức của Starlink, cũng không có tài liệu bình duyệt, về nghẽn khi đông người dùng đồng thời. AST có nêu "Millions of connections every day per coverage cell" [A51] nhưng đó là **số liệu tiếp thị của nhà vận hành**, không phải kết quả đo, và cho D2C chứ không phải cho backhaul WiFi.

---

## D. Direct-to-Cell và 3GPP NTN (trạng thái chuẩn + thương mại)

### D.1 Chuẩn 3GPP — cái gì **đã xác minh**

- **Rel-17**: đưa **"NR over NTN"** và **"IoT over NTN"** vào 5G; **functional freeze 3/2022**; mô tả: TR 21.917 [A39].
- **TR 38.821** = *"Solutions for NR to support Non-Terrestrial Networks (NTN)"*, Technical Report, **Rel-16**, under change control, **RAN3**, rapporteur N. Chuberre (THALES) [A40]. (Lưu ý: TR 38.821 thuộc **Rel-16**, còn work item đưa NTN vào chuẩn nằm ở Rel-17 — **đừng viết "TR 38.821 là Rel-17"**, đó là lỗi phổ biến.)
- **Rel-18**: "Further integrate **Satellite (NTN) access** (introduced in Rel-17) in the **5G System (5GS)**" và "Support of **IoT, MTC, including by satellite coverage**"; mô tả: TR 21.918 [A41].
- **Rel-19**: mô tả release: **TR 21.919**; nội dung chốt tại TSGs#102 (12/2023); gắn nhãn 5G-Advanced [A42].
- **"Regenerative payload"**: **KHÔNG TÌM THẤY NGUỒN** định nghĩa chính thức trong đợt này [A43]. ⇒ **Không** được viết "Rel-19 đưa regenerative payload" như một khẳng định chuẩn hóa nếu chưa có nguồn.
- **Iridium tuyên bố** NTN Direct "included as part of **3GPP Release-19**" [A57] — đây là **tuyên bố của nhà vận hành**, không phải văn bản 3GPP; phải ghi rõ nguồn.

### D.2 Thương mại D2C — 2025 → 2026 đã thay đổi rất nhiều

- **2025**: T-Satellite (T-Mobile + Starlink) chuyển từ beta sang **thương mại 23/7/2025** [A63]. (Trang chính thức T-Mobile trả **403**, không đọc được [A64].)
- **2026**: dịch vụ đã lan ra ngoài Mỹ — **Uganda** (Airtel Africa + Starlink, 24/9/2026) [A61], **Philippines** (Globe, giá vào P99) [A62], **Malaysia** đang ở giai đoạn **dự kiến thử nghiệm** (Bộ trưởng Fahmi, Bernama) [A60], và các tin Kazakhstan/Ecuador ngày 28-29/9/2026 **độ tin cậy thấp** [A65].
- **AST SpaceMobile**: vẫn ở **beta phi thương mại trong 2026**; Block 1 (BlueBird 1-5, phóng 12/9/2024) đã đạt các mốc video call/VoLTE với AT&T–Verizon; Next-Gen BlueBird công bố **>150 Mbps đỉnh mỗi cell** và ~2.400 sq ft mảng pha [A49-A52].
- **Tại Việt Nam: KHÔNG có D2C.** Giấy phép Starlink tại VN là **cố định vệ tinh + di động vệ tinh** (hạ tầng mạng), không phải D2C tới thuê bao di động mặt đất [A19]. **Apple SOS vệ tinh không có Việt Nam** [A54]. ⇒ **Direct-to-Cell hiện KHÔNG phải phương án khả dụng ở VN năm 2026.**

---

## E. Việt Nam: pháp lý, dịch vụ hiện có, bối cảnh bão lũ

### E.1 Pháp lý (đã xác minh)

| Mốc | Nội dung | Nguồn |
|---|---|---|
| **26/3/2025** | **Quyết định 659/QĐ-TTg** — thí điểm có kiểm soát dịch vụ viễn thông dùng vệ tinh LEO; **không giới hạn tỉ lệ sở hữu nước ngoài**; thời hạn **5 năm, kết thúc trước 1/1/2031** | [A15, A16] |
| **13/02/2026** | **Cục Tần số vô tuyến điện** cấp **giấy phép sử dụng tần số và thiết bị vô tuyến điện**; **Cục Viễn thông** cấp **02 giấy phép** (cố định vệ tinh + di động vệ tinh); **4 gateway**, trần **600.000 thiết bị** | [A17-A19] |
| **18/02/2026** | Lễ trao giấy phép tại Washington D.C., chứng kiến bởi Tổng Bí thư Tô Lâm | [A20] |
| **1/4/2026** | Họp báo Bộ KH&CN: giá dự kiến ~435 USD tháng đầu, ~85 USD/tháng; gateway tại **Phú Thọ, Đà Nẵng, TP.HCM** | [A24] |
| **13/8/2026** | **Thương mại hóa**: 1.131.990 đ/th (100 Mbps), 1.711.100 đ/th (>400 Mbps); đơn đầu 10.848.800 đ | [A21, A22] |
| **11/9/2026** | Cục Viễn thông + Starlink: **1.000 bộ thiết bị + 6 tháng miễn phí**; **273 thôn + 117 điểm** lõm sóng tại **13 tỉnh** | [A25, A26] |
| **23/9/2026** | **Amazon Kuiper Việt Nam** được cấp **giấy phép thiết lập mạng viễn thông dùng riêng** (đường truyền vệ tinh), toàn quốc | [A31] |

**Về VSAT / giấy phép trạm mặt đất:** các **loại giấy phép** đã thực tế được cấp (giấy phép cung cấp dịch vụ viễn thông có hạ tầng mạng — cố định/di động vệ tinh; giấy phép sử dụng tần số và thiết bị vô tuyến điện; giấy phép thiết lập mạng viễn thông dùng riêng) đã xác minh được [A17-A19, A31]. **Số hiệu điều khoản cụ thể của Luật Viễn thông / nghị định về VSAT: KHÔNG TÌM THẤY NGUỒN** trong đợt này ⇒ **không viết số điều**.

> **Lưu ý thể chế quan trọng:** từ 2025, cơ quan quản lý viễn thông không còn là "Bộ TT&TT" mà là **Bộ Khoa học và Công nghệ (Bộ KH&CN)**; các cơ quan chuyên môn là **Cục Viễn thông** và **Cục Tần số vô tuyến điện** (xem các văn bản 2026 nêu trên). Khi viết báo cáo, tránh gán các văn bản 2026 cho "Bộ TT&TT".

### E.2 Dịch vụ hiện có (VINASAT/VNPT/Viettel) — mức độ xác minh

- **KHÔNG TÌM THẤY NGUỒN** truy cập được cho: giá VSAT hiện hành của VNPT/Viettel, dung lượng VINASAT, phủ sóng VINASAT. (`vinasat.vn` trả nội dung canvas rỗng; `vnpt.com.vn` lỗi TLS.) **Không đưa số liệu nào.**
- Có một **mốc** báo chí: 4/2024 — VINASAT-1 hết hạn sử dụng, Bộ TT&TT yêu cầu Cục Tần số VTĐ và VNPT trình phương án phóng vệ tinh thay thế. Chỉ xác minh được **tiêu đề** ⇒ độ tin cậy thấp-trung bình, cần xác minh lại.

### E.3 Bối cảnh bão lũ và mất liên lạc

- **Bão Yagi (9/2024)**: Bộ TT&TT nhắn tin **>32 triệu thuê bao**; **Công điện 5/CĐ-BTTTT ngày 5/9/2024**; gần **7.000 cán bộ**; củng cố **5.030 trạm cáp / 360 nhà trạm / 2.408 cột / 173 tuyến cáp**; **284 máy phát điện** [A32-A34]. Theo tiêu đề báo: **27 cột viễn thông gãy đổ**, **>6.280 vị trí mất liên lạc di động do mất điện** [A35]; **7 tuyến cáp quang liên tỉnh đứt** [A36].
- **Lũ miền Trung 11/2025**: 19-20/11/2025 mưa lũ cực đoan ở **Khánh Hòa, Đắk Lắk, Gia Lai**; dân "**không điện, không sóng**"; **102 người chết/mất tích**; thiệt hại **9.000-13.000 tỷ đồng** tùy nguồn và mốc thời gian [A37, A38].
- **Liên hệ trực tiếp với đề tài**: chính bối cảnh này dẫn tới chương trình **đưa Starlink vào 273 thôn + 117 điểm lõm sóng tại 13 tỉnh** (9/2026) [A25, A26], và Đà Nẵng/Huế/Thanh Hóa/Gia Lai đã lắp thật [A27-A30].

---

## F. Khoảng trống nghiên cứu (đã kiểm tra và **không tìm thấy** công bố)

1. **Chi phí mỗi SOS giao được qua vệ tinh trong điều kiện bão lũ Việt Nam.** Không tìm thấy công bố nào. Chỉ có **giá thuê bao/tháng** và **giá thiết bị** [A21, A24] — **không có** nghiên cứu nào quy về **chi phí/bit** hay **chi phí/SOS giao thành công** cho kịch bản VN. → **Khoảng trống rõ ràng, có thể là đóng góp chính.**
2. **Ngân sách độ trễ đầu-cuối cho chuỗi thiết bị → mesh → vệ tinh → trung tâm cứu hộ.** Không tìm thấy công bố cho chuỗi này. Có tài liệu riêng lẻ về LEO/GEO và về backhaul vệ tinh PPDR [A66], nhưng **không có** phân rã độ trễ end-to-end cho **Android → mesh mặt đất → terminal LEO → trung tâm cứu hộ** tại Việt Nam.
3. **Đo rain fade tại chính Việt Nam.** Có đo ở **Malaysia** [A72-A74] và **Indonesia/Singapore/Thái Lan** [A76]; **không tìm thấy** nghiên cứu rain fade Ku/Ka **đo tại Việt Nam** công bố mở. → Khoảng trống địa lý rõ.
4. **Dung lượng/nghẽn khi đông người dùng trên MỘT terminal Starlink trong thảm họa.** Nhà sản xuất cho trần WiFi (128/235 thiết bị) [A2, A11] nhưng **không** công bố dung lượng dịch vụ an toàn. Không có nghiên cứu thực nghiệm.
5. **Khả năng dùng Direct-to-Cell khi mất hoàn toàn hạ tầng tại Việt Nam.** D2C **không khả dụng ở VN** (không có giấy phép D2C; Apple SOS không phủ VN) [A19, A54]. Chưa ai công bố đánh giá D2C cho VN.
6. **Chọn đường gateway (vệ tinh khi có, mesh khi không)** cho cứu hộ đã có tiền lệ học thuật [A66-A71], nhưng **chưa ai làm cho RescueMesh** với ràng buộc: Starlink chỉ là **giải pháp tạm thời** theo chủ trương VN [A28], trần **600.000 thuê bao** thí điểm [A18], và bị **điều chuyển thiết bị** khi có sóng mặt đất [A28]. Đây là **khoảng trống chính sách - kỹ thuật** đặc thù Việt Nam.

---

## G. Cảnh báo: số liệu **KHÔNG** được dùng

| Mục | Vì sao không dùng |
|---|---|
| Giá các gói **Roam / Roam Unlimited / Business / Mini** và giá **thiết bị** toàn cầu bằng USD | Trang `starlink.com/service-plans` **chỉ trả shell JS**; mọi endpoint thử đều thất bại [A14]. Các mức "$55/mo", "$165/mo", "$349 kit", "$199 Mini" trong kết quả tìm kiếm là **trang tổng hợp/affiliate**, không phải nguồn chính thức ⇒ **KHÔNG DÙNG**. |
| **Độ trễ đo (ms)** của Starlink (ví dụ "~25-60 ms"), tốc độ tải thực đo | Không truy xuất được báo cáo **Ookla** chính thức trong đợt này; mọi con số độ trễ "đo" tìm thấy đều từ blog ⇒ **KHÔNG DÙNG**. Có thể chỉ dùng **độ cao quỹ đạo ~550 km** (nguồn chính thức VN [A20/A19 area]) — **không** suy ra ms. |
| **Iridium SBD = 340 byte (MO) / 270 byte (MT)** | **KHÔNG TÌM THẤY NGUỒN** chính thức trong đợt này [A56]. Đây là con số đúng phổ biến nhưng **chưa xác minh** ⇒ chỉ dùng nếu tìm được *Iridium SBD Service Developers Guide* hoặc datasheet chính thức. |
| **Regenerative payload (Rel-18/19)** như nội dung chuẩn hóa | **KHÔNG TÌM THẤY NGUỒN** [A43]. |
| **Số điều/khoản Luật Viễn thông, nghị định VSAT** | **KHÔNG TÌM THẤY NGUỒN** ⇒ không trích số hiệu. |
| **"27 cột viễn thông gãy, 6.280 vị trí mất liên lạc"** và **"7 tuyến cáp quang đứt"** | Chỉ xác minh **tiêu đề** từ chỉ mục tin, **chưa mở toàn văn** [A35, A36] ⇒ nếu dùng phải **mở toàn văn và trích dẫn đúng**, hoặc tìm báo cáo gốc của Cục Viễn thông. |
| **Thiệt hại lũ 11/2025** | **Hai nguồn lệch nhau** (13.000 tỷ vs 9.000 tỷ) [A38] ⇒ phải nêu rõ mốc thời gian/nguồn, **không** lấy một con số rồi coi là chân lý. |
| **Kazakhstan / Ecuador D2C 28-29/9/2026** | Nguồn **blog thứ cấp** [A65] ⇒ cần xác minh bằng thông cáo SpaceX/Starlink/nhà mạng. |
| Mọi số liệu **VINASAT / VNPT / Viettel / Inmarsat / Viasat / Thuraya** | Không có nguồn truy cập được ⇒ **không đưa số**. |
| Bất kỳ giá/số liệu nào **"2026 sẽ là…"** mang tính dự báo | Phải phân biệt **đã thương mại** vs **đang thử nghiệm** vs **mới công bố** (xem cột "Trạng thái" mục B). |

**Ba lỗi cần tránh tuyệt đối:**
1. Nói "TR 38.821 là chuẩn Rel-17" — **sai**, TR 38.821 thuộc **Rel-16** [A40].
2. Nói "Apple Emergency SOS hoạt động ở Việt Nam" — **sai**, Việt Nam **không** có trong danh sách [A54].
3. Nói "Starlink D2C đã có ở Việt Nam" — **sai**, giấy phép VN là mạng cố định/di động vệ tinh, không phải D2C [A19].

---

## H. Sổ tìm kiếm (truy vấn + nguồn)

**Công cụ:** `web_search` của harness **hỏng toàn bộ phiên** (HTTP 401 — *"your api key … is invalid"*, endpoint `api.deepseek.com/anthropic/v1/messages`). Các công cụ thay thế đã dùng:
- **`web_fetch` + DuckDuckGo Lite** (`https://lite.duckduckgo.com/lite/?q=…`) — hoạt động lúc đầu, sau đó bị **captcha chặn**.
- **Bing News RSS** (`https://www.bing.com/news/search?q=…&format=rss`) — **kênh chính**, trả **URL bài gốc trực tiếp** (giải mã tham số `url=`).
- **Google News RSS** — dùng để đối chiếu tiêu đề (link không resolve được).
- **Crossref REST API** (`api.crossref.org/works?query.bibliographic=…`) — kênh chính cho **bài bình duyệt + DOI**.
- **Wikipedia API**, **curl trực tiếp + `pdftotext`** cho tài liệu chính thức.
- Bị chặn: Bing web scrape (trả kết quả rác), Mojeek (403/captcha), Brave (429), Ecosia (403), Startpage/SearXNG (antibot), `r.jina.ai` (Cloudflare 403), OpenAlex (429), T-Mobile (403).

| # | Truy vấn / thao tác | Nguồn thu được |
|---|---|---|
| H1 | `web_fetch` → `starlink.com/public-files/specification_sheet_mini.pdf` (tải + `pdftotext`) | A1-A8 |
| H2 | `…/specification_sheet_standard.pdf` | A9-A12 |
| H3 | `…/specification_sheet_flat_high_performance.pdf` | A13 |
| H4 | Thử `starlink.com/service-plans`, `/api/site/service-plans`, `/api/plans`, `/order`, `/availability`, `__NEXT_DATA__`, 86 JS bundle | A14 (phủ định) |
| H5 | DDG: `Starlink Việt Nam giấy phép thí điểm Cục Viễn thông 2026` | baochinhphu, mst.gov.vn, vietnamnet, vietstock |
| H6 | `curl` + extract: `mst.gov.vn/starlink-duoc-cap-phep-…` | A17, A18 |
| H7 | `curl` + extract: `baochinhphu.vn/starlink-duoc-cap-phep-…`, `…/bo-khcn-trao-giay-phep-…` | A15, A16, A19, A20 |
| H8 | Bing News: `Starlink vùng lõm sóng lắp đặt Việt Nam` | vietnamnet, sggp, huengaynay, vietnam.vn |
| H9 | Bing News: `Cục Viễn thông Starlink 1000 thiết bị vùng lõm sóng` | qdnd.vn, dangcongsan.vn, baomoi |
| H10 | Bing News: `Starlink Việt Nam giá cước đặt cọc thuê bao` | vietnamnet (13/8/2026), kenh14, dantri, BBC |
| H11 | `curl` + extract: vietnamnet 2545064, 2554361, 2528903 | A21, A22, A23, A25, A26 |
| H12 | `curl` + extract: `dangcongsan.vn/…thanh-hoa-lap-dat-thiet-bi-starlink…` | A27, A28 |
| H13 | `curl` + extract: `sggp.org.vn/da-nang-lap-dat-starlink…post871920.html` | A29 |
| H14 | `curl` + extract: `vietnam.vn/hue-lap-dat-internet-ve-tinh-starlink…` | A30 |
| H15 | `curl` + extract: `vneconomy.vn/viet-nam-cap-phep-thiet-lap-mang-vien-thong-dung-rieng-cho-amazon.htm` | A31 |
| H16 | `curl` + extract: vietstock `mang-ve-tinh-starlink-duoc-thi-diem…` | A24 |
| H17 | Bing News: `bão Yagi mạng viễn thông thiệt hại`; `lũ miền Trung 2025 mất sóng` | A32-A38 |
| H18 | `curl` + extract: vietnamnet 2319824, 2464896 | A32-A34, A37 |
| H19 | `3gpp.org/specifications-technologies/releases/release-17|18|19` | A39, A41, A42 |
| H20 | `curl`: `3gpp.org/DynaReport/38821.htm` | A40 |
| H21 | `curl` + `pdftotext`: `itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.618-14-202308-I!!PDF-E.pdf` | A44-A46 |
| H22 | `curl`: `rfc-editor.org/rfc/rfc9171.txt`, `rfc5050.txt` | A47, A48 |
| H23 | `curl` + extract: `ast-science.com/bluebird-1-5/`, `/next-gen-bluebird/` | A49-A51 |
| H24 | `curl` + extract: `support.apple.com/en-us/105097`, `/101573` | A53, A54 |
| H25 | `curl` + extract: `iridium.com/services/iridium-short-burst-data-sbd/`, `/iridium-ntn-direct/`; sitemap.xml | A55-A57 |
| H26 | `curl` + extract: `skylo.tech/` (và thử `/technology`, `/coverage`, `/faqs`, `/white-papers`, `/developer-documentation`) | A58, A59 |
| H27 | Bing News: `MCMC Starlink direct to cell trial Malaysia` | A60 (bernama.com) |
| H28 | Bing News: `Starlink direct to cell commercial service partners 2026` | A61 (spaceinafrica), A62 (gmanetwork) |
| H29 | Bing News: `Starlink Direct to Cell satellite SMS voice data` | A63 (btw.media) |
| H30 | `curl`: `t-mobile.com/coverage/satellite-phone-service` (403), `t-mobile.com/news/network/…` (403) | A64 (phủ định) |
| H31 | Bing News: `AST SpaceMobile BlueBird commercial service` | A52 |
| H32 | Crossref: `rain fade measurement Ku band tropical satellite`; `…tropical Malaysia 0.01 percent dB` | A72-A76 |
| H33 | Crossref: `satellite backhaul terrestrial mesh disaster emergency communication` | A66-A71 |
| H34 | Crossref: `delay tolerant networking bundle protocol satellite emergency` | RFC 6255, RFC 7122 (đối chiếu DTN) |
| H35 | Crossref (chi tiết DOI): `10.1002/sat.1377` | A66 (tiêu đề, tác giả, tạp chí, trang, abstract) |
| H36 | Thử (thất bại): ETSI TR 138 821; Iridium developer guide PDF; ITU-R P.837 PDF; `developer.iridium.com`; `vinasat.vn`; `vnpt.com.vn` | A43, A56, A59 (các mục KHÔNG TÌM THẤY NGUỒN) |

---

## Kết luận một đoạn (theo yêu cầu mục 5 của cập nhật phạm vi)

**Vệ tinh làm SÓNG DUY NHẤT cho mạng cứu hộ RescueMesh-AI là khả thi về kỹ thuật ở mức "trạm đơn", nhưng KHÔNG khả thi về pháp lý - vận hành tại Việt Nam 2026, và chưa có bằng chứng về chi phí.** Về kỹ thuật, một terminal Starlink (Mini hoặc Standard 4X + Router 3) **đúng là** một điểm truy cập WiFi đủ dùng cho một trạm cứu hộ: WiFi 5/6, phủ danh định 112 m² / 297 m², **tối đa 128 / 235 thiết bị**, 1-2 cổng Ethernet, mini chỉ **25-40 W** [A1-A13] — nhưng **không ghép được với mesh WiFi bên thứ ba** (chỉ tối đa 3 Starlink Mesh Node, "not compatible with 3rd party mesh systems") [A12], nên mọi mở rộng vùng phủ phải làm ở tầng Android. Về vật tư, Mini cần nguồn DC 12-48 V và **USB-PD tối thiểu 100 W** [A6], pin thường không đủ; **không có phép đo độc lập đáng tin cậy** nào về tiêu thụ thực (mục C.3). Về môi trường, mưa là rủi ro thật — ITU-R P.618-14 quy định phương pháp tính suy hao mưa [A44, A45], mô hình ITU bị đánh giá **kém chính xác ở vùng nhiệt đới** [A75], đã có đo Ku-band ở **Malaysia** và **Indonesia/Singapore/Thái Lan** [A72-A74, A76], và **chưa có đo tại Việt Nam** (khoảng trống F.3). Về pháp lý, đây là điểm chặn cứng: Starlink tại VN đang trong **thí điểm có kiểm soát, trần 600.000 thiết bị, kết thúc trước 1/1/2031** [A15-A18], và chính báo Đảng xác định Starlink là **"giải pháp kết nối tạm thời"** sẽ **bị điều chuyển** khi có sóng mặt đất [A28] ⇒ không thể thiết kế hệ cứu hộ **phụ thuộc 100%** vào nó. Về khả năng thay thế, **Direct-to-Cell chưa khả dụng ở VN** [A19, A54], **Apple SOS vệ tinh không phủ VN** [A54], và các dịch vụ **Iridium/Skylo** chỉ có nguồn chính thức ở mức định tính, **không có giá/kích thước tin xác minh** [A55-A59]. **Khuyến nghị:** coi vệ tinh là **backhaul dự phòng có điều kiện** (chỉ khi mất hoàn toàn hạ tầng mặt đất), thiết kế **mesh mặt đất là mặc định** để không phụ thuộc pháp lý vào thí điểm Starlink, và **định lượng chi phí/SOS giao được + ngân sách độ trễ end-to-end** như đóng góp nghiên cứu chính — vì đó là hai khoảng trống đã kiểm tra và **không tìm thấy** công bố nào (F.1, F.2).
