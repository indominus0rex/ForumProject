# plan_a — full Hierarchical Stage Pipeline (HSP)

Plan A = the whole 12-stage pipeline. Nothing trimmed.

## What it is

- Code: `firmware/stages/` (one file per stage) + shared DSP in `firmware/common/`.
- Entry: `firmware/embedded_main_hsp.py` (thin dispatcher: timing + window
  management only, processing delegated to stages via `STAGE_ORDER`).
- Supervisory path: quality -> bandpass -> fft -> features -> classify (DNN)
  -> state_machine. Actuation path: `stages/suppress.py` PLL anti-phase chain
  via `frame['suppress_duty']`, which `stages/haptic.py` prefers.
- Contract: every stage implements `process(self, frame: dict) -> dict`.
  Frame is a plain dict (see `firmware/stages/__init__.py`).

## Stage order

safety -> sensor -> stationarity -> quality -> bandpass -> fft -> features
-> classify -> state_machine -> actuate -> haptic -> audit

## Hardware

ESP32-S3-Kaluga-1, up to 4× GY-521 via TCA9548A @0x70 (SDA=GPIO21, SCL=GPIO22),
LED=GPIO2, LRA=GPIO25 (200 Hz PWM via MOSFET). Size 57 × 28 mm. See `docs/assembly_checklist.md`.

## When to use Plan A vs Plan B

- Plan A: you have headroom and want DNN-supervised actuation
  (classification gates the LRA via state_machine + actuate).
- Plan B (`firmware/plan_b/`): you need a smaller fit — thin combos reusing
  the same `common/*` math. Current fit build is `b7_fit`
  (PLL-only, polling loop; device entry `fit_main.py`, not versioned in this repo).

## Rules (same as Plan B)

- No numpy/scipy in `firmware/`. MicroPython only.
- Feature order in `feature_extract.compute()` must match the host trainer.
- No weights enter `common/` without beating baseline on CV (bake gates hold).
