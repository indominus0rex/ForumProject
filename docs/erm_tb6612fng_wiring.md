# ERM Motor + TB6612FNG Wiring Instructions

## Overview
This document provides detailed instructions for wiring an Eccentric Rotating Mass (ERM) vibration motor to the ESP32 via a TB6612FNG dual H-bridge motor driver. The TB6612FNG provides clean motor power amplification with built-in flyback protection, replacing the previous LRA + MOSFET approach.

## Key Differences from LRA
- **ERM (Eccentric Rotating Mass)**: Simple DC brushed motor with offset mass. No resonant frequency — just apply voltage and it spins. Slower start/stop than LRA.
- **TB6612FNG**: Dual H-bridge motor driver. Handles motor current (up to 1.2A peak per channel), provides built-in flyback protection (no external diode needed), and offers PWM speed control via PWMA pin.

## TB6612FNG Pinout
| Pin | Function | Connection |
|-----|----------|------------|
| VMOT | Motor power supply (2.5V-5.5V) | ERM power source — NOT from ESP32 GPIO |
| VCC | Logic power (2.7V-5.5V) | ESP32 3V3 or separate logic supply |
| GND | Ground | Common with ESP32 GND |
| STBY | Standby (HIGH=enable, LOW=disable) | ESP32 GPIO (pulled HIGH to enable) |
| AIN1 | Direction input A | ESP32 GPIO |
| AIN2 | Direction input A | ESP32 GPIO |
| PWMA | PWM speed control A | ESP32 GPIO (PWM object) |
| BIN1/BIN2/PWMB | Channel B | Unused for single-ERM build |

## Materials Required
- ERM vibration motor (coin type, typically 10mm diameter × 3mm, 1.5V-3V rated)
- TB6612FNG dual H-bridge breakout board
- 30AWG silicone-insulated stranded wire (2-core recommended)
- Wire strippers/cutters
- Soldering iron and solder
- Heat-shrink tubing (various sizes)
- Multimeter
- Optional: micro-JST PH 2-pin connectors for detachable wiring

## Wiring Diagram

```
ESP32                 TB6612FNG              ERM Motor
───                   ───                    ───
3V3   ────────────── VCC
GND   ────────────── GND ───────────────── GND (motor side)
GPIO25 ───────────── AIN1 (direction)
GPIO26 ───────────── AIN2 (direction)
GPIO27 ───── PWM ── PWMA (speed)
GPIO28 ───────────── STBY (enable)
                      VMOT ───┬─── 3V-5V supply
                              │  (NOT from ESP32)
                         [ERM motor]
                         + ── VMOT
                         - ── GND (common with ESP32)
```

## Connection Steps

### Step 1: Prepare TB6612FNG Breakout
1. Identify TB6612FNG breakout pins (refer to your breakout board's pinout).
2. Ensure VMOT and VCC are NOT shorted — they are separate supplies.

### Step 2: Wire Logic Pins to ESP32
1. **VCC** → ESP32 3V3 (logic power for TB6612FNG)
2. **GND** → ESP32 GND (common ground — MUST be shared with VMOT ground)
3. **STBY** → ESP32 GPIO28 (pulled HIGH to enable driver)
4. **AIN1** → ESP32 GPIO25 (direction control)
5. **AIN2** → ESP32 GPIO26 (direction control)
6. **PWMA** → ESP32 GPIO27 (PWM speed control)

### Step 3: Wire Motor Power (VMOT)
1. **VMOT** → ERM motor positive (+) terminal
   - Use separate 3V-5V supply (battery, boost regulator, or bench supply)
   - Do NOT power VMOT from ESP32 GPIO — motors draw too much current
2. **ERM motor negative (-)** → Common GND (same as ESP32 GND and TB6612FNG GND)

### Step 4: Direction Configuration (for ERM)
ERM motors are unidirectional for vibration — only one direction is used.
- **AIN1 = HIGH** (GPIO25 → 1)
- **AIN2 = LOW** (GPIO26 → 0)
- This sets the H-bridge to drive the motor in one direction.

To reverse direction (if needed): AIN1=LOW, AIN2=HIGH.

### Step 5: PWM Speed Control
- **PWMA** receives PWM from ESP32 GPIO27.
- PWM frequency: 1kHz typical for ERM (no resonant frequency to match).
- Duty cycle 0-1023: 0 = motor off, 1023 = full speed.
- Vibration intensity scales with duty cycle.

### Step 6: Enable Driver
- **STBY** must be HIGH for the driver to be active.
- When STBY is LOW, the driver is in standby (all outputs disabled, motor off).
- In firmware: set STBY HIGH at startup, keep it HIGH during operation.

## Firmware Configuration

In `firmware/common/config.py`:
```python
# TB6612FNG pin assignments
TB6612FNG_PIN_AIN1 = 25
TB6612FNG_PIN_AIN2 = 26
TB6612FNG_PIN_PWMA = 27
TB6612FNG_PIN_STBY = 28

# ERM motor supply voltage (adjust to your ERM spec)
ERM_VMOT_VOLTS = 3.0  # typical for coin ERM motors
```

In `firmware/stages/haptic.py`:
- Motor control via `_set_motor(tb6612, duty)` — sets PWMA duty cycle
- `_motor_off(tb6612)` — sets duty to 0
- Duty values: 0 = off, 512 = ~50% (moderate vibration), 1023 = full speed

## Assembly Notes

### Strain Relief
1. Create 3mm strain-relief loop at ERM pocket entry.
2. Secure loop with stitches or flexible epoxy.
3. Route wires along strap interior every 15mm.
4. Create second strain-relief loop at strap exit toward ESP32.

### Heat Management
- TB6612FNG gets warm under load — ensure some airflow.
- For continuous duty >50%, consider a small heatsink on TB6612FNG.
- Monitor MOSFET/bridge temperature during initial testing.

### Power Supply
- ERM current draw: typically 50-150mA for coin motors at rated voltage.
- TB6612FNG can handle up to 1.2A peak per channel — plenty for ERM.
- Ensure VMOT supply can deliver enough current for your ERM.
- Common GND between ESP32, TB6612FNG, and VMOT supply is critical.

## Validation

### Continuity Check
1. AIN1 ↔ ESP32 GPIO25: <1Ω
2. AIN2 ↔ ESP32 GPIO26: <1Ω
3. PWMA ↔ ESP32 GPIO27: <1Ω
4. STBY ↔ ESP32 GPIO28: <1Ω
5. VCC ↔ ESP32 3V3: <1Ω
6. GND ↔ ESP32 GND: <1Ω
7. No shorts between adjacent signal wires.

### Functional Test (Thonny)
```python
from machine import Pin, PWM
import time

# Setup (match config.py pins)
ain1 = Pin(25, Pin.OUT)
ain2 = Pin(26, Pin.OUT)
pwma = PWM(Pin(27), freq=1000, duty=0)
stby = Pin(28, Pin.OUT)

# Enable driver
stby.value(1)
ain1.value(1)  # direction
ain2.value(0)

# Test vibration
pwma.duty(512)   # 50% duty — should vibrate
time.sleep_ms(500)
pwma.duty(0)     # off
time.sleep_ms(200)
pwma.duty(1023)  # full speed
time.sleep_ms(500)
pwma.duty(0)     # off

# Disable driver
stby.value(0)
```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| No vibration | STBY low, wrong direction, no VMOT power | Check STBY=HIGH, AIN1/AIN2, VMOT connected |
| Motor spins but no vibration | Wrong motor terminals | Swap ERM wires (polarity matters for vibration feel) |
| ESP32 resets | Brownout from VMOT supply sag | Add bulk cap on VMOT, use stronger supply |
| TB6612FNG hot | High duty cycle sustained | Reduce duty, add heatsink, check VMOT voltage |
| Intermittent vibration | Loose connection | Check solder joints, strain relief |

## Integration with Firmware

The haptic stage (`firmware/stages/haptic.py`) controls the TB6612FNG based on tremor classification:
- **rest/baseline**: Motor OFF (duty=0), LED off
- **postural**: Motor OFF, LED blinks 1Hz
- **kinetic**: Motor pulses 2Hz (50% duty on/off), LED on
- **grasp_guidance/other**: Motor steady ~50% duty, LED on

The actuation stage (`firmware/stages/actuate.py`) can also drive the motor via `suppress_duty` when the PLL-based suppression pipeline is active.
