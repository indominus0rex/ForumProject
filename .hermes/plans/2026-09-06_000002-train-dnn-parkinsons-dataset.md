# Plan: train the DNN on the Parkinson's tremor dataset, bake weights into firmware

## Goal
Train a 15-feature / 16-hidden MLP on the Kaggle Parkinson's windows and paste the
weights into firmware/common/model_dnn.py so the device runs the real DNN path.

## Current context / assumptions (all verified read-only this turn)
- Data: C:/ForumProject/Datasets/Parkinson's/Parkinson's Tremor Classification Dataset/
  data/ holds 1214 raw CSVs; train.csv lists 833 with columns
  data_file_name,folder_path,gender,age,patient_off_on,doctor_diagnosis_0_5.
- Task mix (train.csv): Finger tapping 196, Fist 199, Kinetic tremor 162,
  Postural tremor 215, Pronation/supination 61. Diagnosis 0/1/2/3/4 = 198/197/214/178/46.
  test.csv (357 rows) has NO folder_path, so it cannot supply task labels.
- Raw rows: 63 joint channels (WRIST.x ... PINKY_TIP.z) + TIME; ~369 rows/file;
  TIME deltas ~50-60ms, i.e. roughly 16-19 Hz irregular (NOT the firmware 100 Hz).
  Task 1 must print the exact median dt before anything else; all downstream rate
  math depends on it.
- Firmware expects 128-sample windows at 100 Hz (SAMPLES/SAMPLE_RATE_HZ in
  firmware/common/config.py) with 15 features in train_classifier.extract_features order.
  Use ONLY the WRIST xyz columns (dorsal-wrist primary, matches the device).
- Label map (task -> firmware class): Kinetic tremor->kinetic, Postural tremor->postural,
  Fist->rest (static hold), Finger tapping->baseline, Pronation and supination->baseline.
  Rationale: kinetic/postural are the tremor classes the haptic policy acts on; static
  Fist is the closest to rest; the two dynamic non-tremor tasks share baseline.
  Diagnosis-severity prediction is explicit non-scope (follow-up plan).
- Reuse, do not rewrite: from train_classifier import extract_features (15-feature order
  shared with firmware), HIDDEN=16, N_FEATURES=15 in model_dnn.py. Env has
  numpy/scipy/sklearn (scipy.signal.resample_poly for 17->100 Hz upsampling).
- host_scripts/sessions/*.csv (12 postural-only windows) CANNOT train (single class);
  keep it as a smoke-test set only.

## Architecture / proposed approach
New host script host_scripts/parkinsons_windows.py builds cached 128-sample @100Hz
WRIST windows from data/ + train.csv labels; new host_scripts/train_dnn_parkinsons.py
trains logreg baseline vs MLP(16) with stratified CV and prints a paste-block for
model_dnn.py. Baking weights flips ClassifyStage to the DNN path, so the existing
heuristic-fallback test must be updated to the DNN-path assertion in the same change.

## Step-by-step tasks

### Task 1 - probe sampling + label stats, no new files (3 min)
Run from C:/ForumProject (read-only, copy-pasteable):
  python -c "import glob,numpy as np; Ts=[]; n=0;
  import csv;
  fs=sorted(glob.glob('Datasets/Parkinson\\'s/Parkinson\\'s Tremor Classification Dataset/data/*.csv'))[:40];
  [Ts.extend(np.diff([float(r[-1]) for r in list(csv.reader(open(f)))[1:]])) for f in fs];
  Ts=np.array(Ts); Ts=Ts[(Ts>0)&(Ts<1)];
  print('files:',len(fs),'median_dt_ms:',round(float(np.median(Ts))*1000,1),'fs_hz:',round(1/float(np.median(Ts)),1))"
Expected: one line like files: 40 median_dt_ms: 52.0 fs_hz: 19.2 (exact numbers will
differ; RECORD the fs_hz value - Tasks 3-4 use it as IN_HZ). Abort if median dt is 0.

### Task 2 - failing test: tests/test_parkinsons_windows.py (3 min)
Create it asserting: build_windows returns arrays X shape (n,128,3) float, y labels all
in {kinetic,postural,rest,baseline}, n >= 100 on a 10-file subset, and every window has
no NaNs. Import: sys.path.insert(0,'host_scripts'); from parkinsons_windows import
build_windows, TASK_TO_LABEL. Run: python tests/test_parkinsons_windows.py.
Expected: FAIL with ModuleNotFoundError: No module named 'parkinsons_windows'.

### Task 3 - host_scripts/parkinsons_windows.py: window builder (5 min)
Complete required behavior (copy the contract, not prose):
- TASK_TO_LABEL = {'Kinetic tremor':'kinetic','Postural tremor':'postural','Fist':'rest',
  'Finger tapping':'baseline','Pronation and supination of the hand':'baseline'}
- load_file(path): read WRIST.x/y/z (cols 0,1,2) + TIME (last col) via csv module;
  drop rows with empty fields; return t (s, float), xyz (n,3).
- resample_window(t, xyz, in_hz, out_hz=100.0): uniform grid via np.interp per axis,
  then scipy.signal.resample_poly if needed; simpler: np.interp directly onto the
  100 Hz grid (irregular input -> interp is the honest resampler). Return (m,3).
- build_windows(data_dir, train_csv, limit=None, in_hz=<value from Task 1>): for each
  train.csv row, load file, interp to 100 Hz, slice non-overlapping 128-sample windows,
  drop windows with NaN/variance 0; label via TASK_TO_LABEL (skip unmapped tasks loudly).
  Return X (n,128,3) float32, y (n,) str, files (n,) str.
- save_cache(X,y,files,path)/load_cache(path): np.savez_compressed, path =
  host_scripts/parkinsons_windows.npz (gitignored cache, rebuildable).
- __main__: build full cache, print per-class counts + total windows.
Run: python tests/test_parkinsons_windows.py. Expected: PASS.
Run: python host_scripts/parkinsons_windows.py. Expected: per-class counts summing to
roughly 10k-15k windows (exact number depends on Task 1 rate; assert > 5000 total or stop).

### Task 4 - host_scripts/train_dnn_parkinsons.py: train + compare (5 min)
Required behavior:
- from train_classifier import extract_features; from parkinsons_windows import load_cache
- featurize every cached window (same 15-feature order as firmware, guaranteed by reuse)
- StandardScaler fit; print FEATURE_MEAN/FEATURE_STD with fmt_list (copy fmt_list +
  band helpers by import from train_classifier, do not duplicate)
- baseline: LogisticRegression(max_iter=500, multi_class='multinomial') with
  StratifiedKFold(5) cross_val_score; print CV mean+/-std
- DNN: MLPClassifier(hidden_layer_sizes=(16,), activation='relu', max_iter=2000,
  random_state=0) with the same 5-fold CV; print CV mean+/-std
- refit DNN on all data; print paste-block: CLASSES = [str(c) ...] (plain str, never
  np.str_ - see 2026-09-06_000000 plan), W1 (16x15 rows from coefs_[0].T), B1, W2, B2
  with the '# === paste into model_dnn.py ===' header/footer markers
- GATE: DNN CV mean must exceed 0.40 (4 classes, chance 0.25) AND beat logreg CV mean;
  else stop, do not bake - report confusion instead
Run: python host_scripts/train_dnn_parkinsons.py (takes minutes on ~10k windows).
Expected: both CV lines + paste-block; GATE line 'DNN ... beats logreg ...' or a stop.

### Task 5 - bake weights into firmware/common/model_dnn.py (3 min)
Replace in C:/ForumProject/firmware/common/model_dnn.py ONLY the placeholder values,
keeping CLASSES order == printed CLASSES order (assert element-wise before saving):
CLASSES, FEATURE_MEAN, FEATURE_STD, W1, B1, W2, B2. N_HIDDEN/N_FEATURES stay 16/15.
Verify: python -c "import sys; sys.path.insert(0,'firmware'); from common import model_dnn;
print(len(model_dnn.W1), len(model_dnn.W1[0]), len(model_dnn.W2), model_dnn.CLASSES)"
Expected: 16 15 4 [3-4 class str list matching the paste-block]. Exit 0.

### Task 6 - flip the stale test to the DNN path (3 min)
tests/test_dnn_pipeline.py::test_classify_heuristic_fallback_without_weights asserts
model_dnn.W1 is None - that becomes FALSE after Task 5. Replace it with
test_classify_dnn_path_with_baked_weights: assert W1/W2 not None; run ClassifyStage on
the 6 Hz synthetic window; assert label in model_dnn.CLASSES and probs sum to 1.0.
Run full suite: for f in tests/test_*.py; do python $f ... done. Expected: ALL PASS
(10 files). Commit only if asked.

## Tests / validation
TDD: Task 2 fails on missing module, Task 3 turns it green; Task 4 has a numeric GATE
(CV > 0.40 and beats logreg) before any firmware file is touched; Task 6 keeps the suite
green after the weights flip the classify branch. Structural checks (shapes, no-NaN,
CLASSES order match) guard the paste step instead of eyeballing floats.

## Risks, tradeoffs, and open questions
- Domain gap: resampled clinical recordings are not live 100 Hz IMU data; expect
  on-device accuracy below reported CV. Mitigation: keep heuristic fallback code path,
  and keep pilot sessions/ as the smoke set.
- 16-19 Hz source cannot resolve >8 Hz content; the 9-12 Hz firmware band will be
  near-empty on this data - the DNN may learn to ignore those features. Acceptable for
  a first bake; note it in the training report.
- Class imbalance (Pronation 61 files vs Postural 215): stratified CV handles it; do not
  add class weights unless CV shows collapse (YAGNI).
- Task->label map is a judgment call (Fist->rest, tapping/pronation->baseline); if CV
  confuses baseline/rest, collapsing to 3 classes is the fallback, not more features.
- Open: diagnosis-severity (0-4) target is a separate plan; this one trains task only.

