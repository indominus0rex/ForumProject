# plan_b — thin fallback combos (small-fit alternatives to plan_a)

Plan B = thin wiring only. DSP math lives in `firmware/common/` and
`firmware/stages/` (shared with Plan A). Each combo exposes
`NAME / DESCRIPTION / PERCEPTION / SUPPRESSION / GATE_OK / Combo`
(see `firmware/plan_b/__init__.py`).

## Combos

| Name | Perception | Suppression | Needs weights | Note |
|---|---|---|---|---|
| b1_safe | heuristic 3-12 Hz peak | fixed-duty haptic | no | runs with nothing baked |
| b2_baseline_ml | logreg | haptic | `common/model.py` | baseline ML |
| b3_current_best | DNN | full PLL + adaptive gain | `common/model_dnn.py` | reference best |
| b4_pll_only | none | full PLL + adaptive gain | no | no classifier |
| b5_fixed_gain | DNN gate | fixed-gain PLL | `common/model_dnn.py` | no adaptation |
| b7_fit | none (amp + lock gates) | PLL, fused multi-IMU, dominant-axis, normalized drive | no | DevKitC fit build (device entry `fit_main.py`, not versioned here) |

Select: `from plan_b.runner import load, run_with_fallback`.
Fallback chain: b3 -> b5 -> b2 -> b4 -> b1
(b7 is a separate fit entry, not in the chain).

## Plan A vs Plan B

- Plan A (`firmware/plan_a/`, entry `firmware/embedded_main_hsp.py`):
  full 12-stage HSP with DNN supervision. Use when the board has headroom.
- Plan B (here): pick one combo when you need a smaller fit.

## Rules

- No numpy in `firmware/`; feature order = train_classifier.extract_features.
- Bake gates hold — no weights enter `common/` without beating baseline on CV.
