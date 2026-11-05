# Plan: research-grounded new pipeline - 1D-CNN perception, LSTM onset gate, phase-burst actuation

## Goal
Replace all three stages of the current pipe with published methods this project has never
used: 1D-CNN classifier on raw windows, LSTM tremor-persistence gate, phase-tracking burst
LRA drive with per-tremor-type targets (pill 4-6 Hz, ET 6-9 Hz).

## Research anchors (repo research/ survey)
- research-08: 1D-CNN beats MLP on sensor time series (local temporal patterns).
- research-01 Felix NeuroAI: LSTM onset prediction 89.5%, stimulate only when needed.
- research-01 IEEE TNSRE 2026: wrist-worn adaptive phase-tracking bursts for PD rest tremor.
- research-01 scoping review: accelerometers are the dominant input (26 studies).

## Phase 1 (this execution): 1D-CNN classifier with bake-gate discipline
1. Check framework: torch preferred (CPU), fallback tensorflow, last resort numpy-only
   separable-conv trainer. Install via uv pip if missing.
2. New host_scripts/train_cnn1d_parkinsons.py: rebuild window cache via parkinsons_windows
   (deleted after bake, rebuild ~15 s), train small 1D-CNN
   (Conv1D k5 + ReLU + MaxPool, Conv1D k3 + ReLU + GlobalAvgPool, Dense 32, softmax)
   on raw 128x3 windows with the same TASK_TO_LABEL map and stratified CV; compare
   against the baked MLP CV 0.750. GATE: CNN CV beats 0.750 or stop with report.
3. Port: quantize to int8-ish scaled integers, implement firmware/common/cnn1d.py forward
   (pure python conv/pool/dense, mirror common/dnn.py style), bake into
   firmware/common/model_cnn.py, add tests/test_cnn1d.py (forward math + baked-shape
   assertions + one synthetic-window classification).
4. Swap ClassifyStage backend MLP->CNN behind the same heuristic fallback; full suite green.

## Phase 2 (follow-up plan): LSTM persistence gate replacing label-threshold gating.
## Phase 3 (follow-up plan): burst actuation replacing continuous PLL PWM, bench-tuned.

## Risks
- 22 Hz source data caps learnable content above ~8 Hz (carried-over weakness).
- No torch/TF on box: fall back to smaller install or numpy trainer, do not invent weights.
- ESP32 integer forward must match host float within tolerance: assert max-abs-diff in test.

