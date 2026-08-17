# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Embedded tremor-detection system. Two-tier setup:

- **MicroPython on ESP32** (firmware layer): reads GY-521 (MPU6050) accelerometer over I2C, computes FFT on-device, detects dominant tremor frequency, drives an LED when intensity crosses threshold.
- **Google Colab** (analysis layer): offline FFT/plot of raw 3-axis samples for dataset exploration and graph export (`graph_1.png`).

Repo name is `C:\ForumProject` (Windows). Do not rename — git remote is pinned to `Project_Thonny` (legacy).

## Files

- `RawDataCollection.py` — MicroPython, runs on ESP32. Streams 3-axis samples as CSV (label-prefixed) for dataset capture. Set `LABEL = "healthy"` or `"tremor"` before flash.
- `fft.py` — MicroPython, runs on ESP32. Same sensor pipeline plus on-device Cooley-Tukey FFT; reports dominant frequency + intensity; toggles LED on GPIO 2 when `mag > 1.2`.
- `colab.py` — Python 3, runs in Colab. Parses raw CSV string, plots time-domain + single-sided FFT spectrum (fs=20 Hz, Nyquist=10 Hz). Comment is Thai — leave as-is.
- `data.txt` — 100-row sample of 3-axis accelerometer data (X,Y,Z in g, comma-separated, one sample per line).
- `graph_1.png` — Pre-rendered output from `colab.py`.

## Hardware contract (do not break)

- I2C: `I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)` — fast-mode 400 kHz.
- MPU6050 (`GY521`) at `0x68`: reset → wake → ±2g (`0x1C=0x00`) → DLPF 94 Hz (`0x1A=0x02`) → sample-rate div 0 (`0x19=0x00`).
- Accel scale: 16384 LSB/g (raw 16-bit → signed → divide by 16384).
- LED: `Pin(2, Pin.OUT)`.
- Sampling: `SAMPLES = 128`, `SAMPLE_INTERVAL_US = 20000` (target 50 Hz); actual `fs` computed from measured loop duration, not assumed.
- FFT: in-place Cooley-Tukey, `num_samples` must be power of 2. Hann window pre-applied, DC mean removed before FFT.
- `NOISE_THRESHOLD = 0.35` in `process_data` — below this, returns `(0.0, 0.0)`.
- `get_3axis_vector` returns scalar magnitude `sqrt(x² + y² + z²)`; on I2C read error returns `1.0` (gravity fallback).

## Run / flash

No build system, no tests, no linter, no `requirements.txt`. MicroPython files are deployed via **Thonny** (per README) directly to the ESP32.

Quick local check (no hardware) — `colab.py` standalone:

```bash
python -c "import matplotlib, numpy; print('ok')"
python colab.py   # or paste cells into a notebook
```

CSV capture workflow: flash `RawDataCollection.py` → run → copy `LABEL,<samples...>` lines from Thonny shell → paste into `colab.py` `raw_data` string → run cells.

## Conventions

- MicroPython: 4-space indent, class-per-stage (`GY521`, `FFTProcessor`), `from machine import I2C, Pin`, `time.ticks_us` for microsecond timing (not `time.time()`).
- Colab cells: bilingual Thai/English comments OK; do not translate existing Thai.
- Commit messages terse English; existing log: `add 3-axis detection to fft.py`, `update rawdatacollection.py to convert to fft`.
- `numpy.fft` / `matplotlib` only in `colab.py` — never import on-device (RAM/flash).
- Branch: `ASUS` (current dev), `main` for PRs. Recent merges from `work`.
