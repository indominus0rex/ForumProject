# Plan: Switch Charger from MCP73831 to TP4056 (1A)

**Created:** 2026-09-01
**Goal:** Replace the MCP73831 LiPo charger (500mA, SOT-23-5) with a TP4056 module (1A, with protection) across all project diagrams and documentation.

---

## Current Context / Assumptions

- **Existing charger:** MCP73831 (SOT-23-5, 500mA charge current) — shown in all diagrams
- **New charger:** TP4056 module (SOP-8 or breakout board, 1A charge current, with DW01 protection)
- **Hardware on hand:** Per `sessions/session-ses-fbc7.md`, user has TP4056 charger module with DW01 protection, BAT± pads, and possibly OUT± (load-sharing)
- **Power chain change:** TP4056 module replaces U7. May also affect U8 (AP2112K-3.3) if switching to boost-to-5V architecture per session notes
- **Key difference:** TP4056 is a module (not bare IC), includes battery protection, charges at 1A (vs 500mA)

---

## Architecture / Proposed Approach

The TP4056 module replaces U7 (MCP73831) in the power section. The module has:
- Micro-USB input (5V)
- BAT± pads (connect to LiPo battery)
- OUT± pads (load-sharing output, if available)
- Built-in DW01 protection + FS8205A MOSFET
- LED indicators (red=charging, green=full)

The TP4056 outputs battery voltage (3.0-4.2V) on BAT±. Regulation to 3.3V or 5V remains downstream (U8 AP2112K-3.3 or boost converter).

Files to update:
1. `docs/images/wiring_diagram_build_guide.html` — HTML build guide
2. `docs/images/system_architecture_schematic.excalidraw` — Excalidraw schematic
3. `docs/images/connection_table.md` — Connection tables
4. `docs/images/ML Tremor Analysis Papers.md` — Obsidian note (if referenced)

---

## Step-by-Step Tasks

### Task 1: Update HTML build guide — replace U7 MCP73831 with TP4056

**File:** `docs/images/wiring_diagram_build_guide.html`

**Changes:**
1. In SVG section, find U7 block (around line 177-185):
   - Change `MCP73831` → `TP4056`
   - Change `LiPo Charger` → `LiPo Charger 1A`
   - Change `SOT-23-5` → `Module (SOP-8)`
   - Add note: `DW01 Protection`
   - Add pin labels: `BAT+`, `BAT-`, `OUT+`, `OUT-` (if load-sharing)

2. In BOM table (around line 511):
   - Change `MCP73831` → `TP4056 Module`
   - Change `SOT-23-5` → `Module (SOP-8)`
   - Change `LiPo charger, 500mA` → `LiPo charger, 1A, with protection`

3. In build notes (around line 182):
   - Add note: `TP4056 module includes DW01 battery protection`
   - Add note: `Charge current: 1A (vs 500mA for MCP73831)`

**Expected result:** U7 now shows TP4056 module.

**Verification:** Browser shows updated diagram with TP4056.

---

### Task 2: Update Excalidraw schematic — replace U7

**File:** `docs/images/system_architecture_schematic.excalidraw`

**Changes:**
1. Find element with id `t_u7` (text label for U7):
   - Change `"U7\nMCP73831\nLiPo Charger\nSOT-23-5"` → `"U7\nTP4056\nLiPo Charger 1A\nModule"`

2. Find element with id `u7` (rectangle for U7):
   - Optionally change `backgroundColor` from `#ffd8a8` to `#ffd8a8` (same, no change needed)

**Expected result:** Excalidraw shows TP4056 label.

**Verification:** Open in Excalidraw, verify label updated.

---

### Task 3: Update connection table — replace MCP73831 references

**File:** `docs/images/connection_table.md`

**Changes:**
1. In BOM table, find MCP73831 row:
   - Change `MCP73831` → `TP4056 Module`
   - Change `SOT-23-5` → `Module (SOP-8)`
   - Change `500mA` → `1A`

2. Add note after BOM:
   ```
   **Note:** TP4056 module includes DW01 battery protection and FS8205A MOSFET. Charge current: 1A (programmable via resistor). Some modules include OUT± pads for load-sharing.
   ```

**Expected result:** Connection table shows TP4056.

**Verification:** Markdown renders correctly.

---

### Task 4: Update Obsidian notes — replace charger reference

**File:** `C:\Users\Admin\Obsidian\ForumProject\06-Research\Essential Research Master Reference.md`

**Changes:**
1. Search for `MCP73831` (if present)
2. Replace with `TP4056 (1A)`

**Expected result:** Notes updated.

**Verification:** Obsidian shows updated text.

---

### Task 5: Verify consistency across all files

**Checklist:**
- [ ] `wiring_diagram_build_guide.html` shows TP4056
- [ ] `system_architecture_schematic.excalidraw` shows TP4056
- [ ] `connection_table.md` shows TP4056
- [ ] No remaining references to `MCP73831` in project files
- [ ] BOM updated to reflect TP4056 module (not bare IC)
- [ ] Pin labels updated (BAT±, OUT± for TP4056)

**Verification:** All files consistent.

---

## Tests / Validation

This is a documentation update task — no automated tests. Validation is:

1. **Visual inspection:** Open HTML guide in browser, verify TP4056 label visible
2. **Excalidraw inspection:** Open `.excalidraw` file, verify label updated
3. **Markdown inspection:** Open connection table, verify BOM updated
4. **Cross-reference:** No remaining MCP73831 references

---

## Risks, Tradeoffs, and Open Questions

- **Pin count mismatch:** MCP73831 is 5-pin SOT-23-5. TP4056 module has more connections (Micro-USB, BAT±, OUT±, LEDs). Diagram may need simplification to show module-level connections.
- **Load-sharing:** If TP4056 module has OUT± pads, the power chain changes (battery → OUT± → regulator). Need to verify if user has load-sharing version.
- **Charge current:** 1A vs 500mA — faster charging but more heat. Ensure LiPo cell can handle 1A charge rate (most 500mAh+ cells can).
- **Protection:** TP4056 module includes DW01 protection. If user already has separate protection, this may be redundant but not harmful.
- **Open:** Does the TP4056 module have OUT± pads (load-sharing) or only BAT±? This affects whether the system can run while charging.
- **Open:** Should U8 (AP2112K-3.3) remain, or switch to boost-to-5V architecture per session notes?

---

## Files Changed

| File | Action |
|------|--------|
| `docs/images/wiring_diagram_build_guide.html` | Update — replace MCP73831 with TP4056 |
| `docs/images/system_architecture_schematic.excalidraw` | Update — replace label text |
| `docs/images/connection_table.md` | Update — replace MCP73831 with TP4056 |
| `C:\Users\Admin\Obsidian\ForumProject\06-Research\Essential Research Master Reference.md` | Update — replace charger reference |

No code files modified.
