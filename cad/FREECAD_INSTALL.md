# FreeCAD Install + Run

## Install FreeCAD

Download from https://www.freecad.org/downloads.php (Windows installer recommended).

Default install: `C:\Program Files\FreeCAD 0.21\bin\FreeCAD.exe`

After install, verify `freecadcmd` is on PATH:
```
freecadcmd --version
```

If not on PATH, use full path:
```
"C:\Program Files\FreeCAD 0.21\bin\freecadcmd.exe" C:\ForumProject\cad\build_parts.py
```

## Run the build pipeline

```
cd C:\ForumProject\cad
freecadcmd build_parts.py     # generates parts in parts/
freecadcmd build_assembly.py  # generates assembly in assembly/
```

## What gets produced

- `parts/perfboard.step` + `.stl`
- `parts/RES_220.step` + `.stl`
- `parts/RES_10K.step` + `.stl`
- `parts/LED_5MM.step` + `.stl`
- `parts/2N7000.step` + `.stl`
- `parts/1N4148.step` + `.stl`
- `parts/LRA_COIN.step` + `.stl`
- `assembly/tremor_assembly.step`
- All parts also saved as `.FCStd` (FreeCAD native)

## Vendor parts

ESP32-S3-Kaluga-1 and GY-521 are not auto-generated — you need real STEPs:

1. Search GrabCAD or TraceParts for:
   - "ESP32-S3 USB-C" (Espressif official, ~30×26 mm) — optional vendor STEP
   - "GY-521" or "MPU6050 breakout board"
2. Download STEP files
3. Save to `parts/_vendor/`:
   - `parts/_vendor/ESP32-S3-Kaluga-1.step` (user-supplied; no official STEP)
4. Re-run `build_assembly.py`

Without vendor STEPs, assembly script still runs but skips those two components (with [SKIP] messages).

## Troubleshooting

- "No module named FreeCAD" — install FreeCAD or use `freecadcmd` instead of `python`
- Parts render as cylinders only — make sure `recompute()` runs at end of each `make_*` function
- Wires render as thin lines, not tubes — FreeCAD limitation. Use Draft.make_wire (BSpline) and increase LineWidth in view properties for thicker appearance. For real 3D wires, use Part.makePipe with a circular profile (advanced).
- Import error on Draft — older FreeCAD uses `Draft.makeWire` (camelCase), newer uses `Draft.make_wire`. Script uses `_wire`.
