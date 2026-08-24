"""embedded_main.py — Real-time tremor classifier + haptic feedback on ESP32.

Pipeline:
  GY-521 -> 128-sample window @ 100Hz -> 15 features ->
  z-normalise -> 4-class logistic regression -> LED + LRA haptic.

Hardware:
  ESP32, GY-521 on I2C(0, scl=22, sda=21, freq=400000)
  LED on GPIO 2
  LRA on GPIO 25 (PWM via LEDC, 200 Hz drive)

If model.WEIGHTS is None, falls back to the heuristic from fft.py
(peak-in-band 3-12 Hz, magnitude > threshold).
"""

from machine import I2C, Pin, PWM, Timer
import time
import math
import sys

import model
import feature_extract
import scaler
import logreg
from fft import GY521, FFTProcessor


# ---- CONFIG ----

SAMPLES = 128
SAMPLE_INTERVAL_US = 10000   # 100 Hz
WINDOW_SECONDS = SAMPLES * SAMPLE_INTERVAL_US / 1_000_000  # 1.28 s

LED_PIN = 2
LRA_PIN = 25
LRA_FREQ = 200               # Hz, typical LRA resonance

# Heuristic fallback thresholds (used only if model.WEIGHTS is None)
HEURISTIC_LO_HZ = 3.0
HEURISTIC_HI_HZ = 12.0
HEURISTIC_MAG_THRESHOLD = 1.2

# Haptic policy
LRA_DUTY_ON = 512            # 50% of 1023
LRA_DUTY_OFF = 0

# Pre-allocate window buffer to avoid repeated allocation
WINDOW_BUFFER = [[0.0, 0.0, 0.0] for _ in range(SAMPLES)]


# ---- HARDWARE ----

led = Pin(LED_PIN, Pin.OUT)
lra = PWM(Pin(LRA_PIN), freq=LRA_FREQ, duty=LRA_DUTY_OFF)

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
try:
    sensor = GY521(i2c)
    print("GY-521 OK. 100Hz classifier online.")
except Exception as e:
    print("Sensor init failed:", e)
    sys.exit()

fft_proc = FFTProcessor(num_samples=SAMPLES)
print("Model: {}".format(
    "logistic-regression 4-class" if model.WEIGHTS is not None
    else "heuristic fallback (model.WEIGHTS is None)"))


# ---- HELPERS ----

# Timer-based sampling state
window_index = 0
first_sample_time = None
last_sample_time = None
window_ready = False

def sample_callback(t):
    global window_index, first_sample_time, last_sample_time, window_ready
    # Get sensor sample
    try:
        raw = sensor.i2c.readfrom_mem(sensor.addr, 0x3B, 6)
        def combine(h, l):
            v = (h << 8) | l
            return v if v < 32768 else v - 65536
        x = combine(raw[0], raw[1]) / 16384.0
        y = combine(raw[2], raw[3]) / 16384.0
        z = combine(raw[4], raw[5]) / 16384.0
    except Exception:
        x, y, z = 0.0, 0.0, 1.0  # gravity fallback

    # Store sample
    WINDOW_BUFFER[window_index][0] = x
    WINDOW_BUFFER[window_index][1] = y
    WINDOW_BUFFER[window_index][2] = z
    now = time.ticks_us()
    if window_index == 0:
        first_sample_time = now
    last_sample_time = now
    window_index += 1
    if window_index >= SAMPLES:
        window_ready = True
        timer.deinit()  # Stop timer to prevent overwriting while processing


# ---- FEEDBACK POLICY ----

def apply_feedback(label, conf):
    """Non-blocking. LED + LRA updated; haptic pulse scheduled via tick counters."""
    global _led_off_at, _lra_off_at
    now = time.ticks_ms()
    if label == "baseline":
        led.value(0)
        lra.duty(LRA_DUTY_OFF)
        return
    if label == "rest":
        led.value(0)
        lra.duty(LRA_DUTY_OFF)
        return
    if label == "postural":
        # 0.5 Hz blink (1s on, 1s off)
        phase = (now // 1000) % 2
        led.value(1 if phase == 0 else 0)
        lra.duty(LRA_DUTY_OFF)
        return
    if label == "kinetic":
        led.value(1)
        # 2 Hz pulse, 100 ms on, 400 ms off
        phase = (now // 500) % 2
        lra.duty(LRA_DUTY_ON if phase == 0 else LRA_DUTY_OFF)
        return
    # unknown
    led.value(0)
    lra.duty(LRA_DUTY_OFF)


# ---- MAIN LOOP ----

use_model = model.WEIGHTS is not None
last_log = time.ticks_ms()
try:
    # Initialize timer for periodic sampling
    timer = Timer(0)
    timer.init(period=SAMPLE_INTERVAL_US // 1000, mode=Timer.PERIODIC, callback=sample_callback)

    while True:
        if window_ready:
            # Process the filled window
            window_ready = False
            # Calculate actual sampling frequency from first and last sample timestamps (for potential future use)
            # Note: current processing functions use fixed 100.0 Hz, but we compute actual_fs for reference/metrics
            if first_sample_time is not None and last_sample_time is not None:
                total_time_us = time.ticks_diff(last_sample_time, first_sample_time)
                if total_time_us > 0:
                    actual_fs = SAMPLES / (total_time_us / 1000000.0)
                else:
                    actual_fs = SAMPLES / (SAMPLE_INTERVAL_US / 1000000.0)  # fallback
            else:
                actual_fs = SAMPLES / (SAMPLE_INTERVAL_US / 1000000.0)  # fallback

            # For now, we use fixed 100.0 Hz in processing functions as before
            window = WINDOW_BUFFER
            if use_model:
                label, conf, probs = classify_logreg(window)
            else:
                label, conf, _ = classify_heuristic(window)
                probs = None

            apply_feedback(label, conf)

            now = time.ticks_ms()
            if time.ticks_diff(now, last_log) >= 500:
                if probs is not None:
                    pstr = "[" + ", ".join("{:.2f}".format(p) for p in probs) + "]"
                else:
                    pstr = "n/a"
                print("pred={:>8s} conf={:.2f} probs={} dt={}ms".format(
                    label, conf, pstr, time.ticks_diff(now, t0)))
                last_log = now

            # Reset state and restart timer for next window
            window_index = 0
            first_sample_time = None
            last_sample_time = None
            window_ready = False
            timer.init(period=SAMPLE_INTERVAL_US // 1000, mode=Timer.PERIODIC, callback=sample_callback)

        time.sleep(0.001)  # Short sleep to prevent busy-wait in main loop

except KeyboardInterrupt:
    timer.deinit()
    led.value(0)
    lra.duty(LRA_DUTY_OFF)
    print("\nStopped.")