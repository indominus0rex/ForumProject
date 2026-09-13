"""common/adaptive_gain.py — Adaptive gain controller for tremor suppression.

Continuously adjusts stimulation amplitude based on residual tremor
(measured after cancellation). Prevents over-stimulation and habituation.

Algorithm:
- Measure residual tremor (post-stimulation)
- If residual > target: increase gain
- If residual < target: decrease gain
- Rate-limited to prevent oscillation
"""

import math
from typing import Optional


class AdaptiveGain:
    """Adaptive gain controller for anti-phase stimulation."""

    def __init__(self, initial_gain: float = 0.5, min_gain: float = 0.0,
                 max_gain: float = 2.0, attack_rate: float = 0.01,
                 decay_rate: float = 0.005, target_residual: float = 0.3):
        """Initialize adaptive gain.

        Args:
            initial_gain: Starting gain value.
            min_gain: Minimum allowed gain.
            max_gain: Maximum allowed gain.
            attack_rate: Rate of gain increase (when residual too high).
            decay_rate: Rate of gain decrease (when residual too low).
            target_residual: Target residual tremor level (0-1).
        """
        self.gain = initial_gain
        self._initial_gain = initial_gain
        self.min_gain = min_gain
        self.max_gain = max_gain
        self.attack_rate = attack_rate
        self.decay_rate = decay_rate
        self.target_residual = target_residual

        # Smoothing
        self.residual_smoothed = 0.0
        self.alpha = 0.1  # EMA smoothing factor

        # Limits
        self.max_step = 0.05  # Max change per update

    def update(self, residual: float) -> float:
        """Update gain based on measured residual tremor.

        Args:
            residual: Measured residual tremor amplitude (0-1+).

        Returns:
            Updated gain value.
        """
        # Smooth residual
        self.residual_smoothed += self.alpha * (residual - self.residual_smoothed)

        # Error from target
        error = self.residual_smoothed - self.target_residual

        # Adjust gain
        if error > 0:
            # Residual too high: increase gain
            delta = self.attack_rate * error
        else:
            # Residual too low: decrease gain
            delta = self.decay_rate * error

        # Rate limit
        delta = max(-self.max_step, min(self.max_step, delta))

        # Apply
        self.gain += delta

        # Clamp
        self.gain = max(self.min_gain, min(self.max_gain, self.gain))

        return self.gain

    def reset(self):
        """Reset to initial state."""
        self.gain = self._initial_gain
        self.residual_smoothed = 0.0

    def get_gain(self) -> float:
        """Return current gain."""
        return self.gain

    def set_target_residual(self, target: float):
        """Update target residual level."""
        self.target_residual = target

    def set_rates(self, attack: float, decay: float):
        """Update attack/decay rates."""
        self.attack_rate = attack
        self.decay_rate = decay
