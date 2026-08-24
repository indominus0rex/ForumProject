"""collect_pilot.py — Single-IMU pilot data collection using DataCollector base."""

from common.data_collection import DataCollector
from common.gy521 import GY521
from common.config import SAMPLES


class PilotCollector(DataCollector):
    """Single GY-521 IMU data collector for pilot labeling."""

    def init_sensors(self) -> None:
        sensor = GY521(self.i2c)
        self.sensors = [sensor]
        print("GY-521 3-Axis 100Hz Pilot Capture Ready")

    def allocate_buffer(self) -> None:
        self._buffer = [0.0] * (SAMPLES * 3)

    def read_sample(self) -> Tuple[float, float, float]:
        return self.sensors[0].read_3axis()

    def format_output(self, buffer: list) -> str:
        return self.label + "," + ",".join("{:.4f}".format(v) for v in buffer)


if __name__ == "__main__":
    collector = PilotCollector()
    collector.run()