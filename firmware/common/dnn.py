"""common/dnn.py — MicroPython 2-layer MLP forward pass.

Hidden layer uses ReLU, output layer uses softmax. Pure-Python loops,
no allocations beyond outputs — same style as common/logreg.py.

Generate weights with:
    python host_scripts/train_classifier.py --dnn sessions/*.csv
and paste the output into common/model_dnn.py.
"""

import math
from typing import List, Tuple


def relu(xs: List[float]) -> List[float]:
    """Rectified linear unit, elementwise."""
    return [v if v > 0.0 else 0.0 for v in xs]


def forward(
    x: List[float],
    W1: List[List[float]],
    b1: List[float],
    W2: List[List[float]],
    b2: List[float],
) -> Tuple[List[float], List[float]]:
    """Two-layer forward pass: hidden = relu(W1 x + b1), out = softmax(W2 hidden + b2).

    Args:
        x: Input feature vector (length n_features).
        W1: Hidden weights (n_hidden x n_features).
        b1: Hidden bias (n_hidden).
        W2: Output weights (n_classes x n_hidden).
        b2: Output bias (n_classes).

    Returns:
        Tuple of (logits, probs) where probs is softmax-normalized.
    """
    n_hidden = len(b1)
    hidden = [0.0] * n_hidden
    for i in range(n_hidden):
        s = b1[i]
        wi = W1[i]
        for j in range(len(x)):
            s += wi[j] * x[j]
        hidden[i] = s if s > 0.0 else 0.0

    k = len(b2)
    logits = [0.0] * k
    for i in range(k):
        s = b2[i]
        wi = W2[i]
        for j in range(n_hidden):
            s += wi[j] * hidden[j]
        logits[i] = s

    # Numerically stable softmax
    m = max(logits) if logits else 0.0
    exps = [math.exp(l - m) for l in logits]
    z = sum(exps)
    if z <= 0.0:
        z = 1.0
    probs = [e / z for e in exps]
    return logits, probs
