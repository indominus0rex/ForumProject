"""firmware/stages/safety.py

Safety stage: lightweight sanity checks before downstream stages run.
- Detects repeated sensor read errors and marks the frame as bad.
- Ensures the time base is sane (no huge jumps between ticks).
- Optionally tracks slow drift of gravity (z-axis) over rest periods and
  flags the frame for auto-recalibration downstream.
"""

from stages import Frame


class SafetyStage:
    def __init__(self):
        # Short rolling window for drift detection (median of recent z).
        self._z_hist: list[float] = []
        self._hist_len = 16

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
            # Anything > 2 seconds between samples is obviously wrong.
            if dt > 2_000_000:
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
                if abs(z - med) > 0.10:
                    frame["drift_flag"] = True
                else:
                    frame["drift_flag"] = False
            else:
                frame["drift_flag"] = False

        frame["safe"] = True
        return frame