"""B4 pll-only — no classifier; pure real-time PLL loop (logging-only label)."""

NAME = "b4_pll_only"
DESCRIPTION = "bandpass/PLL/predictor/anticancel/adaptive-gain, no classifier dependency"
PERCEPTION = "none"
SUPPRESSION = "S1_full_pll"
GATE_OK = True


class Combo:
    def __init__(self, fs: float = 100.0, pll_bandwidth: float = 1.0,
                 prediction_ms: float = 15.0, initial_gain: float = 0.5):
        from stages.suppress import SuppressStage
        self._sup = SuppressStage(fs=fs, pll_bandwidth=pll_bandwidth,
                                  prediction_ms=prediction_ms, initial_gain=initial_gain)

    def process(self, frame: dict) -> dict:
        # Full-window replay (one PLL step per sample; single-stepping here
        # would stretch the 50-sample lock threshold to ~64 s wall-clock).
        window = frame.get("window") or []
        last = 0
        for r in window:
            last = self._sup.process_sample(float(r[0]), float(r[1]), float(r[2]))
        frame["suppress_duty"] = int(last)
        frame["pll_phase"] = self._sup.pll.phase
        frame["pll_freq"] = self._sup.pll.freq
        frame["pll_locked"] = self._sup.pll.locked
        frame["adaptive_gain"] = self._sup.adaptive_gain.get_gain()
        frame["label"] = frame.get("label", "unknown")
        frame["plan_b"] = NAME
        return frame

    def process_sample(self, x: float, y: float, z: float) -> int:
        return int(self._sup.process_sample(x, y, z))
