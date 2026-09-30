# Tổng hợp bằng chứng đã xác minh — mesh MỘT SÓNG (LoRa) cho RescueMesh-AI

**Ngày truy cập toàn bộ:** 2026-09-30 · **Phạm vi:** đã bỏ BLE và đa sóng; trọng tâm là mesh LoRa thuần + DTN + SOS tự động do cảm biến.
**Giới hạn công cụ của phiên:** `web_search` hỏng (HTTP 401) → dùng `curl` + Crossref/OpenAlex/arXiv/Semantic Scholar/Europe PMC/GitHub API và `web_fetch` cho DuckDuckGo HTML. Nhiều trang MDPI/ACM/IEEE bị chặn (403/429) nên một số số liệu lấy qua bản PDF kho mở hoặc abstract API.

**Quy ước cột "cách kiểm":**
- `TỰ` = tôi trực tiếp `curl`/`web_fetch` trong phiên này.
- `TỰ+VER` = tôi trực tiếp kiểm **và** có một tác nhân kiểm chứng độc lập mở lại URL/DOI (hai đường độc lập).
- `VER` = chỉ tác nhân kiểm chứng độc lập mở lại nguồn (tôi chưa tự mở).

---

## A. Bảng bằng chứng đã xác minh — định tuyến mesh MỘT SÓNG (LoRa)

| # | Khẳng định | Số liệu | Loại nguồn | URL / DOI | Ngày | Cách kiểm |
|---|---|---|---|---|---|---|
| A1 | Bor et al., "Do LoRa Low-Power Wide-Area Networks Scale?" — MSWiM 2016, tr. 59–67 | DOI hợp lệ; 4 tác giả | bài báo bình duyệt | `10.1145/2988287.2989163` | 2026-09-30 | TỰ+VER |
| A2 | **Bản đã sửa lỗi** của A1: LoRaWAN mặc định (SF12/BW125/CR4-5) chỉ chịu được **64 nút/3,8 ha** với DER>0,9; tối ưu airtime (SN4) lên **>1.100 nút** | 64 nút/3,8 ha; >1100 nút; 20 B/gói mỗi 16,7 phút; tầm mô hình ~100 m | bài báo bình duyệt (bản repository) | https://eprints.lancs.ac.uk/81674/13/lora_scalability_r338.pdf | 2026-09-30 | VER |
| A3 | Capture effect đo được: ở N=200, DER tăng **0,51 → 0,64**; máy thu cần **≥5 symbol preamble** nguyên vẹn | 0,51→0,64; ≥5 symbol; DER(ALOHA)=e^(−2N·T·λ) | bài báo bình duyệt | như A2 | 2026-09-30 | VER |
| A4 | Haxhibeqiri et al., "LoRa Scalability: A Simulation Model Based on Interference Measurements" — mô hình dựng **từ đo nhiễu thực** (2 node IMST iM880A + gateway) | 1.000 nút/gateway → mất tới **32 %** gói; ALOHA thuần ~**90 %** mất | bài báo bình duyệt | `10.3390/s17061193` · https://biblio.ugent.be/publication/8531813/file/8531814.pdf | 2026-09-30 | VER |
| A5 | ETSI EN 300 220-2 V3.2.1 (2018-06): giới hạn duty cycle theo băng | 868,0–868,6 MHz ≤**1 %**; 868,7–869,2 MHz ≤**0,1 %**; 869,4–869,65 MHz ≤**10 %**; FHSS dwell <10 ms → 0,1 % | tiêu chuẩn | https://www.etsi.org/deliver/etsi_en/300200_300299/30022002/03.02.01_60/en_30022002v030201p.pdf | 2026-09-30 | VER |
| A6 | FCC 47 CFR 15.247(a)(1)(i): giới hạn chiếm dụng tần số 902–928 MHz | **0,4 s / 20 s** (BW 20 dB <250 kHz, ≥50 kênh); **0,4 s / 10 s** (≥250 kHz, ≥25 kênh) | quy định | https://www.govinfo.gov/content/pkg/CFR-2024-title47-vol1/xml/CFR-2024-title47-vol1-sec15-247.xml | 2026-09-30 | VER |
| A7 | Hidden node trong LoRa khi dùng Listen-Before-Talk: "Hidden Node Probability in LoRa With Listen-Before-Talk", IEEE WCL 13(10):2917–2921 | HNP theo vành/SF; Nakagami-m + path loss; vùng thường **>10 km**; LBT **không đáng tin khi có nút ẩn** | bài báo bình duyệt | `10.1109/LWC.2024.3453788` | 2026-09-30 | VER |
| A8 | Nhiều base station thắng anten định hướng khi có nhiễu liên mạng | 600 nút bị 4 mạng×600 nút nhiễu: 3 BS nâng DER **0,24 → 0,56** (anten định hướng chỉ 0,32) | preprint | arXiv:1611.00688 · https://arxiv.org/pdf/1611.00688 | 2026-09-30 | VER |
| A9 | **Meshtastic** dùng managed flooding; tham số chính thức | **Max Hops ≤7, mặc định 3**; EU_433/EU_868 "hourly duty cycle limitation of **10 %**, rolling 1-hour"; có "Override Duty Cycle Limit" | tài liệu dự án | https://meshtastic.org/docs/configuration/radio/lora/ | 2026-09-30 | TỰ |
| A10 | **Meshtastic** có tham số điều khiển overhead: "Node Info Broadcast Seconds" (chu kỳ quảng bá NodeInfo), và role CLIENT "rebroadcasts packets when no other node has done so" | tham số tồn tại; **giá trị mặc định: KHÔNG lấy được** trong phiên này | tài liệu dự án | https://meshtastic.org/docs/configuration/radio/device/ | 2026-09-30 | TỰ |
| A11 | **MeshCore** là thư viện C++ định tuyến gói **multi-hop** trên LoRa; node "Companion" **không** chuyển tiếp; số hop cấu hình được | giấy phép **MIT** (xác nhận trên trang GitHub) | tài liệu dự án + repo | https://raw.githubusercontent.com/ripplebiz/MeshCore/main/README.md · https://github.com/ripplebiz/MeshCore | 2026-09-30 | TỰ |
| A12 | **LoRaWAN Relay Specification TS011-1.0.0** (LoRa Alliance, ©2022) tồn tại: cơ chế relay chuyển tiếp frame hai chiều giữa end-device và Gateway/Network Server | 60 trang; Relay/D2D Task Force; **không phải mesh** | tài liệu chính thức (chuẩn công nghiệp) | https://resources.lora-alliance.org/technical-specifications/ts011-1-0-0-relay | 2026-09-30 | TỰ |
| A13 | LoRaWAN là **star-of-stars**, mesh "không dùng gateway" là hướng riêng: Berto et al., Sensors 21(13):4314 | P2P giữa các node không cần gateway | bài báo bình duyệt | `10.3390/s21134314` | 2026-09-30 | TỰ (abstract) |
| A14 | Mai & Kim: multi-hop LoRa **collision-free** bằng cây + gán timeslot/kênh cho từng link | định tuyến theo cây tới sink, tránh va chạm với node lân cận | bài báo bình duyệt | `10.3390/en13061368` | 2026-09-30 | TỰ (abstract) |
| A15 | **LoRaOpp**: multi-hop cơ hội giữa các cặp node và tới gateway **kể cả khi không có đường end-to-end**; có "experimental results in real conditions and in emulation" | điều kiện thực + emulation | bài báo bình duyệt | `10.1109/WIMOB55322.2022.9941716` | 2026-09-30 | TỰ (abstract) |
| A16 | Kiến trúc **hybrid LoRaWAN + LoRa mesh** chuyển tự động; ghi rõ **LoRa mesh tốn pin hơn LoRaWAN** | backup mesh khi vật cản động (tán lá) | bài báo bình duyệt | `10.1109/ICCCN61486.2024.10637558` | 2026-09-30 | TỰ (abstract) |
| A17 | Pham & Ehsan: CAD (Channel Activity Detection) + capture effect trong mạng LoRa dày; đề xuất né va chạm **không cần CCA tin cậy** | "preliminary tests show promising capabilities in increasing the PDR" | bài báo bình duyệt | `10.3390/s21030825` | 2026-09-30 | TỰ (abstract) |

**Kết luận mục A:** tồn tại **đo lường bình duyệt về PDR/DER theo số nút** cho LoRa/LoRaWAN (A2–A4, A17) và **so sánh định tuyến** (A14–A16), nhưng **không tìm thấy** bài bình duyệt nào đo PDR / số lần phát / độ trễ theo **số hop trong mesh LoRa một kênh, một SF** — mọi thí nghiệm quy mô đều dựa vào **trực giao SF của LoRaWAN**, thứ không tồn tại trong mesh một sóng.

---

## B. DTN / store-carry-forward trên LoRa (cơ chế + kết quả thực địa)

| # | Khẳng định | Số liệu | Loại nguồn | URL / DOI | Ngày | Cách kiểm |
|---|---|---|---|---|---|---|
| B1 | **RFC 9171 (BPv7)**, Standards Track, 01/2022 (Burleigh, Fall, Birrane): BP là lớp phủ store-carry-forward; nêu rõ "Ability to use physical motility for the movement of data" | chuẩn | RFC | https://www.rfc-editor.org/rfc/rfc9171.txt | 2026-09-30 | TỰ+VER |
| B2 | **RFC 5050 (BPv6)** là **Experimental**, 11/2007; **RFC 4838** "Delay-Tolerant Networking Architecture", 04/2007 (Cerf et al.) | chuẩn | RFC | https://www.rfc-editor.org/rfc/rfc5050.txt · https://www.rfc-editor.org/rfc/rfc4838.txt | 2026-09-30 | TỰ |
| B3 | ⚠️ **RFC 9177 KHÔNG phải Contact Graph Routing** — đó là "CoAP Block-Wise Transfer Options". CGR **không** có RFC riêng; nằm trong CCSDS + tài liệu nghiên cứu | RFC 9177 = CoAP, 03/2022 | RFC | https://www.rfc-editor.org/rfc/rfc9177.txt | 2026-09-30 | TỰ |
| B4 | Bổ trợ BPv7: **RFC 9172** BPSec, **RFC 9174** TCPCLv4 (01/2022), **RFC 6693** PRoPHET (2012) | chuẩn | RFC | rfc-editor.org/rfc/rfc9172 · rfc9174 · rfc6693 | 2026-09-30 | TỰ |
| B5 | CGR là chủ đề nghiên cứu thực: Segui 2011; Bezirgiannidis 2014; Hylton 2023 (multigraph thay CGR) | DOI hợp lệ | bài báo bình duyệt | `10.1109/GLOCOM.2011.6134460` · `10.1109/ASMS-SPSC.2014.6934518` · `10.1109/ICCCN58024.2023.10230117` | 2026-09-30 | TỰ (Crossref) |
| B6 | **Höchst et al. 2023** — thực địa chuỗi **3 nút DTN** trên LoRa (rf95modem 868 MHz, SF7/500 kHz/CR4-5), n1 đặt giữa để n0–n2 **không** có liên lạc trực tiếp; xác minh chuyển tiếp bằng trường "previous node" | **RTT 1,7 s**; long-range (SF12) giải mã tới **−140 dBm** (medium −130 dBm); xuyên **600 m** rừng; phần mở rộng 1.000 người dùng là **mô phỏng**, tải cao delivery **≤50 %** | bài báo bình duyệt | `10.1007/978-3-031-20939-0_12` · https://peasec.de/paper/2023/2023_HoechstBaumgaertnerKuntkePenningSterzSommerFreisleben_MobileD2DCommunication_DMaIT.pdf | 2026-09-30 | VER |
| B7 | **Theissen et al., Sensors 26(8):2369 (2026)** — **data mule thực địa**: Jeep gắn modem LoRa thu dữ liệu trạm nhiên liệu trong mỏ kali (K+S, Werra, Đức; EU H2020 NEXGEN SIMS grant 101003591) | tốc độ **20–40 km/h**; chuyển tiếp thành công **180–770 m** dù cua 90° và NLoS; **link-up 3 s / ~100 m**; tour 3.500 m; mất gói mục tiêu **<5 %** | bài báo bình duyệt | `10.3390/s26082369` · https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13120548/fullTextXML | 2026-09-30 | VER |
| B8 | **BPoL — Bundle Protocol over LoRa** (GHTC 2023): overlay BP (RFC 9171) trên LoRa D2D, hỗ trợ broadcast/multicast, tôn trọng duty-cycle; đánh giá bằng **emulator LoRaEmu**, kịch bản Darmstadt 17 nút (2 xe + 4 người đi bộ + 3 cụm tĩnh), 1 h, bundle mỗi 2 phút | quadrant **40–60 %** vs random **20–30 %**; ở kịch bản so sánh Meshtasticator (20 nút) quadrant đạt **~80 % median** với "trail time" | bài báo bình duyệt | `10.1109/GHTC56179.2023.10354717` · https://peasec.de/paper/2023/2023_SchmidtKuntkeBauerBaumgaertner_BPOL_GHTC.pdf | 2026-09-30 | VER |
| B9 | **Florita et al., Computer Communications 154:410–432 (2020)** — gateway LoRa **di động cơ hội**, 3 chế độ (Independent / Pure Pass Through / Instruction-based); đánh giá bằng **triển khai campus nhỏ + mô phỏng sự kiện rời rạc** | hệ pull-based gửi được **% điểm dữ liệu cao hơn** baseline push-based | bài báo bình duyệt | `10.1016/j.comcom.2020.02.066` | 2026-09-30 | VER |
| B10 | **Msaad et al. 2020** — LoRa + DTN "at sea", gateway di động trên tàu: **chỉ là đề xuất**, không có PDR/độ trễ thực địa trong phần truy xuất được | — | bài báo bình duyệt | `10.1145/3426746.3434053` | 2026-09-30 | VER |
| B11 | **Anabi et al., Information 16(11):984 (2025)** — LoRa mesh khẩn cấp dưới mỏ: WPT far-field **35 m** là **thực nghiệm**; các chỉ số thông lượng là **mô phỏng 2.000 lần chạy** | **49 % vs 22 %** delivery ratio (10 nút/hop), 2,2×; giảm **64 %** va chạm | bài báo bình duyệt | `10.3390/info16110984` | 2026-09-30 | VER |
| B12 | **Saraereh et al., Sensors 20(8):2396 (2020)** — UAV làm relay cho nút LoRa mặt đất trong cứu hộ: kết quả PRR/độ trễ **là mô phỏng** | — | bài báo bình duyệt | `10.3390/s20082396` | 2026-09-30 | VER |
| B13 | **AERPAW AADM Challenge (arXiv:2602.16163, 02/2026)** — dataset UAV "data mule" hai giai đoạn (digital twin + outdoor testbed), **có đo link-quality từ máy thu LoRa** | 10 trang, 12 hình | preprint | https://arxiv.org/abs/2602.16163 | 2026-09-30 | VER |
| B14 | Cộng đồng DTN đã có tích hợp LoRa: **d3tn** (µD3TN) mô tả LoRa CLA và store-and-forward; DTN7 có LoRa CLA | "reliance on consistent backhaul connectivity limits its reliability in disrupted scenarios" | tài liệu dự án (vendor) | https://d3tn.com/blog/posts/2024-12-19-lora-dtn/ | 2026-09-30 | VER |
| B15 | Triển khai BPv7 hiện đại có CGR/SABR: **Unibo-BP** (Caini & Persampieri) | C++, tuân thủ RFC 9171; LTP + TCPCLv3; CGR/SABR | bài báo bình duyệt | `10.1109/JRFID.2024.3358012` | 2026-09-30 | TỰ (abstract) |
| B16 | So sánh hiệu năng **giữa các implementation BP**: Pöttner et al., CHANTS 2011; ION: Burleigh 2007 | DOI hợp lệ | bài báo bình duyệt | `10.1145/2030652.2030670` · `10.1109/CCNC.2007.51` | 2026-09-30 | TỰ (Crossref) |
| B17 | So sánh định tuyến DTN có đo lường (nền tham chiếu): Abdelkader et al., IEEE Network 2016 | DOI hợp lệ (chi tiết toàn văn chưa mở) | bài báo bình duyệt | `10.1109/MNET.2016.7437024` | 2026-09-30 | TỰ (Crossref) |

**Kết luận mục B:** cơ chế DTN/BP trên LoRa **đã được công bố** (B8, B14) và có **thực địa với nút di động** trong công nghiệp (B7) cùng **chuỗi relay 3 nút** (B6). **KHÔNG TÌM THẤY** thí nghiệm thực địa công bố về DTN-over-LoRa với nút di động **trong bối cảnh cứu hộ/sau thảm họa** có đầy đủ PDR–độ trễ–thời gian contact.

---

## C. Airtime / overhead điều khiển / duty cycle / hidden terminal / công bằng

| # | Khẳng định | Số liệu | Loại nguồn | URL | Ngày | Cách kiểm |
|---|---|---|---|---|---|---|
| C1 | Giới hạn duty cycle theo băng (EU) | xem A5 | tiêu chuẩn | ETSI EN 300 220-2 V3.2.1 | 2026-09-30 | VER |
| C2 | Giới hạn dwell time (US) | xem A6 | quy định | 47 CFR 15.247 | 2026-09-30 | VER |
| C3 | Meshtastic: EU_433/EU_868 dùng hạn mức **10 %/giờ** (rolling), không phải 1 % | 10 % | tài liệu dự án | https://meshtastic.org/docs/configuration/radio/lora/ | 2026-09-30 | TỰ |
| C4 | Có tham số overhead điều khiển tường minh: `Node Info Broadcast Seconds` (chu kỳ NodeInfo) | tham số tồn tại; **giá trị mặc định chưa xác minh** | tài liệu dự án | https://meshtastic.org/docs/configuration/radio/device/ | 2026-09-30 | TỰ |
| C5 | Hidden terminal là vấn đề nghiên cứu riêng; LBT **không** giải quyết được khi có nút ẩn | HNP theo SF/vành; >10 km | bài báo bình duyệt | `10.1109/LWC.2024.3453788` | 2026-09-30 | VER |
| C6 | Capture effect làm DER thực cao hơn mô hình ALOHA thuần | 0,51→0,64 ở N=200 | bài báo bình duyệt | https://eprints.lancs.ac.uk/81674/13/lora_scalability_r338.pdf | 2026-09-30 | VER |
| C7 | Đo nhiễu thực → mô hình; mất gói tới 32 % ở 1.000 nút/GW | 32 % vs ALOHA ~90 % | bài báo bình duyệt | `10.3390/s17061193` | 2026-09-30 | VER |
| C8 | Simulator công bố có mô hình collision + capture effect: **LoRaSim** (SimPy, mcbor/lorasim), **FLoRa** (OMNeT++/INET, bản 1.3.1 ngày 2026-09-16), **ns-3 LoRaWAN** (GPL-2.0) | 4 script LoRaSim, tới 24 BS; FLoRa mô tả ở NOMS 2018 | tài liệu chính thức | https://www.lancaster.ac.uk/scc/sites/lora/lorasim.html · https://flora.aalto.fi/ · https://apps.nsnam.org/app/lorawan/ · `10.1109/NOMS.2018.8406255` | 2026-09-30 | VER |
| C9 | **Hiệu chuẩn mô phỏng ↔ đo thực cho LoRa**: LoRaWANSim đối chiếu 5 board thật + 1 gateway ở 50 m | SF7: mô phỏng **0,997** / thực nghiệm **0,968** / giải tích 0,991; SF10: **0,978 / 0,914 / 0,959**; 10.000 vòng lặp | bài báo bình duyệt | `10.3390/s21030695` | 2026-09-30 | VER |

**KHÔNG TÌM THẤY** (đã tra Crossref bằng nhiều cụm từ, không có kết quả phù hợp):
- Công thức time-on-air **từ URL semtech.com còn sống**: `AN1200.13`/`LoraDesignGuide_STD.pdf` đã bị chuyển hướng ("Document Has Moved"); trang chính thức còn lại là https://www.semtech.com/design-support/development-support-documents (không có link PDF trực tiếp). → **Không được trích số airtime từ trí nhớ.**
- **Bất kỳ nghiên cứu bình duyệt nào về công bằng (fairness) giữa các nút trong mesh LoRa một kênh** (đã thử "fairness LoRa network channel access duty cycle" — chỉ ra bài duty-cycle WSN/LAA, không liên quan).
- **Số % overhead beacon/control đo được** cho mesh LoRa một kênh.

---

## D. Phương pháp luận: cạm bẫy mô phỏng mạng & hiệu chuẩn

| # | Khẳng định | Loại nguồn | DOI / URL | Ngày | Cách kiểm |
|---|---|---|---|---|---|
| D1 | Floyd & Paxson, "Difficulties in simulating the Internet", IEEE/ACM ToN 19(2), 2001 — bài nền về **cạm bẫy mô phỏng mạng** | bài báo bình duyệt | `10.1109/90.944338` | 2026-09-30 | TỰ |
| D2 | Paxson, "Why we don't know how to simulate the Internet", ACM WSC 1997 | bài báo bình duyệt | `10.1145/268437.268737` | 2026-09-30 | TỰ |
| D3 | Noubir, "Reproducibility in wireless experimentation: need, challenges, and approaches", ACM WiNTECH 2016 | bài báo bình duyệt | `10.1145/2980159.2984738` | 2026-09-30 | TỰ |
| D4 | Pullwitt et al., "Pitfalls in Measuring Ultra Low Power Energy Harvesting Wireless Sensor Networks", WONS 2023 — cạm bẫy **đo** năng lượng | bài báo bình duyệt | `10.23919/WONS57325.2023.10062282` | 2026-09-30 | TỰ |
| D5 | Tiền lệ **hiệu chuẩn** mô phỏng LoRa bằng đo thực (5 node, 50 m, 10.000 vòng lặp) — mẫu để viết mục "calibration" của đề tài | bài báo bình duyệt | `10.3390/s21030695` | 2026-09-30 | VER |
| D6 | Tiền lệ **kiểm soát âm/tái lập**: BPoL chạy **10 lần** kịch bản; Anabi 2025 chạy **2.000 trial độc lập**; LoRaWANSim **10.000 vòng** — đây là các mốc số seed/lần lặp có thật trong tài liệu | bài báo bình duyệt | `10.1109/GHTC56179.2023.10354717` · `10.3390/info16110984` · `10.3390/s21030695` | 2026-09-30 | VER |
| D7 | Khảo sát LoRa (Sensors 2018) xác nhận bối cảnh duty cycle EU 1 % (hoặc LBT/adaptive frequency agility) và tổng hợp simulator | bài báo bình duyệt | `10.3390/s18113995` | 2026-09-30 | VER |
| D8 | **ACM Artifact Review and Badging** — **CHƯA xác minh** trong phiên này (tác nhân phụ trách bị dừng khi đổi phạm vi) | — | — | — | **KHÔNG TÌM THẤY NGUỒN** |
| D9 | "Cách báo cáo kết quả phủ định" (negative results) trong networking — **chưa tìm được bài bình duyệt chuyên biệt** trong phiên này | — | — | — | **KHÔNG TÌM THẤY NGUỒN** |

---

## E. Khoảng trống nghiên cứu (đã kiểm tra, có thể tuyên bố được)

1. **Không tìm thấy** bài bình duyệt đo **PDR / số lần phát / độ trễ theo số hop và số nút** cho **mesh LoRa một kênh, một SF**. Mọi số liệu quy mô hiện có (64–1100 nút/3,8 ha; 1.000 nút/GW mất 32 %) đều dựa vào **trực giao SF của LoRaWAN** → không chuyển được sang mesh một sóng.
2. **Không tìm thấy** thí nghiệm thực địa công bố về **DTN/store-carry-forward trên LoRa với nút di động trong bối cảnh cứu hộ sau thảm họa** có đầy đủ PDR–độ trễ–thời gian contact. Gần nhất là data mule **trong mỏ** (B7) và đề xuất **trên biển** (B10).
3. **Không tìm thấy** nghiên cứu về **công bằng kênh (fairness)** trong mesh LoRa một kênh.
4. **Không tìm thấy** số đo **% overhead beacon/control** cho mesh LoRa một kênh.
5. **SOS tự động do cảm biến qua LoRa**: **CÓ tiền lệ nhưng điểm-điểm**, không mesh/không DTN — Dhineshkumar et al., ICEAMST 2025, DOI `10.1109/ICEAMST67459.2025.11335748`: dùng **cảm biến rung + nghiêng** phát hiện va chạm/lật xe rồi gửi qua **module LoRa tới một máy thu**. → Khoảng trống **đúng mức**: chưa có công bố nào kết hợp SOS tự động do cảm biến (ngã/bất động) với **mesh LoRa một sóng + store-carry-forward** ở **bối cảnh bão lũ nhiệt đới**.

**Cách diễn đạt an toàn:** "trong phạm vi tìm kiếm đã ghi ở mục G, không tìm thấy công bố nào về X" — **không** nói "chưa từng có ai làm".

---

## F. Danh sách số liệu **KHÔNG được dùng**

1. **"120 nút/3,8 ha"** của Bor et al.: con số này là của **bản MSWiM 2016 gốc**; bản đã sửa lỗi (do bug simulator) ghi **64 nút**. Nếu trích phải ghi rõ **phiên bản**.
2. **64 nút/3,8 ha** tuyệt đối **không** được chuyển thành "mesh LoRa một sóng chịu được 64 nút" — đó là LoRaWAN có trực giao SF.
3. **Mọi con số airtime (ms/gói theo SF)** lấy từ trí nhớ hoặc từ URL semtech.com đã chết → chỉ dùng khi mở được nguồn sống.
4. **"median ~80 %"** của BPoL: thuộc **kịch bản so sánh Meshtasticator (20 nút)**, không phải kịch bản Darmstadt 17 nút (ở đó là 40–60 %). Không được trộn hai kịch bản.
5. **LoRaWAN Relay (TS011)** không phải mesh — không được viết "LoRaWAN hỗ trợ mesh".
6. **Số sao GitHub** như thước đo chất lượng khoa học: không dùng.
7. **Mọi số liệu về bão Yagi 2024 / mưa lũ 2025 / quy định tần số Việt Nam**: **phiên này không xác minh** (nhánh tìm kiếm Việt Nam bị dừng khi đổi phạm vi) → nếu cần phải chạy lại, **không** lấy từ tài liệu cũ mà chưa mở nguồn.
8. **"LBT vô dụng trong LoRa"**: nguồn chỉ nói hiệu quả giảm khi có nút ẩn — không được phóng đại.
9. **Tuyên bố "chưa ai công bố"**: chỉ dùng dạng "không tìm thấy trong phạm vi tìm kiếm đã ghi".
10. **Giá trị mặc định của `Node Info Broadcast Seconds`** (Meshtastic): chưa xác minh số → chỉ được nêu tên tham số.

---

## G. Sổ tìm kiếm & giới hạn phiên

| Trường | Giá trị |
|---|---|
| Ngày tìm | 2026-09-30 |
| Công cụ | `curl` (Crossref, OpenAlex, arXiv, Semantic Scholar, Europe PMC, GitHub API, ETSI, govinfo, rfc-editor), `web_fetch` cho DuckDuckGo HTML |
| `web_search` | **HỎNG (HTTP 401)** — không dùng được; mọi kết quả đều qua API/`curl` |
| Truy vấn đã dùng | "LoRa mesh network performance evaluation"; "LoRa delay tolerant network store carry forward"; "LoRaWAN scalability collision"; "LoRa hidden terminal capture effect"; "LoRa mesh network multi-hop"; "delay tolerant network LoRa implementation"; "LoRa opportunistic networking mobile node"; "UAV LoRa data collection field experiment"; "LoRa emergency communication disaster"; "fall detection LoRa emergency alert wearable"; "fairness LoRa network channel access duty cycle"; "automatic emergency SOS LoRa mesh sensor triggered"; "simulation calibration validation network research credibility"; "wireless network simulation pitfalls reproducibility"; "Contact Graph Routing delay tolerant network space" |
| Tiêu chí nhận | URL/DOI mở được; có số liệu dùng được; phân biệt rõ bình duyệt vs tài liệu dự án/vendor |
| Tiêu chí loại | Chỉ có tiêu đề mà không mở được nội dung khi số liệu là trọng yếu; tạp chí nghi thu tiền để đăng |
| Tuyên bố novelty | **not_assessed** — chỉ được nói "không tìm thấy trong phạm vi tìm kiếm đã ghi" |
| Chưa làm được trong phiên | (a) xác minh bối cảnh Việt Nam & pháp lý tần số; (b) tiêu chuẩn khẩn cấp 3GPP/CAP/PWS; (c) ACM Artifact Badging; (d) số mặc định overhead của Meshtastic; (e) URL Semtech sống cho AN1200.13. |
