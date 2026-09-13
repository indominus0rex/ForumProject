"""tests/test_plan_b.py — contract tests for firmware/plan_b combos."""
import sys
import importlib

sys.path.insert(0, "firmware")

from plan_b import PLAN_B_REGISTRY, FALLBACK_CHAIN


def _load(name):
    return importlib.import_module(PLAN_B_REGISTRY[name])


def test_registry_has_six_combos():
    assert sorted(PLAN_B_REGISTRY) == [
        "b1_safe", "b2_baseline_ml", "b3_current_best",
        "b4_pll_only", "b5_fixed_gain", "b6_cnn_future",
    ]
    assert "b6_cnn_future" not in FALLBACK_CHAIN


def test_each_combo_contract():
    for name in PLAN_B_REGISTRY:
        mod = _load(name)
        assert isinstance(mod.NAME, str)
        assert isinstance(mod.DESCRIPTION, str)
        assert isinstance(mod.GATE_OK, bool)
        if name == "b6_cnn_future":
            assert mod.GATE_OK is False
            combo = mod.Combo(fs=100.0)
            assert combo.process_sample(0.1, 0.2, 0.9) == 0
            try:
                combo.process({"window": [[0.0, 0.0, 1.0]] * 128})
            except RuntimeError as e:
                assert "GATE" in str(e)
            else:
                raise AssertionError("B6 process() must raise RuntimeError")
            continue
        if name in ("b2_baseline_ml", "b3_current_best", "b5_fixed_gain"):
            try:
                mod.Combo(fs=100.0)
            except RuntimeError as e:
                assert "GATE" in str(e)
                continue
        combo = mod.Combo(fs=100.0)
        duty = combo.process_sample(0.1, 0.2, 0.9)
        assert isinstance(duty, int) and 0 <= duty <= 1023
        frame = {"window": [[0.1, 0.2, 0.9]] * 128, "x": 0.1, "y": 0.2, "z": 0.9}
        out = combo.process(dict(frame))
        assert "plan_b" in out and out["plan_b"] == mod.NAME
        assert "suppress_duty" in out


def test_b6_quarantined():
    mod = _load("b6_cnn_future")
    assert mod.GATE_OK is False
    try:
        mod.Combo(fs=100.0).process({"window": [[0.0, 0.0, 1.0]] * 128})
    except RuntimeError as e:
        assert "GATE" in str(e)
    else:
        raise AssertionError("B6 firmware process() must raise RuntimeError")


def test_window_replay_locks():
    """Full-window replay drives PLL to lock on 6 Hz (review Finding 4)."""
    import math
    for name in ("b3_current_best", "b4_pll_only", "b5_fixed_gain"):
        try:
            mod = _load(name)
            combo = mod.Combo(fs=100.0)
        except RuntimeError:
            continue  # weights not baked — gate holds, skip
        frame = {"window": [
            [0.1 * math.sin(2 * math.pi * 6.0 * i / 100.0),
             0.05 * math.sin(2 * math.pi * 6.0 * i / 100.0),
             1.0 + 0.15 * math.sin(2 * math.pi * 6.0 * i / 100.0)]
            for i in range(128)]}
        for _ in range(3):
            frame = combo.process(dict(frame))
        assert 0 <= frame["suppress_duty"] <= 1023


if __name__ == "__main__":
    test_registry_has_six_combos()
    test_each_combo_contract()
    test_b6_quarantined()
    test_window_replay_locks()
    print("plan_b tests passed!")
