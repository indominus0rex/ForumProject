"""tests/test_common.py — Unit tests for common/ modules."""

import sys
sys.path.insert(0, r"C:\ForumProject\firmware")

import math
from common import scaler, logreg, fft, feature_extract


def test_scaler_apply():
    """Test z-normalization with known mean/std."""
    x = [1.0, 2.0, 3.0]
    mean = [0.0, 1.0, 2.0]
    std = [1.0, 1.0, 1.0]
    out = scaler.apply(x, mean, std)
    assert out == [1.0, 1.0, 1.0]
    print("test_scaler_apply passed")


def test_scaler_zero_std():
    """Test scaler handles zero std gracefully."""
    x = [5.0, 5.0]
    mean = [0.0, 0.0]
    std = [0.0, 0.0]
    out = scaler.apply(x, mean, std)
    assert out == [0.0, 0.0]
    print("test_scaler_zero_std passed")


def test_logreg_forward():
    """Test logistic regression forward pass."""
    x = [1.0, 0.0]
    W = [[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.0, -1.0]]
    b = [0.0, 0.0, 0.0, 0.0]
    logits, probs = logreg.forward(x, W, b)
    assert len(logits) == 4
    assert len(probs) == 4
    assert abs(sum(probs) - 1.0) < 1e-6
    print("test_logreg_forward passed")


def test_logreg_argmax():
    """Test argmax returns correct index."""
    xs = [0.1, 0.5, 0.2, 0.2]
    assert logreg.argmax(xs) == 1
    print("test_logreg_argmax passed")


def test_fft_processor():
    """Test FFTProcessor with known sinusoid."""
    fs = 100.0
    n = 128
    proc = fft.FFTProcessor(num_samples=n)

    # 10 Hz sine wave
    signal = [math.sin(2 * math.pi * 10 * i / fs) for i in range(n)]
    freq, mag = proc.process_data(signal, fs)

    # Should detect ~10 Hz
    assert 9.0 < freq < 11.0
    assert mag > 0.1
    print(f"test_fft_processor passed: freq={freq:.2f}, mag={mag:.3f}")


def test_fft_noise_threshold():
    """Test FFT returns 0 for pure noise below threshold."""
    n = 128
    proc = fft.FFTProcessor(num_samples=n)
    signal = [0.0] * n
    freq, mag = proc.process_data(signal, 100.0)
    assert freq == 0.0
    assert mag == 0.0
    print("test_fft_noise_threshold passed")


def test_feature_extract_shape():
    """Test feature_extract returns 15 features."""
    window = [[0.1, 0.2, 0.3] for _ in range(128)]
    feats = feature_extract.compute(window, fs=100.0, n=128)
    assert len(feats) == 15
    print("test_feature_extract_shape passed")


def test_feature_extract_interleaved():
    """Test feature_extract handles interleaved input."""
    window = [0.1, 0.2, 0.3] * 128  # flat interleaved
    feats = feature_extract.compute(window, fs=100.0, n=128)
    assert len(feats) == 15
    print("test_feature_extract_interleaved passed")


def test_feature_extract_dominant_axis():
    """Test dominant_axis detection."""
    # Z-axis dominant (varying z, constant x,y)
    window = [[0.0, 0.0, float(i % 2)] for i in range(128)]
    feats = feature_extract.compute(window, fs=100.0, n=128)
    assert feats[9] == 2.0  # dominant_axis index 2 = z
    print("test_feature_extract_dominant_axis passed")


def run_all():
    test_scaler_apply()
    test_scaler_zero_std()
    test_logreg_forward()
    test_logreg_argmax()
    test_fft_processor()
    test_fft_noise_threshold()
    test_feature_extract_shape()
    test_feature_extract_interleaved()
    test_feature_extract_dominant_axis()
    print("\nAll tests passed!")


if __name__ == "__main__":
    run_all()