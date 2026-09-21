"""firmware/stages/audit.py

Audit stage: tiny ring buffer for decision telemetry.
Stores last N decisions (label, confidence, timestamp) for debugging.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from stages import Frame


class AuditStage:
    def __init__(self, capacity: int = 32):
        self.capacity = capacity
        self._buf: list[dict] = []

    def process(self, frame: Frame) -> Frame:
        import time
        label = frame.get("label")
        conf = frame.get("confidence")
        if label is not None:
            entry = {
                "ts": time.ticks_ms(),
                "label": label,
                "conf": conf,
                "safe": frame.get("safe", True),
                "stationary": frame.get("stationary", False),
                "drift_flag": frame.get("drift_flag", False),
                "quality_ok": frame.get("quality_ok", True),
                "quality_reason": frame.get("quality_reason", "ok"),
                "state": frame.get("state", "?"),
                "action": frame.get("action", "?"),
                "dominant_freq": frame.get("dominant_freq", 0.0),
                "dominant_mag": frame.get("dominant_mag", 0.0),
                "haptic_reason": frame.get("haptic_reason", ""),
            }
            self._buf.append(entry)
            if len(self._buf) > self.capacity:
                self._buf.pop(0)
            # Compact CSV event line for Thonny / offline personalization
            # ts,label,conf,quality_ok,state,action,freq,mag
            try:
                print("EVT,{},{},{:.2f},{},{},{},{:.1f},{:.2f},{}".format(
                    entry["ts"], entry["label"], entry["conf"] if entry["conf"] else 0.0,
                    1 if entry["quality_ok"] else 0,
                    entry["state"], entry["action"],
                    entry["dominant_freq"], entry["dominant_mag"],
                    entry["quality_reason"],
                ))
            except Exception:
                pass
        frame["audit_log"] = self._buf
        return frame

    def get_log(self) -> list[dict]:
        return list(self._buf)


if __name__ == "__main__":
    import time as _time
    # Host-side fallback for MicroPython's time.ticks_ms()
    if not hasattr(_time, "ticks_ms"):
        _time.ticks_ms = lambda: int(_time.time() * 1000)

    stage = AuditStage(capacity=32)
    frame = {"label": "kinetic", "confidence": 0.8, "safe": True, "stationary": False,
             "drift_flag": False, "quality_ok": True, "quality_reason": "ok",
             "state": "feedback", "action": "cue_high", "dominant_freq": 6.0,
             "dominant_mag": 1.2, "haptic_reason": "suppress:512"}
    out = stage.process(frame)
    assert len(out["audit_log"]) == 1
    assert out["audit_log"][0]["label"] == "kinetic"
    print("audit stage smoke test passed")