"""common/bandpass.py — 2nd-order IIR bandpass filter for 3-12 Hz tremor band.

Efficient biquad cascade suitable for real-time MicroPython.
Each biquad section: y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]
"""

import math
from typing import List, Tuple


class Biquad:
    """Single 2nd-order IIR section (biquad)."""

    def __init__(self, b0: float, b1: float, b2: float, a1: float, a2: float):
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.a1 = a1
        self.a2 = a2
        # State
        self.x1 = 0.0
        self.x2 = 0.0
        self.y1 = 0.0
        self.y2 = 0.0

    def process_sample(self, x: float) -> float:
        """Process single sample, return filtered output."""
        y = (self.b0 * x + self.b1 * self.x1 + self.b2 * self.x2
             - self.a1 * self.y1 - self.a2 * self.y2)
        self.x2 = self.x1
        self.x1 = x
        self.y2 = self.y1
        self.y1 = y
        return y

    def reset(self):
        """Clear filter state."""
        self.x1 = 0.0
        self.x2 = 0.0
        self.y1 = 0.0
        self.y2 = 0.0


class BandpassFilter:
    """2nd-order IIR bandpass filter for tremor frequency band (3-12 Hz).

    Uses biquad cascade for steeper rolloff.
    """

    def __init__(self, fs: float = 100.0, low_hz: float = 3.0, high_hz: float = 12.0):
        """Initialize bandpass filter.

        Args:
            fs: Sampling frequency in Hz.
            low_hz: Lower cutoff frequency in Hz.
            high_hz: Upper cutoff frequency in Hz.
        """
        self.fs = fs
        self.low_hz = low_hz
        self.high_hz = high_hz
        self.sections: List[Biquad] = []
        self._design_filter()

    def _design_filter(self):
        """Design 4th-order bandpass as cascade of 2 biquad sections."""
        # Center frequency and bandwidth
        f0 = math.sqrt(self.low_hz * self.high_hz)  # geometric mean
        bw = self.high_hz - self.low_hz
        Q = f0 / bw

        # Normalized frequency
        w0 = 2.0 * math.pi * f0 / self.fs
        cos_w0 = math.cos(w0)
        sin_w0 = math.sin(w0)

        # Bandwidth in octaves for each section
        alpha = sin_w0 / (2.0 * Q)

        # Section 1: Low-pass to bandpass transformation
        b0_1 = alpha
        b1_1 = 0.0
        b2_1 = -alpha
        a0_1 = 1.0 + alpha
        a1_1 = -2.0 * cos_w0
        a2_1 = 1.0 - alpha

        # Normalize section 1
        self.sections.append(Biquad(
            b0_1 / a0_1, b1_1 / a0_1, b2_1 / a0_1,
            a1_1 / a0_1, a2_1 / a0_1
        ))

        # Section 2: Additional biquad for steeper rolloff
        # Slightly different Q for Butterworth-like response
        Q2 = Q * 1.5
        alpha2 = sin_w0 / (2.0 * Q2)
        b0_2 = alpha2
        b1_2 = 0.0
        b2_2 = -alpha2
        a0_2 = 1.0 + alpha2
        a1_2 = -2.0 * cos_w0
        a2_2 = 1.0 - alpha2

        # Normalize section 2
        self.sections.append(Biquad(
            b0_2 / a0_2, b1_2 / a0_2, b2_2 / a0_2,
            a1_2 / a0_2, a2_2 / a0_2
        ))

    def process_sample(self, x: float) -> float:
        """Process single sample through filter cascade."""
        y = x
        for section in self.sections:
            y = section.process_sample(y)
        return y

    def process_block(self, samples: List[float]) -> List[float]:
        """Process list of samples."""
        return [self.process_sample(x) for x in samples]

    def reset(self):
        """Clear all filter states."""
        for section in self.sections:
            section.reset()
