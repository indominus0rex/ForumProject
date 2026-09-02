# Plan: Manually Create Wiring Diagram in DigiKey Scheme It

**Created:** 2026-09-01
**Goal:** Create a professional wiring diagram for the 4-IMU ESP32 tremor monitor using DigiKey Scheme It's free online schematic editor.

---

## Current Context / Assumptions

- **Tool:** DigiKey Scheme It (https://www.digikey.com/en/schemeit/project) — free, browser-based, no download required
- **Firmware config** (`firmware/common/config.py`): SDA=GPIO21, SCL=GPIO22, LED=GPIO2, LRA deferred (NC), TCA9548A @0x70, 4× GY-521 @0x68 via mux, I2C0 @400kHz, 100Hz, 128-sample window
- **Sensor placement (locked 2026-08-27 Option A + ET):**
  - CH0 — dorsal wrist proximal (primary)
  - CH1 — thenar volar (thumb base)
  - CH2 — thumb proximal phalanx, 20° tilt, pill-rolling 4-6Hz
  - CH3 — index proximal phalanx, ET 6-8Hz
- **Scheme It capabilities:** 700+ schematic symbols, drag-and-drop, wire routing, custom symbol editor, BOM manager, export to PNG/SVG/PDF/KiCad
- **User has:** Zero context for the codebase, questionable taste — plan must be explicit and unambiguous

---

## Architecture / Proposed Approach

The diagram will use a **box-schematic style** (not pictorial) with 7 component boxes: ESP32 (U1), TCA9548A (U2), 4× GY-521 (U3-U6), and LED (D1). Power rails at bottom (3.3V + GND). I2C bus wires (SDA21, SCL22) from ESP32 to mux, then per-channel pairs from mux to each IMU. LED wire from ESP32 GPIO2 to LED. Labels with pin numbers, addresses, and anatomical positions. Connection table at bottom. Export as SVG for documentation.

---

## Step-by-Step Tasks

### Task 1: Open Scheme It and create new project

**URL:** https://www.digikey.com/en/schemeit/project

**Steps:**
1. Open Chrome/Firefox/Safari browser
2. Navigate to `https://www.digikey.com/en/schemeit/project`
3. Click **"New"** button (top-left toolbar) → Select **"Blank Project"**
4. Wait for editor to load — you should see a large white canvas with a left sidebar containing component categories

**Expected result:** Empty canvas with toolbar at top, component library on left, properties panel on right.

**Verification:** Canvas is visible, no error messages, "Untitled" project name in top bar.

---

### Task 2: Find and place ESP32 symbol (U1)

**Steps:**
1. In left sidebar, click **"Integrated Circuits (ICs)"** category
2. Scroll down to **"Embedded"** subcategory
3. Look for **"ESP32"** or **"ESP32-WROOM-32"** symbol
4. If not found, use search bar at top of sidebar: type `ESP32` and press Enter
5. Drag the ESP32 symbol onto the canvas, position it at approximately **x=120, y=140** (left side)
6. Click the symbol to select it — handles appear on corners
7. In right panel (Properties), set:
   - **Reference Designator:** `U1`
   - **Value:** `ESP32-DevKitC`

**Expected result:** ESP32 symbol on canvas, labeled "U1".

**Verification:** Symbol is visible, selected, properties show U1.

---

### Task 3: Find and place TCA9548A symbol (U2)

**Steps:**
1. In left sidebar search bar, type `TCA9548A` and press Enter
2. If no exact match, try `TCA9548` or `I2C multiplexer`
3. Drag the TCA9548A symbol onto canvas, position at approximately **x=400, y=160** (center)
4. If no symbol exists, create custom symbol (see Task 3a below)
5. Set properties:
   - **Reference Designator:** `U2`
   - **Value:** `TCA9548A @0x70`

**Expected result:** TCA9548A symbol on canvas, labeled "U2".

**Verification:** Symbol is visible, selected, properties show U2.

---

### Task 3a: Create custom TCA9548A symbol (if not in library)

**Steps:**
1. Click **"Custom"** button in left sidebar (or go to **File → New Custom Symbol**)
2. In symbol editor:
   - Draw rectangle: width=160, height=130 (use Rectangle tool)
   - Add pins on left side (4 pins): SDA, SCL, VCC, GND
   - Add pins on right side (8 pins): SD0, SC0, SD1, SC1, SD2, SC2, SD3, SC3
   - Add text labels inside box: "TCA9548A" (bold, 11pt), "@0x70" (9pt)
3. Click **"Save"** → Name it `TCA9548A_Custom`
4. Return to main editor, find custom symbol in **"Custom"** category
5. Drag onto canvas at x=400, y=160

**Expected result:** Custom TCA9548A symbol on canvas.

**Verification:** Symbol has correct pin count and labels.

---

### Task 4: Find and place 4× GY-521 symbols (U3-U6)

**Steps:**
1. In left sidebar search bar, type `MPU6050` or `GY-521` and press Enter
2. If no exact match, try `IMU` or `accelerometer`
3. Drag the symbol onto canvas 4 times, position vertically stacked at **x=680**, y-values:
   - U3 (CH0): **y=60**
   - U4 (CH1): **y=120**
   - U5 (CH2): **y=180**
   - U6 (CH3): **y=240**
4. Set properties for each:
   - U3: RefDes=`U3`, Value=`GY-521 CH0`
   - U4: RefDes=`U4`, Value=`GY-521 CH1`
   - U5: RefDes=`U5`, Value=`GY-521 CH2`
   - U6: RefDes=`U6`, Value=`GY-521 CH3`

**Expected result:** 4 IMU symbols stacked on right side of canvas.

**Verification:** All 4 symbols visible, labeled U3-U6.

---

### Task 5: Find and place LED symbol (D1)

**Steps:**
1. In left sidebar, click **"Optoelectronics"** category
2. Find **"LED"** symbol (standard diode with arrows)
3. Drag onto canvas at approximately **x=680, y=310** (below U6)
4. Set properties:
   - **Reference Designator:** `D1`
   - **Value:** `LED · GPIO2 · 220Ω`

**Expected result:** LED symbol on canvas, labeled "D1".

**Verification:** LED visible below IMU stack.

---

### Task 6: Draw power rails (3.3V and GND)

**Steps:**
1. Select **"Wire"** tool from top toolbar (or press `W` key)
2. Draw horizontal line for 3.3V bus:
   - Start point: **x=40, y=470**
   - End point: **x=1060, y=470**
   - Stroke: **2.5px**, color: **black (#1A1A1A)**
3. Draw horizontal line for GND bus:
   - Start point: **x=40, y=490**
   - End point: **x=1060, y=490**
   - Stroke: **2.5px**, color: **gray (#666666)**
4. Add text labels (use **"Text"** tool or press `T`):
   - "3.3V bus (star)": x=40, y=462, font 9.5pt monospace, black
   - "GND bus (star)": x=40, y=507, font 9.5pt monospace, gray
   - "0.1µF per IC + 10µF bulk": x=200, y=462, font 8.5pt monospace, gray

**Expected result:** Two horizontal lines at bottom with labels.

**Verification:** Lines span full width, labels legible.

---

### Task 7: Draw I2C bus wires (ESP32 → TCA9548A)

**Steps:**
1. Select **"Wire"** tool
2. Draw SDA21 wire:
   - Start: **x=300, y=187** (ESP32 GPIO21 pin)
   - End: **x=406, y=207** (TCA9548A SDA pin)
   - Stroke: **1.3px**, color: **black**
3. Draw SCL22 wire:
   - Start: **x=300, y=205** (ESP32 GPIO22 pin)
   - End: **x=406, y=225** (TCA9548A SCL pin)
   - Stroke: **1.3px**, color: **black**
4. Add net labels (use **"Text"** tool):
   - "SDA21": x=340, y=183, font 8pt monospace, color **#2C5282** (muted blue), weight 600
   - "SCL22": x=340, y=215, font 8pt monospace, color **#2C5282**, weight 600

**Expected result:** Two wires connecting ESP32 to mux with blue net labels.

**Verification:** Wires connect pin-to-pin, labels visible.

---

### Task 8: Draw per-channel wires (TCA9548A → IMUs)

**Steps:**
1. Select **"Wire"** tool
2. Draw CH0 pair (TCA CH0 → U3):
   - Wire 1: **M 554 205 L 688 76** (SD0 → SDA)
   - Wire 2: **M 554 215 L 688 88** (SC0 → SCL)
3. Draw CH1 pair (TCA CH1 → U4):
   - Wire 1: **M 554 227 L 688 136** (SD1 → SDA)
   - Wire 2: **M 554 237 L 688 148** (SC1 → SCL)
4. Draw CH2 pair (TCA CH2 → U5):
   - Wire 1: **M 554 249 L 688 196** (SD2 → SDA)
   - Wire 2: **M 554 259 L 688 208** (SC2 → SCL)
5. Draw CH3 pair (TCA CH3 → U6):
   - Wire 1: **M 554 271 L 688 256** (SD3 → SDA)
   - Wire 2: **M 554 281 L 688 268** (SC3 → SCL)
6. All wires: stroke **1.3px**, color **black**

**Expected result:** 8 wires connecting mux to 4 IMUs (2 per IMU).

**Verification:** All wires connect pin-to-pin, no crossings.

---

### Task 9: Draw LED wire

**Steps:**
1. Select **"Wire"** tool
2. Draw LED wire:
   - Path: **M 300 223 L 400 223 L 400 30 L 688 30 L 688 324**
   - Stroke: **1.3px**, color: **black**
3. Add net label: "LED", x=450, y=25, font 8pt monospace, color **#2C5282**

**Expected result:** Wire from ESP32 GPIO2 routing up and over to LED.

**Verification:** Wire connects ESP32 pin to LED anode.

---

### Task 10: Draw power tap wires

**Steps:**
1. Select **"Wire"** tool
2. Draw 3 dashed vertical lines from component boxes to power buses:
   - U1 (ESP32): **M 160 300 L 160 470** (dashed, 3px dash pattern)
   - U2 (TCA): **M 480 290 L 480 470** (dashed)
   - U3-U6 (IMUs): **M 800 346 L 800 470** (dashed)
3. All wires: stroke **1.3px**, color **black**, dash pattern **3 3**

**Expected result:** 3 dashed vertical lines connecting components to 3.3V bus.

**Verification:** Lines are dashed, connect boxes to bottom bus.

---

### Task 11: Add component detail labels

**Steps:**
1. Use **"Text"** tool to add labels inside/next to each box:
   - U1: "I²C0 @400kHz" (inside box, below title, 9.5pt monospace)
   - U2: "A0-A2→GND · EN→3.3V" (inside box, below title, 9.5pt monospace)
   - U3: "@0x68 · AD0→GND · 0.1µF" (inside box, 9.5pt monospace)
   - U4: "@0x68 · AD0→GND · 0.1µF" (inside box, 9.5pt monospace)
   - U5: "@0x68 · AD0→GND · 0.1µF" (inside box, 9.5pt monospace)
   - U6: "@0x68 · AD0→GND · 0.1µF" (inside box, 9.5pt monospace)
   - D1: "GPIO2 → 220Ω → GND · active high" (inside box, 9.5pt monospace)
2. Add anatomical position labels (outside boxes, 8.5pt monospace, gray):
   - U3: "dorsal wrist proximal · primary" (below box)
   - U4: "thenar volar · thumb base" (below box)
   - U5: "thumb proximal phalanx · 20° tilt · pill 4-6Hz" (below box)
   - U6: "index proximal phalanx · ET 6-8Hz" (below box)

**Expected result:** All components have technical labels with pin numbers, addresses, and positions.

**Verification:** Labels legible, no overlapping text.

---

### Task 12: Add connection table

**Steps:**
1. Use **"Text"** tool to create a table at bottom-left (below power buses):
   - Header: "Net | Source | Destination | Notes" (11pt, bold, background #F5F5F5)
   - Row 1: "SDA21 | U1 GPIO21 | U2 SDA | I²C0 data, 400kHz"
   - Row 2: "SCL22 | U1 GPIO22 | U2 SCL | I²C0 clock, 400kHz"
   - Row 3: "CH0 | U2 SD0/SC0 | U3 SDA/SCL | dorsal wrist"
   - Row 4: "CH1 | U2 SD1/SC1 | U4 SDA/SCL | thenar volar"
   - Row 5: "CH2 | U2 SD2/SC2 | U5 SDA/SCL | thumb phalanx"
   - Row 6: "CH3 | U2 SD3/SC3 | U6 SDA/SCL | index phalanx"
   - Row 7: "LED | U1 GPIO2 | D1 anode | 220Ω → GND"
   - Row 8: "3.3V | U1 3.3V | U2-U6 VCC | star topology"
   - Row 9: "GND | U1 GND | U2-U6 GND | star topology"
2. Font: 'JetBrains Mono' or 'Consolas', 11pt, color #1A1A1A

**Expected result:** 9-row connection table at bottom of diagram.

**Verification:** Table legible, all nets documented.

---

### Task 13: Add legend

**Steps:**
1. Use **"Text"** tool to create legend at top-right (below title block):
   - Background: #F8F8F8, border 1px solid #CCC, padding 10px 14px
   - Item 1: "■ Signal / power" (solid black line swatch, 11pt)
   - Item 2: "■ Power tap (schematic)" (dashed black line swatch, 11pt)
   - Item 3: "■ Net name" (muted blue #2C5282 line swatch, 11pt)
   - Item 4: "■ NC / deferred" (dashed grey box swatch, 11pt)

**Expected result:** Legend with 4 items at top-right.

**Verification:** Legend visible, swatches match wire styles.

---

### Task 14: Add title block

**Steps:**
1. Use **"Text"** tool at top-left:
   - Title: "Wiring Diagram — 4-IMU ESP32 Tremor Monitor"
     Font: 'Segoe UI', 18pt, weight 600, color #1A1A1A, letter-spacing 0.3px
   - Subtitle: "ESP32-DevKitC · TCA9548A I²C Mux · 4× GY-521 (MPU6050) · LED Indicator · LRA Deferred"
     Font: 'JetBrains Mono', 11pt, color #666666
   - Subtitle 2: "I²C0 @400kHz · 100Hz · 128-sample window · Rev 2026-09-01"
     Font: 'JetBrains Mono', 11pt, color #666666
2. Add border bottom: 2px solid #1A1A1A, from x=24 to x=1076

**Expected result:** Title block at top with bold title and monospace subtitle.

**Verification:** Title legible, subtitle readable.

---

### Task 15: Add technical notes

**Steps:**
1. Use **"Text"** tool at bottom (below connection table):
   - Text: "Operating Parameters: VCC 3.3V · I²C 400kHz · Sampling 100Hz (SAMPLE_INTERVAL_US 10000) · Window 128 samples · TCA9548A @0x70 (A0-A2→GND, EN→3.3V) · All GY-521 @0x68 via mux (AD0→GND, channel select via 1<<ch) · Wire length <15cm · 0.1µF decoupling per IC + 10µF bulk · LRA GPIO25/18/19/20 deferred (NC)"
   - Font: 'JetBrains Mono', 11pt, color #666666
   - Border top: 1px solid #CCC, padding-top 12px

**Expected result:** Technical notes at bottom of diagram.

**Verification:** Notes legible, all parameters correct.

---

### Task 16: Save and export

**Steps:**
1. Click **"Save"** button (top toolbar) → Enter project name: `ESP32_4IMU_Tremor_Monitor_Wiring_Diagram`
2. Click **"Export"** button (top toolbar) → Select **"SVG"** format
3. Choose filename: `docs/images/wiring_diagram_4imu_schemeit.svg`
4. Click **"Download"**
5. Also export as **"PNG"** for quick preview: `docs/images/wiring_diagram_4imu_schemeit.png`

**Expected result:** SVG and PNG files downloaded to local machine.

**Verification:** Files open correctly in browser/image viewer.

---

### Task 17: Verify diagram accuracy

**Checklist:**
- [ ] U1 (ESP32) has GPIO21, GPIO22, GPIO2, 3.3V, GND, NC pins labeled
- [ ] U2 (TCA9548A) has @0x70, A0-A2→GND, EN→3.3V labeled
- [ ] U3-U6 (GY-521) have @0x68, AD0→GND, 0.1µF labeled
- [ ] D1 (LED) has GPIO2 → 220Ω → GND labeled
- [ ] SDA21 wire connects U1 GPIO21 → U2 SDA
- [ ] SCL22 wire connects U1 GPIO22 → U2 SCL
- [ ] CH0-CH3 wire pairs connect U2 to U3-U6
- [ ] LED wire connects U1 GPIO2 → D1
- [ ] Power taps connect U1, U2, U3-U6 to 3.3V bus
- [ ] Connection table has 9 rows with correct net names
- [ ] Legend has 4 items matching wire styles
- [ ] Title block has title, subtitle, date
- [ ] Technical notes have all operating parameters
- [ ] Monochrome palette (black/gray/white + blue accent only)
- [ ] Sharp corners on all boxes
- [ ] Orthogonal wire routing (90° angles)

**Verification:** All checklist items pass.

---

## Tests / Validation

This is a manual GUI task — no automated tests. Validation is visual + cross-reference:

1. **Visual inspection:** All components visible, wires connect pin-to-pin, labels legible, no overlapping elements.
2. **Firmware cross-reference:** All pin numbers, addresses, and parameters match `firmware/common/config.py`.
3. **Export verification:** SVG file opens in browser, PNG file opens in image viewer.
4. **Share verification:** If shared via Scheme It link, URL opens correctly in another browser.

---

## Risks, Tradeoffs, and Open Questions

- **Symbol availability:** ESP32 and TCA9548A symbols may not exist in Scheme It library. Mitigation: create custom symbols using built-in symbol editor (Task 3a).
- **Text rendering:** Scheme It may not support custom fonts (JetBrains Mono). Mitigation: use built-in monospace font (Consolas or Courier New).
- **Wire routing:** Manual wire routing may not achieve perfect orthogonal paths. Mitigation: use grid snapping (enable in View → Grid).
- **Canvas size:** Default canvas may be too small for all components. Mitigation: resize canvas in File → Page Setup (set to 1100×520 or larger).
- **No undo for some actions:** Scheme It has limited undo history. Mitigation: save frequently (Ctrl+S).
- **Open:** Should the diagram include a hand anatomy inset? (Not included in this plan — YAGNI, can be added as separate image later.)
- **Open:** Should the diagram include decoupling capacitor symbols? (Not included — described in text only; add symbols if space permits.)

---

## Files Changed

| File | Action |
|------|--------|
| `docs/images/wiring_diagram_4imu_schemeit.svg` | Create new (export from Scheme It) |
| `docs/images/wiring_diagram_4imu_schemeit.png` | Create new (export from Scheme It) |

No existing project files modified.
