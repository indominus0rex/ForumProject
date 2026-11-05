"""common/model_dnn.py — Baked 2-layer MLP weights for embedded DNN inference.

Replace the placeholders below with the output of:
    python host_scripts/train_classifier.py --dnn sessions/*.csv

If W1 is None, the pipeline falls back to the heuristic classifier
(peak in 3-12 Hz band, magnitude > threshold) — same contract as model.py.

Shapes: W1 = N_HIDDEN x N_FEATURES, b1 = N_HIDDEN,
        W2 = N_CLASSES x N_HIDDEN, b2 = N_CLASSES.
Order of CLASSES must match rows of W2 and b2.
Order of FEATURE_MEAN / FEATURE_STD must match feature_extract.compute().
"""

from typing import List, Optional

# Class labels in order matching W2 rows
CLASSES: List[str] = ['baseline', 'kinetic', 'postural', 'rest']

# 15 features in the order defined by feature_extract.compute()
N_FEATURES = 15
N_HIDDEN = 16
N_CLASSES = 4

FEATURE_MEAN: List[float] = [0.396724, 0.236842, 0.003154, 1.404442, 0.00146, 0.000446, 0.000227, 8.1e-05, 0.321774, 0.90446, 0.482401, 0.472386, 0.0, 1.105719, 376.374583]
FEATURE_STD: List[float] = [0.078415, 0.046808, 0.002381, 0.99636, 0.001634, 0.000492, 0.000254, 0.000111, 0.137103, 0.293959, 0.135533, 0.128015, 1.0, 0.471971, 630.082791]

# N_HIDDEN x N_FEATURES — populate from train_classifier.py --dnn output
# TODO: retrain with Option A+ET pilot data (thumb phalanx + index phalanx)
W1: Optional[List[List[float]]] = None

# N_CLASSES x N_HIDDEN — populate from train_classifier.py --dnn output
W2: Optional[List[List[float]]] = None
