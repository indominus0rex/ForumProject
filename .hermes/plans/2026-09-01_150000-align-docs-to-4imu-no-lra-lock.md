# Plan: Align physical-design docs with locked 4-IMU no-LRA config

**Goal:** Make every physical-design document in the repo consistent with the 2026-08-27 locked configuration — 4 IMUs (CH0 dorsal wrist, CH1 thenar volar, CH2 thumb proximal phalanx 20° dorsal-radial, CH3 index proximal phalanx dorsal), LRAs deferred, no LRA hardware this build.

**Current context / assumptions:**
The lock is recorded in `PIN_ASSIGNMENTS.md:45`, `imu_lra_placement.txt:40`, `component_positions.txt:13`, `knowledge.md:47`, `WIRING_DIAGRAM_DESIGN.md:26`, and `cad/connections_4imu.csv`. These are already correct. The problem: older docs still describe a 1-IMU + 1-LRA or 3-IMU + 3-LRA baseline, so a newcomer building from `assembly_checklist.md` or `strap_and_lra_design.md` would wire the wrong hardware. This plan updates the stale docs only — no firmware, no netlist, no new design.

**Architecture / proposed approach:**
Doc-by-doc cleanup. For each stale file, update the IMU count to 4, remove or annotate LRA content as "deferred," add the index-phalanx location, and point to the canonical lock docs. Keep changes surgical — don't rewrite whole sections, just fix the lines that contradict the lock. Each task below is one file, 2–5 minutes.

---

## Tasks

### T1 — `docs/strap_and_lra_design.md`
Section 2 "LRA Mounting (Three actuator locations)" and Section 3 BOM are wrong.
- Section 1: change "2 IMUs" framing to 4 IMUs. Add index proximal phalanx dorsal as a 4th pocket location (cut 26×26 mm like the other IMU pockets). Update materials table Qty for mesh/Velcro/thread to ×4.
- Section 2: replace "Three actuator locations" with **"LRA Mounting — DEFERRED for this build."** Keep the pocket dimensions and wiring notes as reference, but prefix: "LRAs are not populated in the current build. GPIO25/18/19/20 left unpopulated. The following is retained for when actuators are procured." Remove the 3-location strap option or relabel as future.
- Section 3 BOM table: change title to "Full Set – 4 IMUs (LRAs deferred)." Remove LRA rows or group them under "Deferred." Update elastic fabric total to ~0.40 m (4 IMU straps), mesh to 0.12 m × 0.12 m, Velcro to 0.20 m. Drop JST-PH / silicone grip dots to deferred section.
- Section 4 construction steps: renumber, remove LRA soldering/PWM steps or move to "deferred" subsection. Step 10 test: drop "Run a quick PWM test on LRAs."
- Verify: `grep -n "LRA\|2 IMU\|three\|3 " docs/strap_and_lra_design.md` shows only deferred/future references.

### T2 — `docs/breathable_imu_mount_design.md`
Only lists 3 IMU pockets (dorsum, thenar, thumb CMC).
- "IMU Integration" bullet list: change "Thumb CMC joint" → "Thumb proximal phalanx, dorsal-radial 20° tilt" and add "Index proximal phalanx, dorsal" as 4th pocket.
- Pocket dimensions: add 22×22×4 mm for index (same as dorsum/thenar).
- Verify: `grep -c "IMU pockets\|22mm" docs/breathable_imu_mount_design.md` shows 4 locations.

### T3 — `docs/strapping_materials.txt`
Only 3 locations, no index finger.
- Add row: `Index proximal phalanx (dorsal) | 3M Micropore or Hypafix (~1 cm squares) | Double-sided medical adhesive disc, narrow kinesiology tape | Small bony prominence, secure without restricting finger flexion, keep clear of PIP joint motion`.
- Add 20° tilt note to thumb row: append "(dorsal-radial 20° tilt toward nail)" to the Location cell.
- Verify: `grep -c "phalanx\|eminence\|Dorsum" docs/strapping_materials.txt` = 4.

### T4 — `docs/refined_hardware_design.md`
This is a pre-lock (2026-08-21) research-synthesis doc recommending CMC + LRA array. Don't rewrite — add a banner.
- Insert at top under the heading: "> **Superseded by 2026-08-27 lock:** IMU placement is locked at thumb proximal phalanx 20° + index proximal phalanx (not CMC), and LRAs are deferred. See `imu_lra_placement.txt:40` and `PIN_ASSIGNMENTS.md:45`. The research references below remain valid context."
- Verify: `head -5 docs/refined_hardware_design.md` shows the banner.

### T5 — `docs/assembly_checklist.md`
Framed around 1 IMU + 1 LRA as baseline, multi-IMU as "optional upgrade." Invert this.
- Phase 1: change "Recommended first build" to **4 IMUs via TCA9548A, no LRA** (matching `connections_4imu.csv`). Move 1-IMU build to "minimal smoke-test only."
- Phase 2 parts check: GY-521 → 4×, TCA9548A → add 1×, LRA/MOSFET/diode → move to "deferred" sub-bullet, add 0.1 µF caps → 4×.
- Phase 4 pocket table: add IMU pocket for index phalanx. Move LRA pocket row to a "deferred" table.
- Phase 5 (wire IMU): add TCA9548A wiring (VCC, GND, SCL, SDA, A0-A2→GND, EN→3.3V) and per-channel IMU wiring. Reference `connections_4imu.csv`.
- Phase 6 (haptic driver): prefix "DEFERRED — no LRA this build. Retain for when actuators are procured."
- Phase 12 (multi-LRA upgrade): already optional, fine as future path.
- Phase 13 (multi-IMU upgrade): **delete or replace** with "Already baseline — see Phase 1. This phase is current config, not upgrade."
- Verify: `grep -n "1 ×\|optional multi-IMU\|first prototype" docs/assembly_checklist.md` shows these are removed or relabeled.

### T6 — `docs/validation_test_procedures_elastic_strap_velcro.md`
References IMU/LRA pockets and LRA mass (~3g) in test setup.
- Section 3.1: change test weights to "IMU (~8g) ×4, no actuator this build." Remove LRA mass.
- Section 3.1 static loads: add index-phalanx load case (0.3N dorsal, 0.2N radial) alongside the dorsum/thenar cases.
- Section 4.1 comfort test: change "IMU/LRA pockets (non-functional dummy weights)" → "4 IMU pockets with dummy weights (~8g each), no actuator."
- Verify: `grep -n "LRA\|3g\|actuator" docs/validation_test_procedures_elastic_strap_velcro.md` shows only deferred/future refs.

### T7 — `cad/README.md`
Component placement table has GY-521 ×1, LRA_COIN ×1.
- Placement table: change to 4 GY-521 entries (different X/Y per `build_assembly.py` if updated, or note "TBD per hand locations"). Move LRA_COIN to a "deferred" subsection.
- "Pitfalls" section: update "Vendor parts (ESP32, GY-521) not auto-generated" → note 4 IMUs needed.
- Verify: `grep -n "GY-521\|LRA_COIN" cad/README.md` shows 4 IMU entries, LRA deferred.

### T8 — `cad/DRAWING_CHECKLIST.md`
BOM lists GY-521 ×1, LRA coin ×1.
- Balloon callouts: change GY-521 → 4× (or "GY-521 ×4"), remove LRA coin or mark deferred.
- Optional Sheet 3 BOM: GY-521 x4, LRA coin → deferred / "not this build."
- Verify: `grep -n "GY-521\|LRA" cad/DRAWING_CHECKLIST.md` shows 4 IMUs, LRA deferred.

---

## Tests / validation
This is a docs-only change. Verification per-task is `grep` checks above. Final sweep:
```
grep -rn "1 LRA\|3 LRA\|three LRA\|thumb CMC\|1 × MPU\|single IMU" docs/ cad/ \
  | grep -v "deferred\|future\|retained\|optional\|Superseded"
```
should return zero lines. Commit after each file or one commit per logical group (strap docs, cad docs, checklist).

## Risks, tradeoffs, open questions
- `refined_hardware_design.md` contains genuine research (CMC + LRA array have evidence). The banner preserves it without letting it mislead the build. Tradeoff: two docs now say different things — lock wins.
- `build_parts.py` / `build_assembly.py` still generate 1 IMU + 1 LRA. Updating CAD models is out of scope here (separate task). `cad/README.md` text will be consistent with itself but not with the scripts until scripts are updated.
- Strap pocket dimensions for index phalanx: assumed same 26×26 mm as other IMU pockets. If the index phalanx is smaller, pocket may need trim — verify with real GY-521 on hand before cutting.
