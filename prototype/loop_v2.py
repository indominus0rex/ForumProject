"""Improved Plan B loop: gear-shift bandwidth + zero-crossing coarse seeding.

Same PLL core as loop.py (device-identical math), plus:
  G1 gear-shift: wide loop (3 Hz) while unlocked for fast pull-in,
     narrow (0.8 Hz) once locked for steadiness.
  G2 coarse seeding: rising-zero-crossing period estimate recenters the
     NCO when unlocked > 1 s, so far-off tremors (4 / 8 Hz) acquire fast.
Lock band unchanged (absolute 0.1/0.2) to stay device-comparable.
  B1 beat-aware lock: fast/slow EMAs of phase error separate true lock
     (both agree, small) from a slow beat (fast wobbles around slow).
     False lock on far-off tones was confirmed: 4.2 Hz in, NCO parked
     at 6.0, duties firing at wrong phase.
"""
import math

from loop import Biquad, bandpass_sections, FS, AMP_GATE, FIXED_GAIN, PREDICT_S, MAX_DUTY


def _gains(bandwidth):
    wn = 2 * math.pi * bandwidth / 0.707
    return 2 * 0.707 * wn / FS, wn * wn / (FS * FS)


class Loop2:
    def __init__(self):
        self.bp = bandpass_sections()
        self.phase = 0.0
        self.center = 6.0
        self.freq = 6.0
        self.integ = 0.0
        self.perr = 0.0
        self._fast = 0.0
        self._slow = 0.0
        self.lock_n = 0
        self.locked = False
        self.mx = 0.0
        self.kp, self.ki = _gains(3.0)  # start wide for fast first lock
        # coarse estimator state
        self._prev_f = 0.0
        self._prev_cross = None
        self._period = 1.0 / 6.0
        self._cross_n = 0
        self._t = 0.0
        self._unlocked_n = 0
        self._disagree_n = 0
        self._reject_n = 0
        self._armed = False
        self._crate = 6.0  # start at center so early vetoes don't false-fire
        self._cslow = 6.0  # slow EMA of rate: kills within-cycle ripple

    def _coarse(self, f, amp):
        # Rate-counting estimator (self-healing, no last-crossing cascade):
        # leaky count of hysteresis-gated rising crossings over ~1 s window.
        # crate converges to crossings-per-100-samples = Hz at fs=100.
        H = 0.015  # Schmitt half-width: kills zero-chatter, tremor amp >> H
        if f < -H:
            self._armed = True
        self._crate *= (1.0 - 1.0 / 100.0)
        if self._armed and f > H and amp > 2 * AMP_GATE:
            self._armed = False
            self._crate += 1.0
            self._cross_n += 1
        fest = max(3.0, min(12.0, self._crate))
        self._period = 1.0 / fest
        self._cslow += 0.02 * (fest - self._cslow)

    def step(self, x, y, z):
        self._t += 1.0 / FS
        self.mx += 0.02 * (x - self.mx)
        s = x - self.mx
        f = s
        for b in self.bp:
            f = b.step(f)
        amp = abs(f)
        self._coarse(f, amp)  # unconditional: decay must run every sample
        perr = f * math.cos(self.phase)
        self.perr += 0.1 * (perr - self.perr)
        # B1: beat detector — fast EMA tracks oscillation, slow EMA the DC.
        # True lock: both small and agreeing. Slow beat: fast wobbles.
        self._fast += 0.2 * (perr - self._fast)
        self._slow += 0.02 * (perr - self._slow)
        wobble = abs(self._fast - self._slow)
        level = abs(self._slow)
        # Agreement veto: coarse zero-crossing freq vs NCO freq. A slow
        # beat keeps perr small but the two estimates disagree. Veto needs
        # 30 consecutive disagreeing samples so noisy crossings can't flicker.
        agree = True
        fcoarse = 0.0
        if self._cross_n >= 3:
            fcoarse = min(12.0, max(3.0, self._cslow))
            if abs(fcoarse - self.freq) < 0.5:
                self._disagree_n = 0
                agree = True
            else:
                self._disagree_n += 1
                agree = self._disagree_n < 30
        else:
            self._disagree_n = 0
        self.integ += self.ki * self.perr
        self.freq = min(12.0, max(3.0, self.center + self.kp * self.perr + self.integ))
        self.phase = (self.phase + 2 * math.pi * self.freq / FS) % (2 * math.pi)
        if wobble < 0.05 and level < 0.12 and agree:
            self.lock_n += 1
            if self.lock_n >= 50 and not self.locked:
                self.locked = True
                self.kp, self.ki = _gains(1.5)  # G1: firm up once locked (0.8 froze false locks)
        elif wobble > 0.15 or level > 0.30 or self._disagree_n >= 30:
            self.lock_n = 0
            if self.locked:
                self.locked = False
                self.kp, self.ki = _gains(3.0)  # G1: widen on loss
        if not self.locked:
            self._unlocked_n += 1
            # G2: recenter on coarse estimate if starved for > 1 s
            if self._unlocked_n > 100 and self._cross_n >= 3:
                fc = min(12.0, max(3.0, 1.0 / self._period))
                if abs(fc - self.center) > 0.3:
                    self.center = fc
                    self.integ = 0.0
                    self._unlocked_n = 0
        else:
            self._unlocked_n = 0
        if amp < AMP_GATE or not self.locked:
            return 0, amp
        pred = (self.phase + 2 * math.pi * self.freq * PREDICT_S) % (2 * math.pi)
        duty = abs(int(math.sin(pred + math.pi) * amp * FIXED_GAIN * MAX_DUTY))
        return min(MAX_DUTY, duty), amp
