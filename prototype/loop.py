"""Plan B loop for one channel: bandpass -> PLL -> predict -> anti-phase. stdlib only."""
import math

FS = 100.0
AMP_GATE = 0.03
FIXED_GAIN = 0.8
PREDICT_S = 0.015
MAX_DUTY = 1023


class Biquad:
    def __init__(self, b0, b1, b2, a1, a2):
        self.b0, self.b1, self.b2, self.a1, self.a2 = b0, b1, b2, a1, a2
        self.x1 = self.x2 = self.y1 = self.y2 = 0.0

    def step(self, x):
        y = self.b0 * x + self.b1 * self.x1 + self.b2 * self.x2 - self.a1 * self.y1 - self.a2 * self.y2
        self.x2, self.x1, self.y2, self.y1 = self.x1, x, self.y1, y
        return y


def bandpass_sections(fs=FS, lo=3.0, hi=12.0):
    f0 = math.sqrt(lo * hi)
    Q = f0 / (hi - lo)
    w0 = 2 * math.pi * f0 / fs
    c, s = math.cos(w0), math.sin(w0)
    out = []
    for q in (Q, Q * 1.5):
        a = s / (2 * q)
        n = 1 + a
        out.append(Biquad(a / n, 0.0, -a / n, -2 * c / n, (1 - a) / n))
    return out


class Loop:
    """Mirrors firmware/common/pll.py update math exactly (raw input,
    absolute lock band) so the prototype shows true device behavior."""

    def __init__(self, bandwidth=1.0):
        self.bp = bandpass_sections()
        self.phase = 0.0
        self.freq = 6.0
        self.integ = 0.0
        self.perr = 0.0
        self.lock_n = 0
        self.locked = False
        self.mx = 0.0
        wn = 2 * math.pi * bandwidth / 0.707
        self.kp = 2 * 0.707 * wn / FS
        self.ki = wn * wn / (FS * FS)

    def step(self, x, y, z):
        self.mx += 0.02 * ((x) - self.mx)  # DC track, x is tremor axis in sim
        s = x - self.mx
        f = s
        for b in self.bp:
            f = b.step(f)
        amp = abs(f)
        perr = f * math.cos(self.phase)
        self.perr += 0.1 * (perr - self.perr)
        self.integ += self.ki * self.perr
        self.freq = min(12.0, max(3.0, 6.0 + self.kp * self.perr + self.integ))
        self.phase = (self.phase + 2 * math.pi * self.freq / FS) % (2 * math.pi)
        if abs(self.perr) < 0.1:
            self.lock_n += 1
            self.locked = self.lock_n >= 50
        elif abs(self.perr) > 0.2:
            self.lock_n = 0
            self.locked = False
        if amp < AMP_GATE or not self.locked:
            return 0, amp
        pred = (self.phase + 2 * math.pi * self.freq * PREDICT_S) % (2 * math.pi)
        duty = abs(int(math.sin(pred + math.pi) * amp * FIXED_GAIN * MAX_DUTY))
        return min(MAX_DUTY, duty), amp
