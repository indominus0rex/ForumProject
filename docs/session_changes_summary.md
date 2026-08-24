# Session Changes Summary

This file summarizes the practical changes made during the wearable strap / haptic feedback design session.

## Documentation created or updated

- `AGENTS.md`
  - Added repo-specific agent instructions for this ESP32 tremor-detection project.
  - Covers project layout, host commands, MicroPython conventions, and pitfalls.

- `knowledge.md`
  - Added research notes on wearable hand tremor suppression gloves.
  - Covers IMU placement, haptic feedback, LRA/ERM considerations, validation metrics, and implementation ideas.

- `docs/strap_and_lra_design.md`
  - Added removable strap design using elastic nylon/spandex, breathable mesh, and Velcro.
  - Includes IMU/LRA pocket sizes, flap design, strain relief, wire routing, and maintenance notes.

- `docs/assembly_checklist.md`
  - Added a build checklist for the wearable prototype.
  - Revised it to recommend a safe first build: 1 ESP32 + 1 MPU6050 + 1 haptic actuator on GPIO25.
  - Separates optional multi-LRA and multi-IMU upgrades from the first prototype.
  - Adds warnings for MPU6050 I2C address conflicts, GPIO20 availability, LiPo power, MOSFET gate pulldown, and actuator brownout risk.

- `docs/validation_test_procedures_elastic_strap_velcro.md`
  - Added quantitative validation procedures for strap elasticity, Velcro adhesion, migration resistance, and comfort.

- `docs/integration_guide.md`
  - Added guide mapping research findings into concrete firmware, hardware, and validation improvements.

## Firmware changed

- `firmware/embedded_main.py`
  - Added optional multi-LRA configuration:
    - `LRA_PINS = [18, 19, 20]`
    - `USE_LRA_ARRAY = False`
  - Added optional `lra_array` initialization.
  - Updated feedback logic to use `_set_all_lras()` so single-LRA mode and array mode share one control path.
  - Added proximal-to-distal pulse sequencing for optional grasp-guidance / non-standard-label feedback:
    - proximal / hypothenar
    - middle / thenar
    - distal / dorsal MC2-MC3
    - 333 ms per phase, about 1 second per full cycle
  - Left single-actuator GPIO25 behavior as the default mode.

## Host-side scripts added or modified by subagents

- `host_scripts/analyze_suppression.py`
  - Added suppression-effectiveness analysis for pre/post intervention data.

- `host_scripts/generate_test_data.py`
  - Added synthetic data generation for testing suppression metrics.

- `host_scripts/analyze_pilot.py`
  - Subagent reported adding suppression-analysis helper functions.

- `host_scripts/train_classifier.py`
  - Subagent reported adding suppression-analysis integration helpers.

## Hardware guidance changed

- First prototype should not start with 3 IMUs and 3 actuators wired at once.
- Recommended first build:
  - 1 ESP32
  - 1 MPU6050 / GY-521
  - 1 LRA or ERM vibration motor
  - 1 MOSFET driver channel on GPIO25
- Optional upgrades remain documented:
  - 3-actuator haptic array after board pins are verified.
  - 2 IMUs using `0x68` and `0x69`, or 3+ IMUs using an I2C multiplexer such as TCA9548A plus firmware/host-script changes.

## Notes before flashing hardware

- Verify your exact ESP32 board pinout before using `LRA_PINS = [18, 19, 20]`; GPIO20 may not exist on classic ESP32 DevKit boards.
- Do not wire 3 MPU6050 modules all with AD0 tied to GND; they will all use I2C address `0x68` and conflict.
- For baseline data collection, keep the actuator off so motor vibration does not contaminate tremor training data.

## Later refinement

- Cleaned `firmware/embedded_main.py` without changing materials guidance.
- Added missing `classify_logreg()` and `classify_heuristic()` helpers so the main loop has definitions for the functions it calls.
- Removed unused feedback globals from `apply_feedback()`.
- Added a safe fallback for `grasp_guidance` when `USE_LRA_ARRAY = False`: it now uses the default single actuator instead of entering empty array logic.
- Added an explicit note in `docs/assembly_checklist.md` that material choices were intentionally left unchanged.
