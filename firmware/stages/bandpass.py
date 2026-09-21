"""firmware/stages/bandpass.py

Bandpass stage: per-axis IIR bandpass over the full window (3-12 Hz tremor
band). Wraps common.bandpass.BandpassFilter and exposes process(frame).

Reads frame["window"], writes the filtered window back in place (new list,
input rows untouched). IIR state persists across windows — no reset per
window — so the filter does not re-ring on every window boundary.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.bandpass import BandpassFilter
from stages import Frame


class BandpassStage:
    def __init__(self, fs: float = 100.0, low_hz: float = 3.0, high_hz: float = 12.0):
        self.fs = fs
        self.low_hz = low_hz
        self.high_hz = high_hz
        self._filters = [BandpassFilter(fs=fs, low_hz=low_hz, high_hz=high_hz)
                         for _ in range(3)]

    def reset(self) -> None:
        """Clear IIR state on all three axes."""
        for f in self._filters:
            f.reset()

    def process(self, frame: Frame) -> Frame:
        window = frame.get("window")
        if not window:
            frame["bandpass_error"] = "no window"
            return frame
        fx = self._filters[0].process_block([r[0] for r in window])
        fy = self._filters[1].process_block([r[1] for r in window])
        fz = self._filters[2].process_block([r[2] for r in window])
        frame["window"] = [[fx[i], fy[i], fz[i]] for i in range(len(window))]
        frame["bandpass_ok"] = True
        return frame


if __name__ == "__main__":
    import math
    stage = BandpassStage(fs=100.0, low_hz=3.0, high_hz=12.0)
    window = [[math.sin(2 * math.pi * 6 * i / 100), 0.0, 1.0] for i in range(128)]
    frame = {"window": window}
    out = stage.process(frame)
    assert out["bandpass_ok"] is True
    assert len(out["window"]) == 128
    print("bandpass stage smoke test passed")
