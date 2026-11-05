# Plan: hybrid gated pipeline - DNN supervises, PLL actuates

## Goal
Drive the LRA with phase-coherent anti-phase PWM from the PLL chain, enabled only when
the DNN supervisory path reports tremor, replacing today's fixed-pattern haptic blink.

## Current context / assumptions (verified this turn)
- Supervisory path (built, trained, baked): quality -> bandpass -> fft -> features ->
  classify (MLP, CV 0.75) -> state_machine. Frame carries label/confidence/state/action
  where action is one of none/observe/cue_low/cue_high.
- Actuation pieces (kept, tested, currently unwired): stages/suppress.py SuppressStage
  with process_sample(x,y,z)->duty (bandpass->PLL->predictor->anticancel->adaptive gain),
  reset(), get_status(). HapticStage already prefers frame[suppress_duty] when present
  (haptic.py lines 44-49) and falls back to label blink when absent - so wiring a new
  stage that sets suppress_duty needs zero haptic changes.
- No ISR surgery: the timer callback stays sample-fill only. Actuation replays the
  completed 128-sample window through process_sample in the main loop (pure python,
  ~128 x small-float ops, measured < 50 ms on host; assert < 200 ms on first device run).
- Honesty note: output lags one window (1.28 s). This is window-rate feedforward, not
  sample-real-time cancellation. Phase is coherent within the replayed window.

## Architecture / proposed approach
New stages/actuate.py ActuationStage sits between state_machine and haptic. It reads
action/confidence/quality_ok, replays frame[window] through an owned SuppressStage when
action is cue_low/cue_high, writes suppress_duty (0 plus a reset() of PLL state when
gated off, so lock never carries across non-tremor gaps). Kinetic scales duty 1.0,
postural 0.5. STAGE_ORDER gains 'actuate'; embedded_main_hsp.py instantiates it.

## Step-by-step tasks

### Task 1 - failing test: tests/test_actuate.py (3 min)
Create it. Imports: sys.path firmware; from stages.actuate import ActuationStage;
make a 6 Hz gravity window (same helper shape as test_dnn_pipeline.make_window).
Three tests: (a) enabled frame (action cue_high, confidence 0.9, quality_ok True, safe
True) -> suppress_duty is int in 0..1023 and pll state keys exist; (b) gated frame
(action none) -> suppress_duty == 0 and stage pll locked is False after a prior enabled
run (reset proof); (c) postural scales: cue_low duty <= cue_high duty on the same window.
Run: python tests/test_actuate.py. Expected: FAIL ModuleNotFoundError stages.actuate.

### Task 2 - firmware/stages/actuate.py (5 min)
Required contract (copy exactly):
- class ActuationStage with __init__(fs=100.0, pll_bandwidth=1.0, prediction_ms=15.0,
  initial_gain=0.5, kinetic_scale=1.0, postural_scale=0.5); owns SuppressStage(fs,
  pll_bandwidth, prediction_ms, initial_gain). No machine/time imports (host-testable).
- process(frame): if not frame.get(quality_ok, True) or not frame.get(safe, True) or
  frame.get(action) not in (cue_low, cue_high): self._sup.reset(); frame[suppress_duty]=0;
  frame[actuation_reason]= gated:<reason>; return frame.
- else: duties = [self._sup.process_sample(r[0],r[1],r[2]) for r in frame[window]];
  duty = median of last 32 duties, scaled (kinetic 1.0 / postural 0.5), clamped 0..1023 int;
  frame[suppress_duty]=duty; frame[pll_locked]=self._sup.pll.locked;
  frame[actuation_reason]= actuate:<label>:<duty>; return frame.
- Median (not mean, not last): robust to single-sample spikes; last-32 window favors
  settled PLL over window-start transient.
Run: python tests/test_actuate.py. Expected: PASS.

### Task 3 - wire STAGE_ORDER + dispatcher (3 min)
- stages/__init__.py: insert actuate between state_machine and haptic in STAGE_ORDER.
- embedded_main_hsp.py: re-add PLL_BANDWIDTH_HZ, PREDICTION_MS, ADAPTIVE_GAIN_INITIAL to
  the config import (BANDPASS/QUALITY/CONF/STATE imports from the DNN switch stay);
  add from stages.actuate import ActuationStage; add stages dict entry actuate with
  fs=SAMPLE_RATE_HZ and the three config values. Do NOT re-add SuppressStage itself.
Verify: python -m py_compile firmware/embedded_main_hsp.py firmware/stages/actuate.py &&
echo COMPILE_OK. Expected: COMPILE_OK, exit 0.

### Task 4 - end-to-end replay on real data + full suite (5 min)
Add to tests/test_actuate.py a replay test: load the first window of
host_scripts/sessions/pre_postural_s01.csv via train_classifier.parse_file, run the full
host-safe chain quality->bandpass->fft->features->classify->state_machine->actuate, assert
suppress_duty in 0..1023 with no exceptions, and print the duty + label (human check that
a real postural window produces nonzero actuation).
Run full suite: for f in tests/test_*.py; do python $f ... done. Expected: ALL PASS
(10 files). Commit only if asked.

### Task 5 - device timing assertion (follow-up, needs hardware, not this turn)
On the ESP32, time the actuate replay over one window; assert < 200 ms so the main loop
keeps up at 100 Hz sampling. If slower, reduce replay to last-64 samples (edit one slice
in actuate.py, re-run tests). Do not guess this on host.

## Tests / validation
TDD: Task 1 fails on missing module, Task 2 greens it (incl. reset-clears-lock proof),
Task 3 compile-gates the dispatcher (device file cannot run on host), Task 4 replays a
real dataset window and holds the whole suite green.

## Risks, tradeoffs, and open questions
- One-window lag is inherent to replay-after-window; true per-sample ISR actuation is a
  separate hard-real-time plan, not this one.
- Median-of-32 on a 6 Hz tremor (~16 samples/cycle) spans ~2 cycles: stable but slow to
  track amplitude jumps; acceptable for first fusion, tune later.
- Coherence/multi-IMU features and severity targets stay out of scope (noted follow-ups).
- Open: kinetic 1.0 / postural 0.5 scales are starting guesses; calibrate against the
  Task 4 printed duties on real windows before hardware trials.

