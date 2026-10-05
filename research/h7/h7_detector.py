"""H7 — phát hiện "chìm / bị cuốn" bằng barometer + IMU của điện thoại.

Nguyên lý (`SUY` vật lý, chắc): áp suất thủy tĩnh tăng ~9,8 kPa/m nước
=> ~1 hPa mỗi 1 cm nước dưới mực nước. Barometer điện thoại đo được mức này.
Chữ ký "chìm/bị cuốn": áp suất TĂNG nhanh + liên tục, đồng thời IMU hỗn loạn
(lộn vòng trong nước), không phải dáng đi tuần hoàn.

Các hằng số dưới đây là `TK` (đặt trước, chưa `ĐO`): phải hiệu chuẩn lại trên
máy thật (mốc Pixel 6 Pro, bồn nước) trước khi tuyên bố bất cứ hiệu năng nào.

Chạy được độc lập, chỉ phụ thuộc numpy — dễ chuyển sang Kotlin cho app.
"""

import numpy as np

# --- Hằng số thiết kế (`TK`, chờ hiệu chuẩn G-H7 trên máy thật) -------------
RISE_RATE_MIN_HPA_S = 2.0    # chìm ≥2 cm/s mới tính là nghi ngờ
CONFIRM_DPA = 15.0           # cộng dồn +15 hPa ≈ đang sâu ≥15 cm dưới nước
CONFIRM_S = 3.0              # duy trì ≥3 s
CHURN_GYRO_STD = 80.0        # std vận tốc góc (°/s) 3 s — lộn/tumble trong nước
RESET_DPA = 3.0              # áp suất về gần mốc gốc ±3 hPa => thoát nghi ngờ
COOLDOWN_S = 30.0            # sau alarm, không báo lại trong 30 s

G_WATER_HPA_PER_CM = 0.981   # 9.81 kPa/m = 0.981 hPa/cm


class H7Detector:
    """Máy trạng thái dòng: NORMAL -> SUSPECT -> ALARM.

    push() nhận MỘT bước (khung 1 s tổng hợp): áp suất hPa, |gia tốc| g,
    std vận tốc góc trong bước (°/s). Trả về trạng thái sau bước.
    """

    def __init__(self):
        self.state = "NORMAL"
        self.t = 0.0
        self.suspect_since = None
        self.dpa = 0.0                 # Δp cộng dồn từ khi nghi ngờ
        self.p_ref = None              # áp suất gốc gần nhất
        self.last_alarm_t = -1e9

    def push(self, dt, p_hpa, accel_g, gyro_std):
        self.t += dt
        if self.p_ref is None:
            self.p_ref = p_hpa
            return self.state

        if self.state == "NORMAL":
            rate = (p_hpa - self.p_ref) / dt
            if rate >= RISE_RATE_MIN_HPA_S and gyro_std >= CHURN_GYRO_STD:
                self.state = "SUSPECT"
                self.suspect_since = self.t
                self.dpa = p_hpa - self.p_ref
            else:
                self.p_ref = p_hpa
            return self.state

        if self.state == "SUSPECT":
            self.dpa = p_hpa - self.p_ref
            churn_ok = gyro_std >= CHURN_GYRO_STD * 0.5
            deep_ok = self.dpa >= CONFIRM_DPA
            long_ok = (self.t - self.suspect_since) >= CONFIRM_S
            fell_back = p_hpa <= self.p_ref + RESET_DPA
            if deep_ok and long_ok and churn_ok:
                self.state = "ALARM"
                self.last_alarm_t = self.t
                return self.state
            if fell_back or (not churn_ok and self.dpa < CONFIRM_DPA * 0.5):
                self.state = "NORMAL"
                self.p_ref = p_hpa
            return self.state

        # ALARM — giữ trạng thái, ghi đè mốc gốc để tính lại từ đầu khi về bình thường
        if p_hpa <= self.p_ref + RESET_DPA and self.t - self.last_alarm_t >= COOLDOWN_S:
            self.state = "NORMAL"
            self.p_ref = p_hpa
        return self.state


# --- Sinh luồng giả lập + kiểm thử ------------------------------------------

def _gyro_std_of(t, kind, rng):
    if kind == "tumble":        # lộn trong nước
        return rng.uniform(120, 320)
    if kind == "gait":          # dáng đi ~1,5 Hz
        return 45.0
    return 8.0                  # gần như đứng yên


def simulate(kind, dur_s=20.0, seed=0, sink_cm_per_s=0.0, depth_cm=0.0):
    """Trả mảng (t, p_hpa, |a|_g, gyro_std) theo kịch bản."""
    rng = np.random.default_rng(seed)
    n = int(dur_s)
    t = np.arange(n, dtype=float)
    p = np.full(n, 1013.25)
    a = np.full(n, 1.0)
    gkind = "still"
    if kind == "walk":
        gkind = "gait"
        a += 0.15 * np.abs(np.sin(2 * np.pi * 1.5 * t)) + rng.normal(0, 0.03, n)
        p += rng.normal(0, 0.4, n)                      # ±0,4 hPa wobble
    elif kind == "fall_ground":
        a[8:10] += rng.uniform(3.0, 5.0)                # spike va đập
        p += rng.normal(0, 0.4, n)
    elif kind == "elevator_down":
        # xuống 9 m trong 10 s => −88 hPa, IMU gần như yên
        p -= np.where(t < 10, t * 8.8, 88.0)
        p += rng.normal(0, 0.3, n)
    elif kind == "rain_in_bag":
        p += rng.normal(0, 0.8, n) + 0.5 * np.sin(2 * np.pi * 0.2 * t)
        a += 0.05 * rng.normal(0, 1, n)
        gkind = "gait"
    elif kind == "wade_phone_above_water":
        gkind = "gait"
        a += 0.2 * np.abs(np.sin(2 * np.pi * 1.2 * t)) + rng.normal(0, 0.04, n)
        p += rng.normal(0, 0.4, n)
    elif kind == "sink":
        # bắt đầu chìm ở giây 5, xuống depth_cm với tốc độ cố định
        gkind = "tumble"
        start = 5
        rate = sink_cm_per_s * G_WATER_HPA_PER_CM
        for i in range(start, n):
            p[i] = p[start - 1] + rate * (i - start + 1)
        p += rng.normal(0, 0.4, n)
        a += 0.4 * rng.normal(0, 1, n)
    return t, p, a, np.array([_gyro_std_of(x, gkind, rng) for x in t])
