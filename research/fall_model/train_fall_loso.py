"""RQ1 — phát hiện ngã trên SisFall, đánh giá LOSO + ngân sách FAR.

Chạy trên Kaggle (kernel) hoặc local:
  python3 train_fall_loso.py --data <thư-mục-chứa-SA*/SE*> [--folds 4] [--epochs 15]

Chuẩn đánh giá theo kế hoạch đề tài:
- LOSO (leave-one-subject-out) 38 người SA01..SA23, SE01..SE15 — không chia theo cửa sổ.
- Chuẩn hoá theo thống kê tập train của từng fold (không rò rỉ từ người test).
- Cửa sổ ngã = quanh đỉnh va đập; phần đứng/ngồi trước ngã trong file ngã được
  coi là không-ngã (tránh thổi phồng recall).
- Ngưỡng báo động chọn trên tập train của từng fold để đạt FAR mục tiêu, rồi
  áp nguyên ngưỡng lên người test (mô phỏng triển khai thật: ngưỡng đóng băng
  trước khi chạy).
- FAR quy đổi ra báo động giả/ngày: app chạy 20 Hz, cửa sổ 2 s, bước 0,5 s
  => 172 800 cửa sổ/ngày. Báo cáo recall tại ≤1 FA/ngày (KPI đề tài, §8) và
  ≤9 FA/ngày (mốc y văn Kangas 2012).
"""

import argparse
import csv
import json
import os
import time

import numpy as np
from scipy.signal import decimate, find_peaks

SEED = 42
FS_RAW = 200          # SisFall ghi ở 200 Hz
FS = 20               # app chạy 20 Hz (điểm cân bằng Villa & Casilari 2025)
WIN_S = 2.0           # cửa sổ 2 s
STRIDE_S = 2.0        # bước trượt khi cắt cửa sổ train
WIN = int(WIN_S * FS)                 # 40 mẫu
STRIDE = int(STRIDE_S * FS)           # 40 mẫu
WINDOWS_PER_DAY = 172_800             # 20 Hz, stride 0.5 s trên thiết bị
ADXL345_LSB_PER_G = 256.0             # full-res mode, ĐÃ KIỂM THỰC NGHIỆM (check_scale.py:
                                      # trọng lực ≈1,03 g; đỉnh ngã F04 ≈4–7 g khớp y văn)
ITG3200_LSB_PER_DPS = 14.375          # ±2000 °/s
FAR_TARGETS_PER_DAY = [1.0, 9.0]
IMPACT_HALFWIN_S = 1.0                # cửa sổ có tâm trong ±1 s quanh đỉnh => lớp NGÃ


def list_subjects(data_root):
    subs = sorted(d for d in os.listdir(data_root)
                  if d.startswith(("SA", "SE")) and os.path.isdir(os.path.join(data_root, d)))
    if not subs:
        raise SystemExit(f"Không tìm thấy SA*/SE* trong {data_root}")
    return subs


def load_file(path):
    """Trả (acc_g [N,3], gyro_dps [N,3]) ở 20 Hz. Cột 0-2 ADXL345, 3-5 ITG3200.

    Một số file SisFall có dòng trắng/thừa khoảng trống cuối file — bỏ qua dòng rỗng.
    """
    rows = []
    with open(path) as f:
        for line in f:
            toks = [t for t in line.strip().split(",") if t.strip()]
            if len(toks) < 6:
                continue
            rows.append([float(t) for t in toks[:6]])
    a = np.asarray(rows, dtype=np.float64)
    acc = a[:, 0:3] / ADXL345_LSB_PER_G
    gyro = a[:, 3:6] / ITG3200_LSB_PER_DPS
    fs_out = FS_RAW / max(1, round(FS_RAW / FS))   # decimate hệ số 10
    acc = decimate(acc, int(FS_RAW / fs_out), axis=0, ftype="iir", zero_phase=True)
    gyro = decimate(gyro, int(FS_RAW / fs_out), axis=0, ftype="iir", zero_phase=True)
    return acc.astype(np.float32), gyro.astype(np.float32)


def file_label_impact(acc, gyro):
    """Chỉ số mẫu (sau decimate) của đỉnh va đập: max |gia tốc tổng| lọc DC."""
    svm = np.linalg.norm(acc, axis=1)
    # bỏ trọng lực 1 g để đỉnh không dính file đứng yên
    svm_hp = np.abs(svm - np.median(svm))
    peaks, _ = find_peaks(svm_hp, height=np.percentile(svm_hp, 99.5))
    if len(peaks) == 0:
        return int(np.argmax(svm_hp))
    return int(peaks[np.argmax(svm_hp[peaks])])


def windows_of(signal_6ch, stride=STRIDE):
    n = (len(signal_6ch) - WIN) // stride + 1
    idx = np.arange(WIN)[None, :] + stride * np.arange(max(n, 0))[:, None]
    return signal_6ch[idx]          # [K, WIN, 6]


def build_subject_windows(subject_dir):
    """X, y, subject, filename cho mọi file của một người."""
    X, y, fnames = [], [], []
    for name in sorted(os.listdir(subject_dir)):
        if not name.endswith(".txt"):
            continue
        acc, gyro = load_file(os.path.join(subject_dir, name))
        sig = np.concatenate([acc, gyro], axis=1)
        wins = windows_of(sig)
        if len(wins) == 0:
            continue
        is_fall_file = name.startswith("F")
        lab = np.zeros(len(wins), dtype=np.float32)
        if is_fall_file:
            impact = file_label_impact(acc, gyro)
            hw = int(IMPACT_HALFWIN_S * FS)
            centers = np.arange(len(wins)) * STRIDE + WIN // 2
            lab[np.abs(centers - impact) <= hw] = 1.0
        X.append(wins)
        y.append(lab)
        fnames.extend([name] * len(wins))
    if not X:
        return np.zeros((0, WIN, 6), np.float32), np.zeros(0, np.float32), []
    return np.concatenate(X), np.concatenate(y), fnames


def build_model(seed=SEED):
    import tensorflow as tf
    tf.keras.utils.set_random_seed(seed)
    m = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(WIN, 6)),
        tf.keras.layers.GRU(32, return_sequences=True),
        tf.keras.layers.GRU(32),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(1, activation="sigmoid"),
    ])
    m.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
              loss="binary_crossentropy",
              metrics=[tf.keras.metrics.AUC(name="auc")])
    return m


def threshold_for_far(y_true, y_score, fa_per_day):
    """Ngưỡng p sao cho FP/ngày ≤ fa_per_day (dùng trên tập TRAIN của fold)."""
    rate_limit = fa_per_day / WINDOWS_PER_DAY
    order = np.argsort(-y_score)
    y_sorted = y_true[order]
    fp_cum = np.cumsum(1 - y_sorted)
    tp_cum = np.cumsum(y_sorted)
    total_neg = max(1, int(np.sum(1 - y_true)))
    ok = np.where(fp_cum / total_neg <= rate_limit)[0]
    if len(ok) == 0:
        return float(np.max(y_score) + 1e-6)   # im lặng hoàn toàn nếu quá ồn
    k = ok[-1]
    return float(y_score[order][min(k + 1, len(order) - 1)])


def build_cache(data_root, cache_path):
    """Cắt cửa sổ cho TẤT CẢ người một lần — LOSO chỉ lát lại từ cache."""
    subjects = list_subjects(data_root)
    X_all, y_all, s_all = [], [], []
    for s in subjects:
        X, y, _ = build_subject_windows(os.path.join(data_root, s))
        if len(X) == 0:
            continue
        X_all.append(X); y_all.append(y); s_all.append(np.full(len(X), s))
    X = np.concatenate(X_all); y = np.concatenate(y_all); s = np.concatenate(s_all)
    np.savez_compressed(cache_path, X=X, y=y, s=s)
    print(f"Cache {cache_path}: {X.shape}, ngã={int(y.sum())}/{len(y)}")


def run(data_root, folds=None, epochs=15, out_dir="out", cache_path=None):
    if cache_path and os.path.exists(cache_path):
        c = np.load(cache_path, allow_pickle=False)
        cache = {s: None for s in set(c["s"].tolist())}
        print(f"Cache tải: X={c['X'].shape}, ngã={int(c['y'].sum())}/{len(c['y'])}, "
              f"{len(cache)} người")
    elif cache_path:
        build_cache(data_root, cache_path)
        c = np.load(cache_path, allow_pickle=False)
        cache = {s: None for s in set(c["s"].tolist())}
    else:
        cache = None

    def subject_windows(sub):
        if cache is None:
            return build_subject_windows(os.path.join(data_root, sub))
        m = c["s"] == sub
        return c["X"][m], c["y"][m], []

    subjects = list_subjects(data_root)
    test_subjects = subjects if folds is None else subjects[:folds]
    print(f"LOSO trên {len(test_subjects)} người: {test_subjects}")

    os.makedirs(out_dir, exist_ok=True)
    rows = []
    t0 = time.time()
    for i, test_sub in enumerate(test_subjects):
        Xtr, ytr = [], []
        for s in subjects:
            if s == test_sub:
                continue
            X, y, _ = subject_windows(s)
            if len(X):
                Xtr.append(X); ytr.append(y)
        Xtr = np.concatenate(Xtr); ytr = np.concatenate(ytr)
        Xte, yte, fn_te = subject_windows(test_sub)
        if len(Xte) == 0:
            continue

        mean = Xtr.reshape(-1, 6).mean(0); std = Xtr.reshape(-1, 6).std(0) + 1e-6
        Xtr_n = (Xtr - mean) / std
        Xte_n = (Xte - mean) / std

        model = build_model(seed=SEED + i)
        n_fall = max(1, int(ytr.sum()))
        w = {0: 1.0, 1: max(1.0, len(ytr) / (2.0 * n_fall) * 0.5)}
        model.fit(Xtr_n, ytr, epochs=epochs, batch_size=256, verbose=0,
                  class_weight=w,
                  callbacks=[__import__("tensorflow").keras.callbacks.EarlyStopping(
                      monitor="loss", patience=3, restore_best_weights=True)])

        score_tr = model.predict(Xtr_n, batch_size=1024, verbose=0).ravel()
        score_te = model.predict(Xte_n, batch_size=1024, verbose=0).ravel()

        row = {"subject": test_sub, "n_test_win": len(yte),
               "n_fall_win": int(yte.sum())}
        for far in FAR_TARGETS_PER_DAY:
            thr = threshold_for_far(ytr, score_tr, far)
            pred = score_te >= thr
            tp = float(np.sum(pred & (yte > 0.5)))
            fn = float(np.sum(~pred & (yte > 0.5)))
            fp = float(np.sum(pred & (yte < 0.5)))
            fp_day = fp / max(1, len(yte)) * WINDOWS_PER_DAY
            row[f"thr@{far:g}fad"] = round(thr, 6)
            row[f"recall@{far:g}fad"] = round(tp / (tp + fn), 4) if tp + fn else None
            row[f"fp_day@{far:g}fad"] = round(fp_day, 1)
        rows.append(row)
        print(f"[{i+1}/{len(test_subjects)}] {test_sub} "
              + " ".join(f"rec@{r:g}={row[f'recall@{r:g}fad']}" for r in FAR_TARGETS_PER_DAY))
        model.save(os.path.join(out_dir, "model_last.h5"))

    def stat(key):
        vals = [r[key] for r in rows if r.get(key) is not None]
        return {"mean": float(np.mean(vals)), "median": float(np.median(vals)),
                "min": float(np.min(vals)), "n": len(vals)} if vals else None

    summary = {
        "meta": {"data_root": data_root, "fs": FS, "win_s": WIN_S, "stride_s": STRIDE_S,
                 "windows_per_day": WINDOWS_PER_DAY, "epochs": epochs,
                 "loso_subjects": len(test_subjects), "minutes": round((time.time()-t0)/60, 1)},
        "recall_at_1fad": stat("recall@1fad"),
        "recall_at_9fad": stat("recall@9fad"),
        "fp_day_measured@1fad": stat("fp_day@1fad"),
        "per_subject": rows,
    }
    with open(os.path.join(out_dir, "metrics_loso.json"), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    with open(os.path.join(out_dir, "per_subject.csv"), "w", newline="") as f:
        wcsv = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wcsv.writeheader(); wcsv.writerows(rows)
    print(json.dumps({k: summary[k] for k in ["recall_at_1fad", "recall_at_9fad"]},
                     indent=2, ensure_ascii=False))


def autodetect_data():
    """Trên Kaggle, dataset gắn vào /kaggle/input/<tên>/ chứa SA*/SE* ở gốc."""
    if os.path.isdir("/kaggle/input"):
        for root, dirs, _files in os.walk("/kaggle/input"):
            if any(d.startswith(("SA", "SE")) for d in dirs):
                return root
    raise SystemExit("Không tìm thấy dữ liệu: truyền --data hoặc gắn dataset có SA*/SE*")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=None, help="thư mục chứa SA*/SE* (mặc định tự dò /kaggle/input)")
    ap.add_argument("--folds", type=int, default=None, help="số người test (smoke test)")
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--out", default=None)
    ap.add_argument("--cache", default=None, help="file .npz cache cửa sổ (tự tạo nếu thiếu)")
    args = ap.parse_args()
    data = args.data or autodetect_data()
    out = args.out or ("/kaggle/working" if os.path.isdir("/kaggle/working") else "out")
    run(data, folds=args.folds, epochs=args.epochs, out_dir=out, cache_path=args.cache)
