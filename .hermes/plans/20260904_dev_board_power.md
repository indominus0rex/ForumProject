# Plan: ESP32 Dev Board (38-pin) Power — TP4056 + MT3608 to VIN

**Goal:** Design power system for ESP32-DevKitC (38-pin dev board): TP4056 charges 1S LiPo, MT3608 boosts to 5V, connects to dev board's VIN pin.

## Current Context / Assumptions

- **ESP32-DevKitC 38-pin** (not bare WROOM) — has onboard AMS1117-3.3 LDO, VIN pin accepts 5V
- **1S LiPo** — 3.7V nominal, 4.2V full, 3.0V empty
- **TP4056 module** — charges 1S LiPo from USB 5V
- **MT3608 boost module** — boosts battery voltage to 5V
- **No external LDO needed** — dev board's onboard AMS1117-3.3 handles 5V→3.3V
- MCU/SENSORS wiring (ESP32 + TCA9548A + 4× GY-521) stays the same

## Architecture / Proposed Approach

```
USB 5V → TP4056 → 1S LiPo → MT3608 boost → 5V → ESP32 dev board VIN pin → onboard 3.3V → ESP32 + peripherals
```

The MT3608 boost takes the LiPo voltage (3.0-4.2V) and boosts it to 5V. The dev board's onboard LDO then drops it to 3.3V. No additional regulators, no bare module worries.

## Step-by-Step Tasks

### Task 1: Create excalidraw file skeleton
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Create with:
- Title: "4-IMU ESP32 Tremor Monitor — TP4056 + MT3608 to Dev Board"
- Subtitle: "ESP32-DevKitC 38-pin · TCA9548A · 4× GY-521 · 1S LiPo · MT3608 Boost 5V"

### Task 2: Add POWER zone components
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Add rectangles:
- `J1` — Micro-USB connector, labeled "J1 USB 5V"
- `U7` — TP4056 module (with DW01A protection), labeled "U7 TP4056 Charger"
- `R_prog` — 1.2kΩ, labeled "1.2kΩ ~1A charge"
- `BT1` — 1S LiPo 3.7V, labeled "BT1 LiPo 3.7V 500mAh+"
- `U8` — MT3608 boost, labeled "U8 MT3608 Boost → 5V"
- `C1` — 10µF input cap on MT3608
- `C2` — 10µF output cap on MT3608

### Task 3: Draw charging + boost path
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

1. J1 5V → U7 IN+ (red)
2. J1 GND → U7 IN- (black)
3. U7 B+ → BT1+ (red)
4. U7 B- → BT1- (black)
5. U7 PROG → R_prog → GND (black)
6. U7 OUT+ → U8 IN+ (red, bold) — battery power to boost
7. U8 OUT+ → 5V rail (red, bold) → ESP32 VIN pin
8. U8 GND → GND rail (black)

### Task 4: Add filter caps
1. C1 across U8 IN+ and GND
2. C2 across U8 OUT+ and GND

### Task 5: Add MCU zone
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

- `U1` — ESP32-DevKitC 38-pin, labeled with: VIN (5V), 3.3V, GND, GPIO21/SDA, GPIO22/SCL, GPIO2/LED
- `U2` — TCA9548A @0x70
- `D1` — LED + 220Ω to GND
- `R_sda` — 4.7kΩ SDA pullup to 3.3V
- `R_scl` — 4.7kΩ SCL pullup to 3.3V

### Task 6: Draw MCU wiring
1. 5V rail → U1 VIN (red, bold)
2. U1 3.3V → U2 VCC (red) — dev board's regulated 3.3V powers mux
3. I2C: U1 GPIO21 → U2 SDA, U1 GPIO22 → U2 SCL
4. Pullups: SDA/SCL → 4.7kΩ → 3.3V
5. LED: U1 GPIO2 → D1 → 220Ω → GND

### Task 7: Add SENSORS zone
- U3-U6 GY-521 IMUs on CH0-CH3
- 3.3V from dev board 3.3V pin → each IMU VCC
- GND common to all

### Task 8: Add notes
- "MT3608 output set to 5V — connects to ESP32 VIN pin"
- "ESP32 dev board onboard AMS1117-3.3 regulates 5V→3.3V"
- "TP4056 charges battery AND powers load simultaneously"

### Task 9: Export and validate
- Export PNG to `docs/images/tremor_monitor_schematic_v3.png`
- Validate JSON

## Tests / Validation

- JSON valid
- Nets: USB_5V, V_BAT, RAIL_5V, RAIL_3V3, GND, I2C_SDA, I2C_SCL all wired
- Confirm TP4056 IS in schematic
- Confirm MT3608 IS in schematic
- Confirm NO external AMS1117 or AP2112K (dev board has it onboard)

## Risks, Tradeoffs

- **MT3608 output must be 5V exactly** — too high damages dev board's LDO (max ~15V but 5V is the target). Too low (<4.3V) and AMS1117 drops out.
- **AMS1117 dropout** — input must be ≥4.3V for clean 3.3V output
- **TP4056 module type** — must be the protected version (with DW01A and OUT+ pads)
