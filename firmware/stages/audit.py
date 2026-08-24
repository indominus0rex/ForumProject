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
            }
            self._buf.append(entry)
            if len(self._buf) > self.capacity:
                self._buf.pop(0)
        frame["audit_log"] = self._buf
        return frame

    def get_log(self) -> list[dict]:
        return list(self._buf)