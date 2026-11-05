"""embedded_main_hsp.py — Thin dispatcher for Hierarchical Stage Pipeline.

Keeps all hardware contracts from embedded_main.py but delegates processing
to firmware/stages/*. Main loop only handles timing and window management.
"""

from machine import I2C, Pin, PWM, Timer
import time
import sys

from common.config import (
    SAMPLES, SAMPLE_INTERVAL_US, LED_PIN,
    TB6612FNG_PIN_AIN1, TB6612FNG_PIN_AIN2,
    TB6612FNG_PIN_PWMA, TB6612FNG_PIN_STBY,
    TB6612FNG_DUTY_ON, TB6612FNG_DUTY_OFF,
    I2C_BUS, I2C_SCL_PIN, I2C_SDA_PIN,
    I2C_FREQ, AUDIT_CAPACITY,
    TCA9548A_ADDR, NUM_IMUS, I2C_MUX_ENABLED, IMU_CHANNELS, IMU_LOCATIONS,
    BANDPASS_LOW_HZ, BANDPASS_HIGH_HZ,
    USE_STFT, STFT_FRAME_LEN, STFT_HOP,
    SAMPLE_RATE_HZ,
    QUALITY_FALLBACK_THRESH, QUALITY_FLAT_VAR_THRESH,
)
from common.gy521 import GY521
try:
    from common.tca9548a import TCA9548A
except ImportError:
    TCA9548A = None

# ---- HARDWARE ----
led = Pin(LED_PIN, Pin.OUT)

# TB6612FNG dual H-bridge motor driver for ERM (replaces LRA PWM)
# Channel A: AIN1, AIN2, PWMA, STBY
# VMOT: external motor power (2.5-5.5V) — NOT from ESP32 GPIO
# VCC: logic power (3.3V from ESP32 or separate)
# GND: common ground (ESP32 GND + VMOT GND must be common)
tb6612 = {
    "ain1": Pin(TB6612FNG_PIN_AIN1, Pin.OUT),
    "ain2": Pin(TB6612FNG_PIN_AIN2, Pin.OUT),
    "pwma": PWM(Pin(TB6612FNG_PIN_PWMA), freq=1000, duty=0),  # 1kHz PWM for ERM
    "stby": Pin(TB6612FNG_PIN_STBY, Pin.OUT),
}
# Enable driver: STBY high, direction set, PWM off initially
tb6612["stby"].value(1)  # enable
tb6612["ain1"].value(1)  # direction (unidirectional for ERM)
tb6612["ain2"].value(0)
tb6612["pwma"].duty(0)   # start with motor off

i2c = I2C(I2C_BUS, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQ)

# TCA9548A mux for 4 IMUs (scalable 1..4) — research lock 2026-08-27 thumb CMC
mux = None
sensors = []
if I2C_MUX_ENABLED and TCA9548A is not None:
    try:
        mux = TCA9548A(i2c, addr=TCA9548A_ADDR)
        # Validate mux present
        if TCA9548A_ADDR not in i2c.scan():
            print("TCA9548A not found at 0x70 — falling back to single IMU.")
            mux = None
        else:
            for ch in IMU_CHANNELS[:NUM_IMUS]:
                mux.select_channel(ch)
                try:
                    s = GY521(i2c)  # each at 0x68 behind mux
                    sensors.append(s)
                    print("GY-521 ch{} ({} ) OK.".format(ch, IMU_LOCATIONS[ch] if ch < len(IMU_LOCATIONS) else ch))
                except Exception as e:
                    print("GY-521 ch{} init failed:".format(ch), e)
            if not sensors:
                print("No IMUs behind mux — falling back to single.")
                mux = None
            else:
                print("Mux online: {} IMU(s) via TCA9548A. Primary ch0 dorsal wrist for classification.".format(len(sensors)))
                sensor = sensors[0]  # primary for legacy single-window pipeline
    except Exception as e:
        print("Mux init failed:", e, "— falling back to single IMU.")
        mux = None

if mux is None:
    try:
        sensor = GY521(i2c)
        sensors = [sensor]
        print("GY-521 OK (single). HSP dispatcher online — use ch0 dorsal wrist.")
    except Exception as e:
        print("Sensor init failed:", e)
        sys.exit()

# ---- STAGES ----
from stages import STAGE_ORDER
from stages.safety import SafetyStage
from stages.sensor import SensorStage
from stages.stationarity import StationarityStage
from stages.quality import QualityStage
from stages.bandpass import BandpassStage
from stages.fft import FFTStage
from stages.stft import STFTStage
from stages.features import FeaturesStage
from stages.audit import AuditStage

# Shared frame dict passed through pipeline
# window = primary IMU (ch0 dorsal wrist) for existing classifier (backward-compatible)
# multi_window = list of 4 windows [128][3] for logging/future fusion (thumb CMC lock)
frame = {
    "now_us": 0,
    "prev_us": None,
    "window": [[0.0, 0.0, 0.0] for _ in range(SAMPLES)],
    "multi_window": [[[0.0, 0.0, 0.0] for _ in range(SAMPLES)] for _ in range(max(1, len(sensors)))],
    "led": led,
    "tb6612": tb6612,  # TB6612FNG motor driver controls (replaces lra/lra_array)
    "sensor": sensor,
    "sensors": sensors,
    "mux": mux,
    "num_imus": len(sensors),
}

# Pre-allocate stages
stages = {
    "safety": SafetyStage(),
    "sensor": SensorStage(sensor, frame["window"], SAMPLES),
    "stationarity": StationarityStage(window_len=SAMPLES),
    "quality": QualityStage(
        fallback_thresh=QUALITY_FALLBACK_THRESH,
        flat_thresh=QUALITY_FLAT_VAR_THRESH,
    ),
    "bandpass": BandpassStage(fs=SAMPLE_RATE_HZ, low_hz=BANDPASS_LOW_HZ,
                              high_hz=BANDPASS_HIGH_HZ),
    "fft": (STFTStage(samples=SAMPLES, fs=SAMPLE_RATE_HZ,
                      frame_len=STFT_FRAME_LEN, hop=STFT_HOP)
            if USE_STFT else
            FFTStage(samples=SAMPLES, fs=SAMPLE_RATE_HZ)),
    "features": FeaturesStage(fs=SAMPLE_RATE_HZ, n=SAMPLES),
    "audit": AuditStage(capacity=AUDIT_CAPACITY),
}

# ---- TIMER SAMPLING ----
window_index = 0
first_sample_time = None
last_sample_time = None
window_ready = False
_sample_errors = 0  # Track consecutive sensor read errors


def sample_callback(t: Timer) -> None:
    """Timer ISR: read ALL multiplexed IMUs per tick (scalable 1..4).

    Budget: 10ms @100Hz; 4× MPU6050 reads ~4ms @400kHz. Keeps ISR short.
    Primary ch0 feeds existing single-IMU pipeline (backward-compatible).
    All channels stored in multi_window for CSV logging / future 60-feat fusion.
    """
    global window_index, first_sample_time, last_sample_time, window_ready, _sample_errors

    # Helper to read one GY521 at 0x68
    def _read_one(s):
        try:
            raw = s.i2c.readfrom_mem(s.addr, 0x3B, 6)
            def combine(h: int, l: int) -> int:
                v = (h << 8) | l
                return v if v < 32768 else v - 65536
            x = combine(raw[0], raw[1]) / 16384.0
            y = combine(raw[2], raw[3]) / 16384.0
            z = combine(raw[4], raw[5]) / 16384.0
            return x, y, z, False
        except Exception:
            return 0.0, 0.0, 1.0, True

    if mux is not None and len(sensors) > 1:
        err_cnt = 0
        # Round-robin: select channel then read that IMU's 0x68
        for idx, s in enumerate(sensors):
            ch = IMU_CHANNELS[idx] if idx < len(IMU_CHANNELS) else idx
            try:
                mux.select_channel(ch)
            except Exception:
                err_cnt += 1
                x = y = 0.0; z = 1.0
                is_err = True
            else:
                x, y, z, is_err = _read_one(s)
                if is_err:
                    err_cnt += 1
            # Store in per-IMU multi_window
            try:
                frame["multi_window"][idx][window_index][0] = x
                frame["multi_window"][idx][window_index][1] = y
                frame["multi_window"][idx][window_index][2] = z
            except Exception:
                pass
            # Primary is ch0 (dorsal wrist) for existing pipeline
            if idx == 0:
                px, py, pz = x, y, z
                primary_err = is_err
        _sample_errors = err_cnt
        x, y, z = px, py, pz
        # expose per-IMU latest for quality stage extension
        frame["multi_xyz"] = [(frame["multi_window"][i][window_index][0],
                               frame["multi_window"][i][window_index][1],
                               frame["multi_window"][i][window_index][2]) for i in range(len(sensors))]
        frame["primary_err"] = primary_err
    else:
        x, y, z, is_err = _read_one(sensor)
        _sample_errors = 1 if is_err else 0
        try:
            frame["multi_window"][0][window_index][0] = x
            frame["multi_window"][0][window_index][1] = y
            frame["multi_window"][0][window_index][2] = z
        except Exception:
            pass
        frame["primary_err"] = is_err

    # Store sample in primary window buffer (backward-compatible)
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