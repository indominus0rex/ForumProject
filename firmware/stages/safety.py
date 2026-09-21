"""firmware/stages/safety.py

Safety stage: lightweight sanity checks before downstream stages run.
- Detects repeated sensor read errors and marks the frame as bad.
- Ensures the time base is sane (no huge jumps between ticks).
- Optionally tracks slow drift of gravity (z-axis) over rest periods and
  flags the frame for auto-recalibration downstream.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from stages import Frame
from common.config import PIPELINE_CONFIG as _CFG


class SafetyStage:
    def __init__(self):
        # Short rolling window for drift detection (median of recent z).
        self._z_hist: list[float] = []
        self._hist_len = _CFG["SAFETY_HIST_LEN"]

    def process(self, frame: Frame) -> Frame:
        # 1) Sensor health flag from the sensor stage.
        if frame.get("sensor_error"):
            frame["safe"] = False
            frame["error_msg"] = "sensor read error"
            return frame

        # 2) Time sanity — huge jumps can mean timer glitch.
        now = frame.get("now_us")
        prev = frame.get("prev_us")
        if prev is not None and now is not None:
            dt = abs(now - prev)
            if dt > _CFG["SAFETY_TIME_JUMP_US"]:
                frame["safe"] = False
                frame["error_msg"] = "time jump"
                return frame

        # 3) Gentle drift tracking (z-axis). We don't correct here, just mark.
        z = frame.get("z_mean")
        if z is not None:
            self._z_hist.append(z)
            if len(self._z_hist) > self._hist_len:
                self._z_hist.pop(0)
            if len(self._z_hist) == self._hist_len:
                # crude median-based drift flag: if current z deviates >0.1g from median.
                s = sorted(self._z_hist)
                med = s[self._hist_len // 2]
                if abs(z - med) > _CFG["SAFETY_DRIFT_G"]:
                    frame["drift_flag"] = True
                else:
                    frame["drift_flag"] = False
            else:
                frame["drift_flag"] = False

        frame["safe"] = True
        return frame


if __name__ == "__main__":
    stage = SafetyStage()
    # Good frame: no errors, sane timing
    good = {"now_us": 1_000_000, "prev_us": 990_000, "sensor_error": False}
    out = stage.process(good)
    assert out["safe"] is True, "good frame should be safe"
    # Bad frame: sensor error
    bad = {"sensor_error": True}
    out = stage.process(bad)
    assert out["safe"] is False, "sensor error should be unsafe"
    assert out["error_msg"] == "sensor read error"
    print("safety stage smoke test passed")