"""common/scaler.py — MicroPython z-normalisation (zero-mean, unit-variance scaling).

Provides apply() for feature scaling to match training preprocessing.
"""

from typing import List


def apply(x: List[float], mean: List[float], std: List[float]) -> List[float]:
    """Apply z-normalization: (x - mean) / std for each element.

    Args:
        x: Input feature vector.
        mean: Per-feature means from training.
        std: Per-feature standard deviations from training.

    Returns:
        Scaled feature vector. If std[i] <= 1e-9, output[i] = 0.0.
    """
    out = [0.0] * len(x)
    for i in range(len(x)):
        s = std[i] if i < len(std) else 1.0
        m = mean[i] if i < len(mean) else 0.0
        out[i] = (x[i] - m) / s if s > 1e-9 else 0.0
    return out