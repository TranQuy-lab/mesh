"""Ngân sách năng lượng của một nút LoRa trong RescueMesh-LoRa.

Vì sao tệp này tồn tại
----------------------
Khi hệ thống chỉ còn MỘT loại sóng (LoRa) và không còn điện thoại, nút phải
chạy bằng pin trong nhiều tháng. Câu hỏi thiết kế trung tâm là: **pin cạn vì
đâu** — vì phát LoRa, vì luôn nghe kênh, vì cảm biến phát hiện ngã luôn bật,
hay vì GNSS? Tệp này biến câu hỏi đó thành phép tính tái lập được.

Nhãn bằng chứng
---------------
Mọi dòng điện dưới đây là `GIẢ ĐỊNH` lấy từ trí nhớ về datasheet điển hình,
**phải đối chiếu datasheet thật trước khi trích vào báo cáo**. Kết quả tính ra
là `SUY`, không phải `ĐO`. Muốn thành `ĐO` phải đo bằng INA219/otii trên nút
thật (work package WP10 của kế hoạch mới).

Cách dùng
---------
    python3 node_power.py     # in bảng tuổi thọ pin và chi phí mỗi SOS
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from lora import BAND_VN_920_923_HZ, LoraProfile

HOURS_PER_DAY = 24.0
SECONDS_PER_HOUR = 3600.0


@dataclass(frozen=True)
class NodePowerParams:
    """Dòng tiêu thụ của các khối trên nút (mA).

    Nhãn nguồn gốc từng dòng:
    - **`NC` (đã xác minh từ datasheet SX1276 Rev.4, Bảng 10)**: `rx_current_ma`
      = 10,3 mA (Rx LoRa BW125), `tx_current_ma` = 28 mA (Tx 13 dBm), và dòng ngủ
      của radio 0,2 µA (không đáng kể, gộp vào `sleep_current_ma`).
      Lưu ý pháp lý: QCVN 122:2020/BTTTT giới hạn **14 dBm e.r.p.**, nên mức
      PA_BOOST 17 dBm / 90 mA của SX1276 **không dùng được hợp pháp** ở Việt Nam.
    - **`GIẢ ĐỊNH` (chưa đo)**: các dòng còn lại của MCU, IMU, GNSS và mạch nguồn —
      phải đo ở WP10 bằng INA219/otii trước khi trích như kết quả.
    """

    #: ESP32-S3 ở deep sleep (chỉ RTC chạy). `GIẢ ĐỊNH`
    sleep_current_ma: float = 0.010
    #: MCU thức trong lúc chuẩn bị/phát khung. `GIẢ ĐỊNH`
    mcu_active_current_ma: float = 40.0
    #: Cảm biến gia tốc ở chế độ công suất thấp, phát hiện chuyển động bằng ngắt. `GIẢ ĐỊNH`
    imu_low_power_current_ma: float = 0.010
    #: Cảm biến gia tốc ở chế độ lấy mẫu 20–50 Hz khi có sự kiện. `GIẢ ĐỊNH`
    imu_active_current_ma: float = 0.5
    #: Module GNSS trong lúc bắt vệ tinh (hot start). `GIẢ ĐỊNH`
    gnss_fix_current_ma: float = 25.0
    #: SX1276 ở chế độ nhận LoRa BW125. `NC` — datasheet.
    rx_current_ma: float = 10.3
    #: SX1276 ở 13 dBm. `NC` — datasheet (17 dBm cần 90 mA nhưng vượt giới hạn QCVN).
    tx_current_ma: float = 28.0
    #: Dung lượng pin (mAh) — một cell 18650 điển hình. `GIẢ ĐỊNH`
    battery_mah: float = 3000.0
    #: Phần dung lượng dùng được trước khi điện áp tụt dưới ngưỡng hoạt động.
    usable_fraction: float = 0.8
    #: Dòng rò của mạch nguồn (regulator, LED, mạch bảo vệ). `GIẢ ĐỊNH`
    quiescent_current_ma: float = 0.020
    #: Tự xả của pin (% dung lượng mỗi tháng) — với cell 18650 điển hình là 1–3 %.
    self_discharge_percent_per_month: float = 2.0

    def __post_init__(self) -> None:
        for name in (
            "sleep_current_ma",
            "imu_low_power_current_ma",
            "rx_current_ma",
            "tx_current_ma",
            "quiescent_current_ma",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} không được âm")
        if self.battery_mah <= 0:
            raise ValueError("battery_mah phải dương")
        if not (0.0 < self.usable_fraction <= 1.0):
            raise ValueError("usable_fraction phải trong (0, 1]")


@dataclass(frozen=True)
class NodeDutyCycle:
    """Chu kỳ hoạt động của nút (mỗi ngày)."""

    beacon_interval_s: float | None = 300.0
    beacon_bytes: int = 18
    sos_per_day: float = 0.05
    sos_bytes: int = 36
    #: Số lần phát lại trung bình cho mỗi SOS (chuyển tiếp trong mesh).
    relays_per_sos: float = 3.0
    #: Số lần bắt GNSS mỗi ngày (một lần khi khởi động + một lần mỗi SOS).
    gnss_fixes_per_day: float = 1.0
    #: Thời gian mỗi lần bắt GNSS (giây).
    gnss_fix_duration_s: float = 30.0
    #: Phần thời gian nút nghe kênh (0–1). 0 nghĩa là chỉ nghe trong cửa sổ beacon.
    rx_fraction: float = 0.0
    #: Số giờ mỗi ngày cảm biến chạy ở chế độ lấy mẫu cao (kiểm thử, va đập).
    imu_active_hours_per_day: float = 0.0


def frames_per_day(
    profile: LoraProfile,
    duty: NodeDutyCycle,
) -> dict[str, float]:
    """Số khung và tổng airtime mỗi ngày, tách theo loại."""
    beacons = 0.0 if not duty.beacon_interval_s else SECONDS_PER_HOUR * HOURS_PER_DAY / duty.beacon_interval_s
    sos_tx = duty.sos_per_day * (1.0 + duty.relays_per_sos)
    airtime_beacon_s = beacons * profile.airtime_s(duty.beacon_bytes)
    airtime_sos_s = sos_tx * profile.airtime_s(duty.sos_bytes)
    return {
        "beacons_per_day": beacons,
        "sos_transmissions_per_day": sos_tx,
        "airtime_beacon_s": airtime_beacon_s,
        "airtime_sos_s": airtime_sos_s,
        "airtime_total_s": airtime_beacon_s + airtime_sos_s,
    }


def charge_per_day_mah(
    params: NodePowerParams,
    profile: LoraProfile,
    duty: NodeDutyCycle,
) -> dict[str, float]:
    """Điện lượng tiêu thụ mỗi ngày (mAh), tách theo từng khối."""
    frames = frames_per_day(profile, duty)

    # Nền: MCU ngủ + dòng rò mạch nguồn, cả ngày.
    baseline = (params.sleep_current_ma + params.quiescent_current_ma) * HOURS_PER_DAY

    # Cảm biến: chế độ công suất thấp cả ngày, cộng giờ lấy mẫu cao.
    imu = params.imu_low_power_current_ma * HOURS_PER_DAY
    imu += (
        params.imu_active_current_ma - params.imu_low_power_current_ma
    ) * max(0.0, duty.imu_active_hours_per_day)

    # Phát LoRa: dòng phát nhân airtime.
    tx_beacon = params.tx_current_ma * frames["airtime_beacon_s"] / SECONDS_PER_HOUR
    tx_sos = params.tx_current_ma * frames["airtime_sos_s"] / SECONDS_PER_HOUR

    # Nghe kênh liên tục theo phần thời gian đặt trước.
    rx = params.rx_current_ma * HOURS_PER_DAY * min(1.0, max(0.0, duty.rx_fraction))

    # GNSS.
    gnss = (
        params.gnss_fix_current_ma
        * duty.gnss_fixes_per_day
        * duty.gnss_fix_duration_s
        / SECONDS_PER_HOUR
        + params.sleep_current_ma
        * 0.0
    )

    total = baseline + imu + tx_beacon + tx_sos + rx + gnss
    # Tự xả của pin: phần trăm dung lượng mỗi tháng, quy về mAh/ngày.
    self_discharge = (
        params.battery_mah
        * params.self_discharge_percent_per_month
        / 100.0
        / 30.0
    )
    total += self_discharge
    return {
        "baseline": baseline,
        "imu": imu,
        "tx_beacon": tx_beacon,
        "tx_sos": tx_sos,
        "rx": rx,
        "gnss": gnss,
        "self_discharge": self_discharge,
        "total": total,
    }


def duty_cycle_fraction(profile: LoraProfile, duty: NodeDutyCycle) -> float:
    """Phần thời gian phát (0–1) mà nút chiếm kênh — để đối chiếu giới hạn luật.

    Giới hạn thật của Việt Nam ở băng 920–923 MHz phải tra văn bản quy phạm;
    hàm này chỉ trả về con số để so, không khẳng định ngưỡng.
    """
    frames = frames_per_day(profile, duty)
    return frames["airtime_total_s"] / (HOURS_PER_DAY * SECONDS_PER_HOUR)


def battery_life_days(
    params: NodePowerParams,
    profile: LoraProfile,
    duty: NodeDutyCycle,
) -> float:
    """Tuổi thọ pin ước lượng (ngày)."""
    charge = charge_per_day_mah(params, profile, duty)["total"]
    if charge <= 0:
        return math.inf
    return params.battery_mah * params.usable_fraction / charge


def energy_cost_per_delivered_sos_mah(
    params: NodePowerParams,
    profile: LoraProfile,
    duty: NodeDutyCycle,
) -> float:
    """Điện lượng (mAh) tiêu thụ cho mỗi SOS được giao tới trạm.

    Tính cả phát lại trong mesh, một lần bắt GNSS và phần nền suốt thời gian
    chờ. Đây là chỉ số so sánh giữa các cấu hình SF và các thuật toán định tuyến.
    """
    if duty.sos_per_day <= 0:
        return math.inf
    charge = charge_per_day_mah(params, profile, duty)["total"]
    return charge / duty.sos_per_day


def _print_table() -> None:
    params = NodePowerParams()
    duty = NodeDutyCycle()

    print("=" * 100)
    print("PHÂN RÃ ĐIỆN LƯỢNG MỖI NGÀY — nút LoRa một sóng (nhãn: SUY từ GIẢ ĐỊNH)")
    print("Pin 18650 3000 mAh, dùng được 80 %, beacon 5 phút, 0,05 SOS/ngày")
    print("=" * 100)
    header = (
        f"{'SF':>3} | {'airtime beacon':>14} | {'mAh/ngày':>9} | {'tuổi thọ':>10} | "
        f"{'mAh/SOS':>9} | {'duty cycle':>11} | {'chi phối bởi':>20}"
    )
    print(header)
    print("-" * len(header))
    for sf in (7, 9, 12):
        profile = LoraProfile(sf, 125_000, 1)
        parts = charge_per_day_mah(params, profile, duty)
        days = battery_life_days(params, profile, duty)
        cost = energy_cost_per_delivered_sos_mah(params, profile, duty)
        dc = duty_cycle_fraction(profile, duty)
        dominant = max(
            ("nền (ngủ+rò)", parts["baseline"]),
            ("cảm biến", parts["imu"]),
            ("phát beacon", parts["tx_beacon"]),
            ("phát SOS", parts["tx_sos"]),
            ("nghe kênh", parts["rx"]),
            ("GNSS", parts["gnss"]),
            ("tự xả pin", parts["self_discharge"]),
            key=lambda kv: kv[1],
        )[0]
        flag = "!" if dc > 0.01 else " "
        print(
            f"{sf:>3} | {profile.airtime_s(duty.beacon_bytes) * 1000:>11.1f} ms | "
            f"{parts['total']:>9.4f} | {days:>8.0f} ng | {cost:>9.2f} | "
            f"{dc * 100:>9.2f} %{flag} | {dominant:>20}"
        )
    print()
    print("Dấu ! = duty cycle vượt 1 % — ngưỡng của QCVN 122:2020/BTTTT cho đầu cuối")
    print("(đã xác minh từ bản công báo gốc; gateway được 10 %).")

    print()
    print("KỊCH BẢN NGHE KÊNH LIÊN TỤC (rx_fraction = 1.0) VÀ GNSS MỖI NGÀY:")
    for sf in (7, 9, 12):
        profile = LoraProfile(sf, 125_000, 1)
        heavy = NodeDutyCycle(rx_fraction=1.0, gnss_fixes_per_day=24.0)
        parts = charge_per_day_mah(params, profile, heavy)
        days = battery_life_days(params, profile, heavy)
        print(
            f"  SF{sf:<2}: {parts['total']:>7.2f} mAh/ngày "
            f"(nghe {parts['rx']:.2f}, GNSS {parts['gnss']:.2f}) → "
            f"{days:>5.1f} ngày pin"
        )

    print()
    print("KẾT LUẬN THIẾT KẾ (SUY): trên nút một sóng, chi phí vô tuyến rất nhỏ so")
    print("với chi phí luôn-nghe và GNSS. Nút phải ngủ theo lịch và bắt GNSS theo")
    print("sự kiện, nếu không pin cạn trong vài tuần dù gần như không phát gói nào.")
    print("Đây là điều phải ĐO ở WP10, không được trích như kết quả.")


if __name__ == "__main__":
    _print_table()
