"""RawDataCollection.py — Multi-IMU (4x via TCA9548A) data collection."""

from machine import I2C, Pin
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
        """Read magnitude from all 4 IMUs."""
        samples = []
        for channel in range(NUM_IMUS):
            self.mux.select_channel(channel)
            x, y, z = self.sensors[channel].read_3axis()
            mag = (x * x + y * y + z * z) ** 0.5
            # Store magnitude in all 3 axes for CSV compatibility
            samples.extend([mag, mag, mag])
        return tuple(samples)

    def format_output(self, buffer: list) -> str:
        # Output first IMU only for CSV compatibility
        imu0_data = [buffer[i * NUM_IMUS * 3] for i in range(SAMPLES)]
        return self.label + "," + ",".join("{:.4f}".format(v) for v in imu0_data)


if __name__ == "__main__":
    collector = MultiIMUCollector()
    collector.run()