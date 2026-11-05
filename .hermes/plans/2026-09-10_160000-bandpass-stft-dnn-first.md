# Plan: back to bandpass → STFT/FFT → DNN first

## Goal

Re-anchor the project on the simplest perception baseline — bandpass → spectral (FFT today, true STFT only if gated in) → DNN classifier — and prove it end-to-end before any PLL-only, CNN, LSTM, or burst-actuation work.

## Current context / assumptions

- Repo root: `C:/ForumProject`. Branch `ASUS` (ahead 12, 14 modified, ~87 untracked at last check). Do NOT commit unless asked; this plan only reads and tests.
- Plan A (full pipeline) is already wired as:
  `safety → sensor → stationarity → quality → bandpass → fft → features → classify (DNN) → state_machine → actuate → haptic → audit`
  Evidence: `firmware/stages/__init__.py:28-41` (`STAGE_ORDER`), `firmware/embedded_main_hsp.py:115-140` (stage wiring), `firmware/plan_a/README.md` (stage order + contracts).
- Actuation path is PLL anti-phase (`firmware/stages/suppress.py`, `firmware/stages/actuate.py` replays the window through `SuppressStage`; `firmware/stages/haptic.py` prefers `frame['suppress_duty']`). The DNN only *supervises* (gates) actuation via `state_machine` + `actuate`. This plan does NOT change actuation — it proves perception first, then leaves actuation parked.
- "STFT" is currently a slide term, not code. `grep -rni stft firmware/ host_scripts/` returns zero hits (documented in `docs/slide_review_2026-09-10.md:33`, finding F3). What actually ships is single-window in-place Cooley–Tukey FFT: `firmware/common/fft.py:11` (`class FFTProcessor`), 128 samples @ 100 Hz = 1.28 s (`firmware/common/config.py:4-7`). The slide (`docs/ถุงมือกันสั่น.pdf` slide 8) says "STFT (x2)" — that is a wrong-term + duplicate bullet.
- Baked DNN weights ALREADY EXIST: `firmware/common/model_dnn.py:18-38` has real `CLASSES`, `FEATURE_MEAN/STD`, `W1/B1/W2/B2` (15 features, 16 hidden, 4 classes). Trainer: `host_scripts/train_dnn_parkinsons.py` (MLP 16-hidden vs logreg, `GATE_MIN_CV = 0.40`, must beat logreg). Feature order contract: `firmware/common/feature_extract.py` output order MUST equal `host_scripts/train_classifier.py:146-186` (`extract_features`). Break this and the baked weights are garbage.
- Reference combo B3 (`firmware/plan_b/combo_b3_dnn_pll.py`) = DNN perception + full PLL suppression, `GATE_OK = True`. Parked: b4/b7 PLL-only (no classifier), b6 CNN quarantined (`GATE_OK = False`, CV 0.597 < 0.750 — do NOT unquarantine in this plan), LSTM/burst = research only (`research/research-06-fft-feature-extraction.md`, `.hermes/plans/2026-09-06_000004-*`).
- Hard rules (from `firmware/plan_a/README.md` + `firmware/plan_b/README.md`): no numpy/scipy in `firmware/` (MicroPython only, pure-Python loops); no weights enter `firmware/common/` without beating baseline on CV (bake gates hold).
- Prior art: `.hermes/plans/2026-09-06_000000-bandpass-fft-dnn-switch.md` (the original bandpass→FFT→DNN switch, 9 tests green). Read it first — this plan is "re-verify that, then decide STFT".

## Architecture / proposed approach

Keep the existing Plan A stage files and `common/` DSP exactly where they are; the only question is whether "spectral" stays single-FFT (recommended default: zero new code, fix the slides) or becomes true overlapping STFT (opt-in experiment behind a flag, host-parity tested). Either way, prove bandpass → spectral → 15 features → DNN forward on synthetic + cached Parkinson's windows with the existing bake-gate before touching suppression, CNN, or docs beyond the one arch bullet.

## Step-by-step tasks

Each task is 2–5 min. Run every command from repo root (`C:/ForumProject`). Prefer `uv run python`; if `uv` is missing, use `.venv/Scripts/python`.

### Task 0 — Baseline: confirm clean starting point (read-only, no edits)

Exact commands:

```
git status --short
git log --oneline -5
ls firmware/stages/ firmware/common/ host_scripts/ tests/
```

Expected output: `firmware/stacks` listing includes `bandpass.py fft.py features.py classify.py suppress.py actuate.py`; `firmware/common/` includes `bandpass.py fft.py feature_extract.py dnn.py model_dnn.py`; `tests/` includes `test_dnn_pipeline.py test_bandpass.py test_parkinsons_windows.py`. `git status` shows pre-existing modifications only — you change nothing in this task.

Commit: no (read-only).

### Task 1 — Prove the DNN perception path is green right now (TDD: no new code, just run)

Commands:

```
uv run python -m pytest tests/test_dnn_pipeline.py tests/test_bandpass.py -v
```

Expected output: all tests in both files pass (prior run: 9/9 in `test_dnn_pipeline.py`). If any fail, STOP — file a bug note with the failing test name and do not proceed to Task 2; the "go back" work is fixing that regression, not adding STFT.

Failing-test discipline: if you later add code (Tasks 4–5), write the failing test first, run it to see red, then implement minimally, then re-run to green. For this task there is nothing to write.

Commit: no.

### Task 2 — Reproduce the host trainer gate on cached windows (read-only run)

Background for zero-context implementer: `host_scripts/parkinsons_windows.py` converts raw Parkinson's CSVs (`Datasets/Parkinson's/.../data/raw_data_*.csv` + `train.csv`, mapped via `TASK_TO_LABEL` to baseline/kinetic/postural/rest) into 128×3 windows @ 100 Hz, cached to `host_scripts/parkinsons_windows.npz`. `host_scripts/train_dnn_parkinsons.py` trains logreg vs MLP-16 on the 15 features and prints paste-ready weights.

Commands:

```
ls "Datasets/Parkinson's/Parkinson's Tremor Classification Dataset/" host_scripts/*.npz 2>&1 | head -n 20
uv run python host_scripts/train_dnn_parkinsons.py host_scripts/parkinsons_windows.npz 2>&1 | head -n 20
```

Expected output (from `parkinsons_dnn_train.log` in repo root): first line `windows: 11838 classes: ['baseline', 'kinetic', 'postural', 'rest']`, then `logreg CV: 0.661 +/- ...`, `dnn CV: 0.750 +/- ...`, `GATE PASS`. If the `.npz` cache is missing, build it first with `uv run python host_scripts/parkinsons_windows.py` (expect `total windows: ...` and `cached ... windows -> ...parkinsons_windows.npz`, exit 0 only if > 5000 windows). If GATE prints FAIL, STOP — do not paste weights anywhere; report the CV numbers.

Commit: no (you ran, you pasted nothing).

### Task 3 — End-to-end synthetic check: bandpass → FFT → features → DNN forward (read-only script, no firmware edits)

Why: proves the four files agree on shapes without needing hardware. Copy-paste exactly (MSYS bash; single quotes intentional):

```
uv run python -c '
import sys; sys.path.insert(0, "firmware"); sys.path.insert(0, "host_scripts")
import math
from stages.bandpass import BandpassStage
from stages.fft import FFTStage
from stages.features import FeaturesStage
from stages.classify import ClassifyStage
fs, n = 100.0, 128
win = [[0.3*math.sin(2*math.pi*6.0*(i/fs)), 0.0, 1.0] for i in range(n)]
f = {"window": [r[:] for r in win]}
f = BandpassStage(fs=fs).process(f)
assert f.get("bandpass_ok"), f
f = FFTStage(samples=n, fs=fs).process(f)
print("dominant:", round(f["dominant_freq"],2), "Hz mag:", round(f["dominant_mag"],2))
f = FeaturesStage(fs=fs, n=n).process(f)
assert len(f["features"]) == 15, len(f["features"])
f = ClassifyStage(samples=n, fs=fs).process(f)
print("label:", f["label"], "conf:", round(float(f["confidence"]),3))
assert f["label"] in ("baseline","kinetic","postural","rest")
print("SYNTHETIC-CHAIN OK")
'
```

Expected output: `dominant: 6.xx Hz`, then `label: <one of the 4>`, then `SYNTHETIC-CHAIN OK`. If `dominant` is 0.0, the bandpass or FFT stage regressed — stop and report. If label key missing, `classify.py` fallback broke — stop and report.

Commit: no.

### Task 4 — Decision: single-FFT (default) vs true STFT (opt-in). Do the default; only do STFT if asked.

Recommended default (no code): keep `firmware/common/fft.py` as the spectral step. Rationale: it is tested, MicroPython-safe, fits 128-sample RAM budget, and matches the baked DNN features (which were trained on whole-window FFT band powers, not spectrograms). In that case skip to Task 6 and fix only the slide wording (Task 7).

Only build true STFT if the team explicitly wants time-frequency frames (e.g. tremor onset inside the 1.28 s window). If so, the contract is:

- New file `firmware/common/stft.py` (pure Python, no numpy): overlapping Hann frames → reuse `FFTProcessor._in_place_fft` per frame → magnitude spectrogram → collapse to the SAME 15 features by averaging band powers across frames (so `model_dnn.py` shapes do not change).
- Suggested signature (do not invent extra params):

```
# firmware/common/stft.py
class STFTProcessor:
    def __init__(self, num_samples=128, frame_len=64, hop=32, fs=100.0): ...
    def spectrogram(self, signal): ...   # returns list of frames x bins magnitudes
    def band_power_over_time(self, spec, lo_hz, hi_hz): ...  # mean across frames
```

- TDD first: new file `tests/test_stft.py` with exactly these 3 tests (write, run red, then implement):
  1. `test_stft_detects_6hz`: 128-sample 6 Hz sine @ 100 Hz → peak bin maps to 6 Hz ± 1 bin.
  2. `test_stft_matches_fft_on_stationary`: stationary sine → mean STFT band power 3–6/6–9 Hz within 20% of `FFTProcessor` equivalent.
  3. `test_stft_no_numpy`: `grep -rn "import numpy\|import scipy" firmware/common/stft.py` returns nothing; 128-sample call completes (host timing < 50 ms as smoke bound).
- Run: `uv run python -m pytest tests/test_stft.py -v` (expect red before impl, green after), then full suite `uv run python -m pytest tests/ -q` (expect all green).
- Then add thin stage `firmware/stages/stft.py` (`class STFTStage` with `process(frame)` writing `frame['spectrogram']` + `frame['dominant_freq']`, honoring `frame.get('skip_fft')` the same way `stages/fft.py` does) and gate it in `firmware/embedded_main_hsp.py` behind a config flag (default OFF, e.g. `USE_STFT = False` in `firmware/common/config.py`). Never run both `fft` and `stft` stages at once in `STAGE_ORDER`.

Commit after green: `git add firmware/common/stft.py firmware/stages/stft.py tests/test_stft.py firmware/common/config.py && git commit -m "feat(firmware): opt-in overlapping STFT behind USE_STFT flag (default off)"`.

### Task 5 — Re-bake DNN weights ONLY if Task 2 GATE passed and weights changed (otherwise skip)

Copy-paste flow (do not hand-edit numbers):

```
uv run python host_scripts/train_dnn_parkinsons.py host_scripts/parkinsons_windows.npz > /tmp/dnn_out.txt 2>&1; head -n 10 /tmp/dnn_out.txt
```

Expected: `GATE PASS` line in output. Only then: open `/tmp/dnn_out.txt`, copy the block between `# === paste into model_dnn.py ===` and `# === end ===` into `firmware/common/model_dnn.py`, replacing `CLASSES/FEATURE_MEAN/FEATURE_STD/W1/B1/W2/B2` wholesale (never mix old mean with new weights). Then:

```
uv run python -m pytest tests/test_dnn_pipeline.py -q
uv run python -c 'import sys; sys.path.insert(0,"firmware"); import common.model_dnn as m; assert len(m.W1)==16 and len(m.W1[0])==15 and len(m.W2)==4 and len(m.W2[0])==16; print("SHAPES OK")'
```

Expected: tests pass, `SHAPES OK`. If GATE FAILed, skip entirely — heuristic fallback stays (`classify.py:51-54` handles `W1 is None`, but with baked weights present the DNN path is live; do NOT null them out as a "rollback").

Commit after green: `git add firmware/common/model_dnn.py && git commit -m "feat(model): rebake DNN weights (CV <logreg> -> <dnn>)"` with the real numbers.

### Task 6 — Park everything else (config + wiring check, no logic edits unless broken)

- Confirm `firmware/stages/__init__.py:28-41` `STAGE_ORDER` still has `bandpass → fft → features → classify` in that order and does NOT include `suppress` (suppress/actuate run later in the order; perception must come first). If `suppress` appears before `classify`, that is the regression — move it back.
- Confirm `firmware/plan_b/combo_b3_dnn_pll.py` still raises without baked weights and gates `rest/baseline`/low-confidence to duty 0 (reference behavior; change nothing).
- Confirm b6 CNN stays quarantined and `train_cnn1d_parkinsons.py` is untouched in this plan. Confirm b7 fit build (`firmware/fit_main.py` if present, else `firmware/plan_b/combo_b7_fit.py`) is not the default entry — `firmware/embedded_main_hsp.py` remains the Plan A entry.
- Quick check command: `grep -n "STAGE_ORDER\|USE_STFT\|GATE_OK" firmware/stages/__init__.py firmware/common/config.py firmware/plan_b/*.py | head -n 30`.

Commit: only if you fixed an order regression: `git commit -m "fix(pipeline): restore bandpass->fft->features->classify order"`.

### Task 7 — Fix the one slide bullet + honest status (docs only, after code is green)

In the slide source (find it first — Q4 in `docs/slide_review_2026-09-10.md:74` notes the `.pptx`/Canva source is not in repo; do NOT retype the PDF):

- Delete the duplicate "STFT" bullet; rewrite the survivor as: "Spectral analysis: in-place Cooley–Tukey FFT on 128-sample windows @ 100 Hz (1.28 s)" (paste-ready fix F3, `docs/slide_review_2026-09-10.md:33`).
- If Task 4 built true STFT and it is ON: "...overlapping STFT (64-sample frames, 32 hop) → mean band powers → DNN". If STFT stayed OFF (default): do not claim STFT anywhere.
- Do NOT claim "Motor speed / suppression frequency" as DNN inputs (F4); the 15 inputs are `rms_all, std_all, mean-crossing rate, dominant freq, band powers 3–6/6–9/9–12/12–25 Hz, spectral entropy, dominant axis, rms_x/y/z, xy_ratio, peak prominence`.

Commit docs separately: `git add docs/ && git commit -m "docs: fix arch slide STFT wording, list real 15 DNN inputs"`.

## Tests / validation

- Per-task TDD: Tasks 1–3 are run-only (no new code). Task 4 (if taken) follows strict RED→GREEN: `tests/test_stft.py` written first and seen failing (`uv run python -m pytest tests/test_stft.py -v` → red), minimal `firmware/common/stft.py` implementation, re-run → green, then full suite `uv run python -m pytest tests/ -q` → all green before commit.
- Gate discipline: `train_dnn_parkinsons.py` GATE must print PASS and DNN CV must beat logreg before any weight paste (Task 5). Never invent weights; never mix scaler stats across bakes.
- No-numpy rule verified by: `grep -rn "numpy\|scipy" firmware/ --include="*.py"` → no output (allowed in `host_scripts/` only).
- Feature-order rule verified by: diffing the 15-element order in `firmware/common/feature_extract.py` header comments against `host_scripts/train_classifier.py:146-186` — any reorder requires retraining + rebaking in the same commit.
- Final acceptance: Tasks 1+2+3 outputs match "Expected" above, full `pytest` green, and the deck no longer claims STFT unless `USE_STFT` is on and tested.

## Risks, tradeoffs, and open questions

- Risk: true STFT costs 2–4× FFT compute and 2× RAM (overlapping frames + spectrogram buffer) on ESP32-DevKitC (classic WROOM-32, not S3; 4× MPU6050 via TCA9548A already eats ~4 ms I2C per 10 ms tick). Tradeoff: default single-FFT keeps headroom; STFT buys time-localization (onset inside window) the baked features cannot see. Mitigation: STFT default-OFF behind `USE_STFT`, host-timed before any device flash.
- Risk: retraining on whole-window features while inferring on STFT-averaged features skews distributions (scaler mismatch). Mitigation: Task 4 collapses STFT to the same 15 features by frame-averaging AND requires the ≤20% parity test; if parity fails, retrain a separate STFT-feature model instead of reusing `model_dnn.py` — do not silently reuse.
- Risk: source data caps content — Parkinson's windows are resampled to 100 Hz from ~22 Hz TIME stamps (`host_scripts/parkinsons_windows.py:31-42`), so content above ~8–11 Hz is interpolation, not measurement. Bands 9–12/12–25 Hz are weak by construction (carried-over weakness from prior plans). Do not over-interpret those two features.
- Risk: "go back" gets read as "delete PLL/CNN". Do NOT delete `stages/suppress.py`, `common/pll.py`, `common/cnn1d.py`, or plan_b combos in this plan — park them. Deletion is a follow-up decision with its own tests (prior plan `.hermes/plans/2026-09-06_000000-*` explicitly kept suppress files for this reason).
- Open Q1: is true overlapping STFT actually wanted, or was "stft" shorthand for "the spectral step before DNN"? Default assumption: shorthand → single-FFT + slide fix is sufficient. Confirm before doing Task 4.
- Open Q2: where is the slide source (`.pptx`/Canva link)? `docs/slide_review_2026-09-10.md:74` asks; without it Task 7 cannot be applied cleanly.
- Open Q3: are 320 g / 6–8 h measured or targets (finding F9)? Leave as "(target)" until a measurement note lands in `docs/`.
