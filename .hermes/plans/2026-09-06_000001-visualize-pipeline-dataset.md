# Plan: visualize the bandpass -> FFT -> DNN pipeline on host_scripts/sessions/

## Goal
Add one script that runs every dataset window through the new pipeline stages and
saves one PNG per window (raw vs bandpassed trace, spectrum with tremor bands,
predicted label/state) so the switch can be eyeballed.

## Current context / assumptions (all verified read-only this turn)
- Dataset: C:/ForumProject/host_scripts/sessions/*.csv, 6 files x 2 windows = 12
  windows, ALL labeled postural. Row format: LABEL + 384 floats (128x3).
- Reuse parse_file() from C:/ForumProject/host_scripts/train_classifier.py
  (returns labels + float32 array shaped (n_win, 128, 3)). Do not rewrite a parser.
- Host-safe stages (pure python, no machine import): QualityStage, BandpassStage,
  FFTStage, FeaturesStage, ClassifyStage, TremorStateMachine. Import with
  sys.path.insert(0, 'firmware') like tests/test_common.py does.
  Do NOT import SensorStage (needs machine.I2C), HapticStage (machine),
  AuditStage (time.ticks_ms is MicroPython-only).
- Env: venv python 3.11 has numpy/sklearn/scipy but NO matplotlib.
  uv is at /c/Users/Admin/AppData/Local/hermes/bin/uv; install matplotlib via uv.
- Existing plot reference (different CSV layout, not directly reusable):
  Datasets/Parkinson's/Parkinson's Tremor Classification Dataset/data_by_diagnosis/plot_tremor_data.py

## Architecture / proposed approach
One host-only script, host_scripts/visualize_pipeline.py. Firmware stages produce
the numbers (dominant freq, label, confidence, state); numpy/matplotlib only draw.
Per-window figure (3 stacked axes: traces, spectrum with 3-6/6-9/9-12 shading,
decision text) plus a printed summary table. A thin test asserts PNGs are created.

## Step-by-step tasks

### Task 1 - install matplotlib (2 min)
Run from C:/ForumProject:  uv pip install matplotlib
Expected: Successfully installed ... Verify: python -c "import matplotlib" exits 0.

### Task 2 - failing test first: tests/test_visualize.py (3 min)
Create the file with a test that imports run_all from visualize_pipeline, runs it
on host_scripts/sessions into a temp dir, and asserts 12 PNGs exist each > 5000 bytes.
Run: python tests/test_visualize.py from C:/ForumProject.
Expected: FAIL with ModuleNotFoundError: No module named 'visualize_pipeline'.
Do not proceed until you see this exact failure.

### Task 3 - implement host_scripts/visualize_pipeline.py (5 min)
Full required content (copy exactly, keep the __main__ guard so the test import
has no side effects):
- backend Agg; sys.path inserts for firmware and the script dir
- from train_classifier import parse_file
- from stages.bandpass/fft/features/classify/quality/state_machine import the stages
- run_window(window_128x3_array) -> dict:
    rows = [[float(x),float(y),float(z)] for each sample]
    raw_mag = [sqrt(x*x+y*y+z*z) per row]
    frame = {window copy, x/y/z = last row}; QualityStage; if quality_ok:
      BandpassStage(fs=100) -> FFTStage(128,100) -> FeaturesStage -> ClassifyStage
      -> TremorStateMachine; filt window -> filt_mag; numpy rfft spectrum of
      mean-centered raw_mag with Hann window; return traces + quality_reason +
      dominant_freq + label/confidence (default label 'rejected' if gated) + state/action
- plot_window(res, title, out_path): 3 stacked axes (traces with legend; spectrum
  xlim 0-25Hz with axvspan shading per BANDS; text axis with quality/dominant/label/state)
  savefig dpi=100, plt.close(fig)
- run_all(sessions_dir, out_dir): mkdir -p out; for each *.csv sorted: parse_file,
  per window plot to {stem}_{i:02d}_true-{true}_pred-{pred}.png, print one summary line
  per window; print total; return count
- main(): argparse --sessions (default host_scripts/sessions) --out (default
  analysis/figures); calls run_all
Run: python tests/test_visualize.py from C:/ForumProject. Expected: PASS.
If a window fails quality it still prints with label 'rejected' - by design, not a bug.

### Task 4 - full run + regression check (3 min)
Run: python host_scripts/visualize_pipeline.py from C:/ForumProject.
Expected: 12 summary lines (quality=ok dom=..Hz label=.. conf=.. state=..) and
'wrote 12 PNGs to analysis/figures'. Verify: ls analysis/figures/*.png shows 12 files.
Then: for f in tests/test_*.py; do python $f ... done - all PASS (9 files).
Commit only if asked.

## Tests / validation
TDD: Task 2 shows the import failure; Task 3 turns it green; Task 4 is the
end-to-end gate (12 PNGs + full suite). Host venv python only, no device needed.

## Risks, tradeoffs, and open questions
- All 12 windows are postural: plots validate signal flow, not class separation.
- model_dnn weights are still None, so labels come from the heuristic fallback;
  do not present the plots as DNN accuracy proof.
- PNG-count assertion (12) is brittle if sessions/ grows; loosen to n >= 1 then.
- Open: per-window figures vs one summary grid. This plan picks per-window + text
  table (cheapest useful); a summary grid is explicit follow-up, not in scope.

