"""common/model.py — Baked logistic-regression model weights for embedded inference.

Replace the placeholders below with the output of:
    python host_scripts/train_classifier.py

If WEIGHTS is None, the pipeline falls back to the heuristic classifier
(peak in 3-12 Hz band, magnitude > threshold).

Order of CLASSES must match the order of rows in WEIGHTS and BIAS.
Order of FEATURE_MEAN / FEATURE_STD must match the order in feature_extract.compute().
"""

from typing import List, Optional

# Class labels in order matching WEIGHTS rows
CLASSES: List[str] = ["baseline", "kinetic", "postural", "rest"]

# 15 features in the order defined by feature_extract.compute()
FEATURE_MEAN: List[float] = [0.0] * 15
FEATURE_STD: List[float] = [1.0] * 15

# 4 classes x 15 features — populate from train_classifier.py output
WEIGHTS: Optional[List[List[float]]] = None

# 4 classes
BIAS: List[float] = [0.0, 0.0, 0.0, 0.0]