# Forum Project — What You Need to Know

## Goal
A wearable hand-tremor suppression system using **phase-locked loop (PLL) tracking** and **adaptive anti-phase cancellation** running entirely on ESP32 edge hardware — no FFT classification, no cloud, no phone. Predicts tremor phase in real-time and delivers precisely timed counter-stimulation.

## What makes this different from published research

Most tremor research follows the same playbook: FFT → feature extraction → ML classifier → haptic cueing. We skip all of that.

| Typical research | Our approach |
|-----------------|--------------|
| FFT + features + LogReg/CNN | PLL phase tracking — no feature extraction |
| Classify then react | Predict phase, cancel before peak |
| Haptic cueing (vague buzz) | Anti-phase stimulation at exact inverse |
| Cloud AI (Felix wristband) | All edge, zero connectivity |
| 100ms+ latency windows | 1ms sample-by-sample tracking |
| Treat tremor as classification | Treat tremor as oscillator to cancel |

## Core Insight

Tremor is a quasi-periodic oscillator (3-12 Hz). Instead of classifying windows of data, we **track its phase in real-time using a PLL** and deliver stimulation at exactly the opposite phase (180° offset) to cancel it. This is the same noise-cancelling headphone principle, but for hand tremors.

## Architecture Overview

```
┌────────────────────── EDGE DEVICE (ESP32) ──────────────────────┐
│                                                                  │
│  [4 IMUs] → [I2C Mux] → [Bandpass filter 3-12 Hz]             │
│      ↓              ↓                                            │
│  (raw accel)    [PLL phase tracker] ←── (adaptive loop)         │
│                      ↓                                           │
│              [Phase predictor: 10-20ms ahead]                    │
│                      ↓                                           │
│              [Anti-phase PWM generator]                          │
│                      ↓                                           │
│              [LRA array: counter-stimulation]                    │
│                                                                  │
│  ALL ON-DEVICE. NO FFT. NO CLASSIFIER. NO CLOUD.                │
│  Sample rate: 1000 Hz. Tracking latency: <1ms.                  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Why this works

1. **PLL tracking**: A software PLL locks onto the tremor oscillator frequency and phase. It adapts to frequency drift (tremor changes over time) without retraining.
2. **Phase prediction**: Using the tracked phase + frequency, we predict where the tremor will be 10-20ms in the future (accounting for mechanical + computational delay).
3. **Anti-phase delivery**: Fire the LRA at exactly the opposite phase — pushing back against the tremor at its peak velocity.
4. **Adaptive gain**: Continuously adjust stimulation amplitude based on residual tremor (the IMU measures what's left after cancellation).

## Project Map

### Firmware (`firmware/`) — Runs on ESP32 (MicroPython)
| File | Purpose | Role |
|------|---------|------|
| `common/config.py` | Hardware pins, I2C, PLL params | Config |
| `common/gy521.py` | GY521/MPU6050 driver | Sensor |
| `common/tca9548a.py` | I2C multiplexer driver | Sensor |
| `common/bandpass.py` | 2nd-order IIR bandpass 3-12 Hz | Signal conditioning |
| `common/pll.py` | Phase-locked loop tracker | **Core algorithm** |
| `common/predictor.py` | Phase prediction (N ms ahead) | **Core algorithm** |
| `common/anticancel.py` | Anti-phase PWM generator | **Actuation** |
| `common/adaptive_gain.py` | Residual-based gain adaptation | **Adaptation** |
| `stages/suppress.py` | Main suppression pipeline stage | **Orchestration** |
| `stages/haptic.py` | LRA haptic output (PWM array) | Actuation |
| `stages/quality.py` | Signal quality gate | Safety |
| `stages/safety.py` | Safety limits | Safety |

### Host Scripts (`host_scripts/`) — Runs on PC (offline)
| File | Purpose |
|------|---------|
| `tune_pll.py` | Tune PLL bandwidth/damping from recorded data |
| `evaluate_cancellation.py` | Measure cancellation efficacy (residual vs raw) |

## Key Algorithms

### 1. Phase-Locked Loop (PLL)
- Software PLL with numerically controlled oscillator (NCO)
- Phase detector: multiply input by NCO output, low-pass filter
- Loop filter: PI controller adjusting NCO frequency
- Tracks tremor frequency (3-12 Hz) and phase in real-time
- Adapts to frequency drift within 2-3 cycles

### 2. Phase Predictor
- Using tracked phase (φ) and frequency (f): φ_pred(t+Δt) = φ + 2π·f·Δt
- Δt = 15ms (mechanical delay + computation)
- Predicts where tremor will be, not where it was

### 3. Anti-Phase Generator
- Target phase = φ_pred + π (180° offset)
- PWM duty proportional to predicted amplitude
- Fires LRA at exact counter-phase

### 4. Adaptive Gain
- Measure residual tremor (post-stimulation)
- If residual > target: increase gain
- If residual < target: decrease gain
- Prevents over-stimulation and habituation

## Suppression Roadmap

| Stage | Approach | Status |
|-------|----------|--------|
| **Stage 1** | PLL tracking + anti-phase haptic | 🔧 In progress |
| **Stage 2** | Anti-phase FES (surface electrodes) | 📋 Planned |
| **Stage 3** | Multi-frequency PLL (tremor has harmonics) | 📋 Planned |
| **Stage 4** | Bilateral coordination (both hands) | 📋 Planned |

## Key Terms

| Term | Meaning |
|------|---------|
| **PLL** | Phase-Locked Loop — tracks oscillator phase/frequency |
| **NCO** | Numerically Controlled Oscillator — digital signal generator |
| **Anti-phase** | 180° offset — push back against tremor at peak |
| **Residual** | Remaining tremor after cancellation |
| **Adaptive gain** | Auto-adjust stimulation strength |
| **IIR** | Infinite Impulse Response (efficient digital filter) |
| **Stochastic resonance** | Using noise to enhance signal detection (future stage) |

## Current State

- [x] Hardware config (4 IMUs, I2C mux, pins, LRA PWM)
- [x] Basic data collection pipeline
- [x] Heuristic classifier (placeholder — being replaced)
- [x] LRA haptic output (3 motors, PWM)
- [ ] PLL phase tracker (new core algorithm)
- [ ] Phase predictor
- [ ] Anti-phase generator
- [ ] Adaptive gain controller
- [ ] Real patient validation

## Environment Setup

```bash
cd C:\ForumProject
python -m venv .venv
.venv\Scripts\activate
pip install numpy matplotlib
```

## Common Pitfalls

1. **Don't add FFT/classifier** — we're not doing FFT-based classification anymore. PLL is the new core.
2. **Mechanical delay matters** — LRA has ~10ms mechanical response time. Must predict ahead.
3. **Loop stability** — PLL bandwidth too wide = noisy tracking, too narrow = can't follow frequency drift. Start with 0.5 Hz bandwidth.
4. **Phase wrapping** — phase is modulo 2π. Handle wrap-around correctly in predictor.
5. **Don't add numpy to firmware** — all firmware runs on MicroPython. Use fixed-point or simple float math.

## Research (context, not implementation)

We deliberately diverge from:
- FFT + ML classification (most papers)
- TAPS/FDA-cleared devices (patterned stimulation, not phase-locked)
- Cloud AI (Felix wristband) — we're edge-only
- Window-based processing (100ms+ latency) — we're sample-by-sample

Our approach is closer to:
- Active noise cancellation (ANC) headphones
- Adaptive feedforward control
- Phase-locked loops in communications

## What To Build Next (ordered by impact)

1. **Implement PLL tracker** (`firmware/common/pll.py`)
2. **Implement phase predictor** (`firmware/common/predictor.py`)
3. **Implement anti-phase generator** (`firmware/common/anticancel.py`)
4. **Implement adaptive gain** (`firmware/common/adaptive_gain.py`)
5. **Integrate into main loop** (`firmware/stages/suppress.py`)
6. **Tune PLL params on real data** (`host_scripts/tune_pll.py`)
