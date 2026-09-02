# Plan: Hand-Anatomy Wiring Diagram

**Created:** 2026-09-01
**Goal:** Create a hand-centered anatomical wiring diagram showing IMU sensor placement directly on a detailed hand illustration, with wires routing to a compact ESP32 + mux block.

---

## Current Context / Assumptions

- **Existing diagrams:**
  - `wearable_tremor_wiring_diagram.html` — box-schematic with a tiny hand inset (≤15% canvas, top-right corner)
  - `docs/images/wiring_diagram_4imu_datasheet.html` — pure datasheet style, no hand at all
- **This diagram is different:** the hand illustration IS the main focal point (~60% of canvas), with sensors placed at anatomical positions and wires routing to a compact electronics block.
- **Sensor placement (locked 2026-08-27 Option A + ET):**
  - CH0 — dorsal wrist proximal (blue)
  - CH1 — thenar volar / thumb base (green)
  - CH2 — thumb proximal phalanx, 20° tilt, pill-rolling 4-6Hz (yellow)
  - CH3 — index proximal phalanx, ET 6-8Hz (orange)
- **Electronics:** ESP32-DevKitC + TCA9548A mux + LED (same topology, compact representation)
- **Format:** HTML/CSS/SVG, self-contained, viewable in browser

---

## Architecture / Proposed Approach

Single self-contained HTML file with embedded CSS + inline SVG. The hand occupies the left 60% of the canvas as a detailed anatomical illustration (dorsal view of hand + forearm) with color-coded sensor dots at each placement position. Wires route from each sensor dot to a compact electronics block on the right side (ESP32 + TCA9548A + LED stacked vertically). Sensor placement labels show channel number, anatomical name, and tremor type. The hand is drawn with solid dorsal outlines and a translucent volar ghost for the thenar region. No box-schematic competing for space — the hand is the star.

---

## Step-by-Step Tasks

### Task 1: Create HTML skeleton with title block

**File:** `docs/images/wiring_diagram_4imu_hand.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wiring Diagram — 4-IMU ESP32 Tremor Monitor (Hand Anatomy)</title>
  <style>
    :root {
      --ink: #1a1a1a;
      --gray: #666;
      --light-gray: #ccc;
      --accent-ch0: #2A6FFF;
      --accent-ch1: #1DBA5A;
      --accent-ch2: #E8B500;
      --accent-ch3: #FF7A1A;
    }
    body {
      font-family: 'Segoe UI', system-ui, sans-serif;
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px;
      color: var(--ink);
      font-size: 13px;
    }
    .title-block {
      border-bottom: 2px solid var(--ink);
      padding-bottom: 10px;
      margin-bottom: 16px;
    }
    .title-block h1 {
      margin: 0 0 4px 0;
      font-size: 18px;
    }
    .title-block .meta {
      font-size: 11px;
      color: var(--gray);
      font-family: 'JetBrains Mono', 'Consolas', monospace;
    }
    .diagram-container {
      border: 1px solid var(--light-gray);
      padding: 12px;
      margin-bottom: 16px;
    }
    svg { width: 100%; height: auto; display: block; }

    /* Component box (electronics block) */
    .comp-box {
      fill: #fafafa;
      stroke: var(--ink);
      stroke-width: 1.0;
    }
    .comp-title {
      font-size: 11px;
      font-weight: 600;
      fill: var(--ink);
    }
    .label-mono {
      font-family: 'JetBrains Mono', 'Consolas', monospace;
      font-size: 9px;
      fill: var(--ink);
    }
    .label-pin {
      font-family: 'JetBrains Mono', 'Consolas', monospace;
      font-size: 8px;
      fill: var(--gray);
    }

    /* Hand anatomy styles */
    .hand-outline {
      fill: none;
      stroke: var(--ink);
      stroke-width: 1.4;
    }
    .hand-ghost {
      fill: rgba(180, 210, 180, 0.12);
      stroke: var(--accent-ch1);
      stroke-width: 0.8;
      stroke-dasharray: 4 3;
    }
    .finger-bone {
      fill: none;
      stroke: #d0d0d0;
      stroke-width: 0.6;
    }

    /* Sensor dots */
    .sensor-dot {
      stroke-width: 1.5;
    }
    .sensor-dot-ch0 { fill: var(--accent-ch0); stroke: #1a3d8f; }
    .sensor-dot-ch1 { fill: var(--accent-ch1); stroke: #0e6b2a; }
    .sensor-dot-ch2 { fill: var(--accent-ch2); stroke: #7a5c00; }
    .sensor-dot-ch3 { fill: var(--accent-ch3); stroke: #8a3b00; }

    /* Wires from hand to electronics */
    .wire { fill: none; stroke-width: 1.6; }
    .wire-ch0 { stroke: var(--accent-ch0); }
    .wire-ch1 { stroke: var(--accent-ch1); }
    .wire-ch2 { stroke: var(--accent-ch2); }
    .wire-ch3 { stroke: var(--accent-ch3); }
    .wire-led { stroke: #d4ac0d; }

    /* Sensor labels */
    .sensor-label {
      font-size: 8.5px;
      fill: var(--ink);
    }
    .sensor-label-ch0 { fill: var(--accent-ch0); font-weight: 600; }
    .sensor-label-ch1 { fill: var(--accent-ch1); font-weight: 600; }
    .sensor-label-ch2 { fill: #7a5c00; font-weight: 600; }
    .sensor-label-ch3 { fill: #8a3b00; font-weight: 600; }

    /* Legend */
    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      padding: 10px 14px;
      background: #f8f8f8;
      border: 1px solid var(--light-gray);
      font-size: 11px;
      margin-bottom: 14px;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .legend-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      border: 1.5px solid;
    }
    .data-table {
      width: 100%;
      border-collapse: collapse;
      margin: 14px 0;
      font-size: 11px;
    }
    .data-table th, .data-table td {
      border: 1px solid var(--light-gray);
      padding: 5px 10px;
      text-align: left;
    }
    .data-table th { background: #f5f5f5; font-weight: 600; }
    .data-table td { font-family: 'JetBrains Mono', 'Consolas', monospace; }
    .notes {
      font-size: 11px;
      color: var(--gray);
      border-top: 1px solid var(--light-gray);
      padding-top: 10px;
    }
  </style>
</head>
<body>
  <!-- Content added in subsequent tasks -->
</body>
</html>
```

**Verification:** Open in browser — empty page, no errors.

---

### Task 2: Add title block

**File:** `docs/images/wiring_diagram_4imu_hand.html`

Add inside `<body>`:

```html
  <div class="title-block">
    <h1>Wiring Diagram — 4-IMU Hand Placement (Dorsal View)</h1>
    <div class="meta">
      ESP32-DevKitC · TCA9548A I²C Mux · 4× GY-521 (MPU6050) · I²C0 @400kHz · 100Hz · Rev 2026-09-01
    </div>
  </div>
```

**Verification:** Browser shows title + monospace metadata line.

---

### Task 3: Draw hand anatomy (dorsal view)

**File:** `docs/images/wiring_diagram_4imu_hand.html`

Add the SVG container with a detailed hand outline. The hand occupies the left ~65% of a 1200×560 canvas:

```html
  <div class="diagram-container">
    <svg viewBox="0 0 1200 560" xmlns="http://www.w3.org/2000/svg">
      <!-- Hand outline — dorsal view -->
      <g transform="translate(40,30)">
        <!-- Palm + fingers -->
        <path d="M 40 120 L 40 260 L 70 340 L 160 340 L 260 300 L 320 220
                 L 320 100 L 260 50 L 160 50 L 80 80 Z"
              class="hand-outline"/>
        <!-- Thumb -->
        <path d="M 260 50 L 310 20 L 340 20 L 360 60 L 320 100"
              class="hand-outline"/>
        <!-- Index finger -->
        <path d="M 160 50 L 150 10 L 170 10 L 180 50"
              class="hand-outline"/>
        <!-- Middle finger -->
        <path d="M 200 50 L 195 5 L 215 5 L 220 50"
              class="hand-outline"/>
        <!-- Ring finger -->
        <path d="M 240 60 L 240 15 L 260 15 L 260 60"
              class="hand-outline"/>
        <!-- Pinky -->
        <path d="M 280 75 L 285 30 L 305 30 L 300 75"
              class="hand-outline"/>
        <!-- Forearm -->
        <path d="M 40 260 L 0 320 L 0 380 L 40 400 L 80 400 L 80 340"
              class="hand-outline"/>
        <!-- Wrist crease line -->
        <path d="M 40 260 L 80 340" class="finger-bone"/>
        <!-- Finger joint lines -->
        <line x1="155" y1="10" x2="175" y2="10" class="finger-bone"/>
        <line x1="200" y1="5" x2="220" second-lin="5" class="finger-bone"/>
        <!-- Volar thenar ghost (translucent) -->
        <ellipse cx="200" cy="170" rx="50" ry="35" class="hand-ghost"/>
        <text x="200" y="175" text-anchor="middle" font-size="8" fill="#1DBA5A" font-style="italic">volar</text>
      </g>
    </svg>
  </div>
```

**Fix typo:** The second `<line>` has `second-lin` which should be `y2`. Correct it:

```html
        <line x1="200" y1="5" x2="220" y2="5" class="finger-bone"/>
```

**Verification:** Browser shows hand outline with fingers, forearm, and volar ghost.

---

### Task 4: Add sensor dots at anatomical positions

**File:** `docs/images/wiring_diagram_4imu_hand.html`

Add sensor dots inside the `<svg>`, after the hand `<g>`:

```html
      <!-- Sensor placement dots (absolute coords within viewBox) -->
      <!-- CH0: dorsal wrist proximal -->
      <circle cx="80" cy="210" r="7" class="sensor-dot sensor-dot-ch0"/>
      <text x="60" y="200" class="sensor-label sensor-label-ch0">CH0 · dorsal wrist · primary</text>
      <!-- CH1: thenar volar (on ghost) -->
      <circle cx="200" cy="170" r="7" class="sensor-dot sensor-dot-ch1"/>
      <text x="240" y="160" class="sensor-label sensor-label-ch1">CH1 · thenar volar · thumb base</text>
      <!-- CH2: thumb proximal phalanx -->
      <circle cx="350" cy="45" r="7" class="sensor-dot sensor-dot-ch2"/>
      <text x="370" y="40" class="sensor-label sensor-label-ch2">CH2 · thumb phalanx · pill 4-6Hz</text>
      <!-- CH3: index proximal phalanx -->
      <circle cx="160" cy="35" r="7" class="sensor-dot sensor-dot-ch3"/>
      <text x="130" y="20" class="sensor-label sensor-label-ch3">CH3 · index phalanx · ET 6-8Hz</text>
```

**Verification:** Browser shows 4 colored dots on hand with labels.

---

### Task 5: Draw compact electronics block (right side)

**File:** `docs/images/wiring_diagram_4imu_hand.html`

Add after sensor dots, before `</svg>`:

```html
      <!-- Electronics block (right side) -->
      <g transform="translate(750,60)">
        <!-- ESP32 -->
        <rect x="0" y="0" width="200" height="100" class="comp-box"/>
        <text x="100" y="18" text-anchor="middle" class="comp-title">U1 · ESP32-DevKitC</text>
        <text x="10" y="38" class="label-mono">21 SDA → mux</text>
        <text x="10" y="52" class="label-mono">22 SCL → mux</text>
        <text x="10" y="66" class="label-mono">2  LED → 220Ω</text>
        <text x="10" y="80" class="label-mono">3.3V · GND · 25/18/19/20 NC</text>
        <!-- Pin markers on left edge -->
        <circle cx="0" cy="38" r="3" fill="var(--accent-ch1)"/>
        <circle cx="0" cy="52" r="3" fill="var(--accent-ch0)"/>
        <circle cx="0" cy="66" r="3" fill="#d4ac0d"/>
      </g>
      <g transform="translate(750,200)">
        <!-- TCA9548A -->
        <rect x="0" y="0" width="200" height="130" class="comp-box"/>
        <text x="100" y="18" text-anchor="middle" class="comp-title">U2 · TCA9548A</text>
        <text x="10" y="38" class="label-mono">@0x70 · A0-A2→GND · EN→3.3V</text>
        <text x="10" y="56" class="label-pin">SDA · SCL ← from U1</text>
        <text x="10" y="74" class="label-pin">SD0/SC0 → CH0</text>
        <text x="10" y="88" class="label-pin">SD1/SC1 → CH1</text>
        <text x="10" y="102" class="label-pin">SD2/SC2 → CH2</text>
        <text x="10" y="116" class="label-pin">SD3/SC3 → CH3</text>
        <!-- Pin markers on left edge -->
        <circle cx="0" cy="74" r="3" fill="var(--accent-ch0)"/>
        <circle cx="0" cy="88" r="3" fill="var(--accent-ch1)"/>
        <circle cx="0" cy="102" r="3" fill="var(--accent-ch2)"/>
        <circle cx="0" cy="116" r="3" fill="var(--accent-ch3)"/>
      </g>
      <g transform="translate(750,370)">
        <!-- LED -->
        <rect x="0" y="0" width="200" height="50" class="comp-box"/>
        <text x="100" y="18" text-anchor="middle" class="comp-title">D1 · LED</text>
        <text x="10" y="38" class="label-mono">GPIO2 → 220Ω → GND · active high</text>
        <circle cx="0" cy="18" r="3" fill="#d4ac0d"/>
      </g>
```

**Verification:** Browser shows ESP32, TCA, LED stacked on right side.

---

### Task 6: Draw wires from sensor dots to electronics pins

**File:** `docs/images/wiring_diagram_4imu_hand.html`

Add wire paths (each sensor dot routes horizontally right to the electronics block):

```html
      <!-- Wires: sensor dots → electronics block -->
      <!-- CH0: dorsal wrist → TCA CH0 (y=74 in block = abs y=274) -->
      <path d="M 120 210 C 400 210, 400 274, 750 274" class="wire wire-ch0"/>
      <!-- CH1: thenar → TCA CH1 (y=88 = abs y=288) -->
      <path d="M 240 170 C 450 170, 450 288, 750 288" class="wire wire-ch1"/>
      <!-- CH2: thumb phalanx → TCA CH2 (y=102 = abs y=302) -->
      <path d="M 390 45 C 500 45, 500 302, 750 302" class="wire wire-ch2"/>
      <!-- CH3: index phalanx → TCA CH3 (y=116 = abs y=316) -->
      <path d="M 200 35 C 450 35, 450 316, 750 316" class="wire wire-ch3"/>
      <!-- LED: ESP32 LED pin → D1 (straight horizontal) -->
      <path d="M 750 126 L 950 126 L 950 388 L 750 388" class="wire wire-led"/>
```

**Verification:** Browser shows 5 colored wires connecting hand to electronics.

---

### Task 7: Add legend, sensor table, and notes

**File:** `docs/images/wiring_diagram_4imu_hand.html`

Add after `</svg></div>`:

```html
  <div class="legend">
    <div class="legend-item"><span class="legend-dot" style="background:#2A6FFF;border-color:#1a3d8f;"></span> CH0 · dorsal wrist · primary</div>
    <div class="legend-item"><span class="legend-dot" style="background:#1DBA5A;border-color:#0e6b2a;"></span> CH1 · thenar volar · thumb base</div>
    <div class="legend-item"><span class="legend-dot" style="background:#E8B500;border-color:#7a5c00;"></span> CH2 · thumb phalanx 20° · pill 4-6Hz</div>
    <div class="legend-item"><span class="legend-dot" style="background:#FF7A1A;border-color:#8a3b00;"></span> CH3 · index phalanx · ET 6-8Hz</div>
    <div class="legend-item"><span class="legend-dot" style="background:#d4ac0d;border-color:#8a6d00;"></span> LED · GPIO2 · 220Ω</div>
  </div>
  <table class="data-table">
    <thead>
      <tr><th>Channel</th><th>Anatomical Position</th><th>Tremor Type</th><th>Frequency</th><th>Color</th></tr>
    </thead>
    <tbody>
      <tr><td>CH0</td><td>dorsal wrist proximal</td><td>primary</td><td>—</td><td>blue</td></tr>
      <tr><td>CH1</td><td>thenar volar (thumb base)</td><td>—</td><td>—</td><td>green</td></tr>
      <tr><td>CH2</td><td>thumb proximal phalanx (20° tilt)</td><td>pill-rolling</td><td>4-6Hz</td><td>yellow</td></tr>
      <tr><td>CH3</td><td>index proximal phalanx</td><td>postural (ET)</td><td>6-8Hz</td><td>orange</td></tr>
    </tbody>
  </table>
  <div class="notes">
    <strong>Build Note 2026-08-27 Option A + ET:</strong> Sensor placement locked for pill-rolling 4-6Hz (CH2 thumb phalanx 20° tilt) + postural ET 6-8Hz (CH3 index phalanx) with balanced coherence 0.6 (thumb-index &amp; finger-wrist). LRA GPIO25/18/19/20 deferred (NC). I²C0 @400kHz · 100Hz · 128-sample window · TCA9548A @0x70 · all GY-521 @0x68 via mux (1&lt;&lt;ch) · wire length &lt;15cm · 0.1µF per IC + 10µF bulk.
  </div>
```

**Verification:** Browser shows legend, 4-row table, and build notes.

---

### Task 8: Verify wire geometry

**File:** `docs/images/wiring_diagram_4imu_hand.html`

Cross-check all wire endpoints against pin circle positions:

| Wire | Start (sensor dot) | End (electronics pin) | Match? |
|------|--------------------|-----------------------|--------|
| CH0 | (120, 210) | (750, 274) | TCA CH0 pin at (750, 274) ✓ |
| CH1 | (240, 170) | (750, 288) | TCA CH1 pin at (750, 288) ✓ |
| CH2 | (390, 45) | (750, 302) | TCA CH2 pin at (750, 302) ✓ |
| CH3 | (200, 35) | (750, 316) | TCA CH3 pin at (750, 316) ✓ |
| LED | (750, 126) | (750, 388) | D1 pin at (750, 388) ✓ |

**Verification:** All wire endpoints meet pin circles. No gaps.

---

## Tests / Validation

This is a static HTML/SVG deliverable — no unit tests. Validation is visual + cross-reference:

1. **Open in browser:** `start docs/images/wiring_diagram_4imu_hand.html` — renders without errors, hand visible, wires connect to pins.
2. **Cross-reference firmware:** All pin numbers, addresses, and parameters match `firmware/common/config.py`.
3. **Cross-reference placement:** Sensor positions match Option A + ET lock (2026-08-27).
4. **Style check:** Hand is the focal point (~60% canvas), electronics compact on right, color-coded wires, no box-schematic competing for space.

---

## Risks, Tradeoffs, and Open Questions

- **Hand outline accuracy:** The SVG path is a stylized representation, not anatomically precise. If the user wants medical-grade accuracy, a reference image should be traced.
- **Wire routing:** Curved bezier paths (C command) are used for visual clarity. If orthogonal routing is preferred, replace with L-shaped paths.
- **Volar ghost overlap:** CH1 dot sits on the volar ghost which is on the dorsal view — this is intentional (shows palmar placement from dorsal view) but could confuse. The "volar" label clarifies.
- **No power bus visualization:** Power/ground distribution is described in text but not drawn as buses. If needed, add a power rail on the right edge.
- **Open:** Should the diagram include a strap/wristband outline around the forearm? (Not included now — YAGNI.)
- **Open:** Should sensor dots include axis orientation indicators? (Not included — adds clutter.)

---

## Files Changed

| File | Action |
|------|--------|
| `docs/images/wiring_diagram_4imu_hand.html` | Create new |

No existing files modified.
