# Plan: 2S LiPo → Buck Converter → Bare WROOM Power Supply

**Goal:** Replace the entire AP2112K + TP4056 + 1S LiPo power section with a 2S LiPo → buck converter → 3.3V power supply for bare ESP32-WROOM-32.

## Current Context / Assumptions

- **Bare ESP32-WROOM-32** (not DevKitC) — takes 3.3V on VCC pin, no 5V tolerance
- **2S LiPo** — 7.4V nominal, 8.4V fully charged, ~6.0V end-of-discharge
- **TP4056 removed** — only charges 1S LiPo, cannot charge 2S
- **AP2112K removed** — 2S voltage too high for LDO input
- **Buck converter: MP1584EN module** (adjustable, 3A, 4.5V–28V input, cheap common module) — *change if using different module*
- **Charging: bench only** — user charges 2S LiPo with external balance charger (not shown in schematic)
- **Deliverable:** New schematic file (excalidraw + PNG), replacing the old v2
- **File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`
- **MCU/SENSORS zones unchanged** — ESP32 + TCA9548A + 4× GY-521 wiring stays the same

## Architecture / Proposed Approach

The POWER zone simplifies to: 2S LiPo → MP1584EN buck converter (set to 3.3V output) → 3.3V rail to ESP32 VCC + TCA9548A + 4× GY-521. Input and output filter caps on the buck converter. No LDO, no charger IC in the schematic (bench charging assumed).

## Step-by-Step Tasks

### Task 1: Create excalidraw file skeleton
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Create a valid excalidraw JSON with:
- Three colored background zones: POWER (#fff3bf yellow), MCU (#e7f5ff blue), SENSORS (#ebfbee green)
- Title: "4-IMU ESP32 Tremor Monitor — 2S LiPo Buck Power"
- Subtitle: "Bare ESP32-WROOM-32 · TCA9548A @0x70 · 4× GY-521 · MP1584EN Buck · I2C0 @400kHz"

### Task 2: Add POWER zone components
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Add the following components (rectangles with labels):
- `BT1` — 2S LiPo battery 7.4V 500mAh+ (JST-XH 2-pin balance connector), labeled "2S LiPo 7.4V"
- `U8` — MP1584EN buck converter module, labeled "U8 MP1584EN Buck 3.3V\n4.5-28V IN → 3.3V OUT 3A"
- `C1` — 10µF input filter cap, labeled "C1 10µF IN"
- `C2` — 10µF output filter cap, labeled "C2 10µF OUT"

### Task 3: Draw POWER zone wiring
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Draw arrows:
1. **Battery positive (red):** BT1+ → U8 IN+ (input +)
2. **Battery negative (black):** BT1- → U8 IN- (input -) → GND rail
3. **Buck output (red, bold):** U8 OUT+ → 3.3V rail
4. **Buck output GND (black):** U8 OUT- → GND rail
5. **Input cap:** C1 across U8 IN+ and IN-
6. **Output cap:** C2 across U8 OUT+ and OUT-
7. **3.3V rail to MCU (red, bold):** 3.3V rail → U1 (ESP32 VCC)

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
- **Charging note:** "Bench charge 2S LiPo with external balance charger — not shown"
- **Buck note:** "MP1584EN set to 3.3V output. Verify trim pot before connecting ESP32."

### Task 9: Export and validate
1. Open `tremor_monitor_schematic_v3.excalidraw` in excalidraw.com
2. Export PNG to `docs/images/tremor_monitor_schematic_v3.png`
3. Run `python -c "import json; json.load(open(r'docs/images/tremor_monitor_schematic_v3.excalidraw', encoding='utf-8')); print('JSON valid')"`
4. Expected output: `JSON valid`

## Tests / Validation

- **JSON validity:** `python -c "import json; json.load(open(r'docs/images/tremor_monitor_schematic_v3.excalidraw', encoding='utf-8'))"` → must print "JSON valid"
- **Net checklist:** Verify these nets are present and correctly wired:
  - V_BAT (BT1+ to U8 IN+)
  - GND (star ground common to all)
  - RAIL_3V3 (U8 OUT+ → ESP32 VCC → TCA + IMUs)
  - I2C_SDA (ESP32 → TCA → 4 IMUs)
  - I2C_SCL (ESP32 → TCA → 4 IMUs)
  - LED_GPIO2 (ESP32 → LED)
- **Error check:** Confirm AP2112K is NOT in the schematic
- **Error check:** Confirm TP4056 is NOT in the schematic
- **Error check:** Confirm MT3608 is NOT in the schematic (if present, it's wrong — this topology uses MP1584EN buck, not MT3608 boost)
- **Error check:** Confirm no LDO is present
- **Voltage check:** Buck converter input range (4.5-28V) covers 2S LiPo range (6.0-8.4V) ✓

## Risks, Tradeoffs, and Open Questions

- **2S LiPo charging:** User needs a separate balance charger (e.g., B6AC, ISDT) or a 2S charger module. TP4056 is 1S only and will not work. If user needs charging in-schematic, recommend HX-2S-A2 or similar 2S charger module.
- **Buck converter output voltage:** MP1584EN modules come adjustable. User MUST verify output is exactly 3.3V before connecting ESP32. Overvoltage will damage the module.
- **Buck converter ripple:** Buck converters produce switching ripple. The 10µF output cap is minimal. Consider adding a 100µF electrolytic in parallel for cleaner 3.3V rail under ESP32 WiFi current spikes.
- **MP1584EN vs other modules:** Plan assumes MP1584EN (cheap, common, adjustable). If user has LM2596, pinout and trim pot location differ but electrical function is identical.
- **No battery protection:** This schematic assumes the 2S LiPo has built-in protection (DW01 equivalent) or user monitors voltage externally. Consider adding a low-voltage cutoff circuit or module.
- **Ground loop:** Single ground point recommended to avoid noise on IMU readings from buck converter switching.
