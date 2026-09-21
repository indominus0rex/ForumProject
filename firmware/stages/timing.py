"""firmware/stages/timing.py — Optional timing instrumentation stage.

Records per-stage execution time in frame["stage_ms"] and prints
a warning if any stage exceeds its budget. Add to STAGE_ORDER last
for debugging; remove for production builds.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from stages import Frame
import time


class TimingStage:
    def __init__(self, budget_ms: float = 2.0):
        self.budget_ms = budget_ms
        self._times: dict = {}

    def process(self, frame: Frame) -> Frame:
        # This stage runs last; measure elapsed since window start
        now = time.ticks_ms()
        start = frame.get("window_start_ms", now)
        elapsed = time.ticks_diff(now, start)
        frame["pipeline_ms"] = elapsed
        if elapsed > self.budget_ms:
            print(f"WARNING: pipeline took {elapsed} ms (budget {self.budget_ms} ms)")
        return frame


if __name__ == "__main__":
    import time as _time
    if not hasattr(_time, "ticks_ms"):
        _time.ticks_ms = lambda: int(_time.time() * 1000)
    if not hasattr(_time, "ticks_diff"):
        _time.ticks_diff = lambda a, b: a - b

    stage = TimingStage(budget_ms=5.0)
    frame = {"window_start_ms": _time.ticks_ms()}
    out = stage.process(frame)
    assert "pipeline_ms" in out
    print(f"timing stage OK — pipeline_ms: {out['pipeline_ms']}")
