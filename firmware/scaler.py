"""scaler.py — MicroPython z-normalisation."""

def apply(x, mean, std):
    out = [0.0] * len(x)
    for i in range(len(x)):
        s = std[i] if i < len(std) else 1.0
        m = mean[i] if i < len(mean) else 0.0
        out[i] = (x[i] - m) / s if s > 1e-9 else 0.0
    return out
