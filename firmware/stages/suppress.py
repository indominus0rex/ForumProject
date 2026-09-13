"""stages/suppress.py — Main suppression pipeline stage.

Orchestrates the PLL-based anti-phase cancellation pipeline:
  sensor data → bandpass filter → PLL phase tracking → phase predictor
  → anti-phase PWM generator → adaptive gain → LRA output

This stage replaces the old FFT→features→classify→state_machine→haptic chain
with a direct phase-locked suppression approach.
"""

import math
from typing import Optional
from stages import Frame
from common.bandpass import BandpassFilter
from common.pll import PLL
from common.predictor import PhasePredictor
from common.anticancel import AntiPhaseGenerator
from common.adaptive_gain import AdaptiveGain


class SuppressStage:
    """PLL-based anti-phase tremor suppression stage."""

    def __init__(self, fs: float = 100.0, pll_bandwidth: float = 1.0,
                 prediction_ms: float = 15.0, initial_gain: float = 0.5):
        """Initialize suppression pipeline.

        Defaults mirror common/config.py (PLL_BANDWIDTH_HZ, PREDICTION_MS,
        ADAPTIVE_GAIN_INITIAL) — keep in sync manually (MicroPython-safe).

        Args:
            fs: Sampling frequency in Hz.
            pll_bandwidth: PLL loop bandwidth in Hz.
            prediction_ms: Phase prediction horizon in milliseconds.
            initial_gain: Initial adaptive gain.
        """
        self.fs = fs

        # Signal conditioning: bandpass filter 3-12 Hz
        self.bandpass = BandpassFilter(fs=fs, low_hz=3.0, high_hz=12.0)

        # Canonical frontend: dominant-axis projection + normalized PLL
        # drive (common/frontend.py). Gating stays with callers (b7 combo /
        # ActuationStage), so duty is still computed unconditionally here.
        from common.frontend import AxisFrontend
        self._frontend = AxisFrontend(self.bandpass)

        # Phase-locked loop for tremor tracking
        self.pll = PLL(fs=fs, center_freq=6.0, bandwidth=pll_bandwidth)

        # Phase predictor (accounts for mechanical delay)
        self.predictor = PhasePredictor(fs=fs, prediction_ms=prediction_ms)

        # Anti-phase PWM generator
        self.anticancel = AntiPhaseGenerator(max_duty=1023)

        # Adaptive gain controller
        self.adaptive_gain = AdaptiveGain(
            initial_gain=initial_gain,
            min_gain=0.0,
            max_gain=2.0,
            target_residual=0.3
        )

        # State
        self._sample_count = 0
        self._last_duty = 0

    def process_sample(self, x: float, y: float, z: float) -> int:
        """Process single IMU sample through suppression pipeline.

        Args:
            x: X-axis acceleration (g).
            y: Y-axis acceleration (g).
            z: Z-axis acceleration (g).

        Returns:
            PWM duty cycle for LRA (0-1023).
        """
        pll_in, filtered, amplitude = self._frontend.step(x, y, z)

        # PLL phase tracking
        phase, freq, _ = self.pll.update(pll_in)

        # Predict future phase (account for mechanical delay)
        predicted_phase = self.predictor.predict(phase, freq)

        # Compute anti-phase PWM duty
        gain = self.adaptive_gain.get_gain()
        duty = self.anticancel.compute_duty(predicted_phase, amplitude, gain)

        # Adaptive gain update (using residual as feedback)
        # Residual = what's left after cancellation (approximated by amplitude)
        self.adaptive_gain.update(amplitude)

        self._sample_count += 1
        self._last_duty = duty

        return duty

    def process(self, frame: Frame) -> Frame:
        """Process frame (for pipeline integration).

        Args:
            frame: Pipeline frame dict with 'x', 'y', 'z' keys.

        Returns:
            Modified frame with 'suppress_duty' and 'pll_state' keys.
        """
        x = frame.get("x", 0.0)
        y = frame.get("y", 0.0)
        z = frame.get("z", 0.0)

        duty = self.process_sample(x, y, z)

        # Store results in frame
        frame["suppress_duty"] = duty
        frame["pll_phase"] = self.pll.phase
        frame["pll_freq"] = self.pll.freq
        frame["pll_locked"] = self.pll.locked
        frame["adaptive_gain"] = self.adaptive_gain.get_gain()

        return frame

    def reset(self):
        """Reset all pipeline components."""
        self._frontend.reset()
        self.pll.reset()
        self.adaptive_gain.reset()
        self._sample_count = 0
        self._last_duty = 0

    def get_status(self) -> dict:
        """Return current pipeline status."""
        return {
            "pll_locked": self.pll.locked,
            "pll_freq": self.pll.freq,
            "pll_phase": self.pll.phase,
            "adaptive_gain": self.adaptive_gain.get_gain(),
            "sample_count": self._sample_count,
            "last_duty": self._last_duty,
        }
