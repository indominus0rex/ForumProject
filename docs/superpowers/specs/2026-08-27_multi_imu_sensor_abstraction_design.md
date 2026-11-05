# Multi-IMU Sensor Abstraction Design
Date: 2026-08-27
Project: ForumProject / Tremor Detection
Approach: Sensor Abstraction Layer + Multi-IMU First (Approach B)

## Context
The ForumProject implements an embedded tremor detection system with ESP32 MicroPython firmware and host-side Python training. Firmware uses Hierarchical Stage Pipeline HSP with stages safety → sensor → stationarity → fft → features → classify → haptic → audit. Host scripts train logistic regression on 15-feature windows from 128-sample 100 Hz IMU windows and export model constants to firmware.

Hardware docs describe TCA9548A multiplexer support for up to 4 MPU6050 IMUs at 0x68 via 0x70, with breathable IMU mount and optional 3-channel LRA array. Current firmware is single-IMU by default; multiplexer support exists in raw_data_collection.py but not integrated into HSP.

Goal: formalize sensor abstraction to enable stable multi-IMU operation while keeping ESP32/MicroPython constraints and research flexibility.

## Requirements
- Stay ESP32/MicroPython, no platform change
- Keep HSP stage interface unchanged
- Support single-IMU default and 4-IMU via TCA9548A
- Preserve host-firmware feature parity
- Research flexibility: configurable fusion, event logging, model versioning

## Architecture

### SensorProvider Interface
`common/sensor_provider.py`
- Protocol with `init()`, `select_channel(ch)`, `read_3axis() -> (x,y,z)`, `reset()`
- `SingleIMUProvider` wraps existing GY521 driver
- `MuxIMUProvider` wraps TCA9548A driver and GY521 with channel selection

`common/mux.py`
- TCA9548A driver, address 0x70, select channel via 1<<ch

### SensorHub Sampling
Config flags in `common/config.py`:
- `NUM_IMUS`, `TCA9548A_ADDR`, `IMU_CHANNEL_MAP`
- `MUX_SAMPLING_MODE` = 'sequential_windows' | 'interleaved'

Default `sequential_windows`:
- Timer ISR fills full 128-sample window for IMU0, then IMU1, etc.
- Keeps ISR short, avoids I2C mux switching in ISR
- Cycle time = NUM_IMUS * 1.28 s

Frame extensions:
- `frame["imu_id"]`
- `frame["imu_windows"]` list of windows

### Feature Extraction & Fusion
- `common/feature_extract.py` unchanged for single IMU
- Optional `common/features_fusion.py` aggregates per-IMU 15-feature vectors via mean/max/weighted by rms_all
- Config `FUSION_MODE = none|mean|max|weighted`

### Host-Firmware Model Contract
Host training outputs to `host_scripts/models/`:
- `model_constants.py` with CLASSES, FEATURE_MEAN, FEATURE_STD, WEIGHTS, BIAS
- `model_manifest.json` with version, feature_names[], feature_order_hash, num_classes, fs, samples, imu_mode

Firmware `common/model.py` validates feature length at import, falls back to heuristic on mismatch.

### Data Contracts
Single-IMU CSV: `LABEL,ax1,ay1,az1,...,ax128,ay128,az128`
Multi-IMU v2 CSV header: `# IMU_MODE=multi, NUM_IMUS=4, SAMPLES=128, FS=100`
Row: `LABEL, IMU0_ax1... IMU0_az128, IMU1_ax1..., ...`
`analyze_pilot.py` and `train_classifier.py` detect mode via header.

### Event Logging
Extend `stages/audit.py` to emit compact CSV per window:
`ts, imu_id, label, confidence, dominant_freq, rms, quality_ok, model_version`

## Files Touched
New:
- firmware/common/mux.py
- firmware/common/sensor_provider.py
- host_scripts/export_model_manifest.py

Modified:
- firmware/common/config.py
- firmware/common/model.py
- firmware/stages/sensor.py
- firmware/embedded_main_hsp.py
- host_scripts/train_classifier.py
- host_scripts/analyze_pilot.py

## Rollout Phases
Phase 1 - Abstraction: create mux/provider, refactor sensor stage, no behavior change for NUM_IMUS=1
Phase 2 - Mux sampling: implement sequential_windows mode, validate 4 IMU bench
Phase 3 - Host parity: multi-IMU CSV parsing, model_manifest generation
Phase 4 - Fusion experiment: optional features_fusion, config flag

## Verification
- Unit: provider channel select, I2C error fallback
- Integration: 4 IMU sequential windows produce correct CSVs
- Parity: host vs firmware feature vectors within 1e-6
- Research: event logs enable single vs fused performance comparison

## Success Criteria
Research flexibility maintained, sensor abstraction clean, multi-IMU data collection stable on ESP32/MicroPython.
