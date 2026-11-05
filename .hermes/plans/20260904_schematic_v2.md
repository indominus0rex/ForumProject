# Plan: Generate Corrected Tremor Monitor Schematic (Bare WROOM)

**Goal:** Create a new, fully-corrected schematic for the 4-IMU ESP32 tremor monitor using a bare ESP32-WROOM-32 module, fixing the wiring errors in the prior "New Project 2026-09-03 15-25" Scheme-it export.

## Current Context / Assumptions

- **Bare ESP32-WROOM-32 module** (not DevKitC) — takes 3.3V directly on 3V3 pin, no onboard LDO
- The prior schematic (`images/Scheme-it-export-New-Project-2026-09-03-15-25-2026-09-04-18-52.png`) had critical errors:
  1. AP2112K-3.3 drawn as 6-pin with wrong pin labels, GND pin unconnected
  2. TP4056 with no USB 5V input
  3. TP4056 used as power-path (can't pass battery voltage to output — it's a charger-only IC)
  4. No PROG resistor on TP4056
- **AP2112K-3.3 is the correct regulator** for bare WROOM: LiPo 3.0-4.2V → 3.3V LDO → ESP32 3V3 pin
- TP4056 remains **bench charger only** — not in the power delivery path during operation
- Project uses excalidraw for schematics (existing: `docs/images/system_architecture.excalidraw`, `docs/images/system_architecture_schematic.excalidraw`, `images/circuit_multiplexer.excalidraw`)

## Architecture / Proposed Approach

Generate a new `.excalidraw` file at `docs/images/tremor_monitor_schematic_v2.excalidraw` showing the complete, correct power delivery path and signal bus. The schematic will have three zones (POWER, MCU, SENSORS) matching the existing project convention. Power path: USB 5V → TP4056 → LiPo (charge only); LiPo → AP2112K-3.3 → 3.3V → ESP32 3V3 pin → TCA9548A + 4× GY-521. Signal path: ESP32 GPIO21/SDA + GPIO22/SCL → TCA9548A @0x70 → CH0-3 → 4× GY-521 @0x68. LED on GPIO2.

## Step-by-Step Tasks

### Task 1: Create excalidraw file skeleton
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Create a valid excalidraw JSON with:
- Three colored background zones: POWER (#fff3bf yellow), MCU (#e7f5ff blue), SENSORS (#ebfbee green)
- Title: "4-IMU ESP32 Tremor Monitor — Corrected Schematic (Bare WROOM)"
- Subtitle: "ESP32-WROOM-32 · TCA9548A · 4× GY-521 · AP2112K-3.3 LDO · TP4056 Charger · LiPo Power"

### Task 2: Add POWER zone components
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Add the following components (rectangles with labels):
- `J1` — Micro-USB connector (5V input for charging)
- `U7` — TP4056 LiPo Charger module (with DW01 protection)
- `R_prog` — 1.2kΩ resistor from PROG pin to GND (sets ~1A charge current; use 10K for ~130mA if desired)
- `BT1` — LiPo 3.7V 500mAh+ (JST connector)
- `U9` — AP2112K-3.3 LDO (3-pin SOT-23: pin 1=VIN, pin 2=GND, pin 3=VOUT)
- `C1` — 10µF input cap on AP2112K VIN
- `C2` — 10µF output cap on AP2112K VOUT

### Task 3: Draw POWER zone wiring (arrows)
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Draw arrows for:
1. **Charging path (red, solid):** J1 pin 5V → U7 (TP4056) VCC pin
2. **Charging path (black, solid):** J1 GND → U7 GND
3. **Battery charge (red, solid):** U7 BAT+ → BT1 positive (JST red wire)
4. **Battery charge (black, solid):** U7 BAT- → BT1 negative (JST black wire)
5. **PROG resistor (black, solid):** U7 PROG → R_prog → GND
6. **Discharge path (red, solid):** BT1+ → U9 (AP2112K) VIN (pin 1)
7. **LDO output (red, solid):** U9 VOUT (pin 3) → 3.3V rail → ESP32 3V3 pin
8. **LDO GND (black, solid):** U9 GND (pin 2) → star GND rail
9. **GND common (black, solid):** All GNDs (J1, U7, BT1-, U9, C1, C2) connected to star GND rail
10. **Input cap (red/black):** C1 across U9 VIN/GND
11. **Output cap (red/black):** C2 across U9 VOUT/GND

**Key note:** TP4056 does NOT connect to the load. Battery+ goes directly to AP2112K VIN. This is the critical fix.

### Task 4: Add MCU zone components
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Add:
- `U1` — ESP32-WROOM-32 (rectangle, label with key pins: 3V3, GND, GPIO21/SDA, GPIO22/SCL, GPIO2/LED, EN)
- `U2` — TCA9548A @0x70 multiplexer (rectangle, label SDA/SCL input, CH0-CH3 outputs)
- `D1` — LED on GPIO2 (with 220Ω resistor to GND)

### Task 5: Draw MCU zone wiring
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Draw arrows:
1. **3.3V power (red, bold):** U9 VOUT → U1 3V3 pin → U2 VCC (3.3V)
2. **I2C bus (blue):** U1 GPIO21 → U2 SDA, U1 GPIO22 → U2 SCL
3. **Pull-ups (blue, dashed):** SDA → 4.7kΩ → 3.3V, SCL → 4.7kΩ → 3.3V
4. **LED signal (orange):** U1 GPIO2 → D1 anode → 220Ω → GND

### Task 6: Add SENSORS zone components
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Add four GY-521 breakout boards:
- `U3` — CH0 @0x68 Dorsal Wrist
- `U4` — CH1 @0x68 Thenar Volar
- `U5` — CH2 @0x68 Thumb Phalanx 20°
- `U6` — CH3 @0x68 Index Phalanx

Each labeled with: GY-521, channel, location, I2C address, VCC (3.3V), GND, SDA, SCL.

### Task 7: Draw SENSORS zone wiring
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Draw arrows:
1. **CH0 (blue):** U2 SD0/SC0 → U3 SDA/SCL
2. **CH1 (blue):** U2 SD1/SC1 → U4 SDA/SCL
3. **CH2 (blue):** U2 SD2/SC2 → U5 SDA/SCL
4. **CH3 (blue):** U2 SD3/SC3 → U6 SDA/SCL
5. **3.3V power (red):** 3.3V rail → each IMU VCC pin
6. **GND (black):** Star GND → each IMU GND pin
7. **AD0 note (text):** All IMUs AD0 → GND (address 0x68)

### Task 8: Add decoupling capacitors
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Add 0.1µF caps near each IC:
- C3 near U1 (ESP32)
- C4 near U2 (TCA9548A)
- C5-C8 near U3-U6 (GY-521s)
Each connected between VCC and GND.

### Task 9: Add legend and notes
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Add text blocks:
- **Legend:** Red = Power, Blue = I2C Bus, Orange = GPIO, Black = GND
- **Operating Parameters:** VCC 3.3V, I2C 400kHz, Sampling 100Hz, 128-sample window
- **TCA config:** A0-A2 → GND, EN → 3.3V
- **IMU config:** AD0 → GND (all @0x68 via mux)
- **Wire length:** <15cm
- **Decoupling:** 0.1µF per IC + 10µF bulk
- **AP2112K pinout note:** SOT-23 pin 1=VIN, pin 2=GND, pin 3=VOUT

### Task 10: Export and verify
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

1. Open file in Excalidraw (excalidraw.com or desktop app)
2. Export as PNG to `docs/images/tremor_monitor_schematic_v2.png`
3. Visually verify all connections match the task list above
4. Specifically verify: TP4056 does NOT connect to load path; battery+ goes directly to AP2112K VIN; AP2112K GND is connected; AP2112K is 3-pin not 6-pin

## Tests / Validation

- **Visual inspection:** All arrows connect source→destination without crossing ambiguously
- **Net checklist:** Verify the following nets are present and correctly wired:
  - USB_5V (J1 pin 1)
  - V_BAT (BT1+ to AP2112K VIN)
  - RAIL_3V3 (AP2112K VOUT → ESP32 3V3 → TCA + IMUs)
  - RAIL_GND (star ground common to all)
  - I2C_SDA (ESP32 → TCA → 4 IMUs)
  - I2C_SCL (ESP32 → TCA → 4 IMUs)
  - LED_GPIO2 (ESP32 → LED)
- **Error check:** Confirm AP2112K is 3-pin (VIN, GND, VOUT) with GND connected
- **Error check:** Confirm TP4056 does NOT connect to AP2112K input (charger only)
- **Error check:** Confirm MT3608 is NOT in the schematic (wrong for bare WROOM)

## Risks, Tradeoffs, and Open Questions

- **Excalidraw complexity:** Drawing detailed wiring in excalidraw JSON by hand is tedious. Consider using the Excalidraw CLI or generating via script if the JSON structure is error-prone.
- **TP4056 module vs discrete IC:** The schematic shows a TP4056 module (which includes DW01 protection). If the user has a bare TP4056 IC, the circuit needs external protection (DW01 + FS8205). Clarify if needed.
- **AP2112K headroom:** AP2112K is a low-dropout regulator (~0.3V dropout at 600mA). With a fully charged LiPo (4.2V), headroom is fine. At end-of-discharge (~3.3V), the LDO may drop out. Consider if this is acceptable or if a lower-dropout alternative (e.g., XC6206 with ~0.2V dropout) is preferred.
- **No power switch in discharge path:** The current design has no switch between battery and LDO. The TP4056 module's protection (DW01) handles over-discharge. If a physical on/off switch is desired, it should be placed between BT1+ and U9 VIN.
