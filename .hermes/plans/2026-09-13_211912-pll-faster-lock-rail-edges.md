# Plan: PLL faster off-center lock + honest rail-edge lock

## Goal

Cut off-center PLL lock time (today 470–720 samples) and make rail-edge tones (3 Hz / 12 Hz) assert lock honestly, without reintroducing false lock or slowing the 6 Hz center lock (sample ~51).

## Current context / assumptions

- Code: `firmware/common/pll.py` (243 lines, MicroPython — `math` only, no numpy). Sole owner of lock behavior. Constructor `PLL(fs=100.0, center_freq=6.0, bandwidth=1.0, damping=0.707)` is called by `firmware/stages/suppress.py:49`, `firmware/plan_b/combo_b7_fit.py`, and all tests — **do not change the signature**.
- How lock works today (`pll.py`): PI loop drives NCO (`kp`/`ki` from bandwidth, lines 42–52); G2 coarse zero-crossing estimator seeds `center_freq` after >100 unlocked samples (lines 205–213); FLL assist feeds `0.02 * (coarse - freq)` into the integrator pre-lock (lines 178–180); B1 disagreement veto blocks lock on 30 consecutive coarse-vs-NCO disagreements (lines 143–152); lock needs 50 consecutive in-band samples (`lock_threshold = 50`, lines 191–198).
- Measured baselines (from `docs/pll_workflow_review_2026-09-13.md`, branch `fix/pll-acquire-and-lock`): 6 Hz locks sample ~51, err ≤0.02; 5 Hz ~470; 4/8/9 Hz ~625–720; rails 3/12 Hz track (err ≤0.05) but **never assert lock** (clamp + coarse-bias deadlock); zero false locks by construction; 4x amplitude jump relocks; suite is 89 passed / 0 failed.
- Hard lesson, do not repeat: `prototype/loop_v2.py` G1 gear-shift (3 Hz wide loop while unlocked) was measured **unstable at unit amplitude** and deliberately NOT ported. Speed up via FLL/G2/coarse paths, never by widening the PI loop.
- Out of scope: body constants (`AMP_GATE`, `PREDICTION_MS`, fusion `W` — need on-device tuning), `fit_main.py` (device-side), bench scoring, CNN (deleted).
- Test commands (Windows, repo venv): `.venv\Scripts\python.exe -m pytest tests/test_pll.py tests/test_suppress.py -q` and full `.venv\Scripts\python.exe -m pytest tests/ -q`. Direct-run style also works: `.venv\Scripts\python.exe tests/test_pll.py` → prints `All PLL tests passed!`.

## Architecture / proposed approach

Pin today's good behavior as regression guardrails first, then attack the two gaps in order: (1) rail-edge lock — diagnose why `lock_count` never reaches 50 at 3/12 Hz, add an explicit rail-agreement lock rule guarded by the same coarse veto that killed the 12 Hz false lock; (2) off-center speed — schedule the FLL assist gain on the coarse-vs-NCO gap and/or refire G2 earlier, tightening horizon bounds only where green. Every change is validated against the full suite plus chain-level (`SuppressStage`) horizon tests.

## Step-by-step tasks

### Task 1 — Pin regression guardrails in `tests/test_pll.py` (all green today)

Append these tests (helper + 6 tests), plus the 6 calls in the `__main__` block before the `print`. All must pass on today's code — if any fails, relax ONLY its bound to measured value + 20% margin and note it here; guardrails pin behavior, they don't fix.

```python
def _samples_to_lock(f0, limit=2000, amp=1.0, glide_to=None):
    """Samples until PLL.locked first True; None if never. glide_to: linear drift target."""
    pll = PLL(fs=100.0, center_freq=6.0, bandwidth=1.0)
    for i in range(limit):
        f = f0 if glide_to is None else f0 + (glide_to - f0) * (i / limit)
        pll.update(amp * math.sin(2 * math.pi * f * (i / 100.0)))
        if pll.locked:
            return i + 1
    return None


def test_center_lock_fast():
    n = _samples_to_lock(6.0)
    assert n is not None and n <= 60, "6 Hz lock took %s samples" % n


def test_no_lock_far_offband():
    """2 Hz and 15 Hz must NEVER lock (guards the 12 Hz false-lock fix)."""
    for f0 in (2.0, 15.0):
        pll = PLL(fs=100.0, center_freq=6.0, bandwidth=1.0)
        for i in range(1200):
            pll.update(math.sin(2 * math.pi * f0 * (i / 100.0)))
        assert pll.locked is False, "false lock at %s Hz" % f0


def test_no_false_lock_4_2hz():
    for _ in range(600):
        pass
    pll = PLL(fs=100.0, center_freq=6.0, bandwidth=1.0)
    for i in range(600):
        pll.update(math.sin(2 * math.pi * 4.2 * (i / 100.0)))
    assert not (pll.locked and abs(pll.freq - 4.2) > 1.0)


def test_drift_6_to_7_follows():
    n = _samples_to_lock(6.0, limit=300)
    assert n is not None
    pll = PLL(fs=100.0, center_freq=6.0, bandwidth=1.0)
    for i in range(300):
        pll.update(math.sin(2 * math.pi * 6.0 * (i / 100.0)))
    for i in range(900):
        f = 6.0 + i / 900.0
        pll.update(math.sin(2 * math.pi * f * (i / 100.0)))
    assert pll.locked and abs(pll.freq - 7.0) < 0.5, "drift ended %.2f locked=%s" % (pll.freq, pll.locked)


def test_amplitude_jump_relocks():
    pll = PLL(fs=100.0, center_freq=6.0, bandwidth=1.0)
    for i in range(300):
        pll.update(math.sin(2 * math.pi * 6.0 * (i / 100.0)))
    assert pll.locked
    for i in range(400):
        pll.update(4.0 * math.sin(2 * math.pi * 6.0 * (i / 100.0)))
    assert pll.locked and abs(pll.freq - 6.0) < 0.5


def test_zero_dc_sine_locks():
    assert _samples_to_lock(6.0, limit=1200) is not None
```

Verify: `.venv\Scripts\python.exe -m pytest tests/test_pll.py -q` → expect `14 passed` (8 existing + 6 new). Then full suite → `95 passed`. Commit: `git add tests/test_pll.py && git commit -m "test: PLL regression guardrails (center speed, offband, drift, amp jump)"`.

### Task 2 — Add lock-horizon ratchet test (green today, tightened later)

Append to `tests/test_pll.py` (+ `__main__` call). Bounds are today's measured values — run first; relax any red bound to measured + 20%:

```python
def test_lock_horizons():
    """Samples-to-lock per tone. Tighten (Task 5), never loosen without a reason in commit msg."""
    bounds = {4.0: 800, 5.0: 600, 6.0: 60, 7.0: 700, 8.0: 800, 9.0: 800}
    for f0, budget in bounds.items():
        n = _samples_to_lock(f0, limit=2000)
        assert n is not None and n <= budget, "%s Hz locked at %s (budget %s)" % (f0, n, budget)
        pll = PLL(fs=100.0, center_freq=6.0, bandwidth=1.0)
        for i in range(n):
            pll.update(math.sin(2 * math.pi * f0 * (i / 100.0)))
        assert abs(pll.freq - f0) < 0.5
```

Verify: `tests/test_pll.py` → `15 passed`; full suite green. Commit.

### Task 3 — Diagnose the rail deadlock (read-only, no fix yet)

Add a temporary probe to `tests/test_pll.py` (delete it in Task 4), run, and record the finding under "Rail diagnosis log" at the bottom of THIS plan file:

```python
def test_rail_probe_tmp():
    for f0 in (3.0, 12.0):
        pll = PLL(fs=100.0, center_freq=6.0, bandwidth=1.0)
        print("\n--- target %s Hz ---" % f0)
        for i in range(1200):
            pll.update(math.sin(2 * math.pi * f0 * (i / 100.0)))
            if i % 100 == 0:
                print("n=%4d freq=%5.2f perr=%+.3f disagree=%d lock_count=%d locked=%s coarse=%.2f" % (
                    i, pll.freq, pll.phase_error_filtered, pll._disagree_n,
                    pll.lock_count, pll.locked, pll._cslow))
```

Run: `.venv\Scripts\python.exe -m pytest tests/test_pll.py::test_rail_probe_tmp -q -s`. Expected shape: freq pinned at rail, `lock_count` repeatedly resetting — the log must say WHICH reset fires (`perr > 0.2` vs `disagree >= 30`, lines 196–198) and whether coarse (`_cslow`) sits biased off the rail. Do not commit the probe. No code change in this task.

### Task 4 — Honest rail-edge lock (red → green)

1. Write failing tests first in `tests/test_pll.py` (verify red with pytest):
```python
def test_rail_3hz_locks():
    n = _samples_to_lock(3.0, limit=1500)
    assert n is not None and n <= 1200, "3 Hz never locked"
    # ...and it locked AT the rail, not below it (the old 12 Hz failure mode):
    pll = PLL(fs=100.0, center_freq=6.0, bandwidth=1.0)
    for i in range(n):
        pll.update(math.sin(2 * math.pi * 3.0 * (i / 100.0)))
    assert abs(pll.freq - 3.0) < 0.5


def test_rail_12hz_locks():
    n = _samples_to_lock(12.0, limit=1500)
    assert n is not None and n <= 1200, "12 Hz never locked"
    pll = PLL(fs=100.0, center_freq=6.0, bandwidth=1.0)
    for i in range(n):
        pll.update(math.sin(2 * math.pi * 12.0 * (i / 100.0)))
    assert abs(pll.freq - 12.0) < 0.5
```
2. Fix in `firmware/common/pll.py` lock-detection block (lines 191–198), guided by the Task 3 finding. Starting-point candidate (adapt, don't blindly paste): hoist `fcoarse = min(12.0, max(3.0, self._cslow))` above the agree block; add `at_rail = self.freq <= 3.15 or self.freq >= 11.85`; `rail_ok = self._cross_n >= 3 and abs(fcoarse - self.freq) < 0.5`; change the lock condition to `abs(perr) < 0.1 and (agree or (at_rail and rail_ok))`. The coarse veto stays authoritative everywhere else — that is what keeps `test_no_lock_far_offband` (2/15 Hz) green.
3. Delete the Task 3 probe. Verify: new tests green AND full suite green (especially `test_no_lock_far_offband`, `test_no_false_lock`, `test_pll_no_false_lock` — any false lock = revert the fix, not the tests). Commit.

### Task 5 — Faster off-center lock (red → green, with rollback rule)

1. Tighten `test_lock_horizons` bounds to the goal: `{4.0: 400, 5.0: 400, 7.0: 400, 8.0: 400, 9.0: 400}` (keep 6.0 at 60). Verify red.
2. Try in order, keep the first that greens the bounds, revert the rest:
   a. FLL gain schedule: in `pll.py` line 180, replace fixed `0.02` with gap-proportional `0.02 + 0.06 * min(1.0, abs(fc_now - self.freq) / 2.0)` (big gap = hard pull, near truth = today's gentle 0.02).
   b. Earlier G2 refire: line 207 `self._unlocked_n > 100` → `> 60`.
   c. FLL maturity gate: line 178 `self._cross_n >= 8` → `>= 5`.
3. **Rollback rule (non-negotiable, the gear-shift lesson):** if 6 Hz exceeds 60 samples, ANY false-lock test fails, or steady-state err exceeds 0.1 Hz anywhere, revert the change and record the attempt + numbers in the commit message. Never widen kp/ki (no G1).
4. Verify full suite green. Tighten only the bounds that stayed green; leave the rest at Task 2 values. Commit.

### Task 6 — Chain-level horizons in `tests/test_suppress.py`

Mirror the existing `test_x_only_tremor_tracks_6hz` pattern (frontend = bandpass 3–12 Hz + dominant-axis, gravity on z). Append (+ `__main__` calls):

```python
def test_chain_4hz_locks_in_budget():
    stage = SuppressStage(fs=100.0, pll_bandwidth=1.0)
    locked_at = None
    for i in range(1200):
        t = i / 100.0
        stage.process_sample(0.15 * math.sin(2 * math.pi * 4.0 * t), 0.0, 1.0)
        if stage.pll.locked:
            locked_at = i + 1
            break
    assert locked_at is not None and locked_at <= 900, "chain 4 Hz locked at %s" % locked_at
    assert abs(stage.pll.freq - 4.0) < 0.5


def test_chain_8hz_locks_in_budget():
    stage = SuppressStage(fs=100.0, pll_bandwidth=1.0)
    locked_at = None
    for i in range(1400):
        t = i / 100.0
        stage.process_sample(0.15 * math.sin(2 * math.pi * 8.0 * t), 0.0, 1.0)
        if stage.pll.locked:
            locked_at = i + 1
            break
    assert locked_at is not None and locked_at <= 1100, "chain 8 Hz locked at %s" % locked_at
    assert abs(stage.pll.freq - 8.0) < 0.5
```

If red after Tasks 4–5, fix forward in `pll.py` (chain adds frontend lag — prefer raising ONLY the test bound to measured + 20% over touching loop gains for the chain's sake). Verify: `tests/test_suppress.py` green + full suite green. Commit.

### Task 7 — Docs + final gate

1. Update the post-fix sweep tables in `docs/pll_workflow_review_2026-09-13.md` with the new horizons, rail-lock rows, and anything from the Rail diagnosis log.
2. Final gate: `.venv\Scripts\python.exe -m pytest tests/ -q` → all passed (baseline 89 + 6 guardrails + 1 horizon + 2 rail + 2 chain = 100). Commit docs.

## Tests / validation

TDD per task: failing test → run to verify the failure → minimal implementation → run to verify pass → full suite → commit. No task is done until `.venv\Scripts\python.exe -m pytest tests/ -q` is fully green. Direct-run style (`.venv\Scripts\python.exe tests/test_pll.py`) must also print its pass line, since device-side history uses it.

## Risks, tradeoffs, and open questions

- **False-lock regression is the top risk.** 12 Hz locked falsely before; the rail task explicitly re-opens that door. Mitigation: offband tests (2/15 Hz) + 4.2 Hz + existing 12 Hz veto tests run on every change; any failure reverts the fix, never the test.
- **Speed vs honesty tradeoff.** Faster pull (higher FLL gain, earlier refire) declaration-earlier risk — the loop2 failure mode (claimed lock 0.1–0.4 Hz off). The `abs(freq - f0) < 0.5` post-lock asserts plus err ≤0.1 steady-state checks exist to catch exactly this.
- **Perf on ESP32.** FLL schedule adds ~3 float ops/sample; rail rule adds ~2 comparisons. Negligible vs the per-sample `sin/cos`. No new state except at most 1–2 floats — MicroPython heap-safe. Still, keep `update()` allocation-free (no new lists/dicts).
- **Product question:** is lock AT 3/12 Hz even wanted, or should rails stay honestly-unlocked by design (tremor fundamentals rarely sit on the rails; bandpass rolls off there anyway)? If the answer is "rails stay unlocked," delete Task 4's tests, keep the diagnosis log, and skip to Task 5.
- **Target numbers are guesses.** 400-sample off-center and 1200-sample rail budgets come from today's 470–720 measurements plus margin, not from a product requirement. If wear testing later says 5 s lock is fine, Task 5's tightening is optional — say so in its commit.
- **Drift re-lock after Task 5.** Faster FLL changes drift-out behavior; `test_drift_6_to_7_follows` guards it, but long dwells (>30 s) and repeated in/out crossings are untested — note as future work, don't expand this plan.

## Rail diagnosis log

Task 3 probe output (2026-09-13, branch fix/pll-acquire-and-lock, today's code):

--- target 3.0 Hz ---
n=   0 freq= 6.00 perr=+0.000 disagree=0 lock_count=1 locked=False coarse=6.00
n= 100 freq= 6.01 perr=+0.130 disagree=0 lock_count=0 locked=False coarse=4.45
n= 200 freq= 4.01 perr=+0.161 disagree=0 lock_count=3 locked=False coarse=3.55
n= 300 freq= 3.15 perr=-0.432 disagree=0 lock_count=0 locked=False coarse=3.24
n= 400 freq= 3.03 perr=-0.404 disagree=0 lock_count=0 locked=False coarse=3.14
n= 500 freq= 3.02 perr=-0.389 disagree=0 lock_count=0 locked=False coarse=3.11
n= 600 freq= 3.02 perr=-0.376 disagree=0 lock_count=0 locked=False coarse=3.10
n= 700 freq= 3.02 perr=-0.362 disagree=0 lock_count=0 locked=False coarse=3.10
n= 800 freq= 3.02 perr=-0.346 disagree=0 lock_count=0 locked=False coarse=3.10
n= 900 freq= 3.03 perr=-0.328 disagree=0 lock_count=0 locked=False coarse=3.10
n=1000 freq= 3.03 perr=-0.308 disagree=0 lock_count=0 locked=False coarse=3.10
n=1100 freq= 3.03 perr=-0.285 disagree=0 lock_count=0 locked=False coarse=3.10

--- target 12.0 Hz ---
n=   0 freq= 6.00 perr=+0.000 disagree=0 lock_count=1 locked=False coarse=6.00
n= 100 freq= 6.79 perr=-0.139 disagree=0 lock_count=0 locked=False coarse=8.12
n= 200 freq= 9.50 perr=+0.050 disagree=79 lock_count=0 locked=False coarse=10.35
n= 300 freq=11.06 perr=+0.091 disagree=0 lock_count=2 locked=False coarse=11.35
n= 400 freq=11.70 perr=+0.453 disagree=0 lock_count=0 locked=False coarse=11.71
n= 500 freq=11.97 perr=+0.321 disagree=0 lock_count=0 locked=False coarse=11.82
n= 600 freq=11.99 perr=+0.288 disagree=0 lock_count=0 locked=False coarse=11.85
n= 700 freq=11.99 perr=+0.272 disagree=0 lock_count=0 locked=False coarse=11.86
n= 800 freq=11.99 perr=+0.255 disagree=0 lock_count=0 locked=False coarse=11.86
n= 900 freq=11.99 perr=+0.236 disagree=0 lock_count=0 locked=False coarse=11.87
n=1000 freq=11.99 perr=+0.215 disagree=0 lock_count=0 locked=False coarse=11.87
n=1100 freq=11.99 perr=+0.188 disagree=0 lock_count=0 locked=False coarse=11.87

Verdict: the resetting branch is `abs(perr) > 0.2` (pll.py:196), NOT the
`_disagree_n >= 30` veto — steady-state disagree=0 at both rails, so coarse
agrees with the NCO and the veto is silent. Mechanism: NCO freq converges to
the rail (3.02 / 11.99) but a steady-state phase offset freezes in — the clamp
+ integrator anti-windup forbids the sub-rail transient the loop would need to
unwind phase, so |perr| parks at 0.29–0.43 (3 Hz) / 0.19–0.45 (12 Hz) and never
enters the <0.1 lock band; lock_count resets forever. Coarse sits slightly
biased off-rail (3.10 / 11.87) but inside the 0.5 agree band, so a rail rule
gated on coarse agreement + mature crossings is safe. (perr decays slowly —
12 Hz eventually locks ~1245 samples — but that is not an honest horizon.)
Probe deleted in Task 4.
