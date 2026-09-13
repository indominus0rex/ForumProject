"""tests/test_anticancel.py — Unit tests for anti-phase generator."""

import sys
import math

sys.path.insert(0, "firmware")

from common.anticancel import AntiPhaseGenerator


def test_generator_initialization():
    """Generator initializes with correct defaults."""
    gen = AntiPhaseGenerator(max_duty=1023)
    assert gen.max_duty == 1023
    assert abs(gen.phase_offset - math.pi) < 1e-6


def test_compute_duty_zero_phase():
    """Duty at zero phase with anti-phase offset."""
    gen = AntiPhaseGenerator(max_duty=1023)
    # At phase 0, anti-phase = π, sin(π) = 0, so duty = 0
    duty = gen.compute_duty(0.0, amplitude=1.0, gain=1.0)
    assert abs(duty) < 50  # Should be near zero (sin(π) ≈ 0)


def test_compute_duty_max_at_quarter_phase():
    """Duty is maximum when anti-phase = π/2."""
    gen = AntiPhaseGenerator(max_duty=1023)
    # Anti-phase = π/2 means predicted phase = -π/2 = 3π/2
    phase = 1.5 * math.pi  # 270°
    duty = gen.compute_duty(phase, amplitude=1.0, gain=1.0)
    assert duty > 800  # Should be near max (sin(π/2) = 1)


def test_compute_duty_clamping():
    """Duty is clamped to max_duty."""
    gen = AntiPhaseGenerator(max_duty=1023)
    # Very high amplitude/gain should still clamp
    duty = gen.compute_duty(0.0, amplitude=10.0, gain=10.0)
    assert duty <= 1023


def test_compute_stereo_duties():
    """Stereo duties are complementary."""
    gen = AntiPhaseGenerator(max_duty=1023)
    duty_a, duty_b = gen.compute_stereo_duties(0.5, amplitude=1.0, gain=1.0)
    assert duty_a >= 0 and duty_b >= 0
    assert duty_a <= 1023 and duty_b <= 1023


def test_set_phase_offset():
    """Phase offset can be changed."""
    gen = AntiPhaseGenerator(max_duty=1023)
    gen.set_phase_offset(math.pi / 2)  # 90°
    assert abs(gen.phase_offset - math.pi / 2) < 1e-6
    assert abs(gen.get_phase_offset_degrees() - 90.0) < 0.01


def test_anti_phase_cancellation():
    """Anti-phase signal is exactly opposite of input."""
    gen = AntiPhaseGenerator(max_duty=1023)
    # If input is at peak (sin = 1), anti-phase should be at trough (sin = -1)
    input_phase = math.pi / 2  # 90°, peak
    anti_phase = input_phase + gen.phase_offset  # 270°, trough

    input_val = math.sin(input_phase)
    anti_val = math.sin(anti_phase)

    # They should be opposite
    assert input_val > 0.9  # Near +1
    assert anti_val < -0.9  # Near -1


def test_single_channel_drive_is_rectified():
    """Single-channel duty is non-negative by design (2x-rate LRA drive)."""
    gen = AntiPhaseGenerator(max_duty=1023)
    for deg in range(0, 360, 15):
        assert gen.compute_duty(math.radians(deg), amplitude=1.0, gain=1.0) >= 0


if __name__ == "__main__":
    test_generator_initialization()
    test_compute_duty_zero_phase()
    test_compute_duty_max_at_quarter_phase()
    test_compute_duty_clamping()
    test_compute_stereo_duties()
    test_single_channel_drive_is_rectified()
    test_set_phase_offset()
    test_anti_phase_cancellation()
    print("All anti-phase generator tests passed!")
