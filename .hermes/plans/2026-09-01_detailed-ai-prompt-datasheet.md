# Plan: Detailed AI Image Generation Prompt — Datasheet Wiring Diagram

**Created:** 2026-09-01
**Goal:** Write a comprehensive AI image generation prompt with exact visual specifications — box dimensions, wire paths, label positions, spacing, font sizes — that produces a monochrome engineering-datasheet wiring diagram.

---

## Current Context / Assumptions

- **Existing prompt:** `docs/images/prompt_datasheet_wiring_diagram.txt` — 71 lines, good technical detail but lacks visual precision
- **Reference diagram:** `docs/images/wiring_diagram_4imu_datasheet.html` — the exact layout we want to replicate (1100×520 viewBox)
- **User wants:** Exact box dimensions, wire paths, label positions, spacing, font sizes — "if someone has to guess, the plan is incomplete"
- **AI generators:** DALL-E, Midjourney, Stable Diffusion — interpret detailed spatial descriptions better than abstract concepts

---

## Architecture / Proposed Approach

The prompt will be a single text file (~800-1000 words) with 7 sections: Canvas & Grid → Component Boxes (exact dimensions) → Pin Markers → Wires (exact path coordinates) → Labels (exact positions + font specs) → Tables → Style Constraints. Each component gets a reference designator (U1-U6, D1), exact width/height, stroke width, and internal label positions with font family, size, color, and weight. Every wire gets a start coordinate, end coordinate, stroke width, and dash pattern. Every text element gets an x/y position, font family, font size in points, color hex code, and weight.

---

## Step-by-Step Tasks

### Task 1: Write the detailed AI image generation prompt

**File:** `docs/images/prompt_datasheet_wiring_diagram_detailed.txt`

Write the following content:

```
DETAILED ENGINEERING DATASHEET WIRING DIAGRAM PROMPT
====================================================

CANVAS SPECIFICATIONS:
- ViewBox: 1100 × 520 units (16:9 landscape)
- Background: solid white (#FFFFFF), no gradients, no texture
- Border: 1px solid light gray (#CCC) rectangle inset 8px from canvas edge
- Grid: invisible 10-unit grid for alignment (components snap to grid)

TITLE BLOCK (top of canvas, full width):
- Position: x=24, y=24 (left-aligned)
- Title text: "Wiring Diagram — 4-IMU ESP32 Tremor Monitor"
  Font: 'Segoe UI' or 'Helvetica Neue', 18px, weight 600, color #1A1A1A, letter-spacing 0.3px
- Subtitle text: "ESP32-DevKitC · TCA9548A I²C Mux · 4× GY-521 (MPU6050) · LED Indicator · LRA Deferred"
  Font: 'JetBrains Mono' or 'Consolas', 11px, weight 400, color #666666, y=46
- Subtitle line 2: "I²C0 @400kHz · 100Hz · 128-sample window · Rev 2026-09-01"
  Font: 'JetBrains Mono' or 'Consolas', 11px, weight 400, color #666666, y=60
- Border bottom: 2px solid #1A1A1A, from x=24 to x=1076, y=78

POWER BUSES (bottom of canvas):
- 3.3V bus: horizontal line from (40, 470) to (1060, 470), stroke-width 2.5, color #1A1A1A
- GND bus: horizontal line from (40, 490) to (1060, 490), stroke-width 2.5, color #666666
- Label "3.3V bus (star)": x=40, y=462, font 'JetBrains Mono', 9.5px, color #1A1A1A
- Label "GND bus (star)": x=40, y=507, font 'JetBrains Mono', 9.5px, color #666666
- Decoupling note: x=200, y=462, font 'JetBrains Mono', 8.5px, color #666666, text "0.1µF per IC + 10µF bulk"

COMPONENT BOX U1 (ESP32-DevKitC):
- Group transform: translate(120, 140)
- Bounding box: x=0, y=0, width=180, height=160, fill #FFFFFF, stroke #1A1A1A, stroke-width 1.2
- Title: "U1 · ESP32-DevKitC", x=90, y=16, text-anchor middle, font 'Segoe UI', 11px, weight 700, color #1A1A1A
- Subtitle: "I²C0 @400kHz", x=90, y=28, text-anchor middle, font 'JetBrains Mono', 9.5px, color #1A1A1A
- Pin row 1: "GPIO21 → SDA", x=10, y=50, font 'JetBrains Mono', 8.5px, color #666666
  Pin marker: circle cx=180, cy=47, r=3, fill #1A1A1A
- Pin row 2: "GPIO22 → SCL", x=10, y=68, font 'JetBrains Mono', 8.5px, color #666666
  Pin marker: circle cx=180, cy=65, r=3, fill #1A1A1A
- Pin row 3: "GPIO2  → LED", x=10, y=86, font 'JetBrains Mono', 8.5px, color #666666
  Pin marker: circle cx=180, cy=83, r=3, fill #1A1A1A
- Pin row 4: "3.3V", x=10, y=104, font 'JetBrains Mono', 8.5px, color #666666
- Pin row 5: "GND", x=10, y=120, font 'JetBrains Mono', 8.5px, color #666666
- NC box: x=100, y=130, width=74, height=22, fill #FAFAFA, stroke #CCCCCC, stroke-width 1.0, stroke-dasharray 4 3
- NC label: "25/18/19/20 NC", x=137, y=145, text-anchor middle, font 'JetBrains Mono', 8.5px, color #666666

COMPONENT BOX U2 (TCA9548A):
- Group transform: translate(400, 160)
- Bounding box: x=0, y=0, width=160, height=130, fill #FFFFFF, stroke #1A1A1A, stroke-width 1.2
- Title: "U2 · TCA9548A", x=80, y=16, text-anchor middle, font 'Segoe UI', 11px, weight 700, color #1A1A1A
- Subtitle: "@0x70 · A0-A2→GND · EN→3.3V", x=80, y=28, text-anchor middle, font 'JetBrains Mono', 9.5px, color #1A1A1A
- Input SDA: "SDA", x=10, y=50, font 'JetBrains Mono', 8.5px, color #666666
  Pin marker: circle cx=6, cy=47, r=2.5, fill #1A1A1A
- Input SCL: "SCL", x=10, y=68, font 'JetBrains Mono', 8.5px, color #666666
  Pin marker: circle cx=6, cy=65, r=2.5, fill #1A1A1A
- Output CH0: "SD0/SC0 → CH0", x=90, y=48, font 'JetBrains Mono', 8.5px, color #666666
  Pin markers: circle cx=154, cy=45, r=2.5, fill #1A1A1A; circle cx=154, cy=55, r=2.5, fill #1A1A1A
- Output CH1: "SD1/SC1 → CH1", x=90, y=68, font 'JetBrains Mono', 8.5px, color #666666
  Pin markers: circle cx=154, cy=67, r=2.5, fill #1A1A1A; circle cx=154, cy=77, r=2.5, fill #1A1A1A
- Output CH2: "SD2/SC2 → CH2", x=90, y=88, font 'JetBrains Mono', 8.5px, color #666666
  Pin markers: circle cx=154, cy=89, r=2.5, fill #1A1A1A; circle cx=154, cy=99, r=2.5, fill #1A1A1A
- Output CH3: "SD3/SC3 → CH3", x=90, y=108, font 'JetBrains Mono', 8.5px, color #666666
  Pin markers: circle cx=154, cy=111, r=2.5, fill #1A1A1A; circle cx=154, cy=121, r=2.5, fill #1A1A1A

COMPONENT BOX U3 (IMU0):
- Group transform: translate(680, 60)
- Bounding box: x=0, y=0, width=240, height=52, fill #FFFFFF, stroke #1A1A1A, stroke-width 1.2
- Title: "U3 · GY-521 (MPU6050) · CH0", x=10, y=16, font 'Segoe UI', 11px, weight 700, color #1A1A1A
- Subtitle: "@0x68 · AD0→GND · 0.1µF", x=10, y=30, font 'JetBrains Mono', 9.5px, color #1A1A1A
- Position: "dorsal wrist proximal · primary", x=10, y=44, font 'JetBrains Mono', 8.5px, color #666666
- Pin markers: circle cx=8, cy=16, r=2.5, fill #1A1A1A; circle cx=8, cy=28, r=2.5, fill #1A1A1A

COMPONENT BOX U4 (IMU1):
- Group transform: translate(680, 120)
- Bounding box: x=0, y=0, width=240, height=52, fill #FFFFFF, stroke #1A1A1A, stroke-width 1.2
- Title: "U4 · GY-521 (MPU6050) · CH1", x=10, y=16, font 'Segoe UI', 11px, weight 700, color #1A1A1A
- Subtitle: "@0x68 · AD0→GND · 0.1µF", x=10, y=30, font 'JetBrains Mono', 9.5px, color #1A1A1A
- Position: "thenar volar · thumb base", x=10, y=44, font 'JetBrains Mono', 8.5px, color #666666
- Pin markers: circle cx=8, cy=16, r=2.5, fill #1A1A1A; circle cx=8, cy=28, r=2.5, fill #1A1A1A

COMPONENT BOX U5 (IMU2):
- Group transform: translate(680, 180)
- Bounding box: x=0, y=0, width=240, height=52, fill #FFFFFF, stroke #1A1A1A, stroke-width 1.2
- Title: "U5 · GY-521 (MPU6050) · CH2", x=10, y=16, font 'Segoe UI', 11px, weight 700, color #1A1A1A
- Subtitle: "@0x68 · AD0→GND · 0.1µF", x=10, y=30, font 'JetBrains Mono', 9.5px, color #1A1A1A
- Position: "thumb proximal phalanx · 20° tilt · pill 4-6Hz", x=10, y=44, font 'JetBrains Mono', 8.5px, color #666666
- Pin markers: circle cx=8, cy=16, r=2.5, fill #1A1A1A; circle cx=8, cy=28, r=2.5, fill #1A1A1A

COMPONENT BOX U6 (IMU3):
- Group transform: translate(680, 240)
- Bounding box: x=0, y=0, width=240, height=52, fill #FFFFFF, stroke #1A1A1A, stroke-width 1.2
- Title: "U6 · GY-521 (MPU6050) · CH3", x=10, y=16, font 'Segoe UI', 11px, weight 700, color #1A1A1A
- Subtitle: "@0x68 · AD0→GND · 0.1µF", x=10, y=30, font 'JetBrains Mono', 9.5px, color #1A1A1A
- Position: "index proximal phalanx · ET 6-8Hz", x=10, y=44, font 'JetBrains Mono', 8.5px, color #666666
- Pin markers: circle cx=8, cy=16, r=2.5, fill #1A1A1A; circle cx=8, cy=28, r=2.5, fill #1A1A1A

COMPONENT BOX D1 (LED):
- Group transform: translate(680, 310)
- Bounding box: x=0, y=0, width=240, height=36, fill #FFFFFF, stroke #1A1A1A, stroke-width 1.2
- Title: "D1 · LED Indicator", x=10, y=16, font 'Segoe UI', 11px, weight 700, color #1A1A1A
- Subtitle: "GPIO2 → 220Ω → GND · active high", x=10, y=30, font 'JetBrains Mono', 9.5px, color #1A1A1A
- Pin marker: circle cx=8, cy=14, r=2.5, fill #1A1A1A

WIRE CONNECTIONS (exact path coordinates):
- SDA21 wire: path "M 300 187 L 406 207", stroke #1A1A1A, stroke-width 1.3, fill none
- SCL22 wire: path "M 300 205 L 406 225", stroke #1A1A1A, stroke-width 1.3, fill none
- CH0 wire pair 1: path "M 554 205 L 688 76", stroke #1A1A1A, stroke-width 1.3, fill none
- CH0 wire pair 2: path "M 554 215 L 688 88", stroke #1A1A1A, stroke-width 1.3, fill none
- CH1 wire pair 1: path "M 554 227 L 688 136", stroke #1A1A1A, stroke-width 1.3, fill none
- CH1 wire pair 2: path "M 554 237 L 688 148", stroke #1A1A1A, stroke-width 1.3, fill none
- CH2 wire pair 1: path "M 554 249 L 688 196", stroke #1A1A1A, stroke-width 1.3, fill none
- CH2 wire pair 2: path "M 554 259 L 688 208", stroke #1A1A1A, stroke-width 1.3, fill none
- CH3 wire pair 1: path "M 554 271 L 688 256", stroke #1A1A1A, stroke-width 1.3, fill none
- CH3 wire pair 2: path "M 554 281 L 688 268", stroke #1A1A1A, stroke-width 1.3, fill none
- LED wire: path "M 300 223 L 400 223 L 400 30 L 688 30 L 688 324", stroke #1A1A1A, stroke-width 1.3, fill none
- Power tap U1: path "M 160 300 L 160 470", stroke #1A1A1A, stroke-width 1.3, stroke-dasharray 3 3
- Power tap U2: path "M 480 290 L 480 470", stroke #1A1A1A, stroke-width 1.3, stroke-dasharray 3 3
- Power tap IMUs: path "M 800 346 L 800 470", stroke #1A1A1A, stroke-width 1.3, stroke-dasharray 3 3

NET LABELS (accent color):
- "SDA21": x=340, y=183, font 'JetBrains Mono', 8px, weight 600, color #2C5282
- "SCL22": x=340, y=215, font 'JetBrains Mono', 8px, weight 600, color #2C5282

CONNECTION TABLE (bottom-left, below diagram):
- Table position: x=24, y=540 (below diagram container)
- Header row: "Net | Source | Destination | Notes"
  Font: 'Segoe UI', 11px, weight 600, background #F5F5F5, border 1px solid #CCC, padding 6px 10px
- Data rows (9 rows):
  Row 1: "SDA21 | U1 GPIO21 | U2 SDA | I²C0 data, 400kHz"
  Row 2: "SCL22 | U1 GPIO22 | U2 SCL | I²C0 clock, 400kHz"
  Row 3: "CH0 | U2 SD0/SC0 | U3 SDA/SCL | dorsal wrist"
  Row 4: "CH1 | U2 SD1/SC1 | U4 SDA/SCL | thenar volar"
  Row 5: "CH2 | U2 SD2/SC2 | U5 SDA/SCL | thumb phalanx"
  Row 6: "CH3 | U2 SD3/SC3 | U6 SDA/SCL | index phalanx"
  Row 7: "LED | U1 GPIO2 | D1 anode | 220Ω → GND"
  Row 8: "3.3V | U1 3.3V | U2-U6 VCC | star topology"
  Row 9: "GND | U1 GND | U2-U6 GND | star topology"
  Font: 'JetBrains Mono', 11px, border 1px solid #CCC, padding 5px 10px

LEGEND (top-right, below title block):
- Position: x=850, y=90
- Background: #F8F8F8, border 1px solid #CCC, padding 10px 14px
- Item 1: 20px solid black line + "Signal / power" (11px sans-serif)
- Item 2: 20px dashed black line + "Power tap (schematic)" (11px sans-serif)
- Item 3: 20px solid blue (#2C5282) line + "Net name" (11px sans-serif)
- Item 4: 12×12px dashed gray box + "NC / deferred" (11px sans-serif)

TECHNICAL NOTES (bottom, full width):
- Position: x=24, y=720 (below connection table)
- Border top: 1px solid #CCC, padding-top 12px
- Text: "Operating Parameters: VCC 3.3V · I²C 400kHz · Sampling 100Hz (SAMPLE_INTERVAL_US 10000) · Window 128 samples · TCA9548A @0x70 (A0-A2→GND, EN→3.3V) · All GY-521 @0x68 via mux (AD0→GND, channel select via 1<<ch) · Wire length <15cm · 0.1µF decoupling per IC + 10µF bulk · LRA GPIO25/18/19/20 deferred (NC)"
  Font: 'JetBrains Mono', 11px, color #666666

STYLE CONSTRAINTS (strict):
- Monochrome palette ONLY: black #1A1A1A, gray #666666, light gray #CCCCCC, white #FFFFFF
- Single accent: muted blue #2C5282 for net labels ONLY
- Sharp corners on ALL boxes (no border-radius, no rounded rectangles)
- ALL strokes: exact widths specified (1.0, 1.2, 1.3, 1.6, 2.5)
- ALL fonts: exact families specified (Segoe UI, JetBrains Mono, Consolas)
- ALL font sizes: exact sizes specified (8, 8.5, 9.5, 11, 18)
- ALL colors: exact hex codes specified
- ALL positions: exact x/y coordinates specified
- NO gradients, NO shadows, NO 3D effects, NO textures
- NO hand, NO fingers, NO anatomical illustration
- NO colored channel fills (no blue/green/yellow/orange backgrounds)
- NO LRA, NO battery, NO photorealistic elements
- NO decorative elements, NO clutter

NEGATIVE PROMPT (absolute exclusions):
- Absolutely NO hand, fingers, wrist, or body parts
- Absolutely NO colored fills (no blue/green/yellow/orange/red backgrounds)
- Absolutely NO LRA, haptic actuators, or vibration motors
- Absolutely NO battery, USB connector, or power jack
- Absolutely NO photorealistic skin, textures, or shadows
- Absolutely NO rounded corners on any box
- Absolutely NO diagonal wires (all wires must be orthogonal 90° angles)
- Absolutely NO decorative borders, icons, or emblems
- Absolutely NO gradients or 3D bevel effects

Ref: firmware/common/config.py (SDA21/SCL22, 0x70, NUM_IMUS 4, IMU_CHANNELS [0,1,2,3], SAMPLES 128 @100Hz), cad/connections_4imu.csv, PIN_ASSIGNMENTS.md:48
```

**Verification:** File exists, ~250 lines, every component has exact dimensions, every wire has exact path coordinates, every label has exact position + font + size + color.

---

### Task 2: Verify prompt completeness against firmware config

**File:** `docs/images/prompt_datasheet_wiring_diagram_detailed.txt`

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

### Task 3: Verify visual precision

**File:** `docs/images/prompt_datasheet_wiring_diagram_detailed.txt`

Count of exact specifications:
- Component boxes: 7 (U1, U2, U3, U4, U5, U6, D1) — each with x, y, width, height, fill, stroke, stroke-width
- Pin markers: 17 circles — each with cx, cy, r, fill
- Wires: 14 paths — each with exact "M/L" coordinates, stroke, stroke-width, dasharray
- Labels: 30+ text elements — each with x, y, font-family, font-size, weight, color
- Tables: 1 connection table with 9 rows, exact column widths, padding, borders
- Font sizes: 8, 8.5, 9.5, 11, 18 — all explicitly stated
- Colors: #1A1A1A, #666666, #CCCCCC, #FFFFFF, #2C5282, #FAFAFA, #F8F8F8, #F5F5F5 — all hex codes

**Verification:** No ambiguous terms ("small", "medium", "large", "near", "beside"). Every visual element has exact numeric values.

---

### Task 4: Test the prompt with an AI image generator

**Tool:** DALL-E, Midjourney, or similar AI image generator

**Action:** Copy the full text from `docs/images/prompt_datasheet_wiring_diagram_detailed.txt` into the image generator.

**Expected output:** A monochrome engineering-datasheet diagram matching the exact specifications:
- 7 component boxes at exact positions with exact dimensions
- 14 wires following exact path coordinates
- 30+ labels at exact positions with correct fonts and sizes
- Connection table with 9 rows
- Legend with 4 items
- No hand, no colored fills, no LRA, no rounded corners

**Verification criteria:**
1. Component boxes at correct positions (U1 at 120,140; U2 at 400,160; U3-U6 at 680,60-240; D1 at 680,310)
2. Box dimensions correct (U1: 180×160, U2: 160×130, U3-U6: 240×52, D1: 240×36)
3. Wire paths match coordinates (SDA21: 300,187→406,207; SCL22: 300,205→406,225; etc.)
4. Font hierarchy visible (18px title, 11px component titles, 9.5px subtitles, 8.5px pins, 8px net labels)
5. Monochrome palette (black/gray/white + blue accent for net names)
6. Sharp corners on all boxes
7. Orthogonal wire routing (90° angles)
8. Connection table present with 9 rows
9. No hand illustration
10. No colored channel fills

**If output fails:**
- If boxes are wrong size → add "exact pixel dimensions" and repeat width/height for each box
- If wires don't connect → add "wires must terminate exactly at pin marker circle centers"
- If text is garbled → add "all text must be legible, no distorted letters, no gibberish"
- If hand appears → add "CRITICAL: no hand, no fingers, no body parts — this is a pure schematic diagram"
- If colored fills appear → add "all box fills must be solid white #FFFFFF, absolutely no colored backgrounds"

---

## Tests / Validation

This is a text prompt deliverable — no unit tests. Validation is:

1. **Completeness check:** All pin numbers, addresses, and parameters match `firmware/common/config.py` (done in Task 2).
2. **Precision check:** Every visual element has exact numeric values — no ambiguous terms (done in Task 3).
3. **Negative check:** Prompt explicitly excludes hand, LRA, battery, photorealistic skin, shadows, rounded corners, diagonal wires, colored fills.
4. **AI test:** Prompt produces a usable image when fed to an AI image generator (done in Task 4).

---

## Risks, Tradeoffs, and Open Questions

- **AI text rendering:** Most AI image generators struggle with legible text at small sizes (8-9.5px). The prompt specifies exact fonts and sizes, but the AI may produce garbled text. Mitigation: use the AI output as a base layer and add text in post-processing (SVG/Illustrator).
- **Coordinate precision:** AI will not follow exact SVG coordinates. The prompt provides relative positions ("U1 left, U2 center, U3-U6 right") as fallback.
- **Connection table accuracy:** AI will not correctly render a markdown table. The table will need to be added in post-processing.
- **Prompt length:** ~250 lines is very long for an AI prompt. Some generators may truncate. Mitigation: split into "primary prompt" (first 100 lines) and "style constraints" (remaining 150 lines).
- **No guaranteed pin accuracy:** AI will not correctly place GPIO21 vs GPIO22 without post-processing. The diagram will need manual verification against firmware.
- **Open:** Should the prompt include a specific aspect ratio? (Not specified — AI default is usually 1:1 or 16:9; add "--ar 16:9" for Midjourney if needed.)
- **Open:** Should the prompt request a specific DPI? (Not specified — add "300 DPI" for print-quality output if needed.)

---

## Files Changed

| File | Action |
|------|--------|
| `docs/images/prompt_datasheet_wiring_diagram_detailed.txt` | Create new |

No existing files modified.
