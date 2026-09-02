# Wearable Tremor Monitoring System Wiring Diagram - Clear Connections Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Create a clear, accurate wiring diagram of the Forum Project wearable tremor monitoring system that shows all electrical connections between components with proper labeling and visual clarity.

**Architecture:** Create an SVG-based wiring diagram that logically separates components (ESP32, multiplexer, sensors, actuators) and uses color-coded, clearly labeled connections to show electrical pathways.

**Tech Stack:** HTML/CSS/SVG for diagram creation, potentially using automated generation from firmware configuration files.

---

### Task 1: Analyze Firmware Configuration for Accurate Pin Mapping

**Objective:** Extract exact pin assignments and component specifications from firmware configuration files to ensure diagram accuracy.

**Files:**
- Read: `C:\ForumProject\firmware\common\config.py`
- Read: `C:\ForumProject\firmware\embedded_main_hsp.py`
- Create: `C:\ForumProject\docs\pin_assignments.md` (documentation of extracted pins)

**Step 1: Extract pin assignments from config.py**

```python
# Extract these values from common/config.py:
SAMPLES = 128
SAMPLE_INTERVAL_US = 10000  # 100 Hz
SAMPLE_RATE_HZ = 100.0
LED_PIN = 2
LRA_PIN = 25
LRA_FREQ = 200
LRA_PINS = [18, 19, 20]  # Proximal-to-distal: [hypothenar, thenar, dorsal]
USE_LRA_ARRAY = False
I2C_BUS = 0
I2C_SCL_PIN = 22
I2C_SDA_PIN = 21
I2C_FREQ = 400000
GY521_ADDR = 0x68
TCA9548A_ADDR = 0x70
NUM_IMUS = 4
```

**Step 2: Verify usage in embedded_main_hsp.py**

Check how these pins are actually used in the code:
- LED initialization
- LRA/PWM initialization  
- I2C initialization
- Sensor initialization

**Step 3: Create pin assignments documentation**

Create a markdown file documenting:
- ESP32 pin functions and usage
- I2C bus configuration
- PWM channels for LRA control
- GPIO usage for LED
- Multiplexer address and channel mapping

**Step 4: Run verification**

Verify extracted values match actual firmware usage by checking:
- All pin usages in embedded_main_hsp.py
- Any conditional code based on USE_LRA_ARRAY

**Step 5: Commit**

```bash
git add C:\ForumProject\docs\pin_assignments.md
git commit -m "docs: extract pin assignments for wiring diagram accuracy"
```

---

### Task 2: Determine Diagram Layout and Component Placement

**Objective:** Design a logical layout for the wiring diagram that separates functional blocks and minimizes wire crossings.

**Files:**
- Create: `C:\ForumProject\docs\diagram_layout.md` (layout design document)
- Create: `C:\ForumProject\templates\wiring_diagram_template.html` (basic template)

**Step 1: Define functional blocks**

Identify logical groupings:
- Microcontroller Block (ESP32 with labeled pins)
- Communication Block (TCA9548A multiplexer)
- Sensor Block (4 × IMU sensors)
- Actuator Block (3 × LRA actuators)
- Indicator Block (Status LED)
- Power/Ground Rails

**Step 2: Choose layout strategy**

Options:
- Left-to-right: ESP32 → MUX → Sensors (top) + Actuators (bottom)
- Top-to-bottom: Processing → Communication → Sensors/Actuators
- Radial: ESP32 center with components arranged around

Select left-to-right flow for clear signal path visualization.

**Step 3: Assign anatomical locations**

Based on documentation research:
- IMU1: Dorsal hand center (global motion)
- IMU2: Thenar eminence (thumb abduction/adduction)  
- IMU3: Thumb CMC joint (thumb rotation)
- IMU4: Forearm proximal wrist (wrist flexion/extension)
- LRA1: Dorsal hand (position feedback)
- LRA2: Palmar - thenar (thumb feedback)  
- LRA3: Palmar - hypothenar (pinky finger feedback)

**Step 4: Create layout documentation**

Document:
- Component positioning coordinates
- Flow direction (left to right: processing → communication → sensors → actuators)
- Ankoring points for wire connections
- Label placement strategy

**Step 5: Create basic HTML template**

Create starter template with:
- CSS for clean, technical appearance
- SVG container for diagram
- Legend section
- Component specifications table
- Notes section

**Step 6: Commit**

```bash
git add C:\ForumProject\docs\diagram_layout.md C:\ForumProject\templates\wiring_diagram_template.html
git commit -m "docs: create wiring diagram layout plan and template"
```

---

### Task 3: Create Base Diagram Structure with Components

**Objective:** Build the foundational SVG diagram with all components placed in their logical positions.

**Files:**
- Create: `C:\ForumProject\wearable_tremor_wiring_diagram_v2.html` (working diagram file)

**Step 1: Set up HTML structure**

Create HTML file with:
- Proper DOCTYPE and meta tags
- Linked stylesheet (internal or external)
- Container div for diagram
- Sections for diagram, specifications, legend, notes

**Step 2: Create ESP32 component**

Draw:
- Rectangle representing ESP32 dev board
- Label: "ESP32 Dev Board"
- Left side pins (vertical): GPIO22 SCL, GPIO21 SDA, GND, 3.3V
- Right side pins (vertical): GPIO18 PWM1, GPIO19 PWM2, GPIO20 PWM3, GPIO25 LRA_SINGLE, GPIO2 LED
- Connection points (small circles) at each pin location
- Pin labels using consistent font and sizing

**Step 3: Create TCA9548A multiplexer component**

Draw:
- Rectangle to the right of ESP32
- Label: "TCA9548A" with subtitle "Addr: 0x70"
- Left side pins: SCL, SDA
- Right side pins: Ch0, Ch1, Ch2, Ch3 (horizontal row)
- Connection points at each pin

**Step 4: Create IMU sensor components**

Draw:
- Four circles (or small rectangles) to the right of multiplexer
- Labels: IMU1, IMU2, IMU3, IMU4
- Anatomical labels below each: Dorsal Hand, Thenar Eminence, Thumb CMC, Forearm Wrist
- Connection points at center-left of each component (for I2C connection)

**Step 5: Create LRA actuator components**

Draw:
- Three rectangles vertically aligned to the right/bottom
- Labels: LRA1, LRA2, LRA3
- Anatomical labels: Dorsal Hand, Palmar-Thenar, Palmar-Hypothenar
- Connection points at center-left of each component (for PWM connection)

**Step 6: Create LED component**

Draw:
- Small circle or LED symbol connected to GPIO2
- Label: "Status LED"

**Step 7: Add power and ground rails**

Draw:
- Horizontal red line at top for 3.3V power rail
- Horizontal black line at bottom for GND rail
- Connection points where components connect to rails
- Or connect power/ground directly from ESP32 pins to components

**Step 8: Commit initial structure**

```bash
git add C:\ForumProject\wearable_tremor_wiring_diagram_v2.html
git commit -m "feat: create base wiring diagram structure with all components"
```

---

### Task 4: Implement Color-Coded Connection System

**Objective:** Add clearly visible, color-coded wires showing all electrical connections according to firmware specification.

**Files:**
- Modify: `C:\ForumProject\wearable_tremor_wiring_diagram_v2.html`

**Step 1: Define color scheme**

Establish consistent colors:
- I2C SCL: Blue (#2980b9)
- I2C SDA: Green (#27ae60)
- PWM Signals: Orange (#e67e22)
- LED Signal: Purple (#9b59b6)
- Power (3.3V): Red (#e74c3c)
- Ground: Black/Dark Gray (#2c3e50)
- Component outlines: Gray (#95a5a6)

**Step 2: Implement I2C connections**

Draw wires for:
- ESP32 GPIO22 (SCL) → TCA9548A SCL
- ESP32 GPIO21 (SDA) → TCA9548A SDA
- TCA9548A Ch0-Ch3 → IMU1-IMU4 (both SCL and SDA lines to each IMU)
- Use smooth curves or orthogonal routing to avoid crossings
- Add small dots at connection points for clarity

**Step 3: Implement PWM connections**

Draw wires for:
- ESP32 GPIO18 → LRA1
- ESP32 GPIO19 → LRA2  
- ESP32 GPIO20 → LRA3
- Keep these visually distinct from I2C lines
- Consider bundling or routing to minimize visual clutter

**Step 4: Implement LED connection**

Draw wire for:
- ESP32 GPIO2 → Status LED
- Use signal color (purple)

**Step 5: Implement power and ground connections**

Draw connections for:
- ESP32 3.3V pin → Power rail → Components needing power
- ESP32 GND pin → Ground rail → Components needing ground
- Or direct connections from ESP32 pins to each component that needs power/ground
- Besides ESP32 itself, TCA9548A and IMUs need power/ground

**Step 6: Add connection labeling**

At key points, add small text labels indicating:
- Signal names (SCL, SDA, PWM1, etc.)
- Especially at component interfaces
- Keep labels small but legible

**Step 7: Verify all connections match firmware**

Double-check that every connection shown corresponds to actual pin usage in firmware.

**Step 8: Commit**

```bash
git add C:\ForumProject\wearable_tremor_wiring_diagram_v2.html
git commit -m "feat: implement color-coded wiring connections with labels"
```

---

### Task 5: Add Comprehensive Legend and Specifications

**Objective:** Create a clear legend explaining all symbols, colors, and component information.

**Files:**
- Modify: `C:\ForumProject\wearable_tremor_wiring_diagram_v2.html`

**Step 1: Create visual legend**

Design legend with:
- Color samples for each wire type with labels
- Symbol explanations for different component types
- Line style explanations (if using different styles)
- Connection point explanation

**Step 2: Create component specifications table**

Build table with columns:
- Component
- Type/Model
- Quantity
- Function
- Connection Details

Populate with:
- Microcontroller: ESP32 Dev Board, 1, Main processing, GPIO22=SCL, GPIO21=SDA, GPIO18/19/20=PWM Array, GPIO2=LED
- IMU Sensor: GY-521 (MPU6050), 4, Motion detection, I2C via TCA9548A @ 0x70
- Actuator: Linear Resonant Actuator (LRA), 3, Haptic feedback, PWM @ 200Hz on GPIO18,19,20
- Indicator: LED, 1, System status, GPIO2
- Multiplexer: TCA9548A, 1, I2C bus expansion, Address 0x70, 4 channels

**Step 3: Add anatomical placement notes**

Include section with:
- Suggested IMU placement locations and rationale
- Suggested LRA placement locations and rationale
- Reference to user documentation/research

**Step 4: Add configuration notes**

Explain:
- Based on firmware configuration in common/config.py
- Current setting: USE_LRA_ARRAY = False (single LRA on GPIO25)
- Diagram shows 3-LRA array mode (would require USE_LRA_ARRAY = true)
- Other fixed configurations (sampling rate, window size, etc.)

**Step 5: Commit**

```bash
git add C:\ForumProject\wearable_tremor_wiring_diagram_v2.html
git commit -m "feat: add legend, specifications, and configuration notes to wiring diagram"
```

---

### Task 6: Review, Validate, and Finalize Diagram

**Objective:** Verify the diagram is accurate, clear, and meets all requirements.

**Files:**
- Modify: `C:\ForumProject\wearable_tremor_wiring_diagram_v2.html`

**Step 1: Accuracy verification**

Check against firmware:
- [ ] All ESP32 pins used correctly per config.py and embedded_main_hsp.py
- [ ] I2C connections: GPIO22/SCL, GPIO21/SDA to TCA9548A
- [ ] TCA9548A channels 0-3 connected to 4 IMUs
- [ ] PWM connections: GPIO18,19,20 to 3 LRAs (in array mode)
- [ ] LED on GPIO2
- [ ] Power and ground connections properly shown

**Step 2: Clarity verification**

Ensure:
- [ ] Wires don't obscure components or labels
- [ ] Connection points are clearly visible
- [ ] Labels are legible and not overlapping
- [ ] Color coding is consistent and explained
- [ ] Diagram flows logically left to right
- [ ] Component spacing is adequate

**Step 3: Label verification**

Check:
- [ ] All components have clear labels
- [ ] All pins have legible labels
- [ ] Connection points are identifiable
- [ ] Anatomical labels are present and correct
- [ ] Legend is complete and understandable

**Step 4: Test in multiple browsers**

Open diagram in:
- Chrome/Firefox/Edge to verify rendering
- Check at different zoom levels
- Verify colors display correctly
- Ensure text is readable

**Step 5: Create final version**

Once verified:
- Rename or copy to final name: `C:\ForumProject\wearable_tremor_wiring_diagram.html`
- Ensure it's the definitive version
- Add any final polish

**Step 6: Commit final version**

```bash
git add C:\ForumProject\wearable_tremor_wiring_diagram.html
git commit -m "feat: finalize clear wiring diagram with verified connections and labels"
```

---

## Files Likely to Change

- `C:\ForumProject\docs\pin_assignments.md` (new)
- `C:\ForumProject\docs\diagram_layout.md` (new)
- `C:\ForumProject\templates\wiring_diagram_template.html` (new)
- `C:\ForumProject\wearable_tremor_wiring_diagram.html` (will be created/updated)
- Possibly: `C:\ForumProject\wearable_tremor_wiring_diagram_v2.html` (intermediate)

## Tests / Validation

**Validation checks:**
1. Pin assignment accuracy: Compare diagram connections to firmware config.py
2. Completeness check: Verify all components from BOM are shown
3. Connection correctness: Every wire in diagram matches actual firmware usage
4. Clarity check: No overlapping labels, legible text, distinct colors
5. Rendering test: Displays correctly in Chrome, Firefox, Edge
6. Label correctness: All component/pin labels match firmware

**Manual verification steps:**
- Open generated HTML in web browser
- Visually inspect connections match pin assignments
- Check legend explains all symbols and colors
- Verify anatomical placement notes are accurate
- Confirm specifications table matches actual hardware

## Risks, Tradeoffs, and Open Questions

**Risks:**
- Diagram becomes too cluttered with many wires
- Misinterpretation of pin usage if firmware is complex
- Anatomical placement suggestions may not be universally optimal
- Maintaining diagram accuracy if firmware changes frequently

**Tradeoffs:**
- Simplicity vs. completeness: May omit some power/ground details for clarity
- Geometric accuracy vs. topological clarity: May not represent exact physical layout
- Detailed labels vs. clean appearance: Balance between information and readability

**Open questions:**
- Should the diagram show actual physical layout on PCB or logical connections?
- Should we include decoupling capacitors and other passive components?
- Should we show the actual hand anatomy or keep it abstract?
- Should we create multiple versions (detailed technical vs. presentation simplified)?

**Assumptions:**
- User wants logical/electrical wiring diagram, not physical PCB layout
- Focus is on showing connections between major components
- Anatomical placement is advisory/reference only
- Diagram should reflect capability (3-LRA array) even if current firmware uses single LRA
- Standard ESP32 Dev Board pinout is applicable