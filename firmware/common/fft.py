"""common/fft.py — MicroPython FFTProcessor for real-valued signals.

Implements in-place Cooley-Tukey FFT with Hann windowing.
Returns dominant frequency and magnitude above noise threshold.
"""

import math
from typing import List, Tuple


class FFTProcessor:
    """FFT processor for fixed-size real-valued signal windows."""

    def __init__(self, num_samples: int = 128):
        """Initialize with Hann window and pre-computed twiddles.

        Args:
            num_samples: Window size (must be power of 2).
        """
        self.num_samples = num_samples
        self.window = [
            0.5 * (1 - math.cos(2 * math.pi * i / (num_samples - 1)))
            for i in range(num_samples)
        ]
        # Pre-compute twiddle factors per FFT size to avoid cos/sin in loop
        # twiddles[size] = ([cos], [sin]) for k in 0..size/2-1
        self._twiddles = {}
        size = 2
        while size <= num_samples:
            half = size // 2
            cos_t = [0.0] * half
            sin_t = [0.0] * half
            for k in range(half):
                ang = -2 * math.pi * k / size
                cos_t[k] = math.cos(ang)
                sin_t[k] = math.sin(ang)
            self._twiddles[size] = (cos_t, sin_t)
            size <<= 1
        # Pre-allocate reusable buffers to reduce GC pressure
        self._real_buf = [0.0] * num_samples
        self._imag_buf = [0.0] * num_samples

    def _in_place_fft(self, real: List[float], imag: List[float]) -> None:
        """In-place iterative Cooley-Tukey FFT (bit-reversal + butterfly)."""
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
            cos_t, sin_t = self._twiddles[size]
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

    def process_data(
        self,
        signal_data: List[float],
        actual_fs: float
    ) -> Tuple[float, float]:
        """Compute FFT and return dominant frequency/magnitude.

        Args:
            signal_data: Time-domain signal (length num_samples).
            actual_fs: Actual sampling frequency in Hz.

        Returns:
            Tuple of (dominant_freq_hz, magnitude).
            Returns (0.0, 0.0) if peak magnitude < NOISE_THRESHOLD (0.35).
        """
        mean_val = sum(signal_data) / len(signal_data)
        real = [(signal_data[i] - mean_val) * self.window[i] for i in range(self.num_samples)]
        imag = [0.0] * self.num_samples

        self._in_place_fft(real, imag)

        max_mag = 0.0
        dominant_freq = 0.0
        NOISE_THRESHOLD = 0.35

        for i in range(1, self.num_samples // 2):
            magnitude = math.sqrt(real[i]**2 + imag[i]**2)
            frequency = (i * actual_fs) / self.num_samples

            if magnitude > max_mag:
                max_mag = magnitude
                dominant_freq = frequency

        if max_mag < NOISE_THRESHOLD:
            return 0.0, 0.0

        return dominant_freq, max_mag