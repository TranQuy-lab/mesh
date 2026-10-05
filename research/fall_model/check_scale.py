"""Kiểm thực nghiệm hệ số quy đổi SisFall trên dữ liệu thật.

Hệ số lý thuyết: ADXL345 ±16 g full-res = 2048 LSB/g; ITG3200 = 14.375 LSB/(°/s).
Kiểm bằng hai bất biến:
  1. |tổng vectơ gia tốc trung bình| ≈ 1 g trên file đứng yên/đi bộ (trọng lực).
  2. Đỉnh gia tốc file ngã (F04 ngã ngửa — va đập mạnh nhất) ≈ 3–8 g, không cắt ngưỡng.
"""
import sys
import numpy as np
from glob import glob
import os

DATA = sys.argv[1] if len(sys.argv) > 1 else "fall_dataset_sisfall"

def raw(path):
    return np.loadtxt(path, delimiter=",", usecols=(0, 1, 2))

# 1. trọng lực
for f in ["SA01/D01_SA01_R01.txt", "SA01/D02_SA01_R01.txt", "SE06/D01_SE06_R01.txt"]:
    p = os.path.join(DATA, f)
    if not os.path.exists(p):
        continue
    a = raw(p)
    g_est = np.linalg.norm(a.mean(0)) / 2048.0
    g_est256 = np.linalg.norm(a.mean(0)) / 256.0
    print(f"{f}: |mean|/2048 = {g_est:.3f} g   |mean|/256 = {g_est256:.3f} g")

# 2. đỉnh ngã + dải động
peaks = []
for f in sorted(glob(os.path.join(DATA, "SA*", "F04_*.txt")))[:10]:
    a = raw(f)
    svm = np.linalg.norm(a - a.mean(0), axis=1)
    peaks.append(svm.max())
print("F04 đỉnh/2048 (g):", np.round(np.array(peaks)/2048.0, 2))
