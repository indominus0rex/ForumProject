"""model.py — Baked logistic-regression weights.

Replace the placeholders below with the output of:
    python train_classifier.py

If WEIGHTS is None, embedded_main.py falls back to the heuristic classifier
from fft.py (peak in 3-12 Hz band, mag > threshold).

Order of CLASSES must match the order of rows in WEIGHTS and BIAS.
Order of FEATURE_MEAN / FEATURE_STD must match the order in feature_extract.compute().
"""

CLASSES = ["baseline", "kinetic", "postural", "rest"]

# 15 features in the order defined by feature_extract.compute()
FEATURE_MEAN = [0.0] * 15
FEATURE_STD = [1.0] * 15

# 4 classes x 15 features
WEIGHTS = None
BIAS = [0.0, 0.0, 0.0, 0.0]
