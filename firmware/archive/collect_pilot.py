from machine import I2C, Pin
import time
import sys

# ---- 1. HARDWARE & SENSOR CLASS ----
# Reuses GY521 init sequence from fft.py / raw_data_collection.py:
#   reset 0x6B=0x80, wake 0x6B=0x00, +/-2g 0x1C=0x00, DLPF94 0x1A=0x02, div0 0x19=0x00

class GY521:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x80')  # reset
        time.sleep(0.1)
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')  # wake
        self.i2c.writeto_mem(self.addr, 0x1C, b'\x00')  # +/- 2g
        self.i2c.writeto_mem(self.addr, 0x1A, b'\x02')  # DLPF 94 Hz
        self.i2c.writeto_mem(self.addr, 0x19, b'\x00')  # sample-rate div 0

    def _combine(self, high, low):
        val = (high << 8) | low
        return val if val < 32768 else val - 65536

    def read_3axis(self):
        try:
            raw = self.i2c.readfrom_mem(self.addr, 0x3B, 6)
            x = self._combine(raw[0], raw[1]) / 16384.0
            y = self._combine(raw[2], raw[3]) / 16384.0
            z = self._combine(raw[4], raw[5]) / 16384.0
            return x, y, z
        except Exception:
            return 0.0, 0.0, 1.0  # gravity fallback, marks error window


# ---- 2. CAPTURE CONFIG ----

# Set LABEL before each session: "rest" | "postural" | "kinetic" | "baseline"
LABEL = "rest"

SAMPLES = 128             # 1.28s window
SAMPLE_INTERVAL_US = 10000  # 10ms = 100 Hz
SESSION_SECONDS = 30        # auto-stop
SESSIONS_TOTAL = 1          # bump to capture multiple sessions per flash
REST_BETWEEN_S = 0          # set 60 for back-to-back with rest
# Pre-allocate buffer for 3-axis data to avoid repeated allocation
RAW_DATA_BUFFER = [0.0] * (SAMPLES * 3)

led = Pin(2, Pin.OUT)
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)

try:
    sensor = GY521(i2c)
    print("GY-521 3-Axis 100Hz Pilot Capture Ready")
    print("LABEL =", LABEL)
    print("WINDOW = {} samples / {:.2f}s".format(SAMPLES, SAMPLES * SAMPLE_INTERVAL_US / 1_000_000))
    print("SESSION = {}s, TOTAL = {}".format(SESSION_SECONDS, SESSIONS_TOTAL))
except Exception as e:
    print("Connection Failed:", e)
    sys.exit()


# ---- 3. CAPTURE LOOP ----

try:
    for sess in range(SESSIONS_TOTAL):
        print("\n=== SESSION {}/{} ===".format(sess + 1, SESSIONS_TOTAL))
        print("Get ready... LED on in 3s")
        time.sleep(3)
        led.value(1)

        t_session_start = time.ticks_us()
        t_end_us = time.ticks_add(t_session_start, SESSION_SECONDS * 1_000_000)
        window_idx = 0

        while time.ticks_diff(t_end_us, time.ticks_us()) > 0:
            buf = RAW_DATA_BUFFER
            t_window_start = time.ticks_us()

            for i in range(SAMPLES):
                t_sample = time.ticks_us()
                x, y, z = sensor.read_3axis()
                buf[i * 3 + 0] = x
                buf[i * 3 + 1] = y
                buf[i * 3 + 2] = z
                while time.ticks_diff(time.ticks_us(), t_sample) < SAMPLE_INTERVAL_US:
                    pass

            actual_fs = SAMPLES / (time.ticks_diff(time.ticks_us(), t_window_start) / 1_000_000)
            row = LABEL + "," + ",".join("{:.4f}".format(v) for v in buf)
            print(row)
            window_idx += 1

            # tiny blink to show life
            led.value(0)
            time.sleep_ms(20)
            led.value(1)

        led.value(0)
        elapsed = time.ticks_diff(time.ticks_us(), t_session_start) / 1_000_000
        print("Session {}/{} done. windows={}, elapsed={:.2f}s".format(
            sess + 1, SESSIONS_TOTAL, window_idx, elapsed))

        if sess < SESSIONS_TOTAL - 1 and REST_BETWEEN_S > 0:
            print("Rest {}s...".format(REST_BETWEEN_S))
            time.sleep(REST_BETWEEN_S)

    print("\nAll sessions done. LED off.")
    led.value(0)

except KeyboardInterrupt:
    led.value(0)
    print("\nLoop stopped.")
