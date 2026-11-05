# Plan: true Short-Time Fourier Transform (STFT) for the spectral step

## Goal

Replace the single whole-window FFT with a true overlapping Short-Time Fourier Transform (STFT) spectrogram, collapsed back to the existing 15-feature vector so the baked DNN keeps working.

## Current context / assumptions

- Repo root: `C:/ForumProject`. `firmware/` is MicroPython (no numpy/scipy, pure-Python loops only); `host_scripts/` may use numpy/sklearn/torch.
- Today's spectral step is ONE FFT over the whole 128-sample window @ 100 Hz (1.28 s): `firmware/common/fft.py:11` (`class FFTProcessor`, in-place Cooley–Tukey, Hann window, magnitude `* 2 / n`), wrapped by `firmware/stages/fft.py` (`class FFTStage`, honors `frame['skip_fft']`). There is no STFT anywhere: `grep -rni stft firmware/ host_scripts/` returns zero hits (recorded in `docs/slide_review_2026-09-10.md:33`, finding F3). The deck slide claiming "STFT (x2)" is a wrong-term + duplicate bullet.
- Spectral features come from `firmware/common/feature_extract.py:167-215`: `_fft_mag_sum()` (per-axis mean removal → magnitude → Hann → FFT → `mag * 2 / n`, peak search skipping DC) feeds `_band_power()` (RMS power in 3–6 / 6–9 / 9–12 / 12–25 Hz) and `_spectral_entropy()`; `compute()` (`:241-300`) returns the fixed 15-feature order that MUST match `host_scripts/train_classifier.py:146-186` and the baked weights in `firmware/common/model_dnn.py` (16 hidden × 15 feats, 4 classes, already baked — do NOT rebake in this plan).
- Pipeline order is locked by test: `tests/test_dnn_pipeline.py:29-34` asserts `STAGE_ORDER == [safety, sensor, stationarity, quality, bandpass, fft, features, classify, state_machine, actuate, haptic, audit]` (`firmware/stages/__init__.py:28-41`). Any stage rename/reorder MUST update that test in the same commit.
- Wiring: `firmware/embedded_main_hsp.py:115-140` instantiates stages; band cutoffs come from `firmware/common/config.py` (`BANDPASS_LOW_HZ = 3.0`, `BANDPASS_HIGH_HZ = 12.0`); no `USE_STFT`/`STFT_*` constants exist yet.
- Reference params (from `research/research-06-fft-feature-extraction.md:360-390`): Hann window, 50% overlap, tremor_power_over_time = sum of 3–12 Hz magnitudes per frame, dominant_freq_over_time = argmax per frame. That doc uses window 100/hop 50, but our FFT requires power-of-2 frame lengths → use frame 64 / hop 32 (both powers of 2, 50% overlap).
- Prior plan this supersedes: `.hermes/plans/2026-09-10_160000-bandpass-stft-dnn-first.md` (which parked STFT as opt-in). This plan CONFIRMS the opt-in: STFT ships default-OFF behind a flag; single-FFT stays until STFT passes parity + full suite.

## Architecture / proposed approach

Add a pure-Python `STFTProcessor` in `firmware/common/stft.py` that reuses the existing Cooley–Tukey butterfly (copied twiddle/Hann pattern from `firmware/common/fft.py` and `firmware/common/feature_extract.py`, not imported, to keep each module standalone for MicroPython) to build a small magnitude spectrogram (3 frames × 32 bins for 128 samples @ 64-frame/32-hop), then collapse to the SAME 15 features by reusing `_band_power`/`_spectral_entropy` on the time-averaged spectrum so `model_dnn.py` shapes never change. A thin `STFTStage` mirrors `FFTStage`'s frame contract; `config.py` + `embedded_main_hsp.py` select fft-vs-stft, never both.

## Step-by-step tasks

Run all commands from repo root (`C:/ForumProject`). Prefer `uv run python`; fallback `.venv/Scripts/python`.

### Task 0 — Confirm green baseline before touching anything (read-only)

```
uv run python -m pytest tests/test_dnn_pipeline.py tests/test_bandpass.py -v
grep -rni "stft" firmware/ host_scripts/ tests/ | head -n 20
```

Expected: all tests pass (9/9 in `test_dnn_pipeline.py` per prior run); grep returns nothing (confirms no STFT exists yet — you are not duplicating one). If any test is red, STOP and report the failing test name; do not start Task 1 on a red tree.

Commit: no (read-only).

### Task 1 — TDD: write failing `tests/test_stft.py` first, watch it fail

Create exactly this file (copy-paste whole; `sys.path.insert(0, "firmware")` matches existing test convention):

```
"""tests/test_stft.py — overlapping STFT spectrogram (MicroPython-safe)."""
import sys
import math

sys.path.insert(0, "firmware")


def make_sine(freq_hz=6.0, amp=0.6, n=128, fs=100.0):
    return [amp * math.sin(2 * math.pi * freq_hz * i / fs) for i in range(n)]


def test_stft_frame_count_and_bins():
    from common.stft import STFTProcessor
    st = STFTProcessor(num_samples=128, frame_len=64, hop=32, fs=100.0)
    spec = st.spectrogram(make_sine())
    assert len(spec) == 3, len(spec)          # (128-64)//32 + 1
    assert all(len(row) == 32 for row in spec), [len(r) for r in spec]


def test_stft_detects_6hz():
    from common.stft import STFTProcessor
    st = STFTProcessor(num_samples=128, frame_len=64, hop=32, fs=100.0)
    spec = st.spectrogram(make_sine(freq_hz=6.0))
    freqs = st.bin_freqs()
    per_frame_peak = [freqs[max(range(len(r)), key=lambda i: r[i])] for r in spec]
    assert all(abs(f - 6.0) <= 100.0 / 64 + 1e-9 for f in per_frame_peak), per_frame_peak


def test_stft_parity_with_single_fft_on_stationary():
    # Stationary sine: mean STFT band power must be within 20% of single-FFT band power.
    from common.stft import STFTProcessor
    from common.fft import FFTProcessor
    import common.feature_extract as fe
    fs, n = 100.0, 128
    sig = make_sine(freq_hz=6.0, amp=0.6, n=n, fs=fs)
    win2d = [[v, 0.0, 1.0] for v in sig]
    _, mag_single, _ = fe._fft_mag_sum(win2d, fs=fs, n=n)
    ref = fe._band_power(mag_single, fs, n, 3.0, 12.0)
    st = STFTProcessor(num_samples=n, frame_len=64, hop=32, fs=fs)
    mean_mag = st.mean_spectrum(sig)
    got = st.band_power(mean_mag, 3.0, 12.0)
    assert abs(got - ref) / max(ref, 1e-9) < 0.20, (got, ref)


def test_stft_no_numpy_and_fast_enough():
    import time
    import subprocess
    out = subprocess.run(["grep", "-rn", "numpy\\|scipy",
                          "firmware/common/stft.py"],
                         capture_output=True, text=True).stdout
    assert out.strip() == "", out
    from common.stft import STFTProcessor
    st = STFTProcessor(num_samples=128, frame_len=64, hop=32, fs=100.0)
    t0 = time.monotonic()
    st.spectrogram(make_sine())
    assert (time.monotonic() - t0) < 0.050, "host smoke bound 50 ms"


def test_stft_rejects_bad_params():
    from common.stft import STFTProcessor
    for kw in ({"frame_len": 100}, {"hop": 48}, {"frame_len": 256}):
        try:
            STFTProcessor(num_samples=128, hop=32, fs=100.0, **kw)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for %r" % (kw,))
```

Verify red:

```
uv run python -m pytest tests/test_stft.py -v
```

Expected: `ModuleNotFoundError` / collection error on `common.stft` (file does not exist yet — that IS the failing test). Do not proceed until you see red.

Commit: `git add tests/test_stft.py && git commit -m "test(firmware): failing STFT spectrogram tests (RED)"`.

### Task 2 — Implement `firmware/common/stft.py` minimally until Task 1 goes green

Create exactly this file. Design notes for the zero-context implementer: per-frame mean removal (not global) is intentional — it is what makes STFT robust to drift inside the window, unlike `_fft_mag_sum` which removes one global mean; magnitude scaling `* 2 / frame_len` matches `fft.py:104` and `feature_extract.py:192`; twiddle/Hann caches are module-level dicts copied from the existing pattern so the module stays standalone.

```
"""common/stft.py — MicroPython Short-Time Fourier Transform (STFT).

Overlapping Hann-windowed frames -> Cooley-Tukey FFT per frame ->
magnitude spectrogram. No numpy/scipy. Frame/hop must be powers of 2
(the butterfly requires it) and hop must divide (num_samples - frame_len).

Collapse rule (keeps the 15-feature DNN contract): average the magnitude
spectra across time, then apply the same band-power/entropy math as
feature_extract on the mean spectrum.
"""

import math
from typing import List

_TWIDDLES: dict = {}
_HANN_CACHE: dict = {}


def _get_twiddles(n: int):
    if n in _TWIDDLES:
        return _TWIDDLES[n]
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
    return d


def _get_hann(n: int):
    if n in _HANN_CACHE:
        return _HANN_CACHE[n]
    w = [0.5 * (1 - math.cos(2 * math.pi * i / (n - 1))) for i in range(n)]
    _HANN_CACHE[n] = w
    return w


def _is_pow2(v: int) -> bool:
    return v > 0 and (v & (v - 1)) == 0


def _in_place_fft(real: List[float], imag: List[float]) -> None:
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
    tw = _get_twiddles(n)
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


class STFTProcessor:
    """Overlapping STFT over a fixed window. Defaults: 128 samples, 64-frame, 32-hop."""

    def __init__(self, num_samples: int = 128, frame_len: int = 64,
                 hop: int = 32, fs: float = 100.0):
        if not _is_pow2(frame_len):
            raise ValueError("frame_len must be a power of 2, got %r" % (frame_len,))
        if not _is_pow2(hop):
            raise ValueError("hop must be a power of 2, got %r" % (hop,))
        if frame_len > num_samples:
            raise ValueError("frame_len %d > num_samples %d" % (frame_len, num_samples))
        if (num_samples - frame_len) % hop != 0:
            raise ValueError("hop must divide num_samples - frame_len")
        self.num_samples = num_samples
        self.frame_len = frame_len
        self.hop = hop
        self.fs = fs
        self.n_frames = (num_samples - frame_len) // hop + 1
        self.n_bins = frame_len // 2

    def bin_freqs(self) -> List[float]:
        df = self.fs / self.frame_len
        return [i * df for i in range(self.n_bins)]

    def spectrogram(self, signal: List[float]) -> List[List[float]]:
        """Magnitude spectrogram: n_frames rows x n_bins cols. Per-frame mean removed."""
        if len(signal) < self.num_samples:
            raise ValueError("signal len %d < num_samples %d" % (len(signal), self.num_samples))
        hann = _get_hann(self.frame_len)
        out: List[List[float]] = []
        for f in range(self.n_frames):
            seg = signal[f * self.hop: f * self.hop + self.frame_len]
            mu = sum(seg) / self.frame_len
            real = [(seg[i] - mu) * hann[i] for i in range(self.frame_len)]
            imag = [0.0] * self.frame_len
            _in_place_fft(real, imag)
            out.append([math.sqrt(real[i] ** 2 + imag[i] ** 2) * 2 / self.frame_len
                        for i in range(self.n_bins)])
        return out

    def mean_spectrum(self, signal: List[float]) -> List[float]:
        spec = self.spectrogram(signal)
        mean = [0.0] * self.n_bins
        for row in spec:
            for i, v in enumerate(row):
                mean[i] += v
        return [v / self.n_frames for v in mean]

    def band_power(self, mean_mag: List[float], lo: float, hi: float) -> float:
        df = self.fs / self.frame_len
        lo_i = max(1, int(lo / df))
        hi_i = min(self.n_bins - 1, int(hi / df))
        if hi_i <= lo_i:
            return 0.0
        s = 0.0
        for i in range(lo_i, hi_i + 1):
            s += mean_mag[i] * mean_mag[i]
        return math.sqrt(s / (hi_i - lo_i + 1))

    def tremor_power_over_time(self, spec: List[List[float]],
                               lo: float = 3.0, hi: float = 12.0) -> List[float]:
        freqs = self.bin_freqs()
        idx = [i for i, f in enumerate(freqs) if lo <= f <= hi and i >= 1]
        return [sum(row[i] for i in idx) for row in spec]

    def dominant_freq_over_time(self, spec: List[List[float]]) -> List[float]:
        freqs = self.bin_freqs()
        out = []
        for row in spec:
            bi = 1
            bv = row[1] if len(row) > 1 else 0.0
            for i in range(2, len(row)):
                if row[i] > bv:
                    bv = row[i]
                    bi = i
            out.append(freqs[bi])
        return out
```

Verify green:

```
uv run python -m pytest tests/test_stft.py -v
```

Expected: 5/5 pass. If `test_stft_parity_with_single_fft_on_stationary` fails by more than 20%, do NOT loosen the bound — the scaling or mean-removal is wrong; recheck `* 2 / frame_len` and per-frame Hann. If the timing test fails on a slow box, confirm it is host-only slowness (not algorithmic) before touching the 50 ms bound, and note it in the commit message.

Commit: `git add firmware/common/stft.py && git commit -m "feat(firmware): MicroPython STFTProcessor 64-frame/32-hop spectrogram (GREEN)"`.

### Task 3 — TDD: thin `firmware/stages/stft.py` mirroring `FFTStage`'s contract

Write this test addition FIRST (append to `tests/test_stft.py`):

```
def test_stft_stage_contract_mirrors_fft():
    import sys
    sys.path.insert(0, "firmware")
    from stages.stft import STFTStage
    import math
    fs, n = 100.0, 128
    win = [[0.3 * math.sin(2 * math.pi * 6.0 * i / fs), 0.0, 1.0] for i in range(n)]
    st = STFTStage(samples=n, fs=fs)
    f = st.process({"window": [r[:] for r in win]})
    assert 3.0 <= f["dominant_freq"] <= 12.0, f["dominant_freq"]
    assert f["dominant_mag"] > 0 and f["fft_skipped"] is False
    assert len(f["spectrogram"]) == 3 and len(f["spectrogram"][0]) == 32
    g = st.process({"window": [r[:] for r in win], "skip_fft": True})
    assert g["fft_skipped"] is True and g["dominant_freq"] == 0.0
    h = st.process({"window": [[0.0, 0.0, 0.0]] * 10})
    assert h["fft_error"] == "insufficient window"
```

Run to see red (`ImportError: common.stft`-stage missing — expected), then create `firmware/stages/stft.py` (copy-paste):

```
"""firmware/stages/stft.py

STFT stage: overlapping-spectrogram twin of stages/fft.py.
Same frame contract (dominant_freq/dominant_mag/fft_skipped/fft_error,
honors skip_fft) plus frame['spectrogram'] and per-frame tracks for
future onset gating. Magnitude signal = sqrt(x^2+y^2+z^2), same as FFTStage.
"""

import math
from common.stft import STFTProcessor
from stages import Frame


class STFTStage:
    def __init__(self, samples: int = 128, fs: float = 100.0,
                 frame_len: int = 64, hop: int = 32):
        self.proc = STFTProcessor(num_samples=samples, frame_len=frame_len,
                                  hop=hop, fs=fs)
        self.samples = samples
        self.fs = fs

    def _signal_from_window(self, window: list[list[float]]) -> list[float]:
        sig = [0.0] * self.samples
        for i, row in enumerate(window):
            x, y, z = row
            sig[i] = math.sqrt(x * x + y * y + z * z)
        return sig

    def process(self, frame: Frame) -> Frame:
        if frame.get("skip_fft"):
            frame["fft_skipped"] = True
            frame["dominant_freq"] = 0.0
            frame["dominant_mag"] = 0.0
            return frame
        window = frame.get("window")
        if not window or len(window) < self.samples:
            frame["fft_error"] = "insufficient window"
            return frame
        signal = self._signal_from_window(window)
        spec = self.proc.spectrogram(signal)
        mean = self.proc.mean_spectrum(signal)
        freqs = self.proc.bin_freqs()
        bi = 1
        bv = mean[1] if len(mean) > 1 else 0.0
        for i in range(2, len(mean)):
            if mean[i] > bv:
                bv = mean[i]
                bi = i
        frame["spectrogram"] = spec
        frame["dominant_freq"] = freqs[bi]
        frame["dominant_mag"] = bv
        frame["fft_skipped"] = False
        frame["tremor_power_over_time"] = self.proc.tremor_power_over_time(spec)
        frame["dominant_freq_over_time"] = self.proc.dominant_freq_over_time(spec)
        return frame
```

Verify:

```
uv run python -m pytest tests/test_stft.py -v
```

Expected: 6/6 pass.

Commit: `git add firmware/stages/stft.py tests/test_stft.py && git commit -m "feat(firmware): STFTStage with FFTStage-identical frame contract (GREEN)"`.

### Task 4 — Wire selection: `config.py` flags + `embedded_main_hsp.py` chooses fft XOR stft (never both)

Edits (exact strings to add — nothing else in these files changes):

1. `firmware/common/config.py`, append after the `BANDPASS_*` block:

```
# STFT (Short-Time Fourier Transform) selection
USE_STFT = False             # False = single FFT (default, proven); True = overlapping STFT
STFT_FRAME_LEN = 64          # must be power of 2 (freq resolution 100/64 = 1.5625 Hz)
STFT_HOP = 32                # 50% overlap; must divide 128-64
```

2. `firmware/embedded_main_hsp.py`: extend the `common.config` import list with `USE_STFT, STFT_FRAME_LEN, STFT_HOP`; add `from stages.stft import STFTStage`; replace the `"fft": FFTStage(...)` line with:

```
    "fft": (STFTStage(samples=SAMPLES, fs=SAMPLE_RATE_HZ,
                      frame_len=STFT_FRAME_LEN, hop=STFT_HOP)
            if USE_STFT else
            FFTStage(samples=SAMPLES, fs=SAMPLE_RATE_HZ)),
```

3. Update the order-lock test `tests/test_dnn_pipeline.py:29-34` ONLY by comment (the `STAGE_ORDER` list itself does NOT change — the stage is still named `"fft"` either way, so the assert stays green untouched; if you renamed the key to `"stft"` instead, you broke the contract — revert and keep key `"fft"`).

Verify:

```
uv run python -m pytest tests/ -q
grep -rn "numpy\\|scipy" firmware/ --include="*.py" | head -n 5
```

Expected: full suite green (including the untouched `test_stage_order_is_dnn_path`); grep returns nothing. Also smoke both branches:

```
uv run python -c 'import sys; sys.path.insert(0,"firmware"); from stages.fft import FFTStage; from stages.stft import STFTStage; import math; w=[[0.3*math.sin(2*math.pi*6*i/100),0,1.0] for i in range(128)]; a=FFTStage().process({"window":[r[:] for r in w]}); b=STFTStage().process({"window":[r[:] for r in w]}); print("fft:",round(a["dominant_freq"],2),"stft:",round(b["dominant_freq"],2)); assert 3.0<=b["dominant_freq"]<=12.0; print("SELECT-OK")'
```

Expected: `fft: 6.xx  stft: 6.xx` (STFT bin grid is coarser — 1.5625 Hz vs 0.78 Hz — so exact equality is NOT required, only same 3–12 Hz band), then `SELECT-OK`.

Commit: `git add firmware/common/config.py firmware/embedded_main_hsp.py && git commit -m "feat(firmware): USE_STFT selector, fft XOR stft (default off)"`.

### Task 5 — Real-data parity on cached Parkinson's windows (read-only check, no rebake)

Why: synthetic parity (Task 1) is not enough — real windows are resampled from ~22 Hz stamps (`host_scripts/parkinsons_windows.py:31-42`) and content above ~8 Hz is interpolation. Copy-paste:

```
uv run python -c '
import sys, numpy as np; sys.path.insert(0,"firmware"); sys.path.insert(0,"host_scripts")
from parkinsons_windows import load_cache
from common.stft import STFTProcessor
import common.feature_extract as fe
Xw, y, _ = load_cache("host_scripts/parkinsons_windows.npz")
st = STFTProcessor()
import math, random
random.seed(0)
idx = random.sample(range(len(y)), min(200, len(y)))
ratios = []
for i in idx:
    w = Xw[i]
    sig = [float(math.sqrt(r[0]**2+r[1]**2+r[2]**2)) for r in w]
    _, mag1, _ = fe._fft_mag_sum([[float(a),float(b),float(c)] for a,b,c in w])
    ref = fe._band_power(mag1, 100.0, 128, 3.0, 12.0)
    got = st.band_power(st.mean_spectrum(sig), 3.0, 12.0)
    if ref > 1e-9: ratios.append(got/ref)
ratios = np.array(ratios)
print("n=%d median_ratio=%.3f p10=%.3f p90=%.3f" % (len(ratios), float(np.median(ratios)), float(np.percentile(ratios,10)), float(np.percentile(ratios,90))))
assert 0.8 < float(np.median(ratios)) < 1.2, "median outside 20% parity band"
print("REAL-DATA PARITY OK")
' 2>&1 | tail -n 5
```

Expected: `REAL-DATA PARITY OK` with median ratio in [0.8, 1.2]. If the `.npz` cache is missing, build it first: `uv run python host_scripts/parkinsons_windows.py` (expect `cached ... windows`, exit 0 only if > 5000). If parity FAILS: STOP — do NOT paste anything into `model_dnn.py`; the correct follow-up is a separate retrain plan on STFT-averaged features, not a silent reuse. Report the median/p10/p90 numbers.

Commit: no (read-only check).

### Task 6 — Docs: fix the slide STFT claim to match what shipped (docs only, after code green)

In the slide source (note `docs/slide_review_2026-09-10.md:74` Q4 — the `.pptx`/Canva source may not be in repo; do not retype the PDF): delete the duplicate "STFT" bullet; rewrite the survivor as "Spectral analysis: overlapping STFT — 64-sample Hann frames, 32-sample hop (50% overlap), 3 frames per 128-sample window @ 100 Hz → mean spectrum → 15 DNN features". If `USE_STFT` is still `False` (default), append "(gated in, default off; single-FFT path active)" so the deck never overclaims. Leave the 15-feature list and actuation-outputs distinction per findings F3/F4 in `docs/slide_review_2026-09-10.md:33-34`.

Commit: `git add docs/ && git commit -m "docs: arch slide describes real STFT params"`.

## Tests / validation

- TDD per code task: Task 1 test written first and seen RED (`ModuleNotFoundError` on `common.stft`) before Task 2 implementation turns it GREEN; Task 3 stage test RED (`ImportError` on `stages.stft`) before stage implementation turns it GREEN. Each task commits RED then GREEN separately — no combined "tests + impl" commits.
- Commands and expected outputs: `uv run python -m pytest tests/test_stft.py -v` → 5/5 (Task 2), 6/6 (Task 3); `uv run python -m pytest tests/ -q` → full suite green including untouched `test_stage_order_is_dnn_path`; `grep -rn "numpy\\|scipy" firmware/ --include="*.py"` → empty; synthetic SELECT-OK prints both dominants in 3–12 Hz; real-data parity prints median ratio in [0.8, 1.2].
- Contract invariants (checked by tests, not by eye): `STAGE_ORDER` key stays `"fft"` regardless of branch; `skip_fft` / `fft_error` / `fft_skipped` frame keys identical between `FFTStage` and `STFTStage`; 15-feature order untouched so `model_dnn.py` is never rebaked in this plan; `frame_len`/`hop` powers of 2 enforced by constructor `ValueError`.
- Final acceptance: Tasks 0–6 outputs match "Expected" above, `USE_STFT = False` default preserved, deck claims STFT only with the gated-in qualifier.

## Risks, tradeoffs, and open questions

- Risk: coarser frequency grid. 64-sample frames @ 100 Hz give 1.5625 Hz bins vs 0.78 Hz for 128-FFT; pill-rolling 4–6 Hz and ET 6–9 Hz (`config.py` `PILL_BAND_*`/`ET_BAND_*`) sit 1–2 bins apart. Tradeoff accepted for time-localization (3 frames catch onset/offset inside the 1.28 s window that single-FFT smears). Mitigation: band powers average across frames; dominant-freq is read from the MEAN spectrum, never a single frame.
- Risk: compute/RAM on ESP32-DevKitC (classic WROOM-32; 4× MPU6050 already ~4 ms I2C per 10 ms tick). Cost is ~3× 64-FFTs + 96-float spectrogram vs 1× 128-FFT — small in absolute terms (host smoke < 50 ms; device impact unmeasured). Mitigation: default-OFF flag; measure on-device latency before flipping `USE_STFT = True` (that flip is a separate plan with a latency bench).
- Risk: source-data ceiling. Parkinson's windows are interpolated from ~22 Hz stamps, so content above ~8 Hz is suspect; STFT cannot create resolution the source lacks. Bands 9–12/12–25 Hz stay weak by construction — do not tune STFT params to chase them.
- Risk: questionable-taste failure modes this plan explicitly blocks — importing numpy "just for the prototype" (banned by test), renaming the stage key to `"stft"` and silently breaking `STAGE_ORDER` consumers (`embedded_main_hsp.py`, plan_b combos, `test_stage_order_is_dnn_path`), changing `_fft_mag_sum`/`compute()` to call STFT internally (would shift baked-feature distributions — STFT collapses to the same features WITHOUT touching `feature_extract.py`), rebaking `model_dnn.py` on vibes (no rebake without a PASSing bake-gate in a follow-up plan).
- Open Q1: after parity passes, does the team flip `USE_STFT = True` as the new default, or keep single-FFT and use STFT's `tremor_power_over_time` only for future onset gating? This plan ends at default-OFF; the flip needs its own latency + CV bake-gate decision.
- Open Q2: slide source location (`.pptx`/Canva link, `docs/slide_review_2026-09-10.md:74` Q4) — Task 6 cannot land cleanly without it.
- Open Q3: 64/32 vs 32/16 framing (finer time, coarser frequency)? 64/32 chosen to keep 4–6 vs 6–9 Hz separable; revisit only with real-data per-band parity numbers from Task 5.
