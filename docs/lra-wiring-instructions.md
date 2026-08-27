# LRA Wiring Instructions

## Overview
This document provides detailed instructions for wiring Linear Resonant Actuators (LRAs) to the ESP32 in the wearable IMU tremor monitoring system. It covers wire preparation, soldering, strain relief, routing, and connection to the ESP32 GPIO pins, ensuring durability and reliability for wearable use.

## Materials Required
- Linear Resonant Actuators (LRAs) - already mounted in fabric pockets per mounting instructions
- 30AWG silicone-insulated stranded wire (2-core recommended for flexibility)
- Wire strippers/cutters
- Soldering iron and solder (lead-free, rosin-core)
- Heat-shrink tubing (various sizes: 1.5mm, 3mm, 6mm)
- Heat gun or lighter
- Tweezers
- Small screwdriver or helping hands (optional)
- Multimeter (for validation)
- Fabric glue or flexible epoxy (e.g., E6000, Sugru) for wire securing
- Fine needle and polyester/nylon upholstery thread (for stitching wires to strap)
- Scissors
- Ruler or measuring tape
- Fabric chalk or washable marker
- Optional: micro-JST PH 2-pin connectors (for detachable wiring)
- Optional: connector housings and crimp tools (if using JST)

## Wire Preparation
### Step 1: Cut and Strip Wires
1. For each LRA, cut two lengths of 30AWG silicone-stranded wire:
   - Length from LRA to strain relief loop inside pocket: ~20mm
   - Length from pocket exit to ESP32: measure along strap route + 20mm for slack and strain relief
   - Total per wire: typically 40-60mm (adjust based on strap length and routing)
2. Strip 3mm of insulation from each end of each wire using wire strippers.
   - Avoid nicking the conductor strands.
   - Twist strands gently to prevent fraying.

### Step 2: Tin the Wire Ends
1. Apply a small amount of solder to each stripped end to prevent oxidation and ease soldering.
   - Hold wire with tweezers, touch soldering iron to wire, apply solder to the wire (not the iron).
   - Aim for a smooth, shiny coating; avoid blobs or cold joints.

### Step 3: Prepare LRA Terminals
1. Identify LRA terminals (usually two pads or wires; note polarity if LRA is polarized).
   - Consult LRA datasheet if unsure; many LRAs are not polarized but check.
2. If terminals are not pre-tinned, apply a small amount of solder to each terminal.

## Soldering Wires to LRA
### Step 4: Solder Wire to LRA
1. Position LRA securely (use helping hands or tape to hold flat).
2. Touch soldering iron to LRA terminal and wire end simultaneously for 1-2 seconds.
   - The solder on both should flow and join.
   - Remove iron and hold wire steady until solder cools (2-3 seconds).
   - Inspect joint: should be concave and smooth, not ball-shaped or cracked.
3. Repeat for second wire to second terminal.
4. Optional polarity marking: if LRA is polarized, use a permanent marker to note + and - on wire insulation near solder joint.

### Step 5: Insulate Solder Joints
1. Cut a 6mm length of 1.5mm or 2mm heat-shrink tubing.
2. Slide tubing over solder joint (before soldering if possible, or carefully over after if joints are small).
3. Apply heat evenly until tubing shrinks tightly around joint and insulation.
   - Avoid overheating wire insulation or LRA.
   - Tubing should be clear and conformal.

## Adding Strain Relief at LRA
### Step 6: Create Strain-Relief Loop at LRA Entry
1. Measure ~5mm from the solder joint along each wire.
2. Bend each wire back toward the LRA to form a 3mm diameter loop.
   - Loop should be in the plane perpendicular to wire exit to prevent tugging on joint.
3. Secure loop to the fabric pocket interior using a few stitches of polyester thread.
   - Stitch through the loop and fabric, not through the wire itself.
   - Alternatively, use a small dab of flexible epoxy to hold loop in place (allow to cure).
4. Ensure loop does not pull on solder joint when wire is tugged gently.

## Routing Wires Along Strap
### Step 7: Determine Wire Path
1. Lay out the strap with LRA pocket mounted.
2. Identify ESP32 mounting location (typically on dorsal wrist or forearm).
3. Plan wire route following natural contours of strap to minimize stress points.
   - Avoid sharp bends; use gradual curves.
   - Route wires on the inside of the strap (next to skin) for protection and comfort.
   - Keep wires flat and not twisted.

### Step 8: Secure Wires to Strap
1. Starting at the LRA pocket, lay wire along planned route.
2. Every 15mm, secure wire to strap using one of:
   - **Stitching**: Use needle and thread to make a loose loop over wire (not through wire) and stitch to strap.
   - **Flexible epoxy**: Apply a small dot of epoxy (e.g., Sugru) to strap, press wire into it, allow to cure.
   - **Fabric glue**: Use a washable fabric glue in small dots.
3. Ensure wire lies flat and does not create bumps or pressure points.
4. Continue securing until reaching ESP32 location.

### Step 9: Create Strain-Relief Loop at Strap Exit
1. Before reaching the ESP32 mounting point, create a second 3mm diameter strain-relief loop.
   - This loop should be where the wire exits the strap toward the ESP32 board.
2. Secure loop to strap using stitches or epoxy, ensuring it does not pull on wire when bent.

## Preparing for ESP32 Connection
### Step 10: Prepare ESP32 End
1. Strip 3mm of insulation from the end of each wire at the ESP32 side.
2. Tin the exposed ends with solder.
3. Optional: if using micro-JST connectors:
   - Crimp JST pins onto tinned wire ends.
   - Insert pins into JST housing (observe polarity if marking used).
   - Mate with corresponding header on ESP32 side.

## Connecting to ESP32
### Step 11: Identify ESP32 GPIO Pins
1. Consult firmware configuration (`firmware/common/config.py`):
   - Single LRA mode: `LRA_PIN` (default GPIO 25)
   - LRA Array mode: `LRA_PINS` array (default [18, 19, 20] for [hypothenar, thenar, dorsal])
   - Ground: any GND pin on ESP32
2. Verify pin capabilities: LRAs require PWM-capable GPIOs (all listed pins support PWM).

### Step 12: Solder Wires to ESP32
1. Position ESP32 securely (use helping hands or breadboard).
2. For each LRA wire:
   - Touch soldering iron to ESP32 GPIO pin and wire end simultaneously.
   - Join solder and remove iron; hold steady until cool.
   - Inspect joint for quality.
3. Connect both wires from each LRA to:
   - One wire to GPIO pin (signal)
   - Other wire to GND
   - If using array, repeat for each LRA to its respective GPIO and common GND.
4. Optional: if using headers or sockets, solder wires to header pins instead of directly to ESP32.

### Step 13: Insulate ESP32 Connections
1. Cut small pieces of heat-shrink tubing (6mm length, 2mm or 3mm diameter).
2. Slide over each solder joint at ESP32.
3. Apply heat to shrink tubing, insulating joints and preventing shorts.

## Final Assembly and Validation
### Step 14: Perform Continuity Check
1. Set multimeter to continuity or lowest ohms setting.
2. For each LRA:
   - Check continuity between the two wires at the LRA end (should be near 0 ohms).
   - Check continuity between each wire and its corresponding ESP32 connection.
   - Verify no continuity between signal wire and GND wire (should be open).
   - Verify no continuity between signal wire and adjacent signal wires (if array).

### Step 15: Check for Shorts
1. With multimeter in continuity mode:
   - Check between each signal wire and GND (should be open).
   - Check between adjacent signal wires (should be open).
   - Check between any wire and the ESP32 metal shielding (if present) - should be open.

### Step 16: Mechanical Strain Test
1. Gently flex the strap along its intended range of motion.
2. Observe wires: they should move freely without pulling on solder joints.
3. Verify strain relief loops absorb bending forces (joints should not flex).
4. Ensure LRA pockets do not pull on wires when strap is stretched.

### Step 17: Functional Test (Pre-Firmware Flash)
1. Connect ESP32 to power source (USB or battery).
2. Use a multimeter to measure voltage between GPIO and GND when pin is driven high (3.3V) - optional.
3. Alternatively, use a simple test script to toggle GPIO and observe LRA response (requires firmware).

## Notes on Wire Selection and Preparation
- **Wire Gauge**: 30AWG is recommended for flexibility and durability in wearable applications.
  - Thicker wire (28AWG or lower) is less flexible and may cause discomfort.
  - Thinner wire (32AWG or higher) is more prone to breakage from flexing.
- **Insulation**: Silicone-insulated wire remains flexible at low temperatures and resists cracking.
- **Stranded vs Solid**: Stranded wire is essential for flexibility; solid wire will break quickly.
- **Color Coding**: Use consistent colors (e.g., red for signal, black for ground) to avoid confusion.

## Integration with Firmware
1. Ensure firmware configuration matches your wiring:
   - `LRA_PIN` or `LRA_PINS` set to correct GPIOs.
   - `LRA_FREQ = 200` (Hz) for optimal LRA resonance.
   - `LRA_DUTY_ON = 512` (50% duty cycle) for standard drive.
   - `USE_LRA_ARRAY = True` if using array of LRAs on GPIOS 18,19,20.
2. The haptic stage (`firmware/stages/haptic.py`) will control the LRAs based on tremor classification:
   - Rest/baseline: LRA off (0% duty)
   - Postural: LRA off
   - Kinetic: LRA pulses at 2Hz (50% duty square wave)
   - Grasp guidance/other: LRA on steady (single mode) or spatial sequence (array)

## Troubleshooting Wiring Issues
- **No vibration from LRA**:
  - Check continuity from ESP32 GPIO to LRA terminal.
  - Verify solder joints are solid and not cracked.
  - Confirm firmware is driving GPIO (check with oscilloscope or multimeter).
  - Ensure LRA is not shorted to ground.
- **Intermittent vibration**:
  - Inspect strain relief loops: wires should move freely at loops, not pull on joints.
  - Check for wire fatigue at bend points (look for discoloration or stiffness).
  - Verify solder joints are not cracked from flexing.
- **LRA weak or sporadic**:
  - Confirm PWM frequency is exactly 200Hz (use oscilloscope or logic analyzer).
  - Check duty cycle is not stuck at 0% or 100%.
  - Ensure LRA is firmly coupled to body through pocket (no air gap).
- **ESP32 resets or behaves erratically**:
  - Check for shorts between signal and ground wires.
  - Verify no loose wire strands touching adjacent GPIO pins.
  - Ensure proper grounding and decoupling on ESP32 board (if using custom board).

## Maintenance and Longevity
- **Regular Inspection**:
  - Before each use: check wires for fraying, especially at strain relief points and solder joints.
  - Monthly: flex strap through full range of motion and watch for wire movement or joint stress.
- **Cleaning**:
  - Hand wash assembly with mild soap; avoid submerging ESP32 if not waterproof.
  - Air dry completely; do not use heat sources that may degrade wire insulation.
- **Wire Replacement**:
  - If wire shows signs of wear, desolder and replace with new 30AWG silicone-stranded wire.
  - Repeat all steps: tin, solder, strain relief, routing, securing.
- **Velcro and Mounting**:
  - Follow mounting instructions for care of fabric pockets and Velcro.
  - Ensure LRA remains securely pocketed; wires should not bear weight of LRA.

This wiring method provides a robust, flexible, and durable connection for LRAs in wearable tremor monitoring systems, following best practices for strain relief, insulation, and mechanical durability.