# Plan: Add Power Section (Option B) to All Wiring Diagrams

**Created:** 2026-09-01
**Goal:** Add a complete LiPo battery power section (Option B: MCP73831 charger + AP2112K-3.3 LDO) to all wiring diagrams in the project.

---

## Current Context / Assumptions

- **Existing diagrams to update:**
  - `docs/images/wiring_diagram_4imu_datasheet.html` — monochrome box-schematic
  - `docs/images/wiring_diagram_4imu_hand_detailed.html` — anatomical hand diagram
  - `docs/images/prompt_datasheet_wiring_diagram.txt` — AI prompt for datasheet
  - `docs/images/prompt_datasheet_wiring_diagram_detailed.txt` — AI prompt with coordinates
  - `docs/images/prompt_realistic_components_wiring_diagram.txt` — AI prompt for photorealistic
  - `.hermes/plans/2026-09-01_schemeit-wiring-diagram-tutorial.md` — Scheme It tutorial
- **Power architecture (Option B):**
  - BT1: LiPo battery 3.7V nominal, 500-2000mAh, JST-PH 2.0 connector
  - J1: Micro-USB connector (for charging only, not data)
  - U7: MCP73831 LiPo charger IC (SOT-23-5), charges at 500mA via USB
  - U8: AP2112K-3.3 LDO regulator (SOT-23-5), 600mA output, 3.3V fixed
  - C1: 4.7µF ceramic capacitor (input to AP2112K, close to pin 1)
  - C2: 4.7µF ceramic capacitor (output from AP2112K, close to pin 3)
  - J2: JST-PH 2.0 battery connector (2-pin, 2.0mm pitch)
- **Power flow:**
  - USB 5V → MCP73831 → LiPo battery (charging)
  - LiPo battery → AP2112K-3.3 → 3.3V rail (powering system)
  - 3.3V rail → ESP32 3.3V pin (bypass onboard regulator), TCA9548A VIN, all GY-521 VCC, LED
- **Bypass ESP32 onboard regulator:** Power the 3.3V pin directly, do NOT use VIN pin

---

## Architecture / Proposed Approach

The power section adds 5 new components (BT1, J1, U7, U8, C1, C2, J2) and 4 new nets (USB_5V, VBAT, 3.3V regulated, GND). The power section is drawn as a separate block at the left-bottom of the datasheet diagram, with clear power flow from USB → charger → battery → regulator → 3.3V rail. In the hand diagram, the power section is shown as a compact module worn on the forearm or in a pocket, with a wire running to the ESP32. In AI prompts, each power component is described with its physical appearance (SOT-23-5 packages, ceramic caps, JST connector).

---

## Step-by-Step Tasks

### Task 1: Update connection table (master reference)

**File:** `docs/images/wiring_diagram_4imu_datasheet.html`

Update the connection table to include power section:

| Net | Source | Destination | Notes |
|-----|--------|-------------|-------|
| USB_5V | J1 pin 1 | U7 pin 1 (VBUS) | 5V from USB, charging only |
| USB_GND | J1 pin 5 | System GND | USB ground |
| VBAT | U7 pin 3 (VBAT) | BT1 (+), U8 pin 1 (VIN) | Battery positive, 3.7V nominal |
| 3.3V | U8 pin 3 (VOUT) | ESP32 3.3V pin, U2 VIN, U3 VCC, U4 VCC, U5 VCC, U6 VCC, D1 anode (via 220Ω) | Regulated output, 600mA max |
| GND | U7 pin 2 (GND), U8 pin 2 (GND), BT1 (-), C1, C2, D1 cathode | System GND | Star ground, common return |
| SDA21 | U1 GPIO21 | U2 SDA | I²C0 data, 400kHz |
| SCL22 | U1 GPIO22 | U2 SCL | I²C0 clock, 400kHz |
| CH0 | U2 SD0/SC0 | U3 SDA/SCL | dorsal wrist |
| CH1 | U2 SD1/SC1 | U4 SDA/SCL | thenar volar |
| CH2 | U2 SD2/SC2 | U5 SDA/SCL | thumb phalanx |
| CH3 | U2 SD3/SC3 | U6 SDA/SCL | index phalanx |
| LED | U1 GPIO2 | D1 anode | 220Ω → GND |

**New components (7):**
- **J1** — Micro-USB connector (charging only)
- **U7** — MCP73831 LiPo charger (SOT-23-5)
- **BT1** — LiPo battery (3.7V, 500mAh+, JST-PH 2.0)
- **U8** — AP2112K-3.3 LDO (SOT-23-5, 600mA)
- **C1** — 4.7µF ceramic capacitor (input decoupling)
- **C2** — 4.7µF ceramic capacitor (output decoupling)
- **J2** — JST-PH 2.0 battery connector (2-pin, 2.0mm pitch)

---

### Task 2: Update datasheet HTML diagram

**File:** `docs/images/wiring_diagram_4imu_datasheet.html`

Add power section at bottom-left, below existing components:

**Power section SVG (add before </svg>):**

```html
      <!-- Power Section -->
      <g transform="translate(40,380)">
        <!-- Micro-USB J1 -->
        <rect x="0" y="0" width="60" height="40" class="comp-box"/>
        <text x="30" y="14" text-anchor="middle" class="comp-title">J1 · Micro-USB</text>
        <text x="30" y="26" text-anchor="middle" class="label-mono">Charging only</text>
        <circle cx="0" cy="14" r="2.5" fill="#1a1a1a"/>
        <circle cx="0" cy="26" r="2.5" fill="#1a1a1a"/>
        
        <!-- MCP73831 U7 -->
        <rect x="100" y="0" width="120" height="50" class="comp-box"/>
        <text x="60" y="14" text-anchor="middle" class="comp-title">U7 · MCP73831</text>
        <text x="60" y="26" text-anchor="middle" class="label-mono">LiPo Charger · SOT-23-5</text>
        <text x="10" y="40" class="label-pin">1 VBUS · 2 GND · 3 VBAT · 4 PROG · 5 STAT</text>
        <circle cx="0" cy="14" r="2.5" fill="#1a1a1a"/>
        <circle cx="0" cy="26" r="2.5" fill="#1a1a1a"/>
        <circle cx="120" cy="14" r="2.5" fill="#1a1a1a"/>
        <circle cx="120" cy="26" r="2.5" fill="#1a1a1a"/>
        <circle cx="120" cy="38" r="2.5" fill="#1a1a1a"/>
        
        <!-- AP2112K-3.3 U8 -->
        <rect x="260" y="0" width="120" height="50" class="comp-box"/>
        <text x="60" y="14" text-anchor="middle" class="comp-title">U8 · AP2112K-3.3</text>
        <text x="60" y="26" text-anchor="middle" class="label-mono">LDO 3.3V · 600mA</text>
        <text x="10" y="40" class="label-pin">1 VIN · 2 GND · 3 VOUT</text>
        <circle cx="0" cy="14" r="2.5" fill="#1a1a1a"/>
        <circle cx="0" cy="26" r="2.5" fill="#1a1a1a"/>
        <circle cx="120" cy="14" r="2.5" fill="#1a1a1a"/>
        
        <!-- Capacitors -->
        <rect x="420" y="0" width="30" height="25" class="comp-box"/>
        <text x="15" y="12" text-anchor="middle" class="comp-title" font-size="8">C1</text>
        <text x="15" y="20" text-anchor="middle" class="label-mono" font-size="7">4.7µF</text>
        <circle cx="0" cy="12" r="2" fill="#1a1a1a"/>
        <circle cx="30" cy="12" r="2" fill="#1a1a1a"/>
        
        <rect x="420" y="30" width="30" height="25" class="comp-box"/>
        <text x="15" y="12" text-anchor="middle" class="comp-title" font-size="8">C2</text>
        <text x="15" y="20" text-anchor="middle" class="label-mono" font-size="7">4.7µF</text>
        <circle cx="0" cy="12" r="2" fill="#1a1a1a"/>
        <circle cx="30" cy="12" r="2" fill="#1a1a1a"/>
        

        <rect x="580" y="0" width="80" height="50" class="comp-box"/>
        <text x="40" y="14" text-anchor="middle" class="comp-title">BT1 · LiPo</text>
        <text x="40" y="26" text-anchor="middle" class="label-mono">3.7V · 500mAh+</text>
        <text x="40" y="38" text-anchor="middle" class="label-mono">JST-PH 2.0</text>
        <circle cx="0" cy="14" r="2.5" fill="#1a1a1a"/>
        <circle cx="0" cy="26" r="2.5" fill="#1a1a1a"/>
      </g>
      
      <!-- Power wires -->
      <path d="M 100 14 L 60 14" class="wire"/>
      <text x="75" y="10" class="label-net" font-size="7">USB_5V</text>
      <path d="M 100 26 L 60 26" class="wire"/>
      <path d="M 220 14 L 260 14" class="wire"/>
      <text x="235" y="10" class="label-net" font-size="7">VBAT</text>
      <path d="M 220 26 L 260 26" class="wire"/>
      <path d="M 380 14 L 420 12" class="wire"/>
      <path d="M 380 26 L 420 42" class="wire"/>
      <path d="M 380 14 L 380 160" class="wire" stroke-dasharray="3 3"/>
      <text x="385" y="90" class="label-net" font-size="7" fill="#2c5282">3.3V rail</text>
```

**Verification:** Power section renders at bottom-left, wires connect components, 3.3V rail connects to main diagram.

---

### Task 3: Update hand anatomy HTML diagram

**File:** `docs/images/wiring_diagram_4imu_hand_detailed.html`

Add power module as a separate box on the forearm, with a wire running to the ESP32:

```html
      <!-- Power Module (on forearm, separate from hand sensors) -->
      <g transform="translate(850,480)">
        <rect x="0" y="0" width="220" height="80" class="comp-box"/>
        <text x="110" y="14" text-anchor="middle" class="comp-title">Power Module (Option B)</text>
        <text x="10" y="30" class="label-mono">J1 · Micro-USB (charging)</text>
        <text x="10" y="42" class="label-mono">U7 · MCP73831 · LiPo charger</text>
        <text x="10" y="54" class="label-mono">BT1 · 3.7V LiPo · 500mAh+</text>
        <text x="10" y="66" class="label-mono">U8 · AP2112K-3.3 · LDO 600mA</text>
        <text x="10" y="78" class="label-mono">C1/C2 · 4.7µF</text>
        <circle cx="0" cy="30" r="3" fill="#d4ac0d"/>
        <circle cx="220" cy="30" r="3" fill="#c0392b"/>
      </g>
      
      <!-- Power wire from module to ESP32 -->
      <path d="M 850 510 L 400 510 L 400 200" class="wire" stroke="#c0392b" stroke-width="2"/>
      <text x="600" y="505" class="label-net" font-size="9" fill="#c0392b">3.3V to ESP32 3.3V pin</text>
```

**Verification:** Power module visible on forearm section, red wire routes to ESP32.

---

### Task 4: Update AI prompt (datasheet style)

**File:** `docs/images/prompt_datasheet_wiring_diagram.txt`

Add power section description:

```
POWER SECTION (bottom-left, below main components):
- J1 · Micro-USB connector: silver metal housing, 5-pin, SMD mounting, "Charging only" label
- U7 · MCP73831: black SOT-23-5 package, "MCP73831" marking, LiPo charger IC
- BT1 · LiPo battery: silver pouch cell, 3.7V 500mAh+, JST-PH 2.0 connector (2-pin, 2.0mm pitch)

```

---

### Task 5: Update AI prompt (detailed coordinates)

**File:** `docs/images/prompt_datasheet_wiring_diagram_detailed.txt`

Add power section with exact coordinates:

```
POWER SECTION (exact coordinates):
- J1 · Micro-USB: x=40, y=380, width=60, height=40, stroke-width 1.2
  Pin 1 (VBUS): circle cx=0, cy=14, r=2.5, fill #1A1A1A
  Pin 5 (GND): circle cx=0, cy=26, r=2.5, fill #1A1A1A
  Label: "J1 · Micro-USB", x=30, y=14, text-anchor middle, font 11px bold
  Subtitle: "Charging only", x=30, y=26, text-anchor middle, font 9.5px monospace

- U7 · MCP73831: x=140, y=380, width=120, height=50, stroke-width 1.2
  Pin 1 (VBUS): circle cx=0, cy=14, r=2.5, fill #1A1A1A
  Pin 2 (GND): circle cx=0, cy=26, r=2.5, fill #1A1A1A
  Pin 3 (VBAT): circle cx=120, cy=14, r=2.5, fill #1A1A1A
  Pin 4 (PROG): circle cx=120, cy=26, r=2.5, fill #1A1A1A
  Pin 5 (STAT): circle cx=120, cy=38, r=2.5, fill #1A1A1A
  Label: "U7 · MCP73831", x=60, y=14, text-anchor middle, font 11px bold
  Subtitle: "LiPo Charger · SOT-23-5", x=60, y=26, text-anchor middle, font 9.5px monospace

- BT1 · LiPo: x=460, y=380, width=80, height=50, stroke-width 1.2
  Pin (+): circle cx=0, cy=14, r=2.5, fill #1A1A1A
  Pin (-): circle cx=0, cy=26, r=2.5, fill #1A1A1A
  Label: "BT1 · LiPo", x=40, y=14, text-anchor middle, font 11px bold
  Subtitle: "3.7V · 500mAh+", x=40, y=26, text-anchor middle, font 9.5px monospace

- U8 · AP2112K-3.3: x=300, y=380, width=120, height=50, stroke-width 1.2
  Pin 1 (VIN): circle cx=0, cy=14, r=2.5, fill #1A1A1A
  Pin 2 (GND): circle cx=0, cy=26, r=2.5, fill #1A1A1A
  Pin 3 (VOUT): circle cx=120, cy=14, r=2.5, fill #1A1A1A
  Label: "U8 · AP2112K-3.3", x=60, y=14, text-anchor middle, font 11px bold
  Subtitle: "LDO 3.3V · 600mA", x=60, y=26, text-anchor middle, font 9.5px monospace

- C1: x=420, y=380, width=30, height=25, stroke-width 1.2
  Label: "C1", x=15, y=12, text-anchor middle, font 8px bold
  Value: "4.7µF", x=15, y=20, text-anchor middle, font 7px monospace

- C2: x=420, y=410, width=30, height=25, stroke-width 1.2
  Label: "C2", x=15, y=12, text-anchor middle, font 8px bold
  Value: "4.7µF", x=15, y=20, text-anchor middle, font 7px monospace

- D2 · LED: x=490, y=380, width=50, height=30, stroke-width 1.2
  Label: "D2 · LED", x=25, y=12, text-anchor middle, font 8px bold
  Value: "Power · 1kΩ", x=25, y=22, text-anchor middle, font 7px monospace

POWER WIRES (exact paths):
- USB_5V: path "M 140 394 L 100 394", stroke #1A1A1A, stroke-width 1.3
- VBAT: path "M 260 394 L 300 394", stroke #1A1A1A, stroke-width 1.3
- VBAT to BT1: path "M 260 394 L 460 394", stroke #1A1A1A, stroke-width 1.3
- 3.3V rail: path "M 420 394 L 420 200", stroke #1A1A1A, stroke-width 1.3, stroke-dasharray 3 3
- GND: path "M 140 406 L 300 406", stroke #1A1A1A, stroke-width 1.3
```

---

### Task 6: Update AI prompt (realistic components)

**File:** `docs/images/prompt_realistic_components_wiring_diagram.txt`

Add realistic power section:

```
POWER MODULE (realistic components, worn in pocket or on forearm):
- J1 · Micro-USB connector: Silver metal housing, 5-pin SMD, on small PCB breakout
- U7 · MCP73831: Black SOT-23-5 package, tiny text "MCP73831" visible, on small PCB
- BT1 · LiPo battery: Silver pouch cell, 3.7V 500mAh+, JST-PH 2.0 connector (white, 2-pin), dimensions 34×20×5mm
- U8 · AP2112K-3.3: Black SOT-23-5 package, "AP2112" marking, on small PCB
- C1/C2 · 4.7µF: Yellow-brown ceramic capacitors, 0805 SMD, marked "475"
- Wires: Red (3.3V), black (GND), yellow (USB 5V), 30AWG silicone-insulated
```

---

### Task 7: Update Scheme It tutorial

**File:** `.hermes/plans/2026-09-01_schemeit-wiring-diagram-tutorial.md`

Add power section tasks after Task 10:

```
### Task 10a: Add power section components

**Steps:**
1. In left sidebar, search for "Micro-USB" or "USB connector"
2. Drag symbol to x=40, y=380
3. Set properties: RefDes=J1, Value=Micro-USB
4. Search for "MCP73831" or create custom SOT-23-5 symbol
5. Drag to x=140, y=380
6. Set properties: RefDes=U7, Value=MCP73831
7. Search for "LiPo battery" or "battery"
8. Drag to x=460, y=380
9. Set properties: RefDes=BT1, Value=LiPo 3.7V
10. Search for "AP2112" or "LDO regulator" or create custom
11. Drag to x=300, y=380
12. Set properties: RefDes=U8, Value=AP2112K-3.3
13. Search for "capacitor" — drag 2× to x=420, y=380 and x=420, y=410
14. Set properties: RefDes=C1/C2, Value=4.7µF

### Task 10b: Add power wires

**Steps:**
1. Draw wire from J1 pin 1 to U7 pin 1 (USB_5V)
2. Draw wire from U7 pin 3 to U8 pin 1 (VBAT)
3. Draw wire from U7 pin 3 to BT1 (+) (VBAT)
4. Draw wire from U8 pin 3 to 3.3V rail (3.3V regulated)
5. Draw wire from J1 pin 5 to GND bus
6. Draw wire from U7 pin 2 to GND bus
7. Draw wire from U8 pin 2 to GND bus
8. Draw wire from BT1 (-) to GND bus
9. Draw dashed wire from 3.3V rail up to main diagram
```

---

### Task 8: Verify all updates

**Checklist:**
- [ ] Datasheet HTML: Power section renders at bottom-left, all 8 components present
- [ ] Datasheet HTML: Power wires connect correctly (USB_5V, VBAT, 3.3V, GND)
- [ ] Datasheet HTML: 3.3V rail connects to main ESP32 diagram
- [ ] Hand diagram: Power module visible on forearm, wire to ESP32
- [ ] AI prompt (datasheet): Power section described with components and nets
- [ ] AI prompt (detailed): Power section has exact coordinates
- [ ] AI prompt (realistic): Power section has realistic component descriptions
- [ ] Scheme It tutorial: Power section tasks added (10a, 10b)
- [ ] All diagrams: Connection table includes power nets (USB_5V, VBAT, 3.3V, GND)

**Verification:** All diagrams updated with Option B power section.

---

## Tests / Validation

This is a multi-file update task. Validation is:

1. **HTML diagrams:** Open in browser — power section renders correctly, no overlapping elements
2. **AI prompts:** Read through — power section clearly described, no missing components
3. **Scheme It tutorial:** Read through — power section tasks are actionable
4. **Cross-reference:** All connection tables match across all files

---

## Risks, Tradeoffs, and Open Questions

- **Diagram clutter:** Adding 8 power components may crowd the datasheet diagram. Mitigation: Move power section to separate row below main components, or create a separate power-only diagram.
- **AI prompt length:** Adding power section increases prompt length by ~100 lines. May hit token limits on some generators. Mitigation: Split into "main diagram" and "power section" prompts.
- **Component availability:** MCP73831 and AP2112K symbols may not exist in Scheme It library. Mitigation: Create custom symbols.
- **Battery representation:** AI generators may struggle with LiPo pouch cell appearance. Mitigation: Describe as "silver pouch cell with JST connector" rather than detailed appearance.
- **Open:** Should the power section include a power switch? (Not included — YAGNI, can be added later.)
- **Open:** Should the power section include a fuel gauge IC? (Not included — YAGNI, can be added later.)

---

## Files Changed

| File | Action |
|------|--------|
| `docs/images/wiring_diagram_4imu_datasheet.html` | Update — add power section SVG |
| `docs/images/wiring_diagram_4imu_hand_detailed.html` | Update — add power module box |
| `docs/images/prompt_datasheet_wiring_diagram.txt` | Update — add power section description |
| `docs/images/prompt_datasheet_wiring_diagram_detailed.txt` | Update — add power section coordinates |
| `docs/images/prompt_realistic_components_wiring_diagram.txt` | Update — add realistic power components |
| `.hermes/plans/2026-09-01_schemeit-wiring-diagram-tutorial.md` | Update — add power section tasks |
