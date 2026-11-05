# Plan: 1S LiPo → MT3608 Boost + LDO for Bare ESP32-WROOM-32

**Goal:** Replace AP2112K with a MT3608 boost converter + AMS1117-3.3 LDO for powering bare ESP32-WROOM-32 from a single 1S LiPo.

## Current Context / Assumptions

- **Bare ESP32-WROOM-32** — takes 3.3V on VCC pin, no 5V tolerance, max 3.6V
- **1S LiPo** — 3.7V nominal, 4.2V fully charged, ~3.0V end-of-discharge
- **MT3608 boost module** — already in project inventory per earlier plans
- **AMS1117-3.3 LDO** — common, cheap, 5V→3.3V, ~1V dropout voltage
- **TP4056 removed** — bench charging only (not shown in schematic)
- **AP2112K removed** — replaced by AMS1117-3.3 (different LDO, same function)
- **Why both boost and LDO?** MT3608 is boost-only. When LiPo is at 4.2V (fully charged), a boost converter **cannot** output 3.3V (boost only increases voltage). You must boost to 5V first, then LDO down to 3.3V.
- **Deliverable:** New schematic file (excalidraw + PNG)
- **File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

## Architecture / Proposed Approach

The POWER zone becomes: 1S LiPo → MT3608 boost to 5V → AMS1117-3.3 LDO to 3.3V → ESP32 VCC. Input/output caps on both converters. No TP4056, no AP2112K, no 2S battery.

**Efficiency note:** Boost (~90%) + LDO (~66% at 5V→3.3V) = ~60% overall. For better battery life, consider TPS63020 buck-boost IC (90%+, single stage) — see alternatives section below.

## Step-by-Step Tasks

### Task 1: Create excalidraw file skeleton
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Create a valid excalidraw JSON with:
- Three colored background zones: POWER (#fff3bf yellow), MCU (#e7f5ff blue), SENSORS (#ebfbee green)
- Title: "4-IMU ESP32 Tremor Monitor — Boost + LDO Power"
- Subtitle: "Bare ESP32-WROOM-32 · TCA9548A @0x70 · 4× GY-521 · MT3608 → AMS1117-3.3 · I2C0 @400kHz"

### Task 2: Add POWER zone components
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Add these rectangles with labels:
- `BT1` — LiPo 3.7V 500mAh+ (JST-PH 2-pin), labeled "BT1 LiPo 3.7V"
- `U8` — MT3608 boost module, labeled "U8 MT3608\nBoost 5V"
- `U9` — AMS1117-3.3 LDO, labeled "U9 AMS1117-3.3\nLDO 3.3V"
- `C1` — 10µF input cap on MT3608
- `C2` — 10µF output cap on MT3608
- `C3` — 10µF input cap on AMS1117
- `C4` — 10µF output cap on AMS1117

### Task 3: Draw POWER zone wiring
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Draw arrows:
1. **Battery positive (red):** BT1+ → U8 IN+
2. **Battery negative (black):** BT1- → U8 GND → GND rail
3. **Boost output (red, bold):** U8 OUT+ → U9 IN
4. **Boost GND (black):** U8 GND → GND rail
5. **LDO output (red, bold):** U9 OUT → 3.3V rail
6. **LDO GND (black):** U9 GND → GND rail
7. **Input cap C1:** U8 IN+ to U8 GND
8. **Output cap C2:** U8 OUT+ to U8 GND
9. **Input cap C3:** U9 IN to U9 GND
10. **Output cap C4:** U9 OUT to U9 GND
11. **3.3V rail to MCU:** U9 OUT → U1 (ESP32 VCC)

### Task 4: Add MCU zone components
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Add (same as v2):
- `U1` — ESP32-WROOM-32 with pins: VCC, GND, GPIO21/SDA, GPIO22/SCL, GPIO2/LED
- `U2` — TCA9548A @0x70
- `D1` — LED with 220Ω resistor
- `R_sda` — 4.7kΩ SDA pullup to 3.3V
- `R_scl` — 4.7kΩ SCL pullup to 3.3V

### Task 5: Draw MCU zone wiring
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Draw arrows:
1. **3.3V power:** U9 OUT → U1 VCC → U2 VCC
2. **I2C:** U1 GPIO21 → U2 SDA, U1 GPIO22 → U2 SCL
3. **Pullups:** SDA/SCL → 4.7kΩ → 3.3V
4. **LED:** U1 GPIO2 → D1 → 220Ω → GND

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
1. **I2C channels:** U2 CH0-CH3 → U3-U6 SDA/SCL
2. **3.3V power:** 3.3V rail → each IMU VCC
3. **GND:** Star GND → each IMU GND
4. **AD0 note:** All IMUs AD0 → GND

### Task 8: Add legend and notes
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Add text:
- Legend: Red=Power, Blue=I2C, Orange=GPIO, Black=GND
- Operating params: VCC 3.3V, I2C 400kHz, 100Hz, 128-sample window
- Warning: "MT3608 set to 5V before connecting AMS1117"
- Warning: "AMS1117-3.3 dropout ~1V. Input must be ≥4.3V."
- Note: "Bench charge LiPo with TP4056 — not shown"

### Task 9: Export and validate
1. Open `tremor_monitor_schematic_v3.excalidraw` in excalidraw.com
2. Export PNG to `docs/images/tremor_monitor_schematic_v3.png`
3. Run: `python -c "import json; json.load(open(r'docs/images/tremor_monitor_schematic_v3.excalidraw', encoding='utf-8')); print('JSON valid')"`

## Tests / Validation

- JSON valid: `python -c "import json; json.load(open(r'docs/images/tremor_monitor_schematic_v3.excalidraw', encoding='utf-8'))"` → "JSON valid"
- Net checklist: V_BAT, RAIL_5V, RAIL_3V3, GND, I2C_SDA, I2C_SCL, LED_GPIO2 all wired
- Error check: No AP2112K, no TP4056, no 2S battery
- Confirm MT3608 IS in schematic as boost to 5V
- Confirm AMS1117-3.3 IS in schematic as 5V→3.3V LDO

## Alternatives (for better battery life)

If efficiency matters, consider these single-chip solutions:

| IC | Type | Efficiency | Iout | Cost |
|----|------|-----------|------|------|
| **TPS63020** | Buck-boost | 90%+ | 2A | Higher |
| **TPS63031** | Buck-boost | 96% | 800mA | Higher |
| **TPS63802** | Buck-boost | 90%+ | 1A | Higher |
| **TPS63900** | Buck-boost | 90%+ | 400mA | Medium |

These can take 1S LiPo directly (3.0-4.2V) and output 3.3V in a single stage. No need for MT3608 + LDO.

## Risks, Tradeoffs, and Open Questions

- **Two-stage conversion inefficiency:** ~60% overall. LiPo capacity wasted as heat in LDO.
- **AMS1117 dropout:** Needs ≥4.3V input. If MT3608 output sags, LDO drops out.
- **Heat:** AMS1117 dissipates (5V - 3.3V) × I_load. At 300mA = 0.51W. May need small heatsink.
- **No TP4056 in schematic:** User must charge battery separately.
- **MT3608 module:** Must be trimmed to exactly 5V before connecting.
