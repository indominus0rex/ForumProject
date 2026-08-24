"""firmware/stages/classify.py

Classify stage: logistic regression forward with heuristic fallback.
Uses model, scaler, logreg. Stores label, confidence, probs in frame.
"""

import common.model as model
import common.scaler as scaler
import common.logreg as logreg
import common.feature_extract as feature_extract
import math
from common.fft import FFTProcessor
from stages import Frame


HEURISTIC_LO_HZ = 3.0
HEURISTIC_HI_HZ = 12.0
HEURISTIC_MAG_THRESHOLD = 1.2


class ClassifyStage:
    def __init__(self, samples: int = 128, fs: float = 100.0):
        self.samples = samples
        self.fs = fs
        self._fft_proc = FFTProcessor(num_samples=samples)

    def _classify_logreg(self, window: list[list[float]]) -> tuple[str, float, list[float]]:
        feats = feature_extract.compute(window, fs=self.fs, n=self.samples)
        x = scaler.apply(feats, model.FEATURE_MEAN, model.FEATURE_STD)
        _, probs = logreg.forward(x, model.WEIGHTS, model.BIAS)
        idx = logreg.argmax(probs)
        return model.CLASSES[idx], probs[idx], probs

    def _classify_heuristic(self, window: list[list[float]]) -> tuple[str, float, None]:
        signal = [0.0] * self.samples
        for i, row in enumerate(window):
            x, y, z = row
            signal[i] = math.sqrt(x * x + y * y + z * z)
        freq, mag = self._fft_proc.process_data(signal, self.fs)
        if HEURISTIC_LO_HZ <= freq <= HEURISTIC_HI_HZ and mag > HEURISTIC_MAG_THRESHOLD:
            return "kinetic", min(1.0, mag / (HEURISTIC_MAG_THRESHOLD * 2.0)), None
        return "rest", 1.0, None

    def process(self, frame: Frame) -> Frame:
        window = frame.get("window")
        if not window:
            frame["classify_error"] = "no window"
            return frame

        if model.WEIGHTS is not None:
            label, conf, probs = self._classify_logreg(window)
        else:
            label, conf, probs = self._classify_heuristic(window)

        frame["label"] = label
        frame["confidence"] = conf
        frame["probs"] = probs
        return frame