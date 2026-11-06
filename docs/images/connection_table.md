# Connection Table — 4-IMU ESP32 Tremor Monitor

**Date:** 2026-09-01
**Revision:** 5.0

---

## Quick Wire Color Guide

| Color | Use |
|-------|-----|
| 🔴 Red | Power (5V or 3.3V) |
| ⚫ Black | Ground |
| 🟢 Green | I²C Data (SDA) |
| 🔵 Blue | I²C Clock (SCL) |
| 🟡 Yellow | LED signal |

---

## Component-to-Component Connections

### J1 — Micro-USB (charging input)
| Pin | Connects To | Wire |
|-----|-------------|------|
| VBUS | → U7 IN+ | 🔴 Red |
| GND | → U7 IN- | ⚫ Black |

### U7 — TP4056 Charger Module
| Pad | Connects To | Wire |
|-----|-------------|------|
| IN+ | ← J1 VBUS | 🔴 Red |
| IN- | ← J1 GND | ⚫ Black |
| B+ | → BT1 (+) | 🔴 Red |
| B- | → BT1 (-) | ⚫ Black |
| OUT+ | → Not connected (charge only) | — |
| OUT- | → Not connected | — |

### BT1 — LiPo Battery (3.7V)
|| Pad | Connects To | Wire |
||-----|-------------|------|
|| + | ← U7 B+ | 🔴 Red |
|| - | ← U7 B- | ⚫ Black |

### F1 — PPTC_900mA Resettable Fuse
|| Pad | Connects To | Wire |
||-----|-------------|------|
|| IN | ← BT1 (+) | 🔴 Red |
|| OUT | → SW1 COM | 🔴 Red |
**Notes:** 900mA hold / ~1.8A trip. Must be placed **before** the switch so the switch does not bypass overcurrent protection. See `cad/connections_4imu.csv:35-37`.

### SW1 — SW_3A Slide Switch (SS22D07)
|| Pad | Connects To | Wire |
||-----|-------------|------|
|| COM | ← F1 OUT | 🔴 Red |
|| NO | → U8 MT3608 IN+ | 🔴 Red |
|| NC | → Not connected | — |
**Notes:** 3A SPDT slide switch; COM is center pin. Switch placed after PPTC fuse. See `cad/connections_4imu.csv:37-38`.

### U8 — MT3608 Boost Converter (5V)
| Pin | Connects To | Wire |
|-----|-------------|------|
| IN+ | ← BT1 (+) | 🔴 Red |
| IN- | ← BT1 (-) (GND bus) | ⚫ Black |
| OUT+ | → U1 VIN (5V) | 🔴 Red |
| OUT- | → GND bus | ⚫ Black |

### U1 — ESP32-S3-Kaluga-1
| Pin | Connects To | Wire |
|-----|-------------|------|
|| VIN | ← U8 OUT+ (5V) | 🔴 Red |
|| 3.3V | ← Onboard AMS1117-3.3 | (internal) |
|| GND | → GND bus | ⚫ Black |
|| GPIO21 | → U2 SDA | 🟢 Green |
|| GPIO22 | → U2 SCL | 🔵 Blue |
|| GPIO2 | → D1 anode (via 220Ω) | 🟡 Yellow |
|| 25/18/19/20 | NC (deferred) | — |

**⚠️ GPIO2 boot warning:** GPIO2 is an ESP32 strapping pin (MTDI). The 220Ω LED to GND could hold it LOW at boot, forcing UART download mode. Empirically verify boot behavior: if the ESP32 fails to boot with the LED connected, add a buffer transistor or move the LED to a non-strapping pin (e.g., GPIO4, GPIO5). See ESP32 Technical Reference Manual §3.4 Strapping Pins.

### U2 — TCA9548A (I²C multiplexer @0x70)
| Pin | Connects To | Wire |
|-----|-------------|------|
| SDA | ← ESP32 GPIO21 | 🟢 Green |
| SCL | ← ESP32 GPIO22 | 🔵 Blue |
| VCC | ← ESP32 3.3V pin | 🔴 Red |
| GND | → GND bus | ⚫ Black |
| SD0/SC0 | → U3 SDA/SCL | 🟢🟢 / 🔵🔵 |
| SD1/SC1 | → U4 SDA/SCL | 🟢🟢 / 🔵🔵 |
| SD2/SC2 | → U5 SDA/SCL | 🟢🟢 / 🔵🔵 |
| SD3/SC3 | → U6 SDA/SCL | 🟢🟢 / 🔵🔵 |

### U3 — GY-521 CH0 (dorsal wrist)
| Pin | Connects To | Wire |
|-----|-------------|------|
| SDA | ← U2 SD0 | 🟢 Green |
| SCL | ← U2 SC0 | 🔵 Blue |
| VCC | ← ESP32 3.3V pin | 🔴 Red |
| GND | → GND bus | ⚫ Black |

### U4 — GY-521 CH1 (thenar volar)
| Pin | Connects To | Wire |
|-----|-------------|------|
| SDA | ← U2 SD1 | 🟢 Green |
| SCL | ← U2 SC1 | 🔵 Blue |
| VCC | ← ESP32 3.3V pin | 🔴 Red |
| GND | → GND bus | ⚫ Black |

### U5 — GY-521 CH2 (thumb phalanx)
| Pin | Connects To | Wire |
|-----|-------------|------|
| SDA | ← U2 SD2 | 🟢 Green |
| SCL | ← U2 SC2 | 🔵 Blue |
| VCC | ← ESP32 3.3V pin | 🔴 Red |
| GND | → GND bus | ⚫ Black |

### U6 — GY-521 CH3 (index phalanx)
| Pin | Connects To | Wire |
|-----|-------------|------|
| SDA | ← U2 SD3 | 🟢 Green |
| SCL | ← U2 SC3 | 🔵 Blue |
| VCC | ← ESP32 3.3V pin | 🔴 Red |
| GND | → GND bus | ⚫ Black |

### D1 — LED Indicator
| Pin | Connects To | Wire |
|-----|-------------|------|
| Anode | ← ESP32 GPIO2 (via 220Ω) | 🟡 Yellow |
| Cathode | → GND bus | ⚫ Black |

---

## 3.3V Rail (red wire from ESP32 3.3V pin powers ALL of these)
| Component | Pin | Wire |
|-----------|-----|------|
| U2 TCA9548A | VCC | 🔴 Red |
| U3 GY-521 CH0 | VCC | 🔴 Red |
| U4 GY-521 CH1 | VCC | 🔴 Red |
| U5 GY-521 CH2 | VCC | 🔴 Red |
| U6 GY-521 CH3 | VCC | 🔴 Red |

---

## GND Rail (black wire — ALL GND connect here)
| Component | Pin |
|-----------|-----|
|| U7 TP4056 | IN-, B- |
|| U8 MT3608 | IN-, OUT- |
|| F1 PPTC_900mA | IN, OUT |
|| SW1 SW_3A | COM, NO |
|| U1 ESP32 | GND |
| U2 TCA9548A | GND |
| U3 GY-521 CH0 | GND |
| U4 GY-521 CH1 | GND |
| U5 GY-521 CH2 | GND |
| U6 GY-521 CH3 | GND |
| D1 LED | Cathode |

---

## I²C Address Map
| Component | Address | How Selected |
|-----------|---------|--------------|
| TCA9548A (U2) | 0x70 | A0/A1/A2→GND |
| GY-521 CH0 (U3) | 0x68 | AD0→GND |
| GY-521 CH1 (U4) | 0x68 | AD0→GND |
| GY-521 CH2 (U5) | 0x68 | AD0→GND |
| GY-521 CH3 (U6) | 0x68 | AD0→GND |

---

## Bill of Materials (BOM)
| Ref | Part | Package | Qty | Notes |
|-----|------|---------|-----|-------|
| U1 | ESP32-S3-Kaluga-1 | Module | 1 | Power via VIN (5V from MT3608 boost) |
| U2 | TCA9548A Breakout | TSSOP-24 | 1 | @0x70, A0/A1/A2→GND, EN→3.3V |
| U3-U6 | GY-521 (MPU6050) | QFN-24 | 4 | @0x68, AD0→GND, 0.1µF each |
|| U7 | TP4056 Module | Module | 1 | 1A charger, DW01 protection, B+/B- |
|| U8 | MT3608 | Module | 1 | Boost converter 3.7V→5V |
|| F1 | PPTC_900mA | PPTC | 1 | Resettable fuse, 900mA hold / ~1.8A trip |
|| SW1 | SW_3A (SS22D07) | Switch | 1 | 3A SPDT slide switch, COM→NO |
|| BT1 | LiPo Battery | Pouch | 1 | 3.7V, 500mAh+, JST-PH 2.0 |
| J1 | Micro-USB Connector | Module | 1 | Charging input |
| C1, C2 | Ceramic Capacitor | 0805 | 2 | 10µF, X5R/X7R (boost input/output) |
| D1 | LED (Blue) | 5mm | 1 | Power indicator |
| R1 | Resistor | 0805 | 1 | 220Ω (LED current limit) |
| R2, R3 | Resistor | 0805 | 2 | 4.7kΩ (I²C pull-ups, if needed) |

---

## Power Chain (signal flow)
```
USB 5V ──→ TP4056 IN+/IN- ──→ (charges) ──→ B+/B- ──→ LiPo 3.7V
                                      │
                                      ↓
                              PPTC_900mA IN
                                      │
                              PPTC_900mA OUT
                                      │
                                      ↓
                              SW_3A COM (slide switch)
                                      │
                              SW_3A NO
                                      │
                                      ↓
                              MT3608 IN+/IN-
                                      │
                                      ↓
                              MT3608 OUT+/OUT- (5V)
                                      │
                                      ↓
                              5V ──→ ESP32 VIN pin
                                      │
                              (onboard AMS1117-3.3)
                                      │
                                      ↓
                              3.3V Rail ──→ TCA9548A + 4× GY-521
```

---

## Build Order (recommended)
1. **Power section first:** J1 → U7 → BT1 → U8
2. **Verify 5V output** from MT3608 before connecting ESP32
3. **Connect ESP32 VIN pin** — verify 3.3V rail = 3.26-3.34V
4. **MCU section:** U1 ESP32 → U2 TCA9548A → D1 LED
5. **Sensor section:** U3 → U4 → U5 → U6 (one at a time)
6. **I²C bus:** Connect SDA/SCL last (after power verified)

---

## Verification Checklist
- [ ] PPTC fuse (F1) in place before slide switch (SW1) — LiPo+ → F1 IN, F1 OUT → SW1 COM
- [ ] Slide switch (SW1) NO → MT3608 IN+, NC unconnected
- [ ] 5V from MT3608 = 4.9-5.1V under load (multimeter)
- [ ] 3.3V from onboard AMS1117 = 3.26-3.34V
- [ ] No shorts between 5V and GND
- [ ] No shorts between 3.3V and GND
|| I²C wires <15cm length |
|| I²C pull-ups on SDA/SCL present — omit external R2/R3 if any breakout board already has 4.7kΩ installed |
|| 4.7kΩ pull-ups on SDA/SCL (if not on breakout) |
- [ ] 0.1µF decoupling cap per IC (close to pins)
- [ ] I²C scan detects 0x70 (TCA9548A)
- [ ] Each IMU channel responds at 0x68 when selected
- [ ] LED lights when GPIO2 goes high
- [ ] All GND connected to common bus (star topology)
