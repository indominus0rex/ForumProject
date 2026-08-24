"""common/gy521.py — GY-521 (MPU-6050) 3-axis accelerometer driver for MicroPython.

Configures sensor for +/-2g range, 94Hz DLPF, 1kHz sample rate (divider 0).
Returns acceleration in g units.
"""

from machine import I2C
import time
from typing import Tuple


class GY521:
    """MPU-6050 accelerometer driver via I2C."""

    def __init__(self, i2c: I2C, addr: int = 0x68):
        """Initialize sensor.

        Args:
            i2c: I2C bus instance.
            addr: I2C address (default 0x68).
        """
        self.i2c = i2c
        self.addr = addr
        # Reset
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x80')
        time.sleep(0.1)
        # Wake
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')
        # +/- 2g range
        self.i2c.writeto_mem(self.addr, 0x1C, b'\x00')
        # DLPF 94Hz
        self.i2c.writeto_mem(self.addr, 0x1A, b'\x02')
        # Sample rate divider 0 (1kHz / (1+0) = 1kHz)
        self.i2c.writeto_mem(self.addr, 0x19, b'\x00')

    def read_3axis(self) -> Tuple[float, float, float]:
        """Read raw 3-axis acceleration.

        Returns:
            Tuple of (x, y, z) in g units.
            On I2C error, returns (0.0, 0.0, 1.0) as gravity fallback.
        """
        try:
            raw = self.i2c.readfrom_mem(self.addr, 0x3B, 6)

            def combine(high: int, low: int) -> int:
                val = (high << 8) | low
                return val if val < 32768 else val - 65536

            x = combine(raw[0], raw[1]) / 16384.0
            y = combine(raw[2], raw[3]) / 16384.0
            z = combine(raw[4], raw[5]) / 16384.0
            return x, y, z
        except Exception:
            return 0.0, 0.0, 1.0  # gravity fallback