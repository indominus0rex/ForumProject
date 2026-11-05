# Plan: Simplify Power Section — Remove AP2112K, Add Single Filter Cap

**Goal:** Remove AP2112K-3.3 LDO and all capacitors, replace with a single filter capacitor connected from TP4056 OUT+ to GND bus.

## Current Context / Assumptions

- File: `docs/images/tremor_monitor_schematic_v2.excalidraw`
- Current POWER zone has: J1 (USB), U7 (TP4056), R_prog (1.2kΩ), BT1 (LiPo), U9 (AP2112K-3.3), C3 (10µF IN cap), C4 (10µF OUT cap)
- Current SENSORS zone has: C5-C8 (0.1µF decoupling caps near each IMU)
- User wants all of those removed
- Single new capacitor connects TP4056 OUT+ pad to GND bus
- The user is aware this removes voltage regulation — likely powering ESP32 directly from LiPo voltage or regulation is handled elsewhere

## Architecture / Proposed Approach

The simplified POWER zone becomes: J1 → TP4056 → BT1 (charge path), with BT1+ connecting to OUT+ and a single filter cap from OUT+ to GND. The MCU and SENSORS zones remain unchanged except the 4 IMU decoupling caps (C5-C8) are removed. All arrows to/from U9, C3, C4, C5, C6, C7, C8 must be deleted.

## Step-by-Step Tasks

### Task 1: Remove AP2112K-3.3 (U9) element
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Delete the rectangle element with id `"u9"` (the AP2112K-3.3 block at x=70, y=430, w=140, h=70).

Delete the text element with id `"t_u9"` (its label).

### Task 2: Remove C3 and C4 (LDO input/output caps)
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Delete the rectangle element with id `"c3"` (at x=240, y=430, w=60, h=30).
Delete the text element with id `"t_c3"`.
Delete the rectangle element with id `"c4"` (at x=240, y=470, w=60, h=30).
Delete the text element with id `"t_c4"`.

### Task 3: Remove C5, C6, C7, C8 (IMU decoupling caps)
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Delete the rectangle element with id `"c5"` (at x=840, y=200, w=40, h=25).
Delete the text element with id `"t_c5"`.
Delete the rectangle element with id `"c6"` (at x=1030, y=200, w=40, h=25).
Delete the text element with id `"t_c6"`.
Delete the rectangle element with id `"c7"` (at x=840, y=320, w=40, h=25).
Delete the text element with id `"t_c7"`.
Delete the rectangle element with id `"c8"` (at x=1030, y=320, w=40, h=25).
Delete the text element with id `"t_c8"`.

### Task 4: Delete arrows connected to removed components
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Delete these arrow elements:
- `"a_c3_u9"` — arrow from C3 to U9
- `"a_c4_u9"` — arrow from C4 to U9
- `"a_bat_ldo"` — arrow from BT1 to U9
- `"a_ldo_esp"` — arrow from U9 to U1 (the 3.3V power rail to ESP32)

### Task 5: Add single filter capacitor C1
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Add a new rectangle element for the filter capacitor:
```json
{
  "type": "rectangle",
  "id": "c1",
  "x": 240,
  "y": 230,
  "width": 60,
  "height": 30,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#ffd8a8",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1,
  "opacity": 100,
  "roundness": { "type": 3 },
  "boundElements": [{ "id": "t_c1", "type": "text" }]
}
```

Add its label text element:
```json
{
  "type": "text",
  "id": "t_c1",
  "x": 245,
  "y": 235,
  "width": 50,
  "height": 20,
  "text": "C1\n10µF",
  "fontSize": 14,
  "fontFamily": 1,
  "strokeColor": "#1e1e1e",
  "textAlign": "center",
  "verticalAlign": "middle",
  "containerId": "c1",
  "originalText": "C1\n10µF",
  "autoResize": true
}
```

### Task 6: Wire C1 from TP4056 OUT+ to GND
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Add arrow from TP4056 to C1 (OUT+ to cap positive):
```json
{
  "type": "arrow",
  "id": "a_u7_c1",
  "x": 210,
  "y": 245,
  "width": 30,
  "height": 0,
  "strokeColor": "#e03131",
  "strokeWidth": 2,
  "roughness": 1,
  "opacity": 100,
  "points": [[0,0],[30,0]],
  "endArrowhead": "arrow",
  "startBinding": { "elementId": "u7", "fixedPoint": [1, 0.5] },
  "endBinding": { "elementId": "c1", "fixedPoint": [0, 0.5] },
  "boundElements": [{ "id": "t_a_u7_c1", "type": "text" }]
}
```

Add label for that arrow:
```json
{
  "type": "text",
  "id": "t_a_u7_c1",
  "x": 215,
  "y": 230,
  "width": 30,
  "height": 15,
  "text": "OUT+",
  "fontSize": 12,
  "fontFamily": 1,
  "strokeColor": "#e03131",
  "textAlign": "center",
  "verticalAlign": "middle",
  "containerId": "a_u7_c1",
  "originalText": "OUT+",
  "autoResize": true
}
```

Add arrow from C1 to GND (cap negative to ground):
```json
{
  "type": "arrow",
  "id": "a_c1_gnd",
  "x": 270,
  "y": 260,
  "width": 0,
  "height": 30,
  "strokeColor": "#1e1e1e",
  "strokeWidth": 2,
  "roughness": 1,
  "opacity": 100,
  "points": [[0,0],[0,30]],
  "endArrowhead": "arrow",
  "startBinding": { "elementId": "c1", "fixedPoint": [0.5, 1] },
  "boundElements": [{ "id": "t_a_c1_gnd", "type": "text" }]
}
```

Add label for that arrow:
```json
{
  "type": "text",
  "id": "t_a_c1_gnd",
  "x": 275,
  "y": 270,
  "width": 30,
  "height": 15,
  "text": "GND",
  "fontSize": 12,
  "fontFamily": 1,
  "strokeColor": "#1e1e1e",
  "textAlign": "left",
  "verticalAlign": "middle",
  "containerId": "a_c1_gnd",
  "originalText": "GND",
  "autoResize": true
}
```

### Task 7: Add wire from BT1+ to OUT+ junction
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Add arrow from BT1 to C1 (battery positive to filter cap — the power delivery path):
```json
{
  "type": "arrow",
  "id": "a_bt1_c1",
  "x": 210,
  "y": 330,
  "width": 0,
  "height": -70,
  "strokeColor": "#e03131",
  "strokeWidth": 3,
  "roughness": 1,
  "opacity": 100,
  "points": [[0,0],[0,-70]],
  "endArrowhead": "none",
  "startBinding": { "elementId": "bt1", "fixedPoint": [0.5, 0] },
  "endBinding": { "elementId": "c1", "fixedPoint": [0.5, 1] },
  "boundElements": [{ "id": "t_a_bt1_c1", "type": "text" }]
}
```

Add label for that arrow:
```json
{
  "type": "text",
  "id": "t_a_bt1_c1",
  "x": 215,
  "y": 295,
  "width": 30,
  "height": 15,
  "text": "BAT+",
  "fontSize": 12,
  "fontFamily": 1,
  "strokeColor": "#e03131",
  "textAlign": "left",
  "verticalAlign": "middle",
  "containerId": "a_bt1_c1",
  "originalText": "BAT+",
  "autoResize": true
}
```

### Task 8: Update subtitle text
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Update the subtitle text element to reflect the change:
- Change `"text"` from: `"Bare ESP32-WROOM-32 · TCA9548A @0x70 · 4× GY-521 · AP2112K-3.3 LDO · I2C0 @400kHz"`
- Change `"originalText"` from: same as above
- New text: `"Bare ESP32-WROOM-32 · TCA9548A @0x70 · 4× GY-521 · TP4056 + LiPo · I2C0 @400kHz"`

### Task 9: Validate JSON
**File:** `docs/images/tremor_monitor_schematic_v2.excalidraw`

Run `python -c "import json; json.load(open(r'docs/images/tremor_monitor_schematic_v2.excalidraw', encoding='utf-8')); print('JSON valid')"` to confirm the file is still valid JSON after all edits.

Expected output: `JSON valid`

## Tests / Validation

- **JSON validity:** `python -c "import json; json.load(open(r'docs/images/tremor_monitor_schematic_v2.excalidraw'))"` → must print "JSON valid"
- **Element count check:** Before: 84 elements. After removing 11 elements (u9, t_u9, c3, t_c3, c4, t_c4, c5, t_c5, c6, t_c6, c7, t_c7, c8, t_c8 = 14 elements removed) and adding 7 new (c1, t_c1, a_u7_c1, t_a_u7_c1, a_c1_gnd, t_a_c1_gnd, a_bt1_c1, t_a_bt1_c1 = 8 new, plus 1 updated subtitle = net -5 elements). Final: ~79 elements.
- **No dangling bindings:** Check that no arrow references a deleted elementId. Specifically: a_c3_u9 and a_c4_u9 must be deleted, a_bat_ldo and a_esp_ldo must be deleted.
- **Visual check:** Open in excalidraw.com — C1 should sit between TP4056 and GND, BT1+ should connect to C1.

## Risks, Tradeoffs, and Open Questions

- **No voltage regulation:** Without AP2112K, the ESP32 gets raw LiPo voltage (3.0-4.2V). The ESP32-WROOM-32 is rated 3.0-3.6V on 3V3 pin. 4.2V fully charged LiPo exceeds this. User may need to confirm this is intentional or add regulation elsewhere.
- **Single 10µF filter cap:** Minimal filtering. May need more bulk capacitance in practice for stable ESP32 WiFi operation.
- **TP4056 OUT+ availability:** This plan assumes the TP4056 module has separate OUT+ pads (DW01 protection version). If the user has the basic 4-pin module (IN+, IN-, B+, B-), OUT+ does not exist and the cap would connect between B+ and B- directly.
