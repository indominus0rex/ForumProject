"""raw_data_collection.py — Multi-IMU (4x via TCA9548A) data collection."""

from machine import I2C, Pin
from typing import Tuple
from common.data_collection import DataCollector
from common.gy521 import GY521
from common.config import (
    SAMPLES, TCA9548A_ADDR, NUM_IMUS, DEFAULT_LABEL,
)


class TCA9548A:
    """TCA9548A I2C multiplexer driver."""

    def __init__(self, i2c: I2C, addr: int = TCA9548A_ADDR):
        self.i2c = i2c
        self.addr = addr

    def select_channel(self, channel: int) -> None:
        if channel < 0 or channel > 7:
            raise ValueError("Channel must be 0-7")
        self.i2c.writeto(self.addr, bytes([1 << channel]))


class MultiIMUCollector(DataCollector):
    """4x GY-521 IMUs on TCA9548A multiplexer data collector."""

    def __init__(self, label: str = DEFAULT_LABEL, **kwargs):
        super().__init__(label=label, **kwargs)
        self.mux: TCA9548A = None  # type: ignore

    def init_sensors(self) -> None:
        self.mux = TCA9548A(self.i2c)
        self.sensors = []
        for channel in range(NUM_IMUS):
            self.mux.select_channel(channel)
            sensor = GY521(self.i2c)
            self.sensors.append(sensor)
        print(f"{NUM_IMUS} IMUs initialized on TCA9548A multiplexer!")

    def allocate_buffer(self) -> None:
        # 128 samples * 4 sensors * 3 axes each
        self._buffer = [0.0] * (SAMPLES * NUM_IMUS * 3)

    def read_sample(self) -> Tuple[float, ...]:
        """Read xyz from all 4 IMUs (12 values, channel order)."""
        samples = []
        for channel in range(NUM_IMUS):
            self.mux.select_channel(channel)
            x, y, z = self.sensors[channel].read_3axis()
            samples.extend([x, y, z])
        return tuple(samples)

    def format_output(self, buffer: list) -> str:
        # Line 1: IMU0 xyz, parse-compatible with train_classifier.parse_file
        imu0 = []
        for i in range(SAMPLES):
            imu0.extend(buffer[i * NUM_IMUS * 3:(i * NUM_IMUS * 3) + 3])
        train_line = self.label + "," + ",".join("{:.4f}".format(v) for v in imu0)
        # Line 2: all 4 IMUs xyz for coherence / future fusion (host splits it out)
        aux_line = self.label + ":aux," + ",".join("{:.4f}".format(v) for v in buffer)
        return train_line + "\n" + aux_line


if __name__ == "__main__":
    collector = MultiIMUCollector()
    collector.run()