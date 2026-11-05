"""tests/test_suppress.py — Unit tests for suppress stage."""

import sys
import math

sys.path.insert(0, "firmware")

from stages.suppress import SuppressStage


def test_suppress_initialization():
    """Suppress stage initializes correctly."""
    stage = SuppressStage(fs=100.0, pll_bandwidth=1.0, initial_gain=0.5)
    assert stage.fs == 100.0
    assert stage.adaptive_gain.gain == 0.5


def test_process_sample_returns_duty():
    """Process sample returns PWM duty cycle."""
    stage = SuppressStage(fs=100.0)

    # Process a few samples
    for i in range(10):
        duty = stage.process_sample(0.1, 0.2, 0.9)
        assert 0 <= duty <= 1023


def test_process_frame():
    """Process frame adds suppression data."""
    stage = SuppressStage(fs=100.0)

    frame = {"x": 0.1, "y": 0.2, "z": 0.9}
    result = stage.process(frame)

    assert "suppress_duty" in result
    assert "pll_phase" in result
    assert "pll_freq" in result
    assert "pll_locked" in result
    assert "adaptive_gain" in result


def test_pll_tracks_tremor():
    """PLL locks onto simulated tremor signal."""
    stage = SuppressStage(fs=100.0, pll_bandwidth=1.0)

    freq = 6.0
    # Simulate 3 seconds of tremor
    for i in range(300):
        t = i / 100.0
        # Tremor signal + gravity
        x = 0.1 * math.sin(2 * math.pi * freq * t)
        y = 0.05 * math.sin(2 * math.pi * freq * t)
        z = 1.0 + 0.15 * math.sin(2 * math.pi * freq * t)
        duty = stage.process_sample(x, y, z)

    # PLL should be locked and tracking ~6 Hz
    assert stage.pll.freq > 4.0
    assert stage.pll.freq < 8.0


def test_reset():
    """Reset clears all state."""
    stage = SuppressStage(fs=100.0)

    for i in range(100):
        stage.process_sample(0.1, 0.2, 0.9)

    stage.reset()
    assert stage.pll.locked is False
    assert stage._sample_count == 0
    assert stage._last_duty == 0


def test_get_status():
    """Get status returns current state."""
    stage = SuppressStage(fs=100.0)

    for i in range(50):
        stage.process_sample(0.1, 0.2, 0.9)

    status = stage.get_status()
    assert "pll_locked" in status
    assert "pll_freq" in status
    assert "adaptive_gain" in status


def test_x_only_tremor_tracks_6hz():
    """Dominant-axis frontend: x-only 6 Hz tremor tracks (review Finding 3)."""
    stage = SuppressStage(fs=100.0, pll_bandwidth=1.0)
    for i in range(300):
        t = i / 100.0
        stage.process_sample(0.2 * math.sin(2 * math.pi * 6.0 * t), 0.0, 1.0)
    assert stage.pll.locked
    assert abs(stage.pll.freq - 6.0) < 0.5


def test_chain_4hz_locks_in_budget():
    stage = SuppressStage(fs=100.0, pll_bandwidth=1.0)
    locked_at = None
    for i in range(1200):
        t = i / 100.0
        stage.process_sample(0.15 * math.sin(2 * math.pi * 4.0 * t), 0.0, 1.0)
        if stage.pll.locked:
            locked_at = i + 1
            break
    assert locked_at is not None and locked_at <= 900, "chain 4 Hz locked at %s" % locked_at
    assert abs(stage.pll.freq - 4.0) < 0.5


def test_chain_8hz_locks_in_budget():
    stage = SuppressStage(fs=100.0, pll_bandwidth=1.0)
    locked_at = None
    for i in range(1400):
        t = i / 100.0
        stage.process_sample(0.15 * math.sin(2 * math.pi * 8.0 * t), 0.0, 1.0)
        if stage.pll.locked:
            locked_at = i + 1
            break
    assert locked_at is not None and locked_at <= 1100, "chain 8 Hz locked at %s" % locked_at
    assert abs(stage.pll.freq - 8.0) < 0.5


if __name__ == "__main__":
    test_suppress_initialization()
    test_process_sample_returns_duty()
    test_process_frame()
    test_pll_tracks_tremor()
    test_x_only_tremor_tracks_6hz()
    test_chain_4hz_locks_in_budget()
    test_chain_8hz_locks_in_budget()
    test_reset()
    test_get_status()
    print("All suppress stage tests passed!")
