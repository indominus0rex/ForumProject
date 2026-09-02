# Plan: Remove D2 Power LED from Power Section

**Created:** 2026-09-01
**Goal:** Remove the D2 green power LED (and its 1kΩ resistor R1) from the power section across all diagrams and prompts.

---

## Current Context / Assumptions

- **Existing plan:** `.hermes/plans/2026-09-01_add-power-section.md` — includes D2 power LED + R1 resistor
- **D2 function:** Charge status indicator (low=charging when MCP73831 STAT pin is used)
- **User wants:** Remove D2 only — keep MCP73831 STAT pin floating or use a different indicator approach
- **Files affected:**
  - `.hermes/plans/2026-09-01_add-power-section.md` — power section plan (update)
  - `docs/images/wiring_diagram_4imu_datasheet.html` — HTML diagram (if power section was added)
  - `docs/images/wiring_diagram_4imu_hand_detailed.html` — hand diagram (if power section was added)
  - `docs/images/prompt_datasheet_wiring_diagram.txt` — AI prompt
  - `docs/images/prompt_datasheet_wiring_diagram_detailed.txt` — AI prompt detailed
  - `docs/images/prompt_realistic_components_wiring_diagram.txt` — AI prompt realistic

---

## Architecture / Proposed Approach

Remove D2 (green LED) and R1 (1kΩ resistor) from the power section. The MCP73831 STAT pin can be left unconnected (floating) or tied to VBAT through a high-value resistor if a future indicator is needed. The power section now has 7 components instead of 8. The connection table loses the CHG_LED net. All references to D2 and R1 are removed from the plan, diagrams, and prompts.

---

## Step-by-Step Tasks

### Task 1: Update power section plan — remove D2 and R1

**File:** `.hermes/plans/2026-09-01_add-power-section.md`

**Changes:**
1. Remove D2 from component list (section: "New components:")
2. Remove R1 from component list
3. Remove CHG_LED net from connection table
4. Remove D2 and R1 from SVG code block (Task 2)
5. Remove D2 and R1 from AI prompt descriptions (Tasks 4, 5, 6)
6. Remove D2 and R1 from Scheme It tutorial (Task 7)
7. Update verification checklist

**Updated component list (7 components):**
- **J1** — Micro-USB connector (charging only)
- **U7** — MCP73831 LiPo charger (SOT-23-5)
- **BT1** — LiPo battery (3.7V, 500mAh+, JST-PH 2.0)
- **U8** — AP2112K-3.3 LDO (SOT-23-5, 600mA)
- **C1** — 4.7µF ceramic capacitor (input decoupling)
- **C2** — 4.7µF ceramic capacitor (output decoupling)
- **J2** — JST-PH 2.0 battery connector (2-pin, 2.0mm pitch)

**Updated connection table (remove CHG_LED row):**

| Net | Source | Destination | Notes |
|-----|--------|-------------|-------|
| USB_5V | J1 pin 1 | U7 pin 1 (VBUS) | 5V from USB, charging only |
| VBAT | U7 pin 3 (VBAT) | BT1 (+), U8 pin 1 (VIN) | Battery positive, 3.7V nominal |
| 3.3V | U8 pin 3 (VOUT) | ESP32 3.3V pin, U2 VIN, U3 VCC, U4 VCC, U5 VCC, U6 VCC, D1 anode (via 220Ω) | Regulated output, 600mA max |
| GND | U7 pin 2 (GND), U8 pin 2 (GND), BT1 (-), C1, C2, D1 cathode | System GND | Star ground, common return |

**Verification:** Plan no longer references D2 or R1. Component count is 7.

---

### Task 2: Update datasheet HTML diagram — remove D2 SVG

**File:** `docs/images/wiring_diagram_4imu_datasheet.html`

**Remove from SVG code block:**
```html
        <!-- Power LED D2 -->
        <rect x="490" y="0" width="50" height="30" class="comp-box"/>
        <text x="25" y="12" text-anchor="middle" class="comp-title" font-size="8">D2 · LED</text>
        <text x="25" y="22" text-anchor="middle" class="label-mono" font-size="7">Power · 1kΩ</text>
        <circle cx="0" cy="12" r="2" fill="#1a1a1a"/>
        <circle cx="50" cy="12" r="2" fill="#1a1a1a"/>
```

**Remove associated wire:**
```html
      <path d="M 450 12 L 490 12" class="wire"/>
```

**Verification:** D2 box and its wire are removed from the SVG. Power section now ends at C2.

---

### Task 3: Update hand anatomy HTML diagram — remove D2 reference

**File:** `docs/images/wiring_diagram_4imu_hand_detailed.html`

**Remove from power module description:**
```
- D2 · Power LED (5mm, 1kΩ resistor)
```

**Updated power module text:**
```html
        <text x="10" y="66" class="label-mono">U8 · AP2112K-3.3 · LDO 600mA</text>
        <text x="10" y="78" class="label-mono">C1/C2 · 4.7µF</text>
```

**Verification:** Power module description no longer mentions D2.

---

### Task 4: Update AI prompt (datasheet style) — remove D2

**File:** `docs/images/prompt_datasheet_wiring_diagram.txt`

**Remove from power section:**
```
- D2 · Green LED: 5mm round, clear lens, with 1kΩ resistor
```

**Remove from power nets:**
```
- CHG_LED: wire from U7 pin 5 (STAT) to D2 anode (charge status indicator)
```

**Verification:** AI prompt no longer describes D2 or CHG_LED net.

---

### Task 5: Update AI prompt (detailed coordinates) — remove D2

**File:** `docs/images/prompt_datasheet_wiring_diagram_detailed.txt`

**Remove D2 coordinate block:**
```
- D2 · LED: x=490, y=380, width=50, height=30, stroke-width 1.2
  Label: "D2 · LED", x=25, y=12, text-anchor middle, font 8px bold
  Value: "Power · 1kΩ", x=25, y=22, text-anchor middle, font 7px monospace
```

**Remove D2 wire:**
```
- D2 wire: path "M 450 392 L 490 392", stroke #1A1A1A, stroke-width 1.3
```

**Verification:** AI prompt no longer includes D2 coordinates or wire.

---

### Task 6: Update AI prompt (realistic components) — remove D2

**File:** `docs/images/prompt_realistic_components_wiring_diagram.txt`

**Remove from power module:**
```
- D2 · Green LED: 5mm round, clear lens, with 1kΩ resistor (blue body, brown-black-red-gold bands)
```

**Verification:** AI prompt no longer describes D2.

---

### Task 7: Update Scheme It tutorial — remove D2 task

**File:** `.hermes/plans/2026-09-01_schemeit-wiring-diagram-tutorial.md`

**Remove from Task 10a:**
```
15. Search for "LED" — drag to x=490, y=380
16. Set properties: RefDes=D2, Value=Power LED
```

**Remove from Task 10b:**
```
7. Draw wire from U7 pin 5 to D2 anode (CHG_LED)
```

**Verification:** Scheme It tutorial no longer includes D2 placement or wiring tasks.

---

### Task 8: Verify all updates

**Checklist:**
- [ ] Power section plan: D2 and R1 removed from component list
- [ ] Power section plan: CHG_LED net removed from connection table
- [ ] Power section plan: D2/R1 removed from SVG code
- [ ] Power section plan: D2/R1 removed from AI prompt descriptions
- [ ] Power section plan: D2/R1 removed from Scheme It tutorial
- [ ] Datasheet HTML: D2 SVG box removed
- [ ] Datasheet HTML: D2 wire removed
- [ ] Hand diagram: D2 reference removed from power module text
- [ ] AI prompt (datasheet): D2 and CHG_LED removed
- [ ] AI prompt (detailed): D2 coordinates and wire removed
- [ ] AI prompt (realistic): D2 description removed
- [ ] Scheme It tutorial: D2 tasks removed
- [ ] All files: Component count is 7 (not 8)
- [ ] All files: Connection table has 4 power nets (not 5)

**Verification:** All references to D2 and R1 are removed. Power section is cleaner and simpler.

---

## Tests / Validation

This is a multi-file edit task. Validation is:

1. **Plan review:** Read `.hermes/plans/2026-09-01_add-power-section.md` — no mentions of D2, R1, or CHG_LED
2. **HTML review:** Open `docs/images/wiring_diagram_4imu_datasheet.html` in browser — no D2 box visible
3. **AI prompt review:** Read all 3 AI prompts — no D2 descriptions
4. **Scheme It tutorial review:** Read tutorial — no D2 tasks
5. **Cross-reference:** All connection tables match across all files (4 power nets, not 5)

---

## Risks, Tradeoffs, and Open Questions

- **Loss of charge indicator:** Without D2, there is no visual indication of charging status. The MCP73831 STAT pin can be left floating (no indicator) or tied to a future indicator circuit.
- **STAT pin floating:** MCP73831 STAT pin is open-drain. If left floating, the charger still works but provides no status output. This is acceptable for a minimal build.
- **Future expansion:** If a charge indicator is needed later, a 10kΩ pull-up to VBAT + LED can be added to the STAT pin without changing the existing layout.
- **Open:** Should the STAT pin be tied to VBAT through a 10kΩ resistor (pull-up) for future use? (Not included — YAGNI, can be added later.)
- **Open:** Should the power section include a power switch between battery and LDO? (Not included — YAGNI, can be added later.)

---

## Files Changed

| File | Action |
|------|--------|
| `.hermes/plans/2026-09-01_add-power-section.md` | Update — remove D2, R1, CHG_LED |
| `docs/images/wiring_diagram_4imu_datasheet.html` | Update — remove D2 SVG box and wire |
| `docs/images/wiring_diagram_4imu_hand_detailed.html` | Update — remove D2 reference |
| `docs/images/prompt_datasheet_wiring_diagram.txt` | Update — remove D2 and CHG_LED |
| `docs/images/prompt_datasheet_wiring_diagram_detailed.txt` | Update — remove D2 coordinates and wire |
| `docs/images/prompt_realistic_components_wiring_diagram.txt` | Update — remove D2 description |
| `.hermes/plans/2026-09-01_schemeit-wiring-diagram-tutorial.md` | Update — remove D2 tasks |
