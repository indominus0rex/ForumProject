"""collect_pilot_4imu.py — 4-IMU pilot capture via TCA9548A (thumb CMC lock 2026-08-27).

Wiring: TCA9548A ch0 dorsal wrist, ch1 thenar, ch2 thumb CMC dorsal, ch3 forearm proximal.
Outputs CSV rows: LABEL,imu0_ax1...az128,imu1_...,imu2_...,imu3_...  (1 + 384*NUM_IMUS cols)
Host train_classifier.py must be updated to split per-IMU features (15*NUM_IMUS).

For 1-IMU fallback set NUM_IMUS=1 and I2C_MUX_ENABLED=False in common/config.py.
"""

from machine import I2C, Pin
import time
import sys

from common.config import (
    SAMPLES, SAMPLE_INTERVAL_US,
    I2C_BUS, I2C_SCL_PIN, I2C_SDA_PIN, I2C_FREQ,
    TCA9548A_ADDR, NUM_IMUS, IMU_CHANNELS, IMU_LOCATIONS,
)
from common.gy521 import GY521
from common.tca9548a import TCA9548A

# ---- CONFIG ----
LABEL = "rest"  # change per session: rest|postural|kinetic|baseline
SESSION_SECONDS = 30
SESSIONS_TOTAL = 1
REST_BETWEEN_S = 0
RAW_BUFFER = [0.0] * (SAMPLES * 3 * NUM_IMUS)

led = Pin(2, Pin.OUT)
i2c = I2C(I2C_BUS, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQ)

mux = None
sensors = []
try:
    mux = TCA9548A(i2c, addr=TCA9548A_ADDR)
    if TCA9548A_ADDR not in i2c.scan():
        raise RuntimeError("TCA9548A 0x70 not found")
    for idx in range(NUM_IMUS):
        ch = IMU_CHANNELS[idx]
        mux.select_channel(ch)
        s = GY521(i2c)
        sensors.append(s)
        print("IMU ch{} {} OK".format(ch, IMU_LOCATIONS[idx] if idx < len(IMU_LOCATIONS) else idx))
    print("4-IMU capture ready: LABEL={} chs={}".format(LABEL, IMU_CHANNELS[:NUM_IMUS]))
except Exception as e:
    print("Mux/IMU init failed:", e)
    sys.exit()

# ---- CAPTURE LOOP ----
try:
    for sess in range(SESSIONS_TOTAL):
        print("\n=== SESSION {}/{} LABEL={} ===".format(sess+1, SESSIONS_TOTAL, LABEL))
        print("Get ready... LED on in 3s")
        time.sleep(3)
        led.value(1)
        t_end = time.ticks_add(time.ticks_us(), SESSION_SECONDS * 1_000_000)
        win_idx = 0
        while time.ticks_diff(t_end, time.ticks_us()) > 0:
            buf = RAW_BUFFER
            t_win = time.ticks_us()
            for i in range(SAMPLES):
                t_s = time.ticks_us()
                base = i * 3 * NUM_IMUS
                for idx, s in enumerate(sensors):
                    ch = IMU_CHANNELS[idx]
                    try:
                        mux.select_channel(ch)
                        x, y, z = s.read_3axis()
                    except Exception:
                        x, y, z = 0.0, 0.0, 1.0
                    buf[base + idx*3 + 0] = x
                    buf[base + idx*3 + 1] = y
                    buf[base + idx*3 + 2] = z
                while time.ticks_diff(time.ticks_us(), t_s) < SAMPLE_INTERVAL_US:
                    pass
            row = LABEL + "," + ",".join("{:.4f}".format(v) for v in buf)
            print(row)
            win_idx += 1
            led.value(0); time.sleep_ms(20); led.value(1)
        led.value(0)
        print("Session {}/{} done windows={}".format(sess+1, SESSIONS_TOTAL, win_idx))
        if sess < SESSIONS_TOTAL-1 and REST_BETWEEN_S>0:
            print("Rest {}s...".format(REST_BETWEEN_S)); time.sleep(REST_BETWEEN_S)
    print("\nAll sessions done.")
    led.value(0)
except KeyboardInterrupt:
    led.value(0)
    print("\nStopped.")
