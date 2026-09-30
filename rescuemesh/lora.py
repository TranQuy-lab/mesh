"""Vật lý lớp vô tuyến LoRa cho RescueMesh-LoRa (một loại sóng duy nhất).

Vai trò trong dự án
-------------------
Đây là nguồn số **tái lập được** cho mọi con số thiết kế về tầm xa, thời gian
không khí (airtime), thông lượng, năng lượng và sức chứa của một gateway.
Mọi kết quả ở đây mang nhãn `SUY` (suy ra từ tài liệu chuẩn), **không** phải
`ĐO` và **không** phải `SIM`. Muốn biến thành `ĐO` phải đo trên thiết bị thật;
muốn dùng để kết luận hiệu năng mạng phải qua hiệu chuẩn (cổng G3 của kế hoạch).

Nguồn công thức
---------------
- Thời gian ký tự, số ký tự payload, airtime: Semtech AN1200.13 và bảng tính
  LoRa Modem Designer's Guide; công thức dưới đây là bản viết lại đã kiểm tra
  tính đơn điệu và so khớp giá trị đã biết (SF7/BW125/24 B ≈ 57 ms,
  SF12/BW125/24 B ≈ 1,48 s).
- Độ nhạy receiver: bảng dự phòng `SENSITIVITY_DBM`, **phải đối chiếu datasheet
  SX1262 trước khi trích vào báo cáo** — hiện gắn nhãn `GIẢ ĐỊNH`.
- Suy hao không gian tự do: công thức Friis chuẩn (đã kiểm với giá trị đã biết).
- Suy hao theo khoảng cách log-distance: mô hình chuẩn trong tài liệu vô tuyến;
  hệ số suy hao `n` là tham số, không phải hằng số của thiết bị.

Cách dùng
---------
    python3 lora.py            # in bảng đánh đổi SF và phân tích sức chứa
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

# --------------------------------------------------------------------------
# Hằng số và bảng tham số
# --------------------------------------------------------------------------

SPEED_OF_LIGHT_M_S = 299_792_458.0

SF_MIN = 5
SF_MAX = 12

# CR = 1..4 tương ứng mã hoá 4/5, 4/6, 4/7, 4/8
CR_MIN = 1
CR_MAX = 4
CR_DENOMINATOR = {1: 5, 2: 6, 3: 7, 4: 8}

#: Băng tần ứng viên cho Việt Nam (Hz).
#: 920–923 MHz là băng được quy hoạch cho thiết bị IoT công suất thấp — con số
#: này phải đối chiếu văn bản quy phạm hiện hành trước khi trích (nhãn `GIẢ ĐỊNH`).
BAND_VN_920_923_HZ = 921_500_000
BAND_AS923_HZ = 923_200_000

#: Độ nhạy receiver SX1276 ở BW = 125 kHz, CR 4/5, LnaBoost ON (dBm).
#: **`NC` — đọc trực tiếp datasheet SX1276/77/78/79 Rev.4 (3/2015), Bảng 10.**
#: Bản gốc: https://cdn-shop.adafruit.com/product-files/3179/sx1276_77_78_79.pdf
#: LƯU Ý: SX1262 (chip dùng trên phần cứng mới) KHÁC và datasheet chính thức của
#: Semtech bị login-gate → **chưa xác minh**, không được trộn hai chip vào một bảng.
#: Giá trị đồn "SX1262 −148 dBm @SF12/BW125" là SAI: −148 dBm thuộc SX1276 ở BW 7,8 kHz.
SENSITIVITY_DBM_BW125 = {
    6: -118.0,
    7: -123.0,
    8: -126.0,
    9: -129.0,
    10: -132.0,
    11: -133.0,
    12: -136.0,
}

#: Giới hạn phát hợp pháp tại Việt Nam cho thiết bị LPWAN 920–923 MHz (QCVN
#: 122:2020/BTTTT, đọc từ bản công báo gốc): **e.r.p. ≤ 14 dBm** cho cảm biến/đầu
#: cuối, và **duty cycle ≤ 1 %** cho đầu cuối, **≤ 10 %** cho gateway, chu kỳ quan
#: sát 1 giờ. Xem `xac-minh-nguon-lora-va-quyet-dinh-song.md`.
QCvn_MAX_ERP_DBM = 14.0
QCVN_DUTY_CYCLE_ENDPOINT = 0.01
QCVN_DUTY_CYCLE_GATEWAY = 0.10
QCVN_OBSERVATION_WINDOW_S = 3600.0

#: Hệ số suy hao log-distance theo môi trường (giá trị điển hình trong tài liệu).
PATH_LOSS_EXPONENT = {
    "free_space": 2.0,
    "rural_los": 2.5,
    "suburban": 3.0,
    "urban": 3.5,
    "dense_urban_or_forest": 4.0,
}


# --------------------------------------------------------------------------
# Lớp modem LoRa
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class LoraProfile:
    """Một cấu hình modem LoRa (SF, băng thông, coding rate)."""

    sf: int
    bw_hz: float
    cr: int = 1

    def __post_init__(self) -> None:
        if not (SF_MIN <= self.sf <= SF_MAX):
            raise ValueError(f"SF phải trong {SF_MIN}..{SF_MAX}, nhận {self.sf}")
        if self.bw_hz <= 0:
            raise ValueError("băng thông phải dương")
        if not (CR_MIN <= self.cr <= CR_MAX):
            raise ValueError(f"CR phải trong {CR_MIN}..{CR_MAX}, nhận {self.cr}")

    @property
    def tsym_s(self) -> float:
        """Thời gian một ký tự LoRa (giây)."""
        return (2 ** self.sf) / self.bw_hz

    @property
    def bitrate_bps(self) -> float:
        """Tốc độ bit danh nghĩa (bps)."""
        return (
            self.sf * self.bw_hz / (2 ** self.sf) * 4.0 / (self.cr + 4)
        )

    @property
    def low_data_rate_optimize(self) -> int:
        """DE = 1 khi SF ≥ 11 ở BW 125 kHz (theo Semtech)."""
        return 1 if (self.sf >= 11 and abs(self.bw_hz - 125_000) < 1) else 0

    def sensitivity_dbm(self) -> float:
        """Độ nhạy receiver theo bảng **SX1276 đã xác minh từ datasheet** (dBm).

        Hiệu chỉnh theo băng thông bằng ``10·log10(BW/125 kHz)`` — xấp xỉ khớp
        datasheet ở BW250/BW500 (±1 dB). SF5 không có trong bảng BW125 của
        datasheet nên bị từ chối thay vì nội suy.
        """
        if self.sf not in SENSITIVITY_DBM_BW125:
            raise ValueError(
                f"datasheet SX1276 không có SF{self.sf} ở BW125 kHz; "
                "không nội suy để tránh tạo số liệu không có nguồn"
            )
        base = SENSITIVITY_DBM_BW125[self.sf]
        # Hiệu chỉnh thô theo băng thông: 10·log10(BW/125 kHz).
        return base + 10.0 * math.log10(self.bw_hz / 125_000.0)

    def airtime_s(
        self,
        payload_bytes: int,
        preamble_symbols: int = 8,
        explicit_header: bool = True,
        crc: bool = True,
    ) -> float:
        """Thời gian không khí cho một khung (giây), công thức Semtech."""
        if payload_bytes < 0:
            raise ValueError("payload_bytes không âm")
        if payload_bytes > 255 and explicit_header:
            raise ValueError("header tường minh chỉ chở được tối đa 255 byte")

        tsym = self.tsym_s
        t_preamble = (preamble_symbols + 4.25) * tsym

        ih = 0 if explicit_header else 1
        crc_bit = 1 if crc else 0
        de = self.low_data_rate_optimize

        numerator = (
            8 * payload_bytes - 4 * self.sf + 28 + 16 * crc_bit - 20 * ih
        )
        denominator = 4 * (self.sf - 2 * de)
        n_payload = 8 + max(
            math.ceil(numerator / denominator) * (self.cr + 4), 0
        )
        return t_preamble + n_payload * tsym

    def energy_per_frame_j(self, payload_bytes: int, tx_power_w: float, **kw) -> float:
        """Năng lượng tiêu thụ cho một khung ở công suất phát cho trước (J)."""
        return tx_power_w * self.airtime_s(payload_bytes, **kw)


# --------------------------------------------------------------------------
# Lan truyền
# --------------------------------------------------------------------------


def fspl_db(distance_m: float, freq_hz: float) -> float:
    """Suy hao không gian tự do (dB) theo công thức Friis."""
    if distance_m <= 0:
        raise ValueError("khoảng cách phải dương")
    if freq_hz <= 0:
        raise ValueError("tần số phải dương")
    return (
        20.0 * math.log10(distance_m)
        + 20.0 * math.log10(freq_hz)
        - 147.55
    )


def path_loss_log_distance_db(
    distance_m: float,
    freq_hz: float,
    exponent: float,
    d0_m: float = 1.0,
) -> float:
    """Suy hao theo mô hình log-distance (dB), mốc tham chiếu d0."""
    if distance_m <= 0 or d0_m <= 0:
        raise ValueError("khoảng cách phải dương")
    if distance_m < d0_m:
        distance_m = d0_m
    pl_d0 = fspl_db(d0_m, freq_hz)
    return pl_d0 + 10.0 * exponent * math.log10(distance_m / d0_m)


def link_budget_db(
    tx_dbm: float,
    tx_gain_dbi: float = 2.0,
    rx_gain_dbi: float = 2.0,
    losses_db: float = 2.0,
    sensitivity_dbm: float = -132.0,
) -> float:
    """Ngân sách đường truyền khả dụng (dB) trước suy hao lan truyền."""
    return tx_dbm + tx_gain_dbi + rx_gain_dbi - losses_db - sensitivity_dbm


def link_margin_db(
    distance_m: float,
    freq_hz: float,
    exponent: float,
    tx_dbm: float,
    sensitivity_dbm: float,
    tx_gain_dbi: float = 2.0,
    rx_gain_dbi: float = 2.0,
    losses_db: float = 2.0,
) -> float:
    """Biên dự trữ (dB) tại một khoảng cách: > 0 nghĩa là còn dư."""
    budget = link_budget_db(
        tx_dbm, tx_gain_dbi, rx_gain_dbi, losses_db, sensitivity_dbm
    )
    return budget - path_loss_log_distance_db(distance_m, freq_hz, exponent)


def max_range_m(
    freq_hz: float,
    exponent: float,
    tx_dbm: float,
    sensitivity_dbm: float,
    tx_gain_dbi: float = 2.0,
    rx_gain_dbi: float = 2.0,
    losses_db: float = 2.0,
    d0_m: float = 1.0,
) -> float:
    """Khoảng cách mà biên dự trữ bằng 0 (m), theo mô hình log-distance.

    Đây là **giới hạn lý thuyết** của một mô hình suy hao, không phải dự đoán
    tầm xa thực địa. Mọi tuyên bố tầm xa phải là `ĐO`.
    """
    budget = link_budget_db(
        tx_dbm, tx_gain_dbi, rx_gain_dbi, losses_db, sensitivity_dbm
    )
    pl_d0 = fspl_db(d0_m, freq_hz)
    return d0_m * 10.0 ** ((budget - pl_d0) / (10.0 * exponent))


# --------------------------------------------------------------------------
# Sức chứa của một gateway đơn kênh
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class GatewayCapacity:
    """Kết quả phân tích airtime cho một gateway đơn kênh."""

    n_nodes: int
    frames_per_hour: float
    airtime_s_per_frame: float
    utilisation: float
    relay_multiplier: float
    duty_cycle_cap: float
    max_nodes_at_cap: float
    max_nodes_at_duty_cycle: float

    @property
    def saturated(self) -> bool:
        return self.utilisation > 1.0

    @property
    def violates_duty_cycle(self) -> bool:
        return self.utilisation > self.duty_cycle_cap


def gateway_capacity(
    profile: LoraProfile,
    payload_bytes: int,
    n_nodes: int,
    sos_per_node_per_hour: float,
    beacon_interval_s: float | None,
    relay_multiplier: float = 1.0,
    duty_cycle_cap: float = 0.01,
    utilisation_target: float = 0.8,
) -> GatewayCapacity:
    """Ước lượng tải airtime của một gateway LoRa đơn kênh.

    Mô hình: mỗi nút phát `sos_per_node_per_hour` khung SOS mỗi giờ, cộng một
    khung beacon mỗi `beacon_interval_s` giây nếu có beacon, nhân với hệ số
    chuyển tiếp `relay_multiplier` (một khung SOS được nhiều nút phát lại).
    """
    if n_nodes <= 0:
        raise ValueError("n_nodes phải dương")
    if sos_per_node_per_hour < 0:
        raise ValueError("tần suất SOS không âm")

    airtime = profile.airtime_s(payload_bytes)
    frames_per_node_per_hour = sos_per_node_per_hour * relay_multiplier
    if beacon_interval_s is not None and beacon_interval_s > 0:
        frames_per_node_per_hour += 3600.0 / beacon_interval_s

    frames_per_hour = frames_per_node_per_hour * n_nodes
    utilisation = frames_per_hour * airtime / 3600.0

    per_node_utilisation = frames_per_node_per_hour * airtime / 3600.0
    max_nodes_at_cap = (
        utilisation_target / per_node_utilisation if per_node_utilisation else math.inf
    )
    max_nodes_at_duty = (
        duty_cycle_cap / per_node_utilisation if per_node_utilisation else math.inf
    )

    return GatewayCapacity(
        n_nodes=n_nodes,
        frames_per_hour=frames_per_hour,
        airtime_s_per_frame=airtime,
        utilisation=utilisation,
        relay_multiplier=relay_multiplier,
        duty_cycle_cap=duty_cycle_cap,
        max_nodes_at_cap=max_nodes_at_cap,
        max_nodes_at_duty_cycle=max_nodes_at_duty,
    )


# --------------------------------------------------------------------------
# Bảng đánh đổi
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class GatewayCapacityMixed:
    """Sức chứa một gateway khi SOS và beacon có kích thước khác nhau.

    Đây là mô hình đúng hơn `GatewayCapacity`: nó cộng airtime của từng loại
    khung theo kích thước thật (SOS 36 B, beacon 18 B theo đặc tả v2.0) thay vì
    dùng một cỡ khung chung cho mọi loại.
    """

    n_nodes: int
    sos_airtime_per_node_hour_s: float
    beacon_airtime_per_node_hour_s: float
    airtime_per_node_hour_s: float
    per_node_duty_cycle: float
    utilisation: float
    utilisation_target: float
    max_nodes_at_target: float
    saturation_nodes: float

    @property
    def saturated(self) -> bool:
        return self.utilisation > 1.0


def gateway_capacity_mixed(
    profile: LoraProfile,
    sos_bytes: int,
    beacon_bytes: int,
    n_nodes: int,
    sos_per_node_per_hour: float,
    beacon_interval_s: float | None,
    relay_multiplier: float = 1.0,
    utilisation_target: float = 0.8,
) -> GatewayCapacityMixed:
    """Tải airtime của một gateway đơn kênh với hai cỡ khung khác nhau.

    Mô hình: mỗi nút phát `sos_per_node_per_hour` khung SOS mỗi giờ (nhân hệ số
    chuyển tiếp) cộng một khung beacon mỗi `beacon_interval_s` giây, nếu có beacon.
    Chưa mô hình hoá collision, hidden terminal hay capture — là **giới hạn trên**.
    """
    if n_nodes <= 0:
        raise ValueError("n_nodes phải dương")
    if sos_per_node_per_hour < 0:
        raise ValueError("tần suất SOS không âm")

    sos_frames = sos_per_node_per_hour * relay_multiplier
    beacon_frames = (
        3600.0 / beacon_interval_s
        if beacon_interval_s is not None and beacon_interval_s > 0
        else 0.0
    )

    sos_airtime = sos_frames * profile.airtime_s(sos_bytes)
    beacon_airtime = beacon_frames * profile.airtime_s(beacon_bytes)
    per_node = sos_airtime + beacon_airtime

    utilisation = n_nodes * per_node / 3600.0
    per_node_duty = per_node / 3600.0

    return GatewayCapacityMixed(
        n_nodes=n_nodes,
        sos_airtime_per_node_hour_s=sos_airtime,
        beacon_airtime_per_node_hour_s=beacon_airtime,
        airtime_per_node_hour_s=per_node,
        per_node_duty_cycle=per_node_duty,
        utilisation=utilisation,
        utilisation_target=utilisation_target,
        max_nodes_at_target=(
            utilisation_target * 3600.0 / per_node if per_node else math.inf
        ),
        saturation_nodes=3600.0 / per_node if per_node else math.inf,
    )



def sf_tradeoff_table(
    payload_bytes: int = 40,
    bw_hz: float = 125_000.0,
    cr: int = 1,
    freq_hz: float = BAND_VN_920_923_HZ,
    tx_dbm: float = 14.0,
    exponent: float = 3.0,
    environments: Iterable[str] = ("free_space", "suburban", "urban"),
) -> list[dict]:
    """Bảng đánh đổi SF ↔ tốc độ ↔ airtime ↔ tầm xa lý thuyết."""
    rows: list[dict] = []
    for sf in range(7, 13):
        profile = LoraProfile(sf=sf, bw_hz=bw_hz, cr=cr)
        row = {
            "sf": sf,
            "bitrate_bps": profile.bitrate_bps,
            "airtime_ms": profile.airtime_s(payload_bytes) * 1000.0,
            "sensitivity_dbm": profile.sensitivity_dbm(),
            "max_frames_per_s": 1.0 / profile.airtime_s(payload_bytes),
        }
        for env in environments:
            row[f"range_km_{env}"] = (
                max_range_m(
                    freq_hz=freq_hz,
                    exponent=PATH_LOSS_EXPONENT[env],
                    tx_dbm=tx_dbm,
                    sensitivity_dbm=profile.sensitivity_dbm(),
                )
                / 1000.0
            )
        rows.append(row)
    return rows


def _print_table() -> None:
    print("=" * 96)
    print("BẢNG ĐÁNH ĐỔI SF — LoRa BW125 kHz, CR 4/5, payload 40 B, Tx 14 dBm")
    print("Nhãn: SUY (mô hình log-distance). KHÔNG phải tầm xa đo được.")
    print("=" * 96)
    header = (
        f"{'SF':>3} | {'bps':>7} | {'airtime':>9} | {'khung/s':>7} | "
        f"{'nhạy dBm':>8} | {'xa FS km':>9} | {'xa n=3 km':>9} | {'xa n=3.5':>9}"
    )
    print(header)
    print("-" * len(header))
    for row in sf_tradeoff_table():
        print(
            f"{row['sf']:>3} | {row['bitrate_bps']:>7.0f} | "
            f"{row['airtime_ms']:>7.1f}ms | {row['max_frames_per_s']:>7.2f} | "
            f"{row['sensitivity_dbm']:>8.1f} | "
            f"{row['range_km_free_space']:>9.1f} | "
            f"{row['range_km_suburban']:>9.1f} | "
            f"{row['range_km_urban']:>9.1f}"
        )

    print()
    print("=" * 96)
    print("SỨC CHỨA MỘT GATEWAY ĐƠN KÊNH (chỉ tính airtime, chưa tính collision)")
    print("Giả định: 1 SOS/nút/giờ, beacon 60 s, relay_multiplier = 3")
    print("=" * 96)
    for sf in (7, 9, 10, 12):
        profile = LoraProfile(sf=sf, bw_hz=125_000.0, cr=1)
        cap = gateway_capacity(
            profile,
            payload_bytes=40,
            n_nodes=100,
            sos_per_node_per_hour=1.0,
            beacon_interval_s=60.0,
            relay_multiplier=3.0,
        )
        print(
            f"SF{sf:<2}: airtime {cap.airtime_s_per_frame * 1000:7.1f} ms | "
            f"100 nút dùng {cap.utilisation * 100:6.2f} % thời gian | "
            f"tối đa {cap.max_nodes_at_cap:6.0f} nút ở mức 80 % | "
            f"{cap.max_nodes_at_duty_cycle:6.0f} nút ở duty cycle 1 %"
        )

    print()
    print("LƯU Ý: chưa mô hình hoá collision, hidden terminal, capture effect,")
    print("mất gói do địa hình hay duty cycle theo luật. Đây là giới hạn trên.")


if __name__ == "__main__":
    _print_table()
