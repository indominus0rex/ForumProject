# Plan: Complete Power System with TP4056 Charging for 1S LiPo + Bare WROOM

**Goal:** Design a complete power system: USB 5V → TP4056 → 1S LiPo → MT3608 boost (5V) → AMS1117-3.3 LDO → bare ESP32-WROOM-32, with charging and power-path management.

## Current Context / Assumptions

- **Bare ESP32-WROOM-32** — 3.3V on VCC pin
- **1S LiPo** — 3.7V nominal, 4.2V full, 3.0V empty
- **TP4056 module with DW01A protection** — charges battery, provides power-path (OUT+ powers load from USB or battery)
- **MT3608 boost** — boosts battery voltage (3.0-4.2V) to 5V
- **AMS1117-3.3 LDO** — steps 5V down to 3.3V for ESP32
- **R_PROG = 1.2kΩ** on TP4056 → ~1A charge current (change to 10kΩ for ~130mA if charging small 100-500mAh cell)
- **TP4056 module pinout:** IN+ (USB 5V), IN- (GND), B+ (battery+), B- (battery-), OUT+ (load power), OUT- (load GND)

## Architecture / Proposed Approach

The complete power chain:
```
USB 5V → TP4056 IN+ → (DW01A protection) → B+/B- → 1S LiPo
                              ↓
                         OUT+ (3.0-4.2V) → MT3608 IN+ → OUT+ (5V) → AMS1117-3.3 IN → OUT (3.3V) → ESP32 VCC
```

When USB connected: TP4056 charges battery AND powers the load from IN+ through the protection circuit.
When USB removed: Battery powers load through DW01A → MT3608 → AMS1117 → ESP32.

## Step-by-Step Tasks

### Task 1: Create excalidraw file skeleton
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Create with:
- Title: "4-IMU ESP32 Tremor Monitor — TP4056 + Boost + LDO"
- Subtitle: "Bare ESP32-WROOM-32 · TP4056 Charger · MT3608 · AMS1117-3.3 · 4× GY-521"

### Task 2: Add POWER zone components
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Add rectangles with labels:
- `J1` — Micro-USB connector, labeled "J1 Micro-USB 5V"
- `U7` — TP4056 module, labeled "U7 TP4056 LiPo Charger\nw/ DW01A Protection"
- `R_prog` — 1.2kΩ resistor, labeled "R_prog 1.2kΩ\n~1A charge"
- `BT1` — 1S LiPo 3.7V, labeled "BT1 LiPo 3.7V 500mAh+"
- `U8` — MT3608 boost, labeled "U8 MT3608 Boost\n→ 5V"
- `U9` — AMS1117-3.3 LDO, labeled "U9 AMS1117-3.3\n→ 3.3V"
- `C1` — 10µF on MT3608 input
- `C2` — 10µF on MT3608 output
- `C3` — 10µF on AMS1117 input
- `C4` — 10µF on AMS1117 output

### Task 3: Draw charging path (POWER zone)
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

1. J1 5V → U7 IN+ (red)
2. J1 GND → U7 IN- (black)
3. U7 B+ → BT1+ (red)
4. U7 B- → BT1- (black)
5. U7 PROG → R_prog → GND (black)

### Task 4: Draw power delivery path (POWER zone)
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

1. U7 OUT+ → U8 IN+ (red, bold) — battery power to boost
2. U8 OUT+ → U9 IN (red, bold) — 5V to LDO
3. U9 OUT → 3.3V rail (red, bold) — 3.3V to ESP32
4. GND common rail (black) — U7 OUT-, U8 GND, U9 GND, C1-C4 negatives

### Task 5: Add filter caps
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

1. C1 across U8 IN+ and GND
2. C2 across U8 OUT+ and GND
3. C3 across U9 IN and GND
4. C4 across U9 OUT and GND

### Task 6: Add MCU and SENSORS zones
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

MCU: U1 ESP32-WROOM-32, U2 TCA9548A, D1 LED + 220Ω, R_sda 4.7kΩ, R_scl 4.7kΩ
SENSORS: U3-U6 GY-521 IMUs on CH0-CH3

### Task 7: Draw MCU/SENSORS wiring
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Same as v2: 3.3V rail → ESP32 VCC → TCA VCC; I2C pullups; LED on GPIO2; 4 IMUs on mux channels.

### Task 8: Add notes and legend
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

- "TP4056 charges battery AND powers load simultaneously (power path via DW01A)"
- "MT3608 set to 5V before connecting"
- "AMS1117-3.3 dropout ~1V. Input must be ≥4.3V."
- "R_PROG = 1.2kΩ → ~1A. Use 10kΩ for small cells (100-500mAh)."

### Task 9: Export and validate
1. Open in excalidraw.com
2. Export PNG to `docs/images/tremor_monitor_schematic_v3.png`
3. Validate JSON

## Tests / Validation

- JSON valid check
- Net checklist: USB_5V, V_BAT, RAIL_5V, RAIL_3V3, GND, I2C_SDA, I2C_SCL
- Confirm TP4056 IS in schematic (IN+, B+, B-, OUT+, OUT-, PROG)
- Confirm DW01A mentioned in label
- Confirm MT3608 IS in schematic
- Confirm AMS1117-3.3 IS in schematic

## Risks, Tradeoffs, and Open Questions

- **TP4056 module type:** Must use version WITH DW01A protection (OUT+ pads). Basic 4-pin module lacks power-path — load must connect directly to battery.
- **Heat in AMS1117:** (5V-3.3V) × I_load. At 300mA = 0.51W. Acceptable without heatsink for TO-252 package.
- **TP4056 charge current:** 1A default is fine for 500mAh+ cells. For smaller 100-200mAh cells, change R_PROG to 4.7kΩ (~200mA) or 10kΩ (~100mA).
- **USB-C option:** TP4056 module with USB-C connector is available and works identically. Micro-USB shown for cost/simplicity.
- **Battery protection:** DW01A in the module provides over-discharge cutoff at ~2.4V. ESP32 will lose power before LiPo is damaged.
- **Alternative charger:** MCP73831 is smaller (SOT-23-5, 500mA max) — better for very compact wearables with small LiPo cells. No power-path; load connects to battery directly.

## Research Sources

- TP4056 vs MCP73831 comparison: TP4056 wins for 1A charging + module availability; MCP73831 wins for compact custom PCBs
- TP4056 module pinout: IN+, IN-, B+, B-, OUT+, OUT-
- R_PROG formula: I_CHG = 1000 / R_PROG (kΩ) mA
- Power path: TP4056+DW01A allows simultaneous charge and discharge
- TP4056 alternatives for better efficiency: MCP73871 (load sharing), IP5306 (USB-C + boost), BQ24075 (power path)
