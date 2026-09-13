"""tests/test_adaptive_gain.py — Unit tests for adaptive gain controller."""

import sys

sys.path.insert(0, "firmware")

from common.adaptive_gain import AdaptiveGain


def test_initialization():
    """Adaptive gain initializes with correct defaults."""
    ag = AdaptiveGain(initial_gain=0.5, min_gain=0.0, max_gain=2.0)
    assert ag.gain == 0.5
    assert ag.min_gain == 0.0
    assert ag.max_gain == 2.0


def test_gain_increases_when_residual_high():
    """Gain increases when residual is above target."""
    ag = AdaptiveGain(initial_gain=0.5, target_residual=0.3)
    initial_gain = ag.gain

    # Residual above target
    for _ in range(50):
        ag.update(residual=0.8)

    assert ag.gain > initial_gain


def test_gain_decreases_when_residual_low():
    """Gain decreases when residual is below target."""
    ag = AdaptiveGain(initial_gain=0.5, target_residual=0.3)
    initial_gain = ag.gain

    # Residual below target
    for _ in range(50):
        ag.update(residual=0.1)

    assert ag.gain < initial_gain


def test_gain_clamped_at_max():
    """Gain never exceeds max_gain."""
    ag = AdaptiveGain(initial_gain=1.5, max_gain=2.0, target_residual=0.0)

    for _ in range(100):
        ag.update(residual=1.0)

    assert ag.gain <= 2.0


def test_gain_clamped_at_min():
    """Gain never goes below min_gain."""
    ag = AdaptiveGain(initial_gain=0.5, min_gain=0.1, target_residual=1.0)

    for _ in range(100):
        ag.update(residual=0.0)

    assert ag.gain >= 0.1


def test_reset():
    """Reset returns to initial state."""
    ag = AdaptiveGain(initial_gain=0.5)

    for _ in range(50):
        ag.update(residual=0.8)

    ag.reset()
    assert ag.gain == 0.5
    assert ag.residual_smoothed == 0.0


def test_set_target_residual():
    """Target residual can be updated."""
    ag = AdaptiveGain(target_residual=0.3)
    ag.set_target_residual(0.5)
    assert ag.target_residual == 0.5


def test_set_rates():
    """Attack/decay rates can be updated."""
    ag = AdaptiveGain()
    ag.set_rates(attack=0.02, decay=0.01)
    assert ag.attack_rate == 0.02
    assert ag.decay_rate == 0.01


def test_reset_restores_custom_initial():
    """Reset honors constructor initial_gain (review Finding 5)."""
    ag = AdaptiveGain(initial_gain=0.9)
    ag.reset()
    assert ag.gain == 0.9


if __name__ == "__main__":
    test_initialization()
    test_gain_increases_when_residual_high()
    test_gain_decreases_when_residual_low()
    test_gain_clamped_at_max()
    test_gain_clamped_at_min()
    test_reset()
    test_reset_restores_custom_initial()
    test_set_target_residual()
    test_set_rates()
    print("All adaptive gain tests passed!")
