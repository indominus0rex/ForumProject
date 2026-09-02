# Plan: Engineering-Datasheet Wiring Diagram

**Created:** 2026-09-01
**Goal:** Create a new HTML/CSS/SVG wiring diagram for the 4-IMU ESP32 tremor monitor in a clean engineering-datasheet style — same topology as the existing diagram but with a more technical, monochrome aesthetic.

---

## Current Context / Assumptions

- **Existing diagram** (`wearable_tremor_wiring_diagram.html`): box-schematic with colored channels (blue/green/yellow/orange), hand inset, yellow notes box, rounded corners, channel-color legend. This is the "visual flair" version.
- **Firmware config** (`firmware/common/config.py`): SDA=GPIO21, SCL=GPIO22, LED=GPIO2, LRA deferred (GPIO25/18/19/20 NC), TCA9548A @0x70, 4x GY-521 @0x68 via mux, I2C0 @400kHz, 100Hz sampling, 128-sample window.
- **Connection reference** (`cad/connections_4imu.csv`): authoritative pin-to-pin mapping.
- **User wants:** cleaner, more technical, less visual flair — engineering-datasheet aesthetic. Same topology, same HTML/CSS/SVG format.

---

## Architecture / Proposed Approach

Single self-contained HTML file with embedded CSS + inline SVG. Monochrome palette (black/white/gray) with a single subtle accent color for net-highlight. Orthogonal box layout (power rails → MCU → mux → sensors) with technical labels: pin numbers, net names, signal specs, operating parameters. Title block, pin table, minimal legend. No hand inset, no colored fills, no decorative elements. Typography: monospace for technical data (pin numbers, net names, addresses), sans-serif for labels.

---

## Step-by-Step Tasks

### Task 1: Create HTML skeleton with title block and monochrome CSS

**File:** `docs/images/wiring_diagram_4imu_datasheet.html`

Create the HTML boilerplate with embedded CSS defining the datasheet aesthetic:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wiring Diagram — 4-IMU ESP32 Tremor Monitor (Datasheet Style)</title>
  <style>
    :root {
      --ink: #1a1a1a;
      --gray: #666;
      --light-gray: #ccc;
      --bg: #ffffff;
      --accent: #2c5282; /* single muted blue for net highlight */
    }
    body {
      font-family: 'Segoe UI', system-ui, sans-serif;
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px;
      background: var(--bg);
      color: var(--ink);
      font-size: 13px;
      line-height: 1.4;
    }
    /* Title block */
    .title-block {
      border-bottom: 2px solid var(--ink);
      padding-bottom: 12px;
      margin-bottom: 20px;
    }
    .title-block h1 {
      margin: 0 0 4px 0;
      font-size: 18px;
      font-weight: 600;
      letter-spacing: 0.3px;
    }
    .title-block .meta {
      font-size: 11px;
      color: var(--gray);
      font-family: 'JetBrains Mono', 'Consolas', monospace;
    }
    /* SVG container */
    .diagram-container {
      border: 1px solid var(--light-gray);
      padding: 16px;
      margin-bottom: 20px;
    }
    svg {
      width: 100%;
      height: auto;
      display: block;
    }
    /* Component boxes — sharp corners, white fill, thin stroke */
    .comp-box {
      fill: #ffffff;
      stroke: var(--ink);
      stroke-width: 1.2;
    }
    .comp-box-muted {
      fill: #fafafa;
      stroke: var(--light-gray);
      stroke-width: 1.0;
      stroke-dasharray: 4 3;
    }
    /* Power buses */
    .bus { stroke-width: 2.5; fill: none; }
    .bus-pwr { stroke: var(--ink); }
    .bus-gnd { stroke: var(--gray); }
    /* Wires */
    .wire { fill: none; stroke-width: 1.3; stroke: var(--ink); }
    .wire-accent { stroke: var(--accent); }
    /* Text */
    .label { font-size: 10px; fill: var(--ink); font-family: 'Segoe UI', sans-serif; }
    .label-mono { font-family: 'JetBrains Mono', 'Consolas', monospace; font-size: 9.5px; fill: var(--ink); }
    .label-net { font-family: 'JetBrains Mono', 'Consolas', monospace; font-size: 8px; fill: var(--accent); font-weight: 600; }
    .label-pin { font-family: 'JetBrains Mono', 'Consolas', monospace; font-size: 8.5px; fill: var(--gray); }
    .comp-title { font-size: 11px; font-weight: 600; fill: var(--ink); }
    /* Tables */
    .data-table {
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
      font-size: 11px;
    }
    .data-table th, .data-table td {
      border: 1px solid var(--light-gray);
      padding: 6px 10px;
      text-align: left;
    }
    .data-table th {
      background: #f5f5f5;
      font-weight: 600;
    }
    .data-table td {
      font-family: 'JetBrains Mono', 'Consolas', monospace;
    }
    /* Legend */
    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      padding: 10px 14px;
      background: #f8f8f8;
      border: 1px solid var(--light-gray);
      font-size: 11px;
      margin-bottom: 16px;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .legend-line {
      width: 20px;
      height: 0;
      border-top: 2px solid var(--ink);
    }
    .legend-line-accent {
      border-top-color: var(--accent);
    }
    /* Notes */
    .notes {
      font-size: 11px;
      color: var(--gray);
      border-top: 1px solid var(--light-gray);
      padding-top: 12px;
    }
  </style>
</head>
<body>
  <!-- Content added in subsequent tasks -->
</body>
</html>
```

**Verification:** Open the file in a browser — should see empty page with no errors.

---

### Task 2: Add title block and metadata

**File:** `docs/images/wiring_diagram_4imu_datasheet.html`

Add inside `<body>`:

```html
  <div class="title-block">
    <h1>Wiring Diagram — 4-IMU ESP32 Tremor Monitor</h1>
    <div class="meta">
      ESP32-DevKitC · TCA9548A I²C Mux · 4× GY-521 (MPU6050) · LED Indicator · LRA Deferred<br>
      I²C0 @400kHz · 100Hz · 128-sample window · Rev 2026-09-01
    </div>
  </div>
```

**Verification:** Browser shows title block with monospace metadata line.

---

### Task 3: Draw power rails (3.3V and GND buses)

**File:** `docs/images/wiring_diagram_4imu_datasheet.html`

Add SVG container with horizontal power buses at bottom:

```html
  <div class="diagram-container">
    <svg viewBox="0 0 1100 520" xmlns="http://www.w3.org/2000/svg">
      <!-- Power buses -->
      <line x1="40" y1="470" x2="1060" y2="470" class="bus bus-pwr"/>
      <line x1="40" y1="490" x2="1060" y2="490" class="bus bus-gnd"/>
      <text x="40" y="462" class="label-mono">3.3V bus (star)</text>
      <text x="40" y="507" class="label-mono">GND bus (star)</text>
      <!-- Decoupling note -->
      <text x="200" y="462" class="label-pin">0.1µF per IC + 10µF bulk</text>
    </svg>
  </div>
```

**Verification:** Browser shows two horizontal lines (black 3.3V, gray GND) with labels.

---

### Task 4: Draw ESP32 box with pin labels

**File:** `docs/images/wiring_diagram_4imu_datasheet.html`

Add inside SVG (before power buses closing):

```html
      <!-- ESP32 -->
      <g transform="translate(120,140)">
        <rect x="0" y="0" width="180" height="160" class="comp-box"/>
        <text x="90" y="16" text-anchor="middle" class="comp-title">U1 · ESP32-DevKitC</text>
        <text x="90" y="28" text-anchor="middle" class="label-mono">I²C0 @400kHz</text>
        <!-- Pins -->
        <text x="10" y="50" class="label-pin">GPIO21 → SDA</text>
        <circle cx="170" cy="47" r="3" fill="var(--ink)"/>
        <text x="10" y="68" class="label-pin">GPIO22 → SCL</text>
        <circle cx="170" cy="65" r="3" fill="var(--ink)"/>
        <text x="10" y="86" class="label-pin">GPIO2  → LED</text>
        <circle cx="170" cy="83" r="3" fill="var(--ink)"/>
        <text x="10" y="104" class="label-pin">3.3V</text>
        <text x="10" y="120" class="label-pin">GND</text>
        <!-- NC box -->
        <rect x="100" y="130" width="74" height="22" class="comp-box-muted"/>
        <text x="137" y="145" text-anchor="middle" class="label-pin">25/18/19/20 NC</text>
      </g>
```

**Verification:** Browser shows ESP32 box with pin labels and NC box.

---

### Task 5: Draw TCA9548A mux box with channel labels

**File:** `docs/images/wiring_diagram_4imu_datasheet.html`

Add after ESP32:

```html
      <!-- TCA9548A -->
      <g transform="translate(400,160)">
        <rect x="0" y="0" width="160" height="130" class="comp-box"/>
        <text x="80" y="16" text-anchor="middle" class="comp-title">U2 · TCA9548A</text>
        <text x="80" y="28" text-anchor="middle" class="label-mono">@0x70 · A0-A2→GND · EN→3.3V</text>
        <!-- Inputs -->
        <text x="10" y="50" class="label-pin">SDA</text>
        <circle cx="6" cy="47" r="2.5" fill="var(--ink)"/>
        <text x="10" y="68" class="label-pin">SCL</text>
        <circle cx="6" cy="65" r="2.5" fill="var(--ink)"/>
        <!-- Channel outputs -->
        <text x="90" y="48" class="label-pin">SD0/SC0 → CH0</text>
        <circle cx="154" cy="45" r="2.5" fill="var(--ink)"/>
        <circle cx="154" cy="55" r="2.5" fill="var(--ink)"/>
        <text x="90" y="68" class="label-pin">SD1/SC1 → CH1</text>
        <circle cx="154" cy="67" r="2.5" fill="var(--ink)"/>
        <circle cx="154" cy="77" r="2.5" fill="var(--ink)"/>
        <text x="90" y="88" class="label-pin">SD2/SC2 → CH2</text>
        <circle cx="154" cy="89" r="2.5" fill="var(--ink)"/>
        <circle cx="154" cy="99" r="2.5" fill="var(--ink)"/>
        <text x="90" y="108" class="label-pin">SD3/SC3 → CH3</text>
        <circle cx="154" cy="111" r="2.5" fill="var(--ink)"/>
        <circle cx="154" cy="121" r="2.5" fill="var(--ink)"/>
      </g>
```

**Verification:** Browser shows mux box with 4 channel pairs.

---

### Task 6: Draw 4 IMU boxes with technical specs

**File:** `docs/images/wiring_diagram_4imu_datasheet.html`

Add after mux:

```html
      <!-- IMU0 -->
      <g transform="translate(680,60)">
        <rect x="0" y="0" width="240" height="52" class="comp-box"/>
        <text x="10" y="16" class="comp-title">U3 · GY-521 (MPU6050) · CH0</text>
        <text x="10" y="30" class="label-mono">@0x68 · AD0→GND · 0.1µF</text>
        <text x="10" y="44" class="label-pin">dorsal wrist proximal · primary</text>
        <circle cx="232" cy="16" r="2.5" fill="var(--ink)"/>
        <circle cx="232" cy="28" r="2.5" fill="var(--ink)"/>
      </g>
      <!-- IMU1 -->
      <g transform="translate(680,120)">
        <rect x="0" y="0" width="240" height="52" class="comp-box"/>
        <text x="10" y="16" class="comp-title">U4 · GY-521 (MPU6050) · CH1</text>
        <text x="10" y="30" class="label-mono">@0x68 · AD0→GND · 0.1µF</text>
        <text x="10" y="44" class="label-pin">thenar volar · thumb base</text>
        <circle cx="232" cy="16" r="2.5" fill="var(--ink)"/>
        <circle cx="232" cy="28" r="2.5" fill="var(--ink)"/>
      </g>
      <!-- IMU2 -->
      <g transform="translate(680,180)">
        <rect x="0" y="0" width="240" height="52" class="comp-box"/>
        <text x="10" y="16" class="comp-title">U5 · GY-521 (MPU6050) · CH2</text>
        <text x="10" y="30" class="label-mono">@0x68 · AD0→GND · 0.1µF</text>
        <text x="10" y="44" class="label-pin">thumb proximal phalanx · 20° tilt · pill 4-6Hz</text>
        <circle cx="232" cy="16" r="2.5" fill="var(--ink)"/>
        <circle cx="232" cy="28" r="2.5" fill="var(--ink)"/>
      </g>
      <!-- IMU3 -->
      <g transform="translate(680,240)">
        <rect x="0" y="0" width="240" height="52" class="comp-box"/>
        <text x="10" y="16" class="comp-title">U6 · GY-521 (MPU6050) · CH3</text>
        <text x="10" y="30" class="label-mono">@0x68 · AD0→GND · 0.1µF</text>
        <text x="10" y="44" class="label-pin">index proximal phalanx · ET 6-8Hz</text>
        <circle cx="232" cy="16" r="2.5" fill="var(--ink)"/>
        <circle cx="232" cy="28" r="2.5" fill="var(--ink)"/>
      </g>
      <!-- LED -->
      <g transform="translate(680,310)">
        <rect x="0" y="0" width="240" height="36" class="comp-box"/>
        <text x="10" y="16" class="comp-title">D1 · LED Indicator</text>
        <text x="10" y="30" class="label-mono">GPIO2 → 220Ω → GND · active high</text>
        <circle cx="232" cy="14" r="2.5" fill="var(--ink)"/>
      </g>
```

**Verification:** Browser shows 4 IMU boxes + LED with reference designators (U3-U6) and specs.

---

### Task 7: Draw wire connections (I2C bus + per-channel pairs)

**File:** `docs/images/wiring_diagram_4imu_datasheet.html`

Add wire paths connecting the boxes:

```html
      <!-- I2C bus: ESP32 → TCA -->
      <path d="M 300 187 L 400 187" class="wire"/>
      <path d="M 300 205 L 400 205" class="wire"/>
      <text x="340" y="183" class="label-net">SDA21</text>
      <text x="340" y="215" class="label-net">SCL22</text>
      <!-- Per-channel pairs: TCA → IMUs -->
      <path d="M 554 205 L 680 76" class="wire"/>
      <path d="M 554 215 L 680 88" class="wire"/>
      <path d="M 554 227 L 680 136" class="wire"/>
      <path d="M 554 237 L 680 148" class="wire"/>
      <path d="M 554 249 L 680 196" class="wire"/>
      <path d="M 554 259 L 680 208" class="wire"/>
      <path d="M 554 271 L 680 256" class="wire"/>
      <path d="M 554 281 L 680 268" class="wire"/>
      <!-- LED wire -->
      <path d="M 300 223 L 400 223 L 400 30 L 680 30 L 680 324" class="wire"/>
      <!-- Power taps (dashed vertical drops) -->
      <path d="M 160 300 L 160 470" class="wire" stroke-dasharray="3 3"/>
      <path d="M 480 290 L 480 470" class="wire" stroke-dasharray="3 3"/>
      <path d="M 800 346 L 800 470" class="wire" stroke-dasharray="3 3"/>
```

**Verification:** Browser shows wires connecting all components with net labels.

---

### Task 8: Add connection/pin table

**File:** `docs/images/wiring_diagram_4imu_datasheet.html`

Add after `</svg></div>`:

```html
  <table class="data-table">
    <thead>
      <tr><th>Net</th><th>Source</th><th>Destination</th><th>Notes</th></tr>
    </thead>
    <tbody>
      <tr><td>SDA21</td><td>U1 GPIO21</td><td>U2 SDA</td><td>I²C0 data, 400kHz</td></tr>
      <tr><td>SCL22</td><td>U1 GPIO22</td><td>U2 SCL</td><td>I²C0 clock, 400kHz</td></tr>
      <tr><td>CH0</td><td>U2 SD0/SC0</td><td>U3 SDA/SCL</td><td>dorsal wrist</td></tr>
      <tr><td>CH1</td><td>U2 SD1/SC1</td><td>U4 SDA/SCL</td><td>thenar volar</td></tr>
      <tr><td>CH2</td><td>U2 SD2/SC2</td><td>U5 SDA/SCL</td><td>thumb phalanx</td></tr>
      <tr><td>CH3</td><td>U2 SD3/SC3</td><td>U6 SDA/SCL</td><td>index phalanx</td></tr>
      <tr><td>LED</td><td>U1 GPIO2</td><td>D1 anode</td><td>220Ω → GND</td></tr>
      <tr><td>3.3V</td><td>U1 3.3V</td><td>U2-U6 VCC</td><td>star topology</td></tr>
      <tr><td>GND</td><td>U1 GND</td><td>U2-U6 GND</td><td>star topology</td></tr>
    </tbody>
  </table>
```

**Verification:** Browser shows 9-row connection table.

---

### Task 9: Add legend and technical notes

**File:** `docs/images/wiring_diagram_4imu_datasheet.html`

Add after the table:

```html
  <div class="legend">
    <div class="legend-item"><span class="legend-line"></span> Signal / power</div>
    <div class="legend-item"><span class="legend-line" style="border-style: dashed;"></span> Power tap (schematic)</div>
    <div class="legend-item"><span class="legend-line legend-line-accent"></span> Net name</div>
    <div class="legend-item"><span style="display:inline-block;width:12px;height:12px;border:1px dashed #ccc;background:#fafafa;"></span> NC / deferred</div>
  </div>
  <div class="notes">
    <strong>Operating Parameters:</strong> VCC 3.3V · I²C 400kHz · Sampling 100Hz (SAMPLE_INTERVAL_US 10000) · Window 128 samples · TCA9548A @0x70 (A0-A2→GND, EN→3.3V) · All GY-521 @0x68 via mux (AD0→GND, channel select via 1&lt;&lt;ch) · Wire length &lt;15cm · 0.1µF decoupling per IC + 10µF bulk · LRA GPIO25/18/19/20 deferred (NC)
  </div>
```

**Verification:** Browser shows legend and notes section.

---

### Task 10: Verify against firmware config

**File:** `docs/images/wiring_diagram_4imu_datasheet.html`

Cross-check all pin assignments against `firmware/common/config.py`:
- SDA = GPIO21 ✓
- SCL = GPIO22 ✓
- LED = GPIO2 ✓
- LRA pins = 25/18/19/20 NC ✓
- TCA9548A @0x70 ✓
- 4× GY-521 @0x68 ✓
- I2C0 @400kHz ✓
- 100Hz sampling ✓
- 128-sample window ✓

**Verification:** All values match firmware config. No discrepancies.

---

## Tests / Validation

This is a static HTML/SVG deliverable — no unit tests. Validation is visual + cross-reference:

1. **Open in browser:** `start docs/images/wiring_diagram_4imu_datasheet.html` — renders without errors, all boxes visible, wires connect correctly.
2. **Cross-reference firmware:** Every pin number, address, and parameter matches `firmware/common/config.py`.
3. **Cross-reference connections:** Every net in the table matches `cad/connections_4imu.csv`.
4. **Style check:** No colored fills, no rounded corners (or minimal), no hand inset, no decorative elements — monochrome + single accent.

---

## Risks, Tradeoffs, and Open Questions

- **Monochrome wires lose channel color-coding** — mitigated by net labels and the connection table. If channel differentiation is needed, a subtle line-style variation (solid/dashed/dotted) could be added.
- **No anatomical inset** — the existing hand illustration is removed. If the user later wants it, it can be added as a small inset (≤15% canvas) per the wiring skill style guide.
- **Single accent color** — chosen as muted blue (`#2c5282`). Could be changed to match any future project branding.
- **Open:** Should the diagram include a revision history block? (Not included now — YAGNI.)
- **Open:** Should the IMU boxes include axis orientation indicators? (Not included — adds visual clutter, conflicts with "minimalist" goal.)

---

## Files Changed

| File | Action |
|------|--------|
| `docs/images/wiring_diagram_4imu_datasheet.html` | Create new |

No existing files modified.
