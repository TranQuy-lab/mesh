# Báo cáo tái lập RescueMesh-LoRa

- Thời điểm chạy (UTC): `2026-09-30T17:27:13Z`
- Python: `Python 3.12.3`
- Máy: `Linux x86_64`

## 1. Kiểm thử

```
test_lora.py               32/32 test qua
test_node_power.py         19/19 test qua
test_packets.py            15/15 test qua
test_packets_lora.py       36/36 test qua
test_sim_lora.py           OK
test_g0_schedule.py        4/4 test qua
```

## 2. Bảng thiết kế (nhãn SUY)

```
--- lora.py ---
================================================================================================
BẢNG ĐÁNH ĐỔI SF — LoRa BW125 kHz, CR 4/5, payload 40 B, Tx 14 dBm
Nhãn: SUY (mô hình log-distance). KHÔNG phải tầm xa đo được.
================================================================================================
 SF |     bps |   airtime | khung/s | nhạy dBm |  xa FS km | xa n=3 km |  xa n=3.5
----------------------------------------------------------------------------------
  7 |    5469 |    82.2ms |   12.17 |   -123.0 |     230.7 |       3.8 |       1.2
  8 |    3125 |   154.1ms |    6.49 |   -126.0 |     325.8 |       4.7 |       1.4
  9 |    1758 |   287.7ms |    3.48 |   -129.0 |     460.3 |       6.0 |       1.7
 10 |     977 |   534.5ms |    1.87 |   -132.0 |     650.1 |       7.5 |       2.1
 11 |     537 |  1069.1ms |    0.94 |   -133.0 |     729.5 |       8.1 |       2.2
 12 |     293 |  1974.3ms |    0.51 |   -136.0 |    1030.4 |      10.2 |       2.7

================================================================================================
SỨC CHỨA MỘT GATEWAY ĐƠN KÊNH (chỉ tính airtime, chưa tính collision)
Giả định: 1 SOS/nút/giờ, beacon 60 s, relay_multiplier = 3
================================================================================================
SF7 : airtime    82.2 ms | 100 nút dùng  14.38 % thời gian | tối đa    556 nút ở mức 80 % |      7 nút ở duty cycle 1 %
SF9 : airtime   287.7 ms | 100 nút dùng  50.36 % thời gian | tối đa    159 nút ở mức 80 % |      2 nút ở duty cycle 1 %
SF10: airtime   534.5 ms | 100 nút dùng  93.54 % thời gian | tối đa     86 nút ở mức 80 % |      1 nút ở duty cycle 1 %
SF12: airtime  1974.3 ms | 100 nút dùng 345.50 % thời gian | tối đa     23 nút ở mức 80 % |      0 nút ở duty cycle 1 %

LƯU Ý: chưa mô hình hoá collision, hidden terminal, capture effect,
mất gói do địa hình hay duty cycle theo luật. Đây là giới hạn trên.
--- node_power.py ---
====================================================================================================
PHÂN RÃ ĐIỆN LƯỢNG MỖI NGÀY — nút LoRa một sóng (nhãn: SUY từ GIẢ ĐỊNH)
Pin 18650 3000 mAh, dùng được 80 %, beacon 5 phút, 0,05 SOS/ngày
====================================================================================================
 SF | airtime beacon |  mAh/ngày |   tuổi thọ |   mAh/SOS |  duty cycle |         chi phối bởi
----------------------------------------------------------------------------------------------
  7 |        51.5 ms |    3.2837 |      731 ng |     65.67 |      0.02 %  |            tự xả pin
  9 |       185.3 ms |    3.5839 |      670 ng |     71.68 |      0.06 %  |            tự xả pin
 12 |      1318.9 ms |    6.1258 |      392 ng |    122.52 |      0.44 %  |          phát beacon

Dấu ! = duty cycle vượt 1 % — ngưỡng của QCVN 122:2020/BTTTT cho đầu cuối
(đã xác minh từ bản công báo gốc; gateway được 10 %).

KỊCH BẢN NGHE KÊNH LIÊN TỤC (rx_fraction = 1.0) VÀ GNSS MỖI NGÀY:
  SF7 :  255.28 mAh/ngày (nghe 247.20, GNSS 5.00) →   9.4 ngày pin
  SF9 :  255.58 mAh/ngày (nghe 247.20, GNSS 5.00) →   9.4 ngày pin
  SF12:  258.12 mAh/ngày (nghe 247.20, GNSS 5.00) →   9.3 ngày pin

KẾT LUẬN THIẾT KẾ (SUY): trên nút một sóng, chi phí vô tuyến rất nhỏ so
với chi phí luôn-nghe và GNSS. Nút phải ngủ theo lịch và bắt GNSS theo
sự kiện, nếu không pin cạn trong vài tuần dù gần như không phát gói nào.
Đây là điều phải ĐO ở WP10, không được trích như kết quả.
--- packets_lora.py ---
==============================================================================
BẢNG KÍCH THƯỚC KHUNG v2.0 (byte)
Nguồn: ĐÓNG BĂNG — con số do đặc tả v2.0 chốt, không phải đo.
==============================================================================
khung      |  mã |  byte | tag B | evidence
-------------------------------------------
SOS        |   1 |    36 |     8 | GIẢ ĐỊNH
HEARTBEAT  |   2 |    14 |     4 | GIẢ ĐỊNH
BEACON     |   3 |    18 |     8 | GIẢ ĐỊNH
ACK        |   4 |    12 |     5 | GIẢ ĐỊNH
MAX_PAYLOAD |   - |   242 |     - | GIẢ ĐỊNH

====================================================================================
BẢNG AIRTIME LoRa — BW 125 kHz, CR 4/5 (Semtech), evidence=SUY
Là thời gian không khí suy ra từ công thức, KHÔNG phải số đo.
====================================================================================
 SF | khung      |  byte |  airtime ms |  khung/s | evidence
------------------------------------------------------------
  7 | SOS        |    36 |      77.1 ms |    12.98 | evidence=SUY
  7 | HEARTBEAT  |    14 |      46.3 ms |    21.58 | evidence=SUY
  7 | BEACON     |    18 |      51.5 ms |    19.43 | evidence=SUY
  7 | ACK        |    12 |      41.2 ms |    24.26 | evidence=SUY
  9 | SOS        |    36 |     267.3 ms |     3.74 | evidence=SUY
  9 | HEARTBEAT  |    14 |     164.9 ms |     6.07 | evidence=SUY
  9 | BEACON     |    18 |     185.3 ms |     5.40 | evidence=SUY
  9 | ACK        |    12 |     144.4 ms |     6.93 | evidence=SUY
 12 | SOS        |    36 |    1974.3 ms |     0.51 | evidence=SUY
 12 | HEARTBEAT  |    14 |    1155.1 ms |     0.87 | evidence=SUY
 12 | BEACON     |    18 |    1318.9 ms |     0.76 | evidence=SUY
 12 | ACK        |    12 |    1155.1 ms |     0.87 | evidence=SUY

============================================================================================
BẢNG VA CHẠM TOKEN ACK — 24 bit (v2) so với 16 bit (v1)
analytic = SUY (bài toán sinh nhật); MC = SIM (Monte Carlo).
Ghi chú lịch sử: token 16 bit của v1 được chứng minh là sụp ở ≥1000 nút.
============================================================================================
 n nút |    p24 SUY |    p24 SIM |    p16 SUY |    p16 SIM |   vòng
-------------------------------------------------------------------
    10 |   0.000003 |   0.000000 |   0.000686 |   0.002500 |   2000
   100 |   0.000295 |   0.000500 |   0.072749 |   0.071500 |   2000
  1000 |   0.029334 |   0.028000 |   0.999510 |   0.999500 |   2000
 10000 |   0.949204 |   0.940000 |   1.000000 |   1.000000 |    400

LƯU Ý: p24 SIM ở n nhỏ có thể bằng 0 vì xác suất thật nhỏ hơn độ phân
giải của số vòng; cột SUY mới là ước lượng dùng để so sánh.
```

## 3. Ma trận mô phỏng chính (nhãn SIM)

```
[SIM] chạy ma trận 120 ô × 20 seed ...

====================================================================================================
BẢNG TÓM TẮT MÔ PHỎNG MẠNG LoRa — evidence=SIM, CHƯA HIỆU CHUẨN
Trung bình trên mọi mật độ/tải/SF và mọi seed trong ma trận.
====================================================================================================
thuật toán           | start |    PDR |   p50 ms |   p95 ms |  tx/giao |   ctl% |  trùng% |     coll |    hoãn | evidence
-------------------------------------------------------------------------------------------------------------------------
flood                | cold  |  0.705 |    265.3 |    942.9 |    58.35 |  31.88 |   44.27 |    487.7 |     0.0 |      SIM
flood                | warm  |  0.690 |    268.1 |    974.2 |    57.00 |  32.72 |   43.55 |    477.1 |     0.0 |      SIM
managed_flood        | cold  |  0.734 |    363.2 |   1682.8 |    30.08 |  44.25 |   69.26 |    250.5 |     0.0 |      SIM
managed_flood        | warm  |  0.711 |    398.0 |   1589.4 |    29.89 |  45.07 |   69.17 |    245.7 |     0.0 |      SIM
gradient             | cold  |  0.555 |    184.4 |    603.3 |     5.43 |  80.01 |   21.60 |     76.8 |     0.0 |      SIM
gradient             | warm  |  0.589 |    239.1 |    801.0 |     7.90 |  76.27 |   32.29 |     86.6 |     0.0 |      SIM
trickle              | cold  |  0.615 |    273.8 |   2591.8 |    35.36 |  45.53 |   56.50 |    226.9 |     0.0 |      SIM
trickle              | warm  |  0.596 |    305.6 |   2620.3 |    35.33 |  45.98 |   55.75 |    222.3 |     0.0 |      SIM
store_carry_forward  | cold  |  0.757 |    349.9 |   1676.6 |    29.51 |  44.32 |   68.57 |    265.2 |     0.0 |      SIM
store_carry_forward  | warm  |  0.728 |    359.5 |   1737.0 |    30.00 |  45.05 |   69.38 |    259.8 |     0.0 |      SIM
-------------------------------------------------------------------------------------------------------------------------
GHI CHÚ: số liệu mô hình (SIM), phụ thuộc tham số GIẢ ĐỊNH; không phải ĐO.
====================================================================================================

[SIM] raw     : /home/noble-tran/AIforlife/results/sim-lora-raw.csv (2400 dòng)
[SIM] summary : /home/noble-tran/AIforlife/results/sim-lora-summary.csv (120 dòng)
```

## 4. Thí nghiệm trọng tâm E1/E1b/E2/E2b/E3 (nhãn SIM)

```
====================================================================================================
THÍ NGHIỆM TRỌNG TÂM v2.1 — nhãn SIM, CHƯA hiệu chuẩn (cổng G9 chưa đạt)
====================================================================================================

=== e1-control: 54 ô × 20 seed ===
  đã ghi sim-lora-e1-control-raw.csv: 1080 dòng
  đã ghi sim-lora-e1-control-summary.csv: 54 dòng

E1 — mặt phẳng điều khiển × chính sách nghe (trung bình 20 seed, SIM)
chế độ                 chính sách     PDR  điều khiển%   hop%   thức%  bỏ vì ngủ
node_hello             continuous   0.523        46.6%  73.8% 100.00%          0
node_hello             windowed     0.069        72.4%   4.4%   7.41%      10903
node_hello             tx_only      0.000        86.4%   0.0%   0.00%      11610
gateway_beacon         continuous   0.762         1.9%  69.3% 100.00%          0
gateway_beacon         windowed     0.029        12.2%  69.3%   1.51%       1152
gateway_beacon         tx_only      0.000        12.2%   0.0%   0.00%       1380
gateway_beacon_relay   continuous   0.719        31.8%  92.8% 100.00%          0
gateway_beacon_relay   windowed     0.003        78.0%  72.5%   5.01%       1370
gateway_beacon_relay   tx_only      0.000        12.2%   0.0%   0.00%       1380

=== e1b-wide: 6 ô × 20 seed ===
  đã ghi sim-lora-e1b-wide-raw.csv: 120 dòng
  đã ghi sim-lora-e1b-wide-summary.csv: 6 dòng

E1b — vùng rộng 3 km, 100 nút (R3b có phụ thuộc kịch bản?), SIM
                                 ô     PDR  điều khiển%    hop%  phát/giao
              node_hello|flood|3km   0.182        49.2%   44.5%      90.75
           node_hello|gradient|3km   0.275        83.8%   44.5%      11.21
          gateway_beacon|flood|3km   0.352         0.5%   21.0%      87.32
       gateway_beacon|gradient|3km   0.597         3.5%   21.0%       6.69
    gateway_beacon_relay|flood|3km   0.323        19.8%   66.8%      77.40
 gateway_beacon_relay|gradient|3km   0.547        49.9%   66.8%      13.88

=== e2-courier: 8 ô × 20 seed ===
  đã ghi sim-lora-e2-courier-raw.csv: 160 dòng
  đã ghi sim-lora-e2-courier-summary.csv: 8 dòng

E2 — số nút di động (H6), trung bình 20 seed, SIM
               ô     PDR   p95 (s)  phát/giao
     courier0|50   0.573      1.95      26.02
    courier0|100   0.463      1.36      48.96
     courier1|50   0.588      2.79      26.31
    courier1|100   0.470      2.56      48.87
     courier3|50   0.578      2.21      26.46
    courier3|100   0.463      2.61      45.57
    courier10|50   0.568      2.58      29.04
   courier10|100   0.500      2.30      45.13

=== e2b-courier-fair: 4 ô × 20 seed ===
  đã ghi sim-lora-e2b-courier-fair-raw.csv: 80 dòng
  đã ghi sim-lora-e2b-courier-fair-summary.csv: 4 dòng

E2 — số nút di động (H6), trung bình 20 seed, SIM
               ô     PDR   p95 (s)  phát/giao
courier0|3km|900s|xe   0.267      4.63      45.78
courier1|3km|900s|xe   0.297      3.64      41.49
courier3|3km|900s|xe   0.283      4.64      37.37
courier10|3km|900s|xe   0.325      5.02      34.24

=== e3-link: 6 ô × 20 seed ===
  đã ghi sim-lora-e3-link-raw.csv: 120 dòng
  đã ghi sim-lora-e3-link-summary.csv: 6 dòng

E3 — link cá nhân (RQ6), trung bình 20 seed, SIM
                 ô     PDR   p50 (s)  trễ link (s)  mất link
  delay0.0|drop0.0   0.465     0.267         0.000      0.00
 delay0.0|drop0.02   0.473     0.267         0.000      0.65
  delay0.0|drop0.2   0.465     0.267         0.000      5.10
 delay0.05|drop0.0   0.480     0.317         0.050      0.00
delay0.05|drop0.02   0.483     0.317         0.052      0.65
 delay0.05|drop0.2   0.458     0.321         0.063      5.10

GHI CHÚ: mọi số là mô hình (SIM); không dùng để kết luận hiệu năng thực.
```

## 5. Phân tích ghép cặp + Pareto

```
====================================================================================================
H2 — GHÉP CẶP THEO SEED, đối thủ so với flooding (nhãn SIM, CHƯA HIỆU CHUẨN)
====================================================================================================
             đối thủ |  tải |    ô |  thắng |  thua |     ΔPDR |  Δphát/giao | Δđiều khiển
------------------------------------------------------------------------------------------
       managed_flood |    5 |   12 |     63 |    35 |   +0.042 |      -27.83 |     +14.1%
       managed_flood |   20 |   12 |     86 |    94 |   +0.009 |      -27.54 |     +10.6%
            gradient |    5 |   12 |     43 |   115 |   -0.128 |      -52.10 |     +44.0%
            gradient |   20 |   12 |     42 |   168 |   -0.123 |      -49.91 |     +47.6%
             trickle |    5 |   12 |     28 |   100 |   -0.076 |      -18.97 |     +14.0%
             trickle |   20 |   12 |     35 |   181 |   -0.108 |      -25.69 |     +12.9%
 store_carry_forward |    5 |   12 |     93 |    40 |   +0.066 |      -28.46 |     +14.0%
 store_carry_forward |   20 |   12 |    106 |    97 |   +0.024 |      -27.37 |     +10.8%

Diễn giải: 'thắng/thua' đếm theo từng cặp seed (cùng ô). ΔPDR dương nghĩa
là đối thủ giao nhiều hơn flooding. Δphát/giao dương nghĩa là tốn hơn.
Không được trích các số này như kết quả: mô hình chưa hiệu chuẩn (cổng G9).

Đã ghi /home/noble-tran/AIforlife/results/sim-lora-h2-paired.csv (96 dòng, mọi dòng suy ra từ dữ liệu evidence=SIM)

============================================================================================
ĐƯỜNG PARETO — PDR vs số lần phát mỗi SOS giao được (nhãn SIM, CHƯA hiệu chuẩn)
============================================================================================
          thuật toán |     PDR |  phát/giao |  trên biên Pareto
--------------------------------------------------------------------------------------------
 store_carry_forward |   0.743 |      29.76 |              CÓ *
       managed_flood |   0.723 |      29.98 |             KHÔNG
               flood |   0.698 |      57.67 |             KHÔNG
             trickle |   0.606 |      35.34 |             KHÔNG
            gradient |   0.572 |       6.66 |              CÓ *

Đọc bảng: đây là đánh đổi, không phải xếp hạng. Mọi số là `SIM` chưa hiệu
chuẩn; cổng G9 phải đạt trước khi dùng để kết luận.

============================================================================================
H2 SỬA LẠI — PDR theo ô: flood vs gradient (nhãn SIM, CHƯA hiệu chuẩn)
============================================================================================
   n  tải  SF start |   flood  gradient     ΔPDR
------------------------------------------------
  25    5   7  warm |   0.960     0.700   -0.260
  25    5   7  cold |   0.950     0.510   -0.440
  25    5   9  warm |   0.700     0.680   -0.020
  25    5   9  cold |   0.680     0.580   -0.100
  25   20   7  warm |   0.943     0.650   -0.293
  25   20   7  cold |   0.948     0.675   -0.272
  25   20   9  warm |   0.708     0.613   -0.095
  25   20   9  cold |   0.675     0.640   -0.035
  50    5   7  warm |   0.890     0.650   -0.240
  50    5   7  cold |   0.900     0.580   -0.320
  50    5   9  warm |   0.480     0.590   +0.110
  50    5   9  cold |   0.520     0.600   +0.080
  50   20   7  warm |   0.897     0.655   -0.242
  50   20   7  cold |   0.905     0.657   -0.248
  50   20   9  warm |   0.465     0.508   +0.043
  50   20   9  cold |   0.522     0.495   -0.027
 100    5   7  warm |   0.710     0.580   -0.130
 100    5   7  cold |   0.760     0.500   -0.260
 100    5   9  warm |   0.360     0.390   +0.030
 100    5   9  cold |   0.400     0.410   +0.010
 100   20   7  warm |   0.762     0.617   -0.145
 100   20   7  cold |   0.762     0.590   -0.172
 100   20   9  warm |   0.408     0.438   +0.030
 100   20   9  cold |   0.443     0.422   -0.020

Tổng hợp theo SF (ΔPDR = gradient − flood, trung bình mọi ô cùng SF):
  SF7: ΔPDR = -0.252 | gradient thắng 0/12 ô
  SF9: ΔPDR = +0.000 | gradient thắng 6/12 ô

Kết luận SIM (chưa hiệu chuẩn): biến quyết định là AIRTIME MỖI KHUNG, không
phải tải SOS. Muốn phát biểu H2 phải nêu rõ SF/BW.
```

## 6. Tệp kết quả và hash SHA-256

```
sim-lora-e1b-wide-raw.csv                  e64019053d631528
sim-lora-e1b-wide-summary.csv              6c9a9e3eb99b30b0
sim-lora-e1-control-raw.csv                5262b3c689f9b050
sim-lora-e1-control-summary.csv            71a15d29c80334e5
sim-lora-e2b-courier-fair-raw.csv          3d1f745b7db1c55c
sim-lora-e2b-courier-fair-summary.csv      45f78abfd161b034
sim-lora-e2-courier-raw.csv                54806bbe24935ff3
sim-lora-e2-courier-summary.csv            9876d021117b484f
sim-lora-e3-link-raw.csv                   bc502590b9788824
sim-lora-e3-link-summary.csv               97cdaf0a5f6802de
sim-lora-h2-paired.csv                     0bfce61021b2b428
sim-lora-raw.csv                           662deb77be427400
sim-lora-summary.csv                       8fc494971f3600a7
```

> Nhắc lại: mọi số là `SUY` hoặc `SIM`, **chưa hiệu chuẩn** (cổng G9 chưa đạt).
> Không được trích như kết quả thực nghiệm.
