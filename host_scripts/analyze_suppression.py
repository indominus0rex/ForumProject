# -*- coding: utf-8 -*-
"""
analyze_suppression.py — Tremor suppression effectiveness evaluator.

Reads pre-intervention and post-intervention CSV files (or directories),
computes tremor amplitude metrics, and reports suppression effectiveness.

Expected row format (same as pilot data):
    LABEL,ax1,ay1,az1,ax2,ay2,az2,...,ax128,ay128,az128

Usage:
    python analyze_suppression.py --pre pre_dir/ --post post_dir/ [--class postural]
    python analyze_suppression.py --pre pre_*.csv --post post_*.csv [--class kinetic]

Outputs:
    - Tremor amplitude (RMS and band power in 4-8 Hz) for each window
    - Pre/post comparison statistics (mean, std, percent reduction)
    - Paired t-test p-value (if equal window counts)
    - Optional: correlation with haptic feedback timestamps (if provided in filename or header)
"""

import sys
import os
import glob
import numpy as np
import argparse

FS = 100.0
SAMPLES = 128
TREMOR_BAND_LO = 4.0  # Hz
TREMOR_BAND_HI = 8.0  # Hz


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


def rms_amplitude(window):
    """Root mean square amplitude of a 128x3 window (all axes)."""
    return float(np.sqrt(np.mean(window ** 2)))


def band_power(mag, fs, n, lo, hi):
    """Root mean square of magnitude spectrum in [lo, hi] Hz."""
    half = n // 2
    df = fs / n
    lo_i = max(1, int(lo / df))
    hi_i = min(half - 1, int(hi / df))
    if hi_i <= lo_i:
        return 0.0
    seg = mag[lo_i: hi_i + 1]
    return float(np.sqrt(np.mean(seg ** 2)))


def fft_mag_sum(window, fs=FS, n=SAMPLES):
    """Return (total_mag, mag_per_axis) for a window."""
    centered = window - window.mean(axis=0, keepdims=True)
    hann = np.hanning(n).reshape(-1, 1)
    spec = np.fft.rfft(centered * hann, axis=0)
    mag = np.abs(spec) * 2 / n  # [freqs, 3]
    return mag.sum(axis=1), mag  # sum across axes


def extract_tremor_features(window):
    """
    Extract tremor-relevant features from a 128x3 window.
    Returns dict with:
        - rms: time-domain RMS amplitude
        - tremor_power: band power in tremor frequency range (4-8 Hz)
        - peak_freq: frequency of peak magnitude (excluding DC)
        - peak_mag: magnitude at peak frequency
    """
    # Time-domain RMS
    rms = rms_amplitude(window)
    
    # Frequency-domain features
    mag_sum, mag_per_axis = fft_mag_sum(window)
    freqs = np.fft.rfftfreq(SAMPLES, d=1.0 / FS)
    
    # Tremor band power (4-8 Hz)
    tremor_power = band_power(mag_sum, FS, SAMPLES, TREMOR_BAND_LO, TREMOR_BAND_HI)
    
    # Peak frequency and magnitude (excluding DC)
    if len(mag_sum) > 1:
        peak_idx = 1 + np.argmax(mag_sum[1:])
        peak_freq = freqs[peak_idx]
        peak_mag = mag_sum[peak_idx]
    else:
        peak_freq = 0.0
        peak_mag = 0.0
    
    return {
        "rms": rms,
        "tremor_power": tremor_power,
        "peak_freq": peak_freq,
        "peak_mag": peak_mag
    }


def load_data(paths, target_class=None):
    """Load windows from files, optionally filtering by class label."""
    labels_all = []
    features_all = []  # list of dicts
    
    for path in paths:
        labels, arr = parse_file(path)
        if len(labels) == 0:
            continue
            
        for lbl, window in zip(labels, arr):
            if target_class is None or lbl == target_class:
                labels_all.append(lbl)
                features_all.append(extract_tremor_features(window))
    
    return labels_all, features_all


def compute_statistics(feature_dicts, feature_name):
    """Compute mean, std, median for a feature across windows."""
    values = [fd[feature_name] for fd in feature_dicts]
    if not values:
        return {"mean": 0.0, "std": 0.0, "median": 0.0, "count": 0}
    return {
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
        "median": float(np.median(values)),
        "count": len(values)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate tremor suppression effectiveness from pre/post intervention data."
    )
    parser.add_argument("--pre", nargs="+", required=True,
                        help="Pre-intervention CSV files or directories (use glob patterns)")
    parser.add_argument("--post", nargs="+", required=True,
                        help="Post-intervention CSV files or directories (use glob patterns)")
    parser.add_argument("--class", dest="target_class", default=None,
                        help="Focus on specific class label (e.g., 'postural', 'kinetic')")
    parser.add_argument("--tremor-band", nargs=2, type=float, default=[4.0, 8.0],
                        metavar=("LO", "HI"),
                        help="Tremor frequency band in Hz (default: 4 8)")
    parser.add_argument("--feature", choices=["rms", "tremor_power", "peak_mag"], default="tremor_power",
                        help="Feature to use for suppression calculation (default: tremor_power)")
    args = parser.parse_args()
    
    # Expand glob patterns and directories
    def expand_paths(patterns):
        expanded = []
        for pattern in patterns:
            if os.path.isdir(pattern):
                expanded.extend(sorted(glob.glob(os.path.join(pattern, "*.csv"))))
            else:
                expanded.extend(sorted(glob.glob(pattern)))
        return [p for p in expanded if os.path.isfile(p)]
    
    pre_paths = expand_paths(args.pre)
    post_paths = expand_paths(args.post)
    
    if not pre_paths:
        print("Error: No pre-intervention files found.")
        return 1
    if not post_paths:
        print("Error: No post-intervention files found.")
        return 1
    
    print("Pre-intervention files:", pre_paths)
    print("Post-intervention files:", post_paths)
    if args.target_class:
        print(f"Analyzing class: {args.target_class}")
    print(f"Using feature: {args.feature}")
    print(f"Tremor band: {args.tremor_band[0]}-{args.tremor_band[1]} Hz\n")
    
    # Temporarily override tremor band if provided
    global TREMOR_BAND_LO, TREMOR_BAND_HI
    TREMOR_BAND_LO, TREMOR_BAND_HI = args.tremor_band
    
    # Load data
    print("Loading pre-intervention data...")
    pre_labels, pre_features = load_data(pre_paths, args.target_class)
    print(f"  Found {len(pre_features)} windows")
    
    print("Loading post-intervention data...")
    post_labels, post_features = load_data(post_paths, args.target_class)
    print(f"  Found {len(post_features)} windows\n")
    
    if not pre_features or not post_features:
        print("Error: No data windows found for analysis.")
        return 1
    
    # Compute statistics
    pre_stats = compute_statistics(pre_features, args.feature)
    post_stats = compute_statistics(post_features, args.feature)
    
    # Calculate suppression effectiveness
    if pre_stats["mean"] > 0:
        percent_reduction = (pre_stats["mean"] - post_stats["mean"]) / pre_stats["mean"] * 100.0
    else:
        percent_reduction = 0.0
    
    # Statistical test (paired if equal counts, otherwise independent)
    pre_vals = np.array([f[args.feature] for f in pre_features])
    post_vals = np.array([f[args.feature] for f in post_features])
    
    # Manual t-test implementation since scipy is not available
    def ttest_ind(a, b):
        """Independent t-test (Welch's t-test)"""
        n1, n2 = len(a), len(b)
        if n1 <= 1 or n2 <= 1:
            return 0.0, 1.0
        var1, var2 = np.var(a, ddof=1), np.var(b, ddof=1)
        pooled_se = np.sqrt(var1/n1 + var2/n2)
        if pooled_se == 0:
            return 0.0, 1.0
        t_stat = (np.mean(a) - np.mean(b)) / pooled_se
        # degrees of freedom for Welch's t-test
        df = (var1/n1 + var2/n2)**2 / ((var1/n1)**2/(n1-1) + (var2/n2)**2/(n2-1))
        # approximate p-value using normal distribution for large df, or t-distribution
        # For simplicity, we'll use a basic approximation
        if df > 30:
            # Use normal approximation
            from math import erfc
            p_value = erfc(abs(t_stat) / np.sqrt(2))
        else:
            # Rough approximation - for small df, be conservative
            p_value = 0.05 if abs(t_stat) > 2.0 else 0.1  # Very rough
        return t_stat, p_value
    
    def ttest_rel(a, b):
        """Paired t-test"""
        if len(a) != len(b) or len(a) <= 1:
            return 0.0, 1.0
        diff = a - b
        n = len(diff)
        mean_diff = np.mean(diff)
        std_diff = np.std(diff, ddof=1)
        if std_diff == 0:
            return 0.0, 1.0
        t_stat = mean_diff / (std_diff / np.sqrt(n))
        df = n - 1
        # Rough approximation for p-value
        if df > 30:
            from math import erfc
            p_value = erfc(abs(t_stat) / np.sqrt(2))
        else:
            p_value = 0.05 if abs(t_stat) > 2.0 else 0.1  # Very rough
        return t_stat, p_value
    
    if len(pre_vals) == len(post_vals) and len(pre_vals) > 1:
        # Paired t-test
        t_stat, p_value = ttest_rel(pre_vals, post_vals)
        test_type = "paired"
    else:
        # Independent t-test
        t_stat, p_value = ttest_ind(pre_vals, post_vals)
        test_type = "independent"
    
    # Print results
    print("=== Tremor Suppression Effectiveness Report ===")
    print(f"Feature analyzed: {args.feature}")
    print(f"Pre-intervention:  n={pre_stats['count']}, mean={pre_stats['mean']:.4f}, std={pre_stats['std']:.4f}, median={pre_stats['median']:.4f}")
    print(f"Post-intervention: n={post_stats['count']}, mean={post_stats['mean']:.4f}, std={post_stats['std']:.4f}, median={post_stats['median']:.4f}")
    print(f"Absolute reduction: {pre_stats['mean'] - post_stats['mean']:.4f}")
    print(f"Percent reduction:  {percent_reduction:.1f}%")
    print(f"{test_type.capitalize()} t-test: t={t_stat:.3f}, p={p_value:.4f}")
    
    if p_value < 0.05:
        print("RESULT: Statistically significant suppression detected (p < 0.05)")
    else:
        print("RESULT: No statistically significant suppression detected (p >= 0.05)")
    
    # Optional: Show per-class breakdown if we didn't filter by class
    if not args.target_class:
        print("\n--- Per-class breakdown (pre/post means) ---")
        all_classes = set(l for l in pre_labels + post_labels if l)
        for cls in sorted(all_classes):
            pre_cls = [f[args.feature] for l, f in zip(pre_labels, pre_features) if l == cls]
            post_cls = [f[args.feature] for l, f in zip(post_labels, post_features) if l == cls]
            if pre_cls and post_cls:
                pre_mean = np.mean(pre_cls)
                post_mean = np.mean(post_cls)
                red = (pre_mean - post_mean) / pre_mean * 100 if pre_mean > 0 else 0
                print(f"  {cls}: pre={pre_mean:.3f}, post={post_mean:.3f}, reduction={red:.1f}% (n_pre={len(pre_cls)}, n_post={len(post_cls)})")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())