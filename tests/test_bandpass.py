"""tests/test_bandpass.py — Unit tests for bandpass filter."""

import sys
import math

sys.path.insert(0, "firmware")

from common.bandpass import BandpassFilter, Biquad


def test_biquad_initialization():
    """Biquad initializes with correct coefficients."""
    bq = Biquad(b0=0.5, b1=0.25, b2=0.1, a1=-0.3, a2=0.2)
    assert bq.b0 == 0.5
    assert bq.b1 == 0.25
    assert bq.b2 == 0.1
    assert bq.a1 == -0.3
    assert bq.a2 == 0.2


def test_biquad_reset():
    """Biquad reset clears state."""
    bq = Biquad(b0=0.5, b1=0.25, b2=0.1, a1=-0.3, a2=0.2)
    bq.process_sample(1.0)
    bq.reset()
    assert bq.x1 == 0.0
    assert bq.x2 == 0.0
    assert bq.y1 == 0.0
    assert bq.y2 == 0.0


def test_bandpass_initialization():
    """Bandpass filter initializes with correct parameters."""
    bp = BandpassFilter(fs=100.0, low_hz=3.0, high_hz=12.0)
    assert bp.fs == 100.0
    assert bp.low_hz == 3.0
    assert bp.high_hz == 12.0
    assert len(bp.sections) > 0


def test_bandpass_attenuates_dc():
    """Bandpass filter attenuates DC (0 Hz)."""
    bp = BandpassFilter(fs=100.0, low_hz=3.0, high_hz=12.0)

    # Process DC signal
    for _ in range(50):
        output = bp.process_sample(1.0)

    # DC should be attenuated
    assert abs(output) < 0.5


def test_bandpass_passes_center_freq():
    """Bandpass filter passes center frequency."""
    bp = BandpassFilter(fs=100.0, low_hz=3.0, high_hz=12.0)

    # Center freq = sqrt(3*12) ≈ 6 Hz
    freq = math.sqrt(3.0 * 12.0)

    # Generate and filter signal
    for i in range(200):
        t = i / 100.0
        sample = math.sin(2 * math.pi * freq * t)
        output = bp.process_sample(sample)

    # After settling, output should be significant
    assert abs(output) > 0.1


def test_bandpass_reset():
    """Bandpass reset clears all states."""
    bp = BandpassFilter(fs=100.0, low_hz=3.0, high_hz=12.0)

    for _ in range(50):
        bp.process_sample(1.0)

    bp.reset()
    for section in bp.sections:
        assert section.x1 == 0.0
        assert section.y1 == 0.0


def test_bandpass_process_block():
    """Bandpass processes blocks of samples."""
    bp = BandpassFilter(fs=100.0, low_hz=3.0, high_hz=12.0)

    samples = [math.sin(2 * math.pi * 6.0 * i / 100.0) for i in range(100)]
    outputs = bp.process_block(samples)

    assert len(outputs) == 100


if __name__ == "__main__":
    test_biquad_initialization()
    test_biquad_reset()
    test_bandpass_initialization()
    test_bandpass_attenuates_dc()
    test_bandpass_passes_center_freq()
    test_bandpass_reset()
    test_bandpass_process_block()
    print("All bandpass filter tests passed!")
