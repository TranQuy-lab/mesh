"""Chuyển model LOSO (.h5) sang TFLite cho app + kiểm nhanh độ trễ suy luận (E3).

Chạy sau khi train_fall_loso.py xong:
  python3 research/fall_model/export_tflite.py research/fall_model/out_full/model_last.h5 \
      --out android-g0/src/main/assets/fall_model.tflite   (đường dẫn ghi chú, app nạp khi nối TFLite)
"""
import argparse
import time

import numpy as np


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--out", default="fall_model.tflite")
    args = ap.parse_args()

    import tensorflow as tf

    model = tf.keras.models.load_model(args.model)
    conv = tf.lite.TFLiteConverter.from_keras_model(model)
    conv.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite = conv.convert()
    with open(args.out, "wb") as f:
        f.write(tflite)
    print(f"Ghi {args.out}: {len(tflite) / 1024:.0f} KB")

    # Đo độ trễ suy luận trung bình (E3 — khoảng trống chưa ai công bố, sổ dữ liệu ngã §D)
    interp = tf.lite.Interpreter(model_content=tflite)
    interp.allocate_tensors()
    inp = interp.get_input_details()[0]
    x = np.random.rand(1, *inp["shape"][1:]).astype(inp["dtype"])
    for _ in range(5):
        interp.invoke()
    t0 = time.perf_counter()
    n = 100
    for _ in range(n):
        interp.invoke()
    ms = (time.perf_counter() - t0) / n * 1000
    print(f"Độ trễ suy luận trung bình: {ms:.2f} ms/lượt (CPU máy này — số tham chiếu, "
          f"chưa phải `ĐO` trên điện thoại)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
