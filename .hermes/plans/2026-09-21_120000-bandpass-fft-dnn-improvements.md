# Bandpass + FFT + DNN Improvement Plan

## Goal

Improve the bandpass filter, FFT stage, and DNN classifier so the pipeline can
classify tremor types (rest/kinetic/postural/baseline) on-device with baked
weights, replacing the current heuristic fallback.

## Current Context

- **Bandpass**: `firmware/common/bandpass.py` — 4th-order IIR biquad cascade
  (2 sections), 3–12 Hz, geometric-mean center frequency. Works but unvalidated
  on real tremor data.
- **FFT**: `firmware/common/fft.py` — Cooley-Tukey, Hann window, 128 samples →
  0.78 Hz resolution. Now uses shared `dsp.py`. Resolution is coarse for
  distinguishing 4–6 Hz (pill-rolling) from 6–12 Hz (ET).
- **DNN**: `firmware/common/model_dnn.py` — weights are `None` (not trained).
  `firmware/common/dnn.py` has a working 2-layer MLP forward pass (ReLU +
  softmax). Training pipeline exists (`train_classifier.py --dnn`,
  `train_dnn_parkinsons.py`) but weights haven't been baked in.
- **Pipeline**: `ClassifyStage` is commented out in `stages/__init__.py` —
  "DNN weights not yet trained for Option A+ET placement."
- **Training data**: `host_scripts/sessions/*.csv` has 6 files (pre/post
  postural). `Datasets/Parkinson's/` has a full classification dataset with
  `train.csv` + `data/`.
- **STFT**: `firmware/stages/stft.py` exists but `USE_STFT=False` — single FFT
  is the default.

## Architecture / Proposed Approach

1. **Validate bandpass** on synthetic tremor signals (4 Hz, 6 Hz, 8 Hz, 12 Hz)
   and real session data; tune Q factor if needed.
2. **Improve FFT resolution** via zero-padding to 256 samples (0.39 Hz
   resolution) — still fits in ESP32 RAM, no hardware change.
3. **Train DNN** on available data (Parkinson's dataset + session CSVs),
   bake weights into `model_dnn.py`, add `ClassifyStage` to the pipeline.
4. **Add STFT option** for time-varying tremor analysis (optional, behind
   `USE_STFT` flag).

## Step-by-Step Tasks

### Task 1: Validate bandpass filter response

**File**: `firmware/common/bandpass.py`

Add a `__main__` block that:
- Creates a `BandpassFilter` at fs=100, 3–12 Hz
- Feeds synthetic sine waves at 2 Hz, 4 Hz, 6 Hz, 8 Hz, 12 Hz, 15 Hz
- Measures output amplitude for each
- Asserts: 4–12 Hz passes (>50% amplitude), 2 Hz and 15 Hz attenuated (<20%)

```python
if __name__ == "__main__":
    import math
    fs = 100.0
    bp = BandpassFilter(fs=fs, low_hz=3.0, high_hz=12.0)
    for freq in [2.0, 4.0, 6.0, 8.0, 12.0, 15.0]:
        samples = [math.sin(2 * math.pi * freq * i / fs) for i in range(256)]
        out = bp.process_block(samples)
        # Measure RMS of last 128 samples (steady-state)
        tail = out[128:]
        rms = math.sqrt(sum(x*x for x in tail) / len(tail))
        print(f"  {freq:5.1f} Hz -> RMS {rms:.4f}")
        if 4.0 <= freq <= 12.0:
            assert rms > 0.3, f"{freq} Hz should pass (got {rms:.4f})"
        else:
            assert rms < 0.2, f"{freq} Hz should be attenuated (got {rms:.4f})"
    print("bandpass validation passed")
```

**Verify**: `python firmware/common/bandpass.py` → "bandpass validation passed"

**Commit**: `test: validate bandpass filter frequency response`

---

### Task 2: Add zero-padding to FFT for better frequency resolution

**File**: `firmware/common/fft.py`

Add optional `zero_pad` parameter to `FFTProcessor.__init__`. When enabled,
pad the 128-sample window to 256 samples with zeros before FFT. This gives
0.39 Hz resolution (vs 0.78 Hz) — critical for distinguishing 4–6 Hz from
6–12 Hz tremor.

```python
def __init__(self, num_samples: int = 128, zero_pad: bool = False):
    self.num_samples = num_samples
    self.zero_pad = zero_pad
    self.fft_size = num_samples * 2 if zero_pad else num_samples
    self.window = get_hann(self.fft_size)
    self._twiddles = get_twiddles(self.fft_size)
    self._real_buf = [0.0] * self.fft_size
    self._imag_buf = [0.0] * self.fft_size
```

Update `process_data` to pad before FFT:

```python
def process_data(self, signal_data, actual_fs):
    n = self.num_samples
    if self.zero_pad:
        # Zero-pad to 2x for finer frequency resolution
        padded = signal_data + [0.0] * n
    else:
        padded = signal_data
    mean_val = sum(padded) / len(padded)
    real = [(padded[i] - mean_val) * self.window[i] for i in range(self.fft_size)]
    # ... rest unchanged
```

**File**: `firmware/stages/fft.py`

Add `zero_pad` parameter to `FFTStage.__init__`, pass through to `FFTProcessor`.

**File**: `firmware/common/config.py`

Add `FFT_ZERO_PAD: bool = False` to `PIPELINE_CONFIG`.

**Verify**: `python firmware/stages/fft.py` → "fft stage smoke test passed"

**Commit**: `feat: add zero-padding option to FFT for finer frequency resolution`

---

### Task 3: Train DNN and bake weights

**Step 3a**: Run the existing training script on the Parkinson's dataset:

```bash
cd /c/ForumProject
python host_scripts/train_dnn_parkinsons.py
```

Expected output: CV accuracy for logreg vs DNN, gate pass/fail, and a Python
literal to paste into `model_dnn.py`.

**Step 3b**: If gate passes (DNN CV > 0.40 and > logreg CV), paste the output
into `firmware/common/model_dnn.py`:
- Replace `W1`, `b1`, `W2`, `b2` with trained values
- Update `FEATURE_MEAN`, `FEATURE_STD` with scaler values
- Update `CLASSES` if class order differs

**Step 3c**: Verify the baked weights work:

```bash
python tests/test_dnn_pipeline.py
```

Uncomment the `test_classify_dnn_path_with_baked_weights` test and verify it passes.

**Commit**: `feat: bake DNN weights into model_dnn.py`

---

### Task 4: Add ClassifyStage to the pipeline

**File**: `firmware/stages/classify.py`

Implement a `ClassifyStage` that:
- Reads `frame["features"]` (15-element vector)
- Normalizes using `model_dnn.FEATURE_MEAN` / `FEATURE_STD`
- Runs `dnn.forward()` to get logits/probs
- Writes `frame["label"]`, `frame["probs"]`, `frame["confidence"]`
- Falls back to heuristic if `model_dnn.W1 is None`

```python
from stages import Frame
from common import model_dnn
from common import dnn as dnn_mod

class ClassifyStage:
    def __init__(self):
        self._mean = model_dnn.FEATURE_MEAN
        self._std = model_dnn.FEATURE_STD

    def process(self, frame: Frame) -> Frame:
        feats = frame.get("features")
        if feats is None:
            frame["label"] = "unknown"
            return frame
        if model_dnn.W1 is None:
            # Heuristic fallback: dominant freq in 3-12 Hz band
            dom = frame.get("dominant_freq", 0.0)
            frame["label"] = "kinetic" if 3.0 <= dom <= 12.0 else "rest"
            frame["confidence"] = 0.5
            return frame
        # Normalize
        x = [(feats[i] - self._mean[i]) / self._std[i] for i in range(len(feats))]
        logits, probs = dnn_mod.forward(x, model_dnn.W1, model_dnn.b1,
                                        model_dnn.W2, model_dnn.b2)
        k = probs.index(max(probs))
        frame["label"] = model_dnn.CLASSES[k]
        frame["probs"] = probs
        frame["confidence"] = probs[k]
        return frame
```

**File**: `firmware/stages/__init__.py`

Add `"classify"` to `STAGE_ORDER` after `"features"`:

```python
STAGE_ORDER = [
    "safety", "sensor", "stationarity", "quality",
    "bandpass", "fft", "features", "classify", "audit",
]
```

**Verify**: `python tests/test_dnn_pipeline.py` → all tests pass

**Commit**: `feat: add ClassifyStage to HSP pipeline`

---

### Task 5: Add STFT option for time-varying analysis

**File**: `firmware/stages/stft.py`

Implement an STFT stage that:
- Splits the 128-sample window into 4 overlapping frames of 64 samples
- Runs FFT on each frame
- Tracks dominant frequency over time
- Writes `frame["stft_freqs"]` (list of 4 dominant frequencies)

```python
from stages import Frame
from common.fft import FFTProcessor

class STFTStage:
    def __init__(self, frame_len: int = 64, hop: int = 32, fs: float = 100.0):
        self.frame_len = frame_len
        self.hop = hop
        self.fs = fs
        self._fft = FFTProcessor(num_samples=frame_len)

    def process(self, frame: Frame) -> Frame:
        window = frame.get("window", [])
        if not window:
            return frame
        freqs = []
        for start in range(0, len(window) - self.frame_len + 1, self.hop):
            segment = window[start:start + self.frame_len]
            # Extract magnitude signal
            mag = [math.sqrt(r[0]**2 + r[1]**2 + r[2]**2) for r in segment]
            dom_freq, _ = self._fft.process_data(mag, self.fs)
            freqs.append(dom_freq)
        frame["stft_freqs"] = freqs
        return frame
```

**File**: `firmware/common/config.py`

Add `USE_STFT: bool = False` to `PIPELINE_CONFIG`.

**File**: `firmware/stages/__init__.py`

Conditionally add `"stft"` to `STAGE_ORDER` when `USE_STFT` is True.

**Verify**: `python firmware/stages/stft.py` → "stft stage smoke test passed"

**Commit**: `feat: add optional STFT stage for time-varying frequency analysis`

---

## Tests / Validation

| Task | Test | Command | Expected |
|---|---|---|---|
| 1 | Bandpass response | `python firmware/common/bandpass.py` | "bandpass validation passed" |
| 2 | FFT zero-pad | `python firmware/stages/fft.py` | "fft stage smoke test passed" |
| 3 | DNN weights | `python tests/test_dnn_pipeline.py` | All tests pass |
| 4 | ClassifyStage | `python tests/test_pipeline_integration.py` | Full pipeline passes |
| 5 | STFT | `python firmware/stages/stft.py` | "stft stage smoke test passed" |

## Risks, Tradeoffs, and Open Questions

- **DNN training data**: The Parkinson's dataset may not match the device's
  IMU placement (Option A+ET: thumb + index phalanx). The gate in
  `train_dnn_parkinsons.py` (CV > 0.40) is a minimum bar — may need
  retraining with pilot data from the actual device.
- **Zero-padding cost**: 256-point FFT is ~2x the compute of 128-point. On
  ESP32 at 100 Hz, this is still feasible (~10 ms budget per window).
- **STFT memory**: 4 frames × 64 samples × 3 axes = 768 floats — fits in
  ESP32 RAM but adds ~5 ms per window.
- **ClassifyStage placement**: Currently placed after `features` in
  `STAGE_ORDER`. If classification latency matters, consider running it
  asynchronously or only every N windows.
- **Heuristic fallback**: If DNN weights fail the gate, the pipeline still
  works with the heuristic classifier — no regression.
