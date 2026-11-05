# Wiring Diagram Design for ESP32-based Wearable Tremor Sensor

## Functional Blocks

1. **Power Management**
   - Components: Battery (LiPo, 3.7V), MT3608 Boost Converter (3.7V→5V), ESP32-DevKitC 38-pin (onboard AMS1117-3.3 for 3.3V), Power distribution rails (3.3V and GND)
   - Connections: 
     - Battery + → MT3608 IN+
     - Battery - → MT3608 IN- and system GND
     - MT3608 OUT+ → ESP32 VIN pin (5V)
     - MT3608 OUT- → system GND
     - ESP32 3.3V (from onboard AMS1117) → 3.3V rail
     - 3.3V rail → ESP32 VCC, TCA9548A VCC, IMUs VCC, LRA (via driver if needed), LED anode (via resistor)
     - GND rail → ESP32 GND, TCA9548A GND, IMUs GND, LRA cathode, LED cathode

2. **Microcontroller (ESP32)**
   - Component: ESP32-DevKitC 38-pin (ESP32-WROOM-32 module on dev board)
   - Key Pins:
     - GPIO2: LED output (active high)
     - GPIO21: I2C SDA
     - GPIO22: I2C SCL
     - GPIO25: Main LRA PWM output
     - GPIO18,19,20: Optional LRA array PWM outputs (for proximial, middle, distal LRAs if used)
     - VIN: 5V power input (from MT3608 boost)
     - GND: Ground

3. **Sensing Block (IMUs via Multiplexer) — LOCKED 2026-08-27 Option A + ET: thumb+index phalanx, LRAs deferred**
   - Components:
     - TCA9548A I2C Multiplexer (1-to-8) @0x70 (A0/A1/A2→GND)
     - 4× MPU-6050 GY-521 @0x68 each, isolated per channel (scalable 1→4, validate incrementally)
     - Channel map per `pin_assignments.md:48` + `cad/connections_4imu.csv:10` + `knowledge.md:5a`: CH0=dorsal wrist proximal (primary, Keba 2025 rubber band 100Hz), CH1=thenar volar, CH2=thumb proximal phalanx dorsal-radial 20° tilt (pill-rolling 4–6Hz, was CMC), CH3=index proximal phalanx dorsal (ET postural 6–8Hz, thumb-index coherence 0.6 balanced)
   - Connections:
     - TCA9548A:
       - VCC → 3.3V rail (with 0.1µF decoupling at mux)
       - GND → system GND (star)
       - SCL → ESP32 GPIO22 (I2C SCL @400kHz)
       - SDA → ESP32 GPIO21 (I2C SDA)
       - A0, A1, A2 → GND (to set I2C address 0x70 per `pin_assignments.md:45`)
       - EN → 3.3V rail (enabled)
       - CH0→IMU0 (dorsal wrist), CH1→IMU1 (thenar), CH2→IMU2 (thumb phalanx 20° pill), CH3→IMU3 (index phalanx ET) — each channel's SCL/SDA routed to corresponding IMU; CH4-7 NC (forearm optional CH4 if re-added)
         - Wire colors for diagram: CH0 blue, CH1 green, CH2 yellow (thumb phalanx pill), CH3 orange (index phalanx ET) per `cad/connections_4imu.csv:10` — coherence 0.6 thresholds in `firmware/common/config.py:64`
       - Selection in firmware: `i2c.writeto(0x70, bytes([1<<ch]))` then `readfrom_mem(0x68, 0x3B, 6)` as in `firmware/raw_data_collection.py:48` and web tutorial `https://randomnerdtutorials.com/tca9548a-i2c-multiplexer-esp32-esp8266-arduino/`
     - Each MPU-6050:
       - VCC → 3.3V rail + 0.1µF ceramic decoupling at IMU, 10-100µF bulk on 3.3V bus
       - GND → system GND (star per IMU, not daisy chain)
       - SCL → TCA9548A channel SCL (channel-specific color)
       - SDA → TCA9548A channel SDA
       - AD0 → GND (so 0x68 on each channel)
       - INT (optional) → not connected or to ESP32 GPIO for interrupt (not used in current firmware; selection via mux makes INT less useful)

4. **Actuation Block (LRA Vibration Motors) — DEFERRED FOR CURRENT 4-IMU BUILD (2026-08-27)**
   - Components: **None populated for this build** — GPIOs 25/18/19/20 left NC as grey pads per `cad/connections_4imu.csv:29` and `pin_assignments.md:55`. HSP `haptic` stage no-ops with duty 0. For reference only:
     - Linear Resonant Actuator (LRA) - main vibration motor (future)
     - Optional: Additional LRAs for array configuration (proximal, middle, distal)
     - Note: LRAs typically require a driver circuit (like DRV2605) for optimal performance, but for simplicity we assume direct PWM drive with low-side MOSFET + flyback diode in practice
   - Connections (intentionally NC this build):
     - Main LRA (future): One terminal → ESP32 GPIO25 (PWM 200Hz, 50% duty), Other terminal → GND via low-side MOSFET+1N4148 (see legacy `cad/connections.csv:14`)
     - Optional LRAs (future if USE_LRA_ARRAY): Proximal→GPIO18, Middle→GPIO19, Distal→GPIO20, each other terminal → GND via MOSFET
   - Diagram instruction: **Show grey NC pads at GPIO25/18/19/20 with label "DEFERRED — no LRA this build"**; do NOT draw LRAs in the hand illustration for the 4-IMU harness (`wiring_diagram_prompt_4imu_no_lra.txt:1`).

5. **Indication Block**
   - Components: Status LED (with current-limiting resistor)
   - Connections:
     - Anode → ESP32 GPIO2 (via 220-470Ω resistor)
     - Cathode → GND

6. **I2C Communication Bus**
   - Signals: SCL (GPIO22), SDA (GPIO21)
   - Pull-up Resistors: 4.7kΩ on SCL and SDA lines to 3.3V (external, not configured in firmware)
   - Devices: ESP32 (master), TCA9548A (slave), MPU-6050s (slaves via multiplexer channels)

## Layout Strategy

To minimize wire crossings and ensure clarity, the wiring diagram follows a **left-to-right, top-to-bottom functional flow**:

1. **Left Side (Power Input)**: 
   - Battery and voltage regulator block placed at far left
   - Power rails (3.3V and GND) run horizontally as buses across the diagram

2. **Center Left (Microcontroller)**:
   - ESP32 placed slightly right of power block
   - Power pins (VCC, GND) connected to buses
   - I2C pins (SCL, SDA) routed to the right toward sensing block
   - PWM pins (GPIO25, 18,19,20) routed downward to actuation block
   - GPIO2 (LED) routed upward to indication block

3. **Center (Sensing Block)**:
   - TCA9548A multiplexer placed center-right of ESP32
   - I2C bus (SCL, SDA) connected from ESP32 to multiplexer
   - Multiplexer channels routed to the right to respective IMUs
   - IMUs arranged vertically: IMU0 (proximial) top, IMU1 (middle) center, IMU2 (distal) bottom
   - Unused channels (CH3-CH7) left unconnected or noted as reserved

4. **Center Right (Actuation Block)**:
   - LRA components placed below the sensing block
   - Main LRA connected to GPIO25
   - Optional LRAs connected to GPIOs 18,19,20 (if array enabled)
   - All LRA bottom terminals connected to GND bus

5. **Top Right (Indication Block)**:
   - Status LED placed above the sensing block
   - Connected to GPIO2 and GND bus

6. **Anatomical Locations (for reference in wiring) — 2026-08-27 Option A + ET LOCKED**:
   - IMU0 (Dorsal wrist, just proximal to joint, dorsal): ch0, primary Keba 2025 rubber band, rest baseline
   - IMU1 (Thenar eminence, volar thumb base): ch1, thumb opposition
   - IMU2 (Thumb proximal phalanx, dorsal-radial 20° tilt): ch2, **was CMC, now phalanx for pill-rolling 4–6Hz** (thumb-index coherence >0.6) — see `docs/component_positions.txt:13` fallback, 20° aligns X to flexion
   - IMU3 (Index proximal phalanx, dorsal): ch3, **was forearm, now index for ET postural 6–8Hz** (finger-wrist coherence >0.6 balanced, per `firmware/common/config.py:64`)
   - LRA: **None this build — see actuation block above**; future LRA when procured → dorsum MC2-3 distal to IMU0 per `docs/imu_lra_placement.txt:20`
   - ESP32 and Battery: Mounted on forearm band or wristband enclosure to minimize movement artifacts
   - Wiring Considerations: Flexible 30AWG silicone, 0.1µF at each IMU + 10-100µF bulk on 3.3V, twisted pair for SDA/SCL >10cm to avoid WiFi glitch per zbotic tutorial; 3mm strain loops at pockets; stitch every 15mm along low-bend dorsal side to avoid grip interference

## Wire Crossing Minimization Techniques

- **Bus Routing**: Power and ground buses run as continuous horizontal lines, with vertical drops to components
- **Signal Separation**: 
  - I2C signals kept together and routed away from high-current PWM lines
  - PWM lines grouped when possible (for LRA array)
  - LED signal isolated on its own path
- **Component Placement**: 
  - Group related components (e.g., all sensing elements on right side)
  - Place multiplexer close to ESP32 to shorten I2C lines
  - Arrange IMUs in vertical column matching anatomical order to prevent crossing when routed from multiplexer
- **Layering Concept**: 
  - Imagine power buses on bottom layer, signals on middle layer, anatomical placements on top layer (for documentation purposes)

## Notes

- All resistors (I2C pull-ups 4.7kΩ if needed, LED 220Ω) should be placed close to the components they serve; GY-521 already has pullups on-board so external only if using long wires or missing breakout.
- Decoupling capacitors (0.1µF per IMU + at TCA9548A, 10-100µF bulk on 3.3V rail) required near VCC/GND per `assembly_checklist.md:43` and `cad/connections_4imu.csv:6` — show near rails in diagram. Short wires <15cm to avoid ESP32 WiFi I2C glitches per Zbotic.
- For future LRA implementation (deferred), consider dedicated DRV2605 driver for better performance and current handling — not shown in 4-IMU harness (`wiring_diagram_prompt_4imu_no_lra.txt:1` negative prompt).
- The diagram assumes 3.3V logic levels throughout; level shifting not required for these components at 3.3V.
- Reference for image generation: `wiring_diagram_prompt_4imu_no_lra.txt:1` (master, now Option A thumb+index phalanx) + `wiring_diagram_prompt_4imu_minimalist.txt:1` (short box+inset, now pill+ET) vs `wiring_diagram_prompt_detailed.txt:1` (legacy 3-LRA hand). Prompt negative includes "no LRA".
- Inset spec 2026-08-27 Option A+ET visible-volar: Main 85% remains pure orthogonal boxes (`X15 power → X30 ESP32 → X50 TCA → X75 IMUs Y25/45/65/85`) with no hand anatomy; inset 12% top-right dashed border `solid dorsal grey + dashed translucent volar ghost rgba(200,230,200,0.15)` with 4 dots color-matched (DOT1 green thenar on ghost, DOT2 yellow thumb phalanx pill 4–6Hz, DOT3 orange index phalanx ET 6–8Hz, coherence 0.6) — wires never inside inset.

---

*Updated 2026-08-27 Option A + ET — thumb phalanx + index phalanx (replaces CMC+forearm), balance 0.6, colors per channel.*

---

*Updated 2026-08-27 — 4-IMU thumb CMC lock, LRAs deferred, colors per channel in legend.*