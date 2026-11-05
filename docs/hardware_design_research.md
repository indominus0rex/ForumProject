# Hardware Design Research Sources for Parkinson's Tremor Monitoring System

This document compiles key research sources (2024-2025) that informed the refined hardware design recommendations for the tremor monitoring and haptic feedback system.

## IMU Placement Research

### Optimal Sensor Locations for Tremor Detection
- **Systematic Evaluation of IMU Sensors for Application in Smart Glove**  
  Comprehensive analysis of IMU placement effectiveness for hand motion monitoring.  
  https://www.mdpi.com/1424-8220/25/1/2

- **WTM-PD: Wearable IMU-Based Model for Real-Time Parkinson's Tremor**  
  Describes optimal IMU placement for Parkinson's tremor detection and modeling.  
  https://link.springer.com/chapter/10.1007/978-3-032-14044-9_13

- **Toward Stroke Rehabilitation: A Single Hand-Mounted IMU and TinyML for ...**  
  Demonstrates effective tremor detection with optimally placed single IMU.  
  https://oulurepo.oulu.fi/bitstream/handle/10024/64186/nbnfioulu-202606305032.pdf?sequence=1

- **Systematic Evaluation of IMU Sensors for Application in Smart Glove (Alternative Source)**  
  https://research.aston.ac.uk/files/199529167/Systematic_Evaluation_of_IMU_Sensors_for_Application_in_Smart_Glove_System_for_Remote_Monitoring_of_Hand_Differences.pdf

### Additional IMU Research
- **Toward Stroke Rehabilitation: A Single Hand-Mounted IMU and ... - Springer**  
  https://link.springer.com/chapter/10.1007/978-3-032-28829-5_11

- **IMU-Based quantitative assessment of stroke from gait**  
  https://www.nature.com/articles/s41598-025-94167-y

## Haptic Feedback and LRA Research

### LRA Effectiveness and Placement
- **DOGlove: Dexterous Manipulation with a Low-Cost Open-Source Haptic ...**  
  Research on optimal haptic feedback placement for hand motor guidance.  
  https://do-glove.github.io/

- **A High-Resolution Wearable Tactile Display Using LRA Arrays***  
  Demonstrates spatial patterning capabilities of LRA arrays for directional cues.  
  https://di0zxmb8pwajl.cloudfront.net/khc/conference/whc/abs2/WP2-34.pdf

- **Development of a Dual-Spring Linear Resonant Actuator for Improved ...**  
  Shows 40% improvement in displacement/force output with dual-spring LRA design.  
  https://ieeexplore.ieee.org/document/10942460

- **Effectiveness of haptic feedback during local and remote robotic ...**  
  Analyzes haptic feedback effectiveness relative to motor control centers.  
  https://link.springer.com/content/pdf/10.1007/s11701-025-02826-z.pdf

- **PDF Haptics LRA Expansion**  
  Overview of LRA technologies and expansion techniques for wearable systems.  
  https://puiaudio.com/wp-content/uploads/2024/01/SurfaceMountHaptics.pdf

### Additional Haptics Resources
- **LRA Motor Deep Dive: Principle, Selection, and HD Haptics**  
  Technical overview of LRA operating principles and selection criteria.  
  https://micromotorpro.com/lra-motor-deep-dive-principles-haptics/

- **An Overview of Linear Haptic Lra: Standards, Grades, and Mechanical ...**  
  Comprehensive guide to LRA specifications and performance characteristics.  
  https://www.alibaba.com/product-insights/linear-haptic-lra.html

## Multi-Sensor Fusion and Tremor Detection

- **Hand Tremor Detection and Feedback System Based on Inertial Measurement ...**  
  Demonstrates improved classification accuracy through multi-IMU sensor fusion.  
  https://www.worldscientific.com/doi/epdf/10.1142/S0219519424400724

- **A Vision-Based Algorithm for Assessing Head and Hand Tremor ... - MDPI**  
  Shows benefits of multi-sensor approaches for tremor type classification.  
  https://www.mdpi.com/1424-8220/26/3/928

- **A Vision-Based Algorithm for Assessing Head and Hand Tremor ...**  
  https://pmc.ncbi.nlm.nih.gov/articles/PMC12899472/

## Validation Methodologies

- **Systematic Evaluation of IMU Sensors for Application in Smart Glove ...**  
  https://www.semanticscholar.org/paper/Systematic-Evaluation-of-IMU-Sensors-for-in-Smart-Harrison-Jester/d3da08bdaad24ccea98ad39369e025245390b01a

## 2026 Web Expansion — Wrist Placement, Multiplexer & Multi-IMU Fusion

### Wrist Placement Validated at 100 Hz
- **Assessing Parkinson's Rest Tremor from the Wrist with Accelerometry and Gyroscope Signals in Patients with Deep Brain Stimulation: An Observational Study — Keba et al. 2025, J. Clin. Med. 14:2073**  
  https://www.mdpi.com/2077-0383/14/6/2073 + PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC11942689/ : Axivity 6-DoF IMU in rubber wristband **proximal to wrist joint**, 100 Hz, MDS-UPDRS + DBS on/off. Mirrors `firmware/common/config.py:5`.

- **Body placement of IMUs differentially affects physical activity assessment accuracy in drug-naïve PD — Scientific Reports 2026**  
  https://www.nature.com/articles/s41598-026-55099-3 : n=25, 8494 epochs, wrist vs lower back vs ankle. **Wrist+back comparable, ankle 20-25% worse**; in tremor-positive subgroup wrist slightly worse, lower back slightly better — justifies IMU0 wrist + IMU3 forearm redundancy.

### Multiplexer for 4× MPU6050 on ESP32
- **TCA9548A I2C Multiplexer: ESP32, ESP8266, Arduino — RandomNerd Tutorials**  
  https://randomnerdtutorials.com/tca9548a-i2c-multiplexer-esp32-esp8266-arduino/ : Single byte to `0x70` bit `1<<ch` selects 1 of 8 buses.

- **TCA9548A I2C Multiplexer with ESP32 — MicrocontrollersLab**  
  https://microcontrollerslab.com/tca9548a-i2c-multiplexer-esp32-multiple-devices/ : 3-device example on default `SDA21/SCL22` `@400kHz`.

- **TCA9548A Guide — componentindex.net**  
  https://componentindex.net/components/tca9548a/ : TI 8-channel mux explanation.

- **TCA9548A Library — tuxmountain/TCA9548A**  
  https://github.com/tuxmountain/TCA9548A : `multiplexer.selectChannel(0..7)` → normal Wire; maps to MicroPython `i2c.writeto(0x70, bytes([1<<ch]))` as in `firmware/raw_data_collection.py:48`.

- **MPU6050 Complete Tutorial — Zbotic.in**  
  https://zbotic.in/mpu6050-imu-sensor-complete-tutorial-with-arduino-python : AD0 `GND=0x68 / 3.3V=0x69` gives only 2 addresses → mux required for 4. Pullups on GY-521 onboard.

### Multi-IMU Virtual Sensor
- **Sensor Fusion for Distributed IMUs — schoi355/multi_imu_fusion (AAS 2025)**  
  https://github.com/schoi355/multi_imu_fusion : 5-18 IMUs to virtual IMU via Allan variance, significant drift reduction vs single.

- **Multi-IMU Sensor Fusion for Legged Robots — Cerberus 2.0, arXiv:2507.11447**  
  https://arxiv.org/abs/2507.11447 : Multi-IMU PO CRLB much smaller, <0.5% drift over 500m.

### Soft-Mount Artifact Suppression
- **Developments and challenges of advanced flexible electronic materials — Adv. Compos. Hybrid Mater. 2024**  
  https://link.springer.com/article/10.1007/s42114-024-00949-9 : Flexible materials + rigid coupling reduce motion artifacts.

- **Source-level motion artifact suppression in wearable — SciDirect 2026**  
  https://www.sciencedirect.com/science/article/pii/S2590006426004850 : Dynamically stable skin contact via foam/silicone.

## Integration and System Design

- **Comparison of Haptic Feedback in Upper-Limb Prostheses for Hand-Wrist ...**  
  Provides context for integrating sensing and actuation in wearable hand systems.  
  https://link.springer.com/chapter/10.1007/978-3-032-08271-8_37

---

*Last updated: 2026-08-27*  
*Sources compiled for Forum Project hardware design refinement — added 2026-08-27 web search (wrist 100Hz, multiplexer, virtual IMU)*