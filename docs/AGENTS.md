# AGENTS.md

Embedded tremor-detection project at `C:\ForumProject` (Windows). Two tiers: **MicroPython firmware on ESP32** (sensor + on-device FFT/feature extraction + classifier + haptic feedback) and **offline Python tooling on the host** (data analysis + scikit-learn trainer). Hardware contract (I2C pins, MPU6050 init, LED GPIO 2, LRA GPIO 25, 128-sample window @ 100 Hz) is documented in `CLAUDE.md` — do not break it.

## Dev environment
Python 3.11 is available as `python` (no `python3`). `pip` is missing — use `uv` for host-side Python deps (`scikit-learn`, `numpy`, `matplotlib`). Host-side scripts (`analyze_pilot.py`, `train_classifier.py`, `colab.py`) run from the repo root.

## Common commands
Verify host-side Python env (no hardware needed):
```
python -c "import matplotlib, numpy; print('ok')"
```

Analyze pilot CSVs (defaults to all `sessions/*.csv`; or pass paths):
```
python analyze_pilot.py
python analyze_pilot.py rest_s01.csv kinetic_s01.csv
```

Train classifier and emit a Python literal block to paste into `model.py`:
```
python train_classifier.py
python train_classifier.py sessions/rest_*.csv sessions/kinetic_*.csv
```

Standalone Colab-style plot of `data.txt` (host only, no ESP32 needed):
```
python colab.py
```

MicroPython files are deployed to ESP32 via Thonny — see `EMBED_README.md` Build + flash section.

## Layout
- `EMBED_README.md` — canonical pipeline + flash instructions for embedded firmware. Read this first.
- `CLAUDE.md` — hardware contract + MicroPython conventions. Treat as load-bearing.
- `docs/strap_and_lra_design.md` — removable IMU/LRA mounting using elastic fabric and Velcro.
- `embedded_main.py` — main firmware loop (flash last). Imports `model`, `feature_extract`, `scaler`, `logreg`, and `fft.GY521` / `FFTProcessor`.
- `model.py` — baked weights; `WEIGHTS = None` triggers heuristic fallback from `fft.py`.
- `fft.py` — `GY521` (sensor) + `FFTProcessor` (in-place Cooley-Tukey). Reused by firmware and `RawDataCollection.py`.
- `feature_extract.py`, `scaler.py`, `logreg.py` — MicroPython, no numpy.
- `RawDataCollection.py` — older 50 Hz CSV streamer (`LABEL = "healthy"|"tremor"`). Superseded by `collect_pilot.py`.
- `collect_pilot.py` — current 100 Hz, 4-class pilot capture (`LABEL = "rest"|"postural"|"kinetic"|"baseline"`). Outputs to `sessions/`.
- `sessions/` — captured CSVs. Filename pattern `<label>_s<NN>.csv`, rows: `<LABEL>,ax1,ay1,az1,...,ax128,ay128,az128`.
- `analyze_pilot.py`, `train_classifier.py` — host-side analysis + training.
- `colab.py`, `data.txt`, `graph_1.png` — legacy Colab-style exploration script + sample data + output.

## Conventions
- MicroPython: **4-space indent**, `from machine import I2C, Pin[, PWM]`, `time.ticks_us()` / `time.ticks_diff()` for µs timing (never `time.time()`), class-per-stage (`GY521`, `FFTProcessor`).
- Performance: Pre-compute twiddle factors for FFT, use fixed-point where possible, leverage ESP32 dual I2C:
    - I2C0: Sensors (SCL=GPIO22, SDA=GPIO21)
    - I2C1: Peripherals (SCL=GPIO23, SDA=GPIO19)
- Memory: Pre-allocate sensor buffers, reuse instead of reallocation, use `bytearray` for I2C.
- On-device FFT: in-place Cooley-Tukey on power-of-2 length with Hann window and DC removal. No `numpy.fft` or `matplotlib` on-device.
- Feature order in `feature_extract.compute()` **must** match `train_classifier.extract_features()`. 15-element list and `FEATURE_MEAN`/`FEATURE_STD` length in `model.py` coupled.
- `model.CLASSES` order must match row order of `WEIGHTS` and `BIAS` from trainer.
- Host-side scripts: tolerate Thai/English bilingual comments (`colab.py` already has Thai — do not translate).
- Commit messages: terse English (e.g., `add 3-axis detection to fft.py`).
- Branch: `ASUS` is current dev; `main` for PRs. Recent merges from `work`. Do not rename repo dir — git remote pinned to `Project_Thonny` (legacy).

## Pitfalls
- **Don't hand-edit auto-generated block in `model.py`.** Run `python train_classifier.py`, copy printed `CLASSES / FEATURE_MEAN / FEATURE_STD / WEIGHTS / BIAS` block verbatim. Keep `FEATURE_MEAN`/`FEATURE_STD` lengths 15 and `WEIGHTS` shape 4×15.
- **Don't add numpy/scipy imports to firmware files.** All `.py` in `firmware/` run on ESP32.
- **Flash order matters.** Per `EMBED_README.md` step 5: `fft.py`, `feature_extract.py`, `logreg.py`, `scaler.py`, `model.py` must be on device before `embedded_main.py` imports them cleanly. `embedded_main.py` is entry point run last.
- **`pip` missing on Windows host.** Use `uv pip install scikit-learn numpy matplotlib` (or `python -m ensurepip`) before `train_classifier.py` / `analyze_pilot.py`.
- **Sampling rates differ:** `RawDataCollection.py` and `fft.py` @ 50 Hz (`SAMPLE_INTERVAL_US = 20000`); `collect_pilot.py` and `embedded_main.py` @ 100 Hz (`SAMPLE_INTERVAL_US = 10000`). Don't mix when reasoning about `fs`.
- **`colab.py` hard-codes `fs = 20`** (from `time.sleep(0.05)`). Not canonical fs for project.
- **`collect_pilot.py` prints rows to Thonny shell**; operator copies to `sessions/<label>_sNN.csv` manually. No serial port/file write on device.
- **Sensor I2C read failures** return `1.0` magnitude (gravity fallback) in `fft.GY521.get_3axis_vector` and `(0.0, 0.0, 1.0)` in `collect_pilot.GY521.read_3axis`. Treat repeated fallbacks as wiring fault, not valid data.
- **`sessions/` empty on fresh clone** — `analyze_pilot.py` and `train_classifier.py` exit with `"No CSVs found in ./sessions/. Pass files on CLI."` until data captured.