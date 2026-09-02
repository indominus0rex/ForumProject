# Plan: AI Image Generation Prompt for Hand-Centered Wiring Diagram

**Created:** 2026-09-01
**Goal:** Write a detailed AI image generation prompt that produces a hand-centered anatomical wiring diagram for the 4-IMU ESP32 tremor monitor.

---

## Current Context / Assumptions

- **Existing prompts:**
  - `wiring_diagram_prompt_4imu_minimalist.txt` — box-schematic + small hand inset, no LRA
  - `wiring_diagram_prompt_detailed.txt` — hand anatomy with IMUs + LRAs (outdated placement, includes LRA)
- **Current firmware config** (`firmware/common/config.py`): SDA=GPIO21, SCL=GPIO22, LED=GPIO2, LRA deferred (NC), TCA9548A @0x70, 4× GY-521 @0x68 via mux, I2C0 @400kHz, 100Hz, 128-sample window
- **Sensor placement (locked 2026-08-27 Option A + ET):**
  - CH0 — dorsal wrist proximal (blue)
  - CH1 — thenar volar / thumb base (green)
  - CH2 — thumb proximal phalanx, 20° tilt, pill-rolling 4-6Hz (yellow)
  - CH3 — index proximal phalanx, ET 6-8Hz (orange)
- **User wants:** A detailed AI image generation prompt (for DALL-E, Midjourney, etc.) that describes the diagram

---

## Architecture / Proposed Approach

The prompt will be a single text file (~500-800 words) structured for AI image generators: style description → main subject (hand + sensors) → wiring details → electronics → legend → technical specs. It will specify a hand-centered composition (hand ~60% of canvas), color-coded sensor dots at anatomical positions, wires routing to a compact electronics block, and a legend. The prompt will explicitly exclude LRA, battery, and photorealistic skin to keep the diagram clean and technical.

---

## Step-by-Step Tasks

### Task 1: Write the AI image generation prompt

**File:** `docs/images/prompt_hand_wiring_diagram.txt`

Write the following content:

```
Professional technical wiring diagram of a left human hand and forearm showing a wearable Parkinson's tremor monitoring system, clean white background, vector-style illustration, slight isometric view with palm facing slightly toward viewer to show both dorsal and volar anatomy.

INERTIAL MEASUREMENT UNITS (IMUs — small rectangular sensor boards highlighted in distinct colors, labeled GY-521 / MPU6050) are mounted at these EXACT anatomical positions:

1. DORSAL WRIST PROXIMAL — center of the dorsal wrist, approximately 1cm proximal to the wrist crease, over the radius/ulna junction (labeled: "CH0 · Dorsal Wrist Proximal · Primary" with BLUE highlight and "0" marker)
2. THENAR EMINENCE (VOLAR) — palmar surface at the thick muscular base of the thumb, between wrist crease and thumb CMC joint, shown as a translucent ghost overlay on the hand (labeled: "CH1 · Thenar Volar · Thumb Base" with GREEN highlight and "1" marker)
3. THUMB PROXIMAL PHALANX — dorsal aspect of thumb's proximal phalanx, roughly midpoint between CMC and MCP joints, with a small 20° tilt indicator (labeled: "CH2 · Thumb Phalanx 20° · Pill-Rolling 4-6Hz" with YELLOW/AMBER highlight and "2" marker)
4. INDEX PROXIMAL PHALANX — dorsal aspect of index finger's proximal phalanx, midpoint between MCP and PIP joints (labeled: "CH3 · Index Phalanx · Postural ET 6-8Hz" with ORANGE highlight and "3" marker)

ELECTRONICS BLOCK (right side of canvas, compact stacked layout):
- ESP32-DevKitC board (labeled "U1 · ESP32" with pin labels: "21 SDA", "22 SCL", "2 LED", "3.3V", "GND", "25/18/19/20 NC")
- TCA9548A multiplexer (labeled "U2 · TCA9548A @0x70" with channel labels: "CH0", "CH1", "CH2", "CH3")
- LED indicator (labeled "D1 · LED · 220Ω")

WIRING (color-coded, orthogonal routing with slight curves, no crossing):
- BLUE wire from CH0 sensor dot → TCA9548A CH0 pin
- GREEN wire from CH1 sensor dot → TCA9548A CH1 pin
- YELLOW/AMBER wire from CH2 sensor dot → TCA9548A CH2 pin
- ORANGE wire from CH3 sensor dot → TCA9548A CH3 pin
- GREEN bundled pair (SDA21) from ESP32 GPIO21 → TCA9548A SDA
- BLUE bundled pair (SCL22) from ESP32 GPIO22 → TCA9548A SCL
- YELLOW wire from ESP32 GPIO2 → LED → 220Ω → GND
- RED wire (3.3V power) and BLACK wire (GND) shown as horizontal buses at bottom with star topology note

I²C BUS DETAIL:
- ESP32 GPIO21 (SDA) → TCA9548A SDA
- ESP32 GPIO22 (SCL) → TCA9548A SCL
- TCA9548A address pins A0/A1/A2 → GND (sets address 0x70)
- TCA9548A EN → 3.3V
- All IMU AD0 pins → GND (address 0x68 per channel via mux select)

LEGEND (top-right corner, 6 swatches):
■ BLUE = CH0 · Dorsal Wrist · Primary
■ GREEN = CH1 · Thenar Volar · Thumb Base
■ YELLOW = CH2 · Thumb Phalanx 20° · Pill-Rolling 4-6Hz
■ ORANGE = CH3 · Index Phalanx · Postural ET 6-8Hz
■ RED = 3.3V Power Bus
■ BLACK = GND Bus

STYLE REQUIREMENTS:
- Clean white background, no gradients
- Vector-style illustration (not photorealistic)
- Hand occupies ~60% of canvas width (left side)
- Electronics block occupies ~30% of canvas width (right side)
- Thin 2px black strokes on component boxes
- Sans-serif font (9-12pt) for labels, monospace for pin numbers
- Orthogonal wire routing with slight curves at corners
- No wires inside the hand outline (only sensor dots)
- Translucent volar ghost (rgba green, 12% opacity) for thenar region
- Small "0-3" number markers on each sensor dot
- Leader lines from labels to sensor dots

NEGATIVE PROMPT (do NOT include):
- No LRA / haptic actuators
- No battery or power connector
- No photorealistic skin texture
- No shadows or 3D effects
- No text on the skin itself
- No MOSFETs or driver circuits
- No strap or wristband
- No clutter or decorative elements

TECHNICAL NOTES (bottom of diagram, small monospace text):
"I²C0 @400kHz · 100Hz · 128-sample window · TCA9548A @0x70 · All GY-521 @0x68 via mux (1<<ch) · Wire length <15cm · 0.1µF per IC + 10µF bulk · LRA GPIO25/18/19/20 deferred (NC)"

Ref: firmware/common/config.py (SDA21/SCL22, 0x70, NUM_IMUS 4, IMU_CHANNELS [0,1,2,3], SAMPLES 128 @100Hz), cad/connections_4imu.csv, PIN_ASSIGNMENTS.md:48
```

**Verification:** File exists, ~600-800 words, all sensor positions match Option A + ET lock.

---

### Task 2: Verify prompt completeness against firmware config

**File:** `docs/images/prompt_hand_wiring_diagram.txt`

Cross-check every technical claim in the prompt:

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

**Action:** Copy the full text from `docs/images/prompt_hand_wiring_diagram.txt` into the image generator.

**Expected output:** A vector-style technical diagram showing:
- Left hand + forearm (dorsal view) occupying ~60% of canvas
- 4 color-coded sensor dots at correct anatomical positions
- Electronics block on right side (ESP32 + TCA + LED)
- Color-coded wires connecting sensors to electronics
- Legend in top-right corner
- Technical notes at bottom

**Verification criteria:**
1. Hand is clearly visible and anatomically plausible
2. 4 sensor dots present with correct colors (blue, green, yellow, orange)
3. Wires route from sensors to electronics without crossing
4. No LRA or haptic actuators visible
5. Legend matches sensor colors
6. Text is legible (pin numbers, labels)

**If output fails:**
- If hand is too small → add "hand is the focal point, 60% of canvas width"
- If wires are missing → add "all wires clearly visible, color-coded, orthogonal routing"
- If LRA appears → strengthen negative prompt: "absolutely no LRA, no haptic actuators, no third actuator type"
- If text is garbled → add "all text is clean, sans-serif, no distorted letters"

---

## Tests / Validation

This is a text prompt deliverable — no unit tests. Validation is:

1. **Completeness check:** All pin numbers, addresses, and parameters match `firmware/common/config.py` (done in Task 2).
2. **Placement check:** All 4 sensor positions match Option A + ET lock (2026-08-27).
3. **Negative check:** Prompt explicitly excludes LRA, battery, photorealistic skin, shadows.
4. **AI test:** Prompt produces a usable image when fed to an AI image generator (done in Task 3).

---

## Risks, Tradeoffs, and Open Questions

- **AI text rendering:** Most AI image generators struggle with legible text. The prompt requests labels and pin numbers, but the AI may produce garbled text. Mitigation: use the AI output as a base layer and add text in post-processing (SVG/Illustrator).
- **Anatomical accuracy:** AI may produce unrealistic hand proportions. The prompt specifies "vector-style" to reduce photorealism pressure.
- **Wire routing:** AI may not follow orthogonal routing instructions perfectly. The prompt specifies "orthogonal routing with slight curves, no crossing" but results may vary.
- **No guaranteed pin accuracy:** AI will not correctly place GPIO21 vs GPIO22 without post-processing. The diagram will need manual verification against firmware.
- **Open:** Should the prompt include a strap/wristband outline? (Not included — YAGNI, can be added later.)
- **Open:** Should the prompt request a specific aspect ratio? (Not specified — AI default is usually 1:1 or 16:9; add "--ar 16:9" for Midjourney if needed.)

---

## Files Changed

| File | Action |
|------|--------|
| `docs/images/prompt_hand_wiring_diagram.txt` | Create new |

No existing files modified.
