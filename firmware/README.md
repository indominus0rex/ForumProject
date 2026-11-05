# firmware — map

Two plans, one shared core. Nothing moved — this file is only a map.

- `firmware/plan_a/` — Plan A: full 12-stage HSP
  (`stages/` + entry `embedded_main_hsp.py`). Start here for the reference
  build. See `firmware/plan_a/README.md`.
- `firmware/plan_b/` — Plan B: thin combos reusing the same math
  (b1..b7, `runner.py` fallback chain). Start here for small-fit builds.
  Current fit build: `b7_fit` (device polling entry `fit_main.py`, not versioned in this repo).
  See `firmware/plan_b/README.md`.
- `firmware/stages/` — Plan A stage implementations (one file per stage).
- `firmware/common/` — shared DSP + drivers (bandpass, pll, predictor,
  anticancel, adaptive_gain, fft, feature_extract, dnn/logreg/scaler,
  gy521, tca9548a, baked `model*.py`). Imported by both plans.
- `firmware/archive/` — superseded mains (`embedded_main.py`,
  `raw_data_collection.py`, old `collect_pilot.py`). Reference only.
- `firmware/collect_pilot.py`, `firmware/raw_data_collection.py` — host-side
  data-capture helpers (root copies). Not flashed.

Rule for both plans: no numpy/scipy in `firmware/` (MicroPython).
