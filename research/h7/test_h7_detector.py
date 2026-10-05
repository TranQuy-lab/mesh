"""Kiểm tra H7 detector trên các kịch bản giả lập.

Chạy: python3 -m pytest research/h7/test_h7_detector.py -v
Lưu ý: hằng số trong h7_detector là `TK` — các test này kiểm LOGIC máy trạng
thái, không phải hiệu năng trên người thật (cái đó phải `ĐO` trên máy thật).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from h7_detector import H7Detector, simulate  # noqa: E402


def run_stream(kind, **kw):
    det = H7Detector()
    states = []
    t, p, a, g = simulate(kind, **kw)
    for i in range(len(t)):
        dt = 1.0 if i == 0 else t[i] - t[i - 1]
        states.append(det.push(dt, p[i], a[i], g[i]))
    return states


def test_sink_slow_alarm():
    # chìm 10 cm/s từ giây 5 => ~15 s sau đạt +15 hPa, lộn trong nước
    states = run_stream("sink", dur_s=25, sink_cm_per_s=10.0)
    assert states[-1] == "ALARM"
    assert "ALARM" not in states[:8]      # trước khi chìm không báo


def test_sink_fast_alarm():
    # bị cuốn: 50 cm/s
    states = run_stream("sink", dur_s=15, sink_cm_per_s=50.0)
    assert states[-1] == "ALARM"
    assert "ALARM" not in states[:8]


def test_walk_no_alarm():
    states = run_stream("walk", dur_s=60)
    assert set(states) == {"NORMAL"}


def test_fall_on_ground_no_alarm():
    # va đập mạnh nhưng áp suất không đổi => không phải chìm nước
    states = run_stream("fall_ground", dur_s=30)
    assert set(states) == {"NORMAL"}


def test_elevator_down_no_alarm():
    # Δp lớn nhưng SLOW và không có churn => không nghi ngờ
    states = run_stream("elevator_down", dur_s=40)
    assert set(states) == {"NORMAL"}


def test_rain_in_bag_no_alarm():
    states = run_stream("rain_in_bag", dur_s=60)
    assert set(states) == {"NORMAL"}


def test_wade_phone_above_water_no_alarm():
    # lội nước nhưng máy còn trên mực nước
    states = run_stream("wade_phone_above_water", dur_s=60)
    assert set(states) == {"NORMAL"}


def test_alarm_persists_until_recover():
    det = H7Detector()
    t, p, a, g = simulate("sink", dur_s=40, sink_cm_per_s=30.0)
    for i in range(20):
        det.push(1.0, p[i], a[i], g[i])
    assert det.state == "ALARM"
    # áp suất tụt về mốc gốc (được vớt lên) + hết churn => về NORMAL
    for i in range(20, 40):
        det.push(1.0, 1013.0, 1.0, 5.0)
    assert det.state == "NORMAL"
