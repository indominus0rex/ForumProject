"""common/config.py — Centralized configuration for firmware."""

# Sampling
SAMPLES = 128
SAMPLE_INTERVAL_US = 10000  # 100 Hz
SAMPLE_RATE_HZ = 100.0
WINDOW_SECONDS = SAMPLES * SAMPLE_INTERVAL_US / 1_000_000  # 1.28 s

# Hardware pins
LED_PIN = 2
LRA_PIN = 25
LRA_FREQ = 200
LRA_PINS = [18, 19, 20]  # Proximal-to-distal: [hypothenar, thenar, dorsal]
USE_LRA_ARRAY = False

# I2C
I2C_BUS = 0
I2C_SCL_PIN = 22
I2C_SDA_PIN = 21
I2C_FREQ = 400000
GY521_ADDR = 0x68

# LRA duty cycles
LRA_DUTY_ON = 512
LRA_DUTY_OFF = 0

# Heuristic fallback thresholds (used when model.WEIGHTS is None)
HEURISTIC_LO_HZ = 3.0
HEURISTIC_HI_HZ = 12.0
HEURISTIC_MAG_THRESHOLD = 1.2

# Stationarity
STATIONARITY_RATIO_THRESH = 0.15

# Audit
AUDIT_CAPACITY = 32

# Data collection defaults
DEFAULT_LABEL = "rest"
DEFAULT_SESSION_SECONDS = 30
DEFAULT_SESSIONS_TOTAL = 1
DEFAULT_REST_BETWEEN_S = 0

# TCA9548A multiplexer (for RawDataCollection)
TCA9548A_ADDR = 0x70
NUM_IMUS = 4