"""common/logreg.py — MicroPython logistic-regression forward pass.

Provides forward() for multi-class logistic regression inference
and argmax() for class prediction.
"""

import math
from typing import List, Tuple


def forward(
    x: List[float],
    W: List[List[float]],
    b: List[float]
) -> Tuple[List[float], List[float]]:
    """Compute logits and softmax probabilities for multi-class logistic regression.

    Args:
        x: Input feature vector (length n_features).
        W: Weight matrix (n_classes x n_features).
        b: Bias vector (n_classes).

    Returns:
        Tuple of (logits, probs) where probs is softmax-normalized.
    """
    k = len(b)
    logits = [0.0] * k
    for i in range(k):
        s = b[i]
        wi = W[i]
        for j in range(len(x)):
            s += wi[j] * x[j]
        logits[i] = s

    # Numerically stable softmax
    m = max(logits) if logits else 0.0
    exps = [math.exp(l - m) for l in logits]
    z = sum(exps)
    if z <= 0.0:
        z = 1.0
    probs = [e / z for e in exps]
    return logits, probs


def argmax(xs: List[float]) -> int:
    """Return index of maximum value in list."""
    bi = 0
    bv = xs[0]
    for i in range(1, len(xs)):
        if xs[i] > bv:
            bv = xs[i]
            bi = i
    return bi