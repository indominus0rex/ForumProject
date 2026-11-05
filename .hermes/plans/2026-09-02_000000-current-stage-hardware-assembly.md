# Plan — Current Stage: Hardware Assembly (No LRAs) + PLL Firmware Integration

## Goal
Assemble all hardware (4 IMUs + TCA9548A + ESP32, no LRAs), flash the PLL firmware, and verify end-to-end tremor phase tracking on the bench.

## Current Context

**Hardware being assembled:**
- ESP32 + 4x GY521 IMUs via TCA9548A I2C mux
- NO LRAs (GPIO25/18/19/20 unpopulated)
- Status LED on GPIO2

**Firmware status:**
- PLL-based suppression implemented (8 new files, all tests passing)
- Pipeline: `safety → sensor → stationarity → quality → suppress → haptic → audit`
- Suppress stage outputs `suppress_duty` but haptic stage no-ops without LRAs

**What we need to verify:**
1. Hardware assembles and powers correctly
2. All 4 IMUs readable via mux
3. PLL locks onto tremor in real-time
4. Suppress output drives (LED or scope) without LRAs

---

## Step-by-Step Tasks

### Task 1: Power the ESP32 and verify boot
**Time**: 2 min

1. Connect ESP32 via USB
2. Open Thonny → select MicroPython ESP32 interpreter
3. Verify REPL prompt appears:
   ```python
   >>> print("boot ok")
   boot ok
   ```
4. Verify GPIO2 LED blinks (if LED test file flashed)

**Expected**: REPL responsive, LED on GPIO2 can be toggled.

---

### Task 2: Flash common files to ESP32
**Time**: 5 min

Copy these files to ESP32 (in order):
```
firmware/common/gy521.py
firmware/common/tca9548a.py
firmware/common/bandpass.py
firmware/common/pll.py
firmware/common/predictor.py
firmware/common/anticancel.py
firmware/common/adaptive_gain.py
firmware/common/config.py
```

**Verify in Thonny REPL:**
```python
from common.config import PLL_BANDWIDTH_HZ, SAMPLE_RATE_HZ
print("Config OK:", PLL_BANDWIDTH_HZ, SAMPLE_RATE_HZ)
```

**Expected**: `Config OK: 1.0 500.0` (or current values)

---

### Task 3: Flash stage files to ESP32
**Time**: 5 min

Copy these files:
```
firmware/stages/__init__.py
firmware/stages/safety.py
firmware/stages/sensor.py
firmware/stages/stationarity.py
firmware/stages/quality.py
firmware/stages/suppress.py
firmware/stages/haptic.py
firmware/stages/audit.py
```

**Verify in Thonny REPL:**
```python
from stages import STAGE_ORDER
print("Stages:", STAGE_ORDER)
```

**Expected**: `Stages: ['safety', 'sensor', 'stationarity', 'quality', 'suppress', 'haptic', 'audit']`

---

### Task 4: Flash main entry point
**Time**: 2 min

Copy `firmware/embedded_main_hsp.py` to ESP32 as `main.py`

**Verify**: ESP32 auto-runs, no import errors in REPL.

---

### Task 5: Verify I2C bus and mux detection
**Time**: 3 min

In Thonny REPL:
```python
from machine import I2C, Pin
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
scan = i2c.scan()
print("I2C devices:", [hex(a) for a in scan])
print("TCA9548A at 0x70:", 0x70 in scan)
```

**Expected**: `TCA9548A at 0x70: True`

---

### Task 6: Verify all 4 IMUs readable via mux
**Time**: 3 min

```python
from common.tca9548a import TCA9548A
from common.gy521 import GY521
from common.config import IMU_CHANNELS

mux = TCA9548A(i2c, addr=0x70)
for ch in IMU_CHANNELS:
    mux.select_channel(ch)
    imu = GY521(i2c)
    x, y, z = imu.read_3axis()
    print(f"CH{ch}: x={x:.3f} y={y:.3f} z={z:.3f}")
```

**Expected**: All 4 channels return valid readings (z ≈ 1.0 when flat)

---

### Task 7: Verify PLL locks on synthetic tremor
**Time**: 5 min

```python
import math
from common.pll import PLL
from common.bandpass import BandpassFilter

fs = 100.0
pll = PLL(fs=fs, center_freq=6.0, bandwidth=1.0)
bp = BandpassFilter(fs=fs, low_hz=3.0, high_hz=12.0)

# Generate 6 Hz synthetic tremor for 3 seconds
for i in range(int(3 * fs)):
    t = i / fs
    signal = math.sin(2 * math.pi * 6.0 * t)
    filtered = bp.process_sample(signal)
    phase, freq, _ = pll.update(filtered)

print(f"PLL freq: {freq:.2f} Hz (target: 6.0)")
print(f"PLL locked: {pll.locked}")
print(f"PLL phase: {pll.phase:.3f} rad")
```

**Expected**: freq ≈ 5.8-6.2 Hz, locked = True

---

### Task 8: Verify suppress stage outputs duty cycle
**Time**: 5 min

```python
import math
from stages.suppress import SuppressStage

fs = 100.0
stage = SuppressStage(fs=fs, pll_bandwidth=1.0, initial_gain=0.5)

# Feed synthetic tremor
for i in range(300):
    t = i / fs
    x = 0.1 * math.sin(2 * math.pi * 6.0 * t)
    y = 0.05 * math.sin(2 * math.pi * 6.0 * t)
    z = 1.0 + 0.15 * math.sin(2 * math.pi * 6.0 * t)
    frame = {'x': x, 'y': y, 'z': z, 'quality_ok': True, 'safe': True}
    frame = stage.process(frame)

status = stage.get_status()
print(f"Suppress duty: {frame['suppress_duty']}")
print(f"PLL freq: {status['pll_freq']:.2f} Hz")
print(f"PLL locked: {status['pll_locked']}")
print(f"Adaptive gain: {status['adaptive_gain']:.3f}")
```

**Expected**: duty varies 0-1000+, PLL locked, gain adapts

---

### Task 9: Verify suppress output on GPIO2 (LED substitute)
**Time**: 3 min

Since no LRAs, use GPIO2 LED to visualize suppression intensity:

```python
from machine import Pin, PWM
from stages.suppress import SuppressStage
import math, time

led = Pin(2, Pin.OUT)
# Use PWM on GPIO2 for intensity visualization
led_pwm = PWM(Pin(2), freq=1000, duty=0)

fs = 100.0
stage = SuppressStage(fs=fs, pll_bandwidth=1.0, initial_gain=0.5)

# Run for 10 seconds, LED brightness = suppression intensity
for i in range(int(10 * fs)):
    t = i / fs
    x = 0.1 * math.sin(2 * math.pi * 6.0 * t)
    y = 0.05 * math.sin(2 * math.pi * 6.0 * t)
    z = 1.0 + 0.15 * math.sin(2 * math.pi * 6.0 * t)
    frame = {'x': x, 'y': y, 'z': z, 'quality_ok': True, 'safe': True}
    frame = stage.process(frame)
    duty = frame['suppress_duty']
    led_pwm.duty(duty)
    time.sleep(1/fs)

led_pwm.duty(0)
```

**Expected**: LED brightness oscillates at 6 Hz (visible flicker), confirming anti-phase output.

---

### Task 10: Full pipeline integration test on hardware
**Time**: 5 min

```python
# Run the actual firmware main loop for 30 seconds
# Monitor PLL state via frame dict

from embedded_main_hsp import stages, pll_stage
import time

# Manually step the pipeline with real IMU data
from common.tca9548a import TCA9548A
from common.gy521 import GY521
from common.config import IMU_CHANNELS

mux = TCA9548A(i2c, addr=0x70)
sensor = GY521(i2c)  # primary ch0

# Run 5 second capture
for i in range(500):
    mux.select_channel(0)
    x, y, z = sensor.read_3axis()
    
    frame = {'x': x, 'y': y, 'z': z, 'quality_ok': True, 'safe': True}
    frame = stages['suppress'].process(frame)
    
    if i % 100 == 0:
        print(f"duty={frame['suppress_duty']}, freq={frame['pll_freq']:.2f}, locked={frame['pll_locked']}")

print("Pipeline integration test passed!")
```

**Expected**: PLL locks onto real IMU noise/movement, duty varies accordingly.

---

## Future Steps (After This Stage)

### A. Add LRA hardware
- Wire 3 LRAs via MOSFET drivers on GPIO25/18/19/20
- Set `USE_LRA_ARRAY = True` in config
- Re-run Task 9 with actual LRA output

### B. Collect real tremor data
- Record from PD/ET patients with actuator OFF
- Tune PLL bandwidth for real tremor characteristics
- Measure cancellation efficacy

### C. Tune PLL parameters
| Parameter | Start | Range | Effect |
|-----------|-------|-------|--------|
| `PLL_BANDWIDTH_HZ` | 0.5 | 0.3-2.0 | Lower=stable, higher=fast |
| `PREDICTION_MS` | 12.0 | 8-20 | Match LRA delay |
| `ADAPTIVE_GAIN_MAX` | 1.5 | 0.5-3.0 | Max stimulation |
| `SAMPLE_RATE_HZ` | 500 | 100-1000 | Phase resolution |

### D. Stage 2: FES (future)
- Add stimulus generator + electrodes
- Replace LRA with anti-phase current pulses
- Requires safety isolation + current limiting

---

## Risks & Open Questions

1. **I2C reliability at 400kHz with 4 IMUs**: May need to reduce to 100kHz or add pull-ups
2. **PLL lock time on real tremor**: Real tremor is noisier than synthetic. May need wider bandwidth.
3. **No LRA = no suppression verification**: LED shows output but can't verify cancellation without actuator
4. **Power consumption at 500Hz**: Battery life may be 2-4 hours. Reduce to 100Hz if needed.
5. **Soft tissue motion artifacts**: Real hand movement creates non-tremor signals. Bandpass helps but not perfect.

---

## Quick Pass/Fail

| Check | Pass Criteria |
|-------|---------------|
| ☐ ESP32 boots | REPL responsive |
| ☐ I2C scan | 0x70 detected |
| ☐ 4 IMUs readable | All return valid (x,y,z) |
| ☐ PLL locks on synthetic | freq ≈ 6 Hz, locked=True |
| ☐ Suppress outputs duty | duty varies 0-1000+ |
| ☐ LED visualizes output | Visible flicker/brightness change |
| ☐ Real IMU → PLL lock | Locks on actual hand movement |

---

*Plan for current stage: hardware assembly without LRAs + PLL firmware integration.*
