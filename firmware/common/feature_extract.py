"""common/feature_extract.py — MicroPython 15-feature extractor for 128x3 IMU window.

Input: window = list of 128 samples, either:
  - 2D: [[x0, y0, z0], [x1, y1, z1], ...]  (axis-major, preferred)
  - 1D: [x0, y0, z0, x1, y1, z1, ...]      (interleaved flat)

Output: list of 15 floats in fixed order. Order MUST match train_classifier.py.

Feature order:
  0  rms_all            — RMS of all axes concatenated
  1  std_all            — Std dev of all axes concatenated
  2  mean_crossing_rate — Zero-mean crossing rate of all axes
  3  dominant_freq_hz   — Peak frequency (Hz) from magnitude FFT
  4  band_3_6           — RMS band power 3-6 Hz
  5  band_6_9           — RMS band power 6-9 Hz
  6  band_9_12          — RMS band power 9-12 Hz
  7  band_12_25         — RMS band power 12-25 Hz
  8  spectral_entropy   — Normalized spectral entropy (0-1)
  9  dominant_axis      — Axis with highest variance (0=x, 1=y, 2=z)
  10 rms_x              — RMS of x-axis
  11 rms_y              — RMS of y-axis
  12 rms_z              — RMS of z-axis
  13 xy_ratio           — rms_x / max(rms_y, 1e-6)
  14 peak_prominence    — peak_mag / max(median_mag, 1e-6)
"""

import math
from typing import List, Tuple, Union


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


def _in_place_fft(real: List[float], imag: List[float]) -> None:
    """In-place iterative Cooley-Tukey FFT."""
    n = len(real)
    if n <= 1:
        return
    j = 0
    for i in range(n):
        if i < j:
            real[i], real[j] = real[j], real[i]
            imag[i], imag[j] = imag[j], imag[i]
        m = n >> 1
        while m >= 1 and j >= m:
            j -= m
            m >>= 1
        j += m
    size = 2
    while size <= n:
        half = size // 2
        for i in range(0, n, size):
            for k in range(half):
                ang = -2 * math.pi * k / size
                c = math.cos(ang)
                s = math.sin(ang)
                ie = i + k
                io = i + k + half
                ro = real[io]
                io_im = imag[io]
                tr = ro * c - io_im * s
                ti = ro * s + io_im * c
                real[io] = real[ie] - tr
                imag[io] = imag[ie] - ti
                real[ie] += tr
                imag[ie] += ti
        size *= 2


def _fft_mag_sum(
    window_2d: Window2D,
    fs: float = 100.0,
    n: int = 128
) -> Tuple[float, List[float], List[float]]:
    """Compute magnitude spectrum from 3-axis window.

    Returns:
        (peak_freq_hz, magnitude_spectrum[0..n//2], magnitude_spectrum_full)
    """
    mean_x = _mean([r[0] for r in window_2d])
    mean_y = _mean([r[1] for r in window_2d])
    mean_z = _mean([r[2] for r in window_2d])
    real = [0.0] * n
    for i, r in enumerate(window_2d):
        mag = math.sqrt((r[0] - mean_x) ** 2 + (r[1] - mean_y) ** 2 + (r[2] - mean_z) ** 2)
        real[i] = mag
    imag = [0.0] * n
    for i in range(n):
        w = 0.5 * (1 - math.cos(2 * math.pi * i / (n - 1)))
        real[i] *= w
    _in_place_fft(real, imag)
    half = n // 2
    mag = [0.0] * half
    for i in range(half):
        mag[i] = math.sqrt(real[i] * real[i] + imag[i] * imag[i]) * 2 / n
    if half <= 1:
        return 0.0, mag, mag
    peak_idx = 1
    peak_val = mag[1]
    for i in range(2, half):
        if mag[i] > peak_val:
            peak_val = mag[i]
            peak_idx = i
    return (peak_idx * fs) / n, mag, mag


def _band_power(mag: List[float], fs: float, n: int, lo: float, hi: float) -> float:
    """RMS band power in [lo, hi] Hz."""
    half = n // 2
    df = fs / n
    lo_i = max(1, int(lo / df))
    hi_i = min(half - 1, int(hi / df))
    if hi_i <= lo_i:
        return 0.0
    s = 0.0
    for i in range(lo_i, hi_i + 1):
        s += mag[i] * mag[i]
    return math.sqrt(s / (hi_i - lo_i + 1))


def _spectral_entropy(mag: List[float]) -> float:
    """Normalized spectral entropy (0-1)."""
    s = sum(m * m for m in mag)
    if s <= 1e-12:
        return 0.0
    h = 0.0
    for m in mag:
        p = (m * m) / s
        if p > 1e-12:
            h -= p * math.log(p)
    return h / math.log(len(mag)) if len(mag) > 1 else 0.0


def _median(xs: List[float]) -> float:
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return 0.0
    if n % 2:
        return s[n // 2]
    return 0.5 * (s[n // 2 - 1] + s[n // 2])


def compute(window: Window, fs: float = 100.0, n: int = 128) -> List[float]:
    """Extract 15 features from 128-sample 3-axis window.

    Args:
        window: 128 samples, either 2D [[x,y,z],...] or flat [x,y,z,x,y,z,...].
        fs: Sampling frequency in Hz.
        n: Number of samples (must be 128).

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

    window_2d = [[x[i], y[i], z[i]] for i in range(n)]
    dom_freq, mag, _ = _fft_mag_sum(window_2d, fs=fs, n=n)
    bp_3_6 = _band_power(mag, fs, n, 3.0, 6.0)
    bp_6_9 = _band_power(mag, fs, n, 6.0, 9.0)
    bp_9_12 = _band_power(mag, fs, n, 9.0, 12.0)
    bp_12_25 = _band_power(mag, fs, n, 12.0, 25.0)
    ent = _spectral_entropy(mag[1:])  # skip DC
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