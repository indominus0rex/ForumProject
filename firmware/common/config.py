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

# Signal quality gate
QUALITY_FALLBACK_THRESH = 0.08
QUALITY_SATURATION_G = 1.95
QUALITY_FLAT_VAR_THRESH = 1e-5

# State machine / confidence gating
CONF_THRESH_KINETIC = 0.55
CONF_THRESH_POSTURAL = 0.50
STATE_CONFIRM_WINDOWS = 2
STATE_COOLDOWN_WINDOWS = 2
STATE_MAX_TREMOR_BEFORE_COOLDOWN = 4

# Audit
AUDIT_CAPACITY = 32
EVENT_LOG_ENABLED = True

# Data collection defaults
DEFAULT_LABEL = "rest"
DEFAULT_SESSION_SECONDS = 30
DEFAULT_SESSIONS_TOTAL = 1
DEFAULT_REST_BETWEEN_S = 0

# TCA9548A multiplexer (for 4-IMU build 2026-08-27)
TCA9548A_ADDR = 0x70
NUM_IMUS = 4  # scalable 1..4 via I2C_MUX_ENABLED
I2C_MUX_ENABLED = True  # True = 4 IMUs via TCA9548A ch0-3; False = single GY521 at 0x68
# Channel mapping locked 2026-08-27 Option A + ET (thumb+index phalanx, balance 0.6):
#  ch0 = dorsal wrist proximal (Keba 2025 primary), ch1 = thenar volar,
#  ch2 = thumb proximal phalanx dorsal-radial 20° tilt (pill-rolling 4-6Hz, ET distal), ch3 = index proximal phalanx dorsal (ET 6-8Hz postural, thumb-index coherence)
IMU_CHANNELS = [0, 1, 2, 3]
IMU_LOCATIONS = ["dorsal_wrist", "thenar", "thumb_prox_phalanx", "index_prox_phalanx"]

# Pill-rolling + Essential Tremor thresholds (balanced 0.6, Option A)
PILL_BAND_LO_HZ = 4.0
PILL_BAND_HI_HZ = 6.0
ET_BAND_LO_HZ = 6.0
ET_BAND_HI_HZ = 9.0
COH_THUMB_INDEX_THRESH = 0.60  # pill-rolling discriminant (thumb phalanx vs index phalanx)
COH_FINGER_WRIST_THRESH = 0.60  # ET postural discriminant (mean[thumb,index] vs wrist)