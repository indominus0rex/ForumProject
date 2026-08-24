# Knowledge Base: Wearable Hand Tremor Suppressing Gloves

## Overview
Wearable glove-based systems for tremor suppression combine inertial measurement units (IMUs) for detection and actuators (e.g., LRAs, motors) for haptic feedback or mechanical counter-tremor. The Forum Project focuses on a sensing-and-feedback glove that detects tremor and provides haptic cues to aid motor control, rather than active mechanical suppression. However, research on suppression gloves informs design choices for feedback placement, actuation types, and wearable form factors.

## Key Research Findings

### 1. DOGlove (Dexterous Manipulation with Low-Cost Open-Source Open-Source Haptic Force Feedback Glove)
- **Source**: https://do-glove.github.io/
- **Key Points**:
  - Open-source glove design for dexterous manipulation and haptic feedback.
  - Uses LRAs (Linear Resonant Actuators) for vibrotactile feedback on the dorsum of hand, thenar, and hypothenar regions.
  - Demonstrates effective haptic cueing for motor guidance in teleoperation and virtual environments.
  - Provides hardware files, firmware, and assembly guides that can be adapted for tremor feedback.
  - Highlights importance of actuator placement matching sensory cortical maps for effective perception.

### 2. IMU Placement for Tremor Detection
- **Sources**:
  - Systematic Evaluation of IMU Sensors for Application in Smart Glove (MDPI Sensors 2025)
  - WTM-PD: Wearable IMU-Based Model for Real-Time Parkinson's Tremor (Springer)
  - Toward Stroke Rehabilitation: Single Hand-Mounted IMU and TinyML (Oulu University)
- **Consensus**:
  - Optimal sensor locations: dorsum of hand (between metacarpals 2-3), thenar eminence, hypothenar eminence.
  - Multiple IMUs improve classification accuracy via sensor fusion.
  - Sampling rates of 100 Hz are sufficient for capturing tremor frequencies (4-12 Hz).

### 3. Haptic Feedback and LRA Effectiveness
- **Sources**: 
  - DOGlove research on haptic placement.
  - High-Resolution Wearable Tactile Display Using LRA Arrays (conference paper).
  - Development of Dual-Spring LRA for improved displacement/force.
- **Insights**:
  - LRAs are preferred for wearable vibrotactile due to low power, fast response, and directional tuning.
  - Arrays of LRAs can encode spatial information (e.g., proximal-to-distal pulses for grasp guidance).
  - Optimal placement aligns with dense mechanoreceptor regions: thenar (high sensitivity), hypothenar, dorsum.
  - Feedback intensity and frequency should match individual perceptual thresholds to avoid habituation.

### 4. Multi-Sensor Fusion and Validation
- **Sources**:
  - Hand Tremor Detection and Feedback System Based on IMU Fusion (World Scientific).
  - Vision-based algorithms for tremor classification (MDPI, PMC).
- **Takeaways**:
  - Combining IMU data with optional vision or EMG improves tremor type classification (rest vs. postural vs. kinetic).
  - Validation requires both clinical scales (e.g., Fahn-Tolosa-Marin) and quantifiable metrics (tremor amplitude reduction, activity counts).

## Design Implications for Forum Project
- **IMU Co-location**: Place IMUs at dorsum (MC2-3), thenar, hypothenar to match successful research mounts.
- **Actuator Selection**: Use LRAs (e.g., coin-type ~10mm diameter) for haptic feedback; consider arrays for spatial cues.
- **Feedback Strategy**: Vibrotactile pulses synchronized to tremor phase or as cue for voluntary suppression (e.g., during goal-directed movement).
- **Wearable Form**: Elastic fabric base with breathable mesh (per breathable_imu_mount_design.md) ensures comfort for extended wear.
- **Closed-Loop Potential**: Though current system is open-loop (feedback not directly suppressing), research shows vibrotactile can reduce tremor amplitude when timed to movement phases—a path for future enhancement.

## References
1. DOGlove: https://do-glove.github.io/
2. Systematic IMU Evaluation for Smart Glove: https://www.mdpi.com/1424-8220/25/1/2
3. WTM-PD Model: https://link.springer.com/chapter/10.1007/978-3-032-14044-9_13
4. Single IMU Tremor Detection: https://oulurepo.oulu.fi/bitstream/handle/10024/64186/bbnfioulu-202606305032.pdf
5. Multisensor Fusion for Tremor: https://www.worldscientific.com/doi/epdf/10.1142/S0219519424400724
6. Vision-Based Tremor Assessment: https://www.mdpi.com/1424-8220/26/3/928
7. High-Resolution LRA Arrays: https://di0zxmb8pwajl.cloudfront.net/khc/conference/whc/abs2/WP2-34.pdf
8. Dual-Spring LRA Development: https://ieeexplore.ieee.org/document/10942460

*Last updated: 2026-08-22*