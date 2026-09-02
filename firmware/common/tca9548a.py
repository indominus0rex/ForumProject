"""common/tca9548a.py — TCA9548A 8-channel I2C multiplexer driver for MicroPython.

MicroPython usage (matches web tutorials https://randomnerdtutorials.com/tca9548a-i2c-multiplexer-esp32-esp8266-arduino/):
    from common.tca9548a import TCA9548A
    mux = TCA9548A(i2c, addr=0x70)
    mux.select_channel(0)  # -> i2c.writeto(0x70, b'\\x01')
    # then normal i2c.readfrom_mem(0x68, 0x3B, 6)

For 4-IMU build 2026-08-27 (thumb CMC lock):
  ch0 = dorsal wrist proximal, ch1 = thenar, ch2 = thumb CMC, ch3 = forearm proximal.
"""

from machine import I2C


class TCA9548A:
    """TCA9548A I2C multiplexer (addr 0x70 by default)."""

    def __init__(self, i2c: I2C, addr: int = 0x70):
        self.i2c = i2c
        self.addr = addr
        self._current_channel = None

    def select_channel(self, channel: int) -> None:
        """Select single channel 0..7 via bit 1<<channel."""
        if not 0 <= channel <= 7:
            raise ValueError("channel must be 0..7")
        # Avoid redundant write for timing budget (10ms @100Hz ×4 IMUs is tight)
        if self._current_channel == channel:
            return
        try:
            self.i2c.writeto(self.addr, bytes([1 << channel]))
            self._current_channel = channel
        except Exception as e:
            # Reset current on error so next call retries
            self._current_channel = None
            raise e

    def select_channels(self, mask: int) -> None:
        """Select multiple channels via bitmask (not used here, kept for completeness)."""
        try:
            self.i2c.writeto(self.addr, bytes([mask & 0xFF]))
            self._current_channel = None  # ambiguous
        except Exception:
            self._current_channel = None
            raise

    def deselect_all(self) -> None:
        try:
            self.i2c.writeto(self.addr, b"\x00")
            self._current_channel = None
        except Exception:
            self._current_channel = None
            raise

    def scan_channel(self, channel: int) -> list[int]:
        """Return I2C scan result for given channel (for bench validation)."""
        self.select_channel(channel)
        return self.i2c.scan()
