# Nghiên cứu chuẩn & định dạng dữ liệu liên lạc khẩn cấp cho RescueMesh-LoRa

**Đề tài:** RescueMesh-LoRa — nút cầu LoRa phát khung SOS 36 byte (vị trí, ID, mức độ, thời gian, chữ ký) qua mesh về trạm cứu hộ.
**Câu hỏi:** khung SOS tự chế ánh xạ/tương thích với định dạng nào cơ quan cứu hộ thực tế dùng, và cần thêm trường gì để chuyển tiếp lên hệ thống quốc gia.
**Ngày truy cập toàn bộ nguồn:** 2026-10-01.
**Khung tham chiếu đối chiếu:** `thiet-ke-he-thong-lora-v2.md` §4.2 (SOS, đúng 36 byte) và `rescuemesh/packets.py` (`LAT_RANGE=(-90,90)`, `LON_RANGE=(-180,180)`, `LATLON_MAX=2^24-1`).

> **Quy ước nguồn:** [STD] = tiêu chuẩn chính thức · [REG] = văn bản quy phạm · [RFC] = IETF RFC · [PR] = bài bình duyệt (DOI đã xác minh qua Crossref) · [PP] = preprint · [TR] = báo cáo kỹ thuật · [GOV] = trang chính phủ.
> **Quy ước số liệu:** [ĐO] = đo được từ nguồn · [TÍNH] = suy ra từ công thức/đọc mã · [NGUỒN-CL] = nguồn tự công bố.
> Không có DOI, số hiệu tiêu chuẩn hay URL nào trong tài liệu này được tạo ra; mọi DOI đều đã tra Crossref.

---

## A. Bảng chuẩn/định dạng

| Loại | Cơ quan | Trường tối thiểu | Phù hợp tổng hợp SOS? | Nguồn (ngày truy cập 2026-10-01) |
|---|---|---|---|---|
| **CAP v1.2** (Common Alerting Protocol, XML) | OASIS (chuẩn quốc tế; ITU-T X.1303 = CAP 1.1) | `<alert>`: `identifier`, `sender`, `sent`, `status`, `msgType`, `scope`. `<info>`: `category`, `event`, `urgency`, `severity`, `certainty`. `<area>`: `areaDesc` + ít nhất một trong `polygon`/`circle`/`geocode` | **CÓ — đích ánh xạ chính.** Là định dạng mà trạm/cổng thông tin cảnh báo dùng để nuốt sự kiện | [STD] CAP v1.2 OS: https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html ; ràng buộc minOccurs đọc từ XSD chính thức https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2.xsd |
| **EDXL-DE v2.0** (Distribution Element) | OASIS | Phong bì: `distributionID`, `senderID` (dạng `actor@domain-name`), `dateTimeSent`, `dateTimeExpires`, `distributionStatus`, `distributionKind` | **CÓ — vỏ định tuyến** chứa CAP hoặc payload khác | [STD] https://docs.oasis-open.org/emergency/edxl-de/v2.0/edxl-de-v2.0.html |
| **EDXL-RM v1.0** (Resource Messaging) | OASIS | Là payload của EDXL-DE; họ thông điệp RequestResource/RequisitionResource/CommitResource…; `ContactInformation`, `Resource Information` ở mức R (required) | **MỘT PHẦN** — điều phối nguồn lực, không phải báo tin khẩn cấp cá nhân | [STD] OASIS Standard 22-12-2009: http://docs.oasis-open.org/emergency/edxl-rm/v1.0/EDXL-RM-SPEC-V1.0.html |
| **EDXL-SitRep v1.0** (Situation Reporting) | OASIS | `reportNumber`, `reportVersion`, `forTimePeriod`, `incidentID`, `reportConfidence`, `severity` (REQUIRED) | **MỘT PHẦN** — báo cáo tình hình, không phải SOS điểm | [STD] Committee Specification 02, 06-10-2016: https://docs.oasis-open.org/emergency/edxl-sitrep/v1.0/edxl-sitrep-v1.0.html |
| **IPAWS/WEA** (profile CAP của Mỹ) | FEMA (IPAWS) / FCC | **5 phần tử CAP bắt buộc**: Event Type, Area Affected, Recommended Action, Expiration Time (kèm múi giờ), Sending Agency | **CÓ — kênh phát tới công chúng.** Nút mesh → CAP → IPAWS là đường hợp lệ về mặt định dạng | [REG] 47 CFR §10.420: https://www.govinfo.gov/content/pkg/CFR-2023-title47-vol1/xml/CFR-2023-title47-vol1-part10.xml ; bằng chứng CAP thật có `<code>IPAWSv1.0</code> (mục B) |
| **Cell Broadcast / PWS / ETWS / CMAS / EU-Alert** | 3GPP (+ ATIS cho WEA 3.0) | Trang CBS = 82 octet (≤15 trang ghép); ETWS Primary Notification: Message Identifier (2 octet) + Serial Number (2) + Warning Type (2) | **CÓ nhưng khác vai** — đây là kênh quảng bá mạng→thiết bị, **không** phải kênh nút→trạm. Chỉ dùng làm đích phát sau khi lên quốc gia | [STD] 3GPP TS 23.041 V20.0.0 (2026-06): https://www.3gpp.org/ftp/Specs/archive/23_series/23.041/23041-k00.zip |
| **3GPP MCPTT / MCX** | 3GPP | Dịch vụ khẩn cấp (`emergency alert`, `emergency call`, `imminent peril`); thông tin vị trí: latitude, longitude, altitude, speed, ECGI | **CÓ — dành cho đội cứu hộ chuyên nghiệp** (không phải công chúng) | [STD] TS 23.280 V20.5.0 (2026-09) https://www.3gpp.org/ftp/Specs/archive/23_series/23.280/23280-k50.zip ; TS 24.379 V20.1.0 (2026-09) https://www.3gpp.org/ftp/Specs/archive/24_series/24.379/24379-k10.zip ; TS 24.380 V20.1.0 (2026-09) https://www.3gpp.org/ftp/Specs/archive/24_series/24.380/24380-k10.zip |
| **ETSI EMTEL** | ETSI | **Không phải định dạng dây** — là yêu cầu. Nhấn mạnh: vị trí phải được chuyển tiếp kèm cuộc gọi khẩn cấp; giao diện cuộc gọi dựa trên SIP + dữ liệu bổ sung theo RFC 7852 | **THAM CHIẾU YÊU CẦU** — dùng để biện luận thiết kế, không để mã hoá | [STD] ETSI TS 102 181 V1.3.1 (2020-06): https://www.etsi.org/deliver/etsi_ts/102100_102199/102181/01.03.01_60/ts_102181v010301p.pdf |
| **TETRA SDS** | ETSI | Payload SDS/SDS-TL tới **4096 octet** (bảng mã độ dài TL-SDU); **status number 0 = emergency call**; access priority "emergency priority"; PDU priority 7 trong chế độ suy giảm | **CÓ — vô tuyến chuyên dụng.** Có thể là định dạng lớp vận chuyển nếu trạm dùng TETRA | [STD] ETSI EN 300 392-2 V3.8.1 (2016-08): https://www.etsi.org/deliver/etsi_en/300300_300399/30039202/03.08.01_60/en_30039202v030801p.pdf |
| **P25 (TIA-102)** | TIA | — | **KHÔNG TÌM THẤY NGUỒN** (truy cập mở). tiaonline.org trả 403; các bản P25 trên cisa.gov/dhs.gov trả 403 từ mạng này. Không suy đoán số hiệu clause | — |
| **NIEM** | US DOJ / OGM | **Mô hình dữ liệu** trao đổi liên ngành (không phải một thông điệp cụ thể) | **THAM CHIẾU** — dùng để chuẩn hoá tên trường khi lên hệ thống Mỹ | [GOV] https://it.ojp.gov/initiatives/niem |
| **ICS-213 (General Message)** | FEMA / NIMS | Biểu mẫu "General Message" (v3) trong bộ ICS Forms | **KHÔNG phải định dạng máy** — bản giấy/biểu mẫu; chỉ ánh xạ như lớp trình bày cho người trực | [GOV] https://training.fema.gov/icsresource/icsforms.aspx |
| **CoT / TAK** (Cursor on Target) | US DoD / MITRE / TAK Program | Sự kiện XML CoT: loại, UID, thời gian, `point` (lat/lon/HAE/CE/LE). TAK chia sẻ CoT **không cần server** ("server-less") | **CÓ — chia sẻ tình huống trong đội.** Là đích thay thế/bổ sung cho CAP trong môi trường TAK | [TR] "The Developer's Guide to Cursor on Target" (2005), DOI 10.21236/ada637348 (đã xác minh Crossref) ; [GOV] https://tak.gov/ ; https://raw.githubusercontent.com/deptofdefense/AndroidTacticalAssaultKit-CIV/main/README.md |
| **Bundle Protocol (DTN)** | IETF | Bundles với DTN time, endpoint ID, hop count, convergence layer → lớp lưu-và-chuyển-tiếp | **CÓ — lớp vận chuyển chịu gián đoạn** giữa mesh và trạm | [RFC] RFC 9171 (Standards Track, 01-2022) https://www.rfc-editor.org/rfc/rfc9171.txt ; RFC 5050 (Experimental, 11-2007) https://www.rfc-editor.org/rfc/rfc5050.txt |

**Kết luận A:** mục tiêu ánh xạ đúng là **CAP v1.2** (bọc trong **EDXL-DE** nếu vào hệ thống EDXL), còn **Cell Broadcast/PWS** chỉ là kênh phát cuối, và **CoT/TAK** là đích song song cho đội tác chiến.

---

## B. CAP: trường, kích thước, bản rút gọn cho băng thông thấp

### B.1 Phiên bản hiện hành
- **CAP v1.2**, OASIS Standard, ban hành **01-07-2010**; đây là bản đang lưu hành tại `docs.oasis-open.org/emergency/cap/v1.2/` [STD, truy cập 2026-10-01].
- CAP 1.1 được ITU-T chấp nhận thành **Khuyến nghị X.1303**, trạng thái "In force", bản 09/2007 [STD] https://www.itu.int/rec/T-REC-X.1303/en.
- Trang Uỷ ban OASIS EMTC **không** cho thấy CAP v1.3/v2.0 (chỉ có EDXL-HAVE 2.0, Event Terms List 1.0 Committee Note 02, 10-2021) [STD] https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=emergency. → **CAP v1.2 là bản mới nhất tìm thấy.**

### B.2 Trường bắt buộc (đọc trực tiếp từ XSD chính thức, minOccurs=1)
- `<alert>`: `identifier` (1..1), `sender` (1..1), `sent` (1..1), `status` (1..1), `msgType` (1..1), `scope` (1..1). *(Các trường `source`, `note`, `references`, `incidents`, `addresses`, `restriction`, `code` đều 0..1; `info` là 0..unbounded nhưng với `msgType=Alert` thì spec nói SHOULD có ít nhất một `<info>`.)*
- `<info>`: `category` (1..unbounded), `event` (1..1), `urgency` (1..1), `severity` (1..1), `certainty` (1..1). *(`effective`, `onset`, `expires`, `headline`, `description`, `instruction`, `web`, `contact`, `parameter`, `resource`, `area`, `eventCode` đều 0..)*
- `<area>`: `areaDesc` (1..1); `polygon`/`circle`/`geocode` đều `minOccurs=0` nhưng về ngữ nghĩa phải có ít nhất một để định vị.
- `<resource>` (nếu có): `resourceDesc` (1..1), `mimeType` (1..1).
- Ràng buộc định danh: `identifier` "MUST NOT include spaces, commas or restricted characters (< and &)"; `sender` "Guaranteed by assigner to be unique globally; e.g., may be based on an Internet domain name" [STD, CAP v1.2 §3.2].
- CAP không có trường chữ ký/integrity trong XML; nó tham chiếu **XML-Signature (XMLSIG)** như cơ chế ký ở §3.3.4.1 [STD].

### B.3 Kích thước điển hình
- CAP XML **không đặt giới hạn byte**. Giới hạn nằm ở profile phát:
  - WEA (Mỹ): tối đa **360 ký tự** văn bản; nếu hạ tầng không đủ thì **90 ký tự** [REG, 47 CFR §10.430, bản CFR 2023].
  - `headline` SHOULD ngắn; spec nêu "**160 characters** MAY be a useful target limit" [STD, CAP v1.2 §3.2].
- **Mẫu CAP thật (đo được):** bản tin CAP v1.2 do NWS/NOAA phát, tải ngày 2026-10-01, **6576 byte**, **1** khối `<info>`, `<area>` dùng `areaDesc` + `geocode` (mã SAME, **không** dùng polygon/circle), và có `<code>IPAWSv1.0</code>`:
  https://api.weather.gov/alerts/urn:oid:2.49.0.1.840.0.6df8c047e1cbe829627cc92d595584cc92d7c79f.002.1 (header `Accept: application/cap+xml`) [GOV, truy cập 2026-10-01].
  → 6576 byte là **một quan sát đơn lẻ**, không phải "kích thước điển hình" của mọi CAP.

### B.4 Có bản rút gọn cho băng thông thấp không?
- **"CAP-lite": KHÔNG TÌM THẤY NGUỒN.** Không có tiêu chuẩn OASIS/ITU/ETSI/3GPP nào mang tên "CAP-lite" (tìm trên OASIS, ITU, Crossref, Wikipedia API — chỉ ra kết quả không liên quan như "Miller Lite", "MikroTik"). **Không được viện dẫn "CAP-lite" như một chuẩn.**
- **Các cơ chế CHÍNH THỨC làm gọn CAP (đây là câu trả lời đúng):**
  1. **Mã hoá ASN.1 + Packed Encoding Rules (PER)** — CAP v1.2 §3.5 "Use of ASN.1 to Specify and Encode the CAP Alert Message"; CAP 1.1 Errata 2007 ra đời chính để hỗ trợ ASN.1; spec viện dẫn ITU-T X.680/X.691 (PER). Đây là đường **nhị phân gọn** chính thức duy nhất cho CAP [STD, CAP v1.2 §1.2 và §3.5].
  2. **Profile WEA: chỉ 5 phần tử CAP bắt buộc** (Event Type, Area Affected, Recommended Action, Expiration Time, Sending Agency) [REG, 47 CFR §10.420].
  3. **CBS compression** — nén thông điệp Cell Broadcast theo thuật toán 3GPP TS 23.042, có header/footer nén, chỉ áp dụng cho phần user information [STD, 3GPP TS 23.041 §9.5].
  4. **ATIS-0700041 "WEA 3.0: Device-Based Geo-Fencing"** — mã hoá toạ độ vùng cảnh báo để thiết bị tự geo-fence; đây là cách biểu diễn không gian gọn cho thiết bị [STD, nêu tại 3GPP TS 23.041 tài liệu tham chiếu [47] và §9.3.63].
  5. **ETWS Primary Notification** — cấu trúc cực gọn: Message Identifier (2 octet) + Serial Number (2) + Warning Type (2), phần dummy/coordinates tuỳ chọn [STD, 3GPP TS 23.041 §9.4.3.3.2].

### B.5 CAP XML mức tối thiểu (ví dụ)
Ví dụ dưới đây do **tôi dựng từ XSD chính thức** (đủ mọi trường minOccurs=1), không phải bản tin do cơ quan nào phát — nhãn: **[DỰNG TỪ XSD]**. Bản tin thật để đối chiếu xem §B.3.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
  <identifier>rescuemesh.example.org:2026-10-01:00123:0007</identifier>
  <sender>gateway@rescuemesh.example.org</sender>
  <sent>2026-10-01T04:15:00-00:00</sent>
  <status>Actual</status>
  <msgType>Alert</msgType>
  <scope>Public</scope>
  <info>
    <category>Rescue</category>
    <event>Person in distress - automatic SOS</event>
    <urgency>Immediate</urgency>
    <severity>Severe</severity>
    <certainty>Observed</certainty>
    <area>
      <areaDesc>Node 00000123 last known position</areaDesc>
      <circle>21.02851,105.80482 0.05</circle>
    </area>
  </info>
</alert>
```
Ghi chú: giá trị `category`/`urgency`/`severity`/`certainty` phải lấy từ tập liệt kê của CAP; `circle` = "vĩ độ,kinh độ bán kính_km" theo WGS 84 [STD, CAP v1.2 §3.3.1 WGS 84 Note + `<circle>`].

---

## C. Vị trí và sai số trong báo tin khẩn cấp

### C.1 Cách chuẩn mã hoá vị trí
| Chuẩn | Hệ quy chiếu | Cách mã hoá / độ phân giải | Nguồn |
|---|---|---|---|
| CAP v1.2 | **WGS 84 = EPSG:4326** (2 chiều) | `<circle>` = cặp toạ độ tâm + bán kính **km**; `<polygon>` = danh sách cặp toạ độ; `altitude`/`ceiling` tính bằng **feet trên mực nước biển** theo WGS 84 | [STD] CAP v1.2 §3.3.1 + `<circle>`/`<altitude>` |
| 3GPP TS 23.032 (GAD) | Ellipsoid WGS 84 (a=6378137 m, b=6356752,314 m) | **Coded with an uncertainty of less than 3 metres**: vĩ độ **24 bit** (1 bit dấu + 23 bit độ lớn); kinh độ **24 bit** bù hai trong (−180°, +180°]. Bản "high accuracy": 32 bit, **<5 mm** vĩ độ / **<10 mm** kinh độ. Kèm các hình bất định (uncertainty circle/ellipse/ellipsoid) + **confidence** | [STD] 3GPP TS 23.032 V19.0.0 (2025-09) §6.1, §6.1a, §5.2–5.7 |
| IETF PIDF-LO | `srsName="urn:ogc:def:crs:EPSG::4326"` | Vị trí là **điểm + vùng bất định**: `<gs:Circle>` gồm `<gml:pos>` và `<gs:radius>`; khuyến nghị uncertainty ở **độ tin cậy 95% trở lên** | [RFC] RFC 5491 §4–5 |
| 3GPP LCS | — | Vị trí/velocity mã hoá theo TS 23.032; LCS QoS gồm **accuracy, response time, LCS QoS Class**; location estimate "with uncertainty" | [STD] 3GPP TS 23.271 V19.0.0 (2025-09); TS 22.071 V19.0.0 (2025-10) §4.3 |

### C.2 So với 24 bit/trục của đề tài
- Khung SOS dùng `LAT_RANGE=(-90,90)`, `LON_RANGE=(-180,180)`, `LATLON_MAX=2^24−1` (offset nhị phân, không bù hai) — đọc từ `rescuemesh/packets.py`.
- Độ phân giải lượng tử hoá **[TÍNH]** (suy từ mã nguồn + công thức, **không phải sai số đo GPS**):
  - vĩ độ: 180/2^24 = **1,073e-5° ≈ 1,194 m** (xích đạo)
  - kinh độ: 360/2^24 = **2,146e-5° ≈ 2,389 m** (xích đạo)
- Đối chiếu 3GPP TS 23.032: bước mã hoá 24 bit của 3GPP cho vĩ độ 90/2^23 ≈ 1,07e-5° và kinh độ 360/2^24 ≈ 2,15e-5° → **trùng khớp về bậc độ phân giải**; 3GPP công bố giá trị này "coded with an uncertainty of less than 3 metres" [STD].
- **Hệ quả:** độ phân giải 24 bit/trục của đề tài **đã đủ chuẩn** (nằm dưới 3 m). Vấn đề không phải lượng tử hoá, mà là **khung không mang trường bất định/độ tin cậy** — trong khi CAP (`circle` bán kính), PIDF-LO (`gs:radius`) và TS 23.032 (uncertainty shape + confidence) đều **bắt buộc/khuyến nghị mô tả sai số kèm điểm**.

### C.3 Yêu cầu sai số của cơ quan cứu hộ (có tài liệu nêu)
| Yêu cầu | Con số | Phạm vi áp dụng | Nguồn |
|---|---|---|---|
| Geographic targeting WEA | Phủ **100%** vùng đích, **overshoot ≤ 0,1 dặm (~161 m)** | Nhà mạng di động Mỹ khi phát WEA theo circle/polygon | [REG] 47 CFR §10.450 |
| WEA 3.0 geo-targeting | Chính xác **tốt hơn 0,1 dặm** | ATIS/3GPP WEA 3.0 | [STD/GOV] ATIS https://www.atis.org/standards/wireless-emergency-alerts/ |
| E911 trong nhà | vị trí x/y trong **50 m** cho 40/50/70/**80%** cuộc gọi khẩn cấp theo lộ trình 2/3/5/6 năm | Nhà mạng Mỹ (nationwide) | [STD] 3GPP TS 22.071 V19.0.0 Annex A, tái bản FCC Fourth Report & Order (FCC 15-9) |
| Thời gian có vị trí đầu tiên (TTFF) | **≤ 30 giây** từ lúc người dùng gọi đến khi vị trí sẵn sàng ở trung tâm thông tin vị trí | E911 Mỹ | [STD] 3GPP TS 22.071 V19.0.0 Annex A |
| Nghĩa vụ EU | Nhà mạng **phải cung cấp thông tin vị trí người gọi** cho cơ quan cứu hộ (kèm quy định uỷ quyền được Commission thông qua) | EU/112 | [GOV] https://digital-strategy.ec.europa.eu/en/policies/112 |
| Chuyển tiếp vị trí | Vị trí từ cuộc gọi khẩn cấp **shall be forwarded along with** cuộc gọi tới mọi đại diện cơ quan; dữ liệu bổ sung theo SIP + RFC 7852 | Yêu cầu EMTEL | [STD] ETSI TS 102 181 §7.2.1.1, §5.3.2.6 |
| Dữ liệu bổ sung cuộc gọi khẩn cấp | Chuyển **theo giá trị hoặc theo tham chiếu**; có Data Provider Info, Device Info, Owner/Subscriber Info | IETF | [RFC] RFC 7852 (Standards Track, 07-2016) |

**Kết luận C:** với ~1,2–2,4 m lượng tử hoá, khung 36 byte **vượt xa** các ngưỡng 50 m và 161 m. Nút thắt nằm ở (a) sai số GPS thực tế, (b) **thiếu trường bất định/confidence**, (c) không có cách biểu diễn "vị trí cũ/độ mới" (freshness).

---

## D. Nghiên cứu cầu nối mesh ↔ hệ thống chính thức

### D.1 Có công bố (đã xác minh DOI qua Crossref, 2026-10-01)
| Công trình | Năm | Loại | Liên quan tới cầu nối |
|---|---|---|---|
| Common Alerting Protocol Compliant Emergency Warning And Alert System for Legacy Broadcasting Networks — https://doi.org/10.1109/cogsima49017.2020.9216105 | 2020 | [PR] hội nghị IEEE | **Kiến trúc CAP → mạng phát thanh truyền thống.** Gần nhất với mô hình "cổng CAP" mà đề tài cần |
| Common Alerting Protocol Message Broker for Last-Mile Hazard Warning System in Sri Lanka — https://doi.org/10.2139/ssrn.1568001 | 2010 | [PP] SSRN | **Mẫu message broker CAP** cho chặng cuối |
| Implementing a Common Alerting Protocol for hazard warning in Sri Lanka — https://doi.org/10.5055/jem.2007.0055 | 2007 | [PR] J. Emergency Management | Triển khai CAP thực địa, bài học tích hợp |
| Hazard Warnings in Sri Lanka: Challenges of Internetworking with CAP — https://doi.org/10.2139/ssrn.1566795 | 2010 | [PP] | Thách thức liên mạng hoá CAP |
| Common Alerting Protocol (CAP) for Flash Flood Early Warning Systems: A Global Review of Implementations — https://doi.org/10.20944/preprints202603.1203.v1 | 2026 | [PP] MDPI Preprints | Tổng quan triển khai CAP mới nhất; chỉ xác minh được metadata (preprints.org chặn 403) |
| EDXL-LD and Architectural Tactics towards Information Sharing and Interoperability in Emergency Context — https://doi.org/10.1017/s1049023x17005878 | 2017 | [PR] Prehospital and Disaster Medicine | Kiến trúc chia sẻ dữ liệu EDXL |
| Delay Tolerant Network for Disaster Information Transmission in Challenged Network Environment — https://doi.org/10.1587/transcom.2016cqi0002 | 2017 | [PR] IEICE Trans. Commun. | DTN cho thông tin thảm hoạ |
| Wide-Area Localization System Based on LoRa Mesh — https://doi.org/10.1007/978-3-031-48008-9_4 | 2024 | [PR] SpringerBriefs | Định vị diện rộng bằng LoRa mesh |
| RFID and Localization by Wearable LoRa for Search and Rescue in Mountains — https://doi.org/10.1109/rfid54732.2022.9795986 | 2022 | [PR] IEEE RFID | LoRa đeo cho SAR (7 trích dẫn) |
| Wearable IoT-Based Rescue System Using LoRa Mesh Network and Physiological Monitoring — https://doi.org/10.1109/gcce65946.2025.11274898 | 2025 | [PR] IEEE GCCE | LoRa mesh cho cứu hộ núi |
| Yap: A High-Performance Cursor on Target Message Router — https://doi.org/10.21236/ada610603 | 2014 | [TR] DTIC | Định tuyến thông điệp CoT (cầu nối CoT) |
| The Developer's Guide to Cursor on Target — https://doi.org/10.21236/ada637348 | 2005 | [TR] DTIC | Đặc tả CoT |

### D.2 Đánh giá
- **Có** nghiên cứu về **CAP gateway/broker** (D.1 dòng 1–3) và về **CAP↔mạng phát legacy**.
- **Có** nghiên cứu LoRa mesh + định vị cứu hộ (dòng 8–10) nhưng **không** nối vào CAP/EDXL.
- **Có** nghiên cứu DTN cho thảm hoạ (dòng 7) nhưng **không** ánh xạ sang CAP.
- **KHÔNG TÌM THẤY NGUỒN** cho: cầu nối **DTN-to-CAP**; cầu nối **ATAK/CoT → CAP** có số đo; và đặc biệt là **ánh xạ khung SOS byte-cố-định từ mesh LoRa sang CAP/EDXL** kèm kiến trúc/số đo. Tìm Crossref với các truy vấn ở §H không trả về kết quả nào trùng khớp.

---

## E. Khuyến nghị ánh xạ cho khung 36 byte

### E.1 Bảng ánh xạ từng trường
| Offset | Trường hiện tại | Ánh xạ sang CAP/EDXL | Việc cổng (gateway) phải làm |
|---:|---|---|---|
| 0 | `header` (version, frame_type) | `msgType`/`status`; dùng nội bộ để chọn profile | `msgType=Alert`, `status=Actual`; `frame_type` không đưa vào CAP |
| 1 | bit `fall_auto`/`manual_button` | `event`/`responseType`; đề xuất thêm `parameter` | Sinh `event` ("automatic SOS" vs "manual SOS") |
| 1 | bit `immobility_confirmed` | `certainty` (tăng độ tin cậy) — xem E.2 | Nâng `certainty` lên `Likely`/`Observed` |
| 1 | bit `low_battery` | `parameter` (`rescuemesh.low_battery`) | CAP không có trường pin |
| 1 | bit `has_gps_fix` | Quyết định có/không có `<area>` | Nếu 0 → không sinh `<area>`, ghi `parameter` |
| 1 | bit `is_relay` | `parameter` (`rescuemesh.relayed`) | Không đưa vào CAP như trường chuẩn |
| 2 | `src_id` (4 B, xoay theo ngày) | **`sender`** + thành phần **`identifier`** | **Không dùng trực tiếp:** `src_id` không globally unique. Cổng sinh `sender = gateway@<domain>` và `identifier = <domain>:<ngày>:<src_id>:<seq>` |
| 6 | `seq` | Thành phần `identifier`; chống trùng | Ghép vào `identifier` |
| 8–9 | `hop_count`, `ttl` | **KHÔNG ánh xạ** — định tuyến nội bộ mesh | Loại bỏ khi lên CAP |
| 10–15 | `lat`, `lon` (24 bit/trục) | `<area><circle>` tâm (WGS 84) hoặc `<polygon>` 1 điểm | Đổi sang thập phân; **đã đúng độ phân giải chuẩn** (§C.2) |
| 16 | `battery_pct` | `parameter` | CAP không có trường pin |
| 17 | `severity` (0–255) | **`severity`** (và một phần `urgency`/`certainty`) | Bắt buộc có **bảng ánh xạ** sang tập liệt kê CAP (Extreme/Severe/Moderate/Minor/Unknown) |
| 18–19 | `time_offset_min` (uint16, wrap) | `sent`/`effective` | CAP yêu cầu **DateTime tuyệt đối kèm múi giờ**. Cổng phải đóng dấu thời gian nhận; wrap 16 bit ≈ 45,5 ngày → **mơ hồ**, cần ghi rõ quy ước |
| 20–21 | `impact_g_x100` | `parameter` (`rescuemesh.impact_g`) | Không có trường CAP |
| 22–23 | `immobility_s` | `parameter` | Không có trường CAP |
| 24–25 | `node_temp_c_x10` | `parameter` | Không có trường CAP |
| 26–27 | **dự trữ 2 byte (16 bit)** | **Dùng cho ánh xạ CAP** — xem E.2 | — |
| 28–35 | `tag` (HMAC cắt 64 bit) | **Không có trường CAP** → `parameter` +/hoặc XML Digital Signature tại cổng | CAP viện dẫn XMLSIG; không có trường integrity trong XML CAP |

### E.2 Dùng 16 bit dự trữ (offset 26–27) — đề xuất phân bổ
| Bit | Trường mới | Ánh xạ CAP |
|---|---|---|
| 2 bit | `cap_severity` (Extreme/Severe/Moderate/Minor hoặc Unknown) | `severity` |
| 2 bit | `cap_urgency` (Immediate/Expected/Future/Unknown) | `urgency` |
| 2 bit | `cap_certainty` (Observed/Likely/Possible/Unknown) | `certainty` |
| 4 bit | `incident_class` (Rescue/Safety/Health/Fire/Geo/Met/Transport/Infra/CBRNE/Other) | `category` + `event`; ánh xạ WEA Event Type |
| 3 bit | `pos_accuracy_class` (bucket HDOP/độ bất định: <5 m, <10 m, <50 m, <150 m, >150 m, không rõ) | **bán kính `<circle>`** trong CAP / `gs:radius` trong PIDF-LO / uncertainty trong TS 23.032 |
| 3 bit | dự phòng | — |

### E.3 Thêm/bớt khác
- **Thêm** một định danh mạng/miền (2 byte, hoặc quy ước trong `src_id`) để cổng sinh `sender`/`identifier` globally unique — CAP yêu cầu `sender` "unique globally" và `identifier` không chứa khoảng trắng/ký tự cấm [STD, CAP v1.2 §3.2].
- **Thêm** cờ "vị trí cũ/độ mới" (1–2 bit) để đặt `effective`/`onset` và để cổng biết có nên hạ `certainty` không.
- **Giữ** 24 bit/trục — không cần tăng, vì đã ngang chuẩn 3GPP TS 23.032 và vượt xa ngưỡng 50 m / 161 m.
- **Giữ** `severity` 8 bit như trường nội bộ mesh (dùng cho ưu tiên hàng đợi), nhưng **bổ sung** bảng ánh xạ tường minh sang ba trục CAP.

### E.4 Điều **KHÔNG** nên nhồi vào khung 36 byte
- **Văn bản tự do** (`description`, `instruction`, `headline`, `areaDesc`): WEA cho tới 360 ký tự (dự phòng 90) [REG §10.430]; headline mục tiêu 160 ký tự [STD]. Cổng sinh văn bản, khung chỉ mang mã.
- **URL/nội dung nhúng** (`web`, `resource`, `uri`, `derefUri`): CAP có trường riêng, khung không nên chứa.
- **Nhiều ngôn ngữ** (nhiều `<info>`): xử lý ở cổng.
- **Đỉnh polygon**: CAP `polygon` 0..* và TS 23.032 giới hạn 3–15 điểm [STD TS 23.032 §5.4]; một SOS 36 byte không nên mang đa giác.
- **Chữ ký đầy đủ 64 byte**: khung chỉ có HMAC cắt 64 bit; chữ ký số đầy đủ nên ký ở cổng (XMLSIG).
- **Phong bì EDXL** (`distributionID`, `dateTimeSent`, `dateTimeExpires`, `distributionStatus`, `distributionKind`): do cổng/EDXL-DE sinh [STD].
- **Định danh dạng chuỗi, altitude/vertical uncertainty, DeviceInfo/SubscriberInfo của RFC 7852**: quá tốn kém cho 36 byte.
- **`hop_count`/`ttl`**: giữ nội bộ, **không** lên CAP.

---

## F. Khoảng trống

1. **Chưa ai công bố việc ánh xạ một khung SOS 36 byte (byte-cố-định, mesh LoRa) sang CAP/EDXL.** → **KHÔNG TÌM THẤY NGUỒN**. Gần nhất là CAP message broker (SSRN 2010) và CAP→legacy broadcast (IEEE 2020) — cả hai đều **không** xuất phát từ khung nhị phân cố định của mesh.
2. **Chưa có ngân sách độ trễ từ miền mesh đến cơ quan cứu hộ/PSAP.** → **KHÔNG TÌM THẤY NGUỒN**. Chỉ có các mảnh rời: TTFF ≤ 30 s cho E911 (TS 22.071 Annex A), và overshoot ≤ 0,1 dặm cho geo-targeting WEA (47 CFR §10.450). **Không** được cộng các số này thành "ngân sách mesh→PSAP".
3. **Không có chuẩn CAP cho LPWAN/LoRa** và **không có "CAP-lite"** (§B.4). Đường gọn chính thức là ASN.1/PER + profile 5 phần tử, đều chưa được ai kiểm chứng trên LoRa.
4. **Không có cách chuẩn để mang MAC cắt ngắn trong CAP**: CAP không có trường integrity; XMLSIG quá nặng cho thiết bị. Đề tài phải tự định nghĩa cách mang `tag`.
5. **Không có ánh xạ chuẩn từ một byte `severity` sang bộ ba `urgency × severity × certainty`** của CAP.
6. **P25 không truy cập mở được** từ mạng này (TIA 403; cisa.gov/dhs.gov 403) → không so sánh được với TETRA SDS.
7. **EMTEL đã chỉ ra đúng khoảng trống này ở mức yêu cầu:** "fragmentation of communication standards impacting interoperability when used to exchange information between authorities" khi nói về thiết bị IoT trong tình huống khẩn cấp [STD, ETSI TS 102 181 §5.3.2.4] — nghĩa là bài toán của đề tài **được công nhận là có thật**, nhưng chưa có lời giải chuẩn.

---

## G. Số liệu KHÔNG được dùng

| Không dùng | Vì sao |
|---|---|
| "CAP-lite là một chuẩn" | **KHÔNG TÌM THẤY NGUỒN**. Tên gọi này không tồn tại trong OASIS/ITU/ETSI/3GPP |
| "CAP có kích thước X byte" | CAP XML không đặt giới hạn byte. Chỉ được nói **6576 byte là một mẫu NWS đo được ngày 2026-10-01** (1 khối info, dùng geocode) |
| "36 byte của đề tài ≈ CAP" | Sai về bản chất: 36 byte là khung nhị phân cảm biến; CAP là XML có ngữ nghĩa giàu hơn. Chỉ được nói **ánh xạ qua cổng** |
| "Độ chính xác vị trí của đề tài là 1,19 m / 2,39 m" | Đó là **độ phân giải lượng tử hoá [TÍNH]**, không phải sai số đo. Sai số thực do GPS chi phối |
| "FCC yêu cầu 50 m nên mesh LoRa phải đạt 50 m" | 50 m là quy định E911 cho **nhà mạng di động Mỹ**, không áp cho mesh LoRa. Chỉ dùng làm **mốc tham chiếu** |
| "0,1 dặm là yêu cầu cho SOS của đề tài" | 0,1 dặm là **overshoot geo-targeting WEA** (47 CFR §10.450), không phải sai số vị trí nút |
| "3GPP PWS/ETWS là kênh nút→trạm" | PWS/CBS là kênh **quảng bá mạng→thiết bị**. Dùng sai vai sẽ hỏng kiến trúc |
| Số hiệu clause P25/TIA-102 | Không truy cập được nguồn mở → **không suy đoán** |
| "EDXL-DE v2.0 XSD" tại URL `docs.oasis-open.org/emergency/edxl-de/v2.0/EDXL-DE-v2.0.xsd` | URL này trả về **trang HTML 404**, không phải XSD. Trích **spec HTML** thay thế |
| Trường bắt buộc của EDXL-DE **1.0** áp cho **2.0** | Hai bản khác nhau; số liệu ở §A lấy từ chính spec 2.0 |

---

## H. Sổ tìm kiếm

**Công cụ:** `web_search` của harness vẫn hỏng (HTTP 401) → **không dùng**. Đã dùng: `web_fetch`, `curl`, Crossref REST API, Wikipedia API (chỉ để khám phá), OpenAlex (bị 429 liên tục, không dùng được kết quả nào).

| # | Truy vấn / URL | Kết quả |
|---:|---|---|
| 1 | `docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html` + `CAP-v1.2.xsd` | CAP v1.2 OS + XSD; trường bắt buộc; WGS84; ASN.1 |
| 2 | `itu.int/rec/T-REC-X.1303/en` | X.1303 = CAP 1.1, "In force" |
| 3 | `oasis-open.org/committees/tc_home.php?wg_abbrev=emergency` | Không có CAP v1.3/2.0 |
| 4 | `docs.oasis-open.org/emergency/edxl-de/v2.0/edxl-de-v2.0.html` | EDXL-DE v2.0 envelope; suite EDXL |
| 5 | `docs.oasis-open.org/emergency/edxl-rm/v1.0/EDXL-RM-SPEC-V1.0.html` | EDXL-RM 1.0 (2009) |
| 6 | `docs.oasis-open.org/emergency/edxl-sitrep/v1.0/edxl-sitrep-v1.0.html` | EDXL-SitRep 1.0 CS02 (2016) |
| 7 | 3GPP FTP `23_series/23.041/23041-k00.zip` | TS 23.041 v20.0.0 (2026-06): CBS 82 octet, ETWS/CMAS/WEA, Warning Area Coordinates, nén CBS |
| 8 | 3GPP FTP `23.280/23280-k50`, `24.379/24379-k10`, `24.380/24380-k10` | MCX/MCPTT: emergency alert, location info |
| 9 | 3GPP FTP `23.032/23032-j00` | GAD: 24 bit <3 m; high accuracy 32 bit; uncertainty shapes |
| 10 | 3GPP FTP `22.071/22071-j00`, `23.271/23271-j00` | LCS QoS; Annex A FCC E911 (50 m/80%, TTFF 30 s) |
| 11 | `etsi.org/deliver/.../ts_102181v010301p.pdf` | EMTEL TS 102 181 v1.3.1 (2020-06): IoT, location, RFC 7852 |
| 12 | `etsi.org/deliver/.../en_30039202v030801p.pdf` | TETRA EN 300 392-2 v3.8.1 (2016-08): SDS, status 0 = emergency |
| 13 | `govinfo.gov` CFR-2023 title 47 vol1 part10 | 47 CFR §10.420 / §10.430 / §10.450 |
| 14 | `govinfo.gov` CFR-2023 title 47 vol2 part20 | §20.18 "[Reserved]" trong bản 2023 → **không** dùng làm nguồn E911 |
| 15 | `rfc-editor.org` RFC 7852, 5491, 6442, 9171, 5050 | Dữ liệu bổ sung cuộc gọi; PIDF-LO uncertainty 95%; DTN BPv7 |
| 16 | `atis.org/standards/wireless-emergency-alerts/` | WEA 1.0 90 ký tự, WEA 2.0 360 ký tự, WEA 3.0 <0,1 dặm |
| 17 | `it.ojp.gov/initiatives/niem` | NIEM (DOJ) |
| 18 | `training.fema.gov/icsresource/icsforms.aspx` | ICS Form 213 "General Message (v3)" |
| 19 | `tak.gov/` + ATAK-CIV README (raw.githubusercontent) | TAK; CoT chia sẻ server-less |
| 20 | `digital-strategy.ec.europa.eu/en/policies/112` | EU: nhà mạng phải cung cấp vị trí người gọi |
| 21 | `api.weather.gov/alerts/...` (`Accept: application/cap+xml`) | CAP v1.2 thật, 6576 byte, `<code>IPAWSv1.0</code>` |
| 22 | Crossref `query.bibliographic`: "Common Alerting Protocol gateway emergency", "delay tolerant network disaster alerting", "LoRa emergency rescue localization mesh", "Cursor on Target interoperability ATAK", "low bandwidth public warning LPWAN alert", "gateway CAP sensor network integration", "mesh network to public warning system gateway", "LoRa CAP disaster alerting", "DTN emergency warning dissemination gateway", "offline smartphone mesh PSAP", "mapping compact SOS frame to CAP", "byte-level emergency frame translation CAP EDXL", "LoRa SOS gateway CAP", "latency budget mesh to PSAP", "UAV gateway cell broadcast warning sensor" | 12 DOI dùng được (đã xác minh); **không** có kết quả nào về ánh xạ khung SOS byte-cố-định → CAP/EDXL, và **không** có ngân sách độ trễ mesh→PSAP |
| 23 | Wikipedia API `srsearch=CAP-lite` | Không có chủ đề "CAP-lite" → **KHÔNG TÌM THẤY NGUỒN** |
| 24 | `tiaonline.org`, `cisa.gov/...p25...`, `dhs.gov/...p25` | 403 → P25 **KHÔNG TÌM THẤY NGUỒN** truy cập mở |
| 25 | `preprints.org/manuscript/202603.1203/v1` | 403 → chỉ xác minh metadata qua Crossref |

### Tổng hợp kiểm đếm nguồn chính thức
- **Tiêu chuẩn chính thức:** CAP v1.2 (+XSD), ITU-T X.1303, EDXL-DE v2.0, EDXL-RM v1.0, EDXL-SitRep v1.0, 3GPP TS 23.041/23.280/24.379/24.380/23.032/22.071/23.271, ETSI TS 102 181, ETSI EN 300 392-2, ATIS-0700041 → **15+.**
- **Văn bản quy phạm:** 47 CFR Part 10 → **1** (Part 20 loại bỏ, §20.18 Reserved).
- **RFC:** 7852, 5491, 6442, 9171, 5050 → **5**.
- **Bài bình duyệt (DOI xác minh):** 8. **Preprint:** 2. **Báo cáo kỹ thuật/DOI:** 2. **Trang GOV:** 5.
