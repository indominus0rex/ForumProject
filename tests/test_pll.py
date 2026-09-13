"""tests/test_pll.py — Unit tests for PLL phase tracker."""

import sys
import math

# Add firmware to path for testing on host
sys.path.insert(0, "firmware")

from common.pll import PLL


def test_pll_initialization():
    """PLL initializes with correct default state."""
    pll = PLL(fs=100.0, center_freq=6.0, bandwidth=0.5)
    assert pll.freq == 6.0
    assert pll.phase == 0.0
    assert pll.locked is False
    assert pll.lock_count == 0


def test_pll_frequency_tracking():
    """PLL locks onto a 6 Hz sinusoid."""
    fs = 100.0
    freq = 6.0
    pll = PLL(fs=fs, center_freq=6.0, bandwidth=0.5)

    # Generate 2 seconds of 6 Hz sine
    n_samples = int(2 * fs)
    for i in range(n_samples):
        t = i / fs
        sample = math.sin(2 * math.pi * freq * t)
        phase, tracked_freq, _ = pll.update(sample)

    # After 1 second, should be close to 6 Hz
    assert abs(pll.freq - freq) < 0.5, f"Expected ~6 Hz, got {pll.freq} Hz"
    assert pll.locked is True


def test_pll_phase_wrapping():
    """PLL phase wraps correctly at 2*pi."""
    pll = PLL(fs=100.0, center_freq=6.0)

    # Run enough samples to accumulate phase
    for i in range(500):
        sample = 0.5  # DC input just to advance phase
        phase, _, _ = pll.update(sample)
        assert 0 <= phase < 2 * math.pi, f"Phase {phase} out of range"


def test_pll_frequency_clamping():
    """PLL frequency stays within 3-12 Hz band."""
    pll = PLL(fs=100.0, center_freq=6.0)

    # Drive with extreme input
    for i in range(100):
        pll.update(0.0)

    assert 3.0 <= pll.freq <= 12.0


def test_pll_reset():
    """PLL reset returns to initial state."""
    pll = PLL(fs=100.0, center_freq=6.0)

    for i in range(100):
        pll.update(0.5)

    pll.reset()
    assert pll.phase == 0.0
    assert pll.freq == 6.0
    assert pll.locked is False
    assert pll.lock_count == 0


def test_pll_period_calculation():
    """PLL period calculation is correct."""
    pll = PLL(fs=100.0, center_freq=5.0)
    period = pll.get_period_samples()
    assert abs(period - 20.0) < 0.01  # 100/5 = 20 samples


def test_pll_acquires_off_center():
    """PLL pulls in to 5 Hz and 7 Hz within 6 s (review Blocker 1)."""
    for f0 in (5.0, 7.0):
        pll = PLL(fs=100.0, center_freq=6.0, bandwidth=1.0)
        for i in range(600):
            pll.update(math.sin(2 * math.pi * f0 * (i / 100.0)))
        assert pll.locked, "never locked to %s Hz" % f0
        assert abs(pll.freq - f0) < 0.5, "target %s, tracked %s" % (f0, pll.freq)


def test_pll_no_false_lock():
    """PLL must never report lock >1 Hz from the true tone (review Blocker 2)."""
    for f0 in (4.0, 8.0, 12.0):
        pll = PLL(fs=100.0, center_freq=6.0, bandwidth=1.0)
        for i in range(600):
            pll.update(math.sin(2 * math.pi * f0 * (i / 100.0)))
        assert not (pll.locked and abs(pll.freq - f0) > 1.0), \
            "false lock: target %s, claims %s" % (f0, pll.freq)


if __name__ == "__main__":
    test_pll_initialization()
    test_pll_frequency_tracking()
    test_pll_phase_wrapping()
    test_pll_frequency_clamping()
    test_pll_reset()
    test_pll_period_calculation()
    test_pll_acquires_off_center()
    test_pll_no_false_lock()
    print("All PLL tests passed!")
