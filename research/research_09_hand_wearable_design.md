---
date: 2025-09-02
type: research
status: success
topic: Hand Wearable Design for Mounting IMUs — Attachment Methods, Enclosures & Ergonomics
sources: [web_search, web_extract]
---

# Research Handoff: Hand Wearable Design for Mounting IMUs

## Research Question
What are the current best practices for designing hand-worn wearable devices that mount IMU sensors for tremor monitoring, including attachment methods, enclosure design, ergonomics, and sensor placement stability?

## Key Findings

### 1. Mounting Location Options

| Location | Signal Quality | Wearability | Stability | Best For |
|----------|---------------|-------------|-----------|----------|
| **Wrist (dorsal)** | Moderate | Excellent | Good | Long-term monitoring, compliance |
| **Hand dorsum** | High | Good | Moderate | Task-based assessment |
| **Finger (ring)** | Highest | Moderate | Good | Clinical assessment, PD vs ET |
| **Forearm** | Moderate-Low | Good | Excellent | Reference sensor, motion rejection |

**Key trade-off**: Distal = higher tremor amplitude but more motion artifacts. Proximal = cleaner signal but attenuated tremor.

### 2. Attachment Methods

**A. Velcro Strap (Most Common)**
- Used in: SlimeVR trackers, most research prototypes
- Pros: Adjustable, easy don/doff, lightweight, low cost
- Cons: Can loosen over time, may compress soft tissue
- **Best for**: Wrist and forearm mounting
- **Design tip**: Use elastic Velcro with 25-50mm width. Add silicone grip strips to prevent sliding.

**B. Glove-Mounted**
- Used in: PowerGlove, data gloves, ELENA project
- Pros: Secure, distributes force, multiple sensor positions
- Cons: Sizing issues, heat buildup, restricts finger movement
- **Best for**: Multi-sensor hand tracking
- **Design tip**: Open-palm design improves comfort and reduces sizing issues. Use breathable fabrics.

**C. Ring-Mounted**
- Used in: RT-Ring, smart rings (Oura), Wrist2Finger
- Pros: Minimal, socially acceptable, captures finger tremor
- Cons: Limited battery space, finger size variation
- **Best for**: Finger tremor assessment, PD vs ET differentiation
- **Design tip**: Offer multiple sizes (US 6-12). Use flexible PCB for comfort.

**D. 3D-Printed Enclosure**
- Used in: ELENA project, PHTM, custom research devices
- Pros: Custom fit, lightweight, rapid prototyping
- Cons: Rigid, may cause pressure points
- **Design tip**: Use PLA or TPU (flexible). Add sponge lining for comfort. Keep mass <50g.

**E. Adhesive/Tape**
- Used in: Short-term clinical assessments
- Pros: Direct skin contact, no strap movement
- Cons: Skin irritation, not reusable, sweat issues
- **Best for**: Lab sessions <1 hour
- **Design tip**: Use hypo-allergenic double-sided tape. Avoid for long-term wear.

### 3. Enclosure Design Guidelines

**Materials**
| Material | Weight | Comfort | Durability | Printability |
|----------|--------|---------|------------|--------------|
| **PLA** | Light | Moderate | Good | Excellent |
| **TPU (flexible)** | Light | Excellent | Good | Moderate |
| **PETG** | Light | Moderate | Excellent | Good |
| **Resin (SLA)** | Light | Good | Moderate | Excellent |
| **Nylon** | Light | Good | Excellent | Moderate |

**Design Principles**
1. **Minimize mass**: Keep total device <50g (hand), <100g (wrist)
2. **Rounding**: All corners R≥3mm to prevent pressure points
3. **Ventilation**: Add ventilation slots for breathability
4. **Cable management**: Internal channels for wires, strain relief at exits
5. **Battery access**: Easy swap or USB-C charging
6. **Sensor window**: Expose IMU to skin (or use thin plastic) for best coupling

**ELENA Project Design (MDPI 2025)**
- ESP32 Feather + MPU6050 in 3D-printed PLA case
- Glove-mounted with custom holder
- Lightweight, non-restrictive
- No observable worsening/improvement of tremor from glove presence

### 4. Ergonomic Requirements

**Comfort Types (from tremor orthosis literature)**
1. **Thermophysiological**: Breathable materials, RET < 21 m²Pa/W
2. **Sensory**: No shear loads, minimal friction
3. **Ergonomic**: Full range of motion, lightweight
4. **Psychological**: Socially acceptable appearance

**Key Design Constraints**
- **Mass**: <100g for wrist, <50g for hand, <10g for finger
- **Range of motion**: Must not restrict wrist flexion/extension (±90°)
- **Pressure**: Distribute force over large surface area
- **Don/doff**: <30 seconds, one-handed possible
- **Sizing**: Accommodate 5th-95th percentile adult hand dimensions

**Anthropometric Data (for sizing)**
| Measurement | 5th %ile Female | 50th %ile Male | 95th %ile Male |
|-------------|-----------------|----------------|----------------|
| Wrist circumference | 140 mm | 170 mm | 200 mm |
| Hand length | 165 mm | 190 mm | 215 mm |
| Hand breadth | 75 mm | 89 mm | 100 mm |
| Finger diameter (index) | 16 mm | 19 mm | 22 mm |

### 5. Sensor Stability & Signal Quality

**Critical Design Rules**
1. **Mount on bony prominences**: Dorsal hand (3rd metacarpal), wrist (ulna/radius), finger phalanges
2. **Avoid soft tissue**: Causes low-pass filtering and oscillation artifacts
3. **Secure coupling**: Sensor must not move relative to skin
4. **Minimize mass loading**: Device mass alters tremor spectrum

**Mass Loading Effects**
- **<10g**: Negligible effect on tremor spectrum
- **10-50g**: Slight peak frequency reduction
- **50-100g**: Moderate spectral changes, possible double-peaked spectrum
- **>100g**: Significant tremor suppression, altered mechanics

**Dual-Sensor Motion Rejection**
- Place reference IMU on forearm (low tremor)
- Subtract forearm signal from hand signal
- Isolates tremor from voluntary motion

### 6. Reference Designs

**A. QSense Wristband-Style Holder**
- Watch-style strap
- Easy don/doff
- Good for wrist IMU
- ~30g total

**B. RT-Ring (Bioengineering 2024)**
- LSM6DSL IMU on middle finger
- BLE to smartphone
- 92% accuracy PD vs ET classification
- Custom 3D-printed ring enclosure

**C. ELENA Glove (MDPI 2025)**
- ESP32 + MPU6050
- 3D-printed PLA enclosure
- Custom glove with sensor pocket
- Lightweight, non-restrictive

**D. SlimeVR Tracker**
- Multi-IMU (BMI270, ICM-42688)
- Velcro strap mounting
- 6-side calibration
- Open-source firmware

### 7. Complete Design Checklist

**Mechanical**
- [ ] Total mass <50g (hand) or <100g (wrist)
- [ ] All edges rounded (R≥3mm)
- [ ] Ventilation slots for breathability
- [ ] Secure strap attachment (Velcro or elastic)
- [ ] Easy don/doff (<30 seconds)
- [ ] Accommodates 5th-95th percentile hand sizes
- [ ] Does not restrict wrist ROM (±90°)

**Electrical**
- [ ] IMU mounted on bony prominence
- [ ] Battery accessible or USB-C charging
- [ ] Cable strain relief
- [ ] Water/sweat resistance (IPX4 minimum)

**Signal Quality**
- [ ] Sensor coupled to skin (no air gap)
- [ ] No soft tissue compression
- [ ] Mass <10g for hand-mounted
- [ ] Reference sensor on forearm (optional)

**User Experience**
- [ ] Comfortable for >8 hours
- [ ] Socially acceptable appearance
- [ ] One-handed operation
- [ ] Easy cleaning/wipe down

## Recommendations

1. **Start with Velcro strap on wrist**: Easiest to prototype, good balance of signal and wearability. Use elastic Velcro with silicone grip.

2. **Use 3D-printed PLA enclosure**: Lightweight, customizable, rapid prototyping. Add sponge lining for comfort.

3. **Mount on dorsal hand (3rd metacarpal)**: Best signal-to-wearability ratio for tremor. Avoid soft tissue.

4. **Keep mass <50g for hand-mounted**: Prevents mass loading artifacts. Use small LiPo battery (100-200mAh).

5. **Design for 6-side calibration**: Include flat surfaces on enclosure for accelerometer calibration.

6. **Consider dual-sensor**: Wrist (reference) + hand (tremor) for motion artifact rejection.

7. **Open-palm glove design**: If using glove, leave palm free for natural grip and comfort.

## Potential Pitfalls

- **Soft tissue mounting**: Causes signal attenuation and oscillation noise. Always mount on bone.
- **Excessive mass**: >100g on hand suppresses tremor and alters spectrum.
- **Rigid enclosures**: Cause pressure points during long wear. Use flexible materials or padding.
- **Poor strap design**: Sliding or loosening causes motion artifacts. Use silicone grip strips.
- **Ignoring hand sizes**: One-size-fits-all doesn't work. Offer S/M/L or adjustable.
- **Blocking wrist ROM**: Device must not restrict natural wrist movement.

## Sources

1. [Flexible and Self-Powered Wearable Sensors for Tremor Monitoring (Wiley)](https://advanced.onlinelibrary.wiley.com/doi/10.1002/adhm.71380)
2. [Wearable device for tremor-like motion acquisition (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S2468067226000830)
3. [Wearable Devices for Assessment of Tremor (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8226078/)
4. [QSense IMU Placement Straps](https://qsense-motion.com/imu-placement-straps/)
5. [Ring-a-Pose: A Ring for Continuous Hand Pose Tracking (arXiv)](https://doi.org/10.48550/arxiv.2404.12980)
6. [Wrist2Finger: Ring-Watch Wearable (arXiv)](https://arxiv.org/html/2510.04122)
7. [Modular architecture for IMU-based data gloves (arXiv)](https://arxiv.org/html/2401.13254)
8. [Systematic Evaluation of IMU Sensors for Smart Glove (MDPI)](https://mdpi.com/1424-8208/25/1/2/xml)
9. [4D printing of soft orthoses for tremor suppression (Springer)](https://link.springer.com/article/10.1007/s42242-022-00199-y)
10. [Design of lightweight passive orthosis for tremor suppression (JNER)](https://jneuroengrehab.biomedcentral.com/counter/pdf/10.1186/s12984-020-00673-7.pdf)
11. [ELENA Project: Wearable for Hand Tremor Assessment (MDPI)](https://www.mdpi.com/1424-8208/25/9/2763)
12. [PHTM: Low-Cost 3D-Printed Tremor Monitor (arXiv)](https://doi.org/10.17632/859c935kb8)
13. [Lightweight wrist exoskeleton for tremor suppression (IEEE)](https://ieeexplore.ieee.org/document/11459141)
14. [Viscous damping tremor suppression wearable (KU Leuven)](https://lirias.kuleuven.be/retrieve/0bf5609a-74e5-4861-92f0-7139febb7303)

## For Next Agent

This research supports the mechanical/firmware design of the wearable tremor monitor. Key takeaways:

- **Mounting**: Velcro strap on wrist or dorsal hand. Keep <50g for hand, <100g for wrist.
- **Enclosure**: 3D-printed PLA, rounded edges, ventilation, sponge lining.
- **Sensor placement**: Dorsal hand (3rd metacarpal) or wrist (ulna/radius). Mount on bone, not soft tissue.
- **Dual-sensor**: Consider wrist + hand for motion artifact rejection.
- **Sizing**: Offer S/M/L or adjustable. Accommodate 5th-95th percentile.
- **Calibration**: Design flat surfaces for 6-side accelerometer calibration.
- **Comfort**: Open-palm design, breathable materials, <30s don/doff.
