"""B5 fixed-gain — P2 DNN gate + S2 fixed-gain PLL (no adaptation)."""
import math

NAME = "b5_fixed_gain"
DESCRIPTION = "DNN gate + PLL with fixed gain 0.5 (no AdaptiveGain.update)"
PERCEPTION = "P2_dnn_gated"
SUPPRESSION = "S2_fixed_gain_pll"
GATE_OK = True
FIXED_GAIN = 0.5
CONF_THRESH = 0.50


class Combo:
    def __init__(self, fs: float = 100.0, pll_bandwidth: float = 1.0,
                 prediction_ms: float = 15.0):
        from common.bandpass import BandpassFilter
        from common.pll import PLL
        from common.predictor import PhasePredictor
        from common.anticancel import AntiPhaseGenerator
        import common.model_dnn as model
        import common.scaler as scaler
        import common.logreg as logreg
        import common.dnn as dnn
        import common.feature_extract as feature_extract
        if model.W1 is None or model.W2 is None:
            raise RuntimeError("B5 GATE: bake DNN weights first")
        self.fs = fs
        self._bp = BandpassFilter(fs=fs, low_hz=3.0, high_hz=12.0)
        self._pll = PLL(fs=fs, center_freq=6.0, bandwidth=pll_bandwidth)
        self._pred = PhasePredictor(fs=fs, prediction_ms=prediction_ms)
        self._gen = AntiPhaseGenerator(max_duty=1023)
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
        if frame["label"] in ("rest", "baseline") or frame["confidence"] < CONF_THRESH:
            frame["suppress_duty"] = 0
        else:
            # Full-window replay (one PLL step per sample).
            duty = 0
            for r in window:
                duty = self.process_sample(float(r[0]), float(r[1]), float(r[2]))
            frame["suppress_duty"] = duty
        frame["plan_b"] = NAME
        return frame

    def process_sample(self, x: float, y: float, z: float) -> int:
        mag = math.sqrt(x * x + y * y + z * z) - 1.0
        filt = self._bp.process_sample(mag)
        phase, freq, _nco = self._pll.update(filt)
        amp = abs(filt)
        pred = self._pred.predict(phase, freq)
        return int(self._gen.compute_duty(pred, amp, gain=FIXED_GAIN))
