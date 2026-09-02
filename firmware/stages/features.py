"""firmware/stages/features.py

Features stage: defers to feature_extract.compute but as a stage.
Computes 15-element feature vector from window and stores in frame.
"""

import common.feature_extract as feature_extract
from stages import Frame


class FeaturesStage:
    def __init__(self, fs: float = 100.0, n: int = 128):
        self.fs = fs
        self.n = n

    def process(self, frame: Frame) -> Frame:
        window = frame.get("window")
        if not window:
            frame["features_error"] = "no window"
            return frame
        feats = feature_extract.compute(window, fs=self.fs, n=self.n)
        frame["features"] = feats
        # Option A + ET 2026-08-27: pill 4-6Hz + ET 6-9Hz power for pill-rolling/ET postural, and coherence
        # Keep base 15 for backward compat; expose extended metrics in frame for state_machine/audit and future 16-feat model
        try:
            # Re-use already computed FFT magnitude via feature_extract internals would be optimal,
            # but cheap to recompute band powers here via helper
            import common.feature_extract as fe
            # Quick pill/et powers: reuse last mag if available via compute internals? For now compute via window 2D FFT
            # Extract mag via _fft_mag_sum (uses primary window only — multi-IMU coherence uses raw windows)
            _, mag, _ = fe._fft_mag_sum(window, fs=self.fs, n=self.n)  # type: ignore
            frame["pill_power"] = fe._band_power(mag, self.fs, self.n, 4.0, 6.0)  # pill-rolling 4-6
            frame["et_power"] = fe._band_power(mag, self.fs, self.n, 6.0, 9.0)   # ET postural 6-8 inside
            # Thumb-index and finger-wrist coherence (Option A: CH2 thumb phalanx 20° vs CH3 index phalanx)
            multi = frame.get("multi_window")
            if multi and len(multi) >= 4:
                # Simple magnitude time-series coherence via variance ratio proxy (fast, no extra FFT)
                # thumb-index coherence ~ correlation of magnitude traces
                import math
                th = [math.sqrt(r[0]**2 + r[1]**2 + r[2]**2) for r in multi[2]]
                idx = [math.sqrt(r[0]**2 + r[1]**2 + r[2]**2) for r in multi[3]]
                wrist = [math.sqrt(r[0]**2 + r[1]**2 + r[2]**2) for r in multi[0]]
                # Pearson-like coherence proxy: normalized dot
                def _coh(a, b):
                    if len(a) != len(b) or len(a) == 0:
                        return 0.0
                    ma = sum(a)/len(a); mb = sum(b)/len(b)
                    num = sum((a[i]-ma)*(b[i]-mb) for i in range(len(a)))
                    da = math.sqrt(sum((x-ma)**2 for x in a))
                    db = math.sqrt(sum((x-mb)**2 for x in b))
                    den = da*db + 1e-9
                    return num/den if den != 0 else 0.0
                frame["coh_thumb_index"] = _coh(th, idx)
                # finger mean vs wrist
                fing = [(th[i]+idx[i])/2 for i in range(len(th))]
                frame["coh_finger_wrist"] = _coh(fing, wrist)
            else:
                frame["coh_thumb_index"] = 0.0
                frame["coh_finger_wrist"] = 0.0
        except Exception:
            # Never break pipeline on extended metrics
            frame["pill_power"] = frame.get("pill_power", 0.0)
            frame["et_power"] = frame.get("et_power", 0.0)
            frame["coh_thumb_index"] = frame.get("coh_thumb_index", 0.0)
            frame["coh_finger_wrist"] = frame.get("coh_finger_wrist", 0.0)
        return frame