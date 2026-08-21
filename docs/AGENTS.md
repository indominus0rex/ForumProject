# AGENTS.md

Embedded tremor-detection project at `C:\ForumProject` (Windows). Two tiers: **MicroPython firmware on ESP32** (sensor + on-device FFT/feature extraction + classifier + haptic feedback) and **offline Python tooling on the host** (data analysis + scikit-learn trainer). Hardware contract (I2C pins, MPU6050 init, LED GPIO 2, LRA GPIO 25, 128-sample window @ 100 Hz) is documented in `CLAUDE.md` — do not break it.

There is **no build system, no test suite, no linter, no `requirements.txt`, no CI**. MicroPython files are flashed directly to the ESP32 via Thonny (per `EMBED_README.md`); the host-side Python is run as plain scripts.

## Dev environment

Python 3.11 is available as `python` (no `python3`). `pip` is missing — use `uv` for host-side Python deps (`scikit-learn`, `numpy`, `matplotlib`).

No virtualenv, no lockfile. The host-side scripts (`analyze_pilot.py`, `train_classifier.py`, `colab.py`) run from the repo root.

## Common commands

Verify the host-side Python env works (no hardware needed):

```
python -c "import matplotlib, numpy; print('ok')"
```

Analyze pilot CSVs (defaults to all `sessions/*.csv`; or pass paths):

```
python analyze_pilot.py
python analyze_pilot.py rest_s01.csv kinetic_s01.csv
```

Train the classifier and emit a Python literal block to paste into `model.py`:

```
python train_classifier.py
python train_classifier.py sessions/rest_*.csv sessions/kinetic_*.csv
```

Standalone Colab-style plot of `data.txt` (host only, no ESP32 needed):

```
python colab.py
```

MicroPython files (`fft.py`, `feature_extract.py`, `logreg.py`, `scaler.py`, `model.py`, `embedded_main.py`, `RawDataCollection.py`, `collect_pilot.py`) have **no host-side runner**. They are deployed to the ESP32 via Thonny — see `EMBED_README.md` Build + flash section for the exact sequence.

## Layout

- `EMBED_README.md` — canonical pipeline + flash instructions for the embedded firmware tier. Read this before touching firmware files.
- `CLAUDE.md` — hardware contract + MicroPython conventions. Treat as load-bearing.
- `README.md` — only dated progress notes, not real docs. Ignore for new work.
- `embedded_main.py` — main firmware loop (flash last). Imports `model`, `feature_extract`, `scaler`, `logreg`, and `fft.GY521` / `FFTProcessor`.
- `model.py` — baked weights; `WEIGHTS = None` triggers heuristic fallback from `fft.py`.
- `fft.py` — `GY521` (sensor) + `FFTProcessor` (in-place Cooley-Tukey). Reused by both firmware and `RawDataCollection.py`.
- `feature_extract.py`, `scaler.py`, `logreg.py` — MicroPython, no numpy.
- `RawDataCollection.py` — older 50 Hz CSV streamer (`LABEL = "healthy"|"tremor"`). Superseded by `collect_pilot.py` for pilot capture; keep for the original workflow.
- `collect_pilot.py` — current 100 Hz, 4-class pilot capture (`LABEL = "rest"|"postural"|"kinetic"|"baseline"`). Outputs land in `sessions/`.
- `sessions/` — captured CSVs. Filename pattern `<label>_s<NN>.csv`, rows are `<LABEL>,ax1,ay1,az1,...,ax128,ay128,az128`.
- `analyze_pilot.py`, `train_classifier.py` — host-side analysis + training.
- `colab.py`, `data.txt`, `graph_1.png` — legacy Colab-style exploration script + sample data + its rendered output.

## Conventions

- MicroPython files: **4-space indent**, `from machine import I2C, Pin[, PWM]`, `time.ticks_us()` / `time.ticks_diff()` for microsecond timing (never `time.time()`), class-per-stage (`GY521`, `FFTProcessor`).
- On-device FFT is in-place Cooley-Tukey on power-of-2 length with a Hann window and DC removal already applied. Do not pull in `numpy.fft` or `matplotlib` on-device — RAM/flash budget is tight.
- Feature order in `feature_extract.compute()` **must** match the order in `train_classifier.extract_features()`. The 15-element list and the matching `FEATURE_MEAN`/`FEATURE_STD` length in `model.py` are coupled.
- `model.CLASSES` order must match the row order of `WEIGHTS` and `BIAS` produced by the trainer.
- Host-side scripts: tolerate Thai/English bilingual comments (`colab.py` already has Thai — do not translate).
- Commit messages are terse English (existing log: `add 3-axis detection to fft.py`, `update rawdatacollection.py to convert to fft`).
- Branch: `ASUS` is current dev; `main` for PRs. Recent merges from `work`. Do not rename the repo directory — git remote is pinned to `Project_Thonny` (legacy).

## Pitfalls

- **Don't hand-edit the auto-generated block in `model.py`.** Run `python train_classifier.py`, copy the printed `CLASSES / FEATURE_MEAN / FEATURE_STD / WEIGHTS / BIAS` block verbatim. Keep `FEATURE_MEAN`/`FEATURE_STD` lengths at 15 and `WEIGHTS` shape 4×15.
- **Don't add numpy/scipy imports to firmware files.** `embedded_main.py`, `feature_extract.py`, `logreg.py`, `scaler.py`, `fft.py`, `RawDataCollection.py`, `collect_pilot.py` all run on the ESP32.
- **Flash order matters for firmware.** Per `EMBED_README.md` step 5, `fft.py`, `feature_extract.py`, `logreg.py`, `scaler.py`, `model.py` must all be on the device before `embedded_main.py` will import them cleanly. `embedded_main.py` is the entry point run last.
- **`pip` is missing on this Windows host.** Use `uv pip install scikit-learn numpy matplotlib` (or `python -m ensurepip`) before running `train_classifier.py` / `analyze_pilot.py`.
- **`RawDataCollection.py` and `fft.py` sample at 50 Hz** (`SAMPLE_INTERVAL_US = 20000`); **`collect_pilot.py` and `embedded_main.py` sample at 100 Hz** (`SAMPLE_INTERVAL_US = 10000`). Don't mix the two when reasoning about `fs`.
- **`colab.py` hard-codes `fs = 20`** because its sample data came from a script with `time.sleep(0.05)`. It is **not** the canonical fs for the rest of the project.
- **`collect_pilot.py` prints rows to the Thonny shell**; the operator copies them into `sessions/<label>_sNN.csv` by hand. Don't expect a serial port / file write on the device.
- **Sensor I2C read failures return `1.0` magnitude (gravity fallback)** in `fft.GY521.get_3axis_vector` and `(0.0, 0.0, 1.0)` in `collect_pilot.GY521.read_3axis`. Treat repeated fallback values as a wiring fault, not valid data.
- **`sessions/` is empty on a fresh clone** — `analyze_pilot.py` and `train_classifier.py` will exit with `"No CSVs found in ./sessions/. Pass files on CLI."` until you capture data.
