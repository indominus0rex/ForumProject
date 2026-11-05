# PLL Workflow Review Plan

**Date:** 2026-09-13
**Scope:** review-only (read code, run tests/benches, write report). No behavior changes in this plan except failing-test reproductions saved as scratch files under `/tmp` or `sessions/` — never edits to `firmware/` or `tests/`.
**Deliverable:** review report + ranked findings list (file + chat summary).

---

## Goal

Systematically review the end-to-end PLL tremor-suppression workflow for correctness, consistency, and test coverage, and produce a ranked findings report with exact file:line evidence and reproduction commands.

## Current context / assumptions

- Repo root: `C:\ForumProject` (Windows, MSYS bash via `terminal`; run Python with `python`, tests with `python -m pytest`).
- The PLL workflow is a sample-by-sample chain (100 Hz default):
  `IMU xyz → conditioning → bandpass 3–12 Hz → PLL (phase/freq track) → phase predictor (15 ms) → anti-phase PWM (180°) → gain → LRA duty 0–1023`.
- Canonical DSP math lives in (read these first, in this order):
  1. `firmware/common/pll.py` (133 lines — `PLL.update()` phase detector + PI loop filter + NCO + lock detector)
  2. `firmware/common/bandpass.py` (4th-order bandpass as 2×biquad cascade)
  3. `firmware/common/predictor.py` (`φ + 2π·f·Δt`, 15 ms default)
  4. `firmware/common/anticancel.py` (`sin(pred+π)·amp·gain·1023`, `abs()` + clamp)
  5. `firmware/common/adaptive_gain.py` (EMA residual vs 0.3 target, attack 0.01 / decay 0.005, step cap 0.05)
  6. `firmware/stages/suppress.py` (`SuppressStage`: magnitude-minus-gravity → bandpass → PLL → predictor → duty; `process(frame)` only reads `x/y/z` keys)
  7. `firmware/plan_b/combo_b7_fit.py` (`b7_fit`: DevKitC fit build — multi-IMU fusion + dominant-axis projection + amplitude-normalized PLL drive + `AMP_GATE=0.03` + lock gate; `self._sup = self` compat shim)
  8. `firmware/stages/actuate.py` (`ActuationStage`: DNN-gated replay of `window` through owned `SuppressStage`, median-of-last-32 duties × postural 0.5 / kinetic 1.0 scale, **resets PLL on any gate closure**)
  9. `firmware/plan_b/combo_b4_pll_only.py` (thin wrapper over `SuppressStage`, label passthrough), `firmware/plan_b/combo_b3_dnn_pll.py` (DNN gate + full PLL), `firmware/plan_b/combo_b5_dnn_fixed_gain.py` (DNN gate + fixed 0.5 gain, replays only `window[len//2]` single sample — known shortcut), `firmware/plan_b/combo_b6_cnn_pll.py` (quarantined, `GATE_OK=False`, `process()` raises)
  10. `prototype/loop.py` (`Loop.step()`: claims to "mirror `firmware/common/pll.py` exactly" — verify, it uses its own `Biquad` + DC tracker on x only)
  11. `firmware/common/config.py` lines 75–98 (canonical tunables: `PLL_BANDWIDTH_HZ=1.0`, `PLL_DAMPING=0.707`, `PLL_CENTER_FREQ_HZ=6.0`, `PLL_LOCK_THRESHOLD=50`, `PREDICTION_MS=15.0`, `ADAPTIVE_GAIN_*`, `BANDPASS_*`)
  12. `firmware/embedded_main_hsp.py` lines 140–142 (ActuationStage wiring), `firmware/plan_b/__init__.py` (registry: 6 combos, fallback chain `b3→b5→b2→b4→b1`, b6 excluded, b7 separate), `firmware/plan_b/README.md`, `host_scripts/bench_plan_b.py` (currently only prints feature means — does NOT score PLL combos; do not confuse with a PLL bench)
- Tests (all host-side, `sys.path.insert(0, "firmware")` style, runnable via pytest or `python <file>`):
  - `tests/test_pll.py` (init, 6 Hz lock, wrap, clamp, reset, period)
  - `tests/test_suppress.py` (bounds, frame keys, 6 Hz track, reset, status)
  - `tests/test_b7_fit.py` (contract, bounds, 6 Hz track, 128-window <0.5 s, no-heavy-imports, multi-IMU fusion, dominant-axis, 4× amplitude-jump lock survival)
  - `tests/test_actuate.py` (bounded duty, gate-zero+reset, postural≤kinetic, **live-CSV replay** of `host_scripts/sessions/pre_postural_s01.csv` through quality→…→actuate — needs that CSV present)
  - `tests/test_plan_b.py` (6-combo registry contract + b6 quarantine)
- Memory context (do not re-verify hardware here, just don't contradict it): ESP32-DevKitC classic, 4×MPU6050 via TCA9548A, LRA GPIO25 200 Hz PWM, `b7_fit` is the fit build; user wants TODO markers on tunables (review should flag hardcoded values lacking TODO).
- Assumption: `python -m pytest` works. If not installed, fall back to `python tests/<file>.py` per-file (each has a `__main__` runner printing `* tests passed!`).

## Architecture / proposed approach

Read the chain leaf-to-root (`common/` math → `stages/suppress.py` → plan_b combos + `stages/actuate.py` → prototype mirror), then execute the existing tests plus small throwaway probe scripts (sine lock, 3–12 Hz sweep, amplitude jump, stall conditions) to confirm or refute each suspected defect before writing anything up. Findings go into a single report file with severity, exact `file:line` evidence, reproduction command, and a concrete suggested fix — no source edits in this review.

## Step-by-step tasks

### Task 1 — Inventory the workflow files (2 min)

List every file that touches the PLL chain and confirm none are missed.

```bash
grep -rn --include='*.py' -l -E 'pll|PLL|SuppressStage|AntiPhase|PhasePredictor|AdaptiveGain|process_multisample' firmware/ tests/ prototype/ host_scripts/ | sort
```

Expected: at minimum `firmware/common/pll.py`, `firmware/common/bandpass.py`, `firmware/common/predictor.py`, `firmware/common/anticancel.py`, `firmware/common/adaptive_gain.py`, `firmware/common/config.py`, `firmware/stages/suppress.py`, `firmware/stages/actuate.py`, `firmware/plan_b/__init__.py`, `firmware/plan_b/combo_b3_dnn_pll.py`, `firmware/plan_b/combo_b4_pll_only.py`, `firmware/plan_b/combo_b5_dnn_fixed_gain.py`, `firmware/plan_b/combo_b6_cnn_pll.py`, `firmware/plan_b/combo_b7_fit.py`, `firmware/embedded_main_hsp.py`, `prototype/loop.py`, `tests/test_pll.py`, `tests/test_suppress.py`, `tests/test_b7_fit.py`, `tests/test_actuate.py`, `tests/test_plan_b.py`. If any listed file is missing, note it in the report and continue.

### Task 2 — Read the core loop math (5 min, no edits)

Read `firmware/common/pll.py` fully (133 lines). Write down in the report: (a) phase-detector formula (`sample * cos(phase)`), (b) LPF `alpha=0.1`, (c) PI gains derived from `bandwidth/damping`, (d) freq clamp 3–12 Hz, (e) lock rule (`|err|<0.1` increments, `>0.2` resets, threshold 50). Flag anything that looks wrong but do NOT fix — file under findings.

Verify with:

```bash
sed -n '40,115p' firmware/common/pll.py
```

Expected: matches the (a)–(e) summary above.

### Task 3 — Run the existing PLL test baseline (3 min)

```bash
python -m pytest tests/test_pll.py tests/test_suppress.py tests/test_b7_fit.py tests/test_actuate.py tests/test_plan_b.py -v 2>&1 | tail -30
```

Expected: all pass (5 files, ~25 tests). If `pytest` is missing, run `python tests/test_pll.py && python tests/test_suppress.py && python tests/test_b7_fit.py` and expect each to print `* tests passed!`. Record exact pass/fail counts in the report. If `tests/test_actuate.py::test_replay_real_postural_window` fails on missing `host_scripts/sessions/pre_postural_s01.csv`, verify the file exists with `ls host_scripts/sessions/ | head` and mark the failure as environment, not PLL logic.

### Task 4 — Probe: lock time + freq accuracy at 6 Hz (5 min)

Save as scratch file `/tmp/pll_probe_lock.py` (do NOT put in `tests/`), run it, paste numbers into report. This is a measurement probe, not a repo test — no TDD cycle needed.

```python
"""Scratch probe: PLL lock time + freq accuracy on clean 6 Hz sine."""
import sys, math
sys.path.insert(0, "firmware")
from common.pll import PLL

fs, f0 = 100.0, 6.0
pll = PLL(fs=fs, center_freq=6.0, bandwidth=1.0)
lock_at = None
for i in range(400):
    t = i / fs
    pll.update(math.sin(2 * math.pi * f0 * t))
    if pll.locked and lock_at is None:
        lock_at = i
print("locked:", pll.locked, "lock_sample:", lock_at,
      "freq:", round(pll.freq, 3), "err:", round(abs(pll.freq - f0), 3))
assert pll.locked and abs(pll.freq - f0) < 0.5, "FAIL: did not lock to 6 Hz"
print("PASS")
```

```bash
python /tmp/pll_probe_lock.py
```

Expected: `locked: True lock_sample: <~50-150> freq: ~6.0 err: <0.5` + `PASS`. If lock never happens or error >0.5 Hz, that is Finding #1 ( cite `firmware/common/pll.py:104-111` lock rule).

### Task 5 — Probe: frequency sweep 3–12 Hz edge behavior (5 min)

```python
"""Scratch probe: does PLL track across the whole 3-12 Hz tremor band?"""
import sys, math
sys.path.insert(0, "firmware")
from common.pll import PLL

for f0 in (3.0, 4.0, 6.0, 9.0, 12.0):
    pll = PLL(fs=100.0, center_freq=6.0, bandwidth=1.0)
    for i in range(400):
        pll.update(math.sin(2 * math.pi * f0 * (i / 100.0)))
    print(f"target={f0:5.1f} tracked={pll.freq:5.2f} locked={pll.locked} "
          f"err={abs(pll.freq - f0):.2f}")
```

```bash
python /tmp/pll_probe_sweep.py
```

Expected: every row `locked=True`, `err<0.5`. Known risk: 3 Hz and 12 Hz band edges may show larger error or no lock (loop gains computed for 6 Hz center). Report per-frequency numbers; any row with `err>1.0` or `locked=False` becomes a finding citing `firmware/common/pll.py:89-93` (clamp) and `:44-47` (gain derivation).

### Task 6 — Probe: amplitude sensitivity + DC vulnerability (5 min)

The lock detector thresholds on absolute `phase_error_filtered` (`<0.1` / `>0.2`), which scales with input amplitude — suspect small tremors never lock and large ones false-lock, and `SuppressStage`'s `magnitude - 1.0` may feed a doubled-frequency / DC-shifted signal. Measure it:

```python
"""Scratch probe: amplitude scaling of lock detector + DC offset effect."""
import sys, math
sys.path.insert(0, "firmware")
from common.pll import PLL

for amp in (0.05, 0.15, 0.5, 2.0):
    pll = PLL(fs=100.0, center_freq=6.0, bandwidth=1.0)
    for i in range(300):
        pll.update(amp * math.sin(2 * math.pi * 6.0 * (i / 100.0)))
    print(f"amp={amp:4.2f} locked={pll.locked} freq={pll.freq:.2f}")

for dc in (0.0, 0.3, 1.0):
    pll = PLL(fs=100.0, center_freq=6.0, bandwidth=1.0)
    for i in range(300):
        pll.update(dc + 0.15 * math.sin(2 * math.pi * 6.0 * (i / 100.0)))
    print(f"dc={dc:3.1f} locked={pll.locked} freq={pll.freq:.2f}")
```

```bash
python /tmp/pll_probe_amp.py
```

Expected to check: whether tiny `amp=0.05` locks (probably not) and whether `dc=1.0` breaks tracking. Cross-reference `firmware/plan_b/combo_b7_fit.py:96-99` (b7 already normalizes by `amp_smooth + 0.05` — the fix pattern) vs `firmware/stages/suppress.py:71-81` and `firmware/plan_b/combo_b5_dnn_fixed_gain.py:54-56` (both feed raw filtered magnitude with no normalization). Any divergence is a finding: "b7 fixed amplitude sensitivity; SuppressStage/B5 did not."

### Task 7 — Audit the four known divergence points (5 min, code read + one command)

Check each of these deliberately (they are the highest-value review targets) and record verdict + evidence:

1. **Magnitude vs dominant-axis** — `firmware/stages/suppress.py:71-76` uses `sqrt(x²+y²+z²)-1.0` (magnitude folds oscillation frequency and mixes axes) while `firmware/plan_b/combo_b7_fit.py:75-94` uses per-axis DC removal + dominant-axis projection. Confirm b7's comment block lines 7–8 claims this fixes "magnitude frequency-doubling."
2. **B5 single-sample shortcut** — `firmware/plan_b/combo_b5_dnn_fixed_gain.py:47-49` replays only `window[len//2]` instead of the full window. Confirm by reading; check whether any test covers it (search `grep -rn 'b5' tests/ | head` — expect no dedicated B5 test).
3. **ActuationStage reset-on-gate** — `firmware/stages/actuate.py:25-30` resets the entire `SuppressStage` (PLL unlock) on every gated frame; `process()` replays the whole 128-sample window then takes median-of-last-32 (`:46-50`). Assess: lock must re-acquire every window (~50-sample threshold vs 128-sample window = plausible but wasteful; note `test_gated_outputs_zero_and_resets` in `tests/test_actuate.py:15-21` enshrines the reset).
4. **Prototype mirror drift** — diff `prototype/loop.py:52-69` against `firmware/common/pll.py:73-111` line by line (DC tracker `0.02` vs none, `Biquad` vs `BandpassFilter`, identical kp/ki/lock math?). Note any drift from the "mirrors exactly" claim in `prototype/loop.py:36-37`.

```bash
grep -rn 'b5_fixed\|combo_b5\|B5' tests/ host_scripts/ | head -20
```

Expected: no dedicated B5 coverage (confirm or correct in report).

### Task 8 — Audit tunables: hardcoded vs `common/config.py` (3 min)

```bash
grep -rn -E 'bandwidth|prediction_ms|initial_gain|center_freq|AMP_GATE|MEAN_ALPHA|ENERGY_ALPHA|AMP_ALPHA|kinetic_scale|postural_scale|CONF_THRESH|FIXED_GAIN|MAX_DUTY' firmware/common/config.py firmware/common/pll.py firmware/stages/suppress.py firmware/stages/actuate.py firmware/plan_b/combo_b7_fit.py firmware/plan_b/combo_b5_dnn_fixed_gain.py prototype/loop.py
```

Expected findings to verify: `SuppressStage.__init__` defaults (`pll_bandwidth=1.0`, `prediction_ms=15.0`, `initial_gain=0.5`) duplicate but don't import `config.py`; `combo_b7_fit.py` hardcodes `AMP_GATE=0.03`, `NORM_EPS=0.05`, `W=[0.4,0.2,0.2,0.2]` with TODOs (good per user convention — verify TODOs present); `prototype/loop.py` hardcodes `AMP_GATE/FIXED_GAIN/PREDICT_S/MAX_DUTY`; `ActuationStage` hardcodes `kinetic_scale=1.0/postural_scale=0.5`; `AdaptiveGain.reset()` resets to literal `0.5` not `self` initial (`firmware/common/adaptive_gain.py:81-84` — confirm, likely bug); `PLL` default `bandwidth=0.5` in `common/pll.py:24` vs `config.PLL_BANDWIDTH_HZ=1.0` vs `SuppressStage` default `1.0` (inconsistent defaults — confirm). Each confirmed item = one finding row.

### Task 9 — Check `compute_duty` sign/rectification + downstream use (3 min)

Read `firmware/common/anticancel.py:25-48`: `duty = abs(int(sin(anti_phase)*amp*gain*max))`. Confirm: output is always non-negative (half-wave rectified — negative half-cycle folds positive, so LRA fires twice per tremor period, not push-pull). Check whether any caller uses `compute_stereo_duties` (`:50-75`): `grep -rn 'compute_stereo\|compute_duty' firmware/ | head`. Expected: only `compute_duty` used; stereo dead code. Assess against 200 Hz LRA PWM contract (`LRA_FREQ=200`, `max_duty=1023`) and the `b7` docstring line 13 (`MAX_DUTY cap lives in fit_main.py` — but no `fit_main.py` exists in repo; verify with file search and flag as stale doc).

### Task 10 — Write the report (5 min)

Write `docs/pll_workflow_review_YYYY-MM-DD.md` (or `sessions/` if `docs/` write is restricted — report path decision goes in chat summary). Required sections per finding: **Severity** (Blocker/Major/Minor/Nit), **File:line evidence**, **Repro command + observed output**, **Suggested fix (concrete, ≤5 lines or exact constant)**. Mandatory coverage checklist (mark each PASS/FAIL with evidence): lock acquisition, band-edge tracking, amplitude robustness, DC/gravity handling, magnitude-vs-axis, B3/B4/B5/b7 consistency, gate/reset behavior, tunable traceability, prototype mirror fidelity, test gaps (esp. B5 + sweep + stereo + `AdaptiveGain.reset`). End with a ranked fix list (top 3 first) and explicit "no change needed" items to prevent churn. Do NOT edit source files.

Verify report completeness:

```bash
ls -la docs/pll_workflow_review_*.md && grep -c '^### Finding' docs/pll_workflow_review_*.md && grep -E 'PASS|FAIL' docs/pll_workflow_review_*.md | head -20
```

Expected: file exists, finding count ≥3, PASS/FAIL checklist present.

## Tests / validation

- This is a review plan: the TDD cycle applies to **probe scripts**, not repo code. For each suspected defect: (1) write the failing-behavior probe as a `/tmp` scratch script, (2) run it to confirm the behavior (paste output), (3) do NOT implement the fix — record it as a finding with a concrete suggestion. No commits to `firmware/` or `tests/`.
- Regression gate before writing the report (Task 3 command): `python -m pytest tests/test_pll.py tests/test_suppress.py tests/test_b7_fit.py tests/test_actuate.py tests/test_plan_b.py -v` — expected all green; any red must be triaged as environment (missing CSV/weights) vs real PLL defect and labeled as such in the report.
- Report self-check (Task 10 command): review file exists, findings numbered, every severity justified with a repro command and observed output. Acceptance = a zero-context reader can reproduce any finding by copy-pasting its command.

## Risks, tradeoffs, and open questions

- **Risk: scope creep into fixing.** The workflow has obvious fix candidates (amplitude-normalized drive for SuppressStage, `AdaptiveGain.reset()` literal, B5 single-sample replay). Resist — this plan is review-only; fixes are a follow-up task to keep the report honest and the diff reviewable.
- **Risk: hardware truth vs host probes.** All probes use synthetic sines at 100 Hz; real tremor has drift, harmonics, sensor noise, and LRA latency the probes don't model. Mark host-only conclusions explicitly; body-tuned constants (`AMP_GATE`, `PREDICTION_MS`, fusion `W`) need on-device validation, not host argument.
- **Risk: missing artifacts.** `host_scripts/sessions/pre_postural_s01.csv` (actuate replay test), baked DNN weights (`common/model_dnn.py` `W1/W2`), and the referenced-but-absent `firmware/fit_main.py` may be missing — treat absence as a docs/test-gap finding, not a PLL defect.
- **Tradeoff: magnitude (simple, always available) vs dominant-axis (cleaner phase, axis-switch glitches).** b7 chose dominant-axis; SuppressStage/B5 kept magnitude. The report should recommend one canonical frontend and name the migration cost rather than blessing both.
- **Tradeoff: reset-on-gate (clean state, provable) vs persistent PLL (fast re-lock, lock carryover risk).** `ActuationStage` chose reset; note the 50-sample lock threshold consumes ~40% of each 128-sample window and say whether that is acceptable.
- **Open questions for the user:** (1) Is `b7_fit` now canonical, making `SuppressStage` legacy — or must both be kept? (2) Should `prototype/loop.py` remain bit-exact with firmware, or is it allowed to drift as an experiment? (3) Is `compute_stereo_duties` (push-pull) or `abs()` rectified single-channel the intended LRA drive? (4) Body-test availability for re-tuning `AMP_GATE` / `PREDICTION_MS` / fusion weights?
