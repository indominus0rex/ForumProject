"""common/stft.py — MicroPython Short-Time Fourier Transform (STFT).

Overlapping Hann-windowed frames -> Cooley-Tukey FFT per frame ->
magnitude spectrogram. No numpy/scipy. Frame/hop must be powers of 2
(the butterfly requires it) and hop must divide (num_samples - frame_len).

Collapse rule (keeps the 15-feature DNN contract): average the magnitude
spectra across time, then apply the same band-power/entropy math as
feature_extract on the mean spectrum.
"""

import math
from typing import List

_TWIDDLES: dict = {}
_HANN_CACHE: dict = {}


def _get_twiddles(n: int):
    if n in _TWIDDLES:
        return _TWIDDLES[n]
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
    return d


def _get_hann(n: int):
    if n in _HANN_CACHE:
        return _HANN_CACHE[n]
    w = [0.5 * (1 - math.cos(2 * math.pi * i / (n - 1))) for i in range(n)]
    _HANN_CACHE[n] = w
    return w


def _is_pow2(v: int) -> bool:
    return v > 0 and (v & (v - 1)) == 0


def _in_place_fft(real: List[float], imag: List[float]) -> None:
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
    tw = _get_twiddles(n)
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


class STFTProcessor:
    """Overlapping STFT over a fixed window. Defaults: 128 samples, 64-frame, 32-hop."""

    def __init__(self, num_samples: int = 128, frame_len: int = 64,
                 hop: int = 32, fs: float = 100.0):
        if not _is_pow2(frame_len):
            raise ValueError("frame_len must be a power of 2, got %r" % (frame_len,))
        if not _is_pow2(hop):
            raise ValueError("hop must be a power of 2, got %r" % (hop,))
        if frame_len > num_samples:
            raise ValueError("frame_len %d > num_samples %d" % (frame_len, num_samples))
        if (num_samples - frame_len) % hop != 0:
            raise ValueError("hop must divide num_samples - frame_len")
        self.num_samples = num_samples
        self.frame_len = frame_len
        self.hop = hop
        self.fs = fs
        self.n_frames = (num_samples - frame_len) // hop + 1
        self.n_bins = frame_len // 2

    def bin_freqs(self) -> List[float]:
        df = self.fs / self.frame_len
        return [i * df for i in range(self.n_bins)]

    def spectrogram(self, signal: List[float]) -> List[List[float]]:
        """Magnitude spectrogram: n_frames rows x n_bins cols. Per-frame mean removed."""
        if len(signal) < self.num_samples:
            raise ValueError("signal len %d < num_samples %d" % (len(signal), self.num_samples))
        hann = _get_hann(self.frame_len)
        out: List[List[float]] = []
        for f in range(self.n_frames):
            seg = signal[f * self.hop: f * self.hop + self.frame_len]
            mu = sum(seg) / self.frame_len
            real = [(seg[i] - mu) * hann[i] for i in range(self.frame_len)]
            imag = [0.0] * self.frame_len
            _in_place_fft(real, imag)
            out.append([math.sqrt(real[i] ** 2 + imag[i] ** 2) * 2 / self.frame_len
                        for i in range(self.n_bins)])
        return out

    def mean_spectrum(self, signal: List[float]) -> List[float]:
        spec = self.spectrogram(signal)
        mean = [0.0] * self.n_bins
        for row in spec:
            for i, v in enumerate(row):
                mean[i] += v
        return [v / self.n_frames for v in mean]

    def band_power(self, mean_mag: List[float], lo: float, hi: float) -> float:
        df = self.fs / self.frame_len
        lo_i = max(1, int(lo / df))
        hi_i = min(self.n_bins - 1, int(hi / df))
        if hi_i <= lo_i:
            return 0.0
        s = 0.0
        for i in range(lo_i, hi_i + 1):
            s += mean_mag[i] * mean_mag[i]
        return math.sqrt(s / (hi_i - lo_i + 1))

    def tremor_power_over_time(self, spec: List[List[float]],
                               lo: float = 3.0, hi: float = 12.0) -> List[float]:
        freqs = self.bin_freqs()
        idx = [i for i, f in enumerate(freqs) if lo <= f <= hi and i >= 1]
        return [sum(row[i] for i in idx) for row in spec]

    def dominant_freq_over_time(self, spec: List[List[float]]) -> List[float]:
        freqs = self.bin_freqs()
        out = []
        for row in spec:
            bi = 1
            bv = row[1] if len(row) > 1 else 0.0
            for i in range(2, len(row)):
                if row[i] > bv:
                    bv = row[i]
                    bi = i
            out.append(freqs[bi])
        return out
