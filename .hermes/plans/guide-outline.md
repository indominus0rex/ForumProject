# LRA Assembly Guide Outline

## 1. Introduction
- Purpose of the guide
- Intended audience (makers, researchers, clinicians)
- Prerequisites (basic soldering, sewing skills)

## 2. Parts and Tools Required
### 2.1 Electronic Components
- ESP32 development board
- IMU (MPU6050 or similar)
- Linear Resonant Actuators (LRAs) - quantity and specs
- Wiring: 30AWG silicone-insulated stranded wire
- Connectors (optional): micro-JST PH 2-pin
- Resistors, capacitors if needed

### 2.2 Mounting Materials
- Elastic nylon/spandex strap (15-35mm wide)
- Breathable mesh panels (mesh) fabric panels
- Stabilizer strips (cotton webbing or twill tape)
- Hook-and-loop tape (Velcro): sew-on type, 15-20mm width
- Optional: silicone grip dots, fabric adhesive

### 2.3 Tools
- Soldering iron and solder (lead-free)
- Wire strippers
- Fine needle and polyester/nylon upholstery thread
- Scissors, ruler, fabric chalk or washable marker
- Sewing pins or clips
- Multimeter (for validation)
- Heat gun or lighter (for heat-shrink)
- Tweezers

## 3. Firmware Preparation
### 3.1 Configuration Review
- Check `firmware/common/config.py` for:
  - `LRA_PIN` (single) or `LRA_PINS` (array)
  - `LRA_FREQ` (should be 200)
  - `LRA_DUTY_ON` (512 for 50%)
  - `USE_LRA_ARRAY` flag
### 3.2 Haptic Stage Verification
- Review `firmware/stages/haptic.py` for duty cycle and labeling logic

## 4. Mounting Procedure
### 4.1 Pocket Dimensions
- For typical LRA (~10mm × 10mm × 3-4mm):
  - Shell cut: 14mm × 14mm (10mm internal + 2mm seam allowance)
  - Flap cut: 18mm × 13mm
  - Velcro squares: 12mm × 12mm

### 4.2 Step-by-Step Sewing
1. Cut fabric pieces with seam allowance
2. Prepare Velcro (hook and loop squares)
3. Sew pocket shell: right sides together, sew three sides, leave one open
4. Turn right-side out, press flat
5. Attach Velcro: hook to flap underside, loop to pocket rim
6. Finish edges (optional top-stitch)
7. Mount pocket to strap/base: sew outer edges, avoid blocking opening
8. Create strain-relief loop for wire entry

## 5. Wiring Procedure
### 5.1 Wire Preparation
- Cut two lengths of 30AWG silicone-stranded wire per LRA (~50mm)
- Strip 3mm, tin ends
- Solder to LRA terminals (observe polarity if applicable)
- Slide heat-shrink over joints, apply heat
- Create 3mm diameter strain-relief loop 5mm from joint, secure with stitch

### 5.2 Routing to ESP32
- Route wires along inside of strap, following natural contour
- Secure with stitches or flexible epoxy every 15mm
- Create second strain-relief loop where wire exits toward ESP32
- Connect to ESP32:
  - Single LRA: LRA_PIN (GPIO 25) and GND
  - Array mode: LRA_PINS[0] (GPIO 18), [1] (GPIO 19), [2] (GPIO 20) and common GND
- Optional: use micro-JST connectors for detachability

## 6. Assembly Integration
### 6.1 Component Placement
- Refer to `LRA_PINS` array for anatomical mapping:
  - Index 0: hypothenar (pinky side of wrist)
  - Index 1: thenar (thumb base)
  - Index 2: dorsal (back of hand)
- Mount IMU over dorsal hand center (3rd metacarpal) for minimal motion artifact
- Ensure LDRA pockets do not interfere with IMU placement or strap comfort

### 6.2 Final Checks
- Verify LRA slides into pocket with light pressure (no force)
- Confirm flap overlaps opening by ≥5mm for secure closure
- Check full range of motion is not restricted
- Perform continuity test from ESP32 GPIO to LRA terminals
- Verify no shorts between signal and ground

## 7. Firmware flashing and Testing
### 7.1 Flash Order
1. `fft.py`
2. `feature_extract.py`
3. `logreg.py`
4. `scaler.py`
5. `model.py`
6. `embedded_main_hsp.py` (last)

### 7.2 Functional Validation
- Rest/baseline: LED off, LRA off (0% duty)
- Postural: LED blinks 1Hz, LRA off
- Kinetic: LED on, LRA pulses 2Hz square wave (50% duty)
- Grasp guidance/other: LED on, LRA on steady (single mode) or spatial sequence (array)

### 7.3 Wear Test
- Wear assembly for extended period
- Check for comfort, slippage, or skin irritation
- Adjust pocket placement if needed

## 8. Maintenance and Troubleshooting
### 8.1 Regular Care
- Hand wash with mild soap, air dry completely
- Lint roll Velcro hook side after washing
- Inspect elastic for loss of recovery; replace when stretched out
- Examine seams for fraying; resew if needed

### 8.2 Common Issues
- No vibration: check PWM duty, wiring continuity, solder joints
- Weak/intermittent: inspect strain relief, wire fatigue at bends
- Excessive heating: verify PWM frequency and duty cycle
- Detachment: ensure adequate flap overlap and Velcro grip

## 9. Reference Diagrams
[To be populated with annotated images]
- Figure 1: Strap layout showing IMU and LRA pocket locations
- Figure 2: LRA pocket sewing diagram with dimensions and Velcro placement
- Figure 3: Wiring diagram showing wire routing, strain relief loops, and ESP32 connections
- Figure 4: Assembled module front and back views
- Figure 5: ESP32 pinout highlighting LRA and IMU connections

## 10. Bill of Materials (BOM)
- Table listing all parts with quantities, suggested suppliers, and approximate costs

## Appendix
- A. Firmware configuration reference
- B. Haptic stage truth table
- C. Sewing stitch guide (running stitch, backstitch, bar tack)
- D. Wire gauge comparison table