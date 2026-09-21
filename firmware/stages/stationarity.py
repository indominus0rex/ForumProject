"""firmware/stages/stationarity.py

Stationarity stage: cheap variance-ratio pre-check to avoid full FFT when
signal is quiet. Uses a rolling window of recent samples to compute a
variance ratio (high-freq / low-freq energy proxy) and sets
frame['stationary'] and frame['skip_fft'].
"""

from stages import Frame
from common.config import PIPELINE_CONFIG as _CFG


class StationarityStage:
    def __init__(self, window_len: int = 128, ratio_thresh: float = None):
        if ratio_thresh is None:
            ratio_thresh = _CFG["STATIONARITY_RATIO_THRESH"]
        self.window_len = window_len
        self.ratio_thresh = ratio_thresh
        self._buf: list[float] = []

    def _variance(self, data: list[float]) -> float:
        if not data:
            return 0.0
        m = sum(data) / len(data)
        return sum((x - m) ** 2 for x in data) / len(data)

    def process(self, frame: Frame) -> Frame:
        # Expect frame contains 'x','y','z' for latest sample and 'window' reference.
        # For a true variance ratio we need a short history; here we keep a simple
        # buffer of recent magnitude values.
        mag = 0.0
        x = frame.get("x")
        y = frame.get("y")
        z = frame.get("z")
        if x is not None and y is not None and z is not None:
            # magnitude
            mag = (x * x + y * y + z * z) ** 0.5

        self._buf.append(mag)
        if len(self._buf) > self.window_len:
            self._buf.pop(0)

        if len(self._buf) >= self.window_len // 2:
            # split buffer in half for crude high/low variance proxy
            half = len(self._buf) // 2
            low = self._buf[:half]
            high = self._buf[half:]
            var_low = self._variance(low)
            var_high = self._variance(high)
            ratio = var_high / (var_low + 1e-9)
            stationary = ratio < self.ratio_thresh
        else:
            stationary = False
            ratio = 0.0

        frame["stationary"] = stationary
        frame["var_ratio"] = ratio
        # If stationary, downstream stages can skip expensive FFT
        frame["skip_fft"] = stationary
        return frame