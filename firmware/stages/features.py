"""firmware/stages/features.py

Features stage: defers to feature_extract.compute but as a stage.
Computes 15-element feature vector from window and stores in frame.
"""

import common.feature_extract as feature_extract
from stages import Frame


class FeaturesStage:
    def __init__(self, fs: float = 100.0, n: int = 128):
        self.fs = fs
        self.n = n

    def process(self, frame: Frame) -> Frame:
        window = frame.get("window")
        if not window:
            frame["features_error"] = "no window"
            return frame
        feats = feature_extract.compute(window, fs=self.fs, n=self.n)
        frame["features"] = feats
        return frame