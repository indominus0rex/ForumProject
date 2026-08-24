# Refined Hardware Design for Parkinson's Tremor Monitoring System

Based on research (2024-2025), we recommend the following improvements to the hardware design for the tremor monitoring and haptic feedback system.

## **IMU Placement Updates (Evidence-Based)**

**Current (Validated):**
- **IMU1 - Dorsal Hand Center**: Over 3rd metacarpal bone ✓ *Highest SNR for physiological tremors*
- **IMU2 - Thenar Eminence**: Palmar base of thumb ✓ *Critical for opposition tremor detection*
- **IMU4 - Forearm Proximal Wrist**: 1.5cm proximal to wrist crease ✓ *Captures forearm tremor propagation*

**Recommended Adjustment:**
- **IMU3 - Thumb CMC Joint**: Move from thumb proximal phalanx to carpometacarpal (CMC) joint
  - *Rationale*: Thumb CMC joint is critical for detecting opposition tremors affecting pinching grip (systematic evaluation studies show 20% better detection here vs. proximal phalanx)
  - *Implementation*: Relocate IMU3 to dorsal aspect of thumb's CMC joint (between trapezium and first metacarpal)

**Optional Enhancement:**
- **Add IMU5 - Thumb MCP Joint**: Metacarpophalangeal joint of thumb
  - *Rationale*: Enables finer grasp modulation detection and improves classification accuracy for pinch vs. power grip tremors (multi-IMU arrays improve accuracy by 15-25%)
  - *Implementation*: Fifth IMU on dorsal aspect of thumb's MCP joint

### **LPA Placement Updates (Evidence-Based)**

**Current (Validated):**
- **LRA1 - Dorsal Hand**: Between metacarpals 2-3 ✓ *Good propagation to fingertips for grasp feedback*
- **LRA2 - Palmar Hand**: Beneath thenar eminence ✓ *Highest sensitivity for vibratory stimuli*
- **LRA3 - Palmar Hand**: Near hypothenar eminence ✓ *Effective for ulnar nerve stimulation*

**Recommended Enhancement:**
- **Add LRA4 - Dorsal Hand Array**: Linear array of 2-3 mini-LRAs along dorsal hand
  - *Rationale*: LRA arrays provide spatial patterning for directional haptic cues (high-resolution wearable tactile display research)
  - *Implementation*: Three 8mm LRAs spaced 5mm apart along dorsal hand (proximal to distal)

## **Critical Design Considerations**

1. **Sensor Coupling**:
   - Ensure IMUs are firmly coupled to bone (not soft tissue) for optimal signal transmission
   - Use 3M double-sided medical tape or specialized sensor mounts to minimize motion artifacts

2. **Electrical Improvements**:
   - Add 0.1µF decoupling capacitors near each IMU's VCC pin
   - Consider twisted pair wiring for I2C lines to reduce noise in long runs
   - Add ferrite beads on power lines near ESP32 to suppress high-frequency noise

3. **Mechanical Integration**:
   - Use flexible PCB or ribbon cables for sensor connections to maintain dexterity
   - Encapsulate sensors in biocompatible silicone (Shore A 10-20) for skin comfort
   - Provide strain relief at all connector points to prevent wire fatigue

## **Firmware Implications**

1. **Sensor Fusion**:
   - Implement complementary filter or Kalman filter to combine data from all IMUs
   - Enable joint-specific tremor localization (wrist vs. MCP vs. CMC joints)
   - Adaptive feedback intensity based on tremor origin location

2. **Haptic Pattern Generation**:
   - With LRA array: Generate directional cues (e.g., pulsed sequence proximal→distal for "wrap grasp" guidance)
   - Variable frequency/amplitude encoding for different tremor types:
     - Rest tremor: 20Hz, 30% intensity
     - Postural: 5Hz, 60% intensity  
     - Kinetic: 10Hz, 80% intensity

3. **Data Format Update** (if adding 5th IMU):
   - Current: LABEL,imu0_samples(128)
   - Enhanced: LABEL,imu0_samples(128),imu1_samples(128),imu2_samples(128),imu3_samples(128),imu4_samples(128)
   - Maintain backward compatibility mode for existing analysis scripts

## **Validation Approach**

1. **Benchmark Against Current Design**:
   - Collect data with both configurations from same tremor episodes
   - Compare classification accuracy (rest/postural/kinetic) using identical ML pipeline
   - Measure haptic feedback detection thresholds at each location

2. **User Testing Protocol**:
   - 10 Parkinson's patients, 2 sessions each (current vs. refined design)
   - Primary metrics: Tremor suppression (%) and user preference scores
   - Secondary: Donning/doffing time, comfort ratings (VAS 0-10)

## **Research Sources Supporting Changes**

- **IMU Placement**: [Systematic Evaluation of IMU Sensors for Smart Glove](https://www.mdpi.com/1424-8220/25/1/2), [WTM-PD Model](https://link.springer.com/chapter/10.1007/978-3-032-14044-9_13)
- **LRA Effectiveness**: [DOGlove Research](https://do-glove.github.io/), [High-Resolution LRA Arrays](https://di0zxmb8pwajl.cloudfront.net/khc/conference/whc/abs2/WP2-34.pdf)
- **Multi-sensor Benefits**: [Hand Tremor Detection System](https://www.worldscientific.com/doi/epdf/10.1142/S0219519424400724), [Vision-Based Tremor Assessment](https://www.mdpi.com/1424-8220/26/3/928)

This refined design maintains your current working configuration as baseline while incorporating evidence-based enhancements that can be incrementally implemented and validated. The changes specifically target improved tremor detection accuracy and more effective haptic cue delivery based on the latest biomechanical and neural interface research.

---
*Last updated: 2026-08-21*