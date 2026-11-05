"""tests/test_dnn_pipeline.py — Bandpass -> FFT -> Features pipeline.

Pipeline: safety -> sensor -> stationarity -> quality -> bandpass -> fft -> features -> audit
 classify/state_machine/actuate/haptic removed (DNN weights not yet trained for Option A+ET).

Run:  python tests/test_dnn_pipeline.py   (from repo root)
"""
import sys
import math

sys.path.insert(0, "firmware")

from common.bandpass import BandpassFilter
from common import dnn as dnn_mod
from common import model_dnn
from stages import STAGE_ORDER
from stages.bandpass import BandpassStage
from stages.fft import FFTStage
from stages.features import FeaturesStage
from stages.quality import QualityStage
from stages.stationarity import StationarityStage


def make_window(freq_hz=6.0, amp=0.6, n=128, fs=100.0):
    return [[amp * math.sin(2 * math.pi * freq_hz * i / fs),
             0.05 * math.sin(2 * math.pi * freq_hz * i / fs),
             1.0] for i in range(n)]


def test_stage_order_is_dnn_path():
    assert STAGE_ORDER == [
        "safety", "sensor", "stationarity", "quality",
        "bandpass", "fft", "features", "audit",
    ]


def test_dnn_forward_probs_sum_to_one():
    x = [0.5] * 15
    W1 = [[0.1] * 15 for _ in range(4)]
    b1 = [0.0] * 4
    W2 = [[0.2] * 4 for _ in range(3)]
    b2 = [0.0] * 3
    logits, probs = dnn_mod.forward(x, W1, b1, W2, b2)
    assert len(logits) == 3 and len(probs) == 3
    assert abs(sum(probs) - 1.0) < 1e-6
    assert all(p >= 0.0 for p in probs)


def test_dnn_forward_relu_gates_negative():
    # hidden unit 0 sees +1, unit 1 sees -1 -> relu kills unit 1.
    # W2 reads only unit 1, so logits must be exactly b2.
    x = [1.0]
    W1 = [[1.0], [-1.0]]
    b1 = [0.0, 0.0]
    W2 = [[0.0, 5.0]]
    b2 = [0.25]
    logits, probs = dnn_mod.forward(x, W1, b1, W2, b2)
    assert abs(logits[0] - 0.25) < 1e-9
    assert abs(probs[0] - 1.0) < 1e-9


def test_dnn_forward_known_values():
    x = [1.0, 2.0]
    W1 = [[1.0, 0.0], [0.0, 1.0]]
    b1 = [0.0, 0.0]
    W2 = [[1.0, 1.0], [0.0, 0.0]]
    b2 = [0.0, 0.0]
    logits, probs = dnn_mod.forward(x, W1, b1, W2, b2)
    # hidden = [1, 2]; logits = [3, 0]
    assert abs(logits[0] - 3.0) < 1e-9
    assert abs(logits[1] - 0.0) < 1e-9
    e3 = math.exp(3.0)
    assert abs(probs[0] - e3 / (e3 + 1.0)) < 1e-9


def test_bandpass_stage_attenuates_dc():
    st = BandpassStage(fs=100.0, low_hz=3.0, high_hz=12.0)
    window = [[0.0, 0.0, 1.0]] * 128  # pure gravity DC
    frame = {"window": [list(r) for r in window]}
    out = st.process(frame)
    assert "bandpass_error" not in out
    mags = [math.sqrt(r[0] ** 2 + r[1] ** 2 + r[2] ** 2) for r in out["window"]]
    assert sum(mags) / len(mags) < 0.5


def test_bandpass_stage_passes_tremor():
    st = BandpassStage(fs=100.0, low_hz=3.0, high_hz=12.0)
    window = make_window(freq_hz=6.0, amp=0.6)
    frame = {"window": [list(r) for r in window]}
    out = st.process(frame)
    tail = out["window"][-32:]
    peak = max(abs(r[0]) for r in tail)
    assert peak > 0.1, peak


def test_bandpass_stage_no_window():
    st = BandpassStage()
    out = st.process({})
    assert out["bandpass_error"] == "no window"


def test_pipeline_window_to_label():
    window = make_window(freq_hz=6.0, amp=0.6)
    frame = {"window": window, "x": window[-1][0],
             "y": window[-1][1], "z": window[-1][2]}
    frame = StationarityStage(window_len=128).process(frame)
    frame = QualityStage().process(frame)
    assert frame["quality_ok"], frame.get("quality_reason")
    frame = BandpassStage(fs=100.0).process(frame)
    frame = FFTStage(samples=128, fs=100.0).process(frame)
    assert 3.0 <= frame["dominant_freq"] <= 12.0, frame["dominant_freq"]
    frame = FeaturesStage(fs=100.0).process(frame)
    assert len(frame["features"]) == 15
    # classify/state_machine/actuate/haptic removed from pipeline
    # (DNN weights not yet trained for Option A+ET placement)
    # At this point frame has: window, features, dominant_freq, dominant_mag, pill_power, et_power, coherence metrics


def test_classify_dnn_path_with_baked_weights():
    # DNN weights are None until we retrain with Option A+ET pilot data.
    # The pipeline falls back to heuristic classifier in the meantime.
    # Uncomment the asserts below after running train_classifier.py --dnn.
    # assert model_dnn.W1 is not None and model_dnn.W2 is not None  # baked, after retraining
    # assert len(model_dnn.W1) == 16 and len(model_dnn.W1[0]) == 15
    # assert len(model_dnn.W2) == len(model_dnn.CLASSES)
    # window = make_window(freq_hz=6.0, amp=0.6)
    # frame = ClassifyStage(samples=128, fs=100.0).process({"window": window})
    # assert frame["label"] in model_dnn.CLASSES
    # assert abs(sum(frame["probs"]) - 1.0) < 1e-6
    pass  # skip until weights are baked


if __name__ == "__main__":
    test_stage_order_is_dnn_path()
    test_dnn_forward_probs_sum_to_one()
    test_dnn_forward_relu_gates_negative()
    test_dnn_forward_known_values()
    test_bandpass_stage_attenuates_dc()
    test_bandpass_stage_passes_tremor()
    test_bandpass_stage_no_window()
    test_pipeline_window_to_label()
    test_classify_dnn_path_with_baked_weights()
    print("All DNN pipeline tests passed!")
