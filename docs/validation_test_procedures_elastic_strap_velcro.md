# Quantitative Validation Test Procedures for Elastic Strap and Velcro Closure System

## Overview
This document outlines quantitative validation test procedures for the elastic strap (nylon/spandex 4-way stretch) and Velcro closure system used in the IMU/LRA mounting system described in `strap_and_lra_design.md`. The procedures focus on four key validation areas:
1. Elastic recovery after repeated stretching
2. Velcro adhesion strength over time and after washing
3. Migration resistance during simulated hand movements
4. Comfort metrics via user testing

These tests reference the materials and design specifications from:
- `strap_and_lra_design.md`
- `strapping_materials.txt` 
- `breathable_imu_mount_design.md`

## 1. Elastic Recovery After Repeated Stretching

### Objective
Quantify the elastic fabric's ability to return to original dimensions after repeated stretching cycles under specified forces.

### Test Specimens
- Elastic nylon/spandex (30-35mm wide, 4-way stretch) as specified in strap_and_lra_design.md sections 1.3 and 2.3
- Minimum 5 samples per test condition, each 100mm in original length

### Equipment
- Universal testing machine (Instron or equivalent) with grips
- Force gauge capable of 0-50N range
- Digital calipers (0.01mm precision)
- Environmental chamber (optional, for temperature/humidity conditioning)

### Procedure
#### 1.1 Baseline Measurement
1. Condition specimens at 23±2°C and 50±5% RH for 24 hours
2. Measure original length (L₀) and width (W₀) of each specimen
3. Record cross-sectional area if possible

#### 1.2 Cyclic Stretching Test
1. Mount specimen in testing grips with initial preload of 0.5N
2. Apply cyclic loading:
   - Stretch to 25% elongation (125mm length) at 100mm/min
   - Hold at peak elongation for 5 seconds
   - Return to preload at 100mm/min
   - Hold at preload for 5 seconds
   - Repeat for 1,000 cycles
3. Measure length after 100, 500, and 1,000 cycles

#### 1.3 Recovery Assessment
1. After cyclic testing, allow specimen to rest unloaded for 30 minutes
2. Measure final length (Lf) and width (Wf)
3. Calculate:
   - Elastic recovery ratio: (L₀ - Lf)/L₀ × 100%
   - Permanent set: (Lf - L₀)/L₀ × 100%
   - Width change ratio: (Wf - W₀)/W₀ × 100%

### Acceptance Criteria
- Elastic recovery ratio ≥ 85% after 1,000 cycles
- Permanent set ≤ 15%
- Width change ≤ ±5% (to maintain proper strap tension)

### Reporting
- Tabulate results for each specimen
- Include mean, standard deviation, and range
- Plot recovery ratio vs. cycle number
- Note any visual damage or deformation

## 2. Velcro Adhesion Strength Over Time and After Washing

### Objective
Quantify the peel strength and shear strength of Velcro closures under various environmental conditions and after repeated washing cycles.

### Test Specimens
- Hook-side and loop-side Velcro (15mm width, sew-on) as specified in strap_and_lra_design.md sections 1.3 and 2.3
- Bonded to elastic strap substrate using recommended sewing procedure
- Minimum 5 samples per test condition

### Equipment
- Universal testing machine with peel and shear fixtures
- Washing machine (standard household, gentle cycle)
- Mild soap solution (as per maintenance section in strap_and_lra_design.md)
- Air drying rack
- Environmental conditioning chamber

### Procedure
#### 2.1 Initial Adhesion Strength
1. Prepare specimens with 50mm overlap of hook and loop sides
2. Condition at 23±2°C and 50±5% RH for 24 hours
3. Test peel strength (180° peel) at 100mm/min
4. Test shear strength (overlap shear) at 50mm/min
5. Record peak force and average force over bond area

#### 2.2 Environmental Aging
1. Divide specimens into groups:
   - Control (room conditions)
   - High humidity (40°C, 90% RH)
   - Thermal cycling (-20°C to +60°C, 2 cycles/hour)
   - UV exposure (equivalent to 100 hours sunlight)
2. Age for 168 hours (1 week)
3. Retest peel and shear strength
4. Calculate strength retention: (F_aged/F_initial) × 100%

#### 2.3 Wash Cycle Resistance
1. Subject specimens to washing:
   - Hand wash with mild soap (30°C, 5 minutes)
   - Gentle machine wash (30°C, mild detergent)
   - Rinse thoroughly, air dry
2. Repeat for 5, 10, 20, and 50 wash cycles
3. After each interval, test peel and shear strength
4. Calculate strength retention per wash interval

### Acceptance Criteria
- Peel strength retention ≥ 80% after environmental aging
- Shear strength retention ≥ 75% after environmental aging
- Peel strength ≥ 1.5 N/mm after 50 wash cycles
- No delamination or fabric damage visible after testing

### Reporting
- Tabulate peel and shear strength for each condition
- Include failure mode analysis (adhesive vs cohesive)
- Plot strength retention vs. wash cycles/aging time
- Document any contamination or lint accumulation effects

## 3. Migration Resistance During Simulated Hand Movements

### Objective
Quantify resistance to lateral and longitudinal migration of the strap system during realistic hand and wrist motions.

### Test Setup
- Elastic strap with Velcro closure assembled per strap_and_lra_design.md
- IMU/LRA pocket assemblies installed at designated locations
- Test weights simulating IMU (~8g) and LRA (~3g) masses
- Motion capture system or high-speed camera (≥120 fps)
- Force sensors mounted on test rig

### Procedure
#### 3.1 Static Position Holding
1. Mount assembled strap on standardized hand/wrist phantom
2. Apply known loads simulating tendon resistance:
   - Dorsum IMU: 0.5N radial, 0.3N ventral
   - Thenar IMU: 0.4N palmar, 0.2N radial
3. Measure initial position of pocket centers
4. Apply cyclic loads simulating tremor frequencies (3-8Hz)
5. Track position displacement over 10-minute period
6. Calculate migration velocity (mm/hour)

#### 3.2 Dynamic Movement Simulation
1. Program robotic wrist fixture to simulate:
   - Flexion/extension: 0-90° at 30°/s
   - Radial/ulnar deviation: 0-30° at 20°/s
   - Pronation/supination: 0-80° at 40°/s
   - Combined motions mimicking ADL (activities of daily living)
2. Run for 1 hour continuously
3. Use motion capture to track:
   - Strap slip relative to skin phantom
   - Pocket migration from target location
   - Closure loosening (Velcro engagement change)
4. Record peak forces required to initiate slip

#### 3.3 Sweat and Lubrication Effects
1. Repeat dynamic test with:
   - Artificial sweat solution (pH 4.8, 0.5% NaCl, 0.1% lactic acid)
   - Light mineral oil lubrication
2. Compare migration rates to dry condition

### Acceptance Criteria
- Migration velocity ≤ 2mm/hour under static load
- Total displacement ≤ 5mm after 1 hour dynamic movement
- Peak slip force ≥ 15N (indicates secure fastening)
- No migration observed with sweat/lubrication that exceeds dry condition by >50%

### Reporting
- Tabulate migration distances for each test condition
- Include time-series plots of displacement
- Document correlation between motion type and migration direction
- Note any strap creep or closure degradation observed

## 4. Comfort Metrics via User Testing

### Objective
Collect quantitative comfort and wearability data from human subjects during extended wear.

### Test Subjects
- Minimum 15 healthy adult participants (diverse demographics)
- Informed consent obtained
- Screening for skin sensitivities or contraindications

### Equipment
- Assembled strap systems with IMU/LRA pockets (non-functional dummy weights)
- Comfort questionnaire (validated scales)
- Skin assessment tools (dermatographometer, moisture sensor)
- Activity monitors (to correlate movement with discomfort)
- Data logging system

### Procedure
#### 4.1 Donning and DoFFing Assessment
1. Time required to don and doff the system
2. Number of adjustments needed for proper fit
3. Subjective ease rating (1-10 scale)

#### 4.2 Extended Wear Test
1. Subjects wear system for 4 continuous hours during normal activities
2. Schedule:
   - 0 min: Baseline comfort and skin assessment
   - Every 30 min: Discomfort VAS (Visual Analog Scale)
   - 120 min: Moderate activity period (10 min walking, light tasks)
   - 240 min: Final assessment
3. Monitor:
   - Comfort VAS (0=none, 10=worst imaginable)
   - Pain VAS (if applicable)
   - Itch VAS
   - Thermal sensation (hot/cold scale)
4. Conduct skin inspection at 120 and 240 min:
   - Erythema (redness) scoring (0-4 scale)
   - Edema (swelling) assessment
   - Indentation marks from strap

#### 4.3 Activity-Specific Comfort
1. Repeat wear test during specific activities:
   - Typing (keyboard use)
   - Gripping objects (various sizes)
   - Modalities requiring wrist extension/flexion
2. Collect task-specific comfort ratings

### Acceptance Criteria
- Mean comfort score ≤ 3/10 at 4 hours
- No participant reports score ≥ 7/10 at any time
- Mean donning time < 60 seconds
- Skin irritation score ≤ 1 (mild erythema) for ≥90% of participants
- No reports of numbness, tingling, or circulation issues

### Reporting
- Tabulate comfort scores over time for each participant
- Include mean ± SD and range at each time point
- Document correlation between activity type and discomfort peaks
- Note any adverse skin reactions or compression symptoms
- Perform statistical analysis (ANOVA) for demographic effects

## General Test Conditions and Notes

### Environmental Conditions
Unless otherwise specified:
- Temperature: 23±2°C
- Relative humidity: 50±5%
- Atmospheric pressure: Local ambient

### Sample Preparation
- All specimens cut from same production lot when possible
- Condition all specimens per Section 1.1 before testing
- Use consistent sewing/assembly procedures per strap_and_lra_design.md
- Label all samples with unique identifiers

### Safety Considerations
- Discontinue testing if any specimen shows signs of catastrophic failure
- For human testing, monitor for adverse reactions and provide exit option
- Use appropriate PPE when testing with conditioning chambers

### Equipment Calibration
- Verify testing equipment calibration within last 30 days
- Perform linearity checks on load cells and extensometers
- Validate environmental chamber readings with independent sensors

### Data Analysis
- Use appropriate statistical tests for comparison (t-test, ANOVA)
- Report confidence intervals (95%) where applicable
- Identify outliers using Tukey's method or equivalent
- Consider both statistical and practical significance

## References
- strap_and_lra_design.md: Primary design document
- strapping_materials.txt: Material recommendations
- breathable_imu_mount_design.md: Design inspiration and materials
- ASTM D4964: Standard Test Method for Elastic Recovery of Knitted Fabrics
- ASTM D6828: Standard Test Method for Strength Properties of Adhesive Bonds
- ISO 10993-10: Tests for irritation and skin sensitization
- ISO 20683: Determination of resistance to pilling of textile fabrics

## Revision History
| Version | Date | Changes | Approved By |
|---------|------|---------|-------------|
| 1.0 | 2026-08-22 | Initial creation | [To be filled] |

---
*End of Validation Test Procedures*