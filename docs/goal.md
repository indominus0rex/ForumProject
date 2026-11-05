# Main goal

Build a Parkinson's hand tremor suppression device that handles pill-rolling and
essential tremor as separate problems, suppresses in real time, and computes
entirely on the edge (ESP32) - efficient, research-backed, no phone or cloud in the loop.

## Goal constraints

- Two tremor types, two problems: pill-rolling (rest, 4-6 Hz, thumb-index driven) and
  essential tremor (postural/kinetic, 6-12 Hz, wrist/finger driven) get separate
  detection bands, coherence discriminants, and actuation targets.
- Real-time suppression: sample-to-actuation in the tens of milliseconds at 100 Hz
  sampling. Per-sample actuation (PLL / phase-burst replay) supervised by per-window
  classification (~1.28 s windows). The window path never drives the LRA directly.
- Edge computing: all inference (bandpass, FFT, features, MLP/CNN forward, PLL, state
  machine) runs on the ESP32 in MicroPython. Training stays on the host; the only
  host-to-device bridge is baked weights pasted into firmware/common/model_*.py.
  No cloud or phone dependency at runtime - on-device closed loop is the differentiator.

## Current architecture (see firmware/)

- Supervisory path: firmware/stages quality -> bandpass -> fft -> features -> classify
  -> state_machine, wired by firmware/embedded_main_hsp.py via STAGE_ORDER.
- Actuation path: firmware/stages/suppress.py (PLL anti-phase chain), driven from
  frame['suppress_duty'] which firmware/stages/haptic.py already prefers.
- Research direction (plans in .hermes/plans/): 1D-CNN perception, LSTM persistence
  gate, phase-tracking burst actuation; hybrid DNN-gated PLL as fallback.

## Data doctrine

- Live 100 Hz pilot data (docs/pilot_collection_protocol.md) outranks resampled
  clinical data for every training decision.
- Bake gates hold: no weights enter firmware/common/ without beating the baseline on
  cross-validation. Negative results are recorded, not tuned around.

