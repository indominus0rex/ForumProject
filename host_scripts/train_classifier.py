"""train_classifier.py — scikit-learn trainer for tremor classifier.

Reads every CSV in ./sessions/, extracts 15 features per window,
fits a StandardScaler + multinomial LogisticRegression, then prints
a Python literal that can be pasted into model.py.

Run:
    pip install scikit-learn numpy matplotlib
    python train_classifier.py
    python train_classifier.py sessions/rest_*.csv sessions/kinetic_*.csv
"""

import sys
import os
import glob
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score

# Optional: tremor suppression analysis functions
def calculate_tremor_suppression(pre_data, post_data, feature='tremor_power'):
    """
    Calculate tremor suppression effectiveness between pre and post intervention data.
    
    Args:
        pre_data: list of tremor feature values from pre-intervention
        post_data: list of tremor feature values from post-intervention
        feature: name of feature being analyzed (for reporting)
        
    Returns:
        dict with suppression metrics
    """
    if not pre_data or not post_data:
        return {"error": "Insufficient data"}
    
    pre_mean = np.mean(pre_data)
    post_mean = np.mean(post_data)
    
    if pre_mean > 0:
        percent_reduction = (pre_mean - post_mean) / pre_mean * 100.0
    else:
        percent_reduction = 0.0
        
    return {
        "pre_mean": float(pre_mean),
        "post_mean": float(post_mean),
        "absolute_reduction": float(pre_mean - post_mean),
        "percent_reduction": float(percent_reduction),
        "pre_std": float(np.std(pre_data)),
        "post_std": float(np.std(post_data)),
        "pre_count": len(pre_data),
        "post_count": len(post_data)
    }


def extract_tremor_features_from_window(window):
    """
    Extract tremor-relevant features from a 128x3 window (lightweight version).
    Returns tremor power in 4-8 Hz band.
    """
    FS = 100.0
    SAMPLES = 128
    
    # Time-domain RMS
    rms = float(np.sqrt(np.mean(window ** 2)))
    
    # Frequency-domain features
    centered = window - window.mean(axis=0, keepdims=True)
    hann = np.hanning(SAMPLES).reshape(-1, 1)
    spec = np.fft.rfft(centered * hann, axis=0)
    mag = np.abs(spec) * 2 / SAMPLES
    freqs = np.fft.rfftfreq(SAMPLES, d=1.0 / FS)
    mag_total = mag.sum(axis=1)  # sum across x+y+z
    
    # Tremor band power (4-8 Hz)
    lo_i = max(1, int(4.0 / (FS / SAMPLES)))
    hi_i = min(SAMPLES//2 - 1, int(8.0 / (FS / SAMPLES)))
    if hi_i > lo_i:
        tremor_power = float(np.sqrt(np.mean(mag_total[lo_i:hi_i+1] ** 2)))
    else:
        tremor_power = 0.0
    
    return {"rms": rms, "tremor_power": tremor_power}


FS = 100.0
N = 128
HIDDEN = 16  # must match N_HIDDEN in firmware/common/model_dnn.py


def parse_file(path):
    """Return (labels, array[N_windows, 128, 3]). Skip malformed rows."""
    labels = []
    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) != 1 + N * 3:
                continue
            try:
                floats = [float(p) for p in parts[1:]]
            except ValueError:
                continue
            labels.append(parts[0])
            chunks.append(floats)
    if not chunks:
        return labels, np.zeros((0, N, 3))
    arr = np.array(chunks, dtype=np.float32).reshape(-1, N, 3)
    return labels, arr


def fft_mag_sum(window, fs=FS, n=N):
    centered = window - window.mean(axis=0, keepdims=True)
    hann = np.hanning(n).reshape(-1, 1)
    spec = np.fft.rfft(centered * hann, axis=0)
    mag = np.abs(spec) * 2 / n
    return mag.sum(axis=1), mag


def band_power(mag, fs, n, lo, hi):
    half = n // 2
    df = fs / n
    lo_i = max(1, int(lo / df))
    hi_i = min(half - 1, int(hi / df))
    if hi_i <= lo_i:
        return 0.0
    seg = mag[lo_i: hi_i + 1]
    return float(np.sqrt(np.mean(seg ** 2)))


def spectral_entropy(mag):
    p = mag ** 2
    s = p.sum()
    if s <= 1e-12:
        return 0.0
    p = p / s
    p = p[p > 1e-12]
    h = -float((p * np.log(p)).sum())
    return h / np.log(len(mag)) if len(mag) > 1 else 0.0


def extract_features(window):
    """Match the order in feature_extract.py exactly."""
    x = window[:, 0]
    y = window[:, 1]
    z = window[:, 2]
    all_vals = np.concatenate([x, y, z])

    rms_all = float(np.sqrt(np.mean(all_vals ** 2)))
    std_all = float(np.std(all_vals))
    centered = all_vals - all_vals.mean()
    signs = np.sign(centered)
    mcr = float(np.sum(signs[1:] != signs[:-1]) / len(all_vals))

    rms_x = float(np.sqrt(np.mean(x ** 2)))
    rms_y = float(np.sqrt(np.mean(y ** 2)))
    rms_z = float(np.sqrt(np.mean(z ** 2)))
    var = [float(np.var(a)) for a in (x, y, z)]
    dom_axis = int(np.argmax(var))
    xy_ratio = rms_x / rms_y if rms_y > 1e-6 else 1.0

    mag_sum, mag = fft_mag_sum(window)
    df = fs = FS
    n = N
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    peak_idx = 1 + int(np.argmax(mag_sum[1:])) if len(mag_sum) > 2 else 0
    dom_freq = float(freqs[peak_idx])
    bp_3_6 = band_power(mag_sum, fs, n, 3.0, 6.0)
    bp_6_9 = band_power(mag_sum, fs, n, 6.0, 9.0)
    bp_9_12 = band_power(mag_sum, fs, n, 9.0, 12.0)
    bp_12_25 = band_power(mag_sum, fs, n, 12.0, 25.0)
    ent = spectral_entropy(mag_sum[1:])
    med = float(np.median(mag_sum[1:])) if len(mag_sum) > 1 else 0.0
    peak_val = float(mag_sum[1:].max()) if len(mag_sum) > 1 else 0.0
    prominence = peak_val / med if med > 1e-6 else 0.0

    return np.array([
        rms_all, std_all, mcr, dom_freq,
        bp_3_6, bp_6_9, bp_9_12, bp_12_25,
        ent, float(dom_axis),
        rms_x, rms_y, rms_z, xy_ratio, prominence,
    ], dtype=np.float32)


def fmt_list(arr, fmt="{:.6f}"):
    return "[" + ", ".join(fmt.format(float(v)) for v in arr) + "]"


def main(paths, use_dnn=False):
    if not paths:
        paths = sorted(glob.glob(os.path.join("sessions", "*.csv")))
        if not paths:
            print("No CSVs found in ./sessions/. Pass files on CLI.")
            return 1

    X, y = [], []
    for p in paths:
        labels, arr = parse_file(p)
        print("  {}: {} windows".format(p, len(labels)))
        for lbl, w in zip(labels, arr):
            X.append(extract_features(w))
            y.append(lbl)
    X = np.array(X)
    y = np.array(y)
    print("\nDataset: {} windows, {} classes ({})".format(
        len(y), len(set(y)), ", ".join(sorted(set(y)))))

    if len(set(y)) < 2:
        print("Need at least 2 classes. Aborting.")
        return 2

    scaler = StandardScaler().fit(X)
    Xs = scaler.transform(X)
    if use_dnn:
        from sklearn.neural_network import MLPClassifier
        clf = MLPClassifier(
            hidden_layer_sizes=(HIDDEN,),
            activation="relu",
            max_iter=2000,
            random_state=0,
        ).fit(Xs, y)
    else:
        clf = LogisticRegression(
            max_iter=500,
            multi_class="multinomial",
            C=1.0,
            solver="lbfgs",
        ).fit(Xs, y)

    train_acc = float((clf.predict(Xs) == y).mean())
    print("\nTrain accuracy: {:.3f}".format(train_acc))

    if len(y) >= 20 and len(set(y)) >= 2:
        n_splits = min(5, len(y) // max(1, len(set(y))))
        if n_splits >= 2:
            scores = cross_val_score(clf, Xs, y, cv=StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=0))
            print("CV accuracy: {:.3f} +/- {:.3f}".format(scores.mean(), scores.std()))

    if use_dnn:
        print("\n# === paste into model_dnn.py ===")
    else:
        print("\n# === paste into model.py ===")
    print("CLASSES = {}".format([str(c) for c in clf.classes_]))
    print("FEATURE_MEAN = {}".format(fmt_list(scaler.mean_)))
    print("FEATURE_STD  = {}".format(fmt_list(scaler.scale_)))
    if use_dnn:
        print("W1 = [  # {} x {}".format(HIDDEN, X.shape[1]))
        for row in clf.coefs_[0].T:
            print("    " + fmt_list(row) + ",")
        print("]")
        print("B1 = {}".format(fmt_list(clf.intercepts_[0])))
        print("W2 = [  # {} x {}".format(len(clf.classes_), HIDDEN))
        for row in clf.coefs_[1].T:
            print("    " + fmt_list(row) + ",")
        print("]")
        print("B2 = {}".format(fmt_list(clf.intercepts_[1])))
    else:
        print("WEIGHTS = [")
        for row in clf.coef_:
            print("    " + fmt_list(row) + ",")
        print("]")
        print("BIAS   = {}".format(fmt_list(clf.intercept_)))
    print("# === end ===")

    # confusion
    pred = clf.predict(Xs)
    print("\nPer-class accuracy:")
    for c in sorted(set(y)):
        m = y == c
        if m.sum() == 0:
            continue
        acc = (pred[m] == c).mean()
        print("  {}: {:.3f} (n={})".format(c, acc, int(m.sum())))

    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    use_dnn = "--dnn" in args
    paths = [a for a in args if a != "--dnn"]
    sys.exit(main(paths, use_dnn=use_dnn))
