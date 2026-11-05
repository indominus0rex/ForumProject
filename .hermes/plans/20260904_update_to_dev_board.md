# Plan: Update Project Files to ESP32-DevKitC 38-pin Target

**Goal:** Update all project documentation, notes, and configuration files to reflect the ESP32-DevKitC 38-pin dev board as the target hardware (replacing bare WROOM + AP2112K assumptions).

## Current Context / Assumptions

- **Target changed:** ESP32-DevKitC 38-pin (has VIN pin, onboard AMS1117-3.3 LDO) — NOT bare WROOM module
- **Power topology:** USB 5V → TP4056 → 1S LiPo → MT3608 boost (5V) → VIN pin → onboard 3.3V
- **No AP2112K** — removed from design
- **No external AMS1117** — dev board has it onboard
- Files referencing bare WROOM, AP2112K, or external AMS1117 must be updated

## Files to Update

| File | Current State | Needed Change |
|------|--------------|---------------|
| `docs/images/tremor_monitor_schematic_v2.excalidraw` | References bare WROOM, AP2112K LDO, external 3.3V | Full redesign for dev board + MT3608 + TP4056 |
| `docs/wokwi_power_section_notes.md` | References bare WROOM, AP2112K pinout, 3V3 pin | Update to dev board VIN, MT3608 boost, TP4056 |
| `docs/wokwi_diagram_4imu.json` | Notes say "Bare ESP32-WROOM-32: Power from AP2112K-3.3" | Update to dev board VIN from MT3608 |
| `docs/images/connection_table.md` | U8 = AP2112K-3.3 LDO | Change to MT3608 boost converter, remove AP2112K |
| `docs/wiring/WIRING_DIAGRAM_DESIGN.md` | Mentions AMS1117-3.3 or similar, 3.3V rail | Update to MT3608 5V boost → VIN, onboard regulator |

## Step-by-Step Tasks

### Task 1: Update `docs/images/connection_table.md`
**File:** `docs/images/connection_table.md`

Find/replace:
- `U8 — AP2112K-3.3 LDO` → `U8 — MT3608 Boost Converter (5V output)`
- Any AP2112K pin references (VIN, GND, VOUT) → MT3608 pin references (IN+, IN-, OUT+, OUT-)
- Update BOM: remove AP2112K, add MT3608 module

### Task 2: Update `docs/wiring/WIRING_DIAGRAM_DESIGN.md`
**File:** `docs/wiring/WIRING_DIAGRAM_DESIGN.md`

Find/replace:
- `Voltage Regulator (AMS1117-3.3 or similar to provide 3.3V)` → `MT3608 Boost Converter (LiPo → 5V) → ESP32 VIN pin (onboard 3.3V regulator)`
- `3.3V rail` from external regulator → `5V rail to VIN` and `3.3V from onboard regulator`
- Update components list: remove AMS1117/AP2112K, add MT3608

### Task 3: Update `docs/wokwi_power_section_notes.md`
**File:** `docs/wokwi_power_section_notes.md`

Rewrite power topology section:
- Remove all AP2112K pinout references
- Change `Bare ESP32-WROOM-32` → `ESP32-DevKitC 38-pin`
- Change `AP2112K-3.3 VOUT -> 3.3V pin` → `MT3608 OUT -> 5V -> VIN pin`
- Update the power chain diagram
- Update BOM: remove AP2112K, C1-C4 for LDO; add MT3608, C1-C2 for boost

### Task 4: Update `docs/wokwi_diagram_4imu.json`
**File:** `docs/wokwi_diagram_4imu.json`

Update the `notes` field on the ESP32 part:
- From: `"Bare ESP32-WROOM-32: Power from AP2112K-3.3 VOUT -> 3.3V pin. See power section notes."`
- To: `"ESP32-DevKitC 38-pin: Powered via VIN pin from MT3608 boost (5V). Onboard AMS1117-3.3 regulates to 3.3V."`

### Task 5: Generate new schematic `docs/images/tremor_monitor_schematic_v3.excalidraw`
**File:** `docs/images/tremor_monitor_schematic_v3.excalidraw`

Create new schematic (or overwrite v2) with:
- POWER zone: J1 USB → TP4056 → BT1 LiPo → MT3608 boost → 5V rail
- MCU zone: ESP32-DevKitC (VIN, 3.3V, GND, GPIO21/SDA, GPIO22/SCL, GPIO2), TCA9548A, LED
- SENSORS zone: 4× GY-521
- No AP2112K, no external AMS1117

### Task 6: Update `CLAUDE.md` if it references bare WROOM
**File:** `CLAUDE.md`

Check for any bare WROOM references and update to dev board if found.

### Task 7: Update `docs/AGENTS.md` if it references power topology
**File:** `docs/AGENTS.md`

Check for power topology references and update.

## Tests / Validation

- **Grep check:** Run `grep -r "AP2112K" docs/ images/` → should return no matches after updates
- **Grep check:** Run `grep -r "bare WROOM" docs/` → should return no matches
- **Grep check:** Run `grep -r "WROOM-32" docs/ images/` → should only appear in session history, not active docs
- **JSON valid:** `python -c "import json; json.load(open(r'docs/images/tremor_monitor_schematic_v3.excalidraw', encoding='utf-8'))"` → "JSON valid"

## Risks, Tradeoffs, and Open Questions

- **Session history:** `sessions/session-ses_fbc7.md` contains extensive WROOM/AP2112K references but is historical record — do NOT modify
- **Generated schematic v2 PNG:** `tremor_monitor_schematic_v2.png` will be stale — regenerate or leave as reference
- **Backward compatibility:** If user reverts to bare WROOM later, these docs will need reverting
