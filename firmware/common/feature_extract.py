"""common/feature_extract.py — MicroPython 15-feature extractor for 128x3 IMU window.

Input: window = list of 128 samples, either:
  - 2D: [[x0, y0, z0], [x1, y1, z1], ...]  (axis-major, preferred)
  - 1D: [x0, y0, z0, x1, y1, z1, ...]      (interleaved flat)

Output: list of 15 floats in fixed order. Order MUST match train_classifier.py.

Feature order (15-base, backward-compatible):
  0  rms_all            — RMS of all axes concatenated
  1  std_all            — Std dev of all axes concatenated
  2  mean_crossing_rate — Zero-mean crossing rate of all axes
  3  dominant_freq_hz   — Peak frequency (Hz) from magnitude FFT
  4  band_3_6           — RMS band power 3-6 Hz
  5  band_6_9           — RMS band power 6-9 Hz (ET postural 6-8 peak inside)
  6  band_9_12          — RMS band power 9-12 Hz
  7  band_12_25         — RMS band power 12-25 Hz
  8  spectral_entropy   — Normalized spectral entropy (0-1)
  9  dominant_axis      — Axis with highest variance (0=x, 1=y, 2=z)
  10 rms_x              — RMS of x-axis
  11 rms_y              — RMS of y-axis
  12 rms_z              — RMS of z-axis
  13 xy_ratio           — rms_x / max(rms_y, 1e-6)
  14 peak_prominence    — peak_mag / max(median_mag, 1e-6)

Extended (Option A + ET, 2026-08-27):
  pill_4_6 / et_6_9 via helper pill_band_power() and coherence metrics (thumb-index 0.6, finger-wrist 0.6) in FeaturesStage — not in base 15, exposed in frame["pill_power"]/["et_power"]/["coherence"] for future 16-feat model.
"""

import math
from typing import List, Tuple, Union

from common.dsp import compute_spectrum, band_power, spectral_entropy

Window2D = List[List[float]]
WindowFlat = List[float]
Window = Union[Window2D, WindowFlat]


def _flatten_axis_major(window_2d: Window2D) -> Tuple[List[float], List[float], List[float]]:
    """Split 2D window into separate x, y, z lists."""
    n = len(window_2d)
    x = [0.0] * n
    y = [0.0] * n
    z = [0.0] * n
    for i, row in enumerate(window_2d):
        x[i] = row[0]
        y[i] = row[1]
        z[i] = row[2]
    return x, y, z


def _flatten_interleaved(window_flat: WindowFlat) -> Tuple[List[float], List[float], List[float]]:
    """Split interleaved flat window into separate x, y, z lists."""
    n = len(window_flat) // 3
    x = [window_flat[i * 3 + 0] for i in range(n)]
    y = [window_flat[i * 3 + 1] for i in range(n)]
    z = [window_flat[i * 3 + 2] for i in range(n)]
    return x, y, z


def _mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs: List[float], mu: float = None) -> float:
    if mu is None:
        mu = _mean(xs)
    if not xs:
        return 0.0
    s = 0.0
    for v in xs:
        d = v - mu
        s += d * d
    return math.sqrt(s / len(xs))


def _rms(xs: List[float]) -> float:
    if not xs:
        return 0.0
    s = 0.0
    for v in xs:
        s += v * v
    return math.sqrt(s / len(xs))


def _mean_crossing_rate(xs: List[float], mu: float) -> float:
    """Zero-mean crossing rate."""
    cnt = 0
    prev = xs[0] - mu
    for v in xs[1:]:
        cur = v - mu
        if (prev > 0) != (cur > 0):
            cnt += 1
        prev = cur
    return cnt / len(xs) if xs else 0.0


def _median(xs: List[float]) -> float:
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return 0.0
    if n % 2:
        return s[n // 2]
    return 0.5 * (s[n // 2 - 1] + s[n // 2])


def compute(window: Window, fs: float = 100.0, n: int = 128,
            spectrum: Tuple[float, List[float], List[float]] = None) -> List[float]:
    """Extract 15 features from 128-sample 3-axis window.

    Args:
        window: 128 samples, either 2D [[x,y,z],...] or flat [x,y,z,x,y,z,...].
        fs: Sampling frequency in Hz.
        n: Number of samples (must be 128).
        spectrum: Optional pre-computed (peak_freq, mag, _) from compute_spectrum().
                  When provided, skips the internal FFT.

    Returns:
        List of 15 feature floats in fixed order.
    """
    if isinstance(window[0], (list, tuple)):
        x, y, z = _flatten_axis_major(window)  # type: ignore
    else:
        x, y, z = _flatten_interleaved(window)  # type: ignore

    all_vals = x + y + z
    rms_all = _rms(all_vals)
    std_all = _std(all_vals)
    mean_all = _mean(all_vals)
    mcr = _mean_crossing_rate(all_vals, mean_all)

    rms_x = _rms(x)
    rms_y = _rms(y)
    rms_z = _rms(z)
    var = [sum((v - _mean(a)) ** 2 for v in a) / len(a) for a in (x, y, z)]
    dom_axis = 0
    if var[1] > var[0]:
        dom_axis = 1
    if var[2] > var[dom_axis]:
        dom_axis = 2
    xy_ratio = rms_x / rms_y if rms_y > 1e-6 else 1.0

    if spectrum is not None:
        dom_freq, mag, _ = spectrum
    else:
        window_2d = [[x[i], y[i], z[i]] for i in range(n)]
        dom_freq, mag, _ = compute_spectrum(window_2d, fs=fs, n=n)
    bp_3_6 = band_power(mag, fs, n, 3.0, 6.0)
    bp_6_9 = band_power(mag, fs, n, 6.0, 9.0)
    bp_9_12 = band_power(mag, fs, n, 9.0, 12.0)
    bp_12_25 = band_power(mag, fs, n, 12.0, 25.0)
    ent = spectral_entropy(mag[1:])  # skip DC
    med = _median(mag[1:])
    peak_val = max(mag[1:]) if len(mag) > 1 else 0.0
    prominence = peak_val / med if med > 1e-6 else 0.0

    return [
        rms_all,
        std_all,
        mcr,
        dom_freq,
        bp_3_6,
        bp_6_9,
        bp_9_12,
        bp_12_25,
        ent,
        float(dom_axis),
        rms_x,
        rms_y,
        rms_z,
        xy_ratio,
        prominence,
    ]