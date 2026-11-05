"""plan_b — named fallback algorithm combos (thin wiring only).

Each combo module exposes:
    NAME: str
    DESCRIPTION: str
    PERCEPTION: str
    SUPPRESSION: str
    GATE_OK: bool         # False until weights bake past the gate
    class Combo:
        def __init__(self, fs: float = 100.0): ...
        def process(self, frame: dict) -> dict: ...
        def process_sample(self, x: float, y: float, z: float) -> int: ...
"""

PLAN_B_REGISTRY = {
    "b1_safe": "plan_b.combo_b1_heuristic_haptic",
    "b2_baseline_ml": "plan_b.combo_b2_logreg_haptic",
    "b3_current_best": "plan_b.combo_b3_dnn_pll",
    "b4_pll_only": "plan_b.combo_b4_pll_only",
    "b5_fixed_gain": "plan_b.combo_b5_dnn_fixed_gain",
}

FALLBACK_CHAIN = ["b3_current_best", "b5_fixed_gain", "b2_baseline_ml", "b4_pll_only", "b1_safe"]

__all__ = ["PLAN_B_REGISTRY", "FALLBACK_CHAIN"]
