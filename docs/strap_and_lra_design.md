# Strap and LRA Design for IMU/Haptic Mount

## Overview
This document describes a removable, adjustable mounting system for IMUs and Linear Resonant Actuators (LRAs) using:
- Elastic fabric (nylon/spandex 4‑way stretch) for conformity and comfort.
- Hook‑and‑loop (Velcro) closures for secure fastening and quick release.
- Fabric pockets with Velcro flaps that allow the sensors/actuators to be slid in/out without undoing the strap.

The design follows the recommendations in `strapping_materials.txt`, `breathable_imu_mount_design.md`, and the LRA placement notes from `imu_lra_placement.txt` and `refined_hardware_design.md`.

---
## 1. IMU Mounting (4 IMU Locations)

### 1.1 Pocket‑Style IMU Holder
- **Pocket shell**: two pieces of breathable mesh/spacer fabric (≈ 26 mm × 26 mm cut, 2 mm seam allowance) sewn on three sides, leaving one 22 mm side open.
- **Flap**: overlapping mesh piece (≈ 30 mm × 25 mm) with a 15 mm × 15 mm hook‑side Velcro on its underside.
- **Pocket interior**: matching 15 mm × 15 mm loop‑side Velcro sewn on the rim of the opening.
- **Result**: IMU (≈ 20 mm × 20 mm × 4 mm) slides into the pocket; flap folds down and presses the Velcro to secure it. Removal: peel flap, slide IMU out.

### 1.2 Attachment to Strap/Gloves
- The completed pocket/flap unit is sewn onto the elastic strap or glove base at the exact IMU location:
  - CH0 — Dorsum hand center (over 3rd metacarpal).
  - CH1 — Thenar eminence (palmar base of thumb).
  - CH2 — Thumb proximal phalanx (dorsal-radial 20° tilt toward nail).
  - CH3 — Index proximal phalanx (dorsal).
- Strap ends finished with Velcro (hook on one end, loop on the other) for adjustable closure around the wrist or hand.

### 1.3 Materials (per IMU, ×4 for full set)
| Item | Spec | Qty (×4 IMUs) |
|------|------|-----|
| Elastic nylon/spandex (30‑35 mm wide) | 4‑way stretch | ~0.40 m total |
| Breathable mesh/spacer fabric | 3D spacer or moisture‑wicking | 0.12 m × 0.12 m |
| Hook‑side Velcro (sew‑on, 15 mm) | – | 0.060 m |
| Loop‑side Velcro (sew‑on, 15 mm) | – | 0.060 m |
| Thread (polyester/nylon) | – | – |
| Optional stabilizer strip (2 mm cotton webbing) | – | 0.12 m |

---
## 2. LRA Mounting — DEFERRED for this build

> **LRAs are not populated in the current build.** GPIO25/18/19/20 left unpopulated. The following is **retained for reference** for when actuators are procured.

### 2.1 Pocket‑Style LRA Holder (retained)
- **Pocket shell**: two pieces of mesh (≈ 14 mm × 14 mm cut, 2 mm seam) sewn three sides, leaving one 12 mm side open (fits ~10 mm × 10 mm × 3‑4 mm LRA).
- **Flap**: mesh piece (≈ 18 mm × 13 mm) with a 12 mm × 12 mm hook‑side Velcro on its underside.
- **Pocket interior**: matching 12 mm × 12 mm loop‑side Velcro on the rim.
- **Optional stabilizer**: thin cotton webbing strip sewn inside bottom seam to prevent sag.

### 2.2 Attachment Options (retained)
**A. Separate LRA Strap**
- Cut a 15 mm‑wide elastic strap (~0.20‑0.25 m long).
- Sew three LRA pockets (retained for future) at the prescribed locations:
  1. Dorsal hand, between MC2‑MC3 (distal to IMU‑1).
  2. Palmar hand, beneath thenar eminence (opposite IMU‑2).
  3. Palmar hand, near hypothenar eminence (~2 cm proximal to wrist crease).
- Strap ends finished with hook/loop Velcro for adjustable wear.

**B. Integrated into IMU Glove/Base**
- Sew LRA pockets directly onto the same breathable mesh panels that hold the IMUs, at the locations above.
- Use the same elastic wrist band for closure.

### 2.3 Wiring & Strain Relief (retained)
- Use 30 AWG silicone‑insulated stranded wire (2‑core) for flexibility.
- Route wires along the inside of strap/glove, tacking down every 15 mm with a stitch or a tiny epoxy dot.
- At each LRA pocket, form a small strain‑relief loop (Ø ≈ 3 mm) and stitch it down before soldering to the actuator.
- (Optional) Crimp micro‑JST‑PH 2‑pin connectors on the strap side for quick disconnect.
- ESP32 side: wiring to PWM outputs (GPIO 18/19/20 for three‑channel drive, or GPIO 25 for single LRA as in current firmware).

### 2.4 Materials (per LRA, retained)
| Item | Spec | Qty |
|------|------|-----|
| Elastic nylon/spandex (15 mm wide) | 4‑way stretch | ~0.08 m (if separate strap) |
| Breathable mesh/spacer fabric | 3D spacer or moisture‑wicking | 0.02 m × 0.02 m |
| Hook‑side Velcro (sew‑on, 15 mm) | – | 0.012 m |
| Loop‑side Velcro (sew‑on, 15 mm) | – | 0.012 m |
| Silicone wire (30 AWG, 2‑core) | – | ~0.20 m |
| Thread (polyester/nylon) | – | – |
| Optional stabilizer strip (2 mm cotton webbing) | – | 0.015 m |
| Optional micro‑JST‑PH connectors | 2‑pin, 2 mm pitch | 1 set per LRA |
| Optional silicone grip dots | Medical‑grade, 4 mm | ~4 dots per LRA |

---
## 3. Bill of Materials (Full Set – 4 IMUs, LRAs deferred)

| Item | Spec | Total Qty | Approx. Cost (USD) |
|------|------|-----------|--------------------|
| Elastic nylon/spandex (30‑35 mm) | 4‑way stretch | 0.40 m | $3‑$5 |
| Breathable mesh/spacer fabric | 3D spacer or moisture‑wicking | 0.12 m × 0.12 m | $3‑$4 |
| Hook‑side Velcro (sew‑on, 15 mm) | – | 0.060 m | $1‑$2 |
| Loop‑side Velcro (sew‑on, 15 mm) | – | 0.060 m | $1‑$2 |
| Thread (polyester/nylon) | – | 1 small spool | $2 |
| Stabilizer strips (cotton webbing) | 2 mm | 0.12 m | $1 |
| **Total (approx.)** | – | – | **$11‑$16** |

### Deferred (not this build)
| Item | Spec | Qty |
|------|------|-----|
| Silicone wire (30 AWG, 2‑core) | – | 0.60 m |
| Micro‑JST‑PH connectors (optional) | 2‑pin | 3 sets |
| Silicone grip dots (optional) | Medical‑grade | ~24 dots |

*(If you already have elastic fabric, mesh, Velcro, and thread from earlier work, the incremental cost is mainly fabric and Velcro for 4 IMU straps.)*

---
## 4. Construction Steps (Summary)

1. **Cut fabric** for pockets and flaps according to dimensions above (add 2 mm seam allowance).
2. **Prepare Velcro** squares; sew hook side to flap underside, loop side to pocket rim.
3. **Sew pocket shells** (three‑side seam), turn right‑side out, press.
4. **Attach Velcro** to flap and pocket as described.
5. **(Optional) Sew stabilizer strip** inside pocket bottom seam.
6. **Mount pockets** onto elastic strap or glove base at the four IMU locations (CH0–CH3).
7. **Finish strap ends** with hook/loop Velcro for adjustable closure.
8. **Test**: slide IMUs into pockets, close flaps, verify secure fit and easy removal.
9. **Maintenance**: hand‑wash strap with mild soap, air‑dry, inspect Velcro for lint, replace if needed.

### Deferred steps (for when LRAs are procured)
- Route and secure wires for LRAs with stitches or epoxy dots, include strain‑relief loops.
- Solder wire ends to LRA terminals (or to connectors).
- Run a quick PWM test on LRAs to confirm haptic output.

---
## 5. Notes & Tips

- Use **super‑flexible silicone wire** to avoid fatigue where the strap bends.
- Keep **Velcro surfaces clean**; a lint roller restores grip after washing.
- If pocket sags over time, add a thin non‑stretch tape line along the bottom seam.
- For **water‑resistance**, consider a light spray‑on fabric protector (e.g., Scotchgard) – avoid covering Velcro.
- The design allows **hot‑swapping** of IMUs/LRAs for debugging or replacement without removing the mount from the hand.
- All seams should be **flat and smooth** to prevent irritation during extended wear.

*End of document*.