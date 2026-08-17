# Embed README — Real-time Tremor Classifier on ESP32

## Pipeline

```
GY-521 (I2C 400 kHz) -> 100 Hz sampler -> 128-sample window
  -> feature_extract.compute()   (15 floats)
  -> scaler.apply()              (z-normalise)
  -> logreg.forward()            (4 logits -> softmax -> argmax)
  -> apply_feedback()            (LED GPIO 2 + LRA PWM GPIO 25)
  -> print to Thonny (pred, conf, probs)
```

## Files

- `embedded_main.py` — main loop, flash this last
- `feature_extract.py` — 15-feature extractor (no numpy)
- `logreg.py` — 4-class inference (matmul + softmax)
- `scaler.py` — z-normalise
- `model.py` — baked weights (paste from `train_classifier.py` output)
- `train_classifier.py` — offline trainer (scikit-learn)
- `fft.py` — `GY521` + `FFTProcessor` reused

## Wiring

| ESP32 pin | Device                                |
|-----------|---------------------------------------|
| 3V3       | GY-521 VCC                            |
| GND       | GY-521 GND                            |
| GPIO 21   | GY-521 SDA                            |
| GPIO 22   | GY-521 SCL                            |
| GPIO 2    | Status LED (built-in)                 |
| GPIO 25   | LRA haptic (PWM, 200 Hz, via MOSFET)  |
| 5V        | LRA VCC (if separate rail)            |
| GND       | LRA GND                               |

For first prototype, drive LRA from GPIO 25 via a logic-level MOSFET (IRLZ44N
or 2N7000) with flyback diode. LRA resonance ~200 Hz, so PWM freq must match
or use DRV2605 driver for clean drive later.

## Build + flash

1. `pip install scikit-learn numpy`
2. Collect data: see `sessions/README.md`
3. Train:
   ```
   python train_classifier.py
   ```
4. Copy the printed `CLASSES / FEATURE_MEAN / FEATURE_STD / WEIGHTS / BIAS` block into `model.py`
5. Flash these to ESP32 via Thonny (in any order, must all be on device):
   - `fft.py`
   - `feature_extract.py`
   - `logreg.py`
   - `scaler.py`
   - `model.py`
   - `embedded_main.py`
6. Open Thonny shell, run `embedded_main.py`

## Feedback map

| Class     | LED                | LRA                   |
|-----------|--------------------|-----------------------|
| baseline  | off                | off                   |
| rest      | off                | off                   |
| postural  | 0.5 Hz blink       | off                   |
| kinetic   | on solid           | 2 Hz pulse (100 ms)   |

## Verification checklist

- [ ] `python train_classifier.py` runs without error
- [ ] Train accuracy > 0.85 on pilot set
- [ ] Paste into `model.py`, `WEIGHTS` becomes a 4×15 list
- [ ] `embedded_main.py` boots, prints "Model: logistic-regression 4-class"
- [ ] Hold sensor still on table -> `rest` or `baseline`, conf > 0.7
- [ ] Shake sensor 5 Hz -> `kinetic`, conf > 0.6, LED on, LRA pulses
- [ ] Hold sensor extended in air -> `postural`, LED blinks, LRA off
- [ ] 60 s continuous run, no crashes, no OOM
- [ ] End-to-end latency < 1500 ms per window

## Heuristic fallback

If `model.WEIGHTS = None` in `model.py`, `embedded_main.py` uses the
peak-in-band detector from `fft.py` (3-12 Hz, magnitude > 1.2). No training
needed, less accurate. Useful for testing the pipeline before collecting
data.

## Out of scope

- DRV2605 LRA driver (raw PWM for now)
- Battery + charger
- SD card logging
- BLE telemetry
- On-device retraining
