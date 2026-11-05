# Pilot collection protocol - live 100 Hz training data

Goal: multi-class native-rate sessions that train_classifier.py can eat directly.
Minimum per class: 50 windows (~65 s). Recommended: 100 windows (~2 min).

## Classes and tasks (do all four, same wearer, same mount)
- rest: hands flat on table, fingers relaxed, breathe normally.
- postural: seated, both arms extended forward, palms down, hold still.
- kinetic: repeated finger-to-nose motion at comfortable pace.
- baseline: everyday motion - typing, phone use, pouring water.

## Device side (Thonny REPL, board running MicroPython)
1. Copy firmware/ to the board (collect_pilot.py for single IMU,
   raw_data_collection.py for 4-IMU multi capture).
2. Per class, run one session block, e.g.:
     from collect_pilot import PilotCollector
     PilotCollector(label='postural', session_seconds=130, sessions_total=1).run()
   For 4-IMU: from raw_data_collection import MultiIMUCollector
     MultiIMUCollector(label='postural', session_seconds=130, sessions_total=1).run()
   130 s at 1.28 s/window yields ~100 windows with margin.
3. LED on means recording. Do the task only while the LED is on.

## Host side (repo root, plain python)
Find the serial port (Device Manager, e.g. COM5), then per session:
  python host_scripts/capture_session.py --port COM5 --label postural \
      --out host_scripts/sessions/live_postural_s01.csv \
      --aux host_scripts/sessions/live_postural_s01_multi.csv
Single-IMU runs print only train lines; --aux may stay empty, that is fine.
Start capture BEFORE starting the device session; stop with Ctrl-C after.

## QC after each session (must all pass before training)
  python -c "import sys; sys.path.insert(0,'host_scripts');" \
      "from train_classifier import parse_file;" \
      "l,a=parse_file('host_scripts/sessions/live_postural_s01.csv');" \
      "print(len(l), 'windows, labels:', sorted(set(l)))"
Expect: >= 50 windows, exactly one label, zero skips reported by capture.
Spot-check z-axis mean near 1.0 g (gravity present, sensor alive).

## Retrain once all four classes exist
  python host_scripts/train_classifier.py host_scripts/sessions/live_*.csv
  python host_scripts/train_classifier.py --dnn host_scripts/sessions/live_*.csv
Gates: >= 2 classes to train at all; DNN CV must beat logreg CV before baking
into firmware/common/model_dnn.py (same paste-block procedure as the Parkinson bake).
Then rerun the full test suite; test_dnn_pipeline asserts the DNN path.

