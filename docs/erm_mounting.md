# ERM Motor Mounting Instructions

## Overview
This document provides detailed instructions for mounting an Eccentric Rotating Mass (ERM) vibration motor onto wearable straps using elastic fabric and Velcro closures. The ERM replaces the previous LRA (Linear Resonant Actuator) for simpler, more robust vibration feedback.

## Key Differences from LRA Mounting
- **ERM motors** are typically coin-shaped (10mm diameter × 3mm thick) with two wire leads.
- **No resonant frequency** to match — any PWM duty produces vibration.
- **Slower response** than LRA — start/stop takes a few milliseconds.
- **Mounting is similar** to LRA: secure pocket, good skin contact, strain relief on wires.

## Materials Required
- Elastic nylon/spandex strap (15-35mm wide, 4-way stretch)
- Breathable mesh fabric panels (optional for ventilation)
- Stabilizer strips (2-3mm cotton webbing or twill tape)
- Hook-and-loop tape (Velcro): sew-on type, 15-20mm width
- Fabric scissors, ruler, fabric chalk or washable marker
- Sewing pins or clips, fine needle
- Polyester/nylon upholstery thread
- ERM vibration motor (coin type, typically 10mm × 3mm)
- Optional: silicone grip dots, fabric adhesive

## Pocket Dimensions (for typical coin ERM 10mm × 3mm)
- **Shell pieces**: 14mm × 14mm cut size (provides ~10mm × 10mm internal pocket + 2mm seam allowance)
- **Flap**: 18mm × 13mm cut size
- **Velcro squares**: 12mm × 12mm (hook side on flap underside, loop side on pocket rim)

*Note: All measurements include 2mm seam allowance unless noted. Adjust if your ERM differs significantly.*

## Step-by-Step Construction

### Step 1: Cut Fabric Pieces
1. Measure and mark fabric using ruler and fabric chalk:
   - Cut two shell pieces: 14mm × 14mm rectangles
   - Cut one flap piece: 18mm × 13mm rectangle
   - Cut two Velcro squares: 12mm × 12mm (one hook, one loop)
2. If using stabilizer strip: cut a 2-3mm wide strip slightly shorter than pocket width (~8-9mm)

### Step 2: Prepare Velcro
- Hook side (rough) attaches to flap underside
- Loop side (soft) attaches to inside rim of pocket opening

### Step 3: Sew Pocket Shell
1. **Optional stabilizer placement**: Place stabilizer strip centered on inside of one shell piece.
2. **Place shell pieces together**: Right sides facing each other.
3. **Secure with pins**: Hold shells together along three sides, leaving one side open.
4. **Sew three sides**: Running stitch or backstitch with 2mm seam allowance. Backstitch at start/end.
5. **Trim corners**: Reduce bulk when turning right-side out.
6. **Turn right-side out**: Pull pocket through open side.
7. **Press flat**: Fingers to press seams flat, corners fully turned out.

### Step 4: Attach Velcro
1. **Hook Velcro to flap**: Center hook-side square on flap underside. Sew around all four edges.
2. **Loop Velcro to pocket**: With pocket right-side out, center loop-side square on inside rim of opening. Sew around all four edges.
3. **Test alignment**: Fold flap down — hook and loop should align and make full contact.

### Step 5: Finish Edges (Optional)
- Fold raw edges of open side inward by 2mm, press flat, top-stitch. Skip if flap covers edge.

### Step 6: Mount Pocket to Strap
1. **Determine placement**: See placement guidelines below.
2. **Position pocket**: Place completed ERM pocket at desired location on strap.
3. **Secure with pins**: Ensure pocket lies flat, doesn't pucker strap.
4. **Sew outer edges**: Stitch pocket to strap with running stitch or whip stitch.
   - **Critical**: Avoid stitching across open side or interfering with flap.
   - Leave small gap for wire exit toward ESP32.
5. **Reinforce stress points**: Bar tacks or extra stitching at corners.

### Step 7: Prepare for ERM Insertion
1. **Test opening**: Pocket should be wide enough to slide ERM in with light pressure.
2. **Check flap closure**: Flap should overlap opening by ≥5mm, secure with Velcro.
3. **Inspect interior**: No loose threads or sharp edges that could damage ERM wires.

## ERM Placement Guidelines

For tremor feedback, place the ERM where vibration is easily felt without interfering with hand function:

### Recommended Locations
1. **Thenar eminence (thumb base, volar side)** — best for general haptic feedback, easily felt during thumb movement.
2. **Hypothenar (pinky side, volar wrist)** — alternative, less intrusive during grasp.
3. **Dorsal wrist proximal** — visible but less felt during palm-side activities.

### Avoid
- Palm side of fingers (interferes with grasp)
- Directly over wrist joint (movement artifact)
- Areas that contact hard surfaces during typical use

### Orientation
- ERM should lie flat against skin for maximum vibration transfer.
- Wire exit should face toward ESP32 mounting location (typically forearm/wrist dorsal).
- Stitch wires every 15mm along route to prevent tugging on solder joints.

## Wiring Considerations
- ERM has two wire leads (typically red/black or both same color).
- Solder wires to ERM terminals before mounting (or use connectors).
- Create 3mm strain-relief loop at pocket entry.
- Route wires along strap interior toward ESP32.
- Secure with stitches or flexible epoxy every 15mm.

## Quality Check
Before inserting ERM:
1. **Dimensions**: Internal pocket ~10mm × 10mm.
2. **Access**: ERM slides in with light pressure.
3. **Closure**: Flap overlaps ≥5mm, Velcro secure.
4. **Strap integrity**: Elastic retains stretch/recovery.
5. **No sharp edges**: Seams smooth inside pocket.

## Maintenance
- Hand wash with mild soap, air dry.
- Lint roll Velcro after washing.
- Inspect elastic monthly for loss of recovery.
- Check wires for fatigue at bend points before each use.

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Pocket too tight | Forgot seam allowance | Remake with 14mm × 14mm shells |
| Flap doesn't stay closed | Insufficient overlap/misaligned Velcro | Ensure ≥5mm overlap, realign Velcro |
| ERM visible through fabric | Fabric too thin | Use thicker fabric or add lining |
| Vibration weak | Poor skin contact, loose pocket | Reposition for better contact, tighten strap |
| Wires pull on solder joints | Missing strain relief | Add 3mm loop, stitch or epoxy to secure |
