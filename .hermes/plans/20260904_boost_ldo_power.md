# Plan: 1S LiPo → Boost → LDO Power Supply for Bare WROOM

**Goal:** Replace the AP2112K LDO with a 1S LiPo → MT3608 boost (5V) → AMS1117-3.3 LDO (3.3V) power chain for bare ESP32-WROOM-32.

## Current Context / Assumptions

- **Bare ESP32-WROOM-32** (not DevKitC) — takes 3.3V on VCC pin, no 5V tolerance
- **1S LiPo** — 3.7V nominal, 4.2V fully charged, ~3.0V end-of-discharge
- **MT3608 boost module** — boosts 1S LiPo to 5V (already in project inventory per earlier plans)
- **AMS1117-3.3 LDO** — steps 5V down to 3.3V for ESP32 VCC
- **AP2112K removed** — replaced by AMS1117-3.3 (different LDO, same function)
- **TP4056 removed** — no longer needed in schematic (bench charging only, or user charges battery separately)
- **Why both boost and LDO?** A boost converter cannot output 3.3V when input is already 4.2V (boost only increases voltage). So you boost to 5V first, then LDO down to 3.3V.
- **Deliverable:** New schematic file (excalidraw + PNG)
- **File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`
- **MCU/SENSORS zones unchanged** — ESP32 + TCA9548A + 4× GY-521 wiring stays the same

## Architecture / Proposed Approach

The POWER zone becomes: 1S LiPo → MT3608 boost to 5V → AMS1117-3.3 LDO to 3.3V → ESP32 VCC. Input/output caps on both converters. No TP4056, no AP2112K, no 2S battery.

## Step-by-Step Tasks

### Task 1: Create excalidraw file skeleton
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Create a valid excalidraw JSON with:
- Three colored background zones: POWER (#fff3bf yellow), MCU (#e7f5ff blue), SENSORS (#ebfbee green)
- Title: "4-IMU ESP32 Tremor Monitor — Boost + LDO Power"
- Subtitle: "Bare ESP32-WROOM-32 · TCA9548A @0x70 · 4× GY-521 · MT3608 Boost · AMS1117-3.3 · I2C0 @400kHz"

### Task 2: Add POWER zone components
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Add the following components (rectangles with labels):
- `BT1` — 1S LiPo battery 3.7V 500mAh+ (JST-PH 2-pin), labeled "BT1 LiPo 3.7V 500mAh"
- `U8` — MT3608 boost converter module, labeled "U8 MT3608 Boost\n2-24V IN → 5V OUT"
- `U9` — AMS1117-3.3 LDO module, labeled "U9 AMS1117-3.3\n5V IN → 3.3V OUT"
- `C1` — 10µF input cap on MT3608, labeled "C1 10µF"
- `C2` — 10µF output cap on MT3608, labeled "C2 10µF"
- `C3` — 10µF input cap on AMS1117, labeled "C3 10µF"
- `C4` — 10µF output cap on AMS1117, labeled "C4 10µF"

### Task 3: Draw POWER zone wiring
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Draw arrows:
1. **Battery positive (red):** BT1+ → U8 IN+ (MT3608 input +)
2. **Battery negative (black):** BT1- → U8 IN- → GND rail
3. **Boost output (red, bold):** U8 OUT+ (5V) → U9 IN (AMS1117 input)
4. **Boost GND (black):** U8 OUT- → GND rail
5. **LDO output (red, bold):** U9 OUT (3.3V) → 3.3V rail → ESP32 VCC
6. **LDO GND (black):** U9 GND → GND rail
7. **Input cap C1:** across U8 IN+ and IN-
8. **Output cap C2:** across U8 OUT+ and OUT-
9. **Input cap C3:** across U9 IN and GND
10. **Output cap C4:** across U9 OUT and GND
11. **3.3V rail to MCU (red, bold):** 3.3V rail → U1 (ESP32 VCC)

### Task 4: Add MCU zone components
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Add (same as v2):
- `U1` — ESP32-WROOM-32 (large rectangle), labeled with pins: VCC ← 3.3V, GND, GPIO21/SDA, GPIO22/SCL, GPIO2/LED
- `U2` — TCA9548A @0x70 multiplexer
- `D1` — LED on GPIO2 with 220Ω resistor to GND
- `R_sda` — 4.7kΩ pullup on SDA to 3.3V
- `R_scl` — 4.7kΩ pullup on SCL to 3.3V

### Task 5: Draw MCU zone wiring
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Draw arrows:
1. **3.3V power (red, bold):** 3.3V rail → U1 VCC → U2 VCC
2. **I2C bus (blue):** U1 GPIO21 → U2 SDA, U1 GPIO22 → U2 SCL
3. **Pullups (blue, dashed):** SDA → 4.7kΩ → 3.3V, SCL → 4.7kΩ → 3.3V
4. **LED signal (orange):** U1 GPIO2 → D1 anode → 220Ω → GND

### Task 6: Add SENSORS zone components
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Add (same as v2):
- `U3` — GY-521 CH0 @0x68 Dorsal Wrist
- `U4` — GY-521 CH1 @0x68 Thenar Volar
- `U5` — GY-521 CH2 @0x68 Thumb Phalanx 20°
- `U6` — GY-521 CH3 @0x68 Index Phalanx

### Task 7: Draw SENSORS zone wiring
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Draw arrows:
1. **CH0-CH3 (blue):** U2 SD0/SC0 → U3, SD1/SC1 → U4, SD2/SC2 → U5, SD3/SC3 → U6
2. **3.3V power (red):** 3.3V rail → each IMU VCC
3. **GND (black):** Star GND → each IMU GND
4. **AD0 note:** All IMUs AD0 → GND

### Task 8: Add legend and notes
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Add text blocks:
- **Legend:** Red = Power, Blue = I2C Bus, Orange = GPIO, Black = GND
- **Operating Parameters:** VCC 3.3V · I2C 400kHz · 100Hz · 128-sample window
- **Boost note:** "MT3608 set to 5V output before connecting AMS1117"
- **LDO note:** "AMS1117-3.3 dropout ~1V. Input must be ≥4.3V for clean 3.3V output."
- **Charging note:** "Bench charge LiPo with TP4056 or similar 1S charger — not shown"

### Task 9: Export and validate
1. Open `tremor_monitor_schematic_v3.excalidraw` in excalidraw.com
2. Export PNG to `docs/images/tremor_monitor_schematic_v3.png`
3. Run `python -c "import json; json.load(open(r'docs/images/tremor_monitor_schematic_v3.excalidraw', encoding='utf-8')); print('JSON valid')"`
4. Expected output: `JSON valid`

## Tests / Validation

- **JSON validity:** `python -c "import json; json.load(open(r'docs/images/tremor_monitor_schematic_v3.excalidraw', encoding='utf-8'))"` → must print "JSON valid"
- **Net checklist:** Verify these nets are present and correctly wired:
  - V_BAT (BT1+ to U8 IN+)
  - RAIL_5V (U8 OUT+ → U9 IN)
  - RAIL_3V3 (U9 OUT → ESP32 VCC → TCA + IMUs)
  - GND (star ground common to all)
  - I2C_SDA (ESP32 → TCA → 4 IMUs)
  - I2C_SCL (ESP32 → TCA → 4 IMUs)
  - LED_GPIO2 (ESP32 → LED)
- **Error check:** Confirm AP2112K is NOT in the schematic
- **Error check:** Confirm TP4056 is NOT in the schematic
- **Error check:** Confirm MT3608 IS in the schematic as boost to 5V
- **Error check:** Confirm AMS1117-3.3 IS in the schematic as 5V→3.3V LDO
- **Voltage check:** MT3608 input range (2-24V) covers 1S LiPo range (3.0-4.2V) ✓
- **Voltage check:** AMS1117-3.3 input (5V) is above minimum (4.3V for 1V dropout) ✓

## Risks, Tradeoffs, and Open Questions

- **Why not boost directly to 3.3V?** MT3608 is boost-only. When LiPo is at 4.2V, a boost converter cannot output 3.3V (it can only increase voltage). You'd need a buck-boost converter (e.g., TPS63020) to do that.
- **Two-stage conversion inefficiency:** Boost (90% efficient) + LDO (66% efficient at 5V→3.3V) = ~60% overall. Not ideal for battery life.
- **AMS1117 dropout:** AMS1117-3.3 needs ~1V dropout. If MT3608 output sags below 4.3V under load, the LDO drops out. Consider XC6206 (0.2V dropout) instead.
- **No TP4056 in schematic:** User must charge battery separately. If they want charging in-schematic, add TP4056 between USB and BT1.
- **MT3608 module output:** Must be trimmed to exactly 5V before connecting. Overvoltage on AMS1117 input is fine (max 15V), but output must be clean.
