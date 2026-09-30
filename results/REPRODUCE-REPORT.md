# Báo cáo tái lập RescueMesh-LoRa

- Thời điểm chạy (UTC): `2026-09-30T17:38:06Z`
- Python: `Python 3.12.3`
- Máy: `Linux x86_64`

## 1. Kiểm thử

```
test_lora.py               32/32 test qua
test_node_power.py         19/19 test qua
test_packets.py            15/15 test qua
test_packets_lora.py       43/43 test qua
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
flood                | cold  |  0.849 |    246.3 |   1041.0 |    58.97 |  27.34 |   46.16 |    765.8 |     0.0 |      SIM
flood                | warm  |  0.840 |    250.4 |   1035.2 |    59.37 |  27.47 |   46.19 |    762.2 |     0.0 |      SIM
managed_flood        | cold  |  0.862 |    328.5 |   1826.4 |    29.97 |  39.79 |   74.31 |    448.4 |     0.0 |      SIM
managed_flood        | warm  |  0.858 |    334.2 |   1849.8 |    29.92 |  39.99 |   74.48 |    447.6 |     0.0 |      SIM
gradient             | cold  |  0.616 |    172.8 |    255.7 |     2.18 |  89.60 |    3.25 |    234.7 |     0.0 |      SIM
gradient             | warm  |  0.627 |    177.8 |    282.0 |     2.44 |  88.69 |    5.16 |    236.1 |     0.0 |      SIM
trickle              | cold  |  0.735 |    308.5 |   2783.1 |    33.50 |  41.35 |   65.77 |    410.4 |     0.0 |      SIM
trickle              | warm  |  0.740 |    320.1 |   2806.2 |    33.44 |  41.34 |   65.70 |    411.1 |     0.0 |      SIM
store_carry_forward  | cold  |  0.863 |    318.5 |   1634.7 |    30.33 |  40.50 |   74.48 |    472.8 |     0.0 |      SIM
store_carry_forward  | warm  |  0.873 |    334.2 |   1752.9 |    30.07 |  40.37 |   73.91 |    474.9 |     0.0 |      SIM
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
node_hello             continuous   0.703        50.6%   1.8% 100.00%          0
node_hello             windowed     0.023        82.1%   1.8%   6.65%       1106
node_hello             tx_only      0.000        86.4%   0.0%   0.00%       1158
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
              node_hello|flood|3km   0.350        33.4%    0.7%      90.24
           node_hello|gradient|3km   0.212        92.5%    0.7%       5.49
          gateway_beacon|flood|3km   0.352         0.5%   21.0%      87.32
       gateway_beacon|gradient|3km   0.597         3.5%   21.0%       6.69
    gateway_beacon_relay|flood|3km   0.323        19.8%   66.8%      77.40
 gateway_beacon_relay|gradient|3km   0.547        49.9%   66.8%      13.88

=== e2-courier: 8 ô × 20 seed ===
  đã ghi sim-lora-e2-courier-raw.csv: 160 dòng
  đã ghi sim-lora-e2-courier-summary.csv: 8 dòng

E2 — số nút di động (H6), trung bình 20 seed, SIM
               ô     PDR   p95 (s)  phát/giao
     courier0|50   0.802      2.44      25.28
    courier0|100   0.672      2.39      50.69
     courier1|50   0.790      2.32      25.85
    courier1|100   0.708      2.57      48.41
     courier3|50   0.782      2.14      26.99
    courier3|100   0.767      2.26      46.01
    courier10|50   0.765      2.31      29.84
   courier10|100   0.790      2.96      47.52

=== e2b-courier-fair: 4 ô × 20 seed ===
  đã ghi sim-lora-e2b-courier-fair-raw.csv: 80 dòng
  đã ghi sim-lora-e2b-courier-fair-summary.csv: 4 dòng

E2 — số nút di động (H6), trung bình 20 seed, SIM
               ô     PDR   p95 (s)  phát/giao
courier0|3km|900s|xe   0.478      5.60      38.47
courier1|3km|900s|xe   0.478      6.52      38.15
courier3|3km|900s|xe   0.515      6.62      36.06
courier10|3km|900s|xe   0.532      6.20      36.09

=== e3-link: 12 ô × 20 seed ===
  đã ghi sim-lora-e3-link-raw.csv: 240 dòng
  đã ghi sim-lora-e3-link-summary.csv: 12 dòng

E3 — link cá nhân (RQ6), trung bình 20 seed, SIM
                 ô     PDR   p50 (s)  trễ link (s)  mất link
delay0.000|drop0.00   0.685     0.267         0.000      0.00
delay0.000|drop0.01   0.685     0.267         0.000      0.20
delay0.000|drop0.10   0.662     0.267         0.000      2.35
delay0.015|drop0.00   0.685     0.282         0.015      0.00
delay0.015|drop0.01   0.685     0.282         0.015      0.20
delay0.015|drop0.10   0.662     0.282         0.017      2.35
delay0.045|drop0.00   0.685     0.312         0.045      0.00
delay0.045|drop0.01   0.685     0.312         0.045      0.20
delay0.045|drop0.10   0.662     0.312         0.050      2.35
delay0.160|drop0.00   0.690     0.427         0.160      0.00
delay0.160|drop0.01   0.690     0.427         0.162      0.20
delay0.160|drop0.10   0.667     0.427         0.179      2.35

=== e4-beacon-interval: 12 ô × 20 seed ===
  đã ghi sim-lora-e4-beacon-interval-raw.csv: 240 dòng
  đã ghi sim-lora-e4-beacon-interval-summary.csv: 12 dòng

E4 — chi phí điều khiển theo chu kỳ quảng bá (H3 sửa lại), SIM
                           ô    ctl%    PDR   hop%  ctl mỗi nút/giờ  bcn/nút/giờ
        beacon60s|node_hello   94.6%  0.600   0.0%            60.60        60.60
    beacon60s|gateway_beacon    3.0%  0.653  69.1%             0.60         0.60
  beacon60s|adaptive_gateway    0.3%  0.818  69.1%             0.12         0.12
       beacon300s|node_hello   93.3%  0.637   0.0%            14.54        14.54
   beacon300s|gateway_beacon    1.2%  0.710   0.0%             0.14         0.14
 beacon300s|adaptive_gateway    0.3%  0.710   0.0%             0.04         0.04
      beacon3600s|node_hello   91.3%  0.647   0.0%             1.36         1.36
  beacon3600s|gateway_beacon    9.4%  0.708   0.0%             0.01         0.01
beacon3600s|adaptive_gateway    3.4%  0.708   0.0%             0.00         0.00
     beacon10800s|node_hello   87.5%  0.647   0.0%             0.32         0.32
 beacon10800s|gateway_beacon    6.5%  0.708   0.0%             0.00         0.00
beacon10800s|adaptive_gateway    3.4%  0.708   0.0%             0.00         0.00

GHI CHÚ: mọi số là mô hình (SIM); không dùng để kết luận hiệu năng thực.
```

## 5. Phân tích ghép cặp + Pareto

```
====================================================================================================
H2 — GHÉP CẶP THEO SEED, đối thủ so với flooding (nhãn SIM, CHƯA HIỆU CHUẨN)
====================================================================================================
             đối thủ |  tải |    ô |  thắng |  thua |     ΔPDR |  Δphát/giao | Δđiều khiển
------------------------------------------------------------------------------------------
       managed_flood |    5 |   12 |     60 |    62 |   +0.023 |      -30.07 |     +15.0%
       managed_flood |   20 |   12 |     92 |   100 |   +0.008 |      -28.38 |     +10.0%
            gradient |    5 |   12 |     33 |   154 |   -0.207 |      -58.06 |     +54.8%
            gradient |   20 |   12 |     33 |   196 |   -0.239 |      -55.66 |     +68.7%
             trickle |    5 |   12 |     36 |    90 |   -0.054 |      -24.44 |     +14.6%
             trickle |   20 |   12 |     19 |   210 |   -0.159 |      -26.95 |     +13.3%
 store_carry_forward |    5 |   12 |     72 |    54 |   +0.028 |      -30.03 |     +16.0%
 store_carry_forward |   20 |   12 |     92 |    97 |   +0.019 |      -27.91 |     +10.1%

Diễn giải: 'thắng/thua' đếm theo từng cặp seed (cùng ô). ΔPDR dương nghĩa
là đối thủ giao nhiều hơn flooding. Δphát/giao dương nghĩa là tốn hơn.
Không được trích các số này như kết quả: mô hình chưa hiệu chuẩn (cổng G9).

Đã ghi /home/noble-tran/AIforlife/results/sim-lora-h2-paired.csv (96 dòng, mọi dòng suy ra từ dữ liệu evidence=SIM)

============================================================================================
ĐƯỜNG PARETO — PDR vs số lần phát mỗi SOS giao được (nhãn SIM, CHƯA hiệu chuẩn)
============================================================================================
          thuật toán |     PDR |  phát/giao |  trên biên Pareto
--------------------------------------------------------------------------------------------
 store_carry_forward |   0.868 |      30.20 |              CÓ *
       managed_flood |   0.860 |      29.94 |              CÓ *
               flood |   0.844 |      59.17 |             KHÔNG
             trickle |   0.738 |      33.47 |             KHÔNG
            gradient |   0.621 |       2.31 |              CÓ *

Đọc bảng: đây là đánh đổi, không phải xếp hạng. Mọi số là `SIM` chưa hiệu
chuẩn; cổng G9 phải đạt trước khi dùng để kết luận.

============================================================================================
H2 SỬA LẠI — PDR theo ô: flood vs gradient (nhãn SIM, CHƯA hiệu chuẩn)
============================================================================================
   n  tải  SF start |   flood  gradient     ΔPDR
------------------------------------------------
  25    5   7  warm |   0.990     0.690   -0.300
  25    5   7  cold |   1.000     0.500   -0.500
  25    5   9  warm |   0.780     0.660   -0.120
  25    5   9  cold |   0.810     0.660   -0.150
  25   20   7  warm |   0.988     0.528   -0.460
  25   20   7  cold |   0.990     0.555   -0.435
  25   20   9  warm |   0.802     0.675   -0.127
  25   20   9  cold |   0.797     0.688   -0.110
  50    5   7  warm |   0.970     0.550   -0.420
  50    5   7  cold |   0.960     0.520   -0.440
  50    5   9  warm |   0.690     0.630   -0.060
  50    5   9  cold |   0.690     0.660   -0.030
  50   20   7  warm |   0.975     0.547   -0.427
  50   20   7  cold |   0.980     0.550   -0.430
  50   20   9  warm |   0.685     0.653   -0.032
  50   20   9  cold |   0.685     0.655   -0.030
 100    5   7  warm |   0.880     0.610   -0.270
 100    5   7  cold |   0.920     0.620   -0.300
 100    5   9  warm |   0.700     0.770   +0.070
 100    5   9  cold |   0.720     0.760   +0.040
 100   20   7  warm |   0.912     0.517   -0.395
 100   20   7  cold |   0.932     0.532   -0.400
 100   20   9  warm |   0.708     0.693   -0.015
 100   20   9  cold |   0.698     0.690   -0.007

Tổng hợp theo SF (ΔPDR = gradient − flood, trung bình mọi ô cùng SF):
  SF7: ΔPDR = -0.398 | gradient thắng 0/12 ô
  SF9: ΔPDR = -0.048 | gradient thắng 2/12 ô

Kết luận SIM (chưa hiệu chuẩn): biến quyết định là AIRTIME MỖI KHUNG, không
phải tải SOS. Muốn phát biểu H2 phải nêu rõ SF/BW.
```

## 6. Tệp kết quả và hash SHA-256

```
sim-lora-e1b-wide-raw.csv                  1af0c05a181b577d
sim-lora-e1b-wide-summary.csv              3aab618b2ed4492c
sim-lora-e1-control-raw.csv                1758ca91c37b88ae
sim-lora-e1-control-summary.csv            a2152d7727b50229
sim-lora-e2b-courier-fair-raw.csv          dc82ee7fca93246b
sim-lora-e2b-courier-fair-summary.csv      67b5d5c6222a1915
sim-lora-e2-courier-raw.csv                16338a2e81f283cc
sim-lora-e2-courier-summary.csv            f23d69b1652979d0
sim-lora-e3-link-raw.csv                   c2cdfe27e187d0cc
sim-lora-e3-link-summary.csv               6465fd2ce7271c81
sim-lora-e4-beacon-interval-raw.csv        9161e4d5322a9fc3
sim-lora-e4-beacon-interval-summary.csv    49ec2c15e8d1cfe1
sim-lora-h2-paired.csv                     d3102677629f51b7
sim-lora-raw.csv                           df132eb9447b2af1
sim-lora-sensitivity.csv                   896430a5ed65a839
sim-lora-summary.csv                       94ae35f1e1b75c43
```

> Nhắc lại: mọi số là `SUY` hoặc `SIM`, **chưa hiệu chuẩn** (cổng G9 chưa đạt).
> Không được trích như kết quả thực nghiệm.
