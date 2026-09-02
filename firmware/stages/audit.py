"""firmware/stages/audit.py

Audit stage: tiny ring buffer for decision telemetry.
Stores last N decisions (label, confidence, timestamp) for debugging.
"""

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