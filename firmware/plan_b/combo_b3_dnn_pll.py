"""B3 current-best — P2 DNN perception + S1 full PLL chain (reference)."""

NAME = "b3_current_best"
DESCRIPTION = "DNN gate + bandpass/PLL/predictor/anticancel/adaptive-gain"
PERCEPTION = "P2_dnn"
SUPPRESSION = "S1_full_pll"
GATE_OK = True

CONF_THRESH = 0.50


class Combo:
    def __init__(self, fs: float = 100.0, pll_bandwidth: float = 1.0,
                 prediction_ms: float = 15.0, initial_gain: float = 0.5):
        from stages.suppress import SuppressStage
        import common.model_dnn as model
        import common.scaler as scaler
        import common.logreg as logreg
        import common.dnn as dnn
        import common.feature_extract as feature_extract
        if model.W1 is None or model.W2 is None:
            raise RuntimeError("B3 GATE: bake DNN weights (host_scripts/train_dnn_parkinsons.py) first")
        self.fs = fs
        self._sup = SuppressStage(fs=fs, pll_bandwidth=pll_bandwidth,
                                  prediction_ms=prediction_ms, initial_gain=initial_gain)
        self._model, self._scaler, self._logreg = model, scaler, logreg
        self._dnn, self._fe = dnn, feature_extract

    def process(self, frame: dict) -> dict:
        window = frame.get("window")
        feats = self._fe.compute(window, fs=self.fs, n=len(window))
        x = self._scaler.apply(feats, self._model.FEATURE_MEAN, self._model.FEATURE_STD)
        _, probs = self._dnn.forward(x, self._model.W1, self._model.B1,
                                     self._model.W2, self._model.B2)
        idx = self._logreg.argmax(probs)
        frame["label"] = self._model.CLASSES[idx]
        frame["confidence"] = probs[idx]
        frame["probs"] = probs
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
        if frame.get("label") in ("rest", "baseline") or frame.get("confidence", 0.0) < CONF_THRESH:
            frame["suppress_duty"] = 0
        frame["plan_b"] = NAME
        return frame

    def process_sample(self, x: float, y: float, z: float) -> int:
        return int(self._sup.process_sample(x, y, z))
