# LRA Design Refinement Plan (Research-Based, Components Unchanged)

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Refine the wearable tremor monitoring design with research-based improvements, keeping IMU positions and counts unchanged; LRA components may be modified for improved haptic effectiveness.

**Architecture:** Retain the validated 4-IMU (TCA9548A-multiplexed, I2C0) layout and single ESP32 firmware pipeline; refine LRA mounting, drive electronics, placement details, and haptic encoding based on peer-reviewed literature and manufacturer datasheets, without altering IMU count/placement.

**Tech Stack:** ESP32 MicroPython HSP firmware, 30AWG silicone wire, elastic nylon/spandex straps, breathable mesh, Hook-and-loop (Velcro), LRAs (10 mm × 10 mm × 3–4 mm class), SVG/ Markdown documentation.

---

## Current context / assumptions

- Hardware contract is fixed from `CLAUDE.md` and `firmware/common/config.py`:
  - **IMUs**: 4 units (`NUM_IMUS = 4`). I2C bus 0, SCL=GPIO22, SDA=GPIO21, TCA9548A addr 0x70.
  - **Fixed placements** (no change per request):
    - IMU1 – Dorsal wrist just proximal to wrist joint
    - IMU2 – Thenar eminence (palmar thumb base)
    - IMU3 – Thumb CMC joint (dorsal)
    - IMU4 – Forearm proximal wrist (1.5 cm proximal to wrist crease)
- **LRA set**: 3 units (default array mode). GPIOs 18/19/20 → [hypothenar, thenar, dorsal] per `LRA_PINS`.
- **Firmware**: `embedded_main_hsp.py` → `stages/haptic.py` drives LRAs at 200 Hz, 50% duty (LRA_DUTY_ON = 512).
- Existing docs:
  - `docs/strap_and_lra_design.md`
  - `docs/imu_lra_placement.txt`
  - `docs/refined_hardware_design.md`
  - `docs/hardware_design_research.md`

---

## Proposed approach

1. **Research synthesis** – extract evidence-based recommendations for LRA drive parameters, mounting coupling, and haptic encoding from peer-reviewed sources referenced in `docs/hardware_design_research.md`.
2. **LRA-specific refinements only** – keep IMU positions/counts unchanged; improve:
   - LRA mounting (coupling, mechanical isolation, strain relief details)
   - Electrical drive (resonance matching, PWM filtering, power decoupling)
   - Haptic encoding table (frequency/amplitude per tremor label) grounded in haptics literature
3. **Document changes** – update `docs/LRA-Assembly-Guide.md` and create a summary `reference` file with citations.

---

## Step-by-step plan

### Task 1: Audit current LRA configuration and documentation

**Objective:** Establish baseline config and docs before making research-based changes.

**Files:**
- Read: `firmware/common/config.py`
- Read: `firmware/stages/haptic.py`
- Read: `docs/strap_and_lra_design.md`
- Read: `docs/imu_lra_placement.txt`

**Step 1: Extract config values**
Run in terminal:
```
grep -n "LRA_PIN\|LRA_PINS\|LRA_FREQ\|LRA_DUTY" C:/ForumProject/firmware/common/config.py
```
Expected: `LRA_PIN = 25`, `LRA_PINS = [18, 19, 20]`, `LRA_FREQ = 200`, `LRA_DUTY_ON = 512`.

**Step 2: Verify haptic stage logic**
```
grep -n "label.*LRA\|duty" C:/ForumProject/firmware/stages/haptic.py
```
Expected: duty set to 0 or 512 based on label.

**Step 3: Commit baseline audit note**
```
git add docs/
git commit -m "docs: audit baseline LRA config and hardware docs"
```

---

### Task 2: Research LRA drive parameter optimization

**Objective:** Gather evidence for optimal drive frequency, duty, and PWM filtering to maximize perceptibility without fatigue.

**Files:**
- Read: `docs/hardware_design_research.md`
- Read: `docs/refined_hardware_design.md`

**Step 1: Identify research sources**
From `hardware_design_research.md`, extract citations on LRA resonance and haptic encoding:
- DOGlove / high-resolution LRA arrays (spatial patterning)
- Dual-spring LRA (40% improvement in displacement/force)
- Haptic feedback effectiveness relative to motor control centers

**Step 2: Summarize key findings for LRA class (10×10×3-4mm)**
- Typical resonance range: 150–250 Hz, manufacturer spec ~200 Hz.
- PWM drive at resonance maximizes displacement per current draw.
- Low-pass RC filter (e.g., 1 kΩ + 0.1 µF) reduces PWM harmonics audible on skin.

**Step 3: Document findings**
Create: `docs/references/lra-drive-optimization.md`
Content should cite chapter/section refs and note decision rules: “If LRA datasheet resonance is R Hz, set `LRA_FREQ = R` and use RC low-pass with f_cut ≈ 300 Hz.”

---

### Task 3: Refine LRA mounting for mechanical coupling

**Objective:** Improve haptic transmission without changing LRA components; ground recommendations in biomechanics/haptics research.

**Files:**
- Modify: `docs/strap_and_lra_design.md`
- Read: `docs/refined_hardware_design.md` (Sensor Coupling section)

**Step 1: Research coupling recommendations**
From `refined_hardware_design.md`:
- Use firm coupling to bone/proximal tissue to avoid soft-tissue damping.
- Biocompatible silicone encapsulation (Shore A 10–20) improves comfort and transmission.

**Step 2: Update mounting instructions**
In `docs/strap_and_lra_design.md`, add:
- For dorsal LRA (between MC2–MC3): add 2 mm silicone pad beneath LRA pocket to improve transmission.
- For palmar LRAs (thenar/hypothenar): use thin (1 mm) silicone grip dots (medical-grade 4 mm) inside pocket to increase skin contact and reduce slip.
- Keep LRA pocket closed with ≥5 mm flap overlap to prevent movement artifacts.

**Step 3: Validate pocket dimensions still fit**
Verify pocket shell 14×14 mm cut still accommodates LRA + silicone pad (10 mm internal + 2 mm seam = 14 mm). No change to components.

---

### Task 4: Update wiring and strain relief best practices

**Objective:** Reduce wire fatigue and electrical noise, research-based.

**Files:**
- Modify: `docs/lra-wiring-instructions.md`
- Read: `docs/refined_hardware_design.md` section on Electrical Improvements

**Step 1: Adopt recommendations**
- Add 0.1 µF decoupling caps near each LRA? Actually per `refined_hardware_design.md`, caps are near IMU VCC. For LRAs, add small series resistor (10 Ω) to limit inrush current and damp ringing.
- Use twisted-pair wiring for LRA signal/ground to reduce EMI pickup.
- Add ferrite bead on power line near ESP32 to suppress high-frequency noise.

**Step 2: Update wiring instructions**
Add note: “For each LRA signal wire, pair with GND wire in a loose twist (1 twist per 20 mm). Install a ferrite bead on the ESP32 3.3 V output rail feeding LRAs.”

---

### Task 5: Refine haptic encoding table with research-based parameters

**Objective:** Replace generic duty settings with evidence-based frequency/amplitude per tremor label, staying within existing PWM hardware.

**Files:**
- Modify: `firmware/stages/haptic.py` (documentation only; no code change yet)
- Create: `docs/references/haptic-encoding.md`

**Step 1: Map tremor types to haptic encoding**
From `refined_hardware_design.md` section on Haptic Pattern Generation:
- Rest tremor: 20 Hz, 30% intensity
- Postural: 5 Hz, 60% intensity
- Kinetic: 10 Hz, 80% intensity

**Step 2: Document mapping**
Create `docs/references/haptic-encoding.md` with table:
| Label | Suggested freq (Hz) | Duty % | Rationale |
|-------|---------------------|--------|-----------|
| rest/baseline | 0 (off) | 0% | No stimulation |
| postural | 5 Hz burst | 60% | Low-frequency cue |
| kinetic | 10 Hz burst | 80% | Higher intensity for movement |
| grasp_guidance | 200 Hz continuous | 50% | Resonance drive for directional cue |

Note firmware currently uses duty-only control at 200 Hz; frequency modulation would require changes beyond scope of research-only refinement. Keep doc as design recommendation.

---

### Task 6: Validate no IMU changes

**Objective:** Ensure no IMU count/placement modifications were introduced.

**Files:**
- Read: `firmware/common/config.py` (NUM_IMUS, GY521_ADDR)
- Read: `docs/imu_lra_placement.txt`

**Step 1: Run diff check**
```
git diff --name-only | grep -i imu
```
Expected: no changes to IMU placement files.

**Step 2: Document compliance**
Add note in plan: “IMU positions unchanged per user constraint.”

---

### Task 7: Update assembly guide with refined LRA sections

**Objective:** Integrate research findings into the existing assembly guide without altering IMU content.

**Files:**
- Modify: `docs/LRA-Assembly-Guide.md`

**Step 1: Add LRA mounting refinement subsection**
Under “Mounting Procedure”, add:
- Silicone coupling pad for dorsal LRA
- Silicone grip dots for palmar LRAs

**Step 2: Add wiring refinement subsection**
Under “Wiring Procedure”, add:
- Twisted-pair signal/ground
- Ferrite bead on power rail
- Optional series resistor 10 Ω

**Step 3: Update Bill of Materials**
Add:
- Medical-grade silicone dots (4 mm) — 12 qty
- Ferrite bead — 1 qty
- Silicone pads (2 mm, 10 mm square) — 3 qty

---

### Task 8: Produce research citation summary

**Objective:** Provide source list for the decisions made.

**Files:**
- Create: `docs/references/lra-research-summary.md`

**Step 1: Compile citations**
From `docs/hardware_design_research.md`:
- DOGlove research (optimal haptic placement)
- High-resolution LRA arrays for spatial patterning
- Dual-spring LRA improvement (40% displacement)
- Haptic feedback effectiveness relative to motor control centers

**Step 2: Write summary**
Include 1–2 sentence description per source, plus how it informed the refinement (e.g., “supports spatial patterning for dorsal array”).

---

## Files likely to change

- `docs/LRA-Assembly-Guide.md` (add LRA refinement sections)
- `docs/strap_and_lra_design.md` (add coupling notes)
- `docs/lra-wiring-instructions.md` (add twisted pair, ferrite bead)
- `docs/references/lra-drive-optimization.md` (new)
- `docs/references/haptic-encoding.md` (new)
- `docs/references/lra-research-summary.md` (new)

Firmware files **not changed** per constraint (IMU components unchanged, LRA code unchanged beyond documentation).

---

## Tests / validation

- **Documentation review**: Ensure `docs/LRA-Assembly-Guide.md` still references IMU positions exactly as in `docs/imu_lra_placement.txt`.
- **Config check**: Verify `firmware/common/config.py` LRA values unchanged (`LRA_FREQ = 200`, `LRA_DUTY_ON = 512`, `LRA_PINS`).
- **Research traceability**: Each recommendation in the guide must reference a doc/source file (e.g., `refined_hardware_design.md` § Sensor Coupling).

---

## Risks, tradeoffs, and open questions

**Risks:**
- Adding silicone coupling pads may slightly increase pocket thickness; verify LRA still fits in 14×14 mm shell.
- Ferrite bead may increase cost/complexity; verify ESP32 3.3 V rail can supply current for 3 LRAs at 50% duty.

**Tradeoffs:**
- Research-based haptic encoding (frequency modulation) would require firmware changes beyond PWM duty control; kept as design recommendation only.

**Open questions:**
- Exact LRA datasheet resonance value for the specific part number in use (affects `LRA_FREQ` tuning).
- Whether series resistor is needed for inrush current suppression (depends on LRA driver spec).
- Availability of medical-grade silicone pads in the lab.

---

*Plan complete and saved. Ready to execute using subagent-driven-development — I'll dispatch a fresh subagent per task with two-stage review (spec compliance then code quality). Shall I proceed?*