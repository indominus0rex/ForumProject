# LRA Mounting Instructions

## Overview
This document provides detailed instructions for mounting Linear Resonant Actuators (LRAs) onto wearable straps using elastic fabric and Velcro closures. The mounting method allows for secure attachment while maintaining comfort and enabling easy removal/replacement of components.

## Materials Required
- Elastic nylon/spandex strap (15-35mm wide, 4-way stretch)
- Breathable mesh fabric panels (optional for ventilation)
- Stabilizer strips (2-3mm cotton webbing or twill tape)
- Hook-and-loop tape (Velcro): sew-on type, 15-20mm width
- Fabric scissors
- Ruler or measuring tape
- Fabric chalk or washable marker
- Sewing pins or clips
- Fine needle
- Polyester/nylon upholstery thread (matches strap color)
- LRA components (typical size: ~10mm × 10mm × 3-4mm)
- Optional: silicone grip dots, fabric adhesive

## Pocket Dimensions
For typical LRA components (~10mm × 10mm × 3-4mm):
- **Shell pieces**: 14mm × 14mm cut size (provides 10mm × 10mm internal pocket + 2mm seam allowance on all sides)
- **Flap**: 18mm × 13mm cut size
- **Velcro squares**: 12mm × 12mm (hook side on flap underside, loop side on pocket rim)

*Note: All measurements include 2mm seam allowance unless noted otherwise. Adjust dimensions if your LRA differs significantly from 10mm × 10mm × 3-4mm.*

## Step-by-Step Construction

### Step 1: Cut Fabric Pieces
1. Measure and mark fabric using ruler and fabric chalk:
   - Cut two shell pieces: 14mm × 14mm rectangles
   - Cut one flap piece: 18mm × 13mm rectangle
   - Cut two Velcro squares: 12mm × 12mm (one hook, one loop)
2. If using stabilizer strip: cut a 2-3mm wide strip slightly shorter than the pocket width (~8-9mm)

### Step 2: Prepare Velcro
- Identify hook side (rough, prickly) and loop side (soft, fuzzy)
- Hook side will attach to flap underside
- Loop side will attach to inside rim of pocket opening

### Step 3: Sew Pocket Shell
1. **Optional stabilizer placement**: If using stabilizer strip, place it centered on the inside of one shell piece (this will be the interior of the pocket).
2. **Place shell pieces together**: Right sides facing each other (fabric sides that will be visible on the outside of the finished pocket should face inward during sewing).
3. **Secure with pins**: Use sewing pins or clips to hold shells together along three sides, leaving one side open for component insertion.
4. **Sew three sides**: Using a running stitch or backstitch, sew along three sides with a 2mm seam allowance. Begin and end stitches with a backstitch or knot for security.
5. **Trim corners**: Trim excess fabric at corners to reduce bulk when turning right-side out.
6. **Turn right-side out**: Carefully pull the pocket through the open side so that the right sides of the fabric are now facing outward.
7. **Press flat**: Use fingers to press seams flat, ensuring corners are fully turned out.

### Step 4: Attach Velcro
1. **Hook Velcro to flap**: 
   - Center the hook-side Velcro square on the underside of the flap piece.
   - Sew securely around all four edges using a tight running stitch or box stitch.
   - Ensure stitches are close to the edge but do not go through to the top side visible when flap is folded down.
2. **Loop Velcro to pocket**:
   - With pocket turned right-side out, identify the inside rim of the opening.
   - Center the loop-side Velcro square on the inside rim of the pocket opening.
   - Sew securely around all four edges, ensuring the Velcro lies flat against the fabric.
3. **Test alignment**: Fold flap down over pocket opening. Hook and loop Velcro should align and make full contact when pressed together.

### Step 5: Finish Edges (Optional)
For a cleaner finish or if flap will not cover the edge:
1. Fold raw edges of the open side inward by 2mm.
2. Press flat with fingers.
3. Top-stitch along the folded edge using a running stitch, catching both layers of fabric.
4. Secure thread with a knot on the inside.

*Note: If the flap will fully cover the pocket opening when closed, this step can be skipped as the flap will conceal the raw edges.*

### Step 6: Mount Pocket to Strap/Base
1. **Determine placement**: Refer to firmware configuration for LRA anatomical placement:
   - Single LRA: typically mounted based on use case (consult haptic feedback requirements)
   - LRA Array: 
     - Index 0 (LRA_PINS[0] = GPIO 18): hypothenar (pinky side of wrist)
     - Index 1 (LRA_PINS[1] = GPIO 19): thenar (thumb base)
     - Index 2 (LRA_PINS[2] = GPIO 20): dorsal (back of hand)
     - IMU typically mounted over dorsal hand center (3rd metacarpal)
2. **Position pocket**: Place the completed LRA pocket at the exact desired location on the elastic strap or breathable base.
3. **Secure with pins**: Use sewing pins or clips to hold pocket in place, ensuring it lies flat and does not pucker the strap.
4. **Sew outer edges**: Stitch along the outer edges of the pocket shell, attaching it securely to the strap/base. Use a running stitch or whip stitch.
   - **Critical**: Avoid stitching across the open side of the pocket or interfering with the flap's movement.
   - Stitch close to the pocket edge but leave a small gap to ensure the pocket opening remains accessible.
5. **Reinforce stress points**: Add bar tacks or extra stitching at corners where the pocket meets the strap to prevent tearing under load.

### Step 7: Prepare for LRA Insertion
1. **Test opening**: Ensure the pocket opening is wide enough to slide the LRA in with light pressure (should not require force).
2. **Check flap closure**: Fold flap down and press Velcro together. It should create a secure closure that prevents lateral movement of the LRA.
3. **Inspect interior**: Ensure no loose threads or sharp edges inside the pocket that could damage the LRA wires.

## Wiring Considerations (Reference for Next Steps)
While this document focuses on mounting, consider the following for wiring integration:
- Plan wire exit point: determine where wires will leave the pocket toward the ESP32.
- Create strain relief: when sewing wires in place (see wiring instructions), create a 3mm diameter loop where wires enter/exit the pocket and secure with stitches.
- Wire routing: follow natural contours of the strap to minimize stress points during movement.
- Secure wires: use stitches or flexible epoxy every 15mm along the wire path.

## Quality Check
Before inserting LRA:
1. **Dimensions**: Internal pocket should measure approximately 10mm × 10mm.
2. **Access**: LRA should slide in with light pressure, not force.
3. **Closure**: Flap should overlap opening by at least 5mm and secure firmly with Velcro.
4. **Strap integrity**: Elastic strap should retain its stretch and recovery properties.
5. **No sharp edges**: All seams should be smooth inside the pocket.

## Maintenance Guidelines
- **Cleaning**: Hand wash completed assembly with mild soap and water. Avoid harsh detergents that may degrade elastic or Velcro.
- **Drying**: Air dry completely before next use. Do not use dryer as heat may damage elastic and melt synthetic fabrics.
- **Velcro care**: 
  - Lint roll hook side after washing to remove debris.
  - Replace Velcro squares if grip diminishes significantly after multiple washes.
  - Avoid washing with lint-producing fabrics (e.g., cotton towels) that can clog hook side.
- **Inspection schedule**:
  - Weekly: Check elastic for loss of recovery (replace when stretched out significantly).
  - Before each use: Examine seams for fraying or separation.
  - Monthly: Verify Velcro alignment after multiple openings and closings.
  - Regularly: Inspect skin contact areas for irritation or pressure points.
- **Longevity expectations**:
  - Elastic components: 2-3 months regular use with proper care.
  - Velcro: Typically lasts 500+ closure cycles with proper maintenance.
  - Mesh fabrics: 6+ months with regular cleaning.

## Troubleshooting Common Mounting Issues
- **Pocket too tight**: 
  - Cause: Forgot seam allowance or cut pieces too small.
  - Solution: Remake pocket with correct 14mm × 14mm shell pieces (10mm internal + 2mm seam).
  - Prevention: Always add 2mm seam allowance to internal dimensions.
  
- **Flap doesn't stay closed**:
  - Cause: Insufficient flap overlap or misaligned Velcro.
  - Solution: Ensure flap overlaps opening by ≥5mm. Realign Velcro if needed.
  - Prevention: Test closure before final mounting.
  
- **Pocket sags under LRA weight**:
  - Cause: Missing stabilizer or weak seam.
  - Solution: Add stabilizer strip inside pocket seam. Reinforce seams with backstitch.
  - Prevention: Use stabilizer for components >3mm thick or if using thinner elastic.
  
- **Velcro irritates skin**:
  - Cause: Velcro placed where it contacts skin during movement.
  - Solution: Reposition pocket so Velcro faces inward toward strap or add fabric barrier.
  - Prevention: Always place hook side where it faces strap material, not skin.
  
- **Strap puckers around pocket**:
  - Cause: Insufficient ease or overly tight stitching.
  - Solution: Remount with slight ease in fabric; use flexible stitch that allows stretch.
  - Prevention: Use stretch stitch or zigzag if sewing machine allows; hand sew with loose tension.

## Integration with Wiring
After completing mounting:
1. Follow wiring instructions to prepare LRA with wires and strain relief.
2. Route wires from LRA terminals along inside of strap toward ESP32 location.
3. Secure wires with stitches or flexible epoxy every 15mm.
4. Create strain-relief loops at pocket entry/exit points and where wires exit strap.
5. Connect to ESP32 GPIO pins per firmware configuration (LRA_PIN for single, LRA_PINS for array).
6. Perform final assembly check: LRA inserts easily, wires move freely with strap, no tugging on connections.

This mounting method provides a secure, adjustable, and removable system for integrating LRAs into wearable tremor monitoring devices while maintaining user comfort and enabling long-term use.