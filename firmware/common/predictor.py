"""common/predictor.py — Phase prediction for anti-phase cancellation.

Predicts tremor phase N milliseconds in the future to account for
mechanical delay (LRA response time) and computational delay.

Formula: φ_pred(t+Δt) = φ + 2π·f·Δt
"""

import math
from typing import Tuple


class PhasePredictor:
    """Predicts future phase of tremor oscillation."""

    def __init__(self, fs: float = 100.0, prediction_ms: float = 15.0):
        """Initialize predictor.

        Args:
            fs: Sampling frequency in Hz.
            prediction_ms: How far ahead to predict (milliseconds).
                          15ms accounts for LRA mechanical delay + computation.
        """
        self.fs = fs
        self.prediction_ms = prediction_ms
        self.dt = prediction_ms / 1000.0  # Convert to seconds

    def predict(self, phase: float, freq: float) -> float:
        """Predict phase at t + dt.

        Args:
            phase: Current phase (radians, 0 to 2*pi).
            freq: Current frequency (Hz).

        Returns:
            Predicted phase (radians, 0 to 2*pi).
        """
        # Predict future phase
        phase_pred = phase + 2.0 * math.pi * freq * self.dt

        # Wrap to [0, 2*pi)
        while phase_pred >= 2.0 * math.pi:
            phase_pred -= 2.0 * math.pi
        while phase_pred < 0.0:
            phase_pred += 2.0 * math.pi

        return phase_pred

    def predict_with_amplitude(self, phase: float, freq: float,
                                amplitude: float) -> Tuple[float, float]:
        """Predict phase and amplitude at t + dt.

        Args:
            phase: Current phase (radians).
            freq: Current frequency (Hz).
            amplitude: Current amplitude estimate.

        Returns:
            Tuple of (predicted_phase, predicted_amplitude).
        """
        phase_pred = self.predict(phase, freq)
        # Amplitude prediction: assume constant for now
        # Future: could use amplitude decay/growth model
        amplitude_pred = amplitude
        return phase_pred, amplitude_pred

    def set_prediction_ms(self, ms: float):
        """Update prediction horizon."""
        self.prediction_ms = ms
        self.dt = ms / 1000.0

    def get_prediction_samples(self) -> float:
        """Return prediction horizon in samples."""
        return self.dt * self.fs
