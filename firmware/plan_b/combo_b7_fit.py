"""B7 fit — DevKitC-safe: sample PLL + fixed/adaptive gain, no FFT/DNN/CNN.

Pushes included (firmware-only, no hardware change):
  1. Multi-IMU fusion: process_multisample() fuses up to 4 IMU xyz with
     static weights (TODO: auto-tune from band power). Single-IMU
     process_sample() stays backward-compatible (weight 1.0 on ch0).
  2. Dominant-axis projection: tracks the AC component of the highest-energy
     axis instead of magnitude, avoiding magnitude frequency-doubling.
  4. Amplitude-normalized PLL drive: PLL sees filt/(amp_smooth+eps) so loop
     gain is constant across shakes; raw amplitude still sets output duty.

TODO (tune on body): AMP_GATE, fixed_gain, PREDICTION_MS (measure LRA latency),
  W fusion weights, MAX_DUTY cap lives in fit_main.py.
"""
import math

NAME = "b7_fit"
DESCRIPTION = "sample-by-sample bandpass/PLL/predictor/anticancel, fused multi-IMU, amplitude-gated, no classifier"
PERCEPTION = "none"
SUPPRESSION = "S1_pll_fit"
GATE_OK = True

AMP_GATE = 0.03  # TODO: tune on body (g units after bandpass)
W = [0.4, 0.2, 0.2, 0.2]  # TODO: auto-tune from per-channel band power


class Combo:
    def __init__(self, fs=100.0, pll_bandwidth=1.0,
                 prediction_ms=15.0, initial_gain=0.5, fixed_gain=None):
        # Defaults mirror common/config.py — keep in sync manually.
        from common.bandpass import BandpassFilter
        from common.pll import PLL
        from common.predictor import PhasePredictor
        from common.anticancel import AntiPhaseGenerator
        from common.adaptive_gain import AdaptiveGain
        from common.frontend import AxisFrontend
        self.fs = fs
        self.fixed_gain = fixed_gain
        self.weights = list(W)
        self._bp = BandpassFilter(fs=fs, low_hz=3.0, high_hz=12.0)
        self._pll = PLL(fs=fs, center_freq=6.0, bandwidth=pll_bandwidth)
        self._pred = PhasePredictor(fs=fs, prediction_ms=prediction_ms)
        self._ac = AntiPhaseGenerator(max_duty=1023)
        self._ag = AdaptiveGain(initial_gain=initial_gain)
        self._frontend = AxisFrontend(self._bp)
        self._dom = 0
        # compat: old tooling expects combo._sup.pll
        self._sup = self

    @property
    def pll(self):
        return self._pll

    def set_weights(self, w):
        if len(w) != 4:
            raise ValueError("need 4 weights")
        s = sum(w)
        if s <= 0:
            raise ValueError("weights must sum > 0")
        self.weights = [v / s for v in w]

    def _gain(self):
        if self.fixed_gain is not None:
            return self.fixed_gain
        return self._ag.get_gain()

    def _step(self, x, y, z):
        # Canonical frontend (common/frontend.py): dominant-axis projection
        # (push 2) + amplitude-normalized PLL drive (push 4). Multi-IMU
        # fusion still happens in process_multisample before this call.
        pll_in, filt, amp = self._frontend.step(x, y, z)
        self._dom = self._frontend._dom
        phase, freq, _ = self._pll.update(pll_in)
        pred = self._pred.predict(phase, freq)
        if amp < AMP_GATE or not self._pll.locked:
            duty = 0
        else:
            duty = self._ac.compute_duty(pred, amp, self._gain())
        if self.fixed_gain is None:
            self._ag.update(amp)
        return int(duty)

    def process_sample(self, x, y, z):
        return self._step(x, y, z)

    def process_multisample(self, samples):
        # push 1: fuse up to 4 IMU xyz with static weights
        n = len(samples)
        if n == 1:
            return self._step(samples[0][0], samples[0][1], samples[0][2])
        fx = 0.0
        fy = 0.0
        fz = 0.0
        for i, (x, y, z) in enumerate(samples[:4]):
            w = self.weights[i] if i < len(self.weights) else 0.1
            fx += w * x
            fy += w * y
            fz += w * z
        return self._step(fx, fy, fz)

    def process(self, frame):
        window = frame.get("window") or []
        multi = frame.get("multi_window")
        last = 0
        if multi and len(multi) >= 2:
            # fused replay: sample i across channels
            n = len(window)
            for i in range(n):
                quad = []
                for ch in multi[:4]:
                    quad.append(ch[i] if i < len(ch) else (0.0, 0.0, 1.0))
                last = self.process_multisample(quad)
        else:
            for r in window:
                last = self.process_sample(r[0], r[1], r[2])
        frame["suppress_duty"] = int(last)
        frame["pll_freq"] = self._pll.freq
        frame["pll_locked"] = self._pll.locked
        frame["adaptive_gain"] = self._gain()
        frame["dom_axis"] = self._dom
        frame["label"] = frame.get("label", "unknown")
        frame["plan_b"] = NAME
        return frame

    def reset(self):
        self._frontend.reset()
        self._pll.reset()
        self._dom = 0
