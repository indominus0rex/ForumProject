"""common/anticancel.py — Anti-phase PWM generator for tremor cancellation.

Takes predicted tremor phase and generates PWM signals at exactly
180° offset (anti-phase) to cancel the tremor oscillation.

Principle: if tremor is at phase φ, push back at phase φ + π.
"""

import math
from typing import Tuple


class AntiPhaseGenerator:
    """Generates anti-phase PWM signals for tremor cancellation."""

    def __init__(self, max_duty: int = 1023):
        """Initialize generator.

        Args:
            max_duty: Maximum PWM duty cycle (10-bit = 1023).
        """
        self.max_duty = max_duty
        self.phase_offset = math.pi  # 180° = anti-phase

    def compute_duty(self, predicted_phase: float, amplitude: float,
                     gain: float = 1.0) -> int:
        """Compute PWM duty cycle for anti-phase cancellation.

        Args:
            predicted_phase: Predicted tremor phase (radians).
            amplitude: Predicted tremor amplitude (0-1+).
            gain: Adaptive gain multiplier.

        Returns:
            PWM duty cycle (0 to max_duty).

        Output is abs()-rectified by design (single-channel LRA fires both
        half-cycles); use compute_stereo_duties for push-pull.
        """
        # Anti-phase: target = predicted_phase + π
        anti_phase = predicted_phase + self.phase_offset

        # PWM duty proportional to sin of anti-phase
        # This creates a counter-force at the opposite phase
        duty_float = math.sin(anti_phase) * amplitude * gain * self.max_duty

        # Clamp to valid range
        duty = int(duty_float)
        duty = max(-self.max_duty, min(self.max_duty, duty))

        return abs(duty)

    def compute_stereo_duties(self, predicted_phase: float, amplitude: float,
                               gain: float = 1.0) -> Tuple[int, int]:
        """Compute complementary PWM duties for push-pull cancellation.

        Args:
            predicted_phase: Predicted tremor phase (radians).
            amplitude: Predicted tremor amplitude.
            gain: Adaptive gain multiplier.

        Returns:
            Tuple of (duty_a, duty_b) for complementary actuators.
        """
        anti_phase = predicted_phase + self.phase_offset

        # Complementary signals (push-pull)
        duty_a_float = math.sin(anti_phase) * amplitude * gain * self.max_duty
        duty_b_float = -duty_a_float  # Inverted

        duty_a = int(duty_a_float)
        duty_b = int(duty_b_float)

        # Clamp
        duty_a = max(-self.max_duty, min(self.max_duty, duty_a))
        duty_b = max(-self.max_duty, min(self.max_duty, duty_b))

        return abs(duty_a), abs(duty_b)

    def set_phase_offset(self, offset_rad: float):
        """Set custom phase offset (default π = 180°).

        Args:
            offset_rad: Phase offset in radians.
        """
        self.phase_offset = offset_rad

    def get_phase_offset_degrees(self) -> float:
        """Return phase offset in degrees."""
        return math.degrees(self.phase_offset)
