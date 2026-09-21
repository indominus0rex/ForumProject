"""common/config.py — Centralized configuration for firmware."""

# Sampling
SAMPLES = 128
SAMPLE_INTERVAL_US = 10000  # 100 Hz
SAMPLE_RATE_HZ = 100.0
WINDOW_SECONDS = SAMPLES * SAMPLE_INTERVAL_US / 1_000_000  # 1.28 s

# Hardware pins
LED_PIN = 2

# TB6612FNG dual H-bridge motor driver (replaces LRA PWM):
#  - VMOT: motor power supply (2.5V-5.5V) — do NOT power from ESP32 GPIO
#  - VCC: logic power (2.7V-5.5V), can use ESP32 3V3
#  - GND: common ground (ESP32 GND + VMOT GND must be common)
#  - STBY: standby — pulled HIGH to enable driver, LOW to disable
#  - AIN1, AIN2: direction control for channel A (single ERM)
#  - PWMA: PWM speed control for channel A (0-1023 duty)
#  - BIN1, BIN2, PWMB: channel B unused for single-ERM build
# Direction: AIN1=1, AIN2=0 → motor spins one way; AIN1=0, AIN2=1 → reverse.
# For ERM (unidirectional vibration), only one direction is used.
TB6612FNG_PIN_AIN1 = 25
TB6612FNG_PIN_AIN2 = 26
TB6612FNG_PIN_PWMA = 27
TB6612FNG_PIN_STBY = 28
# Motor supply voltage for ERM (check your ERM datasheet, typically 1.5V-3V for coin motors)
# TB6612FNG VMOT must be >= motor rated voltage; TB6612FNG VCC can be 3.3V from ESP32
ERM_VMOT_VOLTS = 3.0  # adjust to your ERM spec

# I2C
I2C_BUS = 0
I2C_SCL_PIN = 22
I2C_SDA_PIN = 21
I2C_FREQ = 400000
GY521_ADDR = 0x68

# Stationarity
STATIONARITY_RATIO_THRESH = 0.15

# Signal quality gate
QUALITY_FALLBACK_THRESH = 0.08
QUALITY_SATURATION_G = 1.95
QUALITY_FLAT_VAR_THRESH = 1e-5

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

# Bandpass filter parameters
BANDPASS_LOW_HZ = 3.0           # Lower cutoff frequency
BANDPASS_HIGH_HZ = 12.0         # Upper cutoff frequency

# STFT (Short-Time Fourier Transform) selection
USE_STFT = False             # False = single FFT (default, proven); True = overlapping STFT
STFT_FRAME_LEN = 64          # must be power of 2 (freq resolution 100/64 = 1.5625 Hz)
STFT_HOP = 32                # 50% overlap; must divide 128-64

# Pipeline stage tunables (single source of truth)
PIPELINE_CONFIG = {
    # Quality stage
    "QUALITY_FALLBACK_THRESH": 0.08,
    "QUALITY_SATURATION_G": 1.95,
    "QUALITY_FLAT_VAR_THRESH": 1e-5,
    "QUALITY_GRAVITY_MIN": 0.6,
    "QUALITY_GRAVITY_MAX": 1.6,
    "QUALITY_JITTER_VAR_THRESH": 5.0,
    # Stationarity stage
    "STATIONARITY_RATIO_THRESH": 0.15,
    # FFT stage
    "FFT_NOISE_THRESHOLD": 0.35,
    # Safety stage
    "SAFETY_TIME_JUMP_US": 2_000_000,
    "SAFETY_DRIFT_G": 0.10,
    "SAFETY_HIST_LEN": 16,
}