"""firmware/stages/fft.py

FFT stage: in-place Cooley-Tukey for a single axis magnitude signal.
Wraps common.fft.FFTProcessor and exposes process(frame) contract.
If frame['skip_fft'] is True, stage returns frame unchanged.
"""

import math
from common.fft import FFTProcessor
from stages import Frame


class FFTStage:
    def __init__(self, samples: int = 128, fs: float = 100.0):
        self.processor = FFTProcessor(num_samples=samples)
        self.samples = samples
        self.fs = fs

    def _signal_from_window(self, window: list[list[float]]) -> list[float]:
        # window is a list of [x,y,z] rows
        sig = [0.0] * self.samples
        for i, row in enumerate(window):
            x, y, z = row
            sig[i] = math.sqrt(x * x + y * y + z * z)
        return sig

    def process(self, frame: Frame) -> Frame:
        if frame.get("skip_fft"):
            frame["fft_skipped"] = True
            frame["dominant_freq"] = 0.0
            frame["dominant_mag"] = 0.0
            return frame

        window = frame.get("window")
        if not window or len(window) < self.samples:
            frame["fft_error"] = "insufficient window"
            return frame

        signal = self._signal_from_window(window)
        freq, mag = self.processor.process_data(signal, self.fs)
        frame["dominant_freq"] = freq
        frame["dominant_mag"] = mag
        frame["fft_skipped"] = False
        return frame