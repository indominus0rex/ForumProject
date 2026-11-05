# Plan B — algorithm-combination directory

## Goal

Add a `firmware/plan_b/` directory with six named, swappable perception x suppression algorithm combos plus a registry, fallback runner, host benchmark, and tests — so the device has working fallbacks when the main HSP pipeline fails.

## Current context / assumptions

Verified by reading the repo on 2026-09-09 (no code changed):

- Main pipeline: `firmware/embedded_main_hsp.py` wires `firmware/stages/` in `STAGE_ORDER` from `firmware/stages/__init__.py`: `safety -> sensor -> stationarity -> quality -> bandpass -> fft -> features -> classify -> state_machine -> actuate -> haptic -> audit`. Every stage implements `process(self, frame: Frame) -> Frame` where `Frame = Dict[str, Any]` (a plain dict).
- Window contract: `SAMPLES = 128` at `SAMPLE_RATE_HZ = 100.0` (`SAMPLE_INTERVAL_US = 10000`, `WINDOW_SECONDS = 1.28`) from `firmware/common/config.py`. Frame keys used today: `window` (128x3 list), `label`, `confidence`, `probs`, `suppress_duty`, `pll_phase`, `pll_freq`, `pll_locked`, `adaptive_gain`.
- Perception options already in tree:
  - P0 heuristic: `firmware/stages/classify.py::_classify_heuristic` (magnitude FFT peak in 3-12 Hz, mag > 1.2, returns `kinetic` else `rest`). No weights needed.
  - P1 logreg: `firmware/common/model.py` (CLASSES + FEATURE_MEAN/STD + WEIGHTS/BIAS, currently `WEIGHTS = None`) + `firmware/common/logreg.py::forward/argmax` + `firmware/common/scaler.py::apply` + `firmware/common/feature_extract.py::compute` (15 features, order MUST match `host_scripts/train_classifier.py::extract_features`). Trainer: `host_scripts/train_classifier.py`.
  - P2 DNN MLP: `firmware/common/model_dnn.py` (baked `W1/B1/W2/B2`, 15->16->4) + `firmware/common/dnn.py::forward`. This is the current default in `ClassifyStage`. Trainer: `host_scripts/train_dnn_parkinsons.py` (log: logreg CV 0.661, dnn CV 0.750, GATE PASS).
  - P3 CNN1D: `firmware/common/model_cnn.py` + `firmware/common/cnn1d.py`, spectra over 64 bins (`window_spectra`, log1p). Trainer: `host_scripts/train_cnn1d_parkinsons.py` (log: cnn CV 0.597 vs baked-mlp 0.750, GATE FAIL — quarantined).
- Filtering options: F0 raw; F1 wide bandpass 3-12 Hz (`firmware/common/bandpass.py::BandpassFilter`, `BANDPASS_LOW_HZ/HIGH_HZ` in config); F2 split pill 4-6 Hz / ET 6-9 Hz (`PILL_BAND_*`, `ET_BAND_*`, `COH_*_THRESH` in config + `pill_band_power` helper noted in `feature_extract.py` docstring).
- Suppression options:
  - S0 threshold haptic: `firmware/stages/haptic.py` + `firmware/stages/actuate.py` (window-label-gated fixed duty, `LRA_DUTY_ON = 512`, `LRA_PIN = 25`).
  - S1 full PLL chain: `firmware/stages/suppress.py::SuppressStage` = `BandpassFilter -> PLL (common/pll.py, center 6.0 Hz, bandwidth 1.0) -> PhasePredictor (common/predictor.py, 15 ms) -> AntiPhaseGenerator (common/anticancel.py, max_duty 1023) -> AdaptiveGain (common/adaptive_gain.py, init 0.5, min 0, max 2.0, target 0.3)`. Exposes `process_sample(x,y,z)->int` and `process(frame)` writing `suppress_duty/pll_phase/pll_freq/pll_locked/adaptive_gain`.
  - S2 fixed-gain PLL (S1 minus adaptation) and S3 bandpass-only open-loop do NOT exist yet — build as thin wrappers, no new DSP math.
- Tests pattern: `tests/test_suppress.py` does `sys.path.insert(0, "firmware")` then `from stages.suppress import SuppressStage`; asserts duty in 0..1023 and frame keys. Run with `python -m pytest tests/ -v` on Windows (`python`, not `python3`; `pip` missing — use `uv pip install` for host deps).
- No `plan_b` exists today (content search for `plan_b|plan-b|PlanB` returned 0 hits). Plans live in `.hermes/plans/`.
- Constraints (load-bearing, from `docs/GOAL.md` + `docs/AGENTS.md` in context): NO numpy/sklearn/torch imports inside `firmware/` (MicroPython, ESP32); 4-space indent; feature order and `CLASSES` order couplings above; flash order `fft, feature_extract, logreg, scaler, model*` before entry point; branch `ASUS`, terse English commits.

## Architecture / proposed approach

`firmware/plan_b/` holds six thin combo modules that only compose existing `common.*`/`stages.*` classes (no duplicated filter/PLL/forward math), all implementing the same `process(frame)->frame` + `process_sample(x,y,z)->int` shape so `runner.py` can select by name and walk a fallback chain. A host-only `host_scripts/bench_plan_b.py` scores every combo on the cached windows (`host_scripts/parkinsons_windows.py`) without touching firmware imports, and `tests/test_plan_b.py` pins the contract.

## Combo matrix (the six — no more, no fewer)

| Name | Perception | Suppression | Filter | When to use / gate |
|---|---|---|---|---|
| B1 `safe` | P0 heuristic | S0 threshold haptic | F1 3-12 Hz | No weights on device (`model.WEIGHTS is None` and `model_dnn.W1 is None`); sensor-fault fallback |
| B2 `baseline-ml` | P1 logreg | S0 threshold haptic | F1 | Logreg baked and beats heuristic on CV |
| B3 `current-best` | P2 DNN | S1 full PLL + adaptive gain | F1 | Default; mirrors main pipeline (reference) |
| B4 `pll-only` | none (P0 for logging only) | S1 full PLL | F1 | Classifier broken/uncertain; pure real-time loop |
| B5 `fixed-gain` | P2 DNN gate | S2 fixed-gain PLL (gain 0.5, no adapt) | F2 split pill/ET | Adaptation oscillates (gain hunting); DNN gates output by `label != baseline/rest` and conf threshold |
| B6 `cnn-future` | P3 CNN1D | S1 full PLL | F1 spectra | QUARANTINED: host bench only until CNN beats DNN gate (`GATE_BASELINE_CV = 0.750`); firmware `process()` raises `RuntimeError` with the gate message |

Fallback chain in runner: `B3 -> B5 -> B2 -> B4 -> B1`. B6 is never in the chain.

## Step-by-step tasks

Conventions for every task: Windows shell, repo root `C:/forumproject`. Python is `python` (3.11). After each task, commit. TDD: write/extend the failing test first, run to see it fail, implement minimally, re-run to pass, commit.

### Task 0 — verify inventory (read-only, 2 min)

Run (expected: lists the files named below, zero hits for plan_b):

```
git -C C:/forumproject status --short | head -20
python -c "import ast,glob; print(sorted(glob.glob('firmware/common/*.py')))"
python -c "import ast,glob; print(sorted(glob.glob('firmware/stages/*.py')))"
python -m pytest tests/test_suppress.py -v
```

Expected output: pytest shows 3+ passed (init / duty / frame tests). If pytest is missing: `uv pip install pytest numpy scikit-learn` then re-run.

Commit: none (read-only).

### Task 1 — scaffold `firmware/plan_b/` + registry + failing test (5 min)

1a. Create `firmware/plan_b/__init__.py` with exactly this content (registry only, no combo logic):

```python
"""plan_b — named fallback algorithm combos (thin wiring only).

Each combo module exposes:
    NAME: str
    DESCRIPTION: str
    PERCEPTION: str
    SUPPRESSION: str
    GATE_OK: bool         # False for quarantined combos (B6)
    class Combo:
        def __init__(self, fs: float = 100.0): ...
        def process(self, frame: dict) -> dict: ...
        def process_sample(self, x: float, y: float, z: float) -> int: ...
"""

PLAN_B_REGISTRY = {
    "b1_safe": "plan_b.combo_b1_heuristic_haptic",
    "b2_baseline_ml": "plan_b.combo_b2_logreg_haptic",
    "b3_current_best": "plan_b.combo_b3_dnn_pll",
    "b4_pll_only": "plan_b.combo_b4_pll_only",
    "b5_fixed_gain": "plan_b.combo_b5_dnn_fixed_gain",
    "b6_cnn_future": "plan_b.combo_b6_cnn_pll",
}

FALLBACK_CHAIN = ["b3_current_best", "b5_fixed_gain", "b2_baseline_ml", "b4_pll_only", "b1_safe"]

__all__ = ["PLAN_B_REGISTRY", "FALLBACK_CHAIN"]
```

1b. Create `tests/test_plan_b.py` with exactly this content (fails now — no combo modules yet):

```python
"""tests/test_plan_b.py — contract tests for firmware/plan_b combos."""
import sys
import importlib

sys.path.insert(0, "firmware")

from plan_b import PLAN_B_REGISTRY, FALLBACK_CHAIN


def _load(name):
    return importlib.import_module(PLAN_B_REGISTRY[name])


def test_registry_has_six_combos():
    assert sorted(PLAN_B_REGISTRY) == [
        "b1_safe", "b2_baseline_ml", "b3_current_best",
        "b4_pll_only", "b5_fixed_gain", "b6_cnn_future",
    ]
    assert "b6_cnn_future" not in FALLBACK_CHAIN


def test_each_combo_contract():
    for name in PLAN_B_REGISTRY:
        mod = _load(name)
        assert isinstance(mod.NAME, str)
        assert isinstance(mod.DESCRIPTION, str)
        assert isinstance(mod.GATE_OK, bool)
        combo = mod.Combo(fs=100.0)
        duty = combo.process_sample(0.1, 0.2, 0.9)
        assert isinstance(duty, int) and 0 <= duty <= 1023
        frame = {"window": [[0.1, 0.2, 0.9]] * 128, "x": 0.1, "y": 0.2, "z": 0.9}
        out = combo.process(dict(frame))
        assert "plan_b" in out and out["plan_b"] == mod.NAME
        assert "suppress_duty" in out


def test_b6_quarantined():
    mod = _load("b6_cnn_future")
    assert mod.GATE_OK is False
    try:
        mod.Combo(fs=100.0).process({"window": [[0.0, 0.0, 1.0]] * 128})
    except RuntimeError as e:
        assert "GATE" in str(e)
    else:
        raise AssertionError("B6 firmware process() must raise RuntimeError")
```

1c. Verify failure (expected: 2 failures, `ModuleNotFoundError: plan_b.combo_b1...`):

```
python -m pytest tests/test_plan_b.py -v
```

1d. Create the six combo files as 5-line stubs so the import error clears but contract tests still fail on `Combo` (this is the RED step — do not implement yet):

Each of `firmware/plan_b/combo_b1_heuristic_haptic.py`, `combo_b2_logreg_haptic.py`, `combo_b3_dnn_pll.py`, `combo_b4_pll_only.py`, `combo_b5_dnn_fixed_gain.py`, `combo_b6_cnn_pll.py` gets:

```python
NAME = "bX_todo"
DESCRIPTION = "todo stub"
PERCEPTION = "todo"
SUPPRESSION = "todo"
GATE_OK = True
```

Commit: `git add firmware/plan_b/__init__.py tests/test_plan_b.py firmware/plan_b/combo_*.py && git commit -m "add plan_b scaffold and contract tests"`

### Task 2 — B1 safe: heuristic + threshold haptic (5 min)

RED: `python -m pytest tests/test_plan_b.py -v` currently fails (stubs have no `Combo`).

Replace entire `firmware/plan_b/combo_b1_heuristic_haptic.py` with:

```python
"""B1 safe — P0 heuristic perception + S0 threshold haptic. No weights needed."""
import math

NAME = "b1_safe"
DESCRIPTION = "heuristic 3-12Hz peak + fixed-duty haptic; runs with no baked weights"
PERCEPTION = "P0_heuristic"
SUPPRESSION = "S0_threshold_haptic"
GATE_OK = True

HEURISTIC_LO_HZ = 3.0
HEURISTIC_HI_HZ = 12.0
HEURISTIC_MAG_THRESHOLD = 1.2
LRA_DUTY_ON = 512
LRA_DUTY_OFF = 0


class Combo:
    def __init__(self, fs: float = 100.0):
        from common.fft import FFTProcessor
        self.fs = fs
        self._fft = FFTProcessor(num_samples=128)

    def _heuristic(self, window):
        signal = [0.0] * len(window)
        for i, row in enumerate(window):
            signal[i] = math.sqrt(row[0] ** 2 + row[1] ** 2 + row[2] ** 2)
        freq, mag = self._fft.process_data(signal, self.fs)
        if HEURISTIC_LO_HZ <= freq <= HEURISTIC_HI_HZ and mag > HEURISTIC_MAG_THRESHOLD:
            return "kinetic", min(1.0, mag / (HEURISTIC_MAG_THRESHOLD * 2.0))
        return "rest", 1.0

    def process(self, frame: dict) -> dict:
        window = frame.get("window") or [[0.0, 0.0, 1.0]] * 128
        label, conf = self._heuristic(window)
        duty = LRA_DUTY_ON if label != "rest" else LRA_DUTY_OFF
        frame["label"] = label
        frame["confidence"] = conf
        frame["suppress_duty"] = duty
        frame["plan_b"] = NAME
        return frame

    def process_sample(self, x: float, y: float, z: float) -> int:
        mag = math.sqrt(x * x + y * y + z * z) - 1.0
        return LRA_DUTY_ON if mag > 0.2 else LRA_DUTY_OFF
```

Verify (expected: registry test still fails on other combos, but `python -c` below prints `b1_safe kinetic-or-rest`):

```
python -c "import sys; sys.path.insert(0,'firmware'); from plan_b.combo_b1_heuristic_haptic import Combo; c=Combo(); print(c.process({'window':[[0.1,0.2,0.9]]*128})['plan_b'])"
python -m pytest tests/test_plan_b.py -v
```

Expected: still RED overall (other combos missing) — that is correct. Commit: `git add firmware/plan_b/combo_b1_heuristic_haptic.py && git commit -m "add plan_b B1 heuristic-haptic combo"`

### Task 3 — B2 baseline-ml: logreg + threshold haptic (5 min)

Replace entire `firmware/plan_b/combo_b2_logreg_haptic.py` with:

```python
"""B2 baseline-ml — P1 logreg perception + S0 threshold haptic."""
import math

NAME = "b2_baseline_ml"
DESCRIPTION = "15-feat logreg + fixed-duty haptic"
PERCEPTION = "P1_logreg"
SUPPRESSION = "S0_threshold_haptic"
GATE_OK = True

LRA_DUTY_ON = 512
LRA_DUTY_OFF = 0


class Combo:
    def __init__(self, fs: float = 100.0):
        import common.model as model
        import common.scaler as scaler
        import common.logreg as logreg
        import common.feature_extract as feature_extract
        if model.WEIGHTS is None:
            raise RuntimeError("B2 GATE: bake logreg weights (host_scripts/train_classifier.py) first")
        self.fs = fs
        self._model = model
        self._scaler = scaler
        self._logreg = logreg
        self._fe = feature_extract

    def process(self, frame: dict) -> dict:
        window = frame.get("window")
        feats = self._fe.compute(window, fs=self.fs, n=len(window))
        x = self._scaler.apply(feats, self._model.FEATURE_MEAN, self._model.FEATURE_STD)
        _, probs = self._logreg.forward(x, self._model.WEIGHTS, self._model.BIAS)
        idx = self._logreg.argmax(probs)
        label = self._model.CLASSES[idx]
        frame["label"] = label
        frame["confidence"] = probs[idx]
        frame["probs"] = probs
        frame["suppress_duty"] = LRA_DUTY_ON if label not in ("rest", "baseline") else LRA_DUTY_OFF
        frame["plan_b"] = NAME
        return frame

    def process_sample(self, x: float, y: float, z: float) -> int:
        return LRA_DUTY_OFF
```

Verify (expected: raises `RuntimeError: B2 GATE` on this repo because `model.WEIGHTS is None` — that IS the pass condition for the gate; the contract test imports `Combo` fine but `Combo()` raises, so patch the contract test's B2 handling in Task 7 — for now just check the file imports):

```
python -c "import sys; sys.path.insert(0,'firmware'); import plan_b.combo_b2_logreg_haptic as m; print(m.NAME, m.GATE_OK)"
```

Commit: `git add firmware/plan_b/combo_b2_logreg_haptic.py && git commit -m "add plan_b B2 logreg-haptic combo"`

### Task 4 — B3 current-best: DNN + full PLL (5 min)

Replace entire `firmware/plan_b/combo_b3_dnn_pll.py` with:

```python
"""B3 current-best — P2 DNN perception + S1 full PLL chain (reference)."""
import math

NAME = "b3_current_best"
DESCRIPTION = "DNN gate + bandpass/PLL/predictor/anticancel/adaptive-gain"
PERCEPTION = "P2_dnn"
SUPPRESSION = "S1_full_pll"
GATE_OK = True

CONF_THRESH = 0.50


class Combo:
    def __init__(self, fs: float = 100.0, pll_bandwidth: float = 1.0,
                 prediction_ms: float = 15.0, initial_gain: float = 0.5):
        from stages.suppress import SuppressStage
        import common.model_dnn as model
        import common.scaler as scaler
        import common.logreg as logreg
        import common.dnn as dnn
        import common.feature_extract as feature_extract
        if model.W1 is None or model.W2 is None:
            raise RuntimeError("B3 GATE: bake DNN weights (host_scripts/train_dnn_parkinsons.py) first")
        self.fs = fs
        self._sup = SuppressStage(fs=fs, pll_bandwidth=pll_bandwidth,
                                  prediction_ms=prediction_ms, initial_gain=initial_gain)
        self._model, self._scaler, self._logreg = model, scaler, logreg
        self._dnn, self._fe = dnn, feature_extract

    def process(self, frame: dict) -> dict:
        window = frame.get("window")
        feats = self._fe.compute(window, fs=self.fs, n=len(window))
        x = self._scaler.apply(feats, self._model.FEATURE_MEAN, self._model.FEATURE_STD)
        _, probs = self._dnn.forward(x, self._model.W1, self._model.B1,
                                     self._model.W2, self._model.B2)
        idx = self._logreg.argmax(probs)
        frame["label"] = self._model.CLASSES[idx]
        frame["confidence"] = probs[idx]
        frame["probs"] = probs
        frame = self._sup.process(frame)
        if frame.get("label") in ("rest", "baseline") or frame.get("confidence", 0.0) < CONF_THRESH:
            frame["suppress_duty"] = 0
        frame["plan_b"] = NAME
        return frame

    def process_sample(self, x: float, y: float, z: float) -> int:
        return int(self._sup.process_sample(x, y, z))
```

Verify: `python -c "import sys; sys.path.insert(0,'firmware'); import plan_b.combo_b3_dnn_pll as m; print(m.NAME)"` prints `b3_current_best`. Commit: `git add firmware/plan_b/combo_b3_dnn_pll.py && git commit -m "add plan_b B3 dnn-pll combo"`

### Task 5 — B4 pll-only + B5 fixed-gain (5 min)

5a. Replace entire `firmware/plan_b/combo_b4_pll_only.py` with:

```python
"""B4 pll-only — no classifier; pure real-time PLL loop (logging-only label)."""
import math

NAME = "b4_pll_only"
DESCRIPTION = "bandpass/PLL/predictor/anticancel/adaptive-gain, no classifier dependency"
PERCEPTION = "none"
SUPPRESSION = "S1_full_pll"
GATE_OK = True


class Combo:
    def __init__(self, fs: float = 100.0, pll_bandwidth: float = 1.0,
                 prediction_ms: float = 15.0, initial_gain: float = 0.5):
        from stages.suppress import SuppressStage
        self._sup = SuppressStage(fs=fs, pll_bandwidth=pll_bandwidth,
                                  prediction_ms=prediction_ms, initial_gain=initial_gain)

    def process(self, frame: dict) -> dict:
        frame = self._sup.process(frame)
        frame["label"] = frame.get("label", "unknown")
        frame["plan_b"] = NAME
        return frame

    def process_sample(self, x: float, y: float, z: float) -> int:
        return int(self._sup.process_sample(x, y, z))
```

5b. Replace entire `firmware/plan_b/combo_b5_dnn_fixed_gain.py` with:

```python
"""B5 fixed-gain — P2 DNN gate + S2 fixed-gain PLL (no adaptation)."""
import math

NAME = "b5_fixed_gain"
DESCRIPTION = "DNN gate + PLL with fixed gain 0.5 (no AdaptiveGain.update)"
PERCEPTION = "P2_dnn_gated"
SUPPRESSION = "S2_fixed_gain_pll"
GATE_OK = True
FIXED_GAIN = 0.5
CONF_THRESH = 0.50


class Combo:
    def __init__(self, fs: float = 100.0, pll_bandwidth: float = 1.0,
                 prediction_ms: float = 15.0):
        from common.bandpass import BandpassFilter
        from common.pll import PLL
        from common.predictor import PhasePredictor
        from common.anticancel import AntiPhaseGenerator
        import common.model_dnn as model
        import common.scaler as scaler
        import common.logreg as logreg
        import common.dnn as dnn
        import common.feature_extract as feature_extract
        if model.W1 is None or model.W2 is None:
            raise RuntimeError("B5 GATE: bake DNN weights first")
        self.fs = fs
        self._bp = BandpassFilter(fs=fs, low_hz=3.0, high_hz=12.0)
        self._pll = PLL(fs=fs, center_freq=6.0, bandwidth=pll_bandwidth)
        self._pred = PhasePredictor(fs=fs, prediction_ms=prediction_ms)
        self._gen = AntiPhaseGenerator(max_duty=1023)
        self._model, self._scaler, self._logreg = model, scaler, logreg
        self._dnn, self._fe = dnn, feature_extract

    def process(self, frame: dict) -> dict:
        window = frame.get("window")
        feats = self._fe.compute(window, fs=self.fs, n=len(window))
        x = self._scaler.apply(feats, self._model.FEATURE_MEAN, self._model.FEATURE_STD)
        _, probs = self._dnn.forward(x, self._model.W1, self._model.B1,
                                     self._model.W2, self._model.B2)
        idx = self._logreg.argmax(probs)
        frame["label"] = self._model.CLASSES[idx]
        frame["confidence"] = probs[idx]
        if frame["label"] in ("rest", "baseline") or frame["confidence"] < CONF_THRESH:
            frame["suppress_duty"] = 0
        else:
            row = window[len(window) // 2]
            duty = self.process_sample(float(row[0]), float(row[1]), float(row[2]))
            frame["suppress_duty"] = duty
        frame["plan_b"] = NAME
        return frame

    def process_sample(self, x: float, y: float, z: float) -> int:
        mag = math.sqrt(x * x + y * y + z * z) - 1.0
        filt = self._bp.process_sample(mag)
        phase, freq, amp, locked = self._pll.process_sample(filt)
        pred = self._pred.predict(phase, freq)
        return int(self._gen.compute_duty(pred, amp, gain=FIXED_GAIN))
```

NOTE: `PLL.process_sample` return arity above assumes `(phase, freq, amp, locked)` — if the real signature differs, use whatever `stages/suppress.py::process_sample` calls it with (read that function first, match it exactly, do not invent).

Verify: both files import. Commit: `git add firmware/plan_b/combo_b4_pll_only.py firmware/plan_b/combo_b5_dnn_fixed_gain.py && git commit -m "add plan_b B4 pll-only and B5 fixed-gain combos"`

### Task 6 — B6 cnn-future (quarantined) + runner (5 min)

6a. Replace entire `firmware/plan_b/combo_b6_cnn_pll.py` with:

```python
"""B6 cnn-future — QUARANTINED. Host bench only until CNN beats DNN gate."""
NAME = "b6_cnn_future"
DESCRIPTION = "TinyCNN spectra classifier + full PLL (host-only until gate passes)"
PERCEPTION = "P3_cnn1d"
SUPPRESSION = "S1_full_pll"
GATE_OK = False


class Combo:
    def __init__(self, fs: float = 100.0):
        self.fs = fs

    def process(self, frame: dict) -> dict:
        raise RuntimeError("B6 GATE FAIL: cnn CV 0.597 < baked-mlp 0.750; use host bench only")

    def process_sample(self, x: float, y: float, z: float) -> int:
        return 0
```

6b. Create `firmware/plan_b/runner.py` with:

```python
"""Select and run a plan_b combo by name with fallback chain."""
import importlib
from plan_b import PLAN_B_REGISTRY, FALLBACK_CHAIN


def load(name: str):
    mod = importlib.import_module(PLAN_B_REGISTRY[name])
    if not mod.GATE_OK:
        raise RuntimeError("plan_b %s quarantined: %s" % (name, mod.DESCRIPTION))
    return mod.Combo()


def run_with_fallback(frame: dict, chain=None):
    chain = chain or list(FALLBACK_CHAIN)
    last_err = None
    for name in chain:
        try:
            combo = load(name)
            return combo.process(frame)
        except RuntimeError as e:
            last_err = e
            continue
    raise RuntimeError("all plan_b combos failed: %s" % last_err)
```

Verify: `python -m pytest tests/test_plan_b.py -v` — expected: B1/B4/B6 pass; B2/B3/B5 raise GATE RuntimeError on `Combo()` because weights are unbaked on a fresh clone. That is the honest signal. Commit: `git add firmware/plan_b/combo_b6_cnn_pll.py firmware/plan_b/runner.py && git commit -m "add plan_b B6 quarantine and fallback runner"`

### Task 7 — fix contract test for unbaked weights + full suite GREEN (5 min)

Rewrite the middle of `tests/test_plan_b.py::test_each_combo_contract` so weight-gated combos are expected to raise:

```python
def test_each_combo_contract():
    import pytest
    for name in PLAN_B_REGISTRY:
        mod = _load(name)
        assert isinstance(mod.NAME, str)
        assert isinstance(mod.DESCRIPTION, str)
        assert isinstance(mod.GATE_OK, bool)
        if name in ("b2_baseline_ml", "b3_current_best", "b5_fixed_gain"):
            try:
                mod.Combo(fs=100.0)
            except RuntimeError as e:
                assert "GATE" in str(e)
                continue
        combo = mod.Combo(fs=100.0)
        duty = combo.process_sample(0.1, 0.2, 0.9)
        assert isinstance(duty, int) and 0 <= duty <= 1023
        frame = {"window": [[0.1, 0.2, 0.9]] * 128, "x": 0.1, "y": 0.2, "z": 0.9}
        out = combo.process(dict(frame))
        assert "plan_b" in out and out["plan_b"] == mod.NAME
        assert "suppress_duty" in out
```

Verify (expected: all pass):

```
python -m pytest tests/test_plan_b.py -v
python -m pytest tests/ -v
```

Expected: `test_plan_b.py` 3 passed; full suite no new failures vs. pre-change baseline. Commit: `git add tests/test_plan_b.py && git commit -m "tolerate unbaked-weight gates in plan_b tests"`

### Task 8 — host benchmark `host_scripts/bench_plan_b.py` (5 min)

Create `host_scripts/bench_plan_b.py` (host-only: numpy/sklearn allowed; MUST NOT import `firmware/`):

```python
"""bench_plan_b.py — score plan_b combos on cached windows (host only).

Usage:
    python host_scripts/bench_plan_b.py
    python host_scripts/bench_plan_b.py --cache host_scripts/parkinsons_windows.npz
"""
import argparse, os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from train_classifier import extract_features, fmt_list  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "parkinsons_windows.npz"))
    args = ap.parse_args()
    if not os.path.exists(args.cache):
        print("no cache at %s; run parkinsons_windows.py first" % args.cache)
        return 2
    z = np.load(args.cache, allow_pickle=True)
    Xw, y = z["Xw"], z["y"]
    print("combos: b1_heuristic b2_logreg b3_dnn b4_naive_pll_proxy b5_gated b6_cnn_proxy")
    print("windows: %d classes: %s" % (len(y), sorted(set(y.tolist()))))
    X = np.array([extract_features(w) for w in Xw])
    print("feat_mean[0:3] = %s" % fmt_list(X.mean(axis=0)[:3]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Verify (expected: either scores print or clean `no cache` message, exit 2 when cache absent):

```
python host_scripts/bench_plan_b.py
```

Commit: `git add host_scripts/bench_plan_b.py && git commit -m "add plan_b host benchmark"`

### Task 9 — `firmware/plan_b/README.md` + final validation (5 min)

Create `firmware/plan_b/README.md`:

```
# plan_b — fallback algorithm combos

Six thin combos (wiring only, DSP math lives in common/* and stages/*):

- b1_safe: heuristic + threshold haptic (no weights)
- b2_baseline_ml: logreg + haptic (needs baked model.py)
- b3_current_best: DNN + full PLL (needs baked model_dnn.py)
- b4_pll_only: PLL only, no classifier
- b5_fixed_gain: DNN gate + fixed-gain PLL
- b6_cnn_future: QUARANTINED host-only (cnn CV 0.597 < 0.750)

Select: from plan_b.runner import load, run_with_fallback
Fallback chain: b3 -> b5 -> b2 -> b4 -> b1 (b6 never auto-selected).

Rules: no numpy in firmware/; feature order = train_classifier.extract_features;
bake gates hold — no weights enter common/ without beating baseline on CV.
```

Final validation (expected: all GREEN, no regressions):

```
python -m pytest tests/ -v
git status --short
```

Commit: `git add firmware/plan_b/README.md && git commit -m "add plan_b readme"`

## Tests / validation

- Per-task TDD: test written first in Task 1, RED verified (`ModuleNotFoundError`), each combo turns its slice GREEN, commit per task.
- Contract: every combo exposes `NAME/DESCRIPTION/PERCEPTION/SUPPRESSION/GATE_OK` + `Combo.process/process_sample`; duty always int 0..1023; `process()` always sets `frame["plan_b"]` and `frame["suppress_duty"]`.
- Gate honesty: B2/B3/B5 raise `RuntimeError("...GATE...")` when weights unbaked; B6 always raises on device. Test asserts the raise, never works around it.
- Regression: `python -m pytest tests/ -v` must show zero new failures vs. baseline from Task 0.
- Host bench: `python host_scripts/bench_plan_b.py` exits 0 with cache, 2 with clean message without.

## Risks, tradeoffs, and open questions

- Risk: `PLL.process_sample` return arity in Task 5b is guessed from `suppress.py` call-site — implementer MUST read `firmware/stages/suppress.py::process_sample` and `firmware/common/pll.py` before writing B5; if the signature is `(phase, freq)` only, take amplitude from the bandpassed envelope instead. Do not invent parameters.
- Risk: `FFTProcessor.process_data` signature assumed `(signal, fs) -> (freq, mag)` from `classify.py` — verified in tree, but if `common/fft.py` differs from `stages/fft.py`, import the same one `classify.py` uses.
- Tradeoff: six combos deliberately omit the full 4x4 cross product (16). Full matrix doubles test/bench cost for pairs nobody will flash (e.g. CNN + open-loop). If a missing pair is later needed, add it as B7 following the same template — do not refactor the registry.
- Tradeoff: combos compose rather than fork DSP code (DRY) — a bug fix in `common/pll.py` fixes all combos at once, but a breaking change there breaks all six. The contract test is the tripwire.
- Open: should `runner.run_with_fallback` also consult `frame["confidence"]`/`quality` flags before stepping down the chain, or only catch `RuntimeError`? Current plan catches errors only (YAGNI); add confidence-based demotion later if pilot data demands it.
- Open: B5 uses F2 split-band (pill 4-6 / ET 6-9) only as gate labels today, not as two parallel PLLs. True dual-PLL (one per band, coherence-gated per `COH_*_THRESH`) is future work — needs pilot-data evidence first.
- Open: exact host-bench metrics (per-combo CV accuracy + suppression proxy) are stubbed to inventory + feature means; full scoring (train logreg/DNN per combo, PLL residual on cached windows) is a follow-up plan once the directory lands.
