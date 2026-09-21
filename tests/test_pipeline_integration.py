"""tests/test_pipeline_integration.py — Full HSP pipeline integration test.

Runs all 8 stages in STAGE_ORDER on a synthetic 6 Hz tremor window
and verifies the frame has the expected keys at each step.
"""

import sys
import math
import time as _time

# Mock MicroPython's time.ticks_ms() for host-side testing
if not hasattr(_time, "ticks_ms"):
    _time.ticks_ms = lambda: int(_time.time() * 1000)

sys.path.insert(0, "firmware")

from stages import STAGE_ORDER
from stages.safety import SafetyStage
from stages.sensor import SensorStage
from stages.stationarity import StationarityStage
from stages.quality import QualityStage
from stages.bandpass import BandpassStage
from stages.fft import FFTStage
from stages.features import FeaturesStage
from stages.audit import AuditStage


def make_tremor_window(freq=6.0, n=128, fs=100.0):
    """Generate a synthetic tremor window (6 Hz sine on x-axis, gravity on z)."""
    return [[math.sin(2 * math.pi * freq * i / fs), 0.0, 1.0] for i in range(n)]


def test_full_pipeline():
    """Run all HSP stages in order on synthetic tremor data."""
    window = make_tremor_window()
    frame = {
        "window": window,
        "x": window[-1][0],
        "y": window[-1][1],
        "z": window[-1][2],
        "now_us": 1_000_000,
        "prev_us": 990_000,
        "sample_errors": 0,
        "label": "kinetic",  # audit stage logs when label is present
    }

    stages = {
        "safety": SafetyStage(),
        "sensor": SensorStage(sensor=None, sample_buf=window, samples=128),
        "stationarity": StationarityStage(window_len=128),
        "quality": QualityStage(),
        "bandpass": BandpassStage(fs=100.0, low_hz=3.0, high_hz=12.0),
        "fft": FFTStage(samples=128, fs=100.0),
        "features": FeaturesStage(fs=100.0, n=128),
        "audit": AuditStage(capacity=32),
    }

    for name in STAGE_ORDER:
        stage = stages[name]
        frame = stage.process(frame)
        assert frame.get("safe", True), f"pipeline broke at {name}"

    # Verify expected keys exist
    assert "dominant_freq" in frame, "fft stage missing"
    assert "features" in frame, "features stage missing"
    assert len(frame["features"]) == 15, "expected 15 features"
    assert "audit_log" in frame, "audit stage missing"
    assert len(frame["audit_log"]) == 1, "audit should have 1 entry"

    # Verify dominant frequency is in tremor band
    assert 3.0 <= frame["dominant_freq"] <= 12.0, \
        f"dominant_freq {frame['dominant_freq']} outside tremor band"

    print("Full pipeline integration test passed!")


if __name__ == "__main__":
    test_full_pipeline()
