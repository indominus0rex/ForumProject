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

from machine import I2C, Pin, PWM
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

def capture_window():
    """Return 2D list [128][3] of x,y,z at 100 Hz."""
    win = [[0.0, 0.0, 0.0] for _ in range(SAMPLES)]
    for i in range(SAMPLES):
        t0 = time.ticks_us()
        x, y, z = sensor.get_3axis_vector_raw() if hasattr(sensor, "get_3axis_vector_raw") else None, None, None
        if x is None:
            raw = sensor.i2c.readfrom_mem(sensor.addr, 0x3B, 6)
            def combine(h, l):
                v = (h << 8) | l
                return v if v < 32768 else v - 65536
            x = combine(raw[0], raw[1]) / 16384.0
            y = combine(raw[2], raw[3]) / 16384.0
            z = combine(raw[4], raw[5]) / 16384.0
        win[i][0] = x
        win[i][1] = y
        win[i][2] = z
        while time.ticks_diff(time.ticks_us(), t0) < SAMPLE_INTERVAL_US:
            pass
    return win


def classify_logreg(window):
    feats = feature_extract.compute(window, fs=100.0, n=SAMPLES)
    x = scaler.apply(feats, model.FEATURE_MEAN, model.FEATURE_STD)
    _, probs = logreg.forward(x, model.WEIGHTS, model.BIAS)
    idx = logreg.argmax(probs)
    return model.CLASSES[idx], probs[idx], probs


def classify_heuristic(window):
    # flatten to magnitude then reuse FFTProcessor.process_data
    flat = []
    for r in window:
        flat.extend(r)
    signal = [math.sqrt(window[i][0] ** 2 + window[i][1] ** 2 + window[i][2] ** 2)
              for i in range(SAMPLES)]
    freq, mag = fft_proc.process_data(signal, 100.0)
    if mag == 0.0:
        return "rest", 0.0, None
    if HEURISTIC_LO_HZ <= freq <= HEURISTIC_HI_HZ and mag >= HEURISTIC_MAG_THRESHOLD:
        return "kinetic", mag, None
    if freq < HEURISTIC_LO_HZ and mag >= 0.5:
        return "postural", mag, None
    return "rest", mag, None


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
    while True:
        t0 = time.ticks_ms()
        window = capture_window()
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

except KeyboardInterrupt:
    led.value(0)
    lra.duty(LRA_DUTY_OFF)
    print("\nStopped.")
