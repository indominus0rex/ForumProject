"""Synthetic hand signal: drifting tremor + voluntary sway + noise. stdlib only."""
import math
import random


class Hand:
    def __init__(self, fs=100.0, seed=7):
        self.fs = fs
        self.rng = random.Random(seed)
        self.t = 0.0
        self.ph = 0.0  # integrated tremor phase (correct FM: f_true = dph/dt)

    def sample(self):
        # tremor freq drifts 5.5 -> 7.5 Hz over 20 s (phase never fixed)
        f = 6.5 + 1.0 * math.sin(2 * math.pi * 0.05 * self.t)
        self.ph += 2 * math.pi * f / self.fs
        # voluntary sway 0.4 Hz, large but out of tremor band
        vol = 0.5 * math.sin(2 * math.pi * 0.4 * self.t)
        tremor = 0.15 * math.sin(self.ph)
        noise = 0.01 * (self.rng.random() - 0.5) * 2.0
        self.t += 1.0 / self.fs
        # x = tremor axis, z carries gravity
        return tremor + 0.05 * vol, 0.02 * vol, 1.0 + 0.1 * tremor + noise
