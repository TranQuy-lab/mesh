# Khảo sát kiểm chứng dự đoán beacon chiếm 73–93 % airtime — RescueMesh-LoRa

**Ngày truy cập toàn bộ nguồn: 2026-10-01.** Đề tài: mesh LoRa **một kênh, một SF**, nút chuyển tiếp SOS về gateway; gateway phát BEACON định kỳ, nút **chuyển tiếp beacon** để lan hop count.

**Câu hỏi trọng tâm:** mô hình tái lập của đề tài dự đoán beacon chiếm **73–93 % airtime** mỗi nút ở chu kỳ 60–300 s (`SUY` — kết quả mô hình của đề tài, không phải số đo). Khảo sát này tìm bằng chứng đo được để kiểm chứng/bác bỏ, và tìm bằng chứng về beacon thích ứng.

**Kết luận ngắn:** **KHÔNG TÌM THẤY NGUỒN** đo trực tiếp tỉ lệ airtime dành cho beacon/điều khiển trong **mesh LoRa một kênh có relay beacon**. Mọi bằng chứng định lượng tìm được đều là (a) mô phỏng, (b) LoRaWAN hình sao, hoặc (c) suy ra từ công thức. Dự đoán 73–93 % **không được kiểm chứng trực tiếp** bởi bất kỳ bài đo nào; nó chỉ **tương thích về định tính** với ba quan sát độc lập: điều khiển/relay là chi phí trội trong LoRa mesh; các hệ thống thật chọn chu kỳ quảng bá **thưa hơn 60–300 s rất nhiều** (3 h–12 h); và đã có cơ chế **giãn chu kỳ theo số nút** trong firmware thật.

---

## A. Bảng bằng chứng về overhead điều khiển

| Số liệu | Đo / Mô phỏng / Tính từ công thức | Nguồn (DOI/URL) | Độ tin cậy |
|---|---|---|---|
| **Không có bài nào đo tỉ lệ % airtime cho beacon/control trong mesh LoRa một kênh** | — | Khảo sát toàn bộ OpenAlex/Crossref/DDG 2026-10-01 | **KHÔNG TÌM THẤY NGUỒN** |
| Repeater duty cycle (truyền) khi **flooding**: **>10 %** mọi repeater; khi **routing**: **0,7 %–3,7 %** | Mô phỏng (SimPy, LoRaMeshSimulator) | arXiv:2510.03714 — https://arxiv.org/abs/2510.03714 | Trung bình (preprint, mô phỏng) — không phải beacon |
| PDR mạng: **88,7 %** (flooding) vs **96,7 %** (routing); throughput tối đa **+185 %**, năng lượng **−75 %** so với flooding tối ưu | Mô phỏng | arXiv:2510.03714 | Trung bình (preprint) |
| LoRaWAN Class B: **beacon 1 lần mỗi 128 s**, do **gateway** phát (hình sao) | Tiêu chuẩn / tài liệu hãng | Semtech Learning Center — https://learn.semtech.com/mod/book/view.php?id=175&chapterid=168 | Cao (hãng) — **topology khác** |
| ToA beacon LoRaWAN (SF9, 125 kHz) **160 ms**; beacon period 128 s ⇒ beacon chiếm **≈0,125 %** thời gian (tính: 0,160/128) | Tính từ công thức (giá trị tham chiếu trong bài) | DOI 10.1109/ACCESS.2023.3301991 | Trung bình — **hình sao, phía gateway** |
| Khung beacon chuẩn: beacon reserved **2,12 s** + guard **3 s** + window **122,88 s** / 128 s ⇒ reserved = **≈1,66 %** chu kỳ | Tiêu chuẩn (mô tả trong bài bình duyệt) | DOI 10.1109/ACCESS.2023.3301991 | Cao |
| "Usefulness" (tỉ lệ gói nhận được chứa thông tin **mới**, không phải bản sao do rebroadcast) giảm khi tăng hop limit | Mô phỏng (100 lần chạy × 200 s) | Meshtasticator — https://github.com/GUVWAF/Meshtasticator | Thấp–trung bình (project doc) |
| Mesh LoRa dùng flooding "tiêu tốn băng thông do retransmission mọi gói ở mọi repeater" | Tổng quan có bình duyệt | DOI 10.1145/3638241 (ACM CSUR 2024) | Cao (định tính) |
| WiFi mesh: beacon/probing overhead **đo được** (topology khác) | Đo thực nghiệm | DOI 10.1109/ICSPC.2007.4728268 | Thấp cho LoRa — **khác công nghệ** |

**Diễn giải:** không có nguồn nào trả lời trực tiếp câu hỏi 1. Các bài về **LoRaWAN** (Bor 2016, ABPC 2023, LoRaWANSim 2021) đều là **hình sao một hop** — phải ghi rõ khi trích. Các bài **mesh LoRa** (MASCOTS 2024, arXiv 2510.03714, WINS 2026) đo/mô phỏng **flooding dữ liệu**, không tách riêng beacon.

---

## B. Trickle (RFC 6206) và beacon thích ứng: lý thuyết + số đo

### B.1 Nguyên lý (chuẩn)
Nguồn: **RFC 6206**, DOI `10.17487/rfc6206`, https://www.rfc-editor.org/rfc/rfc6206.txt (standard, 2011-03; truy cập 2026-10-01).

- Ba tham số: **I_min** (đơn vị thời gian), **I_max** (số lần gấp đôi so với I_min, tức log2(max/min)), **k** — hằng số dư thừa (*redundancy constant*).
- Biến: **I** (khoảng hiện tại), **t** (thời điểm ngẫu nhiên trong **[I/2, I)**), **c** (bộ đếm).
- Sáu luật: c←0 khi bắt đầu khoảng; nghe bản tin *consistent* thì c++; **tại t chỉ phát nếu c < k** (*suppression*); hết khoảng thì **I ← 2I** (chặn ở I_max); nghe bản tin *inconsistent* và I > I_min thì **reset về I_min** (phát hiện thay đổi).
- Mục tiêu: "chỉ gửi **vài bản tin mỗi giờ** khi thông tin không đổi", phát tán "trong thang thời gian truyền link-layer" khi có thay đổi; tốc độ **scale theo logarit** với mật độ.
- Khuyến nghị: đặt **I_min ≥ 2–3 lần** thời gian truyền **k** gói; k điển hình **1–5** (RFC), **RPL dùng k = 10** (RFC 6550), **MPL dùng k = 1**.

### B.2 Số đo
| Số liệu | Loại | Nguồn |
|---|---|---|
| Chi phí bảo trì "**vài gói mỗi giờ mỗi mote**" (*a few packets per hour per mote*); số truyền tăng theo **O(log n)** với mật độ | Mô phỏng (TOSSIM) + phân tích (NSDI 2004) | Levis et al., NSDI 2004 — http://csl.stanford.edu/~pal/pubs/trickle-nsdi04.pdf |
| Trong mạng 1000 mote (mô phỏng) "redundancy" chỉ **hơn 3**; 512→1024 mote quan sát vẫn ~75 láng giềng nên số truyền tăng | Mô phỏng | NSDI 2004 |
| Testbed thật **43 nút WSN430 (IoT-Lab Rennes, 802.15.4)**, mỗi cấu hình k chạy **5 lần × 1 h**: số truyền **DIO** thay đổi rõ theo k; adaptive-k cân bằng overhead/PDR | **ĐO THỰC NGHIỆM** | Meyfroyt et al., WoWMoM 2015, DOI `10.1109/wowmom.2015.7158134` + arXiv:1509.08664 |
| Mô phỏng Cooja: DODAG formation time **≈0,2–1,6 s**, phụ thuộc mật độ (sparse/medium/dense), ít phụ thuộc k | Mô phỏng | DOI `10.1109/wowmom.2015.7158134` |
| RFC hiện trường: `k` "ảnh hưởng lớn nhất tới việc dựng bảng định tuyến"; có **đánh đổi giữa thời gian hội tụ và số DIO/collision** | Phân tích/mô phỏng (trích dẫn trong bài) | DOI `10.1109/wowmom.2015.7158134` |
| Các biến thể thích ứng: **Trickle-plus** (DOI `10.1109/wcnc.2016.7564654`), **Trickle++** context-aware (DOI `10.1109/glocom.2017.8254531`), **Drizzle** — cơ chế *suppression* thích ứng + bỏ *listen-only period* → hội tụ nhanh hơn (DOI `10.1109/jiot.2018.2862364`, chỉ đọc abstract), **Improved Trickle** (DOI `10.1109/jsen.2017.2787584`), **FL-Trickle** (DOI `10.1007/s11277-019-06792-2`), **Trickle-F** (DOI `10.1109/sustainit.2013.6685187`) | Lý thuyết/mô phỏng | các DOI trên |

### B.3 Trickle trên LoRa?
**KHÔNG TÌM THẤY NGUỒN** về một bài **áp Trickle lên LoRa/LoRaWAN và đo overhead/hội tụ**. Các kết quả Trickle tìm được đều trên **LLN 802.15.4 / RPL / MPL** (Contiki/Cooja, IoT-Lab) — **topology và PHY khác LoRa** (không có vấn đề ToA, duty cycle 1 %, capture effect, một SF). Không được suy thẳng số Trickle 802.15.4 sang LoRa.

### B.4 Bằng chứng beacon thích ứng gần nhất với đề tài
- **Adaptive Beacon Period Configurator (ABPC)** cho **LoRaWAN Class B**: thay beacon period 128 s chuẩn bằng **64/128/256/512/1024 s** tùy số thiết bị/tải, đồng thời chỉnh `k_max` và `t_pingslot`. Kết quả: beacon thưa hơn ⇒ **nghe ít hơn**, pin "**tới +200 % ngày hoạt động**" so với chuẩn. — DOI `10.1109/ACCESS.2023.3301991` (bài bình duyệt; **mô phỏng ns-3 + mô hình giải tích**; **hình sao, gateway→node**, không phải relay beacon).
- **Meshtastic tự giãn chu kỳ quảng bá theo số nút**: từ firmware **2.4.0**, với mesh **>40 nút** (thấy trong 2 h): `ScaledInterval = Interval × (1.0 + ((NumberOfOnlineNodes − 40) × 0.075))`. — https://meshtastic.org/docs/overview/mesh-algo/ (project doc). Ví dụ tài liệu: 62 nút ⇒ telemetry 30 min → **79,5 min**. **Tính thêm (công thức):** NodeInfo 3 h ở 62 nút → 10800 × 2,65 ≈ **28 620 s ≈ 7,95 h**.
- **Mã nguồn firmware** xác nhận cùng cơ chế (`congestionScalingCoefficient`, `getConfiguredOrDefaultMsScaled`): bỏ scale cho `ROUTER`/`ROUTER_LATE`/`SENSOR`/`TRACKER`; scale cho `CLIENT`. — https://raw.githubusercontent.com/meshtastic/firmware/master/src/mesh/Default.cpp và `.../Default.h`.

---

## C. Chu kỳ beacon trong hệ thống thật (giá trị mặc định)

| Hệ thống | Chu kỳ quảng bá định danh/định tuyến | Tắt/giảm beacon? | Nguồn |
|---|---|---|---|
| **Meshtastic — NodeInfo** | **Mặc định 10 800 s (3 h)**; dải cấu hình **3 600 s → UINT MAX**; firmware đặt `min_node_info_broadcast_secs = 60 × 60 = 3 600 s` ("không quảng bá thường xuyên hơn 1 lần/giờ") | Có: giãn theo số nút (>40, công thức B.4); `CLIENT_HIDDEN` đặt `node_info_broadcast_secs = MAX_INTERVAL`; `TAK`/`TAK_TRACKER` = `ONE_DAY` | Docs: https://meshtastic.org/docs/configuration/radio/device/ · Firmware: `src/mesh/Default.h`, `NodeDB.cpp` · https://meshtastic.org/docs/overview/mesh-algo/ |
| **Meshtastic — Position** | Mặc định **15 min** (smart broadcast); Telemetry **30 min** | Có (cùng công thức scale) | https://meshtastic.org/docs/overview/mesh-algo/ |
| **Meshtastic — Neighbor Info** | Mặc định **6 h**, tối thiểu **4 h** | Có | Firmware `src/mesh/Default.h` |
| **MeshCore — repeater flood advert** | **12 h** mặc định; `set flood.advert.interval {hours}`, dải **3–168 h** | Có (cấu hình được); client **chỉ advert khi người dùng bấm**; `set advert.interval {minutes}` cho zero-hop | https://docs.meshcore.io/faq/ · https://docs.meshcore.io/cli_commands/ |
| **LoRaWAN Class B — beacon** | **128 s**, do **gateway** phát (downlink, hình sao) | Không thuộc nút; beacon dùng để đồng bộ + pingslot | Semtech: https://learn.semtech.com/mod/book/view.php?id=175&chapterid=168 · ABPC DOI `10.1109/ACCESS.2023.3301991` |

**Nhận xét định hình:** ba hệ thống mesh thật đều chọn chu kỳ quảng bá định danh **1–12 h**, **không** dùng 60–300 s. Chu kỳ 60–300 s của đề tài thưa hơn mặc định Meshtastic **36–180 lần**. Không hệ thống nào để **nút** phát beacon mỗi 60–300 s; cơ chế gần nhất là **giãn theo số nút** (Meshtastic) — tức đúng hướng "beacon thích ứng".

---

## D. Sức chứa, capture effect, nút ẩn (làm rõ **bản Bor đã sửa lỗi**)

### D.1 Bor et al. — bản đã sửa (quan trọng)
- Bản gốc MSWiM 2016: DOI `10.1145/2988287.2989163`.
- **Bản đã sửa**: https://eprints.lancs.ac.uk/81674/13/lora_scalability_r338.pdf (PDF tải được 2026-10-01, 9 trang). Ghi chú đính chính trong bài: *"Mariusz Slabicki found a bug in the simulator… previously collided packets would in some cases be marked as 'not collided', thereby overestimating the goodput… The bug was fixed and all figures and numbers have been updated."*
- Số liệu **bản sửa — ĐỌC TRỰC TIẾP PDF**:
  - Abstract + thân bài: **"64 nodes per 3.8 ha"** với cấu hình LoRaWAN mặc định (SN 3) và yêu cầu **DER > 0,9**.
  - Tối ưu airtime (SN 4): **"well over N = 1100 nodes"** với DER > 0,9.
  - Capture effect: ở **N = 200**, DER tăng **0,51 → 0,64** khi dùng mô hình kênh LoRa (có capture) thay vì mô hình đơn giản (Pure ALOHA). Cần **≥5 symbol preamble nguyên vẹn** thì máy thu bắt được gói.
  - Công thức Pure ALOHA: **DER = e^(−2N·T_packet·λ)** (Eq. 12) — **tính từ công thức**, không phải đo.
  - SN 1 (SF12, 20 B) airtime **1712,13 ms**; tần suất 1 gói/16,7 min; SN 3 cho channel duty-cycle **0,13 %** > mức 0,1 % của châu Âu ⇒ phải giãn xuống 1 gói/22 min.
  - **Cảnh báo:** chính PDF sửa lỗi vẫn còn dòng **"N = 120 nodes"** sót lại trong **chú thích Figure 4** (mâu thuẫn với thân bài 64 nút); trang EPrints (abstract) cũng còn ghi **"120 nodes per 3.8 ha"**. ⇒ **Không dùng 120.**
- Năng lượng: bài định nghĩa **NEC** (Network Energy Consumption) = năng lượng mạng để trích thành công 1 gói.

### D.2 Capture effect
| Số liệu | Loại | Nguồn |
|---|---|---|
| Capture: DER 0,51→0,64 @ N=200; cần ≥5 preamble symbol | Mô phỏng (mô hình hoá từ thực nghiệm) | Bor bản sửa, URL trên |
| CAD phát hiện được cả **payload chirp**, không chỉ preamble ⇒ có thể carrier-sense | **ĐO THỰC NGHIỆM** (nhiều phép đo) | LMAC, DOI `10.1145/3564530` (ACM TOSN 2023) |
| Capture + CAD cải thiện PDR trong mạng dày; "preliminary tests show promising capabilities in increasing the PDR" | **ĐO THỰC NGHIỆM** | Sensors 2021, DOI `10.3390/s21030825` |
| Mô hình throughput LoRa **có capture effect** từ thực nghiệm | Đo + mô hình | DOI `10.1109/WiMob55322.2022.9941715` |

### D.3 Nút ẩn (hidden node)
- **Hidden Node Probability in LoRa with LBT**, IEEE WCL 13(10), DOI `10.1109/lwc.2024.3453788` (2024-10): HNP phân tích theo **vành (annulus) và SF**, dùng **Nakagami-m + path loss**; mạng trải rộng **>10 km**; kết luận LBT **không đáng tin khi có nút ẩn** (thiết bị có thể tưởng kênh rảnh sai).
- Bor bản sửa (PDF) cũng nêu hidden terminal làm "observed density" bão hoà ~75 láng giềng khi mật độ vật lý tăng.

---

## E. Simulator và hiệu chuẩn

| Simulator | Mô hình hoá gì | Thiếu gì | Nguồn |
|---|---|---|---|
| **LoRaSim** (SimPy) | Va chạm, DER, NEC; tới 24 BS; mô hình kênh log-distance | Không mô hình SF không trực giao hoàn hảo, downlink, duty cycle | https://www.lancaster.ac.uk/scc/sites/lora/lorasim.html · Bor bản sửa |
| **FLoRa** (OMNeT++/INET) | PHY LoRa chi tiết (collision + capture), 1/nhiều gateway, backhaul, ADR, thống kê năng lượng | — (bản 1.3.1, 2026-09-16: sửa lỗi đơn vị SNIR của ADR) | https://flora.aalto.fi/ · DOI `10.1109/NOMS.2018.8406255` |
| **ns-3 LoRaWAN module** | LoRaWAN MAC/PHY, ADR, uplink/downlink | Chủ yếu hình sao | DOI `10.1145/3199902.3199913` |
| **LoRaWANSim** (MATLAB) | PHY + MAC + network; capture, inter-SF, DC, năng lượng | Hình sao LoRaWAN | DOI `10.3390/s21030695` |
| **LoRaMeshSim** (SimPy, Python) | Mesh tuyến tính, repeater, carrier sensing, đa kênh | (MASCOTS 2024 mô tả) | DOI `10.1109/MASCOTS64422.2024.10786574` |
| **Meshtasticator** | Mô phỏng discrete-event radio Meshtastic; interactive dùng firmware Linux thật; dựa trên LoRaSim | Không phải bản firmware đầy đủ trong chế độ discrete-event | https://github.com/GUVWAF/Meshtasticator |

### E.1 Hiệu chuẩn mô phỏng ↔ đo thực (LoRaWANSim, Sensors 2021)
Nguồn: DOI `10.3390/s21030695`; PDF https://mdpi-res.com/d_attachment/sensors/sensors-21-00695/article_deploy/sensors-21-00695.pdf (tải 2026-10-01). Thí nghiệm: **5 bo mạch RN2483 (SX1276), 1 gateway cách 50 m**, 1 h, SF = 7 và SF = 10.

**Table 10 (uplink delivery rate)** — đọc trực tiếp PDF:

| Kết quả | SF = 7 | SF = 10 |
|---|---|---|
| Analytical | 0,991 | 0,959 |
| **Experimental (đo thực)** | **0,968** | **0,914** |
| **Simulated** | **0,997** | **0,978** |

⇒ Sai số simulator vs thực nghiệm (tính): **+2,9 điểm phần trăm** (SF7) và **+6,4 điểm phần trăm** (SF10). Simulator **đánh giá cao hơn thực tế**; bài giải thích phần lệch do nhiễu từ hệ thống bên thứ ba. Đây là **so sánh đo thực** trên mạng **nhỏ, hình sao** — không đại diện mesh nhiều hop.

---

## F. Khoảng trống

1. **KHÔNG TÌM THẤY NGUỒN** đo tỉ lệ airtime của **beacon relay** trong mesh LoRa **một kênh, một SF**. Không bài nào tách "airtime truyền beacon của chính nút" vs "airtime chuyển tiếp beacon của nút khác".
2. **KHÔNG TÌM THẤY NGUỒN** áp **Trickle (RFC 6206)** lên LoRa rồi **đo** overhead/hội tụ. Các biến thể Trickle đều trên 802.15.4/RPL/MPL.
3. **Chưa có số đo** chi phí của **pha học hop count bằng beacon** (thời gian hội tụ, số beacon cần, airtime) trong mesh LoRa.
4. Chưa có **mô hình kênh một-SF nhiều-nút có relay beacon**: mọi simulator mesh (LoRaMeshSim, Meshtasticator) mô phỏng **flooding dữ liệu**, không có beacon định kỳ do nút phát rồi relay.
5. **Chuẩn hoá:** arXiv:2510.03714 nêu **LoRaWAN Relay standard** (LoRa Alliance) mới hỗ trợ **single-hop** gateway↔end device, **không xâu chuỗi nhiều relay** — dẫn nguồn từ preprint, cần xác minh lại bằng chính văn bản chuẩn nếu trích.
6. **LoRaWAN Class B beacon (128 s)** không thể dùng làm chuẩn quy chiếu cho beacon nút trong mesh: đó là **downlink gateway→node**, gateway có nguồn điện và duty cycle khác.

---

## G. Số liệu KHÔNG được dùng

| Số liệu | Vì sao không dùng |
|---|---|
| **"120 nút/3,8 ha"** | Thuộc **bản MSWiM 2016 gốc** (lỗi simulator). Bản sửa ghi **64 nút/3,8 ha**. PDF sửa vẫn sót "120" ở chú thích Figure 4 và trang EPrints vẫn ghi 120 ⇒ chỉ dùng **64**, và **luôn ghi rõ phiên bản**. |
| **Meshtastic `node_info_broadcast_secs` = 900 s (15 min)** | Chỉ có trong **comment của `config.proto`**; **mâu thuẫn** với docs chính thức (**10 800 s**) và firmware (`default_node_info_broadcast_secs = 3*60*60`). Không dùng 900. |
| **"Beacon chiếm 73–93 % airtime"** | Là **kết quả mô hình `SUY` của đề tài**, **không** phải số đo và **không** tìm thấy trong tài liệu. Chỉ được trích như "mô hình của đề tài dự đoán". |
| **"median ~80 %" của BPoL** | Thuộc **kịch bản so sánh Meshtasticator 20 nút**, không phải kịch bản Darmstadt 17 nút (40–60 %). |
| **"Meshtastic dùng duty cycle 1 %"** | Sai: cấu hình EU của Meshtastic là **10 %/giờ (rolling 1 h)**. Mức **1 %** là của **QCVN 122:2020 cho đầu cuối Việt Nam** — không trộn hai nguồn. |
| **Beacon 128 s như chu kỳ nút trong mesh** | Đó là **LoRaWAN hình sao, gateway phát**, không phải nút relay. |
| **Số liệu từ Maman WiMob 2017** (star→mesh energy) | DOI hợp lệ (`10.1109/wimob.2017.8115793`) nhưng **không đọc được toàn văn** trong phiên này ⇒ **không trích số**. |
| **"O(log n)" của Trickle quy đổi thành % airtime** | Là **kết quả lý thuyết/mô phỏng 802.15.4**, không phải tỉ lệ airtime đo được; không quy đổi sang LoRa. |
| **"1100 nút" của Bor** | Là **kết quả mô phỏng** với giả định lạc quan (bài tự nêu "not practical": bỏ qua interference, CR thấp) — không phải năng lực đo được. |
| **Số liệu 185 %/75 % của arXiv:2510.03714** | Là **preprint + mô phỏng**, kịch bản duty cycle 100 % dưới lòng đất — không áp cho mạng một kênh duty-cycle hạn chế. |

---

## H. Sổ tìm kiếm

**Công cụ (2026-10-01):** `web_search` harness **hỏng (HTTP 401)** → không dùng. Dùng: **OpenAlex API** (`research_tools/oa.py`), **Crossref API** (`api.crossref.org`, xác minh DOI), **Semantic Scholar Graph API** (abstract + OA PDF), **DuckDuckGo HTML qua `r.jina.ai`** (thay search engine), **`r.jina.ai`** để đọc trang chặn bot, **curl + pdftotext** cho PDF mở.

**Truy vấn chính:** "Trickle algorithm LoRa"; "Trickle low power lossy network overhead"; "beacon overhead LoRa mesh network"; "LoRaWAN beacon Class B"; "LoRa mesh network beacon relay hop count"; "LoRa capture effect interference"; "LoRaWAN simulation calibration measurement"; "LoRa energy consumption mesh multihop"; "FLoRa LoRa simulator"; "adaptive beacon interval wireless sensor network"; "adaptive beacon rate LoRa network"; "Meshtastic LoRa mesh network evaluation"; "LoRa mesh routing control overhead percentage"; "hidden node probability LoRa listen before talk"; "LoRaWANSim simulator LoRaWAN"; "Trickle protocol measurement testbed overhead"; "Trickle algorithm performance analysis convergence time"; "single channel LoRa mesh network testbed measurement"; "Meshtastic node info broadcast interval overhead measurement"; "LoRa mesh network measured channel occupancy airtime utilization"; "Trickle algorithm applied to LoRa network"; "LoRaWAN specification Class B beacon 128 seconds".

**Nguồn đã xác minh DOI bằng Crossref (2026-10-01):** 10.1145/2988287.2989163 · 10.17487/rfc6206 · 10.1109/wowmom.2015.7158134 · 10.1109/wimob.2017.8115793 · 10.3390/s21030695 · 10.3390/s21030825 · 10.1109/lwc.2024.3453788 · 10.1109/mascots64422.2024.10786574 · 10.1145/3199902.3199913 · 10.1109/noms.2018.8406255 · 10.1109/access.2023.3301991 · 10.1145/3638241 · 10.3311/wins2026-013 · 10.1049/cmu2.70221 · 10.3390/s26072226 · 10.1145/3564530 · 10.1109/jiot.2018.2862364 · 10.1109/jsen.2017.2787584 · 10.1007/s11277-019-06792-2 · 10.1109/wcnc.2016.7564654 · 10.1109/glocom.2017.8254531 · 10.1109/sustainit.2013.6685187 · 10.1109/wimob55322.2022.9941715.

**Tài liệu dự án / hãng đã mở:** meshtastic.org (device, mesh-algo, lora, blog power) · github raw: meshtastic/firmware (`Default.h`, `Default.cpp`, `NodeDB.cpp`), meshtastic/protobufs (`config.proto`) · docs.meshcore.io (faq, cli_commands) · learn.semtech.com (Class B) · flora.aalto.fi · lancaster.ac.uk (LoRaSim) · github.com/GUVWAF/Meshtasticator · eprints.lancs.ac.uk/81674/13 (Bor bản sửa) · rfc-editor.org (RFC 6206) · usenix/csl.stanford.edu (Trickle NSDI 2004).

**Không lấy được toàn văn (chỉ metadata/abstract):** Drizzle (CAPTCHA), Improved Trickle, FL-Trickle, Trickle-plus/Trickle++, Maman WiMob 2017 (CAPTCHA), IET Communications Meshtastic energy (CAPTCHA — có abstract đầy đủ số liệu), ACM CSUR survey (chỉ abstract).

---

## Phụ lục: bằng chứng năng lượng (mesh vs hình sao) — liên quan trực tiếp đến chi phí relay

| Số liệu | Loại | Nguồn |
|---|---|---|
| **6 nút LilyGO, firmware Meshtastic 2.7, EU868, 4 tầng NLOS; đo bằng Otii Arc.** Vai trò Tx / Rx / **relay** có nhu cầu năng lượng **gần như giống nhau**: **125–126 mA trung bình**, **467–470 mJ/gói**, **~25–26 h** với pin 3200 mAh ⇒ "**relaying imposes no measurable energy penalty under always-on operation**" | **ĐO THỰC NGHIỆM** | DOI `10.1049/cmu2.70221` (IET Communications 2026) — đọc qua abstract |
| 1 relay nâng PDR **1,0 % → 96,5 %**; 2 relay chia tải **66,5 % / 33,5 %**; relay tầng trung gian PDR **99,25 %** vs trực tiếp **38,50 %** | **ĐO THỰC NGHIỆM** | DOI `10.1049/cmu2.70221` |
| Flooding làm repeater duty cycle **>10 %**; routing chỉ **0,7–3,7 %** và giảm **75 %** năng lượng | Mô phỏng | arXiv:2510.03714 |
| Quy trình đo năng lượng nút solar thật (không nêu con số tổng hợp) | Tài liệu dự án (phương pháp) | https://meshtastic.org/blog/measuring-solar-node-power-consumption/ |
| DDES: ngủ thích ứng theo thay đổi dữ liệu để tiết kiệm năng lượng LoRa-Mesh | Bài bình duyệt (chỉ abstract) | DOI `10.3390/s26072226` |
| WINS 2026: mô phỏng Meshtastic 26 nút tuyến tính (SF9, 14 dBm, 869,25 MHz) — **không mô hình hoá duty cycle, downlink hay beacon**; năng lượng tăng theo hop | Mô phỏng | DOI `10.3311/wins2026-013` |

**Đối chiếu giả thuyết "mesh tốn pin hơn hình sao":** bằng chứng đo được duy nhất tìm thấy (IET 2026) **không** xác nhận hình phạt năng lượng cho relay khi thiết bị **always-on**; chênh lệch chỉ xuất hiện khi **flooding** làm duty cycle tăng vọt (mô phỏng arXiv). Đây là điểm cần nêu rõ: **KHÔNG TÌM THẤY NGUỒN đo** so sánh trực tiếp pin mesh vs hình sao trên cùng phần cứng/kịch bản.

---

### Nguồn (tối thiểu 15, đã kiểm)
1. Bor, Roedig, Voigt, Alonso — *Do LoRa Low-Power Wide-Area Networks Scale?* (bản sửa) — `10.1145/2988287.2989163` + https://eprints.lancs.ac.uk/81674/13/lora_scalability_r338.pdf — bình duyệt (bản đã sửa).
2. Levis, Clausen, Hui, Gnawali, Ko — *The Trickle Algorithm*, RFC 6206 — `10.17487/rfc6206` — chuẩn.
3. Levis, Patel, Culler, Shenker — *Trickle*, NSDI 2004 — http://csl.stanford.edu/~pal/pubs/trickle-nsdi04.pdf — bình duyệt.
4. Meyfroyt et al. — *Adaptive broadcast suppression for Trickle-based protocols*, WoWMoM 2015 — `10.1109/wowmom.2015.7158134` (+arXiv:1509.08664) — bình duyệt, có testbed.
5. *Trickle-plus* — `10.1109/wcnc.2016.7564654` — bình duyệt.
6. *Trickle++* — `10.1109/glocom.2017.8254531` — bình duyệt.
7. *Drizzle* — `10.1109/jiot.2018.2862364` — bình duyệt (abstract).
8. *Improved Trickle* — `10.1109/jsen.2017.2787584` — bình duyệt (abstract).
9. *FL-Trickle* — `10.1007/s11277-019-06792-2` — bình duyệt (abstract).
10. *Trickle-F* — `10.1109/sustainit.2013.6685187` — bình duyệt.
11. Todolí-Ferrandis et al. — *Adaptive Beacon Period Configurator…* IEEE Access 2023 — `10.1109/access.2023.3301991` — bình duyệt.
12. *LoRaWANSim* Sensors 2021 — `10.3390/s21030695` — bình duyệt (có hiệu chuẩn đo thực).
13. *Slabicki et al. — Adaptive configuration of LoRa networks*, NOMS 2018 (FLoRa) — `10.1109/noms.2018.8406255` + https://flora.aalto.fi/ — bình duyệt + tài liệu dự án.
14. *A LoRaWAN module for ns-3*, WNS3 2018 — `10.1145/3199902.3199913` — bình duyệt.
15. *Scalability Analysis of Linear LoRa Mesh Networks*, MASCOTS 2024 — `10.1109/mascots64422.2024.10786574` — bình duyệt.
16. *Hidden Node Probability in LoRa With Listen-Before-Talk*, IEEE WCL 2024 — `10.1109/lwc.2024.3453788` — bình duyệt.
17. *Dense Deployment of LoRa Networks… CAD and Capture Effect*, Sensors 2021 — `10.3390/s21030825` — bình duyệt.
18. *LMAC*, ACM TOSN 2023 — `10.1145/3564530` — bình duyệt.
19. *Multi-Hop and Mesh for LoRa Networks*, ACM CSUR 2024 — `10.1145/3638241` — bình duyệt.
20. *Beyond Single-Hop: Simulation Study of Meshtastic*, WINS 2026 — `10.3311/wins2026-013` — bình duyệt (mô phỏng).
21. *Communication and Energy Consumption… Meshtastic*, IET Communications 2026 — `10.1049/cmu2.70221` — bình duyệt (đo thực).
22. *Data-Driven Energy-Saving Methods Based on LoRa-Mesh*, Sensors 2026 — `10.3390/s26072226` — bình duyệt (abstract).
23. *Evaluating LoRa energy efficiency… From star to mesh*, WiMob 2017 — `10.1109/wimob.2017.8115793` — bình duyệt (chỉ metadata).
24. *Experimental throughput models for LoRa with capture effect*, WiMob 2022 — `10.1109/wimob55322.2022.9941715` — bình duyệt.
25. *A Position- and Energy-Aware Routing Strategy for Subterranean LoRa Mesh Networks* — arXiv:2510.03714 — **preprint**.
26. Meshtastic docs — https://meshtastic.org/docs/configuration/radio/device/ · https://meshtastic.org/docs/overview/mesh-algo/ · https://meshtastic.org/blog/measuring-solar-node-power-consumption/ — tài liệu dự án.
27. Meshtastic firmware/protobuf nguồn — `src/mesh/Default.h`, `src/mesh/Default.cpp`, `src/mesh/NodeDB.cpp`, `meshtastic/config.proto` (raw.githubusercontent.com) — mã nguồn dự án.
28. MeshCore docs — https://docs.meshcore.io/faq/ · https://docs.meshcore.io/cli_commands/ — tài liệu dự án.
29. Semtech Learning Center — Class B beacon — https://learn.semtech.com/mod/book/view.php?id=175&chapterid=168 — tài liệu hãng.
30. LoRaSim — https://www.lancaster.ac.uk/scc/sites/lora/lorasim.html · Meshtasticator — https://github.com/GUVWAF/Meshtasticator — tài liệu dự án.
