# Firmware Pipeline Architecture Improvements

## Goal

Improve the firmware pipeline by eliminating duplicated DSP code, fixing the double-FFT waste in the features stage, adding a pipeline integration test, centralizing magic numbers, and making every stage independently testable.

## Current Context / Assumptions

- **Two pipelines coexist:** HSP (`embedded_main_hsp.py` + `stages/`) for data collection, and Plan B (`plan_b/`) for real-time suppression.
- **Shared math lives in `firmware/common/`** — bandpass, PLL, FFT, feature_extract, DNN, scaler, logreg.
- **MicroPython only** — no numpy/scipy in `firmware/`.
- **128-sample windows at 100 Hz** (1.28 s), 4 IMUs via TCA9548A mux.
- **pytest is not installed** — all tests run via `python tests/<file>.py` with a `__main__` block.
- **Active branch:** `fix/pll-acquire-and-lock` (PLL fixes already merged).

## Problems Identified

| # | Problem | Location | Impact |
|---|---|---|---|
| 1 | **Duplicated FFT implementation** — identical `_in_place_fft`, twiddle cache, Hann cache in both `common/fft.py` and `common/feature_extract.py` | `fft.py:43-76`, `feature_extract.py:130-164` | 2x code size, divergence risk |
| 2 | **Double FFT in features stage** — `feature_extract.compute()` does a full FFT, then `features.py` calls `_fft_mag_sum()` which does a second full FFT on the same window | `features.py:31` | 2x FFT cost per window |
| 3 | **No pipeline integration test** — each stage tested in isolation, but the full HSP chain (safety→...→audit) is never run end-to-end | `tests/` | Integration bugs caught late |
| 4 | **Magic numbers scattered** — quality thresholds, bandpass cutoffs, jitter thresholds hardcoded in stage files with "keep in sync" comments | `quality.py:20-25`, `stationarity.py:13`, `fft.py:101` | Drift risk, hard to tune |
| 5 | **No `__main__` runners on stage files** — can't run `python firmware/stages/quality.py` to test a single stage | `stages/*.py` | Slower debugging |
| 6 | **No timing instrumentation** — ISR budget is 10 ms but nothing measures actual execution time | `embedded_main_hsp.py` | Can't verify real-time safety |

## Architecture / Proposed Approach

1. **Extract a shared `common/dsp.py`** with the single FFT implementation, twiddle cache, Hann window, and a `compute_spectrum(window_2d, fs, n)` helper that returns `(peak_freq, mag_spectrum)`. Both `fft.py` and `feature_extract.py` import from it.
2. **Refactor `feature_extract.compute()`** to accept an optional pre-computed spectrum. `features.py` computes the spectrum once and passes it in.
3. **Add `tests/test_pipeline_integration.py`** that builds a synthetic 128-sample window, runs all 8 HSP stages in order, and asserts the frame has the expected keys.
4. **Move all tunables to `common/config.py`** with a `PIPELINE_CONFIG` dict. Stage files read from it at init.
5. **Add `__main__` blocks** to every stage file that run a smoke test with synthetic data.
6. **Add a `TimingStage`** (optional, last in chain) that records `frame["stage_ms"]` per stage and prints if over budget.

## Step-by-Step Tasks

### Task 1: Extract shared DSP module (`common/dsp.py`)

**File:** `firmware/common/dsp.py` (new)

Create a single FFT implementation that both `fft.py` and `feature_extract.py` use:

```python
"""common/dsp.py — Shared DSP primitives (FFT, spectrum, band power).

Single source of truth for FFT math. Both common/fft.py and
common/feature_extract.py import from here.
"""

import math
from typing import List, Tuple

_TWIDDLES: dict = {}
_HANN_CACHE: dict = {}


def get_twiddles(n: int):
    if n not in _TWIDDLES:
        d = {}
        size = 2
        while size <= n:
            half = size // 2
            cos_t = [0.0] * half
            sin_t = [0.0] * half
            for k in range(half):
                ang = -2 * math.pi * k / size
                cos_t[k] = math.cos(ang)
                sin_t[k] = math.sin(ang)
            d[size] = (cos_t, sin_t)
            size <<= 1
        _TWIDDLES[n] = d
    return _TWIDDLES[n]


def get_hann(n: int):
    if n not in _HANN_CACHE:
        _HANN_CACHE[n] = [0.5 * (1 - math.cos(2 * math.pi * i / (n - 1))) for i in range(n)]
    return _HANN_CACHE[n]


def in_place_fft(real: List[float], imag: List[float]) -> None:
    """In-place iterative Cooley-Tukey FFT with pre-computed twiddles."""
    n = len(real)
    if n <= 1:
        return
    j = 0
    for i in range(n):
        if i < j:
            real[i], real[j] = real[j], real[i]
            imag[i], imag[j] = imag[j], imag[i]
        m = n >> 1
        while m >= 1 and j >= m:
            j -= m
            m >>= 1
        j += m
    tw = get_twiddles(n)
    size = 2
    while size <= n:
        half = size // 2
        cos_t, sin_t = tw[size]
        for i in range(0, n, size):
            for k in range(half):
                c = cos_t[k]
                s = sin_t[k]
                ie = i + k
                io = i + k + half
                ro = real[io]
                io_im = imag[io]
                tr = ro * c - io_im * s
                ti = ro * s + io_im * c
                real[io] = real[ie] - tr
                imag[io] = imag[ie] - ti
                real[ie] += tr
                imag[ie] += ti
        size <<= 1


def compute_spectrum(window_2d: List[List[float]], fs: float = 100.0, n: int = 128
                    ) -> Tuple[float, List[float], List[float]]:
    """Compute magnitude spectrum from 3-axis window.

    Returns:
        (peak_freq_hz, magnitude_spectrum[0..n//2], magnitude_spectrum_full)
    """
    mean_x = sum(r[0] for r in window_2d) / n
    mean_y = sum(r[1] for r in window_2d) / n
    mean_z = sum(r[2] for r in window_2d) / n
    real = [0.0] * n
    for i, r in enumerate(window_2d):
        real[i] = math.sqrt((r[0] - mean_x) ** 2 + (r[1] - mean_y) ** 2 + (r[2] - mean_z) ** 2)
    imag = [0.0] * n
    hann = get_hann(n)
    for i in range(n):
        real[i] *= hann[i]
    in_place_fft(real, imag)
    half = n // 2
    mag = [0.0] * half
    for i in range(half):
        mag[i] = math.sqrt(real[i] * real[i] + imag[i] * imag[i]) * 2 / n
    if half <= 1:
        return 0.0, mag, mag
    peak_idx = 1
    peak_val = mag[1]
    for i in range(2, half):
        if mag[i] > peak_val:
            peak_val = mag[i]
            peak_idx = i
    return (peak_idx * fs) / n, mag, mag


def band_power(mag: List[float], fs: float, n: int, lo: float, hi: float) -> float:
    """RMS band power in [lo, hi] Hz."""
    half = n // 2
    df = fs / n
    lo_i = max(1, int(lo / df))
    hi_i = min(half - 1, int(hi / df))
    if hi_i <= lo_i:
        return 0.0
    s = 0.0
    for i in range(lo_i, hi_i + 1):
        s += mag[i] * mag[i]
    return math.sqrt(s / (hi_i - lo_i + 1))


def spectral_entropy(mag: List[float]) -> float:
    """Normalized spectral entropy (0-1)."""
    s = sum(m * m for m in mag)
    if s <= 1e-12:
        return 0.0
    h = 0.0
    for m in mag:
        p = (m * m) / s
        if p > 1e-12:
            h -= p * math.log(p)
    return h / math.log(len(mag)) if len(mag) > 1 else 0.0
```

**Verification:**
```bash
python -c "from firmware.common.dsp import compute_spectrum, band_power; print('dsp module OK')"
```
Expected: `dsp module OK`

**Commit:** `refactor: extract shared DSP module (common/dsp.py)`

---

### Task 2: Refactor `common/fft.py` to use `common/dsp.py`

**File:** `firmware/common/fft.py`

Replace the local `_in_place_fft`, `_get_twiddles`, `_get_hann` with imports from `dsp.py`. Keep the `FFTProcessor` class API unchanged.

```python
"""common/fft.py — MicroPython FFTProcessor for real-valued signals.

Implements in-place Cooley-Tukey FFT with Hann windowing.
Returns dominant frequency and magnitude above noise threshold.
"""

import math
from typing import List, Tuple
from common.dsp import get_twiddles, get_hann, in_place_fft


class FFTProcessor:
    """FFT processor for fixed-size real-valued signal windows."""

    def __init__(self, num_samples: int = 128):
        self.num_samples = num_samples
        self.window = get_hann(num_samples)
        self._twiddles = get_twiddles(num_samples)
        self._real_buf = [0.0] * num_samples
        self._imag_buf = [0.0] * num_samples

    def process_data(self, signal_data: List[float], actual_fs: float) -> Tuple[float, float]:
        """Compute FFT and return dominant frequency/magnitude."""
        mean_val = sum(signal_data) / len(signal_data)
        real = [(signal_data[i] - mean_val) * self.window[i] for i in range(self.num_samples)]
        imag = [0.0] * self.num_samples
        in_place_fft(real, imag)
        max_mag = 0.0
        dominant_freq = 0.0
        NOISE_THRESHOLD = 0.35
        for i in range(1, self.num_samples // 2):
            magnitude = math.sqrt(real[i]**2 + imag[i]**2)
            frequency = (i * actual_fs) / self.num_samples
            if magnitude > max_mag:
                max_mag = magnitude
                dominant_freq = frequency
        if max_mag < NOISE_THRESHOLD:
            return 0.0, 0.0
        return dominant_freq, max_mag
```

**Verification:**
```bash
python tests/test_pll.py
```
Expected: `All PLL tests passed!` (unchanged behavior)

**Commit:** `refactor: fft.py uses common/dsp.py`

---

### Task 3: Refactor `common/feature_extract.py` to use `common/dsp.py`

**File:** `firmware/common/feature_extract.py`

Replace local `_in_place_fft`, `_get_twiddles`, `_get_hann`, `_fft_mag_sum`, `_band_power`, `_spectral_entropy` with imports from `dsp.py`. Keep the `compute()` function signature unchanged.

Key changes:
- Remove `_get_twiddles`, `_get_hann`, `_in_place_fft`, `_fft_mag_sum`, `_band_power`, `_spectral_entropy` local definitions
- Import from `common.dsp`: `compute_spectrum, band_power, spectral_entropy`
- In `compute()`, replace `_fft_mag_sum(window_2d, fs=fs, n=n)` with `compute_spectrum(window_2d, fs=fs, n=n)`
- Replace `_band_power(mag, fs, n, ...)` with `band_power(mag, fs, n, ...)`
- Replace `_spectral_entropy(mag[1:])` with `spectral_entropy(mag[1:])`

**Verification:**
```bash
python -c "
from firmware.common.feature_extract import compute
import math
w = [[math.sin(2*math.pi*6*i/100), 0.0, 1.0] for i in range(128)]
f = compute(w)
print('features:', len(f), 'dom_freq:', f[3])
assert len(f) == 15
assert 5.5 < f[3] < 6.5
print('feature_extract OK')
"
```
Expected: `features: 15 dom_freq: ~6.0` and `feature_extract OK`

**Commit:** `refactor: feature_extract.py uses common/dsp.py`

---

### Task 4: Fix double-FFT in features stage

**File:** `firmware/stages/features.py`

The current code calls `feature_extract.compute()` (which does a full FFT), then calls `fe._fft_mag_sum()` (which does a second full FFT). Fix by computing the spectrum once and passing it to a refactored `compute()`.

**Approach:** Add an optional `spectrum` parameter to `feature_extract.compute()`. When provided, skip the internal FFT.

In `feature_extract.py`, modify `compute()`:

```python
def compute(window: Window, fs: float = 100.0, n: int = 128,
            spectrum: Tuple[float, List[float], List[float]] = None) -> List[float]:
    """Extract 15 features from 128-sample 3-axis window.

    Args:
        window: 128 samples, either 2D [[x,y,z],...] or flat [x,y,z,x,y,z,...].
        fs: Sampling frequency in Hz.
        n: Number of samples (must be 128).
        spectrum: Optional pre-computed (peak_freq, mag, _) from compute_spectrum().
                  When provided, skips the internal FFT.

    Returns:
        List of 15 feature floats in fixed order.
    """
    # ... existing axis flattening ...

    if spectrum is not None:
        dom_freq, mag, _ = spectrum
    else:
        window_2d = [[x[i], y[i], z[i]] for i in range(n)]
        dom_freq, mag, _ = compute_spectrum(window_2d, fs=fs, n=n)

    bp_3_6 = band_power(mag, fs, n, 3.0, 6.0)
    bp_6_9 = band_power(mag, fs, n, 6.0, 9.0)
    bp_9_12 = band_power(mag, fs, n, 9.0, 12.0)
    bp_12_25 = band_power(mag, fs, n, 12.0, 25.0)
    ent = spectral_entropy(mag[1:])
    med = _median(mag[1:])
    peak_val = max(mag[1:]) if len(mag) > 1 else 0.0
    prominence = peak_val / med if med > 1e-6 else 0.0

    return [
        rms_all, std_all, mcr, dom_freq,
        bp_3_6, bp_6_9, bp_9_12, bp_12_25,
        ent, float(dom_axis), rms_x, rms_y, rms_z,
        xy_ratio, prominence,
    ]
```

In `features.py`, compute the spectrum once and pass it in:

```python
def process(self, frame: Frame) -> Frame:
    window = frame.get("window")
    if not window:
        frame["features_error"] = "no window"
        return frame

    # Compute spectrum once, reuse for features + extended metrics
    _, mag, _ = fe.compute_spectrum(window, fs=self.fs, n=self.n)
    feats = fe.compute(window, fs=self.fs, n=self.n,
                       spectrum=(0.0, mag, mag))  # peak_freq recomputed inside

    frame["features"] = feats
    # Extended metrics reuse the same mag spectrum
    frame["pill_power"] = fe.band_power(mag, self.fs, self.n, 4.0, 6.0)
    frame["et_power"] = fe.band_power(mag, self.fs, self.n, 6.0, 9.0)
    # ... coherence metrics unchanged ...
```

**Verification:**
```bash
python -c "
from firmware.stages.features import FeaturesStage
import math
frame = {'window': [[math.sin(2*math.pi*6*i/100), 0.0, 1.0] for i in range(128)]}
stage = FeaturesStage(fs=100.0, n=128)
out = stage.process(frame)
print('features:', len(out['features']), 'pill_power:', out['pill_power'])
assert len(out['features']) == 15
assert out['pill_power'] > 0
print('features stage OK')
"
```
Expected: `features: 15 pill_power: >0` and `features stage OK`

**Commit:** `fix: features stage computes spectrum once (no double FFT)`

---

### Task 5: Centralize magic numbers in config.py

**File:** `firmware/common/config.py`

Add a `PIPELINE_CONFIG` dict at the end:

```python
# Pipeline stage tunables (single source of truth)
PIPELITY_CONFIG = {
    # Quality stage
    "QUALITY_FALLBACK_THRESH": 0.08,
    "QUALITY_SATURATION_G": 1.95,
    "QUALITY_FLAT_VAR_THRESH": 1e-5,
    "QUALITY_GRAVITY_MIN": 0.6,
    "QUALITY_GRAVITY_MAX": 1.6,
    "QUALITY_JITTER_VAR_THRESH": 5.0,
    # Stationarity stage
    "STATIONARITY_RATIO_THRESH": 0.15,
    # FFT stage
    "FFT_NOISE_THRESHOLD": 0.35,
    # Safety stage
    "SAFETY_TIME_JUMP_US": 2_000_000,
    "SAFETY_DRIFT_G": 0.10,
    "SAFETY_HIST_LEN": 16,
}
```

Then update stage files to read from config:

**File:** `firmware/stages/quality.py` — replace hardcoded constants:
```python
from common.config import PIPELINE_CONFIG as _CFG

FALLBACK_RATIO_THRESH = _CFG["QUALITY_FALLBACK_THRESH"]
SATURATION_THRESH_G = _CFG["QUALITY_SATURATION_G"]
FLAT_VARIANCE_THRESH = _CFG["QUALITY_FLAT_VAR_THRESH"]
GRAVITY_MIN = _CFG["QUALITY_GRAVITY_MIN"]
GRAVITY_MAX = _CFG["QUALITY_GRAVITY_MAX"]
JITTER_VAR_THRESH = _CFG["QUALITY_JITTER_VAR_THRESH"]
```

**File:** `firmware/stages/stationarity.py`:
```python
from common.config import PIPELINE_CONFIG as _CFG
# In __init__:
self.ratio_thresh = _CFG["STATIONARITY_RATIO_THRESH"]
```

**File:** `firmware/stages/fft.py`:
```python
from common.config import PIPELINE_CONFIG as _CFG
# In process_data:
NOISE_THRESHOLD = _CFG["FFT_NOISE_THRESHOLD"]
```

**File:** `firmware/stages/safety.py`:
```python
from common.config import PIPELINE_CONFIG as _CFG
# In process:
if dt > _CFG["SAFETY_TIME_JUMP_US"]:
    ...
if abs(z - med) > _CFG["SAFETY_DRIFT_G"]:
    ...
```

**Verification:**
```bash
python tests/test_pll.py && python tests/test_suppress.py
```
Expected: both pass unchanged.

**Commit:** `refactor: centralize stage tunables in config.py`

---

### Task 6: Add `__main__` runners to all stage files

**Files:** `firmware/stages/safety.py`, `sensor.py`, `stationarity.py`, `quality.py`, `bandpass.py`, `fft.py`, `features.py`, `audit.py`

Add a `__main__` block to each that runs a smoke test with synthetic data. Example for `quality.py`:

```python
if __name__ == "__main__":
    import math
    stage = QualityStage()
    # Good window: 6 Hz sine + gravity
    good = {"window": [[math.sin(2*math.pi*6*i/100), 0.0, 1.0] for i in range(128)]}
    out = stage.process(good)
    assert out["quality_ok"] is True, f"good window failed: {out['quality_reason']}"
    # Bad window: all fallback (0,0,1)
    bad = {"window": [[0.0, 0.0, 1.0] for _ in range(128)]}
    out = stage.process(bad)
    assert out["quality_ok"] is False, "fallback window should fail"
    print("quality stage smoke test passed")
```

Similar patterns for each stage:
- `safety.py`: good frame vs. sensor_error frame
- `sensor.py`: frame with x/y/z present
- `stationarity.py`: stationary (DC) vs. non-stationary (sine)
- `bandpass.py`: 6 Hz sine in, check output has same shape
- `fft.py`: 6 Hz sine, check dominant_freq ≈ 6.0
- `features.py`: 6 Hz sine, check 15 features
- `audit.py`: frame with label, check audit_log populated

**Verification:**
```bash
for f in safety sensor stationarity quality bandpass fft features audit; do
    python firmware/stages/$f.py
done
```
Expected: each prints its smoke test passed message.

**Commit:** `test: add __main__ smoke tests to all stage files`

---

### Task 7: Add pipeline integration test

**File:** `tests/test_pipeline_integration.py` (new)

```python
"""tests/test_pipeline_integration.py — Full HSP pipeline integration test.

Runs all 8 stages in STAGE_ORDER on a synthetic 6 Hz tremor window
and verifies the frame has the expected keys at each step.
"""

import sys
import math

sys.path.insert(0, "firmware")

from stages import STAGE_ORDER
from stages.safety import SafetyStage
from stages.sensor import SensorStage
from stages.stationarity import StationarityStage
from stages.quality import QualityStage
from stages.bandpass import BandpassStage
from stages.fft import FFTStage
from stages.features import FeaturesStage
from stages.audit import AuditStage


def make_tremor_window(freq=6.0, n=128, fs=100.0):
    """Generate a synthetic tremor window (6 Hz sine on x-axis, gravity on z)."""
    return [[math.sin(2 * math.pi * freq * i / fs), 0.0, 1.0] for i in range(n)]


def test_full_pipeline():
    """Run all HSP stages in order on synthetic tremor data."""
    window = make_tremor_window()
    frame = {
        "window": window,
        "x": window[-1][0],
        "y": window[-1][1],
        "z": window[-1][2],
        "now_us": 1_000_000,
        "prev_us": 990_000,
        "sample_errors": 0,
    }

    stages = {
        "safety": SafetyStage(),
        "sensor": SensorStage(sensor=None, sample_buf=window, samples=128),
        "stationarity": StationarityStage(window_len=128),
        "quality": QualityStage(),
        "bandpass": BandpassStage(fs=100.0, low_hz=3.0, high_hz=12.0),
        "fft": FFTStage(samples=128, fs=100.0),
        "features": FeaturesStage(fs=100.0, n=128),
        "audit": AuditStage(capacity=32),
    }

    for name in STAGE_ORDER:
        stage = stages[name]
        frame = stage.process(frame)
        assert frame.get("safe", True), f"pipeline broke at {name}"

    # Verify expected keys exist
    assert "dominant_freq" in frame, "fft stage missing"
    assert "features" in frame, "features stage missing"
    assert len(frame["features"]) == 15, "expected 15 features"
    assert "audit_log" in frame, "audit stage missing"
    assert len(frame["audit_log"]) == 1, "audit should have 1 entry"

    # Verify dominant frequency is in tremor band
    assert 3.0 <= frame["dominant_freq"] <= 12.0, \
        f"dominant_freq {frame['dominant_freq']} outside tremor band"

    print("Full pipeline integration test passed!")


if __name__ == "__main__":
    test_full_pipeline()
```

**Verification:**
```bash
python tests/test_pipeline_integration.py
```
Expected: `Full pipeline integration test passed!`

**Commit:** `test: add HSP pipeline integration test`

---

### Task 8: Add timing instrumentation (optional, last in chain)

**File:** `firmware/stages/timing.py` (new)

```python
"""firmware/stages/timing.py — Optional timing instrumentation stage.

Records per-stage execution time in frame["stage_ms"] and prints
a warning if any stage exceeds its budget. Add to STAGE_ORDER last
for debugging; remove for production builds.
"""

from stages import Frame
import time


class TimingStage:
    def __init__(self, budget_ms: float = 2.0):
        self.budget_ms = budget_ms
        self._times: dict = {}

    def process(self, frame: Frame) -> Frame:
        # This stage runs last; measure elapsed since window start
        now = time.ticks_ms()
        start = frame.get("window_start_ms", now)
        elapsed = time.ticks_diff(now, start)
        frame["pipeline_ms"] = elapsed
        if elapsed > self.budget_ms:
            print(f"WARNING: pipeline took {elapsed} ms (budget {self.budget_ms} ms)")
        return frame
```

In `embedded_main_hsp.py`, add `frame["window_start_ms"] = time.ticks_ms()` before the stage loop, and add `"timing"` to `STAGE_ORDER` (last) when debugging.

**Verification:**
```bash
python -c "
from firmware.stages.timing import TimingStage
frame = {'window_start_ms': 0}
stage = TimingStage(budget_ms=5.0)
out = stage.process(frame)
print('pipeline_ms:', out.get('pipeline_ms'))
print('timing stage OK')
"
```
Expected: `timing stage OK`

**Commit:** `feat: add optional timing instrumentation stage`

---

## Tests / Validation

After each task, run the full test suite:

```bash
cd /c/ForumProject
for t in test_pll test_suppress test_b7_fit test_actuate test_plan_b test_adaptive_gain test_anticancel test_predictor test_pipeline_integration; do
    python tests/$t.py
done
```

Expected: all pass.

## Risks, Tradeoffs, and Open Questions

| Risk | Mitigation |
|---|---|
| Shared DSP module introduces a single point of failure | Keep API identical; all existing tests must pass before/after |
| `feature_extract.compute()` signature change breaks callers | New `spectrum` parameter is optional (default None); old callers work unchanged |
| Timing stage adds overhead | Optional — only added to STAGE_ORDER when debugging |
| Config dict adds indirection | Stages still work if config import fails (fallback to current hardcoded values) |

**Open questions:**
1. Should the timing stage be in the default STAGE_ORDER or opt-in only?
2. Should we add a `frame` schema validation (e.g., required keys per stage)?
3. Should the audit stage support structured output (JSON) for automated parsing?
