"""common/dsp.py — Shared DSP primitives (FFT, spectrum, band power).

Single source of truth for FFT math. Both common/fft.py and
common/feature_extract.py import from here.
"""

import math
from typing import List, Tuple

_TWIDDLES: dict = {}
_HANN_CACHE: dict = {}


def get_twiddles(n: int):
    if n not in _TWIDDLES:
        d = {}
        size = 2
        while size <= n:
            half = size // 2
            cos_t = [0.0] * half
            sin_t = [0.0] * half
            for k in range(half):
                ang = -2 * math.pi * k / size
                cos_t[k] = math.cos(ang)
                sin_t[k] = math.sin(ang)
            d[size] = (cos_t, sin_t)
            size <<= 1
        _TWIDDLES[n] = d
    return _TWIDDLES[n]


def get_hann(n: int):
    if n not in _HANN_CACHE:
        _HANN_CACHE[n] = [0.5 * (1 - math.cos(2 * math.pi * i / (n - 1))) for i in range(n)]
    return _HANN_CACHE[n]


def in_place_fft(real: List[float], imag: List[float]) -> None:
    """In-place iterative Cooley-Tukey FFT with pre-computed twiddles."""
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
    tw = get_twiddles(n)
    size = 2
    while size <= n:
        half = size // 2
        cos_t, sin_t = tw[size]
        for i in range(0, n, size):
            for k in range(half):
                c = cos_t[k]
                s = sin_t[k]
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
        size <<= 1


def compute_spectrum(window_2d: List[List[float]], fs: float = 100.0, n: int = 128
                    ) -> Tuple[float, List[float], List[float]]:
    """Compute magnitude spectrum from 3-axis window.

    Returns:
        (peak_freq_hz, magnitude_spectrum[0..n//2], magnitude_spectrum_full)
    """
    mean_x = sum(r[0] for r in window_2d) / n
    mean_y = sum(r[1] for r in window_2d) / n
    mean_z = sum(r[2] for r in window_2d) / n
    real = [0.0] * n
    for i, r in enumerate(window_2d):
        real[i] = math.sqrt((r[0] - mean_x) ** 2 + (r[1] - mean_y) ** 2 + (r[2] - mean_z) ** 2)
    imag = [0.0] * n
    hann = get_hann(n)
    for i in range(n):
        real[i] *= hann[i]
    in_place_fft(real, imag)
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


def band_power(mag: List[float], fs: float, n: int, lo: float, hi: float) -> float:
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


def spectral_entropy(mag: List[float]) -> float:
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
