# Assembly Checklist — Wearable Tremor Suppression Glove

Use this checklist to build a practical first prototype for the Forum Project wearable. It separates the **current firmware-safe build** from later multi-actuator / multi-IMU upgrades so you do not wire hardware that the code cannot read yet.

Current repo baseline:
- IMU: four GY-521 / MPU6050 via TCA9548A I2C multiplexer on I2C0, SDA=GPIO21, SCL=GPIO22.
- Status LED: GPIO2.
- Haptic output: **TB6612FNG dual H-bridge + ERM vibration motor**. GPIO25/AIN1, GPIO26/AIN2, GPIO27/PWMA, GPIO28/STBY. VMOT from external supply (NOT ESP32 GPIO).
- 0.1 µF decoupling capacitors near each IMU's VCC pin (×4).

Materials note: this checklist keeps the existing material choices unchanged: elastic nylon/spandex, breathable mesh / 3D spacer mesh, sew-on Velcro, flexible silicone wire, and polyester/nylon thread.

---

## Phase 1 — Choose Build Scope

| ☐ | Decision |
|---|---|
|| ☐ | **Recommended first build:** 4 IMUs via TCA9548A I2C multiplexer + TB6612FNG + ERM motor (matching `connections_4imu.csv` + `docs/erm_tb6612fng_wiring.md`) |
|| ☐ | Minimal smoke-test only: 1 ESP32 + 1 MPU6050 (no multiplexer) — for verifying basic IMU readout before committing to 4-IMU build |
|| ☐ | Multi-ERM build **optional** — only if additional actuators are procured and TB6612FNG channel B is wired |

Notes:
- Do **not** connect 3 MPU6050 boards all with AD0 tied to GND. They will all use address `0x68` and conflict on the same I2C bus.
- Without an I2C multiplexer, MPU6050 gives only two simple addresses: `0x68` when AD0=GND and `0x69` when AD0=3.3V.
- For 3+ IMUs, use a TCA9548A I2C multiplexer or separate buses plus firmware changes.

---

## Phase 2 — Power Section

Wire the power chain before connecting any ICs. Reference `cad/connections_4imu.csv:35-38`.

**Power path:** `LiPo+ → PPTC_900mA (in→out) → SW_3A (COM→NO) → MT3608 IN+`

|| ☐ | Connection |
||---|---|
|| ☐ | LiPo battery (+) → PPTC_900mA `IN` pad (red wire) |
|| ☐ | PPTC_900mA `OUT` → SW_3A slide switch `COM` terminal (red wire) |
|| ☐ | SW_3A slide switch `NO` → MT3608 `IN+` (red wire) |
|| ☐ | LiPo battery (−) → common GND rail (black wire) |
|| ☐ | Add 10 µF capacitor across MT3608 `IN+`/`IN−` (input bulk) |
|| ☐ | Add 10 µF capacitor across MT3608 `OUT+`/`OUT−` (output bulk) |
|| ☐ | Verify 5V output from MT3608 with multimeter before connecting ESP32 |

Notes:
- PPTC must come **before** the switch so the switch does not bypass overcurrent protection.
- Switch is SS22D07 3A SPDT; common terminal (COM) is center pin.

---

## Phase 3 — Parts Check

| ☐ | Item |
|---|---|
|| ☐ | ESP32-DevKitC or compatible ESP32 board |
|| ☐ | 4 × MPU6050 / GY-521 (one per IMU channel) |
|| ☐ | 1 × TCA9548A I2C multiplexer breakout board |
|| ☐ | 1 × PPTC_900mA resettable fuse (900mA hold / ~1.8A trip) |
|| ☐ | 1 × SW_3A slide switch (SS22D07 3A, SPDT) |
|| ☐ | 0.1 µF ceramic capacitors ×5 (one per IMU VCC + one for MT3608) |
|| ☐ | 10 µF ceramic capacitors ×2 (MT3608 boost input/output bulk) |
|| ☐ | 4.7 kΩ I2C pull-up resistors for SDA/SCL if no breakout board already has them installed |
|| ☐ | 10-100 µF bulk capacitor near ESP32 power rail, recommended |
|| ☐ | 30 AWG flexible silicone wire |
|| ☐ | Elastic nylon/spandex fabric |
|| ☐ | Breathable mesh / 3D spacer mesh |
|| ☐ | Sew-on Velcro hook and loop |
|| ☐ | Polyester/nylon thread |
|| ☐ | Heat-shrink tubing or electrical insulation |
|| ☐ | Power source: USB power bank for first test, or LiPo + proper charger + boost/regulator for wearable use |
|| ☐ | **TB6612FNG dual H-bridge breakout board** |
|| ☐ | **ERM vibration motor** (coin type, 10mm × 3mm, 1.5V-3V rated) |
|| ☐ | **VMOT power supply** for ERM (3V-5V, able to deliver 100-200mA) — can be separate battery or boost regulator |

Power warning:
- A single 3.7 V LiPo into ESP32 `VIN` is often not reliable because many dev boards expect ~5 V on VIN/5V.
- Easiest first prototype: use USB power bank into ESP32 USB.
- Wearable battery option: LiPo -> charger/protection -> 5 V boost -> ESP32 5V/VIN, or a safe regulated 3.3 V rail into 3V3 if you know your board’s limits.

---

## Phase 3 — Prepare Strap Base

| ☐ | Step |
|---|---|
| ☐ | Measure wrist/hand circumference where the strap will sit |
| ☐ | Cut elastic band to measured circumference + about 5 cm overlap |
| ☐ | Round or hem edges so fabric does not fray or scratch skin |
| ☐ | Add breathable mesh panel where IMU pocket will sit |
| ☐ | Add breathable mesh panel where actuator pocket will sit |
| ☐ | Sew Velcro hook on one end and loop on the other end for adjustable closure |
| ☐ | Check fit: snug enough to stop sensor sliding, not tight enough to restrict blood flow |

---

## Phase 4 — Sew Removable Pockets

Recommended pockets (4 IMU build):

| Pocket | Location | Cut size | Internal cavity |
|---|---|---:|---:|
| IMU (CH0) | Dorsal hand or wrist/hand back | 26 mm × 26 mm | ~22 mm × 22 mm |
| IMU (CH1) | Thenar eminence (palmar base of thumb) | 26 mm × 26 mm | ~22 mm × 22 mm |
| IMU (CH2) | Thumb proximal phalanx (dorsal-radial 20° tilt) | 26 mm × 26 mm | ~22 mm × 22 mm |
| IMU (CH3) | Index proximal phalanx (dorsal) | 26 mm × 26 mm | ~22 mm × 22 mm |

### Deferred (not this build)
| Pocket | Location | Cut size | Internal cavity |
|---|---|---:|---:|
| LRA/ERM | Thenar, hypothenar, or dorsal hand | 14-18 mm square | fit actual actuator |

| ☐ | Step |
|---|---|
| ☐ | Test pocket size with the actual IMU and actuator before sewing final version |
| ☐ | Cut pocket fabric with ~2 mm seam allowance |
| ☐ | Sew three sides, leaving one side open for insertion |
| ☐ | Add flap with Velcro closure so parts can be removed |
| ☐ | Keep Velcro away from direct skin contact |
| ☐ | Add small stabilizer strip inside pocket bottom if the component sags |
| ☐ | Leave a wire exit gap facing toward ESP32 housing |

---

## Phase 5 — Wire the IMUs (TCA9548A)

Wire the TCA9548A I2C multiplexer first, then connect each IMU to its channel. Reference `connections_4imu.csv`.

**TCA9548A wiring:**

| ☐ | Connection |
|---|---|
| ☐ | ESP32 3V3 -> TCA9548A VCC |
| ☐ | ESP32 GND -> TCA9548A GND |
| ☐ | ESP32 GPIO21 -> TCA9548A SDA |
| ☐ | ESP32 GPIO22 -> TCA9548A SCL |
| ☐ | TCA9548A A0, A1, A2 -> GND (address 0x70) |
| ☐ | TCA9548A EN -> 3.3V (enable) |

**Per-channel IMU wiring (×4, one per TCA9548A channel SD0–SD7):**

| ☐ | Connection |
|---|---|
| ☐ | TCA9548A VCC -> IMU VCC (all 4 IMUs) |
| ☐ | TCA9548A GND -> IMU GND (all 4 IMUs) |
| ☐ | TCA9548A SDn -> IMU SDA (one IMU per channel) |
| ☐ | TCA9548A SCn -> IMU SCL (one IMU per channel) |
| ☐ | Add 0.1 µF ceramic capacitor near each IMU's VCC pin |
| ☐ | Keep AD0 at default GND / `0x68` for all IMUs (channels isolate them) |
| ☐ | Keep wires short and flexible; stitch wire down every ~15 mm |
| ☐ | Add strain relief loop near each IMU pocket |

Before continuing:
- In Thonny, confirm the IMU can be initialized.
- If readings constantly fall back to `(0.0, 0.0, 1.0)`, treat it as wiring/address fault, not valid data.

---

## Phase 6 — Build Haptic Driver (TB6612FNG + ERM)

Use the TB6612FNG dual H-bridge to drive the ERM vibration motor. The TB6612FNG provides built-in flyback protection (no external diode needed) and accepts PWM speed control via PWMA pin.

**TB6612FNG wiring:**

|| ☐ | Connection |
||---|---|
|| ☐ | ESP32 3V3 → TB6612FNG VCC (logic power) |
|| ☐ | ESP32 GND → TB6612FNG GND (common ground) |
|| ☐ | ESP32 GPIO28 → TB6612FNG STBY (pulled HIGH to enable) |
|| ☐ | ESP32 GPIO25 → TB6612FNG AIN1 (direction) |
|| ☐ | ESP32 GPIO26 → TB6612FNG AIN2 (direction) |
|| ☐ | ESP32 GPIO27 → TB6612FNG PWMA (PWM speed control) |
|| ☐ | ERM motor (+) → TB6612FNG VMOT (motor power, 3V-5V external supply) |
|| ☐ | ERM motor (-) → common GND (same as ESP32 GND + TB6612FNG GND) |
|| ☐ | VMOT supply: separate 3V-5V source capable of 100-200mA (NOT from ESP32 GPIO) |
|| ☐ | Add heat-shrink over ESP32 solder joints |
|| ☐ | Add strain relief loop where wires enter ERM pocket |

**Direction configuration (unidirectional for ERM):**
- AIN1 = HIGH (GPIO25 → 1), AIN2 = LOW (GPIO26 → 0) → motor spins one way
- For ERM vibration, only one direction is needed.

**Do NOT power the ERM from ESP32 GPIO.** The TB6612FNG amplifies the PWM signal from PWMA using VMOT power. ESP32 GPIO only controls the logic pins.

**VMOT and ESP32 GND MUST share a common ground** for the H-bridge to function correctly.

---

## Phase 7 — Mount ESP32 and Route Wires

| ☐ | Step |
|---|---|
| ☐ | Put ESP32 on wrist/forearm side, not on palm or finger joints |
| ☐ | Put MOSFET/driver parts on small perfboard or secure insulated area |
| ☐ | Route wires along low-bend paths |
| ☐ | Stitch or tape wires every ~15 mm |
| ☐ | Avoid routing wires across knuckles or high-stress fold points |
| ☐ | Confirm strap still opens/closes easily with Velcro |
| ☐ | Confirm no exposed conductor touches skin |

---

## Phase 8 — Firmware Flash / Run

Per project docs, firmware files are flashed to ESP32 using Thonny.

| ☐ | Step |
|---|---|
| ☐ | Connect ESP32 by USB |
| ☐ | Open Thonny and select the MicroPython ESP32 interpreter |
| ☐ | Copy support files to device: `fft.py`, `feature_extract.py`, `logreg.py`, `scaler.py`, `model.py` |
| ☐ | Copy/run `embedded_main.py` last |
| ☐ | For auto-start, save the entry file as `main.py` on the device only after manual testing works |
| ☐ | Keep `USE_LRA_ARRAY = False` for first single-actuator test |

---

## Phase 9 — Bench Test Before Wearing

| ☐ | Test |
|---|---|
| ☐ | IMU initializes without error |
| ☐ | Still sensor gives stable acceleration around gravity |
| ☐ | Moving sensor changes x/y/z readings |
|| ☐ | GPIO2 LED behavior works |
|| ☐ | ERM stays off at boot (STBY checked, PWMA duty=0) |
|| ☐ | ERM turns on only when commanded |
|| ☐ | TB6612FNG does not get hot during a short 1-2 second test |
|| ☐ | ESP32 does not reset when ERM turns on |

Simple ERM test in Thonny for TB6612FNG on GPIO25/26/27/28:

```python
from machine import Pin, PWM
import time

# Setup (match config.py)
ain1 = Pin(25, Pin.OUT)
ain2 = Pin(26, Pin.OUT)
pwma = PWM(Pin(27), freq=1000, duty=0)
stby = Pin(28, Pin.OUT)

# Enable driver
stby.value(1)
ain1.value(1)  # direction
ain2.value(0)

# Test vibration patterns
pwma.duty(512)   # 50% duty — moderate vibration
time.sleep_ms(500)
pwma.duty(0)     # off
time.sleep_ms(200)
pwma.duty(1023)  # full speed
time.sleep_ms(500)
pwma.duty(0)     # off

# Disable driver
stby.value(0)
```

---

## Phase 10 — Wear Fit Check

| ☐ | Step |
|---|---|
| ☐ | Wear for 5 minutes with electronics off |
| ☐ | Check for pressure points, scratching, or restricted movement |
| ☐ | Confirm IMU pocket does not slide when opening/closing hand |
| ☐ | Confirm actuator pocket stays in skin contact |
| ☐ | Power on while wearing only after bench test passes |
| ☐ | Run short 10-20 second data capture |
| ☐ | Confirm vibration does not shake the IMU so strongly that readings become useless |

---

## Phase 11 — Data Collection Workflow

| ☐ | Step |
|---|---|
| ☐ | For baseline training, collect IMU data with actuator off |
| ☐ | Use `collect_pilot.py` for rest/postural/kinetic/baseline captures |
| ☐ | Save copied Thonny rows into `sessions/<label>_sNN.csv` |
| ☐ | Run `python analyze_pilot.py` from repo root |
| ☐ | Run `python train_classifier.py` from repo root after enough data is captured |
| ☐ | Copy trainer output block into `model.py` without hand-editing individual numbers |
| ☐ | Re-flash `model.py` and run `embedded_main.py` |

Important:
- If the actuator is vibrating during training capture, the IMU may learn the motor vibration instead of the tremor.
- For measuring suppression effect, record separate pre-feedback and post-feedback windows intentionally.

---

## Phase 12 — Optional Multi-ERM Upgrade

Only do this after the single-channel build works.

|| ☐ | Step |
||---|---|
|| ☐ | Confirm your ESP32 board exposes the chosen GPIO pins for TB6612FNG channel B |
|| ☐ | Use TB6612FNG channel B: BIN1, BIN2, PWMB (additional GPIO pins needed) |
|| ☐ | Add second ERM motor with its own VMOT or share VMOT if current budget allows |
|| ☐ | Wire channel B with same logic: BIN1=HIGH, BIN2=LOW, PWMB=PWM, STBY shared |
|| ☐ | Test channel B independently before combining with channel A |
|| ☐ | Update haptic stage if spatial sequencing is desired |

---

## Phase 13 — Multi-IMU Build (Current Config)

**Already baseline — see Phase 1.** This phase is the current locked configuration (4 IMUs via TCA9548A), not an upgrade. No additional steps needed here.

---

## Quick Pass/Fail Summary

| ☐ | Requirement |
|---|---|
|| ☐ | Strap fits comfortably and does not slip |
|| ☐ | IMU initializes reliably |
|| ☐ | ERM is driven through TB6612FNG (not directly by GPIO) |
|| ☐ | VMOT supply is separate from ESP32 (3V-5V, adequate current) |
|| ☐ | Common GND between ESP32, TB6612FNG, and VMOT |
|| ☐ | STBY pulled HIGH to enable driver |
|| ☐ | No exposed wires touch skin |
|| ☐ | ESP32 does not brown out when ERM turns on |
|| ☐ | First data collection is done with actuator off |
|| ☐ | Firmware is tested manually before saving as `main.py` |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| IMU always reads fallback `(0,0,1)` | SDA/SCL swapped, bad power, address conflict | Check GPIO21/22, 3V3/GND, AD0/address |
| Multiple IMUs do not work | Same I2C address conflict | Use AD0 split for 2 IMUs or TCA9548A for 3+ |
|| ERM does not vibrate | STBY low, wrong direction, no VMOT power, no common GND | Check STBY=HIGH, AIN1/AIN2, VMOT connected, GND common |
|| ERM spins but no vibration feel | Wrong motor terminal polarity | Swap ERM wires (+/-) |
|| ERM vibration weak | Low duty, poor skin contact, low VMOT voltage | Increase duty, reposition pocket, check VMOT voltage |
|| TB6612FNG hot | High duty sustained, insufficient VMOT | Reduce duty, add heatsink, check VMOT supply |
|| ESP32 resets when ERM starts | Brownout from VMOT supply sag | Add bulk cap on VMOT, use stronger supply, check common GND |
|| Intermittent vibration | Loose connection, missing strain relief | Check solder joints, add strain relief loop |
