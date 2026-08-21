"""logreg.py — MicroPython logistic-regression forward pass.

forward(x, W, b) -> (logits[4], probs[4])
"""

import math


def forward(x, W, b):
    k = len(b)
    logits = [0.0] * k
    for i in range(k):
        s = b[i]
        wi = W[i]
        for j in range(len(x)):
            s += wi[j] * x[j]
        logits[i] = s
    m = max(logits) if logits else 0.0
    exps = [math.exp(l - m) for l in logits]
    z = sum(exps)
    if z <= 0.0:
        z = 1.0
    probs = [e / z for e in exps]
    return logits, probs


def argmax(xs):
    bi = 0
    bv = xs[0]
    for i in range(1, len(xs)):
        if xs[i] > bv:
            bv = xs[i]
            bi = i
    return bi
