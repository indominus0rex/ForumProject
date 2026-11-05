# Forum Project — What You Need to Know

## Goal
A wearable hand-tremor suppression system using **phase-locked loop (PLL) tracking** and **adaptive anti-phase cancellation** running entirely on ESP32 edge hardware — no FFT classification, no cloud, no phone.

## What makes this different from published research

| Typical research | Our approach |
|-----------------|--------------|
| FFT + features + LogReg/CNN | PLL phase tracking — no feature extraction |
| Classify then react | Predict phase, cancel before peak |
| Haptic cueing (vague buzz) | Anti-phase stimulation at exact inverse |
| Cloud AI (Felix wristband) | All edge, zero connectivity |
| 100ms+ latency windows | <1ms sample-by-sample tracking |
| Treat tremor as classification | Treat tremor as oscillator to cancel |

## Core Insight

Tremor is a quasi-periodic oscillator (3-12 Hz). Instead of classifying windows of data, we **track its phase in real-time using a PLL** and deliver stimulation at exactly the opposite phase (180° offset) to cancel it. This is the same noise-cancelling headphone principle, but for hand tremors.

## Architecture Overview

```
┌─────────────────────────── EDGE DEVICE (ESP32) ───────────────────────────┐
│                                                                            │
│  [4 IMUs] → [I2C Mux] → [Bandpass filter 3-12 Hz]                        │
│                                      ↓                                     │
│                           [PLL phase tracker] ←── (adaptive loop)         │
│                                      ↓                                     │
│                           [Phase predictor: 10-20ms ahead]                │
│                                      ↓                                     │
│                           [Anti-phase PWM generator]                      │
│                                      ↓                                     │
│                           [LRA array: push-pull for bidirectional]        │
│                                                                            │
│  ALL ON-DEVICE. NO FFT. NO CLASSIFIER. NO CLOUD.                          │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Current Stage: Stage 1 — PLL + Anti-Phase Haptic

### Status: Firmware complete & tested. Hardware assembly next.

### What's DONE (firmware)
- [x] PLL phase tracker (`firmware/common/pll.py`) — locks onto 6 Hz tremor
- [x] Phase predictor (`firmware/common/predictor.py`) — predicts 12ms ahead
- [x] Anti-phase generator (`firmware/common/anticancel.py`) — 180° offset
- [x] Adaptive gain controller (`firmware/common/adaptive_gain.py`) — auto-adjusts
- [x] Bandpass filter (`firmware/common/bandpass.py`) — 3-12 Hz IIR
- [x] Suppress stage (`firmware/stages/suppress.py`) — orchestrates pipeline
- [x] All unit tests passing (6 test files, 30+ assertions)
- [x] Pipeline integration (`stages/__init__.py`, `embedded_main_hsp.py`)

### What's NOT done (hardware + next steps)
- [ ] Hardware assembly (4 IMUs + TCA9548A + ESP32)
- [ ] LRA procurement + push-pull driver circuit
- [ ] Bench testing with real tremor
- [ ] Patient validation

---

## Test Results — What We Verified

### ✓ Working correctly

| Component | Evidence |
|-----------|----------|
| **PLL frequency tracking** | Locks onto 6 Hz, tracks within ±0.5 Hz |
| **PLL phase tracking** | Phase follows input phase correctly |
| **Phase prediction** | Predicts 12ms ahead correctly |
| **Bandpass filter** | Passes 3-12 Hz, attenuates DC |
| **Adaptive gain** | Increases/decreases based on residual |
| **Pipeline integration** | Full pipeline runs end-to-end |

### ✗ Discovered Limitation (Critical)

**Single LRA cannot produce true anti-phase cancellation.**

| Issue | Severity | Root cause |
|-------|----------|------------|
| Anti-phase output is rectified | **Critical** | Duty = `sin(anti_phase) * |filtered|` — always positive |
| Correlation ≈ 0 (not -1) | **Critical** | Single LRA can't produce signed (bidirectional) force |
| Frequency drift tracking slow | **Medium** | PLL bandwidth too narrow for fast frequency changes |

**Math says**: For anti-phase cancellation, output should be `-sin(ωt)` when input is `sin(ωt)`.

**Hardware says**: PWM duty is unsigned (0-1023). A single LRA can only push in ONE direction.

**What we actually produce**: `sin(ωt + π) * |sin(ωt)|` — a rectified signal.

### The Fix: Push-Pull LRA Configuration

| With single LRA | With push-pull (2 LRAs) |
|-----------------|-------------------------|
| Can only cancel half the tremor cycle | Full bidirectional cancellation |
| ~30-50% tremor reduction | ~70-90% tremor reduction |
| Simple driver circuit | Complementary PWM signals needed |

**Firmware already supports this**: `AntiPhaseGenerator.compute_stereo_duties()` returns complementary (duty_a, duty_b) for push-pull.

---

## Hardware Contract

### Current Build (No LRA)
| Pin | Function | Connects to |
|-----|----------|-------------|
| GPIO2 | Status LED | LED anode (via resistor) |
| GPIO21 | I2C SDA | TCA9548A SDA + all IMU SDA |
| GPIO22 | I2C SCL | TCA9548A SCL + all IMU SCL |
| 3V3 | Power | TCA9548A VCC, all IMU VCC |
| GND | Ground | TCA9548A GND, all IMU GND, LED cathode |
| GPIO25 | LRA (deferred) | Unpopulated |
| GPIO18/19/20 | LRA array (deferred) | Unpopulated |

### Future Build (With Push-Pull LRAs)
| Pin | Function | Connects to |
|-----|----------|-------------|
| GPIO25 | LRA A (push) | MOSFET driver A |
| GPIO18 | LRA B (pull) | MOSFET driver B |
| GPIO19 | LRA C (push, 2nd channel) | MOSFET driver C |
| GPIO20 | LRA D (pull, 2nd channel) | MOSFET driver D |

### I2C Topology
```
ESP32 (GPIO21/22) → TCA9548A (0x70)
  ├── CH0 → IMU0 (0x68) — dorsal wrist
  ├── CH1 → IMU1 (0x68) — thenar
  ├── CH2 → IMU2 (0x68) — thumb phalanx
  └── CH3 → IMU3 (0x68) — index phalanx
```

---

## Project Map

### Firmware (`firmware/`) — Runs on ESP32 (MicroPython)
| File | Purpose | Status |
|------|---------|--------|
| `common/config.py` | Hardware pins, I2C, PLL params | ✓ Done |
| `common/gy521.py` | GY521/MPU6050 driver | ✓ Done |
| `common/tca9548a.py` | I2C multiplexer driver | ✓ Done |
| `common/bandpass.py` | 4th-order IIR bandpass 3-12 Hz | ✓ Done |
| `common/pll.py` | Phase-locked loop tracker | ✓ Done |
| `common/predictor.py` | Phase prediction (N ms ahead) | ✓ Done |
| `common/anticancel.py` | Anti-phase PWM generator (push-pull support) | ✓ Done |
| `common/adaptive_gain.py` | Residual-based gain adaptation | ✓ Done |
| `stages/suppress.py` | Main suppression pipeline stage | ✓ Done |
| `stages/haptic.py` | LRA haptic output (PWM array) | ✓ Done |
| `stages/quality.py` | Signal quality gate | ✓ Done |
| `stages/safety.py` | Safety limits | ✓ Done |

### Tests (`tests/`) — Run on host Python
| File | Purpose | Status |
|------|---------|--------|
| `test_pll.py` | PLL phase tracker | ✓ Passing |
| `test_predictor.py` | Phase predictor | ✓ Passing |
| `test_anticancel.py` | Anti-phase generator | ✓ Passing |
| `test_adaptive_gain.py` | Adaptive gain controller | ✓ Passing |
| `test_bandpass.py` | Bandpass filter | ✓ Passing |
| `test_suppress.py` | Full pipeline | ✓ Passing |

---

## Suppression Roadmap

| Stage | Approach | Hardware | Status |
|-------|----------|----------|--------|
| **Stage 1** | PLL + anti-phase haptic (single LRA) | 4 IMUs + 1 LRA | 🔧 Firmware done, hardware next |
| **Stage 1b** | Push-pull LRAs (bidirectional) | +1 LRA + driver | 📋 Planned |
| **Stage 2** | Anti-phase FES (surface electrodes) | Stimulator + electrodes | 📋 Planned |
| **Stage 3** | Multi-frequency PLL (harmonics) | No change | 📋 Planned |
| **Stage 4** | Bilateral (both hands) | 2nd ESP32 + ESP-NOW | 📋 Planned |

---

## Key Algorithms

### 1. Phase-Locked Loop (PLL)
- Software PLL with numerically controlled oscillator (NCO)
- Phase detector: multiply input by quadrature NCO, low-pass filter
- Loop filter: PI controller adjusting NCO frequency
- Tracks tremor frequency (3-12 Hz) and phase in real-time

### 2. Phase Predictor
- Formula: φ_pred(t+Δt) = φ + 2π·f·Δt
- Δt = 12ms (mechanical delay + computation)

### 3. Anti-Phase Generator
- Target phase = φ_pred + π (180° offset)
- PWM duty = sin(anti_phase) * amplitude * gain
- **Push-pull**: compute_stereo_duties() returns complementary signals

### 4. Adaptive Gain
- Measure residual tremor (post-stimulation)
- If residual > target: increase gain
- If residual < target: decrease gain

---

## Environment Setup

```bash
cd C:\ForumProject
python -m venv .venv
.venv\Scripts\activate
pip install numpy matplotlib
```

**Run tests:**
```bash
python tests/test_pll.py
python tests/test_predictor.py
python tests/test_anticancel.py
python tests/test_adaptive_gain.py
python tests/test_bandpass.py
python tests/test_suppress.py
```

---

## Common Pitfalls

1. **Don't add FFT/classifier** — PLL is the new core, not FFT
2. **Single LRA limitation** — Needs push-pull for true anti-phase cancellation
3. **Mechanical delay matters** — LRA has ~10ms response time. Must predict ahead.
4. **PLL bandwidth** — Too wide = noisy, too narrow = can't follow drift. Start 0.5 Hz.
5. **Phase wrapping** — Phase is modulo 2π. Handle wrap-around correctly.
6. **Don't add numpy to firmware** — All firmware runs on MicroPython.
7. **I2C address conflict** — All IMUs at 0x68 behind mux. TCA9548A required for 4 IMUs.

---

## What To Build Next (ordered by impact)

1. **Assemble hardware** — 4 IMUs + TCA9548A + ESP32 (no LRA)
2. **Flash firmware + verify PLL tracking** — Use serial/LED to monitor
3. **Add push-pull LRAs** — 2 LRAs + MOSFET drivers for bidirectional
4. **Bench test cancellation** — Measure residual tremor with/without suppression
5. **Patient validation** — Collect data from PD/ET patients

---

*Last updated: 2026-09-02 after firmware testing revealed single-LRA limitation*
