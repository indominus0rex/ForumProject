# Plan: AI Image Generation Prompt — Realistic Components Wiring Diagram

**Created:** 2026-09-01
**Goal:** Write a detailed AI image generation prompt that produces a photorealistic wiring diagram showing actual ESP32, TCA9548A, and GY-521 breakout boards with realistic components, not schematic boxes.

---

## Current Context / Assumptions

- **Existing prompts:**
  - `docs/images/prompt_datasheet_wiring_diagram.txt` — monochrome schematic boxes
  - `docs/images/prompt_datasheet_wiring_diagram_detailed.txt` — detailed schematic boxes with exact coordinates
  - `docs/images/prompt_hand_wiring_diagram.txt` — hand anatomy with colored sensor dots
- **This prompt is different:** Photorealistic render of actual PCBs and components — ESP32-DevKitC board with USB connector and chips, TCA9548A breakout board with header pins, GY-521 (MPU6050) breakout boards with actual component layout, real wires with insulation
- **Firmware config** (`firmware/common/config.py`): SDA=GPIO21, SCL=GPIO22, LED=GPIO2, LRA deferred (NC), TCA9548A @0x70, 4× GY-521 @0x68 via mux, I2C0 @400kHz, 100Hz, 128-sample window
- **Sensor placement (locked 2026-08-27 Option A + ET):**
  - CH0 — dorsal wrist proximal (primary)
  - CH1 — thenar volar (thumb base)
  - CH2 — thumb proximal phalanx, 20° tilt, pill-rolling 4-6Hz
  - CH3 — index proximal phalanx, ET 6-8Hz

---

## Architecture / Proposed Approach

The prompt will be a single text file (~600-800 words) structured for AI image generators: style description (photorealistic product photography) → component descriptions (actual PCB appearance, connectors, chips) → wiring description (real insulated wires, color-coded) → hand anatomy (realistic hand with sensor placement) → technical labels → legend. Each component gets a detailed physical description: ESP32-DevKitC with Micro-USB connector, voltage regulator, GPIO pins along edges; TCA9548A breakout with 16 header pins, address jumpers; GY-521 with MPU6050 chip, pull-up resistors, 8-pin header. Wires are described as insulated stranded copper with specific colors (red=3.3V, black=GND, green=SDA, blue=SCL, yellow=LED). The hand is described as a realistic human hand (dorsal view) with sensors mounted at anatomical positions.

---

## Step-by-Step Tasks

### Task 1: Write the realistic components AI image generation prompt

**File:** `docs/images/prompt_realistic_components_wiring_diagram.txt`

Write the following content:

```
PHOTOREALISTIC WIRING DIAGRAM — REALISTIC COMPONENTS
=====================================================

STYLE:
- Photorealistic product photography style, not schematic
- Clean white background (infinity cove), soft studio lighting from top-left
- Subtle shadows beneath components for depth
- Macro lens perspective, shallow depth of field on edges
- 16:9 landscape orientation, 4K resolution

COMPONENT U1 — ESP32-DevKitC V4 (realistic PCB):
- Physical description: Blue PCB, 52mm × 29mm, 1oz copper, HASL finish
- Micro-USB connector: Silver metal, centered on short edge (bottom)
- Voltage regulator: Black SOT-23-5 chip (AMS1117-3.3) near USB connector, labeled "3.3V"
- ESP32 chip: Black QFN-48 module (ESP32-WROOM-32) centered on board, metal can antenna on right edge
- GPIO pins: Two rows of 19 header pins each (gold-plated, 2.54mm pitch), along both long edges
- Pin labels: Silkscreen white text "3V3", "GND", "D21", "D22", "D2", "D25", "D18", "D19", "D20" next to respective pins
- LEDs: Small red power LED near USB, blue user LED near GPIO2
- Buttons: Black tactile reset button (EN) near USB, black boot button near GPIO0
- Mounting: Four plated mounting holes at board corners
- Position: Left side of canvas, rotated 5° clockwise for dynamic composition

COMPONENT U2 — TCA9548A I²C Multiplexer Breakout (realistic PCB):
- Physical description: Green PCB, 25mm × 20mm, 1oz copper, HASL finish
- Header pins: 2×8 male header pins (gold-plated, 2.54mm pitch) along bottom edge
- TCA9548A chip: Black TSSOP-24 package centered on board, tiny text "9548A" visible
- Address jumpers: Three solder jumpers labeled "A0", "A1", "A2" (all bridged = GND)
- EN pad: Single solder jumper bridged to VCC
- Pull-up resistors: Four 0805 SMD resistors (black, "103" marking) near I²C pins
- Power LED: Small red SMD LED near VCC pin
- Pin labels: Silkscreen "VIN", "GND", "SDA", "SCL", "SD0", "SC0", "SD1", "SC1", "SD2", "SC2", "SD3", "SC3", "RST"
- Position: Center of canvas, below ESP32, rotated 3° counter-clockwise

COMPONENTS U3-U6 — GY-521 MPU6050 Breakout Boards (realistic PCBs):
- Physical description: Blue PCB, 20mm × 15mm, 1oz copper, HASL finish
- MPU6050 chip: Black QFN-24 package centered on board, tiny text visible
- Pull-up resistors: Two 0805 SMD resistors (black, "472" marking) near SDA/SCL
- Decoupling capacitor: Single 0805 SMD capacitor (brown, "104") near VCC
- Header pins: 1×8 male header pins (gold-plated, 2.54mm pitch) along bottom edge
- Pin labels: Silkscreen "VCC", "GND", "SDA", "SCL", "XDA", "XCL", "AD0", "INT"
- AD0 jumper: Solder jumper bridged to GND (sets address 0x68)
- Position: Right side of canvas, stacked vertically with 12mm spacing between boards
- U3 (CH0): Top position, rotated 2° clockwise
- U4 (CH1): Second from top, rotated 1° counter-clockwise
- U5 (CH2): Third from top, rotated 3° clockwise
- U6 (CH3): Bottom position, rotated 2° counter-clockwise

COMPONENT D1 — LED Indicator (realistic):
- Physical description: 5mm round LED, clear lens, diffused white
- Color: Blue when lit (indicates active state)
- Resistor: 220Ω through-hole resistor (blue body, red-red-black-gold bands) soldered to anode lead
- Wires: Red insulated wire to GPIO2, black insulated wire to GND
- Position: Below U6 (CH3), right side of canvas

WIRING (realistic insulated wires):
- Wire type: 30AWG silicone-insulated stranded copper, flexible, slight sheen
- SDA21 wire: Green insulation, 1.5mm diameter, runs from ESP32 GPIO21 pin (right side, row 3) to TCA9548A SDA pin (left side), slight curve, 45mm length
- SCL22 wire: Blue insulation, 1.5mm diameter, runs from ESP32 GPIO22 pin (right side, row 4) to TCA9548A SCL pin (left side), slight curve, 50mm length
- CH0 pair: Green + Blue insulation, runs from TCA9548A SD0/SC0 pins to U3 SDA/SCL pins, 35mm length
- CH1 pair: Green + Blue insulation, runs from TCA9548A SD1/SC1 pins to U4 SDA/SCL pins, 40mm length
- CH2 pair: Green + Blue insulation, runs from TCA9548A SD2/SC2 pins to U5 SDA/SCL pins, 45mm length
- CH3 pair: Green + Blue insulation, runs from TCA9548A SD3/SC3 pins to U6 SDA/SCL pins, 50mm length
- LED wire: Yellow insulation, runs from ESP32 GPIO2 pin to LED anode, 60mm length, slight loop
- Power distribution: Red wire (3.3V) and black wire (GND) daisy-chained from ESP32 to TCA9548A to all GY-521 boards, star topology, 1.0mm diameter
- Wire routing: Wires run below components (under PCB), slight droop between connection points, no sharp bends

HAND ANATOMY (realistic, dorsal view):
- Physical description: Adult human hand, dorsal (back) view, relaxed position, fingers slightly apart
- Skin: Natural skin tone, subtle texture, visible veins on dorsal hand
- Forearm: Visible from wrist to 80mm proximal, tapering
- Fingers: Index, middle, ring, pinky — slightly spread, natural curl
- Thumb: Extended slightly away from palm, natural opposition
- Nails: Natural nail beds, slight pink translucency
- Wrist: Visible crease lines, radial/ulna styloid bumps
- Position: Left side of canvas, hand occupies ~40% of width, fingers pointing up-right at 30°

SENSOR PLACEMENT ON HAND (realistic mounting):
- CH0 (dorsal wrist proximal): GY-521 board mounted on thin double-sided tape, centered over radius/ulna junction, 1cm proximal to wrist crease, wires running proximally along forearm
- CH1 (thenar volar): GY-521 board mounted on palmar surface at thumb base (thenar eminence), visible as slight bulge through skin, wires running along thumb side
- CH2 (thumb proximal phalanx): GY-521 board mounted on dorsal aspect of thumb proximal phalanx, midpoint between CMC and MCP joints, 20° tilt indicator (small arrow), wires running along thumb
- CH3 (index proximal phalanx): GY-521 board mounted on dorsal aspect of index finger proximal phalanx, midpoint between MCP and PIP joints, wires running along finger

TECHNICAL LABELS (overlay text, white with black outline for legibility):
- "U1 · ESP32-DevKitC" — below ESP32 board, 12pt sans-serif
- "U2 · TCA9548A @0x70" — below TCA9548A board, 12pt sans-serif
- "U3 · GY-521 · CH0 · dorsal wrist" — below U3, 10pt sans-serif
- "U4 · GY-521 · CH1 · thenar volar" — below U4, 10pt sans-serif
- "U5 · GY-521 · CH2 · thumb phalanx · pill 4-6Hz" — below U5, 10pt sans-serif
- "U6 · GY-521 · CH3 · index phalanx · ET 6-8Hz" — below U6, 10pt sans-serif
- "D1 · LED · GPIO2 · 220Ω" — below LED, 10pt sans-serif
- "SDA21" — near green wire at ESP32, 8pt monospace, green text
- "SCL22" — near blue wire at ESP32, 8pt monospace, blue text
- "3.3V" — near red wire, 8pt monospace, red text
- "GND" — near black wire, 8pt monospace, black text

LEGEND (top-right corner, semi-transparent white background):
- ■ Blue PCB = ESP32-DevKitC (U1)
- ■ Green PCB = TCA9548A Multiplexer (U2)
- ■ Blue PCB = GY-521 IMU (U3-U6)
- ■ Green wire = I²C SDA
- ■ Blue wire = I²C SCL
- ■ Red wire = 3.3V Power
- ■ Black wire = Ground
- ■ Yellow wire = LED Signal

TITLE BLOCK (top-left):
- "Wiring Diagram — 4-IMU ESP32 Tremor Monitor"
- Subtitle: "Realistic Component View · ESP32-DevKitC · TCA9548A · 4× GY-521 · LED · I²C0 @400kHz · 100Hz"

TECHNICAL NOTES (bottom, small text):
"VCC 3.3V · I²C 400kHz · Sampling 100Hz · Window 128 samples · TCA9548A @0x70 · All GY-521 @0x68 via mux · Wire length <15cm · 0.1µF per IC · LRA GPIO25/18/19/20 deferred (NC)"

NEGATIVE PROMPT (do NOT include):
- No schematic boxes, no abstract symbols, no vector art style
- No hand-drawn sketch, no cartoon, no illustration
- No monochrome-only, no black/white/gray only
- No LRA, no haptic actuators, no vibration motors
- No battery, no USB cable plugged in (just bare boards)
- No breadboard, no perfboard, no custom PCB
- No soldering, no flux residue, no messy wiring
- No fingers touching components, no hand covering sensors

Ref: firmware/common/config.py (SDA21/SCL22, 0x70, NUM_IMUS 4, IMU_CHANNELS [0,1,2,3], SAMPLES 128 @100Hz), cad/connections_4imu.csv, PIN_ASSIGNMENTS.md:48
```

**Verification:** File exists, ~150 lines, each component has detailed physical description (dimensions, colors, materials, positions), wires described with insulation colors and routing, hand described with anatomical detail.

---

### Task 2: Verify prompt completeness against firmware config

**File:** `docs/images/prompt_realistic_components_wiring_diagram.txt`

| Prompt Claim | Firmware Config | Match? |
|--------------|-----------------|--------|
| SDA = GPIO21 | `I2C_SDA_PIN = 21` | ✓ |
| SCL = GPIO22 | `I2C_SCL_PIN = 22` | ✓ |
| LED = GPIO2 | `LED_PIN = 2` | ✓ |
| TCA9548A @0x70 | `TCA9548A_ADDR = 0x70` | ✓ |
| 4× GY-521 @0x68 | `NUM_IMUS = 4`, AD0→GND | ✓ |
| I²C0 @400kHz | `I2C_FREQ = 400000` | ✓ |
| 100Hz sampling | `SAMPLE_INTERVAL_US = 10000` | ✓ |
| 128-sample window | `SAMPLES = 128` | ✓ |
| LRA NC (25/18/19/20) | `LRA_PIN = 25`, `LRA_PINS = [18,19,20]`, duty=0 | ✓ |
| CH0-3 channels | `IMU_CHANNELS = [0,1,2,3]` | ✓ |

**Verification:** All values match firmware config. No discrepancies.

---

### Task 3: Verify component realism detail

**File:** `docs/images/prompt_realistic_components_wiring_diagram.txt`

Component detail checklist:
- ESP32-DevKitC: ✓ USB connector, ✓ voltage regulator, ✓ ESP32 module, ✓ GPIO pins, ✓ LEDs, ✓ buttons, ✓ mounting holes, ✓ dimensions
- TCA9548A breakout: ✓ header pins, ✓ TSSOP-24 chip, ✓ address jumpers, ✓ pull-up resistors, ✓ power LED, ✓ dimensions
- GY-521: ✓ MPU6050 chip, ✓ pull-up resistors, ✓ decoupling cap, ✓ header pins, ✓ AD0 jumper, ✓ dimensions
- Wires: ✓ insulation colors, ✓ wire gauge, ✓ routing description, ✓ star topology
- Hand: ✓ skin tone, ✓ veins, ✓ fingers, ✓ thumb, ✓ nails, ✓ wrist
- Sensors on hand: ✓ anatomical positions, ✓ mounting method, ✓ wire routing

**Verification:** All components have realistic physical descriptions. No abstract "boxes" or "symbols."

---

### Task 4: Test the prompt with an AI image generator

**Tool:** DALL-E, Midjourney, or similar AI image generator

**Action:** Copy the full text from `docs/images/prompt_realistic_components_wiring_diagram.txt` into the image generator.

**Expected output:** A photorealistic image showing:
- Blue ESP32-DevKitC board with visible USB connector, chips, GPIO pins
- Green TCA9548A breakout with visible TSSOP chip, header pins
- Four blue GY-521 boards with visible MPU6050 chips
- Color-coded insulated wires connecting all components
- Realistic human hand with sensors mounted at anatomical positions
- Technical labels overlaid on image
- Legend in corner

**Verification criteria:**
1. Components look like actual PCBs (not schematic boxes)
- ESP32 has visible Micro-USB connector and ESP32-WROOM module
- TCA9548A has visible TSSOP-24 chip and header pins
- GY-521 boards have visible MPU6050 chips
2. Wires look like real insulated wires (not schematic lines)
- Green wire for SDA, blue for SCL, red for 3.3V, black for GND
- Wires have slight droop and curve (not rigid straight lines)
3. Hand looks realistic (not cartoon or vector)
- Visible skin texture, veins, natural finger positions
4. Sensors mounted on hand at correct positions
- CH0 on dorsal wrist, CH1 on thenar, CH2 on thumb, CH3 on index
5. Labels are legible
6. No LRA or haptic actuators visible

**If output fails:**
- If components look like boxes → add "actual PCB, not schematic symbol, show all components"
- If wires look like lines → add "insulated stranded copper wire, 30AWG, visible insulation"
- If hand looks cartoonish → add "photorealistic human hand, macro photography, skin texture"
- If sensors not on hand → add "sensors physically mounted on hand with double-sided tape"
- If too cluttered → add "clean composition, components spaced 10mm apart, wires routed neatly"

---

## Tests / Validation

This is a text prompt deliverable — no unit tests. Validation is:

1. **Completeness check:** All pin numbers, addresses, and parameters match `firmware/common/config.py` (done in Task 2).
2. **Realism check:** All components have detailed physical descriptions — dimensions, colors, materials, positions (done in Task 3).
3. **Negative check:** Prompt explicitly excludes schematic boxes, abstract symbols, cartoon style, LRA, battery, breadboard.
4. **AI test:** Prompt produces a usable image when fed to an AI image generator (done in Task 4).

---

## Risks, Tradeoffs, and Open Questions

- **AI photorealism limitations:** AI image generators struggle with small text on PCBs. The prompt requests silkscreen labels, but the AI may produce garbled text. Mitigation: use the AI output as a base and add labels in post-processing.
- **Component accuracy:** AI may not reproduce exact ESP32-DevKitC or GY-521 layouts. The prompt provides detailed descriptions, but results will be approximate.
- **Hand anatomy:** AI hands are notoriously difficult (finger count, proportions). The prompt specifies "dorsal view, fingers slightly apart" to reduce complexity.
- **Wire routing:** AI may not follow exact wire paths. The prompt provides general routing ("below components, slight droop") rather than exact coordinates.
- **Scale consistency:** AI may render components at inconsistent scales. The prompt provides exact dimensions (52×29mm ESP32, 25×20mm TCA9548A, 20×15mm GY-521) as reference.
- **Open:** Should the prompt include a specific camera angle? (Not specified — "macro lens, top-down" is implied; add "45° overhead angle" for more specificity.)
- **Open:** Should the prompt request a specific background? (Not specified — "clean white background" is generic; add "seamless white photography backdrop" for more realism.)

---

## Files Changed

| File | Action |
|------|--------|
| `docs/images/prompt_realistic_components_wiring_diagram.txt` | Create new |

No existing files modified.
