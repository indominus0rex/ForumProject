# Scheme It Diagram — Quick Reference Tables

**Created:** 2026-09-01
**Goal:** A printable reference table set for manually building the 4-IMU ESP32 wiring diagram in DigiKey Scheme It.

---

## Current Context / Assumptions

- **Tool:** DigiKey Scheme It (https://www.digikey.com/en/schemeit/project) — browser-based, 700+ symbols, custom symbol editor, exports SVG/PNG/PDF/KiCad
- **Existing plan:** `.hermes/plans/2026-09-01_schemeit-wiring-diagram-tutorial.md` — detailed step-by-step tutorial (401 lines)
- **Connection table:** `docs/images/connection_table.md` — full net list (29 connections)
- **Firmware config:** `firmware/common/config.py` — SDA=GPIO21, SCL=GPIO22, LED=GPIO2, TCA9548A @0x70, 4× GY-521 @0x68

---

## Architecture / Proposed Approach

Three reference tables printed and placed next to the monitor while working in Scheme It:
1. **Component Placement Table** — what symbols to find and where to position them
2. **Wiring Table** — which pins to connect, in order
3. **Label Table** — exact text to add inside/outside each box

---

## Step-by-Step Tasks

### Task 1: Prepare reference materials

**Steps:**
1. Print this plan (or open on second monitor)
2. Open https://www.digikey.com/en/schemeit/project in browser
3. Click **New → Blank Project**
4. Resize canvas: **File → Page Setup → Width: 1200, Height: 700**

**Expected result:** Blank canvas 1200×700.

**Verification:** Canvas visible, grid enabled.

---

### Task 2: Place all components (use Component Placement Table)

| RefDes | Component | Symbol Name | Search Term | Position (x, y) | Width | Height |
|--------|-----------|-------------|-------------|-----------------|-------|--------|
| U1 | ESP32-DevKitC | ESP32-WROOM-32 or MCU | `ESP32` or `MCU` | (100, 100) | 200 | 160 |
| U2 | TCA9548A | I2C Multiplexer | `TCA9548` or `I2C mux` | (400, 150) | 180 | 120 |
| U3 | GY-521 CH0 | MPU6050 | `MPU6050` or `accelerometer` | (700, 60) | 150 | 80 |
| U4 | GY-521 CH1 | MPU6050 | `MPU6050` or `accelerometer` | (700, 160) | 150 | 80 |
| U5 | GY-521 CH2 | MPU6050 | `MPU6050` or `accelerometer` | (700, 260) | 150 | 80 |
| U6 | GY-521 CH3 | MPU6050 | `MPU6050` or `accelerometer` | (700, 360) | 150 | 80 |
| D1 | LED | LED | `LED` | (700, 480) | 100 | 50 |
| J1 | Micro-USB | USB Connector | `USB` | (100, 320) | 100 | 60 |
| U7 | MCP73831 | LiPo Charger | `MCP73831` or `charger` | (100, 420) | 120 | 70 |
| BT1 | LiPo Battery | Battery | `Battery` | (100, 520) | 100 | 50 |
| U8 | AP2112K-3.3 | LDO Regulator | `LDO` or `regulator` | (260, 420) | 120 | 70 |
| C1 | 4.7µF Cap | Capacitor | `Capacitor` | (260, 510) | 60 | 40 |
| C2 | 4.7µF Cap | Capacitor | `Capacitor` | (340, 510) | 60 | 40 |

**Expected result:** 13 components placed on canvas.

**Verification:** All components visible, no overlaps.

---

### Task 3: Draw power rails

| Net | Start (x, y) | End (x, y) | Style | Color |
|-----|--------------|------------|-------|-------|
| 3.3V | (40, 620) | (1150, 620) | Solid, 2.5px | Red |
| GND | (40, 650) | (1150, 650) | Solid, 2.5px | Black |

**Expected result:** Two horizontal lines at bottom.

**Verification:** Lines span full width.

---

### Task 4: Draw all wires (use Wiring Table)

| Wire ID | Net Name | From | To | Points | Style |
|---------|----------|------|----|--------|-------|
| W01 | USB_5V | J1 pin 1 | U7 pin 1 | M (100,350) L (100,430) | Solid |
| W02 | VBAT | U7 pin 3 | BT1 (+) | M (220,430) L (260,430) L (260,545) L (100,545) | Solid |
| W03 | VBAT | U7 pin 3 | U8 pin 1 | M (220,430) L (260,430) | Solid |
| W04 | 3.3V | U8 pin 3 | ESP32 3.3V | M (380,430) L (420,430) L (420,200) L (100,200) | Solid |
| W05 | 3.3V | U8 pin 3 | U2 VIN | M (380,430) L (420,430) L (420,220) L (400,220) | Solid |
| W06 | 3.3V | U8 pin 3 | U3 VCC | M (380,430) L (700,430) L (700,80) | Solid |
| W07 | 3.3V | U8 pin 3 | U4 VCC | M (380,430) L (700,430) L (700,180) | Solid |
| W08 | 3.3V | U8 pin 3 | U5 VCC | M (380,430) L (700,430) L (700,280) | Solid |
| W09 | 3.3V | U8 pin 3 | U6 VCC | M (380,430) L (700,430) L (700,380) | Solid |
| W10 | GND | J1 pin 5 | GND bus | M (100,380) L (100,650) | Solid |
| W11 | GND | U7 pin 2 | GND bus | M (100,450) L (100,650) | Solid |
| W12 | GND | U8 pin 2 | GND bus | M (260,450) L (260,650) | Solid |
| W13 | GND | BT1 (-) | GND bus | M (100,560) L (100,650) | Solid |
| W14 | GND | ESP32 GND | GND bus | M (100,230) L (100,650) | Solid |
| W15 | GND | U2 GND | GND bus | M (400,250) L (400,650) | Solid |
| W16 | GND | U3 GND | GND bus | M (700,120) L (700,650) | Solid |
| W17 | GND | U4 GND | GND bus | M (700,220) L (700,650) | Solid |
| W18 | GND | U5 GND | GND bus | M (700,320) L (700,650) | Solid |
| W19 | GND | U6 GND | GND bus | M (700,420) L (700,650) | Solid |
| W20 | SDA21 | ESP32 GPIO21 | U2 SDA | M (100,170) L (350,170) L (350,190) L (400,190) | Solid |
| W21 | SCL22 | ESP32 GPIO22 | U2 SCL | M (100,190) L (350,190) L (350,210) L (400,210) | Solid |
| W22 | CH0_SDA | U2 SD0 | U3 SDA | M (580,190) L (650,190) L (650,90) L (700,90) | Solid |
| W23 | CH0_SCL | U2 SC0 | U3 SCL | M (580,210) L (650,210) L (650,100) L (700,100) | Solid |
| W24 | CH1_SDA | U2 SD1 | U4 SDA | M (580,210) L (650,210) L (650,190) L (700,190) | Solid |
| W25 | CH1_SCL | U2 SC1 | U4 SCL | M (580,230) L (650,230) L (650,200) L (700,200) | Solid |
| W26 | CH2_SDA | U2 SD2 | U5 SDA | M (580,230) L (650,230) L (650,290) L (700,290) | Solid |
| W27 | CH2_SCL | U2 SC2 | U5 SCL | M (580,250) L (650,250) L (650,300) L (700,300) | Solid |
| W28 | CH3_SDA | U2 SD3 | U6 SDA | M (580,250) L (650,250) L (650,390) L (700,390) | Solid |
| W29 | CH3_SCL | U2 SC3 | U6 SCL | M (580,270) L (650,270) L (650,400) L (700,400) | Solid |
| W30 | LED | ESP32 GPIO2 | D1 anode | M (100,210) L (50,210) L (50,500) L (700,500) | Solid |

**Expected result:** 30 wires connecting all components.

**Verification:** All wires connect pin-to-pin, no crossings.

---

### Task 5: Add labels (use Label Table)

| RefDes | Inside Label | Outside Label | Font Size |
|--------|--------------|---------------|-----------|
| U1 | "ESP32-DevKitC\nI²C0 @400kHz\n100Hz · 128 samples" | — | 11pt bold + 9pt |
| U2 | "TCA9548A\n@0x70\nA0/A1/A2→GND · EN→3.3V" | — | 11pt bold + 9pt |
| U3 | "GY-521 CH0\n@0x68 · AD0→GND" | "Dorsal Wrist Proximal · Primary" | 11pt + 8.5pt gray |
| U4 | "GY-521 CH1\n@0x68 · AD0→GND" | "Thenar Volar · Thumb Base" | 11pt + 8.5pt gray |
| U5 | "GY-521 CH2\n@0x68 · AD0→GND" | "Thumb Phalanx · 20° tilt · Pill 4-6Hz" | 11pt + 8.5pt gray |
| U6 | "GY-521 CH3\n@0x68 · AD0→GND" | "Index Phalanx · ET 6-8Hz" | 11pt + 8.5pt gray |
| D1 | "LED\nGPIO2 → 220Ω → GND" | — | 11pt |
| J1 | "Micro-USB\nCharging Only" | — | 11pt |
| U7 | "MCP73831\nLiPo Charger" | — | 11pt |
| BT1 | "LiPo Battery\n3.7V · 500mAh+" | — | 11pt |
| U8 | "AP2112K-3.3\nLDO 3.3V · 600mA" | — | 11pt |
| C1 | "C1 · 4.7µF" | — | 9pt |
| C2 | "C2 · 4.7µF" | — | 9pt |

**Expected result:** All components labeled with technical details.

**Verification:** Labels legible, no overlapping text.

---

### Task 6: Add title block and notes

| Element | Position | Content | Font |
|---------|----------|---------|------|
| Title | (300, 10) | "Wiring Diagram — 4-IMU ESP32 Tremor Monitor" | 20pt bold |
| Subtitle | (300, 35) | "ESP32-DevKitC · TCA9548A · 4× GY-521 · LiPo Power" | 12pt monospace |
| Subtitle 2 | (300, 55) | "I²C0 @400kHz · 100Hz · 128-sample window · Rev 2026-09-01" | 12pt monospace |
| Notes | (40, 680) | "VCC 3.3V · I²C 400kHz · TCA9548A @0x70 · GY-521 @0x68 via mux · Wire <15cm · 0.1µF per IC · LRA GPIO25/18/19/20 NC" | 10pt monospace |

**Expected result:** Title block at top, notes at bottom.

**Verification:** All text legible.

---

### Task 7: Save and export

**Steps:**
1. Click **Save** → Name: `ESP32_4IMU_Tremor_Monitor_Wiring_Diagram`
2. Click **Export** → Select **SVG** → Filename: `wiring_diagram_4imu_schemeit.svg`
3. Click **Export** → Select **PNG** → Filename: `wiring_diagram_4imu_schemeit.png`
4. Save to `docs/images/`

**Expected result:** SVG and PNG files downloaded.

**Verification:** Files open correctly.

---

## Tests / Validation

1. **Visual inspection:** All 13 components visible, 30 wires connect pin-to-pin, labels legible.
2. **Firmware cross-reference:** All pin numbers, addresses, and parameters match `firmware/common/config.py`.
3. **Export verification:** SVG opens in browser, PNG opens in image viewer.
4. **Share verification:** If shared via Scheme It link, URL opens correctly.

---

## Risks, Tradeoffs, and Open Questions

- **Symbol availability:** ESP32 and TCA9548A symbols may not exist. Mitigation: create custom symbols using built-in symbol editor.
- **Text rendering:** Scheme It may not support custom fonts. Mitigation: use built-in monospace.
- **Wire routing:** Manual routing may not achieve perfect orthogonal paths. Mitigation: use grid snapping.
- **Canvas size:** Default canvas may be too small. Mitigation: resize to 1200×700.
- **No undo for some actions:** Save frequently (Ctrl+S).

---

## Files Changed

| File | Action |
|------|--------|
| `docs/images/wiring_diagram_4imu_schemeit.svg` | Create new (export from Scheme It) |
| `docs/images/wiring_diagram_4imu_schemeit.png` | Create new (export from Scheme It) |

No existing project files modified.
