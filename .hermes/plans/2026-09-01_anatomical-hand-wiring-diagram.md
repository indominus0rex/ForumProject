# Plan: Anatomically Detailed Hand Wiring Diagram

**Created:** 2026-09-01
**Goal:** Create a hand-centered wiring diagram with anatomically detailed illustration — bones, muscles, tendons, and skin layers — showing precise IMU sensor placement relative to underlying anatomy.

---

## Current Context / Assumptions

- **Existing plan:** `.hermes/plans/2026-09-01_4imu-hand-wiring-diagram.md` — simple stylized hand outline
- **This plan pushes further:** Detailed anatomical illustration with skeletal structure, muscle groups, tendon lines, and skin layers — not just a flat outline
- **Anatomical layers (bottom to top):**
  1. **Bone layer:** Metacarpals, phalanges, radius/ulna, carpal bones
  2. **Muscle layer:** Thenar eminence, hypothenar eminence, interossei, lumbricals
  3. **Tendon layer:** Extensor digitorum, extensor pollicis longus/brevis, flexor tendons
  4. **Skin layer:** Outer surface with crease lines, fingerprints, nail beds
- **Sensor placement (locked 2026-08-27 Option A + ET):**
  - CH0 — dorsal wrist proximal (over radius/ulna junction)
  - CH1 — thenar volar (thenar eminence muscle group)
  - CH2 — thumb proximal phalanx (over proximal phalanx bone)
  - CH3 — index proximal phalanx (over proximal phalanx bone)
- **Format:** HTML/CSS/SVG, self-contained, viewable in browser

---

## Architecture / Proposed Approach

Single self-contained HTML file with embedded CSS + inline SVG. The hand illustration uses a **layered approach** — each anatomical system (bones, muscles, tendons, skin) is a separate SVG `<g>` group with distinct visual styling. Bones are drawn as precise geometric shapes with proper proportions. Muscle groups use translucent fills with subtle gradients. Tendon lines are thin curved paths. The skin layer is the outermost outline with surface detail (creases, nails, fingerprints). Sensor dots are placed at anatomically correct positions relative to the underlying structures. A **layer toggle** (checkboxes) allows showing/hiding each anatomical system. Electronics block remains compact on the right.

---

## Step-by-Step Tasks

### Task 1: Create HTML skeleton with layer toggle controls

**File:** `docs/images/wiring_diagram_4imu_hand_detailed.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wiring Diagram — 4-IMU ESP32 Tremor Monitor (Anatomical Detail)</title>
  <style>
    :root {
      --ink: #1a1a1a;
      --gray: #666;
      --light-gray: #ccc;
      --accent-ch0: #2A6FFF;
      --accent-ch1: #1DBA5A;
      --accent-ch2: #E8B500;
      --accent-ch3: #FF7A1A;
      --bone-color: #f5e6d3;
      --bone-stroke: #c9a87c;
      --muscle-color: rgba(200, 120, 100, 0.25);
      --muscle-stroke: #8b4513;
      --tendon-color: #d4a574;
      --skin-color: #f5d5c8;
      --skin-stroke: #8b6f5e;
    }
    body {
      font-family: 'Segoe UI', system-ui, sans-serif;
      max-width: 1300px;
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
    .title-block h1 { margin: 0 0 4px 0; font-size: 18px; }
    .title-block .meta {
      font-size: 11px;
      color: var(--gray);
      font-family: 'JetBrains Mono', 'Consolas', monospace;
    }
    .controls {
      display: flex;
      gap: 16px;
      padding: 10px 14px;
      background: #f5f5f5;
      border: 1px solid var(--light-gray);
      margin-bottom: 12px;
      font-size: 12px;
    }
    .controls label {
      display: flex;
      align-items: center;
      gap: 5px;
      cursor: pointer;
    }
    .diagram-container {
      border: 1px solid var(--light-gray);
      padding: 12px;
      margin-bottom: 16px;
    }
    svg { width: 100%; height: auto; display: block; }

    /* Anatomical layer styles */
    .layer-bone { fill: var(--bone-color); stroke: var(--bone-stroke); stroke-width: 1.0; }
    .layer-muscle { fill: var(--muscle-color); stroke: var(--muscle-stroke); stroke-width: 0.6; stroke-dasharray: 3 2; }
    .layer-tendon { fill: none; stroke: var(--tendon-color); stroke-width: 1.2; }
    .layer-skin { fill: none; stroke: var(--skin-stroke); stroke-width: 1.6; }
    .layer-skin-fill { fill: var(--skin-color); fill-opacity: 0.15; stroke: var(--skin-stroke); stroke-width: 1.4; }
    .bone-joint { fill: none; stroke: var(--bone-stroke); stroke-width: 0.5; stroke-dasharray: 2 2; }
    .crease-line { fill: none; stroke: var(--skin-stroke); stroke-width: 0.4; opacity: 0.5; }
    .nail-shape { fill: #f0d0b0; stroke: var(--skin-stroke); stroke-width: 0.6; }

    /* Sensor dots */
    .sensor-dot { stroke-width: 2; }
    .sensor-dot-ch0 { fill: var(--accent-ch0); stroke: #1a3d8f; }
    .sensor-dot-ch1 { fill: var(--accent-ch1); stroke: #0e6b2a; }
    .sensor-dot-ch2 { fill: var(--accent-ch2); stroke: #7a5c00; }
    .sensor-dot-ch3 { fill: var(--accent-ch3); stroke: #8a3b00; }

    /* Wires */
    .wire { fill: none; stroke-width: 1.6; }
    .wire-ch0 { stroke: var(--accent-ch0); }
    .wire-ch1 { stroke: var(--accent-ch1); }
    .wire-ch2 { stroke: var(--accent-ch2); }
    .wire-ch3 { stroke: var(--accent-ch3); }
    .wire-led { stroke: #d4ac0d; }

    /* Electronics */
    .comp-box { fill: #fafafa; stroke: var(--ink); stroke-width: 1.0; }
    .comp-title { font-size: 11px; font-weight: 600; fill: var(--ink); }
    .label-mono { font-family: 'JetBrains Mono', 'Consolas', monospace; font-size: 9px; fill: var(--ink); }
    .label-pin { font-family: 'JetBrains Mono', 'Consolas', monospace; font-size: 8px; fill: var(--gray); }

    /* Labels */
    .sensor-label { font-size: 8.5px; fill: var(--ink); }
    .sensor-label-ch0 { fill: var(--accent-ch0); font-weight: 600; }
    .sensor-label-ch1 { fill: var(--accent-ch1); font-weight: 600; }
    .sensor-label-ch2 { fill: #7a5c00; font-weight: 600; }
    .sensor-label-ch3 { fill: #8a3b00; font-weight: 600; }
    .anatomy-label { font-size: 7px; fill: var(--gray); font-style: italic; }

    /* Legend */
    .legend { display: flex; flex-wrap: wrap; gap: 12px; padding: 10px 14px; background: #f8f8f8; border: 1px solid var(--light-gray); font-size: 11px; margin-bottom: 14px; }
    .legend-item { display: flex; align-items: center; gap: 6px; }
    .legend-dot { width: 10px; height: 10px; border-radius: 50%; border: 1.5px solid; }
    .legend-swatch { width: 14px; height: 8px; border: 1px solid; }

    .data-table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 11px; }
    .data-table th, .data-table td { border: 1px solid var(--light-gray); padding: 5px 10px; text-align: left; }
    .data-table th { background: #f5f5f5; font-weight: 600; }
    .data-table td { font-family: 'JetBrains Mono', 'Consolas', monospace; }
    .notes { font-size: 11px; color: var(--gray); border-top: 1px solid var(--light-gray); padding-top: 10px; }

    /* Layer visibility toggles */
    .layer-hidden { display: none; }
  </style>
</head>
<body>
  <div class="title-block">
    <h1>Wiring Diagram — 4-IMU Hand Placement (Anatomical Detail)</h1>
    <div class="meta">
      ESP32-DevKitC · TCA9548A I²C Mux · 4× GY-521 (MPU6050) · I²C0 @400kHz · 100Hz · Rev 2026-09-01
    </div>
  </div>

  <div class="controls">
    <label><input type="checkbox" id="toggle-bone" checked> Bones</label>
    <label><input type="checkbox" id="toggle-muscle" checked> Muscles</label>
    <label><input type="checkbox" id="toggle-tendon" checked> Tendons</label>
    <label><input type="checkbox" id="toggle-skin" checked> Skin</label>
    <label><input type="checkbox" id="toggle-labels" checked> Labels</label>
  </div>

  <div class="diagram-container">
    <svg viewBox="0 0 1300 600" xmlns="http://www.w3.org/2000/svg">
      <!-- Content added in subsequent tasks -->
    </svg>
  </div>

  <script>
    // Layer toggle functionality
    document.querySelectorAll('.controls input').forEach(toggle => {
      toggle.addEventListener('change', (e) => {
        const layer = e.target.id.replace('toggle-', '');
        const elements = document.querySelectorAll(`.layer-${layer}`);
        elements.forEach(el => {
          el.classList.toggle('layer-hidden', !e.target.checked);
        });
      });
    });
  </script>
</body>
</html>
```

**Verification:** Browser shows title block + 5 checkboxes. SVG is empty but checkboxes work (no errors in console).

---

### Task 2: Draw bone layer (skeletal structure)

**File:** `docs/images/wiring_diagram_4imu_hand_detailed.html`

Add inside `<svg>`, before `</svg>`:

```html
      <!-- BONE LAYER (deepest) -->
      <g class="layer-bone" id="layer-bone">
        <!-- Radius and Ulna (forearm) -->
        <ellipse cx="60" cy="380" rx="18" ry="40" transform="rotate(-5, 60, 380)"/>
        <ellipse cx="90" cy="385" rx="16" ry="38" transform="rotate(5, 90, 385)"/>
        <!-- Carpal bones (wrist cluster) -->
        <ellipse cx="110" cy="310" rx="12" ry="10"/>
        <ellipse cx="130" cy="305" rx="10" ry="9"/>
        <ellipse cx="145" cy="315" rx="11" ry="10"/>
        <ellipse cx="125" cy="325" rx="10" ry="9"/>
        <!-- Metacarpals (palm) -->
        <rect x="130" y="180" width="14" height="130" rx="5" transform="rotate(-5, 137, 245)"/>
        <rect x="150" y="160" width="14" height="150" rx="5"/>
        <rect x="170" y="155" width="14" height="155" rx="5"/>
        <rect x="190" y="160" width="14" height="150" rx="5" transform="rotate(5, 197, 235)"/>
        <rect x="210" y="175" width="12" height="130" rx="4" transform="rotate(12, 216, 240)"/>
        <!-- Thumb metacarpal -->
        <rect x="230" y="200" width="14" height="80" rx="5" transform="rotate(45, 237, 240)"/>
        <!-- Phalanges (fingers) -->
        <!-- Index proximal -->
        <rect x="150" y="100" width="12" height="60" rx="4"/>
        <!-- Index middle -->
        <rect x="152" y="45" width="11" height="55" rx="4"/>
        <!-- Middle proximal -->
        <rect x="170" y="95" width="12" height="65" rx="4"/>
        <!-- Middle middle -->
        <rect x="172" y="38" width="11" height="58" rx="4"/>
        <!-- Ring proximal -->
        <rect x="190" y="100" width="12" height="60" rx="4"/>
        <!-- Ring middle -->
        <rect x="192" y="48" width="11" height="52" rx="4"/>
        <!-- Pinky proximal -->
        <rect x="210" y="110" width="11" height="50" rx="3"/>
        <!-- Pinky middle -->
        <rect x="212" y="65" width="10" height="45" rx="3"/>
        <!-- Thumb proximal phalanx -->
        <rect x="260" y="145" width="12" height="55" rx="4" transform="rotate(50, 266, 172)"/>
        <!-- Thumb distal phalanx -->
        <rect x="285" y="105" width="11" height="45" rx="4" transform="rotate(55, 290, 127)"/>
        <!-- Joint markers -->
        <circle cx="137" cy="180" r="4" class="bone-joint"/>
        <circle cx="160" cy="160" r="4" class="bone-joint"/>
        <circle cx="180" cy="155" r="4" class="bone-joint"/>
        <circle cx="200" cy="160" r="4" class="bone-joint"/>
        <circle cx="216" cy="175" r="4" class="bone-joint"/>
        <circle cx="155" cy="100" r="3" class="bone-joint"/>
        <circle cx="176" cy="95" r="3" class="bone-joint"/>
        <circle cx="196" cy="100" r="3" class="bone-joint"/>
        <circle cx="215" cy="110" r="3" class="bone-joint"/>
        <circle cx="266" cy="145" r="3" class="bone-joint"/>
      </g>
```

**Verification:** Browser shows bone layer — radius/ulna, carpals, metacarpals, phalanges, joint markers.

---

### Task 3: Draw muscle layer (thenar, hypothenar, interossei)

**File:** `docs/images/wiring_diagram_4imu_hand_detailed.html`

Add after bone layer:

```html
      <!-- MUSCLE LAYER -->
      <g class="layer-muscle" id="layer-muscle">
        <!-- Thenar eminence (thumb base) — large muscle group -->
        <path d="M 220 230 Q 250 200 280 210 Q 300 220 290 250 Q 280 280 250 275 Q 220 270 220 230 Z"/>
        <text x="255" y="245" text-anchor="middle" class="anatomy-label">thenar</text>
        <!-- Hypothenar eminence (pinky base) -->
        <path d="M 100 280 Q 120 260 140 270 Q 155 280 145 300 Q 135 320 115 315 Q 100 310 100 280 Z"/>
        <text x="125" y="295" text-anchor="middle" class="anatomy-label">hypothenar</text>
        <!-- Interossei (between metacarpals, dorsal) -->
        <ellipse cx="145" cy="200" rx="6" ry="15" transform="rotate(-10, 145, 200)"/>
        <ellipse cx="165" cy="195" rx="6" ry="15"/>
        <ellipse cx="185" cy="195" rx="6" ry="15"/>
        <ellipse cx="205" cy="200" rx="6" ry="15" transform="rotate(10, 205, 200)"/>
        <!-- Lumbricals (palmar side, small) -->
        <ellipse cx="155" cy="170" rx="4" ry="10"/>
        <ellipse cx="175" cy="165" rx="4" ry="10"/>
        <ellipse cx="195" cy="170" rx="4" ry="10"/>
        <ellipse cx="215" cy="175" rx="4" ry="10" transform="rotate(15, 215, 175)"/>
        <!-- Extensor hood (dorsal, over proximal phalanges) -->
        <ellipse cx="155" cy="115" rx="8" ry="12"/>
        <ellipse cx="175" cy="110" rx="8" ry="12"/>
        <ellipse cx="195" cy="115" rx="8" ry="12"/>
        <ellipse cx="215" cy="120" rx="7" ry="10"/>
      </g>
```

**Verification:** Browser shows muscle groups — thenar (large, thumb base), hypothenar (pinky base), interossei (between metacarpals), lumbricals, extensor hood.

---

### Task 4: Draw tendon layer (extensor and flexor tendons)

**File:** `docs/images/wiring_diagram_4imu_hand_detailed.html`

Add after muscle layer:

```html
      <!-- TENDON LAYER -->
      <g class="layer-tendon" id="layer-tendon">
        <!-- Extensor digitorum (dorsal, runs along fingers) -->
        <path d="M 137 180 Q 145 150 155 100 Q 160 70 155 45"/>
        <path d="M 160 160 Q 170 130 175 95 Q 178 60 172 38"/>
        <path d="M 180 155 Q 188 125 195 95 Q 198 65 192 48"/>
        <path d="M 200 160 Q 208 135 215 110 Q 218 80 212 65"/>
        <!-- Extensor pollicis longus (thumb) -->
        <path d="M 266 145 Q 275 120 285 105 Q 290 90 288 75"/>
        <!-- Extensor pollicis brevis (thumb, shorter) -->
        <path d="M 260 155 Q 268 135 275 120"/>
        <!-- Flexor tendons (palmar side, implied) -->
        <path d="M 137 250 Q 145 270 155 290" opacity="0.5"/>
        <path d="M 160 250 Q 170 270 175 285" opacity="0.5"/>
        <path d="M 180 250 Q 188 270 195 285" opacity="0.5"/>
        <path d="M 200 250 Q 208 270 215 285" opacity="0.5"/>
        <!-- Dorsal intertendinous connections -->
        <path d="M 155 80 Q 165 85 175 80" opacity="0.4"/>
        <path d="M 175 75 Q 185 80 195 75" opacity="0.4"/>
        <path d="M 195 80 Q 205 85 215 80" opacity="0.4"/>
      </g>
```

**Verification:** Browser shows tendon lines — extensor digitorum (4 fingers), extensor pollicis (thumb), flexor tendons (palmar, faint), intertendinous connections.

---

### Task 5: Draw skin layer (outer surface with detail)

**File:** `docs/images/wiring_diagram_4imu_hand_detailed.html`

Add after tendon layer:

```html
      <!-- SKIN LAYER (outermost) -->
      <g class="layer-skin" id="layer-skin">
        <!-- Forearm outline -->
        <path d="M 30 350 Q 40 310 60 290 L 100 280 L 130 290"/>
        <!-- Wrist -->
        <path d="M 130 290 Q 140 300 140 320 Q 140 340 130 350"/>
        <!-- Palm outline -->
        <path d="M 130 350 L 130 290 Q 135 250 155 200 Q 175 170 200 160 Q 230 155 260 170 Q 290 185 300 210 Q 310 240 300 270 Q 290 300 260 320 Q 230 340 200 340 Q 170 340 150 330 Q 135 320 130 310"/>
        <!-- Thumb outline -->
        <path d="M 260 170 Q 280 155 300 155 Q 320 160 330 180 Q 335 200 325 220 Q 315 240 295 250 Q 275 255 260 245 Q 250 230 255 210 Q 258 190 260 170 Z"/>
        <!-- Index finger -->
        <path d="M 155 200 Q 150 170 152 140 Q 154 110 150 80 Q 148 60 152 45 Q 156 35 162 40 Q 168 50 166 70 Q 164 95 168 120 Q 172 150 170 180 Q 168 200 160 210 Z"/>
        <!-- Middle finger -->
        <path d="M 175 195 Q 172 160 174 130 Q 176 100 174 70 Q 172 45 176 30 Q 180 20 186 28 Q 190 40 188 60 Q 186 85 188 110 Q 190 140 188 170 Q 186 195 180 205 Z"/>
        <!-- Ring finger -->
        <path d="M 195 200 Q 192 170 194 140 Q 196 115 194 90 Q 192 65 196 50 Q 200 40 206 48 Q 210 60 208 80 Q 206 105 208 130 Q 210 155 208 180 Q 206 200 200 210 Z"/>
        <!-- Pinky finger -->
        <path d="M 215 210 Q 214 185 216 160 Q 218 140 216 120 Q 214 100 218 85 Q 222 75 228 80 Q 232 90 230 105 Q 228 125 230 145 Q 232 165 230 185 Q 228 200 222 210 Z"/>
        <!-- Finger crease lines (joints) -->
        <line x1="148" y1="100" x2="162" y2="100" class="crease-line"/>
        <line x1="150" y1="75" x2="160" y2="75" class="crease-line"/>
        <line x1="168" y1="95" x2="182" y2="95" class="crease-line"/>
        <line x1="170" y1="70" x2="180" y2="70" class="crease-line"/>
        <line x1="188" y1="100" x2="202" y2="100" class="crease-line"/>
        <line x1="190" y1="78" x2="200" y2="78" class="crease-line"/>
        <line x1="208" y1="110" x2="222" y2="110" class="crease-line"/>
        <line x1="210" y1="92" x2="218" y2="92" class="crease-line"/>
        <!-- Thumb creases -->
        <line x1="262" y1="145" x2="272" y2="142" class="crease-line"/>
        <line x1="275" y1="125" x2="283" y2="122" class="crease-line"/>
        <!-- Wrist crease -->
        <path d="M 120 300 Q 135 305 150 300" class="crease-line"/>
        <!-- Nail beds -->
        <path d="M 152 42 Q 154 38 158 38 Q 162 40 160 45" class="nail-shape"/>
        <path d="M 174 28 Q 176 24 180 24 Q 184 26 182 30" class="nail-shape"/>
        <path d="M 196 48 Q 198 44 202 44 Q 206 46 204 50" class="nail-shape"/>
        <path d="M 218 82 Q 220 78 224 78 Q 228 80 226 84" class="nail-shape"/>
        <path d="M 288 102 Q 290 98 294 98 Q 298 100 296 104" class="nail-shape"/>
      </g>
```

**Verification:** Browser shows complete hand outline with fingers, thumb, palm, forearm, crease lines, nail beds.

---

### Task 6: Add sensor dots at anatomically correct positions

**File:** `docs/images/wiring_diagram_4imu_hand_detailed.html`

Add after skin layer:

```html
      <!-- SENSOR PLACEMENT DOTS -->
      <g id="layer-sensors">
        <!-- CH0: dorsal wrist proximal — over radius/ulna junction -->
        <circle cx="75" cy="340" r="8" class="sensor-dot sensor-dot-ch0"/>
        <text x="55" y="328" class="sensor-label sensor-label-ch0">CH0 · dorsal wrist · primary</text>
        <line x1="75" y1="340" x2="55" y2="332" stroke="#1a3d8f" stroke-width="0.5"/>
        <!-- CH1: thenar volar — center of thenar eminence muscle -->
        <circle cx="255" cy="240" r="8" class="sensor-dot sensor-dot-ch1"/>
        <text x="275" y="235" class="sensor-label sensor-label-ch1">CH1 · thenar volar · thumb base</text>
        <line x1="255" y1="240" x2="275" y2="238" stroke="#0e6b2a" stroke-width="0.5"/>
        <!-- CH2: thumb proximal phalanx — over bone -->
        <circle cx="295" cy="165" r="8" class="sensor-dot sensor-dot-ch2"/>
        <text x="315" y="160" class="sensor-label sensor-label-ch2">CH2 · thumb phalanx · pill 4-6Hz</text>
        <line x1="295" y1="165" x2="315" y2="162" stroke="#7a5c00" stroke-width="0.5"/>
        <!-- CH3: index proximal phalanx — over bone -->
        <circle cx="155" cy="115" r="8" class="sensor-dot sensor-dot-ch3"/>
        <text x="125" y="95" class="sensor-label sensor-label-ch3">CH3 · index phalanx · ET 6-8Hz</text>
        <line x1="155" y1="115" x2="135" y2="100" stroke="#8a3b00" stroke-width="0.5"/>
      </g>
```

**Verification:** Browser shows 4 sensor dots with leader lines and labels at anatomically correct positions.

---

### Task 7: Draw electronics block and wires

**File:** `docs/images/wiring_diagram_4imu_hand_detailed.html`

Add after sensors:

```html
      <!-- ELECTRONICS BLOCK (right side) -->
      <g transform="translate(850,60)">
        <rect x="0" y="0" width="220" height="110" class="comp-box"/>
        <text x="110" y="18" text-anchor="middle" class="comp-title">U1 · ESP32-DevKitC</text>
        <text x="10" y="38" class="label-mono">21 SDA → mux</text>
        <text x="10" y="52" class="label-mono">22 SCL → mux</text>
        <text x="10" y="66" class="label-mono">2  LED → 220Ω</text>
        <text x="10" y="80" class="label-mono">3.3V · GND · 25/18/19/20 NC</text>
        <text x="10" y="98" class="label-mono">I²C0 @400kHz · 100Hz</text>
        <circle cx="0" cy="38" r="3" fill="var(--accent-ch1)"/>
        <circle cx="0" cy="52" r="3" fill="var(--accent-ch0)"/>
        <circle cx="0" cy="66" r="3" fill="#d4ac0d"/>
      </g>
      <g transform="translate(850,210)">
        <rect x="0" y="0" width="220" height="140" class="comp-box"/>
        <text x="110" y="18" text-anchor="middle" class="comp-title">U2 · TCA9548A</text>
        <text x="10" y="38" class="label-mono">@0x70 · A0-A2→GND · EN→3.3V</text>
        <text x="10" y="56" class="label-pin">SDA · SCL ← from U1</text>
        <text x="10" y="74" class="label-pin">SD0/SC0 → CH0</text>
        <text x="10" y="88" class="label-pin">SD1/SC1 → CH1</text>
        <text x="10" y="102" class="label-pin">SD2/SC2 → CH2</text>
        <text x="10" y="116" class="label-pin">SD3/SC3 → CH3</text>
        <circle cx="0" cy="74" r="3" fill="var(--accent-ch0)"/>
        <circle cx="0" cy="88" r="3" fill="var(--accent-ch1)"/>
        <circle cx="0" cy="102" r="3" fill="var(--accent-ch2)"/>
        <circle cx="0" cy="116" r="3" fill="var(--accent-ch3)"/>
      </g>
      <g transform="translate(850,390)">
        <rect x="0" y="0" width="220" height="50" class="comp-box"/>
        <text x="110" y="18" text-anchor="middle" class="comp-title">D1 · LED</text>
        <text x="10" y="38" class="label-mono">GPIO2 → 220Ω → GND · active high</text>
        <circle cx="0" cy="18" r="3" fill="#d4ac0d"/>
      </g>

      <!-- WIRES: sensor dots → electronics -->
      <path d="M 83 340 C 400 340, 400 284, 850 284" class="wire wire-ch0"/>
      <path d="M 263 240 C 500 240, 500 298, 850 298" class="wire wire-ch1"/>
      <path d="M 303 165 C 550 165, 550 312, 850 312" class="wire wire-ch2"/>
      <path d="M 163 115 C 450 115, 450 326, 850 326" class="wire wire-ch3"/>
      <path d="M 850 126 L 1070 126 L 1070 408 L 850 408" class="wire wire-led"/>
```

**Verification:** Browser shows electronics block (ESP32 + TCA + LED) with color-coded wires connecting to sensor dots.

---

### Task 8: Add legend, anatomical key, and notes

**File:** `docs/images/wiring_diagram_4imu_hand_detailed.html`

Add after `</svg></div>`, before `<script>`:

```html
  <div class="legend">
    <div class="legend-item"><span class="legend-dot" style="background:#2A6FFF;border-color:#1a3d8f;"></span> CH0 · dorsal wrist · primary</div>
    <div class="legend-item"><span class="legend-dot" style="background:#1DBA5A;border-color:#0e6b2a;"></span> CH1 · thenar volar · thumb base</div>
    <div class="legend-item"><span class="legend-dot" style="background:#E8B500;border-color:#7a5c00;"></span> CH2 · thumb phalanx 20° · pill 4-6Hz</div>
    <div class="legend-item"><span class="legend-dot" style="background:#FF7A1A;border-color:#8a3b00;"></span> CH3 · index phalanx · ET 6-8Hz</div>
    <div class="legend-item"><span class="legend-dot" style="background:#d4ac0d;border-color:#8a6d00;"></span> LED · GPIO2 · 220Ω</div>
  </div>
  <div class="legend">
    <div class="legend-item"><span class="legend-swatch" style="background:#f5e6d3;border-color:#c9a87c;"></span> Bone</div>
    <div class="legend-item"><span class="legend-swatch" style="background:rgba(200,120,100,0.25);border-color:#8b4513;"></span> Muscle</div>
    <div class="legend-item"><span class="legend-swatch" style="background:#d4a574;border-color:#d4a574;"></span> Tendon</div>
    <div class="legend-item"><span class="legend-swatch" style="background:#f5d5c8;border-color:#8b6f5e;"></span> Skin</div>
  </div>
  <table class="data-table">
    <thead>
      <tr><th>Channel</th><th>Anatomical Position</th><th>Underlying Structure</th><th>Tremor Type</th><th>Frequency</th></tr>
    </thead>
    <tbody>
      <tr><td>CH0</td><td>dorsal wrist proximal</td><td>radius/ulna junction</td><td>primary</td><td>—</td></tr>
      <tr><td>CH1</td><td>thenar volar (thumb base)</td><td>thenar eminence muscle</td><td>—</td><td>—</td></tr>
      <tr><td>CH2</td><td>thumb proximal phalanx</td><td>proximal phalanx bone</td><td>pill-rolling</td><td>4-6Hz</td></tr>
      <tr><td>CH3</td><td>index proximal phalanx</td><td>proximal phalanx bone</td><td>postural (ET)</td><td>6-8Hz</td></tr>
    </tbody>
  </table>
  <div class="notes">
    <strong>Build Note 2026-08-27 Option A + ET:</strong> Sensor placement locked for pill-rolling 4-6Hz (CH2 thumb phalanx 20° tilt) + postural ET 6-8Hz (CH3 index phalanx) with balanced coherence 0.6 (thumb-index &amp; finger-wrist). LRA GPIO25/18/19/20 deferred (NC). I²C0 @400kHz · 100Hz · 128-sample window · TCA9548A @0x70 · all GY-521 @0x68 via mux (1&lt;&lt;ch) · wire length &lt;15cm · 0.1µF per IC + 10µF bulk.<br>
    <strong>Anatomical Reference:</strong> Sensor positions relative to skeletal and muscular structures. Toggle layers using checkboxes above to isolate bone, muscle, tendon, or skin layers.
  </div>
```

**Verification:** Browser shows sensor legend, anatomical key (4 layers), sensor table with underlying structures, and notes.

---

### Task 9: Verify wire geometry

**File:** `docs/images/wiring_diagram_4imu_hand_detailed.html`

| Wire | Start (sensor dot) | End (electronics pin) | Match? |
|------|--------------------|-----------------------|--------|
| CH0 | (83, 340) | (850, 284) | TCA CH0 pin at (850, 284) ✓ |
| CH1 | (263, 240) | (850, 298) | TCA CH1 pin at (850, 298) ✓ |
| CH2 | (303, 165) | (850, 312) | TCA CH2 pin at (850, 312) ✓ |
| CH3 | (163, 115) | (850, 326) | TCA CH3 pin at (850, 326) ✓ |
| LED | (850, 126) | (850, 408) | D1 pin at (850, 408) ✓ |

**Verification:** All wire endpoints meet pin circles. No gaps.

---

## Tests / Validation

1. **Open in browser:** `start docs/images/wiring_diagram_4imu_hand_detailed.html` — renders without errors, all layers visible.
2. **Layer toggles:** Click each checkbox — corresponding layer shows/hides independently.
3. **Cross-reference firmware:** All pin numbers, addresses, and parameters match `firmware/common/config.py`.
4. **Cross-reference placement:** Sensor positions match Option A + ET lock (2026-08-27).
5. **Anatomical accuracy:** Bones, muscles, tendons are stylized but anatomically plausible (not photorealistic).

---

## Risks, Tradeoffs, and Open Questions

- **Complexity vs. readability:** 4 anatomical layers + sensors + wires + electronics = dense diagram. The layer toggles mitigate this by allowing isolation.
- **Anatomical precision:** Stylized SVG shapes, not medical illustrations. For publication-grade accuracy, a reference image should be traced.
- **Wire routing:** Curved bezier paths may overlap with anatomical structures. This is acceptable since wires route above the skin layer.
- **Performance:** ~200+ SVG elements. Modern browsers handle this easily, but very old devices may lag.
- **Open:** Should the diagram include a palmar (volar) view as a separate panel? (Not included — YAGNI.)
- **Open:** Should sensor dots include axis orientation indicators (arrows showing X/Y/Z axes)? (Not included — adds clutter.)

---

## Files Changed

| File | Action |
|------|--------|
| `docs/images/wiring_diagram_4imu_hand_detailed.html` | Create new |

No existing files modified.
