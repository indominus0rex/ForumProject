# -*- coding: utf-8 -*-
"""analyze_pilot.py — Pilot dataset sanity check + per-class FFT summary.

Reads every CSV in ./sessions/ (or files passed on CLI), expects each row:

    LABEL,ax1,ay1,az1,ax2,ay2,az2,...,ax128,ay128,az128

Outputs:
  - per-class window count
  - per-class mean FFT peak frequency + magnitude
  - per-class RMS amplitude (time-domain)
  - overlaid magnitude spectrum plot per class
"""

import sys
import os
import glob
import numpy as np
import matplotlib.pyplot as plt


FS = 100.0
SAMPLES = 128
CLASSES = ["rest", "postural", "kinetic", "baseline"]


def parse_file(path):
    """Return (labels, array[N, 128, 3]). Skip malformed rows."""
    labels = []
    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) != 1 + SAMPLES * 3:
                print("  skip {}:{} expected {} fields, got {}".format(
                    path, ln, 1 + SAMPLES * 3, len(parts)))
                continue
            try:
                floats = [float(p) for p in parts[1:]]
            except ValueError:
                print("  skip {}:{} non-numeric".format(path, ln))
                continue
            labels.append(parts[0])
            chunks.append(floats)
    if not chunks:
        return labels, np.zeros((0, SAMPLES, 3))
    arr = np.array(chunks, dtype=np.float32).reshape(-1, SAMPLES, 3)
    return labels, arr


def fft_peak(window):
    """Return (peak_freq_hz, peak_magnitude) for a 128x3 window."""
    centered = window - window.mean(axis=0, keepdims=True)
    hann = np.hanning(SAMPLES).reshape(-1, 1)
    windowed = centered * hann
    spec = np.fft.rfft(windowed, axis=0)
    mag = np.abs(spec) * 2 / SAMPLES
    freqs = np.fft.rfftfreq(SAMPLES, d=1.0 / FS)
    mag_total = mag.sum(axis=1)  # sum across x+y+z
    # skip DC
    idx = np.argmax(mag_total[1:]) + 1
    return freqs[idx], mag_total[idx]


def main(paths):
    if not paths:
        paths = sorted(glob.glob(os.path.join("sessions", "*.csv")))
        if not paths:
            print("No CSVs found in ./sessions/. Pass files on CLI.")
            return 1

    by_class = {c: [] for c in CLASSES}
    for p in paths:
        print("reading", p)
        labels, arr = parse_file(p)
        for lbl, w in zip(labels, arr):
            if lbl in by_class:
                by_class[lbl].append(w)
            else:
                by_class.setdefault(lbl, []).append(w)

    print("\n=== window counts ===")
    for c in sorted(by_class.keys()):
        print("  {}: {}".format(c, len(by_class[c])))

    print("\n=== per-class stats ===")
    summary = {}
    for c, wins in by_class.items():
        if not wins:
            continue
        a = np.stack(wins, axis=0)  # [N, 128, 3]
        rms = np.sqrt(np.mean(a ** 2, axis=(1, 2)))
        peaks = np.array([fft_peak(w) for w in a])
        summary[c] = {
            "n": len(wins),
            "rms_mean": float(rms.mean()),
            "rms_std": float(rms.std()),
            "peak_freq_mean": float(peaks[:, 0].mean()),
            "peak_freq_std": float(peaks[:, 0].std()),
            "peak_mag_mean": float(peaks[:, 1].mean()),
        }
        s = summary[c]
        print("  {}: n={}  rms={:.4f}+/-{:.4f}  peak_f={:.2f}+/-{:.2f} Hz  peak_mag={:.3f}".format(
            c, s["n"], s["rms_mean"], s["rms_std"],
            s["peak_freq_mean"], s["peak_freq_std"], s["peak_mag_mean"]))

    # overlaid spectrum
    plt.figure(figsize=(12, 6))
    for c, wins in by_class.items():
        if not wins:
            continue
        a = np.stack(wins, axis=0)
        centered = a - a.mean(axis=1, keepdims=True)
        hann = np.hanning(SAMPLES).reshape(1, -1, 1)
        spec = np.fft.rfft(centered * hann, axis=1)
        mag = np.abs(spec).sum(axis=2) * 2 / SAMPLES  # [N, freqs]
        mean_mag = mag.mean(axis=0)
        freqs = np.fft.rfftfreq(SAMPLES, d=1.0 / FS)
        plt.plot(freqs[1:], mean_mag[1:], label="{} (n={})".format(c, len(wins)), linewidth=1.5)
    plt.title("Pilot dataset — mean FFT magnitude per class")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (g)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.xlim(0, FS / 2)
    plt.tight_layout()
    plt.show()

    # stop-gate
    print("\n=== stop-gate check ===")
    ok = True
    for c in ["rest", "postural", "kinetic", "baseline"]:
        if c not in summary:
            print("  MISSING class:", c)
            ok = False
        elif summary[c]["n"] < 20:
            print("  TOO FEW windows for {}: {} < 20".format(c, summary[c]["n"]))
            ok = False
    if summary.get("baseline", {}).get("peak_mag_mean", 0) > 0.05:
        print("  WARN: baseline peak_mag > 0.05 (check sensor mount / vibration)")
    if ok:
        print("  OK — proceed to classifier phase")
    else:
        print("  NOT OK — collect more data or fix capture")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
