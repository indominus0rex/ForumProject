"""tests/test_predictor.py — Unit tests for phase predictor."""

import sys
import math

sys.path.insert(0, "firmware")

from common.predictor import PhasePredictor


def test_predictor_initialization():
    """Predictor initializes with correct parameters."""
    pred = PhasePredictor(fs=100.0, prediction_ms=15.0)
    assert pred.fs == 100.0
    assert pred.prediction_ms == 15.0
    assert abs(pred.dt - 0.015) < 1e-6


def test_predict_phase_advances():
    """Predicted phase is ahead of current phase."""
    pred = PhasePredictor(fs=100.0, prediction_ms=15.0)
    freq = 6.0
    phase = 0.0

    predicted = pred.predict(phase, freq)

    # At 6 Hz, 15ms = 0.09 cycles = 0.565 radians
    expected_advance = 2 * math.pi * freq * 0.015
    assert abs(predicted - expected_advance) < 0.01


def test_predict_phase_wrapping():
    """Predicted phase wraps at 2*pi."""
    pred = PhasePredictor(fs=100.0, prediction_ms=15.0)
    freq = 6.0
    # Start near end of cycle
    phase = 2 * math.pi - 0.1

    predicted = pred.predict(phase, freq)

    assert 0 <= predicted < 2 * math.pi


def test_predict_with_amplitude():
    """Predict with amplitude returns both values."""
    pred = PhasePredictor(fs=100.0, prediction_ms=15.0)
    phase = 1.0
    freq = 5.0
    amplitude = 2.5

    pred_phase, pred_amp = pred.predict_with_amplitude(phase, freq, amplitude)

    assert 0 <= pred_phase < 2 * math.pi
    assert pred_amp == amplitude  # Currently constant


def test_set_prediction_ms():
    """Update prediction horizon."""
    pred = PhasePredictor(fs=100.0, prediction_ms=15.0)
    pred.set_prediction_ms(20.0)

    assert pred.prediction_ms == 20.0
    assert abs(pred.dt - 0.020) < 1e-6


def test_get_prediction_samples():
    """Prediction horizon in samples."""
    pred = PhasePredictor(fs=100.0, prediction_ms=15.0)
    samples = pred.get_prediction_samples()
    assert abs(samples - 1.5) < 0.01  # 15ms @ 100 Hz = 1.5 samples


if __name__ == "__main__":
    test_predictor_initialization()
    test_predict_phase_advances()
    test_predict_phase_wrapping()
    test_predict_with_amplitude()
    test_set_prediction_ms()
    test_get_prediction_samples()
    print("All predictor tests passed!")
