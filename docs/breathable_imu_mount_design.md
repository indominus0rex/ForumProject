# Breathable IMU Mount Design

Elastic fabric IMU mount inspired by bicycle gloves but optimized for breathability:

## Materials
- Base: Lightweight moisture-wicking mesh (polyester/nylon spacer fabric) 3D mesh for airflow
- Palm: Perforated synthetic leather or grip-enhancing mesh with micro-vents
- Back: 80% open mesh for maximum ventilation
- Wrist: Wide elastic band with hook-and-loop closure
- Material: Coolmax or similar performance fabric, 4-way stretch, antimicrobial treatment

## IMU Integration
- IMU pockets: Sewn rectangular openings (22mm x 22mm x 4mm) at:
  - CH0 — Dorsum hand center (over 3rd metacarpal bone)
  - CH1 — Thenar eminence (palmar base of thumb)
  - CH2 — Thumb proximal phalanx (dorsal-radial 20° tilt toward nail)
  - CH3 — Index proximal phalanx (dorsal)
- Pocket dimensions: 22×22×4 mm for all four locations (including index phalanx).
- Pocket flaps: Overlapping mesh panels with hook-and-loop tabs for removable sensor access

## Features
- Anatomically curved fingers, pre-curved palm
- Minimal seams to reduce irritation
- Breathable construction for extended wear
- Removable IMU boards for maintenance/replacement
- Replaceable strap as needed

## Implementation Notes
1. Source elastic mesh fabrics (3D spacer mesh, perforated synthetic leather)
2. Cut pattern for glove shape with pre-curve
3. Sew rectangular pockets for IMU placement
4. Create overlapping flap closures with hook-and-loop tape
5. Assemble with wide elastic wristband and hook-and-loop closure
6. Test fit with actual IMU boards (e.g., GY-521 MPU6050 ~20x20mm) and elastic strap
7. Adjust pocket size if needed for specific IMU breakout board

## Related Projects
- Forum Project tremor monitoring system
- Hardware design research (docs/hardware_design_research.md)
- Refined hardware design (docs/refined_hardware_design.md)