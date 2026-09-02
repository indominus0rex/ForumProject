# Web Research Log — 2026-08-27

Consolidated web search performed before 4-IMU build (thumb CMC locked). Raw excerpts preserved for traceability with query, URL, date, and relevance to Forum Project.

## Queries
- `Parkinson tremor IMU placement dorsum wrist thenar thumb optimal 2024 2025`
- `TCA9548A ESP32 MPU6050 multiplexer 4 IMU 100Hz I2C timing`
- `hand tremor multi-IMU sensor fusion accuracy vs single IMU`
- `wearable tremor strap elastic Velcro vs medical tape motion artifact 2024`

## Results

### 1. Wrist-Proximal Placement Validated
**Keba et al. 2025, J. Clin. Med. 14:2073**
- URL: https://www.mdpi.com/2077-0383/14/6/2073 + PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC11942689/
- Excerpt: "Tremor measurements were made using a 6 degrees of freedom IMU ... housed in a rubber wristband and worn proximal to the wrist joint (Figure 1). Acceleration and angular velocity signals were recorded at sampling rate of 100 Hz." Patients seated forearms on chair arms, hand freely moving, relax, no voluntary movement. Clinical MDS-UPDRS + DBS states.
- Relevance: Directly mirrors `firmware/common/config.py:5` 100Hz and supports `imu_lra_placement.txt:7` dorsal wrist proximal. Use as bench protocol for your HSP validation.

**FAIRPARK-II 2026, Scientific Reports s41598-026-55099-3**
- URL: https://www.nature.com/articles/s41598-026-55099-3
- Excerpt: "Wrist and lower back IMU showed comparable RMSE ... ankle 20-25% higher across all MET levels... Tremor affected RMSE negatively, whereby the lower back position may be slightly favorable... wrist ... without tremor, lower back ... with tremor."
- Relevance: n=25 drug-naïve PD, 8494 epochs. Supports keeping both wrist (IMU0) and forearm 1.5cm proximal (IMU3) for coverage per `refined_hardware_design.md:10`.

### 2. TCA9548A Multiplexer for 4× Same-Address MPU6050
**RandomNerd Tutorials**
- URL: https://randomnerdtutorials.com/tca9548a-i2c-multiplexer-esp32-esp8266-arduino/
- Excerpt: Tutorial to add I2C ports via TCA9548A — especially useful for multiple same-address devices.

**MicrocontrollersLab**
- URL: https://microcontrollerslab.com/tca9548a-i2c-multiplexer-esp32-multiple-devices/
- Excerpt: Connect three I2C devices via default SDA21/SCL22.

**componentindex.net**
- URL: https://componentindex.net/components/tca9548a/
- Excerpt: "8-channel I2C multiplexer made by Texas Instruments ... switch between them by writing a single byte to address 0x70."

**tuxmountain/TCA9548A (GPL-3.0)**
- URL: https://github.com/tuxmountain/TCA9548A
- Excerpt: `TCA9548A multiplexer(0x70); multiplexer.selectChannel(channelNumber);` then normal Wire.

**Zbotic MPU6050 Tutorial**
- URL: https://zbotic.in/mpu6050-imu-sensor-complete-tutorial-with-arduino-python
- Excerpt: "Two — one at address 0x68 (AD0=GND) and one at 0x69 (AD0=3.3V). For more than two, use a TCA9548A."
- Relevance to project: Confirms `firmware/RawDataCollection.py:48` `mux.writeto(0x70, 1<<ch)` and pullups on GY-521. Keep wires <15cm to avoid WiFi I2C glitches.

### 3. Multi-IMU Fusion Benefit
**schoi355/multi_imu_fusion (AAS 2025)**
- URL: https://github.com/schoi355/multi_imu_fusion
- Excerpt: "measurements of multiple MEMS IMUs are fused into a virtual IMU ... Allan variance ... compare noise ... up to 18 simulated and 5 real MEMS IMUs ... significant deviation and error accumulation IMU-only ... "
- Relevance: Justifies 4-IMU choice; `stages/quality.py` fallback >0.08 still leaves 3 valid.

**Cerberus 2.0 arXiv:2507.11447**
- URL: https://arxiv.org/abs/2507.11447
- Excerpt: "CRLB of Multi-IMU PO is much smaller ... <0.5% drift even after traveling for long distances ... Complementary 0.019/0.040 vs Multi-IMU 0.015/0.018 deg."
- Relevance: Redundancy and factor-graph fusion relevant to host-side `train_classifier.py` feature concat 15×4.

**Aerospace/sensors reviews**
- URLs: https://github.com/schoi355/multi_imu_fusion, https://ieeexplore.ieee.org/document/9994677
- Note: Multiple low-cost MEMS vs single high-cost — supports student BOM.

### 4. Soft-Mount & Artifact Suppression
**Nature Rev. Flexible Electronics 2024**
- URL: https://link.springer.com/article/10.1007/s42114-024-00949-9

**SciDirect 2026 source-level suppression**
- URL: https://www.sciencedirect.com/science/article/pii/S2590006426004850
- Excerpt: "dynamically stable skin contact and low contact impedance during movements and even heavy sweating"
- Relevance: Supports thin TPU adapter + Hypafix/foam under IMU vs pure elastic — per `strapping_materials.txt:7` vs `strap_and_lra_design.md:6`.

## Decisions Locked for This Build
- Thumb: **CMC dorsal** (per `refined_hardware_design.md:13` over `component_positions.txt:13` phalanx) — approved 2026-08-27.
- 4-IMU set: dorsal wrist proximal (ch0), thenar (ch1), thumb CMC (ch2), forearm 1.5cm proximal (ch3).
- Multiplexer: TCA9548A @0x70, channels 0-3, all MPU6050 at 0x68.
- LRAs deferred: GPIOs 25/18/19/20 unpopulated.

## File Cross-Refs Updated
- `knowledge.md:46` design implications now lists 4-IMU CMC lock.
- `docs/hardware_design_research.md` added Section 2026 Web Expansion.
- This log saved as `docs/research_web_2026-08-27.md`.

*Search session id: ses_fbc77de81ffeibwjOYtlwAxNiE*
