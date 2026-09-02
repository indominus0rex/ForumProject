# Plan: AI Image Generation Prompt — Datasheet-Style Wiring Diagram

**Created:** 2026-09-01
**Goal:** Write a detailed AI image generation prompt that produces a monochrome engineering-datasheet-style wiring diagram for the 4-IMU ESP32 tremor monitor.

---

## Current Context / Assumptions

- **Existing diagrams:**
  - `docs/images/wiring_diagram_4imu_datasheet.html` — monochrome box-schematic (power rails → MCU → mux → sensors), reference designators (U1-U6, D1), connection table, minimal legend
  - `docs/images/prompt_hand_wiring_diagram.txt` — hand anatomy prompt (colorful, anatomical)
- **This prompt is different:** Monochrome engineering-datasheet aesthetic — black/white/gray, single muted-blue accent, sharp-cornered boxes, orthogonal wires, reference designators, pin tables, no hand illustration, no colored channel fills
- **Firmware config** (`firmware/common/config.py`): SDA=GPIO21, SCL=GPIO22, LED=GPIO2, LRA deferred (NC), TCA9548A @0x70, 4× GY-521 @0x68 via mux, I2C0 @400kHz, 100Hz, 128-sample window
- **Sensor placement (locked 2026-08-27 Option A + ET):**
  - CH0 — dorsal wrist proximal (primary)
  - CH1 — thenar volar (thumb base)
  - CH2 — thumb proximal phalanx, 20° tilt, pill-rolling 4-6Hz
  - CH3 — index proximal phalanx, ET 6-8Hz

---

## Architecture / Proposed Approach

The prompt will be a single text file (~400-600 words) structured for AI image generators: style description → layout (power rails → MCU → mux → sensors) → component boxes with reference designators → wire connections → connection table → legend → technical specs. It will specify a monochrome palette (black/white/gray) with a single muted-blue accent for net names, sharp-cornered boxes, orthogonal wire routing, and a clean engineering-datasheet aesthetic. No hand illustration, no colored channel fills, no decorative elements.

---

## Step-by-Step Tasks

### Task 1: Write the AI image generation prompt

**File:** `docs/images/prompt_datasheet_wiring_diagram.txt`

Write the following content:

```
Professional engineering datasheet-style wiring diagram of a 4-IMU ESP32 tremor monitoring system, clean white background, vector-style technical illustration, 16:9 landscape orientation, monochrome palette with single muted-blue accent color.

LAYOUT (left to right, orthogonal flow):
- Power rails (bottom): horizontal 3.3V bus (black, labeled "3.3V bus star") and GND bus (gray, labeled "GND bus star") with decoupling capacitor note ("0.1µF per IC + 10µF bulk")
- ESP32 box (left, U1): sharp-cornered white box with thin black stroke, labeled "U1 · ESP32-DevKitC" with pin list: "GPIO21 → SDA", "GPIO22 → SCL", "GPIO2 → LED", "3.3V", "GND", dashed grey box "25/18/19/20 NC"
- TCA9548A box (center, U2): sharp-cornered white box, labeled "U2 · TCA9548A" with "@0x70 · A0-A2→GND · EN→3.3V" and channel outputs: "SD0/SC0 → CH0", "SD1/SC1 → CH1", "SD2/SC2 → CH2", "SD3/SC3 → CH3"
- Four IMU boxes (right, U3-U6): stacked vertically, each labeled "U3 · GY-521 (MPU6050) · CH0" through "U6 · GY-521 (MPU6050) · CH3" with "@0x68 · AD0→GND · 0.1µF" and anatomical position: "dorsal wrist proximal · primary", "thenar volar · thumb base", "thumb proximal phalanx · 20° tilt · pill 4-6Hz", "index proximal phalanx · ET 6-8Hz"
- LED box (below IMUs, D1): labeled "D1 · LED Indicator" with "GPIO2 → 220Ω → GND · active high"

WIRE CONNECTIONS (orthogonal routing, thin black strokes):
- SDA21: ESP32 GPIO21 → TCA9548A SDA (single wire, labeled "SDA21" in muted blue)
- SCL22: ESP32 GPIO22 → TCA9548A SCL (single wire, labeled "SCL22" in muted blue)
- CH0 pair: TCA9548A SD0/SC0 → IMU0 (two parallel wires)
- CH1 pair: TCA9548A SD1/SC1 → IMU1 (two parallel wires)
- CH2 pair: TCA9548A SD2/SC2 → IMU2 (two parallel wires)
- CH3 pair: TCA9548A SD3/SC3 → IMU3 (two parallel wires)
- LED wire: ESP32 GPIO2 → D1 (single wire, yellow/grey)
- Power taps: dashed vertical lines from each component box to 3.3V and GND buses

CONNECTION TABLE (bottom-left, monospace font):
| Net | Source | Destination | Notes |
|-----|--------|-------------|-------|
| SDA21 | U1 GPIO21 | U2 SDA | I²C0 data, 400kHz |
| SCL22 | U1 GPIO22 | U2 SCL | I²C0 clock, 400kHz |
| CH0 | U2 SD0/SC0 | U3 SDA/SCL | dorsal wrist |
| CH1 | U2 SD1/SC1 | U4 SDA/SCL | thenar volar |
| CH2 | U2 SD2/SC2 | U5 SDA/SCL | thumb phalanx |
| CH3 | U2 SD3/SC3 | U6 SDA/SCL | index phalanx |
| LED | U1 GPIO2 | D1 anode | 220Ω → GND |
| 3.3V | U1 3.3V | U2-U6 VCC | star topology |
| GND | U1 GND | U2-U6 GND | star topology |

LEGEND (top-right, 4 items):
■ Signal / power (solid black line)
■ Power tap (dashed black line)
■ Net name (muted blue #2c5282 text)
■ NC / deferred (dashed grey box)

TITLE BLOCK (top, bold):
"Wiring Diagram — 4-IMU ESP32 Tremor Monitor"
Subtitle: "ESP32-DevKitC · TCA9548A I²C Mux · 4× GY-521 (MPU6050) · LED Indicator · LRA Deferred · I²C0 @400kHz · 100Hz · 128-sample window · Rev 2026-09-01"

TECHNICAL NOTES (bottom, small monospace):
"VCC 3.3V · I²C 400kHz · Sampling 100Hz (SAMPLE_INTERVAL_US 10000) · Window 128 samples · TCA9548A @0x70 (A0-A2→GND, EN→3.3V) · All GY-521 @0x68 via mux (AD0→GND, channel select via 1<<ch) · Wire length <15cm · 0.1µF decoupling per IC + 10µF bulk · LRA GPIO25/18/19/20 deferred (NC)"

STYLE REQUIREMENTS:
- Clean white background, no gradients
- Monochrome palette: black (#1a1a1a), gray (#666), light gray (#ccc), white (#ffffff)
- Single accent color: muted blue (#2c5282) for net names only
- Sharp-cornered boxes (no rounded corners)
- Thin 1.2px black strokes on component boxes
- Orthogonal wire routing (90° angles, no diagonal lines)
- Sans-serif font (9-12pt) for labels, monospace for pin numbers and table
- Reference designators (U1, U2, U3-U6, D1) in bold
- No hand illustration, no anatomical drawing
- No colored channel fills (blue/green/yellow/orange)
- No photorealistic elements, no shadows, no 3D effects
- No decorative elements, no clutter

NEGATIVE PROMPT (do NOT include):
- No hand, no fingers, no anatomical illustration
- No colored channel fills (no blue/green/yellow/orange boxes)
- No LRA / haptic actuators
- No battery or power connector
- No photorealistic skin texture
- No shadows or 3D effects
- No rounded corners on boxes
- No diagonal wires
- No decorative elements

Ref: firmware/common/config.py (SDA21/SCL22, 0x70, NUM_IMUS 4, IMU_CHANNELS [0,1,2,3], SAMPLES 128 @100Hz), cad/connections_4imu.csv, PIN_ASSIGNMENTS.md:48
```

**Verification:** File exists, ~500 words, monochrome aesthetic specified, no hand illustration, all pin numbers match firmware.

---

### Task 2: Verify prompt completeness against firmware config

**File:** `docs/images/prompt_datasheet_wiring_diagram.txt`

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

### Task 3: Test the prompt with an AI image generator

**Tool:** DALL-E, Midjourney, or similar AI image generator

**Action:** Copy the full text from `docs/images/prompt_datasheet_wiring_diagram.txt` into the image generator.

**Expected output:** A monochrome engineering-datasheet diagram showing:
- Power rails at bottom (3.3V black, GND gray)
- ESP32 box (U1) on left
- TCA9548A box (U2) in center
- 4 IMU boxes (U3-U6) stacked on right
- LED box (D1) below IMUs
- Orthogonal black wires connecting all components
- Connection table at bottom-left
- Legend at top-right
- Title block at top

**Verification criteria:**
1. Monochrome palette (black/white/gray + single blue accent)
2. Sharp-cornered boxes (no rounded corners)
3. Orthogonal wire routing (90° angles)
4. Reference designators visible (U1-U6, D1)
5. No hand illustration
6. No colored channel fills
7. Connection table present
8. No LRA or haptic actuators

**If output fails:**
- If boxes have rounded corners → add "sharp corners, no border-radius, no rounded rectangles"
- If wires are diagonal → add "orthogonal routing only, 90° angles, no diagonal lines"
- If hand appears → strengthen negative prompt: "absolutely no hand, no fingers, no anatomical illustration, no body parts"
- If colored fills appear → add "monochrome only, no colored fills, no blue/green/yellow/orange backgrounds"
- If text is garbled → add "all text is clean sans-serif, no distorted letters, no gibberish"

---

## Tests / Validation

This is a text prompt deliverable — no unit tests. Validation is:

1. **Completeness check:** All pin numbers, addresses, and parameters match `firmware/common/config.py` (done in Task 2).
2. **Style check:** Prompt specifies monochrome, sharp corners, orthogonal wires, no hand, no colored fills.
3. **Negative check:** Prompt explicitly excludes hand, LRA, battery, photorealistic skin, shadows, rounded corners, diagonal wires.
4. **AI test:** Prompt produces a usable image when fed to an AI image generator (done in Task 3).

---

## Risks, Tradeoffs, and Open Questions

- **AI text rendering:** Most AI image generators struggle with legible text. The prompt requests labels, pin numbers, and a connection table, but the AI may produce garbled text. Mitigation: use the AI output as a base layer and add text in post-processing (SVG/Illustrator).
- **Connection table accuracy:** AI will not correctly render a markdown table. The table will need to be added in post-processing.
- **Monochrome constraint:** AI may add color despite instructions. The negative prompt reinforces "monochrome only, no colored fills."
- **No guaranteed pin accuracy:** AI will not correctly place GPIO21 vs GPIO22 without post-processing. The diagram will need manual verification against firmware.
- **Open:** Should the prompt include a specific aspect ratio? (Not specified — AI default is usually 1:1 or 16:9; add "--ar 16:9" for Midjourney if needed.)
- **Open:** Should the prompt request a specific font? (Not specified — "sans-serif" and "monospace" are generic; add "Helvetica" or "Arial" for more specificity.)

---

## Files Changed

| File | Action |
|------|--------|
| `docs/images/prompt_datasheet_wiring_diagram.txt` | Create new |

No existing files modified.
