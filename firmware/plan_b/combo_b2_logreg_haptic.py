"""B2 baseline-ml — P1 logreg perception + S0 threshold haptic."""

NAME = "b2_baseline_ml"
DESCRIPTION = "15-feat logreg + fixed-duty haptic"
PERCEPTION = "P1_logreg"
SUPPRESSION = "S0_threshold_haptic"
GATE_OK = True

LRA_DUTY_ON = 512
LRA_DUTY_OFF = 0


class Combo:
    def __init__(self, fs: float = 100.0):
        import common.model as model
        import common.scaler as scaler
        import common.logreg as logreg
        import common.feature_extract as feature_extract
        if model.WEIGHTS is None:
            raise RuntimeError("B2 GATE: bake logreg weights (host_scripts/train_classifier.py) first")
        self.fs = fs
        self._model = model
        self._scaler = scaler
        self._logreg = logreg
        self._fe = feature_extract

    def process(self, frame: dict) -> dict:
        window = frame.get("window")
        feats = self._fe.compute(window, fs=self.fs, n=len(window))
        x = self._scaler.apply(feats, self._model.FEATURE_MEAN, self._model.FEATURE_STD)
        _, probs = self._logreg.forward(x, self._model.WEIGHTS, self._model.BIAS)
        idx = self._logreg.argmax(probs)
        label = self._model.CLASSES[idx]
        frame["label"] = label
        frame["confidence"] = probs[idx]
        frame["probs"] = probs
        frame["suppress_duty"] = LRA_DUTY_ON if label not in ("rest", "baseline") else LRA_DUTY_OFF
        frame["plan_b"] = NAME
        return frame

    def process_sample(self, x: float, y: float, z: float) -> int:
        return LRA_DUTY_OFF
