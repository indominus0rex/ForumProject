# Plan: switch back to bandpass filter -> FFT -> DNN

Goal: replace the PLL anti-phase suppression path with bandpass -> FFT -> DNN classification.

Context: STAGE_ORDER was safety,sensor,stationarity,quality,suppress,haptic,audit.
FFT/Features/Classify stages existed but were unwired; no DNN existed (trainer was
logreg-only, model weights were None placeholders).

Approach: add MicroPython 2-layer MLP forward (common/dnn.py) + weight placeholders
(common/model_dnn.py), add BandpassStage over the window, point ClassifyStage at the
DNN backend (heuristic fallback preserved), rewire STAGE_ORDER and embedded_main_hsp.py,
add --dnn training to train_classifier.py. TDD: tests/test_dnn_pipeline.py written first.

Done (all verified by real runs):
- tests/test_dnn_pipeline.py: 9 tests green (dnn math, bandpass DC/tremor, full window->label)
- full suite 8/8 green; embedded_main_hsp.py py_compiles; --dnn trainer verified on
  synthetic 2-class data (train 1.0 / CV 1.0, correct W1/B1/W2/B2 shapes)
- fixed NameError: embedded_main_hsp.py used QUALITY_FALLBACK_THRESH /
  QUALITY_FLAT_VAR_THRESH without importing them
- fixed CLASSES printing as np.str_(...) (would break MicroPython paste)

Left / not done:
- No baked DNN weights: repo sessions are single-class (postural only), so model_dnn
  weights stay None and the device runs the heuristic fallback until multi-class
  pilot data is collected and `train_classifier.py --dnn` output is pasted in.
- stages/suppress.py + common pll/anticancel/adaptive_gain/predictor kept (unused by
  pipeline, tests still cover them). Delete in a follow-up if the PLL path is retired.
- Not committed (no commit requested).
