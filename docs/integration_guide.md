# Implementation Integration Guide: Research Findings into Forum Project System

This guide maps key research findings from `knowledge.md` and `imu_lra_placement.txt` to concrete changes in the Forum Project system. It prioritizes changes by impact (potential improvement in tremor detection/feedback) and effort (development complexity).

## Table of Changes

| Priority | Impact | Effort | Research Finding | System Component | Required Changes | Files to Modify |
|----------|--------|--------|------------------|------------------|------------------|-----------------|
| High | High | Low | IMU placement: Dorsal wrist (proximal to wrist joint) improves capture of global hand motion with minimal soft tissue artifact. | IMU Mounting System | Update mounting design to place primary IMU at dorsal wrist (just proximal to wrist joint on dorsal side) instead of dorsum hand center (MC2-3). | `docs/strap_and_lra_design.md` (Section 1.1 Pocket‑Style IMU Holder, Section 1.2 Attachment to Strap/Gloves) |
| High | High | Low | IMU placement: Thenar eminence placement captures thumb abduction/adduction tremor. | IMU Mounting System | Ensure thenar eminence pocket is correctly positioned (volar surface at thumb muscle prominence). Verify current design matches. | `docs/strap_and_lra_design.md` (Section 1.1, Section 1.2) – validate dimensions and placement notes. |
| Medium | Medium | Medium | IMU placement: Proximal phalanx of thumb shows highest effect size for tremor across diagnoses. Adding a third IMU here improves classification accuracy via sensor fusion. | Hardware & Firmware | Add a second IMU (total two) on the thumb proximal phalanx. Requires hardware multiplexing (I2C mux or second I2C bus) and firmware updates to handle multiple sensors. | - `docs/imu_lra_placement.txt` (update summary to reflect three IMUs)<br>- `docs/strap_and_lra_design.md` (add Section 1.3: Thumb IMU Pocket)<br>- `firmware/embedded_main.py` (add second sensor instance, modify sampling window to include both sensors, update feature extraction)<br>- `firmware/fft.py` (extend GY521 to support multiple instances or create manager)<br>- `firmware/feature_extract.py` (adjust to process features from both sensors)<br>- `firmware/model.py` (update FEATURE_MEAN/FEATURE_STD length if features change)<br>- `host_scripts/train_classifier.py` (update feature extraction to match)<br>- `host_scripts/analyze_pilot.py` (update to handle multi-IMU CSV format) |
| High | Medium | Low | Haptic feedback: LRAs are preferred for wearable vibrotactile due to low power, fast response, directional tuning. Current system already uses LRAs. | Haptic Actuator System | Justify LRA selection in documentation; consider optimizing drive waveform (sine vs square) for resonant frequency. | - `docs/strap_and_lra_design.md` (Section 2.3 Wiring & Strain Relief – note driving at resonant frequency ~150-250 Hz)<br>- `firmware/embedded_main.py` (verify LRA_FREQ matches actuator resonant frequency; consider adding config per LRA if multiple) |
| Medium | Medium | Low | Haptic feedback: Arrays of LRAs can encode spatial information (e.g., proximal-to-distal pulses for grasp guidance). | Haptic Feedback Pattern | Expand feedback patterns beyond simple ON/OFF to include sequential pulsing across LRA array for cueing movement direction. | - `firmware/embedded_main.py` (modify `apply_feedback` to support array patterns; add LRA pins/config)<br>- `docs/strap_and_lra_design.md` (Section 2.2 Attachment Options – note spatial array configuration) |
| Medium | Low | Low | Feedback intensity/frequency should match individual perceptual thresholds to avoid habituation. | Haptic Feedback Calibration | Add calibration routine to adjust LRA amplitude based on user preference/threshold. | - `firmware/embedded_main.py` (add calibration mode via button press or serial command to sweep LRA duty and store user-preferred value)<br>- `docs/strap_and_lra_design.md` (Section 5 Notes & Tips – add tip about perceptual threshold testing) |
| Medium | Medium | Medium | Multi‑sensor fusion: Combining IMU data improves tremor type classification (rest vs postural vs kinetic). | Firmware & Host Scripts | Implement sensor fusion algorithm (e.g., weighted average, Kalman filter) or simply concatenate features from multiple IMUs. Update feature extraction and model accordingly. | - Same as Medium‑effort multi‑IMU changes above (feature concatenation is simplest)<br>- Additionally, update `firmware/feature_extract.py` to fuse signals (e.g., compute magnitude per axis across sensors before feature extraction) if desired.<br>- Update host scripts to reflect new feature dimensions. |
| Low | Low | Low | Validation: Use both clinical scales (Fahn‑Tolosa‑Marin) and quantifiable metrics (tremor amplitude reduction). | Testing & Evaluation | Add guidelines for validating the system with quantified metrics; suggest using existing host scripts to compute tremor amplitude from IMU data. | - `docs/knowledge.md` (add subsection on validation metrics under “Design Implications”)<br>- `host_scripts/analyze_pilot.py` (add optional metric: RMS tremor amplitude in 3‑12 Hz band)<br>- `README.md` (add section on validation procedure) |

## Detailed Change Descriptions

### 1. IMU Placement Validation
- **Why**: Research consensus places IMU at dorsal wrist (proximal to wrist joint) for optimal tremor detection with minimal artifact. Current strap_and_lra_design.md places IMU at dorsum hand center (over 3rd metacarpal), which is further distal and may capture more motion noise.
- **Change**: Relocate the primary IMU pocket ~10-15mm proximal to wrist joint on dorsal side. Update pocket sewing instructions and strap attachment points accordingly.
- **Files**:
  - `docs/strap_and_lra_design.md`: Sections 1.1 and 1.2 – adjust dimensions and placement description.
  - *(Optional)* `docs/imu_lra_placement.txt`: Already reflects this recommendation; no change needed.

### 2. Thumb IMU Addition (Medium Effort)
- **Why**: Adding a second IMU on thumb proximal phalanx leverages high effect size location, improving classification accuracy via sensor fusion.
- **Hardware**: Use ESP32’s second I2C bus (I2C1: SCL=GPIO23, SDA=GPIO19) or an I2C multiplexer (TCA9548A) on I2C0. Wire second IMU to thumb mount.
- **Firmware**:
  - Instantiate second `GY521` object on appropriate I2C bus.
  - Modify sampling callback to read from both sensors (interleaved or using separate buffers).
  - Combine sensor data: either concatenate raw windows (256 samples total) or extract features per sensor and concatenate feature vectors.
  - Update `feature_extract.compute()` to accept multiple sensor windows.
  - Adjust `model.py` expectations: if feature vector length changes, regenerate `FEATURE_MEAN`, `FEATURE_STD`, `WEIGHTS`, `BIAS` via host retraining.
- **Host Scripts**:
  - Update `train_classifier.py` and `analyze_pilot.py` to expect two sets of accelerometer/gyro data per sample (or separated by sensor).
  - Update CSV format: each row could containLabel, ax1, ay1, az1, ..., ax128, ay128, az128, bx1, by1, bz1, ..., bx128, by128, bz128 (where second sensor is thumb).
- **Files**:
  - `docs/strap_and_lra_design.md`: Add new section for thumb IMU pocket (similar to existing IMU pocket but sized for thumb phalanx).
  - `firmware/embedded_main.py`, `firmware/fft.py`, `firmware/feature_extract.py`, `firmware/model.py`, `host_scripts/train_classifier.py`, `host_scripts/analyze_pilot.py`.

### 3. Haptic Feedback Pattern Refinement
- **Why**: Research shows vibrotactile pulses synchronized to tremor phase can reduce tremor amplitude. Current feedback uses fixed patterns (LED blink, LRA pulse) based on classified tremor type, not phase.
- **Change**: Enhance `apply_feedback` to optionally pulse LRAs at the detected tremor frequency (dominant frequency from FFT) or in a pattern that cues movement inhibition (e.g., pulse during tremor peak).
- **Implementation**:
  - In `embedded_main.py`, after computing FFT, extract peak frequency in 3‑12 Hz band.
  - Use that frequency to schedule LRA pulses (e.g.,激励 at peak or trough).
  - Keep simple patterns as fallback if frequency unreliable.
- **Files**:
  - `firmware/embedded_main.py`: Modify `apply_feedback` or add new function `apply_phase_feedback`.
  - `firmware/fft.py`: Ensure `FFTProcessor` returns magnitude spectrum; add helper to get dominant frequency.

### 4. Material Selection Justification
- **Why**: Breathable, elastic materials prevent sweat buildup and ensure comfort for extended wear, critical for user compliance.
- **Change**: Annotate `strap_and_lra_design.md` with justification for each material choice (elastic nylon/spandex for conformity, breathable mesh for ventilation, hypoallergenic Velcro for skin safety).
- **Files**:
  - `docs/strap_and_lra_design.md`: Add brief justification table or notes in Sections 1.3 and 2.4.

### 5. Testing Correlations
- **Why**: To validate that changes improve outcomes, need to correlate sensor placement/signal features with tremor severity and feedback efficacy.
- **Change**: Extend analysis scripts to compute:
  - Tremor amplitude (RMS in 3‑12 Hz band) per IMU location.
  - Classification accuracy before/after multi‑IMU fusion.
  - Feedback effect: compare tremor amplitude with LRA on vs off (requires experimental protocol).
- **Files**:
  - `host_scripts/analyze_pilot.py`: Add functions for tremor amplitude calculation, sensor‑wise feature importance.
  - `docs/knowledge.md`: Add subsection under “Design Implications” for validation metrics.
  - `README.md`: Add instructions for running validation tests.

## Prioritization Summary

1. **Quick Wins (Low Effort, High Impact)**:
   - Adjust primary IMU placement to dorsal wrist.
   - Justify material choices and LRA drive frequency.
   - Add perceptual threshold calibration notes.

2. **Medium Term (Medium Effort, Medium Impact)**:
   - Refine haptic feedback to use tremor‑phase information.
   - Update documentation for spatial LRA arrays.

3. **Long Term (Higher Effort, Higher Impact)**:
   - Add second IMU (thumb) and update firmware/host scripts for multi‑IMU processing.
   - Implement sensor fusion and validate with quantified metrics.

## Related Files Overview

- **Mounting Design**: `docs/strap_and_lra_design.md`
- **Placement Recommendations**: `docs/imu_lra_placement.txt`
- **Knowledge Base**: `knowledge.md`
- **Firmware Core**: `firmware/embedded_main.py`, `firmware/fft.py`, `firmware/feature_extract.py`, `firmware/model.py`, `firmware/scaler.py`, `firmware/logreg.py`
- **Host Scripts**: `host_scripts/train_classifier.py`, `host_scripts/analyze_pilot.py`, `host_scripts/colab.py`
- **Hardware Contract**: `CLAUDE.md`

---  
*Guide generated: 2026-08-22*  
*Based on research in `knowledge.md` and mounting design in `strap_and_lra_design.md`.*