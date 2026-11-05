# ESP32 Pin Assignments and Component Specifications

## Overview
This document extracts the exact pin assignments and component specifications from the firmware configuration files (`common/config.py` and `embedded_main_hsp.py`) to ensure wiring diagram accuracy.

## Pin Definitions

### GPIO Usage
| Pin | Function | Details |
|-----|----------|---------|
| GPIO2 | LED | Output pin for status LED (active high) |
| GPIO25 | LRA (Single) | PWM output for Linear Resonant Actuator (main vibration motor) |
| GPIO18 | LRA Array (Optional) | PWM output for proximal LRA (hypothenar) when `USE_LRA_ARRAY = True` |
| GPIO19 | LRA Array (Optional) | PWM output for middle LRA (thenar) when `USE_LRA_ARRAY = True` |
| GPIO20 | LRA Array (Optional) | PWM output for distal LRA (dorsal) when `USE_LRA_ARRAY = True` |
| GPIO22 | I2C SCL | I2C clock line for sensor and multiplexer |
| GPIO21 | I2C SDA | I2C data line for sensor and multiplexer |

### PWM Channels
The firmware uses the ESP32's LEDC PWM controller. The following pins are configured for PWM:
- **GPIO25**: Main LRA control (frequency = 200 Hz, duty cycle configurable)
- **GPIO18, 19, 20**: Optional LRA array control (same frequency) when `USE_LRA_ARRAY = True`

Note: The ESP32 supports up to 16 independent PWM channels. The firmware does not explicitly configure LEDC channels; the MicroPython PWM object defaults to available channels.

### GPIO LED Usage
- GPIO2 is configured as a digital output (`Pin.OUT`) to drive an LED.
- The LED is turned on/off via `led.value(1)` or `led.value(0)`.

**⚠️ GPIO2 boot warning:** GPIO2 is an ESP32 strapping pin (MTDI). The 220Ω LED to GND could hold it LOW at boot, forcing UART download mode. Empirically verify boot behavior: if the ESP32 fails to boot with the LED connected, add a buffer transistor or move the LED to a non-strapping pin (e.g., GPIO4, GPIO5). See ESP32 Technical Reference Manual §3.4 Strapping Pins.

## I2C Bus Configuration
| Parameter | Value | Description |
|-----------|-------|-------------|
| I2C Bus | 0 | ESP32 I2C peripheral number |
| SCL Pin | GPIO22 | I2C clock line |
| SDA Pin | GPIO21 | I2C data line |
| Frequency | 400 kHz | Standard I2C frequency for MPU-6050 and TCA9548A |
| Pull-up Resistors | External (typically 4.7kΩ) | Required on SCL and SDA lines (not configured in firmware) |

### Connected I2C Devices
| Device | Address | Description |
|--------|---------|-------------|
| GY-521 (MPU-6050) | 0x68 | 6-axis accelerometer/gyroscope sensor |
| TCA9548A Multiplexer | 0x70 | 1-to-8 I2C multiplexer (only 4 channels used) |

## Multiplexer (TCA9548A) Address and Channel Mapping — **LOCKED 2026-08-27 Option A + ET (thumb+index phalanx, LRAs deferred)**
- **I2C Address**: 0x70 (fixed by hardware pin grounding; AD0, AD1, AD2 pins grounded)
- **Number of IMUs**: 4 (as defined by `NUM_IMUS = 4` in `firmware/common/config.py:59`) — scalable 1→4, validate incrementally.
- **Channel Mapping (2026-08-27 Option A — pill-rolling + ET, balanced 0.6)**:
  - IMU 0 (Dorsal wrist, just proximal to joint, dorsal side): Channel 0 — primary, Keba 2025 rubber-band 100Hz method (`https://www.mdpi.com/2077-0383/14/6/2073`) — rest baseline
  - IMU 1 (Thenar eminence, volar thumb base): Channel 1 — per `component_positions.txt:9`
  - IMU 2 (Thumb proximal phalanx, dorsal-radial 20° tilt): Channel 2 — **was CMC, now phalanx** per pill-rolling 4–6Hz optimization; 20° tilt aligns X to flexion, Z still up (`docs/component_positions.txt:13` fallback)
  - IMU 3 (Index proximal phalanx, dorsal): Channel 3 — **was forearm, now index** per ET postural 6–8Hz; thumb-index coherence >0.6 pill-rolling, finger-wrist >0.6 ET postural (`firmware/common/config.py:64`)
  - Channels 4-7: Not used (forearm becomes optional CH4 if re-added)
- **Selection**: MicroPython `i2c.writeto(0x70, bytes([1<<ch]))` then `readfrom_mem(0x68, 0x3B, 6)` as in `firmware/raw_data_collection.py:48` and web tutorials `https://randomnerdtutorials.com/tca9548a-i2c-multiplexer-esp32-esp8266-arduino/`. All GY-521 at `0x68` isolated.
- **LRAs**: **Deferred** for this build — `GPIO25/18/19/20` left unpopulated; `USE_LRA_ARRAY=False`. HSP `haptic` stage will no-op with duty 0. When procured, see `docs/imu_lra_placement.txt` dorsum MC2-3.

## Frequencies and Timing
| Parameter | Value | Description |
|-----------|-------|-------------|
| Sampling Interval | 10,000 µs (100 Hz) | Time between samples (`SAMPLE_INTERVAL_US`) |
| LRA PWM Frequency | 200 Hz | Frequency for vibration motor (`LRA_FREQ`) |
| I2C Frequency | 400 kHz | Bus speed for reliable communication |

## Duty Cycle Values (LRA)
| Parameter | Value | Description |
|-----------|-------|-------------|
| LRA_DUTY_ON | 512 | PWM duty cycle for motor on (out of 1023) |
| LRA_DUTY_OFF | 0 | PWM duty cycle for motor off |

## Source Files
- `firmware/common/config.py`: Contains pin definitions and configuration constants.
- `firmware/embedded_main_hsp.py`: Shows hardware initialization and usage of the pins.

## Notes
1. When `USE_LRA_ARRAY = False` (default), only the single LRA on GPIO25 is used. **For current 4-IMU no-LRA build, GPIO25/18/19/20 are intentionally unpopulated.**
2. The LED on GPIO2 is used for status indication (e.g., error codes, readiness).
3. The I2C bus is shared between the MPU-6050 sensor and the TCA9548A multiplexer — all IMUs at `0x68` isolated per channel; **do not wire 3×0x68 in parallel** (`docs/assembly_checklist.md:24`).
4. The multiplexer allows multiple IMUs to share the same I2C address by selecting different channels — short wires <15cm to avoid WiFi I2C glitches per `https://zbotic.in/mpu6050-imu-sensor-complete-tutorial-with-arduino-python`.
5. All pin numbers are ESP32 GPIOs (not ADC-specific or strapping pins).
6. 2026-08-27 Option A+ET lock: Thumb proximal phalanx 20° + index phalanx (replaces CMC+forearm), pill 4–6Hz + ET 6–8Hz, coherence 0.6 balanced — see `knowledge.md:5a` + `docs/research_web_2026-08-27.md` + `firmware/common/config.py:64`.

---
*Updated 2026-08-27 for Option A + ET (thumb phalanx + index phalanx) — see `docs/research_web_2026-08-27.md`*

---
*Documentation generated from firmware source files for wiring diagram accuracy.*