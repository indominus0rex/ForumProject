# PLL Workflow Review — 2026-09-13

**Scope:** end-to-end PLL tremor-suppression chain (review-only, no source edits).
**Baseline:** all existing tests green (`test_pll`, `test_suppress`, `test_b7_fit`, `test_actuate`, `test_adaptive_gain`, `test_anticancel`, `test_predictor` via `python tests/<f>.py`; `test_plan_b` has no `__main__` runner — see Finding 12).
**Probes:** scratch scripts in `%LOCALAPPDATA%\Temp\pll_probe*.py` (not committed); all outputs below are copy-paste reproducible.

## What passes (no change needed)

- 6 Hz center lock: `locked=True` at sample 51, freq err 0.005 Hz (`pll_probe_lock.py`).
- Hold-in-lock when `center_freq` is preset to the target (4.0/5.0/8.0 all `locked=True`, err <0.02).
- b7 survives 4× amplitude jump locked (existing `test_push4_amplitude_normalized` + probe re-confirm).
- Duty bounds 0–1023 everywhere; reset clears state; predictor/bandpass math matches prototype.
- `prototype/loop.py` core (gains, LPF alpha, lock band) is faithful to `firmware/common/pll.py`.

## Findings (ranked)

### Blocker 1 — PLL pull-in range is ~zero; NCO parks at 6.0 Hz
**File:** `firmware/common/pll.py:73-100`
**Repro:** `python %LOCALAPPDATA%\Temp\pll_probe_sweep.py`
**Observed (600 samples ≈ 6 s each, bw=1.0):**

| target | tracked | locked | err |
|---|---|---|---|
| 3.0 | 6.00 | False | 3.00 |
| 4.0 | 5.99 | False | 1.99 |
| 4.2 | 5.91 | False | 1.71 |
| 5.0 | 5.85 | False | 0.85 |
| 6.0 | 5.99 | True | 0.01 |
| 8.0 | 6.03 | False | 1.97 |
| 9.0 | 6.00 | False | 3.00 |
| 12.0 | 5.99 | **True** | **6.01** |

Wider bandwidths don't fix it (`pll_probe2.py` §A: bw=2.0 gives 5.0→5.6, 7.0→8.0; bw=3.0 gives 6.0→5.8 unlocked — worse). Slow drift 6→7 Hz over 6 s ends at 6.60 unlocked (§C).
**Fix:** port the acquisition aid already proven in `prototype/loop_v2.py` (G2 coarse zero-crossing seeding recenters `center` when unlocked >1 s; G1 gear-shift wide-while-unlocked) into `PLL` or `combo_b7_fit`, behind existing constructor defaults so 6 Hz behavior is unchanged.

### Blocker 2 — Lock detector false-locks (absolute error band)
**File:** `firmware/common/pll.py:104-111`
`if abs(phase_error_filtered) < 0.1: lock++` cannot distinguish "tracking well" from "error averaged to ~nothing" (weak signal, far-off beat, 2× image). Evidence: 12 Hz input reports `locked=True` at 5.99 Hz (table above); full `SuppressStage` chain reports `locked=True` at 6.00 for 4 Hz and 8 Hz inputs (`pll_probe2.py` §D). `prototype/loop_v2.py:9-12` independently confirms: *"False lock on far-off tones was confirmed: 4.2 Hz in, NCO parked at 6.0, duties firing at wrong phase."*
**Fix:** port loop_v2's B1 beat detector (fast/slow EMA agreement veto + coarse-vs-NCO disagreement veto, `loop_v2.py:78-111`) and make the lock threshold relative to smoothed amplitude, e.g. `lock_thresh = max(0.05, 0.3 * amp_smooth)`.

### Major 3 — Two canonical frontends disagree (magnitude vs dominant-axis)
**Files:** `firmware/stages/suppress.py:71-76` (`sqrt(x²+y²+z²)-1.0`) vs `firmware/plan_b/combo_b7_fit.py:75-94` (per-axis DC removal + dominant-axis projection; docstring lines 7–8 cite "magnitude frequency-doubling").
x-only tremor through the magnitude path is second-order (`|a|²` term → 12 Hz + DC at tiny amplitude) yet reports `locked=True` at 6.00 (`pll_probe2.py` §E) — indistinguishable from Blocker-2 false lock. SuppressStage/B5 never got b7's push-2/push-4 fixes.
**Fix:** pick one frontend (recommend b7's: dominant-axis + normalized drive) and route `SuppressStage` through it; add an x-only off-axis tracking test mirroring `test_push2_dominant_axis_projection`.

### Major 4 — b3/b4/b5 `process(frame)` don't replay the window
**Files:** `firmware/plan_b/combo_b3_dnn_pll.py:39`, `firmware/plan_b/combo_b4_pll_only.py:18` (both call `SuppressStage.process`, which steps **one** `x/y/z` sample per call — `stages/suppress.py:111-115`), `firmware/plan_b/combo_b5_dnn_fixed_gain.py:47-49` (steps a single mid-window sample). Only b7 (`combo_b7_fit.py:127-141`) and `ActuationStage` (`stages/actuate.py:46`) replay full windows. At one PLL step per 1.28 s window, the 50-sample lock threshold = ~64 s wall-clock in windowed/bench use.
**Fix:** make all combos replay `frame["window"]` sample-by-sample like b7 (or document single-step as intentional with the 64 s consequence).

### Major 5 — `AdaptiveGain.reset()` ignores constructor arg
**File:** `firmware/common/adaptive_gain.py:81-84` — `self.gain = 0.5` literal. Repro: `AdaptiveGain(initial_gain=0.9).reset().gain` → `0.5` (`pll_probe2.py` §F). Existing `test_reset` passes only because it uses the default 0.5.
**Fix:** store `self._initial = initial_gain` in `__init__`, reset to it. Extend `test_reset` with a non-default initial gain.

### Minor 6 — loop_v2 fix never ported; prototype is now the reference impl
`prototype/loop_v2.py` (gear-shift + coarse seeding + beat veto) is imported nowhere in `firmware/`/`tests/`/`host_scripts/`. The tested device code is the known-bad loop; the good loop is untested prototype. **Fix:** decide — port loop_v2 into firmware (recommended, see Blockers) or delete it to stop/Delete confusion. At minimum add a test that fails today: 4.2 Hz in → must not report `locked=True` at 6 Hz.

### Minor 7 — Tunables bypass `common/config.py`; defaults disagree
`PLL.__init__` defaults `bandwidth=0.5`, but `config.PLL_BANDWIDTH_HZ=1.0` and every caller passes/assumes `1.0`. Nothing imports `config.py` for PLL/predictor/gain values; `PREDICTION_MS=15.0` is still unmeasured (b7 docstring itself says "measure LRA latency"). `prototype/loop.py` hardcodes `AMP_GATE/FIXED_GAIN/PREDICT_S`. **Fix:** single-source defaults from `config.py`; keep TODO markers per user convention; measure and record LRA latency for `PREDICTION_MS`.

### Minor 8 — `compute_stereo_duties` is dead code; `abs()` rectification is unexamined
Only `compute_duty` has callers (3: suppress, b5, b7). `abs()` half-wave-rectifies, so output fires at 2× tremor rate rather than push-pull — possibly fine for an LRA, but no comment or test states the intent. **Fix:** one-line doc note + a test pinning rectified behavior, or delete stereo.

### Minor 9 — `test_plan_b.py` has no `__main__` runner
Every sibling test file runs via `python tests/<f>.py`; `test_plan_b.py` ends at the last assert, so `python tests/test_plan_b.py` exits 0 silently testing nothing, and (like all files) it needs pytest-free direct execution since **pytest is not installed** in this env. **Fix:** add the standard runner block.

### Minor 10 — Stale `fit_main.py` references; `bench_plan_b.py` doesn't bench PLL
`firmware/fit_main.py` does not exist, but 4 places name it the b7 entry (`plan_b/combo_b7_fit.py:13`, `plan_b/README.md:18`, `plan_a/README.md:32`, `firmware/README.md:10`). `host_scripts/bench_plan_b.py` prints feature means only — no PLL scoring. **Fix:** restore/retire `fit_main.py` and update the 4 refs; rename or extend the bench if PLL scoring is wanted.

### Nit 11 — ActuationStage reset-on-gate cost
`stages/actuate.py:25-30` resets the whole `SuppressStage` on every gated frame (enshrined by `test_gated_outputs_zero_and_resets`). Cost: 50-sample re-acquisition inside every 128-sample window (~40%). Correctness-first and acceptable, but record the budget implication for the 4-IMU ISR (`embedded_main_hsp.py` ~4 ms reads @10 ms tick).

## Coverage checklist

| Check | Verdict | Evidence |
|---|---|---|
| 6 Hz lock | PASS | probe: sample 51, err 0.005 |
| Off-center acquire (3–12 Hz) | FAIL | Blocker 1 table |
| False-lock rejection | FAIL | Blocker 2 (12 Hz; chain 4/8 Hz) |
| Drift following | FAIL | 6→7 Hz ends 6.60 unlocked |
| Amplitude robustness | PASS* | 0.02–2.0 all lock; *only at center |
| DC/gravity handling | PASS* | b7 per-axis + magnitude-1.0 + bandpass; raw DC=1.0 unlocks (no false lock — good) |
| B3/B4/B5/b7 consistency | FAIL | Findings 3, 4 |
| Gate/reset behavior | PASS (cost noted) | Nit 11 |
| Tunable traceability | FAIL | Finding 7 |
| Prototype mirror fidelity | PASS loop.py / FAIL loop_v2 port | Finding 6 |
| B5 coverage | FAIL | no dedicated test |
| `AdaptiveGain.reset` | FAIL | Finding 5 |

## Top-3 fix order

1. Port loop_v2 acquisition + beat veto into firmware PLL path (fixes Blockers 1–2; add 4.2 Hz no-false-lock + sweep tests first — they fail today).
2. Unify frontend on b7 dominant-axis + normalized drive (Finding 3) and window replay across combos (Finding 4).
3. `AdaptiveGain.reset` one-liner + non-default test; `test_plan_b` runner; `fit_main.py` doc refs (Findings 5, 9, 10 — all <10 min each).

## Open questions (for Singto)

1. Is `b7_fit` canonical (migrate `SuppressStage`/B5 to it) or must both frontends stay?
2. Should `prototype/loop*.py` stay bit-exact with firmware, or is prototype free to experiment?
3. Single-channel rectified drive vs push-pull stereo — which is the intended LRA drive?
4. Is body-test time available to re-tune `AMP_GATE` / `PREDICTION_MS` / fusion `W` after the lock fix?

## Fix verification (2026-09-13, branch `fix/pll-acquire-and-lock`)

All fixes implemented and all 8 suites green (`test_pll/suppress/b7_fit/actuate/plan_b/adaptive_gain/anticancel/predictor` via direct `python` runs — pytest is not installed in this env).

### Post-fix sweep (raw 6-tone sine, 600 samples, bw=1.0)

| target | tracked | locked | err |
|---|---|---|---|
| 3.0 | 3.02 | False | 0.02 |
| 4.0 | 3.98 | True | 0.02 |
| 4.2 | 4.20 | True | 0.00 |
| 5.0 | 4.99 | True | 0.01 |
| 6.0 | 5.99 | True | 0.01 |
| 8.0 | 8.01 | False | 0.01 |
| 9.0 | 9.05 | False | 0.05 |
| 12.0 | 12.00 | False | 0.00 |

vs pre-fix: NCO parked at 6.0 for every input, with false lock at 12 Hz. Zero false locks now by construction (coarse-agreement veto).

### Post-fix chain sweep (600 samples; SuppressStage and b7_fit identical)

| target | tracked | locked |
|---|---|---|
| 4.0 | 4.01 | True |
| 5.0 | 5.01 | True |
| 6.0 | 5.98 | True |
| 8.0 | 8.03 | False (locks ~625 with more samples) |

Lock horizons (raw): 6 Hz sample 51 (unchanged from baseline), 5 Hz ~470, 4/8/9 Hz ~625–720. Rail edges (3/12 Hz) track accurately but stay honestly unlocked (clamp + coarse-bias deadlock, no false lock).

### Faster-lock + rail-edges update (2026-09-13, branch `fix/pll-acquire-and-lock`, uncommitted)

Follow-up plan (`.hermes/plans/2026-09-13_211912-pll-faster-lock-rail-edges.md`): guardrails + horizon ratchet + honest rail lock + FLL/G2 speedup attempt + chain horizons. Full suite: **100 passed** (89 baseline + 6 guardrails + 1 horizon + 2 rail + 2 chain).

Post-update sweep (raw sine, 600 samples, bw=1.0) — rails now lock honestly:

| target | tracked | locked | err |
|---|---|---|---|
| 3.0 | 3.00 | True (was False) | 0.00 |
| 4.0 | 3.98 | True | 0.02 |
| 4.2 | 4.20 | True | 0.00 |
| 5.0 | 4.99 | True | 0.01 |
| 6.0 | 5.99 | True | 0.01 |
| 8.0 | 8.01 | False | 0.01 |
| 9.0 | 9.05 | False | 0.05 |
| 12.0 | 12.00 | True (was False) | 0.00 |

Lock horizons, raw sine (samples to first `locked`, limit 2000):

| tone | 3 Hz | 4 Hz | 5 Hz | 6 Hz | 7 Hz | 8 Hz | 9 Hz | 12 Hz |
|---|---|---|---|---|---|---|---|---|
| horizon | 355 | 549 | 419 | 52 | 554 | 602 | 636 | 482 |

Chain (`SuppressStage`, x-tremor + gravity-z): 4 Hz locks sample 565 (freq 4.01), 8 Hz locks sample 603 (freq 8.02) — inside the 900/1100 budgets.

What changed in `firmware/common/pll.py` (rail fix only; no kp/ki, no signature, no body constants): rail diagnosis showed the `perr > 0.2` reset — not the disagree veto — blocked rail lock (freq converges to the rail but a frozen phase offset parks |perr| at 0.3–0.6; coarse agrees, veto silent). Fix = rail-agreement lock rule (NCO at rail + clamped coarse within 0.5 + wider 0.7 perr band) fenced by a NEW unclamped crossing-rate tracker `_craw` (one float): clamped coarse alone cannot separate 12↔15 Hz (both park at the top rail with small perr — measured 15 Hz best run 892 samples), but raw rate can (|15−12| vs |12−12|). 2/15 Hz verified never-lock over 2500 samples.

Speedup attempt (all reverted per rollback rule — 6 Hz stayed 52, zero false locks throughout): FLL gap-scheduled gain (a) WORSENED horizons (4:549→577, 9:636→675); earlier G2 refire >60 (b) and FLL gate ≥5 (c) neutral singly and combined. Bottleneck is post-G2 PI settle (4 Hz crawls 4.85→4.0 over ~350 samples with ring-back to 3.87), not acquisition — FLL/G2 knobs can't buy the 400-sample goal without touching loop gains. Horizon bounds stay at Task 2 values; 400 remains future work if a product requirement ever demands it.

### What actually shipped (deviations from the fix plan, all measured)

- **Ported from loop_v2:** coarse zero-crossing seeding (G2) + disagreement veto (B1 core). **NOT ported:** gear-shift wide loop (measured unstable at unit amplitude) and raw wobble/level thresholds (scale-dependent — true lock shows level 0.24 at unit amplitude).
- **Added beyond loop_v2:** amplitude-invariant loop drive (RMS normalization + pi/2 crest compensation), FLL assist into the integrator (maturity-gated, cut on lock — breaks the zero-mean beat stalemate), clamp anti-windup, fast-attack/slow-release level AGC (4x jump relocks).
- **loop_v2 verdict:** its "fast lock" (sample ~50 at all freqs) is declaration-before-evidence — measured 0.1–0.4 Hz off while claiming lock, i.e. the exact wrong-phase failure. The firmware port tracks to <=0.06 Hz and refuses to lie.
- b3/b4/b5 replay full windows; `SuppressStage` and b7 share `firmware/common/frontend.py` (dominant-axis + normalized drive); `AdaptiveGain.reset` honors its constructor arg; `test_plan_b.py` gained a `__main__` runner (and its dead `import pytest` was removed — the file was unrunnable here); `fit_main.py` refs marked device-side/unversioned (file never in repo — commit it from the ESP32 if it should be versioned).
- Bench scoring (`bench_plan_b.py`) left alone per YAGNI.

### Known limitations (honest, measured)

- Off-center lock takes ~420–640 samples (4–5 s); rail edges now lock honestly (3 Hz ~355, 12 Hz ~482 — see update above; previously never asserted lock).
- Zero-DC synthetic sine into the raw PLL locks slowly (~1000 samples: slow-release AGC converging from init). Real paths carry gravity DC ~= `_rms` init or frontend normalization — unaffected (all chain tests lock in budget).
- Body constants (`AMP_GATE`, `PREDICTION_MS`, fusion `W`) still untuned — needs on-device validation.
