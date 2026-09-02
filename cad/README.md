# cad/

SolidWorks + FreeCAD source for the tremor-detection wiring diagram 3D model.

## Quick start (FreeCAD — recommended)

1. Install FreeCAD 0.21+ (https://www.freecad.org)
2. Drop vendor STEPs in `parts/_vendor/` (see `FREECAD_INSTALL.md`)
3. Run:
   ```
   cd C:\ForumProject\cad
   freecadcmd build_parts.py
   freecadcmd build_assembly.py
   ```

## Quick start (SolidWorks)

1. Install SolidWorks from `C:\ForumProject\SolidWorksSetup.exe`
2. Follow `SOLIDWORKS_MANUAL.md` step by step
3. Run `perfboard_grid.swp` first (Tools > Macro > Run)

## Files in this folder

### Build scripts (FreeCAD)
- `build_parts.py` — Parametric parts: perfboard, resistors, LED, 2N7000, 1N4148, LRA. Exports STEP + STL + FCStd.
- `build_assembly.py` — Places all parts at predefined positions on perfboard, routes 16 wires per `connections.csv`.
- `_lib/parse_connections.py` — CSV parser used by both scripts.

### Data
- `connections.csv` — Netlist derived from `wiring_diagram.jpg`. 16 wires with color codes.

### SolidWorks
- `perfboard_grid.swp` — VBA macro: auto-generates perfboard with 30x15 hole grid.

### Docs
- `SOLIDWORKS_MANUAL.md` — Step-by-step guide for SolidWorks users.
- `FREECAD_INSTALL.md` — FreeCAD install + troubleshooting.
- `DRAWING_CHECKLIST.md` — SLDDRW / TechDraw checklist (title block, balloons, BOM).

### Output dirs (created on first run)
- `parts/` — individual .step / .stl / .FCStd
- `parts/_vendor/` — user-supplied STEPs (ESP32, GY-521)
- `assembly/` — top-level assembly .step / .FCStd
- `drawings/` — SLDDRW (manual, SolidWorks)

## Component placement (from build_assembly.py)

| Component | X (mm) | Y (mm) | Rotation |
|---|---|---|---|
| ESP32-DevKitC | -25 | -8 | 0° |
| GY-521 (CH0, dorsal wrist) | 22 | 8 | 0° |
| GY-521 (CH1, thenar volar) | 28 | 12 | 0° |
| GY-521 (CH2, thumb proximal phalanx) | 34 | 6 | 20° |
| GY-521 (CH3, index proximal phalanx) | 40 | 10 | 0° |
| RES_220 | -10 | -10 | 30° |
| RES_10K | -5 | 10 | 60° |
| LED_5MM | -15 | 12 | 90° |
| 2N7000 | 8 | -5 | 0° |
| 1N4148 | 5 | 5 | 45° |

### Deferred (not this build)
| Component | X (mm) | Y (mm) | Rotation |
|---|---|---|---|
| LRA_COIN | 15 | -10 | 0° |

Adjust positions in `COMPONENT_POSITIONS` dict in `build_assembly.py` if your real build differs.

## Wire colors

- red = 3V3 power rail
- black = GND
- yellow = signal (GPIO drive)
- blue = I2C (SDA/SCL)

## Pitfalls

- Vendor parts (ESP32, 4× GY-521) not auto-generated — need real STEPs from GrabCAD.
- FreeCAD wires render as lines (not 3D tubes). SolidWorks sweep gives real 3D wires.
- ESP32-DevKitC has two form factors (30-pin and 36-pin DevKitC v4). Match your real board.
- LRA dimensions vary by manufacturer — current model assumes Ø10mm × 2.7mm coin.
- 1N4148 cathode band position: in current model, band is on +X end of body. Verify orientation matches your actual diode.
