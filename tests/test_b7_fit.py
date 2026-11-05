"""tests/test_b7_fit.py — b7_fit combo fits DevKitC: contract + bounds + speed + pushes 1/2/4."""
import sys
import math
import time

sys.path.insert(0, "firmware")


def test_registry_contract():
    from plan_b import combo_b7_fit as m
    assert m.NAME == "b7_fit"
    assert m.GATE_OK is True
    c = m.Combo(fs=100.0)
    assert hasattr(c, "process")
    assert hasattr(c, "process_sample")


def test_process_sample_bounds():
    from plan_b import combo_b7_fit as m
    c = m.Combo(fs=100.0)
    for i in range(20):
        d = c.process_sample(0.0, 0.0, 1.0)
        assert 0 <= d <= 1023


def test_pll_tracks_6hz():
    from plan_b import combo_b7_fit as m
    c = m.Combo(fs=100.0)
    for i in range(300):
        t = i / 100.0
        x = 0.1 * math.sin(2 * math.pi * 6.0 * t)
        y = 0.05 * math.sin(2 * math.pi * 6.0 * t)
        z = 1.0 + 0.15 * math.sin(2 * math.pi * 6.0 * t)
        c.process_sample(x, y, z)
    assert 4.0 < c._pll.freq < 8.0


def test_window_process_fast_enough():
    from plan_b import combo_b7_fit as m
    c = m.Combo(fs=100.0)
    window = [[0.0, 0.0, 1.0] for _ in range(128)]
    t0 = time.time()
    frame = c.process({"window": window, "x": 0.0, "y": 0.0, "z": 1.0})
    dt = time.time() - t0
    assert "suppress_duty" in frame
    assert 0 <= frame["suppress_duty"] <= 1023
    assert dt < 0.5, "host budget 0.5s for 128-sample replay, got %r" % dt


def test_no_heavy_imports():
    with open("firmware/plan_b/combo_b7_fit.py") as f:
        src = f.read()
    for banned in ("cnn1d", "model_cnn", "FFTProcessor", "feature_extract", "model_dnn"):
        assert banned not in src, "b7_fit must not import %s" % banned


def test_push1_multimu_fusion():
    """Push 1: optional multi-sample fusion improves or matches single-IMU duty response."""
    from plan_b import combo_b7_fit as m
    c = m.Combo(fs=100.0, fixed_gain=0.8)
    # lock first on single channel 6 Hz tremor
    for i in range(200):
        t = i / 100.0
        s = math.sin(2 * math.pi * 6.0 * t)
        c.process_sample(0.15 * s, 0.0, 1.0)
    assert hasattr(c, "process_multisample"), "need process_multisample for 4-IMU fusion"
    # 4 IMUs, all seeing same tremor with different noise -> must return valid duty
    d = c.process_multisample([
        (0.15, 0.0, 1.0), (0.14, 0.01, 1.0),
        (0.16, -0.01, 1.0), (0.15, 0.0, 0.99),
    ])
    assert 0 <= d <= 1023


def test_push2_dominant_axis_projection():
    """Push 2: tremor isolated on x-axis still drives output (no magnitude-folding stall)."""
    from plan_b import combo_b7_fit as m
    c = m.Combo(fs=100.0, fixed_gain=0.8)
    duties = []
    for i in range(300):
        t = i / 100.0
        # strong x-only tremor, y/z near static -> magnitude-based would still work,
        # but projection must not stall: last-50 median duty must be > 0
        d = c.process_sample(0.2 * math.sin(2 * math.pi * 6.0 * t), 0.0, 1.0)
        duties.append(d)
    tail = sorted(duties[-50:])
    assert tail[25] > 0, "x-axis tremor should drive nonzero median duty, got %r" % (tail[25],)


def test_push4_amplitude_normalized():
    """Push 4: sudden amplitude jump must not unlock the PLL."""
    from plan_b import combo_b7_fit as m
    c = m.Combo(fs=100.0)
    for i in range(200):
        t = i / 100.0
        s = math.sin(2 * math.pi * 6.0 * t)
        c.process_sample(0.1 * s, 0.0, 1.0)
    assert c._pll.locked, "should be locked before jump"
    # 4x amplitude jump for 100 samples
    for i in range(200, 300):
        t = i / 100.0
        s = math.sin(2 * math.pi * 6.0 * t)
        c.process_sample(0.4 * s, 0.0, 1.0)
    assert c._pll.locked, "PLL must survive 4x amplitude jump (normalization)"
    assert 4.0 < c._pll.freq < 8.0


if __name__ == "__main__":
    test_registry_contract()
    test_process_sample_bounds()
    test_pll_tracks_6hz()
    test_window_process_fast_enough()
    test_no_heavy_imports()
    test_push1_multimu_fusion()
    test_push2_dominant_axis_projection()
    test_push4_amplitude_normalized()
    print("All b7_fit tests passed!")
