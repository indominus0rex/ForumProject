"""firmware/stages/sensor.py

Sensor stage: thin wrapper around the existing common.gy521.GY521 so the pipeline gets
a clean dict. Reads one sample per callback, updates rolling means for safety,
and flags sensor_error on exception (gravity fallback).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Mock machine module for host-side testing (must be before common.gy521 import)
import types
machine = types.ModuleType("machine")
machine.I2C = None
machine.Pin = None
machine.PWM = None
machine.Timer = None
sys.modules["machine"] = machine

from common.gy521 import GY521
from stages import Frame


class SensorStage:
    def __init__(self, sensor: GY521, sample_buf: list, samples: int = 128):
        self.sensor = sensor
        self.sample_buf = sample_buf
        self.samples = samples
        # rolling means for safety drift tracking
        self._n = 0
        self._sum_x = 0.0
        self._sum_y = 0.0
        self._sum_z = 0.0

    def _update_rolling_means(self, x: float, y: float, z: float) -> None:
        # simple incremental mean, no division per sample to keep cost low
        self._n += 1
        self._sum_x += x
        self._sum_y += y
        self._sum_z += z

    def process(self, frame: Frame) -> Frame:
        # The main loop fills WINDOW_BUFFER via timer callback. The sensor stage
        # here is used for per-sample health checks and mean updates when a new
        # sample arrives. If the frame already contains a fresh sample triplet,
        # we just propagate it.
        # For HSP, sensor stage expects frame to contain 'x','y','z' from the
        # latest callback, and 'window' reference.
        sensor_error = False
        x = frame.get("x")
        y = frame.get("y")
        z = frame.get("z")

        # If no sample present, try a direct read (fallback for manual testing)
        if x is None or y is None or z is None:
            try:
                raw = self.sensor.i2c.readfrom_mem(self.sensor.addr, 0x3B, 6)

                def combine(h: int, l: int) -> int:
                    v = (h << 8) | l
                    return v if v < 32768 else v - 65536

                x = combine(raw[0], raw[1]) / 16384.0
                y = combine(raw[2], raw[3]) / 16384.0
                z = combine(raw[4], raw[5]) / 16384.0
            except Exception:
                sensor_error = True
                x, y, z = 0.0, 0.0, 1.0  # gravity fallback

        # Update rolling means for safety stage
        self._update_rolling_means(x, y, z)
        if self._n > 0:
            x_mean = self._sum_x / self._n
            y_mean = self._sum_y / self._n
            z_mean = self._sum_z / self._n
        else:
            x_mean = y_mean = z_mean = 0.0

        frame["x"] = x
        frame["y"] = y
        frame["z"] = z
        frame["x_mean"] = x_mean
        frame["y_mean"] = y_mean
        frame["z_mean"] = z_mean
        frame["sensor_error"] = sensor_error
        return frame


if __name__ == "__main__":
    stage = SensorStage(sensor=None, sample_buf=[[0.0, 0.0, 1.0] for _ in range(128)], samples=128)
    # Frame with x/y/z present
    frame = {"x": 0.1, "y": 0.2, "z": 1.0}
    out = stage.process(frame)
    assert out["sensor_error"] is False
    assert "x_mean" in out
    print("sensor stage smoke test passed")