# Revised Detailed Prompt for Wiring Diagram Generation (Position Texts Removed)

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Provide a revised detailed prompt for AI image generators that focuses ONLY on electrical connections and component labels, removing all anatomical placement descriptions.

**Architecture:** Modify the original detailed prompt by removing all sections related to anatomical placement, suggested positioning, and position-related notes while preserving all connection details, component labels, pin mappings, legends, and specifications.

**Tech Stack:** Text processing and prompt engineering.

---

## Revised Detailed Prompt (Position/Anatomical Texts Removed)

Create a precise technical wiring diagram for an ESP32-based wearable Parkinson's tremor monitoring system. The diagram must follow these exact specifications:

LAYOUT & COMPOSITION:
- Clean, flat vector style with white background
- Left-to-right logical flow: Power → ESP32 → Multiplexer → Sensors (top) + Actuators (bottom) + Indicators
- Minimal wire crossings using bus routing and orthogonal connections
- All components clearly labeled with pin numbers and functions
- Professional electronics schematic aesthetic with consistent line weights

COMPONENT DETAILS:

1. POWER SECTION (Far Left):
   - Horizontal 3.3V power rail: thick RED line (#E74C3C) at y=80
   - Horizontal GND rail: thick BLACK line (#2C3E50) at y=720
   - Vertical connection points every 100px along rails (small 4px diameter circles)

2. ESP32 DEV BOARD (x=100-280, y=200-400):
   - Light gray rounded rectangle (#ECF0F1) with dark gray stroke (#34495E), 2px width
   - Label: "ESP32 Dev Board" centered at top (12px bold, #2C3E50)
   - LEFT SIDE PINS (vertical, 20px spacing, labels left-aligned 10px left):
     * GPIO22: "SCL" (blue connection point)
     * GPIO21: "SDA" (green connection point)
     * GND: "GND" (black connection point)
     * 3.3V: "3.3V" (red connection point)
     * GPIO2: "LED" (purple connection point)
     * GPIO25: "LRA" (red-orange connection point)
   - RIGHT SIDE PINS (vertical, 20px spacing, labels right-aligned 10px right):
     * GPIO18: "PWM1" (orange)
     * GPIO19: "PWM2" (orange)
     * GPIO20: "PWM3" (orange)
     * GPIO??: "NC" (gray)
     * GPIO??: "NC" (gray)
     * GPIO??: "NC" (gray)
   - Connection points: 3px diameter circles at each pin location (matching pin colors)

3. TCA9548A MULTIPLEXER (x=400-540, y=250-370):
   - Light gray rounded rectangle (#ECF0F1) with purple stroke (#8E44AD), 2px width
   - Label: "TCA9548A" centered at top (12px bold, #2C3E50)
   - Sub-label: "Addr: 0x70" centered below (10px italic, #8E44AD)
   - LEFT SIDE PINS:
     * SCL: blue connection point at (400,300)
     * SDA: green connection point at (400,340)
   - RIGHT SIDE PINS (horizontal, 20px spacing, labels above):
     * Ch0: dual connection points (SCL-BLUE at (540,280), SDA-GREEN at (540,300))
     * Ch1: dual connection points (SCL-BLUE at (540,320), SDA-GREEN at (540,340))
     * Ch2: dual connection points (SCL-BLUE at (540,360), SDA-GREEN at (540,380))
     * Ch3: dual connection points (SCL-BLUE at (540,400), SDA-GREEN at (540,420))
   - Connection points: 3px diameter matching pin colors

4. IMU SENSORS (Four units, x=700-1000, y=150-250):
   - Each: 24px diameter circle, no fill, stroke #3498DB (2px)
   - Labels: "IMU1", "IMU2", "IMU3", "IMU4" centered (12px bold, #2C3E50)
   - Sub-label: "MPU-6050" centered below each (10px, #2C3E50)
   - Connection points per IMU:
     * SCL: blue circle at left-middle of IMU (x-12, y)
     * SDA: green circle at right-middle of IMU (x+12, y)

5. LRA ACTUATORS (Three units, x=100-260, y=500-680):
   - Each: 30x20px rectangle, rounded corners (3px), no fill, stroke #E67E22 (2px)
   - Labels: "LRA1", "LRA2", "LRA3" centered vertically (12px bold, #2C3E50)
   - Sub-label: "Vibration Motor" centered below each (10px, #2C3E50)
   - Connection point: orange circle at left-middle of each actuator (x-15, y+10)

6. STATUS LED (x=160-200, y=80-120):
   - Yellow circle (#F1C40F, 16px diameter) with orange stroke (#E67E22, 2px)
   - Label: "LED" centered (6px bold, #2C3E50)
   - Connection point: red circle at bottom-center (x=180, y=120)

CONNECTIONS (ORTHOGONAL ROUTING WHERE POSSIBLE):

- I2C SCL (BLUE, #3498DB, 2.5px):
  * ESP32 GPIO22 (0,40) → TCA9548A SCL (0,50) via: 
    (0,40) → (50,40) → (50,50) → (400,50) [horizontal then vertical]
  * TCA9548A Ch0 SCL (140,30) → IMU1 SCL: 
    (140,30) → (240,30) [straight horizontal]
  * TCA9548A Ch1 SCL (140,50) → IMU2 SCL: 
    (140,50) → (340,50)
  * TCA9548A Ch2 SCL (140,70) → IMU3 SCL: 
    (140,70) → (440,70)
  * TCA9548A Ch3 SCL (140,90) → IMU4 SCL: 
    (140,90) → (540,90)

- I2C SDA (GREEN, #27AE60, 2.5px):
  * ESP32 GPIO21 (0,60) → TCA9548A SDA (0,70) via: 
    (0,60) → (50,60) → (50,70) → (400,70)
  * TCA9548A Ch0 SDA (140,40) → IMU1 SDA: 
    (140,40) → (240,40)
  * TCA9548A Ch1 SDA (140,80) → IMU2 SDA: 
    (140,80) → (340,80)
  * TCA9548A Ch2 SDA (140,120) → IMU3 SDA: 
    (140,120) → (440,120)
  * TCA9548A Ch3 SDA (140,160) → IMU4 SDA: 
    (140,160) → (540,160)

- PWM SIGNALS (ORANGE, #E67E22, 2px):
  * ESP32 GPIO18 (180,40) → LRA1: 
    (180,40) → (180,500) → (100,500) [vertical then horizontal]
  * ESP32 GPIO19 (180,60) → LRA2: 
    (180,60) → (180,560) → (100,560)
  * ESP32 GPIO20 (180,80) → LRA3: 
    (180,80) → (180,620) → (100,620)

- LED SIGNAL (PURPLE, #9B59B6, 2px):
  * ESP32 GPIO2 (0,120) → LED: 
    (0,120) → (180,120) [straight horizontal]

- POWER CONNECTIONS (RED, #E74C3C, 2px):
  * ESP32 3.3V (0,100) → Power rail: 
    (0,100) → (50,100) → (50,80) [horizontal then vertical to rail]

- GROUND CONNECTIONS (BLACK, #2C3E50, 2px):
  * ESP32 GND (0,80) → Ground rail: 
    (0,80) → (50,80) [horizontal]
  * Each LRA actuator right-middle (x+15, y+10) → Ground rail: 
    (x+15, y+10) → (x+15,720) → (50,720) [vertical then horizontal]
  * LED cathode (bottom of LED circle) → Ground rail: 
    (180,120) → (180,720) → (50,720)

LEGEND (Bottom Left, x=50, y=750):
   - ■ RED: Power (3.3V)
   - ■ BLACK: Ground
   - ■ BLUE: I2C Clock (SCL)
   - ■ GREEN: I2C Data (SDA)
   - ■ ORANGE: PWM Signals
   - ■ PURPLE: LED Signal
   Font: 14px, #2C3E50

SPECIFICATIONS TABLE (Bottom Right, x=600, y=750):
   [Three-column header with background #ECF0F1]
   Component | Type/Model | Quantity | Function | Connection Details
   Microcontroller | ESP32 Dev Board | 1 | Main processing | GPIO22=SCL, GPIO21=SDA, GPIO18/19/20=PWM Array, GPIO2=LED, GPIO25=LRA
   IMU Sensor | GY-521 (MPU-6050) | 4 | Motion detection | I2C via TCA9548A @ 0x70 (Channels 0-3)
   Actuator | Linear Resonant Actuator (LRA) | 3 | Haptic feedback | PWM @ 200Hz on GPIO18,19,20
   Indicator | LED | 1 | System status | GPIO2
   Multiplexer | TCA9548A | 1 | I2C bus expansion | Address 0x70, 4 channels used
   Font: 14px, #2C3E50; Table borders: 1px solid #BDC3C7

NOTES SECTION (Below Table, x=600, y=850):
   Configuration Notes:
   • Based on firmware configuration (common/config.py): 
     - Current: USE_LRA_ARRAY = False → Single LRA on GPIO25
     - Diagram shows 3-LRA array mode (requires USE_LRA_ARRAY = true)
   • I2C: GPIO22 (SCL), GPIO21 (SDA) @ 400kHz
   • PWM: GPIO18,19,20 @ 200Hz for LRA control
   • LED: GPIO2 for status indication
   • Sampling Rate: 100 Hz (128 samples = 1.28s window)
   
   Font: 13px, #2C3E50; Line height: 1.4

STYLE REQUIREMENTS:
- All text: Sans-serif (Arial, Helvetica, or similar)
- Connection lines: Straight or single 90-degree bends only
- No overlapping labels or wires
- Consistent padding: 20px minimum between components
- Drop shadow: Subtle (2px, 10% opacity black) on all components
- Overall dimensions: 1200x900px minimum
- Export format: SVG for scalability (or high-resolution PNG 300 DPI)

**KEY CHANGES MADE FROM ORIGINAL PROMPT:**
- Removed all "Anatomical Placement" sections and labels
- Removed suggested positioning text for IMUs (dorsal hand center, thenar eminence, etc.)
- Removed suggested positioning text for LRAs (dorsal hand, palmar-thenar, palmar-hypothenar)
- Kept all connection details, pin labels, component labels, legends, and specifications
- Preserved configuration notes about firmware settings (but removed placement suggestions)
- Maintained all technical connection information for accurate wiring diagram generation

This revised prompt will generate a wiring diagram that shows ONLY:
- Electrical connections between components
- Component labels (IMU1, LRA1, ESP32, etc.)
- Pin labels and functions (GPIO22=SCL, etc.)
- Power/ground rails
- Legend explaining connection types
- Specifications table with technical details
- Configuration notes about firmware settings

Without any anatomical placement descriptions or positioning suggestions.