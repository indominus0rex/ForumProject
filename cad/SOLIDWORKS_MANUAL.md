# SolidWorks Manual — finish the assembly

If you prefer SolidWorks over FreeCAD, follow this. FreeCAD scripts in this folder do the equivalent automatically; this is for SW users.

## Prerequisites

- SolidWorks 2020 or newer (your `SolidWorksSetup.exe` is the installer)
- Vendor STEP files in `parts/_vendor/`:
  - `ESP32-S3-Kaluga-1.step` — GrabCAD/TraceParts search "ESP32-S3 USB-C" (optional vendor STEP)
  - `GY-521.step` — search "GY-521" or "MPU6050 breakout"
- Run `perfboard_grid.swp` first (Tools > Macro > Run) to generate perfboard

## Steps

### 1. Build simple parts

For each of these, open SolidWorks, mm units, model from scratch or use the dimensions in `build_parts.py` as reference:

- `RES_220.SLDPRT` — axial resistor, 6.3mm × Ø2.3mm body, 0.6mm leads
- `RES_10K.SLDPRT` — same dimensions, different color bands
- `LED_5MM.SLDPRT` — 5mm LED, Ø5mm dome, Ø5.6mm flange
- `2N7000.SLDPRT` — TO-92, half-cylinder Ø2.4mm × 4mm, 3 leads
- `1N4148.SLDPRT` — DO-35, Ø1.85mm × 3.6mm glass body, cathode band
- `LRA_COIN.SLDPRT` — Ø10mm × 2.7mm cylinder, 2 pads

Save all to `parts/`.

### 2. Import vendor parts

For each STEP in `parts/_vendor/`:
1. File > Open > pick STEP
2. File > Save As > `parts/<NAME>.SLDPRT` (auto-converts)
3. Done — SW embeds the geometry as a single imported feature

### 3. Create assembly

1. File > New > Assembly
2. Save as `assembly/tremor_assembly.SLDASM`
3. Insert > Component > each `.SLDPRT` from `parts/`
4. Mate the perfboard to the origin plane (coincident mate, top face to Front plane)

### 4. Place components on perfboard

For each component, use Add Mate to position:
- ESP32-S3-Kaluga-1: mate its PCB bottom to perfboard top, distance 1.6mm
- GY-521: same, place to the right of ESP32
- All passives: insert lead ends into perfboard holes
  - Use coincident mate between lead end face and hole axis
  - Distance mate to set insertion depth (e.g. 5mm below board top)

Reference positions (center of each component, in mm from perfboard center):

| Component | X | Y | Rotation (Z) |
|---|---|---|---|
| ESP32-S3-Kaluga-1 | -25 | -8 | 0° |
| GY-521 | 22 | 8 | 0° |
| RES_220 | -10 | -10 | 30° |
| RES_10K | -5 | 10 | 60° |
| LED_5MM | -15 | 12 | 90° |
| 2N7000 | 8 | -5 | 0° |
| 1N4148 | 5 | 5 | 45° |
| LRA_COIN | 15 | -10 | 0° |

### 5. Route wires

For each row in `connections.csv`:

1. Sketch on Front plane
2. Draw 3D spline from pin tip to pin tip (use "Offset Entities" to lift above board)
3. Trim ends so spline starts/ends exactly at pin tips
4. Exit sketch
5. Features > Swept Boss/Base, profile = Ø0.6mm circle
6. Right-click > Appearance > set color per CSV (red=3V3, black=GND, yellow=signal, blue=I2C)

### 6. Drawing

1. File > New > Drawing
2. Pick A3 landscape template
3. Insert > Model View > assembly
4. Add: Standard 3-View, Isometric
5. Add balloons for each component reference (View > Annotation > Balloon)
6. Add title block with: Tremor Detector Wiring 3D, date, scale 1:1, sheet 1 of 1
7. Save as `drawings/tremor_assembly.SLDDRW`

### 7. Backup

File > Pack and Go > select all references > save `.zip` to share or back up.

## Time estimate

- Vendor STEP hunt: 1h
- Model passives + LRA: 2h
- Assembly + mating: 30min
- Wire routing (16 wires): 2-3h
- Drawing: 1h

Total: one evening.
