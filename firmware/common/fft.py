"""common/fft.py — MicroPython FFTProcessor for real-valued signals.

Implements in-place Cooley-Tukey FFT with Hann windowing.
Returns dominant frequency and magnitude above noise threshold.
"""

import math
from typing import List, Tuple
from common.dsp import get_twiddles, get_hann, in_place_fft


class FFTProcessor:
    """FFT processor for fixed-size real-valued signal windows."""

    def __init__(self, num_samples: int = 128):
        """Initialize with Hann window and pre-computed twiddles.

        Args:
            num_samples: Window size (must be power of 2).
        """
        self.num_samples = num_samples
        self.window = get_hann(num_samples)
        # Pre-compute twiddle factors per FFT size to avoid cos/sin in loop
        # twiddles[size] = ([cos], [sin]) for k in 0..size/2-1
        self._twiddles = get_twiddles(num_samples)
        # Pre-allocate reusable buffers to reduce GC pressure
        self._real_buf = [0.0] * num_samples
        self._imag_buf = [0.0] * num_samples

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

        in_place_fft(real, imag)

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
