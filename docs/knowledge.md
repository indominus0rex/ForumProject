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
- **IMU Co-location (2026-08-27 locked)**: 4-IMU set via TCA9548A — (0) dorsal wrist *just proximal to joint* (Keba 2025 rubber-band method, 100 Hz), (1) thenar eminence volar, (2) **thumb CMC dorsal (trapezium–1st MC, confirmed over proximal phalanx, +20% detection)** per refined_hardware_design.md:13, (3) forearm 1.5cm proximal to wrist crease dorsal. All Z-up X-radial Y-proximal per component_positions.txt:22. Elastic 3D spacer + thin TPU adapter + Hypafix for rigid coupling and breathability.
- **Actuator Selection**: Use LRAs (e.g., coin-type ~10mm diameter) for haptic feedback; consider arrays for spatial cues. **For current 4-IMU build LRAs deferred** — GPIO25/18/19/20 left unpopulated, haptic stage no-ops with duty 0 until actuators procured.
- **Feedback Strategy**: Vibrotactile pulses synchronized to tremor phase or as cue for voluntary suppression (e.g., during goal-directed movement).
- **Wearable Form**: Elastic fabric base with breathable mesh (per breathable_imu_mount_design.md) ensures comfort for extended wear.
- **Closed-Loop Potential**: Though current system is open-loop (feedback not directly suppressing), research shows vibrotactile can reduce tremor amplitude when timed to movement phases—a path for future enhancement.

## 5. Latest Evidence (Web Search 2026-08-27)

### 5a. Wrist-Proximal Placement Validated at 100 Hz
- **Keba et al. 2025, J. Clin. Med. 14:2073** — https://www.mdpi.com/2077-0383/14/6/2073 + PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC11942689/ : 6-DoF IMU (Axivity, 3-axis accel + gyro) housed in **rubber wristband worn proximal to wrist joint** (Figure 1), **100 Hz**, rest tremor with forearms on chair arms, hand free, MDS-UPDRS + DBS on/off states. Directly mirrors `firmware/common/config.py:5` (100Hz/128/1.28s) and `imu_lra_placement.txt:7` recommendation.
- **FAIRPARK-II 2026, Sci. Rep. s41598-026-55099-3** — https://www.nature.com/articles/s41598-026-55099-3 : Drug-naïve PD (n=25, 8494 15-min epochs) wrist vs lower back vs ankle ENMO. **Wrist and lower back comparable RMSE, ankle 20-25% worse**. In tremor-positive subgroup (n=11 vs 14), **wrist slightly better without tremor, lower back slightly better with tremor** — supports keeping both wrist (IMU0) and forearm (IMU3) for coverage.

### 5b. Multi-IMU Fusion Benefit for 4-IMU Choice
- **schoi355/multi_imu_fusion 2025 — https://github.com/schoi355/multi_imu_fusion (AAS 2025 Choi et al.)**: Up to 18 simulated / 5 real MEMS IMUs fused to a **virtual IMU** via Allan variance (ARW/VRW/RRW). **Significant drift/error reduction vs single IMU** in hallway robot data — same principle for hand tremor: 4 hand sites suppress per-sensor noise and allow fallback if one channel returns `(0,0,1)` (`gy521.py:55`).
- **Cerberus 2.0 / Multi-IMU PO 2025-07 — https://arxiv.org/abs/2507.11447**: Sliding-window factor graph multi-IMU preintegration **CRLB much smaller than single-IMU PO**, drift <0.5% over 500m vs single breaking — justifies redundancy for `stages/quality.py` fallback gate (>0.08 ratio flagged not tremor).

### 5c. TCA9548A Feasibility for 4× MPU6050 on ESP32
- **RandomNerd TCA9548A ESP32 — https://randomnerdtutorials.com/tca9548a-i2c-multiplexer-esp32-esp8266-arduino/** , **MicrocontrollersLab — https://microcontrollerslab.com/tca9548a-i2c-multiplexer-esp32-multiple-devices/** , **componentindex — https://componentindex.net/components/tca9548a/** : TI 8-channel mux, **single byte to 0x70 with bit `1<<ch`** selects channel. Standard for motion-capture suits with same-address sensors. ESP32 `Wire.begin(SDA21,SCL22)` short <15cm to avoid WiFi I2C glitches.
- **tuxmountain/TCA9548A — https://github.com/tuxmountain/TCA9548A** : Library `multiplexer.selectChannel(0..7)` → normal Wire transactions — maps to MicroPython `i2c.writeto(0x70, bytes([1<<ch]))` already used in `raw_data_collection.py:48`.
- **Zbotic MPU6050 complete tutorial — https://zbotic.in/mpu6050-imu-sensor-complete-tutorial-with-arduino-python**: Confirms AD0 `GND=0x68 / 3.3V=0x69` gives only 2 addresses — mux required for 4. GY-521 pullups onboard, no external needed for 1-2 devices.

### 5d. Soft-Mount Artifact Management
- **Review 2024-09 — https://link.springer.com/article/10.1007/s42114-024-00949-9** + **2026 SciDirect — https://www.sciencedirect.com/science/article/pii/S2590006426004850** : Motion artifacts from poor skin coupling suppressed by **polyurethane foam / thin flexible silicone + rigid coupling adapter**, not pure elastic — reconciles `strapping_materials.txt:7` Hypafix/Micropore vs `strap_and_lra_design.md:6` elastic: use **thin TPU adapter + Hypafix under each pocket**.

## References
1. DOGlove: https://do-glove.github.io/
2. Systematic IMU Evaluation for Smart Glove: https://www.mdpi.com/1424-8220/25/1/2
3. WTM-PD Model: https://link.springer.com/chapter/10.1007/978-3-032-14044-9_13
4. Single IMU Tremor Detection: https://oulurepo.oulu.fi/bitstream/handle/10024/64186/bbnfioulu-202606305032.pdf
5. Multisensor Fusion for Tremor: https://www.worldscientific.com/doi/epdf/10.1142/S0219519424400724
6. Vision-Based Tremor Assessment: https://www.mdpi.com/1424-8220/26/3/928
7. High-Resolution LRA Arrays: https://di0zxmb8pwajl.cloudfront.net/khc/conference/whc/abs2/WP2-34.pdf
8. Dual-Spring LRA Development: https://ieeexplore.ieee.org/document/10942460
9. Wrist rest tremor at 100Hz — Keba et al. J. Clin. Med. 2025: https://www.mdpi.com/2077-0383/14/6/2073
10. FAIRPARK-II wrist vs ankle/back 2026: https://www.nature.com/articles/s41598-026-55099-3
11. Multi-IMU virtual IMU 2025: https://github.com/schoi355/multi_imu_fusion
12. Multi-IMU PO / Cerberus 2025: https://arxiv.org/abs/2507.11447
13. TCA9548A ESP32 guide: https://randomnerdtutorials.com/tca9548a-i2c-multiplexer-esp32-esp8266-arduino/
14. MPU6050 AD0/mux need: https://zbotic.in/mpu6050-imu-sensor-complete-tutorial-with-arduino-python

*Last updated: 2026-08-27 — 4-IMU CMC lock + web research added*