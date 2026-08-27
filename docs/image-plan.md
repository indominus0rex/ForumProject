# Image Plan for LRA Assembly Guide

This document outlines the images/diagrams needed for the LRA Assembly Guide, their sources, and what annotations/labels should be included.

## Required Images

### 1. Strap Layout Diagram
**Purpose**: Show anatomical placement of IMU and LRAs on the wearable strap.
**Source**: To be created based on `docs/strap_and_lra_design.md` and firmware `LRA_PINS` mapping.
**Annotations to Include**:
- Label elastic strap orientation (proximal/distal ends)
- Mark IMU placement: dorsal hand center (3rd metacarpal) with icon
- Label LRA pocket locations:
  - LRA 0 (hypothenar/pinky side) if using array
  - LRA 1 (thenar/thumb base) if using array
  - LRA 2 (dorsal/back of hand) if using array
  - Single LRA placement variant (if applicable)
- Indicate strap width and length dimensions
- Show direction of strap wear (which way goes up arm/hand)
- Callout: "Refer to firmware/config.py LRA_PINS for GPIO mapping"

### 2. LRA Pocket Sewing Diagram
**Purpose**: Illustrate pocket construction with dimensions and part placement.
**Source**: Based on mounting skill dimensions and typical LRA size (10mm × 10mm × 3-4mm).
**Annotations to Include**:
- Shell piece: 14mm × 14mm cut (show 2mm seam allowance, internal 10mm × 10mm)
- Flap piece: 18mm × 13mm cut
- Velcro squares: 12mm × 12mm (hook on flap underside, loop on pocket rim)
- Optional stabilizer strip placement inside pocket seam
- Thread path for sewing (running stitch/backstitch)
- Arrow showing "turn right-side out" step
- Label: "Internal pocket size: 10mm × 10mm"
- Label: "Flap overlap: ≥5mm for secure closure"
- Callout: "Use 30AWG silicone wire for connections (see wiring diagram)"

### 3. Wiring Overview Diagram
**Purpose**: Show wire routing from LRA to ESP32 along the strap.
**Source**: To be created depicting a representative strap with mounted LRA pocket.
**Annotations to Include**:
- LRA pocket with wires exiting
- Strain-relief loop at pocket entry (3mm diameter, secured with stitch)
- Wire routing path along inside of strap
- Regular wire securing points every 15mm (stitches or epoxy dots)
- Strain-relief loop at strap exit toward ESP32 (3mm diameter)
- ESP32 mounting location with labeled GPIOs:
  - Single LRA: GPIO 25 (LRA_PIN) and GND
  - Array: GPIO 18 (LRA_PINS[0]), GPIO 19 [1], GPIO 20 [2], common GND
- Wire color coding suggestion (e.g., red = signal, black = ground)
- Callout: "Use 30AWG silicone-insulated stranded wire"
- Callout: "Create strain-relief loops where wire enters/exits pocket and strap"

### 4. Strain-Relief Loop Detail
**Purpose**: Close-up showing proper strain-relief loop formation.
**Source**: Macro detail or diagram.
**Annotations to Include**:
- 3mm diameter loop dimension
- Loop positioned 5mm from solder joint
- Loop secured to fabric with stitch (show thread path)
- Direction of wire bend to prevent tug on joint
- Label: "Loop absorbs bending forces, protects solder joint"
- Callout: "Essential for preventing wire fatigue"

### 5. Solder Joint and Heat-Shrink Detail
**Purpose**: Show proper solder joint and insulation.
**Source**: Close-up photo or diagram.
**Annotations to Include**:
- Concave, smooth solder joint (not ball or cracked)
- Heat-shrink tubing fully covering joint and wire insulation
- Label: "Solder joint: smooth concave fillet"
- Label: "Heat-shrink: 1.5mm tubing, overlapping insulation"
- Callout: "Avoid cold joints or excess solder"

### 6. Assembled Module Views
**Purpose**: Show final assembly from multiple angles.
**Source**: Photos of completed assembly (to be provided by user or simulated).
**Annotations to Include**:
- Front view: strap with pockets closed, flaps down
- Side view: showing low profile of pockets and wires
- Close-up of pocket opening with LRA inserted, flap secured
- Close-up of wire exit point with strain-relief loop
- ESP32 mounted on strap with wires connected
- Label: "LRA slides in with light pressure"
- Label: "Flap overlaps opening by ≥5mm"
- Label: "Wires lie flat, no pressure points"
- Callout: "Check continuity before final sealing"

### 7. ESP32 Pinout Reference
**Purpose**: Show ESP32 pinout with LRA and IMU connections highlighted.
**Source**: Standard ESP32-WROOM-32 pinout diagram.
**Annotations to Include**:
- Highlight I2C pins: SCL (GPIO 22), SDA (GPIO 21) for IMU
- Highlight LRA pins per firmware:
  - Single: GPIO 25 (LRA_PIN)
  - Array: GPIO 18, 19, 20 (LRA_PINS)
- Highlight LED pin: GPIO 2
- Ground pins: any GND
- Label: "I2C Bus: SCL=22, SDA=21 @ 400kHz"
- Label: "LRA PWM: 200Hz, 50% duty"
- Label: "LED: GPIO 2"
- Callout: "Verify pin assignments in firmware/common/config.py"

### 8. Haptic Feedback Truth Table (Optional Diagram)
**Purpose**: Visualize LRA/LED behavior per tremor label.
**Source**: Based on haptic stage logic.
**Annotations to Include**:
- Table or flowchart showing:
  - Label: rest/baseline → LED off, LRA off (0% duty)
  - Label: postural → LED blinks 1Hz, LRA off
  - Label: kinetic → LED on, LRA pulses 2Hz (50% duty square wave)
  - Label: grasp_guidance/other (single): LED on, LRA on steady (50% duty)
  - Label: grasp_guidance/other (array): spatial sequence (LRA 0→1→2→0... at ~3Hz)
- Label: "See firmware/stages/haptic.py for exact timing"
- Callout: "LRA duty cycle: 512/1024 = 50%"

## Image Creation Guidance
1. **Base Images**: Can be created using:
   - Hand drawings scanned/photographed
   - Digital illustration tools (Inkscape, Illustrator, PowerPoint)
   - Photos of actual components and prototypes
   - Screenshots of firmware/config files (for pinout)
2. **Annotation Tools**: Use:
   - Inkscape/Illustrator for vector callouts
   - PowerPoint or Word for simple shapes and text
   - Image editors (GIMP, Photoshop) for labeling photos
3. **Consistency**: Use same visual language across images:
   - Color code: red for power/signal, black for ground, blue for I2C
   - Use consistent arrow styles for motion/direction
   - Use consistent box/styles for labels and callouts
4. **Size**: Aim for images that are clear when viewed at 100% in markdown (approx 600-800px width).
5. **Format**: Save as PNG or SVG for best quality in markdown.

## Image Integration into Guide
In the final assembly guide (`docs/LRA-Assembly-Guide.md`), images will be embedded using markdown syntax:
![Description](path/to/image.png)
*Caption: Detailed explanation of what the image shows.*

Each image should be referenced in the relevant section with a clear caption.

## Next Steps
1. Create or source base images per this plan.
2. Annotate images with labels and callouts as specified.
3. Insert annotated images into the assembly guide draft.
4. Proceed to final assembly and review tasks.