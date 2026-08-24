"""embedded_main_hsp.py — Thin dispatcher for Hierarchical Stage Pipeline.

Keeps all hardware contracts from embedded_main.py but delegates processing
to firmware/stages/*. Main loop only handles timing and window management.
"""

from machine import I2C, Pin, PWM, Timer
import time
import sys

from common.config import (
    SAMPLES, SAMPLE_INTERVAL_US, LED_PIN, LRA_PIN, LRA_FREQ,
    LRA_PINS, USE_LRA_ARRAY, I2C_BUS, I2C_SCL_PIN, I2C_SDA_PIN,
    I2C_FREQ, AUDIT_CAPACITY,
)
from common.gy521 import GY521

# ---- HARDWARE ----
led = Pin(LED_PIN, Pin.OUT)
lra = PWM(Pin(LRA_PIN), freq=LRA_FREQ, duty=0)
if USE_LRA_ARRAY:
    lra_array = [PWM(Pin(pin), freq=LRA_FREQ, duty=0) for pin in LRA_PINS]
else:
    lra_array = []

i2c = I2C(I2C_BUS, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQ)
try:
    sensor = GY521(i2c)
    print("GY-521 OK. HSP dispatcher online.")
except Exception as e:
    print("Sensor init failed:", e)
    sys.exit()

# ---- STAGES ----
from stages import STAGE_ORDER
from stages.safety import SafetyStage
from stages.sensor import SensorStage
from stages.stationarity import StationarityStage
from stages.fft import FFTStage
from stages.features import FeaturesStage
from stages.classify import ClassifyStage
from stages.haptic import HapticStage
from stages.audit import AuditStage

# Shared frame dict passed through pipeline
frame = {
    "now_us": 0,
    "prev_us": None,
    "window": [[0.0, 0.0, 0.0] for _ in range(SAMPLES)],
    "led": led,
    "lra": lra,
    "lra_array": lra_array,
    "use_lra_array": USE_LRA_ARRAY,
    "sensor": sensor,
}

# Pre-allocate stages
stages = {
    "safety": SafetyStage(),
    "sensor": SensorStage(sensor, frame["window"], SAMPLES),
    "stationarity": StationarityStage(window_len=SAMPLES),
    "fft": FFTStage(samples=SAMPLES, fs=100.0),
    "features": FeaturesStage(fs=100.0, n=SAMPLES),
    "classify": ClassifyStage(samples=SAMPLES, fs=100.0),
    "haptic": HapticStage(),
    "audit": AuditStage(capacity=AUDIT_CAPACITY),
}

# ---- TIMER SAMPLING ----
window_index = 0
first_sample_time = None
last_sample_time = None
window_ready = False
_sample_errors = 0  # Track consecutive sensor read errors


def sample_callback(t: Timer) -> None:
    """Timer ISR: read sensor sample and store in frame buffer.

    Keeps ISR short; logs errors via counter for main-loop visibility.
    """
    global window_index, first_sample_time, last_sample_time, window_ready, _sample_errors

    try:
        raw = sensor.i2c.readfrom_mem(sensor.addr, 0x3B, 6)

        def combine(h: int, l: int) -> int:
            v = (h << 8) | l
            return v if v < 32768 else v - 65536

        x = combine(raw[0], raw[1]) / 16384.0
        y = combine(raw[2], raw[3]) / 16384.0
        z = combine(raw[4], raw[5]) / 16384.0
        _sample_errors = 0  # Reset on success

    except Exception:
        _sample_errors += 1
        # Gravity fallback; flagged as sensor_error by sensor stage
        x, y, z = 0.0, 0.0, 1.0

    # Store sample in window buffer
    frame["window"][window_index][0] = x
    frame["window"][window_index][1] = y
    frame["window"][window_index][2] = z
    # Update per-sample values for sensor/stationarity stages
    frame["x"] = x
    frame["y"] = y
    frame["z"] = z

    # Track timing for actual_fs computation
    now = time.ticks_us()
    frame["prev_us"] = frame.get("now_us")
    frame["now_us"] = now
    if window_index == 0:
        first_sample_time = now
    last_sample_time = now

    window_index += 1
    if window_index >= SAMPLES:
        window_ready = True
        timer.deinit()


timer = Timer(0)
timer.init(period=SAMPLE_INTERVAL_US // 1000, mode=Timer.PERIODIC, callback=sample_callback)

# ---- MAIN LOOP ----
try:
    while True:
        if window_ready:
            window_ready = False

            # Expose error count for safety stage / telemetry
            frame["sample_errors"] = _sample_errors

            # Run pipeline
            for name in STAGE_ORDER:
                stage = stages[name]
                frame = stage.process(frame)
                if not frame.get("safe", True):
                    break

            # Reset for next window
            window_index = 0
            first_sample_time = None
            last_sample_time = None
            timer.init(period=SAMPLE_INTERVAL_US // 1000, mode=Timer.PERIODIC, callback=sample_callback)

        time.sleep(0.001)

except KeyboardInterrupt:
    timer.deinit()
    led.value(0)
    print("\nStopped.")