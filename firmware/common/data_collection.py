"""common/data_collection.py — Base class for timed pilot data collection.

Provides DataCollector base class with timer-driven sampling, session management,
and CSV output formatting. Subclasses implement sensor-specific logic.
"""

from machine import I2C, Pin, Timer
import time
import sys
from typing import Optional, List, Tuple

from common.gy521 import GY521
from common.config import (
    SAMPLES, SAMPLE_INTERVAL_US, LED_PIN,
    I2C_BUS, I2C_SCL_PIN, I2C_SDA_PIN, I2C_FREQ,
    DEFAULT_LABEL, DEFAULT_SESSION_SECONDS, DEFAULT_SESSIONS_TOTAL,
    DEFAULT_REST_BETWEEN_S,
)


class DataCollector:
    """Base class for timed sensor data collection with timer-driven sampling.

    Handles:
    - Periodic timer ISR for consistent sampling rate
    - Multi-session runs with configurable duration/rest
    - Actual sampling rate computation from timestamps
    - CSV-formatted output for ML pipeline compatibility
    - Graceful KeyboardInterrupt handling

    Subclasses must implement:
    - init_sensors(): Initialize sensor hardware
    - allocate_buffer(): Allocate sample buffer
    - read_sample(): Read one sample tuple from sensors
    - format_output(): Format buffer for CSV output
    """

    def __init__(
        self,
        label: str = DEFAULT_LABEL,
        samples: int = SAMPLES,
        sample_interval_us: int = SAMPLE_INTERVAL_US,
        session_seconds: int = DEFAULT_SESSION_SECONDS,
        sessions_total: int = DEFAULT_SESSIONS_TOTAL,
        rest_between_s: int = DEFAULT_REST_BETWEEN_S,
    ):
        """Initialize collector configuration.

        Args:
            label: Class label for CSV output (e.g., "rest", "kinetic").
            samples: Samples per window (default 128).
            sample_interval_us: Sampling period in microseconds (default 10000 = 100Hz).
            session_seconds: Duration of each collection session.
            sessions_total: Number of sessions to run.
            rest_between_s: Rest time between sessions in seconds.
        """
        self.label = label
        self.samples = samples
        self.sample_interval_us = sample_interval_us
        self.session_seconds = session_seconds
        self.sessions_total = sessions_total
        self.rest_between_s = rest_between_s

        # Hardware
        self.led = Pin(LED_PIN, Pin.OUT)
        self.i2c = I2C(I2C_BUS, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQ)

        # Sensor(s) - to be initialized by subclass
        self.sensors: List[GY521] = []

        # Sampling state
        self._timer: Optional[Timer] = None
        self._sample_index = 0
        self._first_sample_time: Optional[int] = None
        self._last_sample_time: Optional[int] = None
        self._window_ready = False

        # Buffer - to be allocated by subclass
        self._buffer: List[float] = []

    def init_sensors(self) -> None:
        """Initialize sensors. Override in subclass."""
        raise NotImplementedError

    def allocate_buffer(self) -> None:
        """Allocate sample buffer. Override in subclass."""
        raise NotImplementedError

    def read_sample(self) -> Tuple[float, ...]:
        """Read one sample from sensor(s). Override in subclass.

        Returns:
            Tuple of float values (e.g., (x, y, z) for single IMU).
        """
        raise NotImplementedError

    def format_output(self, buffer: List[float]) -> str:
        """Format buffer for CSV output. Override in subclass.

        Args:
            buffer: Filled sample buffer.

        Returns:
            CSV line string starting with label.
        """
        raise NotImplementedError

    def _sample_callback(self, t: Timer) -> None:
        """Timer ISR: read sample and store in buffer.

        Keeps ISR short; errors result in gravity fallback.
        """
        try:
            sample = self.read_sample()
        except Exception:
            # Gravity fallback on read error — replicate per-sensor
            # need tuple length 3 * num_sensors, not tuple repetition
            n_sensors = len(self.sensors) if self.sensors else 1
            sample = tuple([0.0, 0.0, 1.0] * n_sensors) if n_sensors > 1 else (0.0, 0.0, 1.0)
            if len(sample) == 3 and n_sensors == 1:
                pass
            elif len(sample) != 3 * n_sensors:
                sample = tuple([0.0, 0.0, 1.0] * n_sensors)

        # Store in buffer
        base_idx = self._sample_index * len(sample)
        for i, val in enumerate(sample):
            self._buffer[base_idx + i] = val

        now = time.ticks_us()
        if self._sample_index == 0:
            self._first_sample_time = now
        self._last_sample_time = now
        self._sample_index += 1

        if self._sample_index >= self.samples:
            self._window_ready = True
            self._sample_index = 0  # Will overwrite on next window
            if self._timer:
                self._timer.deinit()

    def _init_timer(self) -> None:
        """Initialize periodic sampling timer."""
        try:
            self._timer = Timer(0)
            self._timer.init(
                period=self.sample_interval_us // 1000,
                mode=Timer.PERIODIC,
                callback=self._sample_callback,
            )
        except Exception as e:
            print("Timer init failed:", e)
            sys.exit()

    def _reset_window_state(self) -> None:
        """Reset per-window state."""
        self._sample_index = 0
        self._first_sample_time = None
        self._last_sample_time = None
        self._window_ready = False

    def _compute_actual_fs(self) -> float:
        """Compute actual sampling frequency from timestamps."""
        if self._first_sample_time is not None and self._last_sample_time is not None:
            total_time_us = time.ticks_diff(self._last_sample_time, self._first_sample_time)
            if total_time_us > 0:
                return self.samples / (total_time_us / 1_000_000.0)
        return self.samples / (self.sample_interval_us / 1_000_000.0)

    def run(self) -> None:
        """Run collection sessions."""
        self.init_sensors()
        self.allocate_buffer()
        self._init_timer()

        print(f"Label: {self.label}")
        print(f"Window: {self.samples} samples / {self.samples * self.sample_interval_us / 1_000_000:.2f}s")
        print(f"Session: {self.session_seconds}s, Total: {self.sessions_total}")

        try:
            for sess in range(self.sessions_total):
                print(f"\n=== SESSION {sess + 1}/{self.sessions_total} ===")
                print("Get ready... LED on in 3s")
                time.sleep(3)
                self.led.value(1)

                self._reset_window_state()
                t_session_start = time.ticks_us()
                t_end_us = time.ticks_add(t_session_start, self.session_seconds * 1_000_000)
                window_idx = 0

                while time.ticks_diff(t_end_us, time.ticks_us()) > 0:
                    if self._window_ready:
                        self._window_ready = False

                        # Compute actual sampling rate
                        actual_fs = self._compute_actual_fs()

                        # Output formatted data
                        output = self.format_output(self._buffer)
                        print(output)
                        window_idx += 1

                        # Heartbeat blink
                        self.led.value(0)
                        time.sleep_ms(20)
                        self.led.value(1)

                        self._reset_window_state()
                        self._timer.init(
                            period=self.sample_interval_us // 1000,
                            mode=Timer.PERIODIC,
                            callback=self._sample_callback,
                        )

                    time.sleep(0.001)

                self.led.value(0)
                elapsed = time.ticks_diff(time.ticks_us(), t_session_start) / 1_000_000
                print(f"Session {sess + 1}/{self.sessions_total} done. windows={window_idx}, elapsed={elapsed:.2f}s")

                if sess < self.sessions_total - 1 and self.rest_between_s > 0:
                    print(f"Rest {self.rest_between_s}s...")
                    time.sleep(self.rest_between_s)

            print("\nAll sessions done. LED off.")
            self.led.value(0)

        except KeyboardInterrupt:
            if self._timer:
                self._timer.deinit()
            self.led.value(0)
            print("\nLoop stopped.")