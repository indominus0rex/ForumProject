# Assembly Checklist — Wearable Tremor Suppression Glove

Use this checklist to build a practical first prototype for the Forum Project wearable. It separates the **current firmware-safe build** from later multi-actuator / multi-IMU upgrades so you do not wire hardware that the code cannot read yet.

Current repo baseline:
- IMU: one GY-521 / MPU6050 on I2C0, SDA=GPIO21, SCL=GPIO22.
- Status LED: GPIO2.
- Haptic output: single LRA / vibration motor driver on GPIO25.
- Optional multi-LRA array code may use GPIO18/19/20, but check your ESP32 board first: many classic ESP32 DevKit boards do **not** expose GPIO20.

Materials note: this checklist keeps the existing material choices unchanged: elastic nylon/spandex, breathable mesh / 3D spacer mesh, sew-on Velcro, flexible silicone wire, and polyester/nylon thread.

---

## Phase 1 — Choose Build Scope

| ☐ | Decision |
|---|---|
| ☐ | **Recommended first build:** 1 ESP32 + 1 MPU6050 + 1 haptic actuator on GPIO25 |
| ☐ | Multi-LRA build only if your board exposes safe PWM GPIOs and `USE_LRA_ARRAY = True` is tested |
| ☐ | Multi-IMU build only after adding firmware support for multiple addresses or an I2C multiplexer |

Notes:
- Do **not** connect 3 MPU6050 boards all with AD0 tied to GND. They will all use address `0x68` and conflict on the same I2C bus.
- Without an I2C multiplexer, MPU6050 gives only two simple addresses: `0x68` when AD0=GND and `0x69` when AD0=3.3V.
- For 3+ IMUs, use a TCA9548A I2C multiplexer or separate buses plus firmware changes.

---

## Phase 2 — Parts Check

| ☐ | Item |
|---|---|
| ☐ | ESP32-DevKitC or compatible ESP32 board |
| ☐ | 1 × MPU6050 / GY-521 for first prototype |
| ☐ | Optional spare MPU6050 modules for later multi-IMU work |
| ☐ | 1 × LRA coin actuator, or ERM phone vibration motor if LRA is unavailable |
| ☐ | 1 × logic-level MOSFET for first actuator channel |
| ☐ | 1 × flyback diode, e.g. 1N4001 / 1N4148, for motor/LRA protection |
| ☐ | Optional 100 Ω gate resistor |
| ☐ | Optional 10 kΩ gate pulldown resistor from MOSFET gate to GND |
| ☐ | 4.7 kΩ I2C pull-up resistors for SDA/SCL if your GY-521 board does not already include them |
| ☐ | 0.1 µF ceramic capacitor near ESP32 power pins |
| ☐ | 10-100 µF bulk capacitor near actuator supply rail, recommended |
| ☐ | 30 AWG flexible silicone wire |
| ☐ | Elastic nylon/spandex fabric |
| ☐ | Breathable mesh / 3D spacer mesh |
| ☐ | Sew-on Velcro hook and loop |
| ☐ | Polyester/nylon thread |
| ☐ | Heat-shrink tubing or electrical insulation |
| ☐ | Optional JST-PH connectors for detachable actuators |
| ☐ | Power source: USB power bank for first test, or LiPo + proper charger + boost/regulator for wearable use |

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

Recommended first prototype pockets:

| Pocket | Location | Cut size | Internal cavity |
|---|---|---:|---:|
| IMU | Dorsal hand or wrist/hand back | 26 mm × 26 mm | ~22 mm × 22 mm |
| LRA/ERM | Thenar, hypothenar, or dorsal hand test position | 14-18 mm square depending on actuator | fit actual actuator |

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

## Phase 5 — Wire the IMU

For the current firmware-safe build:

| ☐ | Connection |
|---|---|
| ☐ | ESP32 3V3 -> GY-521 VCC |
| ☐ | ESP32 GND -> GY-521 GND |
| ☐ | ESP32 GPIO21 -> GY-521 SDA |
| ☐ | ESP32 GPIO22 -> GY-521 SCL |
| ☐ | Keep AD0 at default GND / `0x68` for one IMU |
| ☐ | Keep wires short and flexible; stitch wire down every ~15 mm |
| ☐ | Add strain relief loop near the IMU pocket |

Before continuing:
- In Thonny, confirm the IMU can be initialized.
- If readings constantly fall back to `(0.0, 0.0, 1.0)`, treat it as wiring/address fault, not valid data.

---

## Phase 6 — Build One Haptic Driver Channel

Use this for either a true LRA or the ERM phone vibration motor you found. A true LRA gives cleaner haptic pulses; an ERM works for simpler buzzing but needs longer pulse timing.

Low-side MOSFET wiring:

| ☐ | Connection |
|---|---|
| ☐ | Actuator + -> actuator supply voltage, usually 3 V to 5 V depending on part |
| ☐ | Actuator - -> MOSFET drain |
| ☐ | MOSFET source -> GND |
| ☐ | MOSFET gate -> ESP32 GPIO25 for first prototype |
| ☐ | ESP32 GND and actuator supply GND are common |
| ☐ | Flyback diode across actuator: cathode to actuator +, anode to actuator - / MOSFET drain |
| ☐ | Optional 100 Ω resistor between ESP32 GPIO and MOSFET gate |
| ☐ | Optional 10 kΩ pulldown from MOSFET gate to GND so motor stays off at boot |
| ☐ | Add heat-shrink over solder joints |
| ☐ | Add strain relief loop where wires enter actuator pocket |

Do not power an actuator directly from an ESP32 GPIO pin. The GPIO controls the MOSFET gate only.

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
| ☐ | GPIO2 LED behavior works |
| ☐ | Actuator stays off at boot |
| ☐ | Actuator turns on only when commanded |
| ☐ | MOSFET does not get hot during a short 1-2 second test |
| ☐ | ESP32 does not reset when actuator turns on |

Simple actuator test in Thonny for LRA on GPIO25:

```python
from machine import Pin, PWM
import time
m = PWM(Pin(25), freq=200, duty=0)
m.duty(512)
time.sleep_ms(200)
m.duty(0)
```

For ERM phone motor, a longer on-time may feel better:

```python
from machine import Pin
import time
m = Pin(25, Pin.OUT)
m.value(1)
time.sleep_ms(100)
m.value(0)
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

## Phase 12 — Optional Multi-LRA Upgrade

Only do this after the single-channel build works.

| ☐ | Step |
|---|---|
| ☐ | Confirm your ESP32 board exposes the chosen GPIO pins |
| ☐ | Avoid boot-strapping pins and pins not present on your board |
| ☐ | Prefer known safe PWM-capable pins such as GPIO25/26/27/32/33 if available |
| ☐ | Build one MOSFET driver channel per actuator |
| ☐ | Update `LRA_PINS` in `embedded_main.py` to match actual pins |
| ☐ | Set `USE_LRA_ARRAY = True` only after each channel is bench-tested |
| ☐ | Test proximal-to-distal pattern slowly before wearing |

Note: the earlier GPIO18/19/20 mapping is conceptual. GPIO20 is not available on many ESP32 DevKit boards, so verify your exact board pinout.

---

## Phase 13 — Optional Multi-IMU Upgrade

Only do this after firmware is updated.

| ☐ | Step |
|---|---|
| ☐ | Decide method: two addresses (`0x68`, `0x69`) or TCA9548A I2C multiplexer |
| ☐ | Update firmware to initialize and read each IMU separately |
| ☐ | Update data format before collecting training CSVs |
| ☐ | Update host-side feature extraction/training to match the new data format |
| ☐ | Re-check feature order coupling between firmware and trainer |

Do not wire 3 MPU6050 modules all in parallel with the same address.

---

## Quick Pass/Fail Summary

| ☐ | Requirement |
|---|---|
| ☐ | Strap fits comfortably and does not slip |
| ☐ | IMU initializes reliably |
| ☐ | Actuator is driven through MOSFET, not directly by GPIO |
| ☐ | Common ground is connected between ESP32 and actuator supply |
| ☐ | No exposed wires touch skin |
| ☐ | ESP32 does not brown out when actuator turns on |
| ☐ | First data collection is done with actuator off |
| ☐ | Firmware is tested manually before saving as `main.py` |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| IMU always reads fallback `(0,0,1)` | SDA/SCL swapped, bad power, address conflict | Check GPIO21/22, 3V3/GND, AD0/address |
| Multiple IMUs do not work | Same I2C address conflict | Use AD0 split for 2 IMUs or TCA9548A for 3+ |
| Motor/LRA does not vibrate | MOSFET wiring wrong or no common ground | Check source/drain/gate and shared GND |
| Motor vibrates at boot | Floating MOSFET gate | Add 10 kΩ pulldown gate -> GND |
| ESP32 resets when motor starts | Brownout / supply sag | Use stronger supply and add 10-100 µF bulk capacitor |
| Vibration weak | Wrong drive voltage/frequency or loose pocket | Check actuator spec, pocket contact, PWM freq |
| Strap slips | Too loose, no grip/stabilizer, Velcro dirty | Tighten, add silicone dots/stabilizer, clean Velcro |
