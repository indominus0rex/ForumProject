"""tests/test_stft.py — overlapping STFT spectrogram (MicroPython-safe)."""
import sys
import math

sys.path.insert(0, "firmware")


def make_sine(freq_hz=6.0, amp=0.6, n=128, fs=100.0):
    return [amp * math.sin(2 * math.pi * freq_hz * i / fs) for i in range(n)]


def test_stft_frame_count_and_bins():
    from common.stft import STFTProcessor
    st = STFTProcessor(num_samples=128, frame_len=64, hop=32, fs=100.0)
    spec = st.spectrogram(make_sine())
    assert len(spec) == 3, len(spec)          # (128-64)//32 + 1
    assert all(len(row) == 32 for row in spec), [len(r) for r in spec]


def test_stft_detects_6hz():
    from common.stft import STFTProcessor
    st = STFTProcessor(num_samples=128, frame_len=64, hop=32, fs=100.0)
    spec = st.spectrogram(make_sine(freq_hz=6.0))
    freqs = st.bin_freqs()
    per_frame_peak = [freqs[max(range(len(r)), key=lambda i: r[i])] for r in spec]
    assert all(abs(f - 6.0) <= 100.0 / 64 + 1e-9 for f in per_frame_peak), per_frame_peak


def test_stft_parity_with_single_fft_on_stationary():
    # Stationary sine: total in-band STFT power must be within 20% of the
    # single-FFT total on the SAME 1-D signal (identical mean-removal, Hann,
    # and *2/n scaling on both paths; measured <2% at 4.5-10 Hz).
    # NOTE: compared as TOTALS (sum of squares), not RMS. Both band_power()
    # impls divide by their own bin count (13 bins @128-FFT vs 7 @64-FFT),
    # so RMS values differ by the deterministic factor sqrt(13/7) ~= 1.36
    # for an in-band tone even when scaling is exactly right. Total power
    # is the Parseval-consistent quantity across different bin widths.
    from common.stft import STFTProcessor
    import common.feature_extract as fe
    fs, n = 100.0, 128
    sig = make_sine(freq_hz=6.0, amp=0.6, n=n, fs=fs)
    mu = sum(sig) / n
    hann = fe._get_hann(n)
    real = [(s - mu) * hann[i] for i, s in enumerate(sig)]
    imag = [0.0] * n
    fe._in_place_fft(real, imag)
    mag_single = [math.sqrt(real[i] ** 2 + imag[i] ** 2) * 2 / n
                  for i in range(n // 2)]
    df1 = fs / n
    lo1, hi1 = max(1, int(3.0 / df1)), min(n // 2 - 1, int(12.0 / df1))
    ref_total = sum(m * m for m in mag_single[lo1:hi1 + 1])
    st = STFTProcessor(num_samples=n, frame_len=64, hop=32, fs=fs)
    mean_mag = st.mean_spectrum(sig)
    df2 = fs / st.frame_len
    lo2, hi2 = max(1, int(3.0 / df2)), min(st.n_bins - 1, int(12.0 / df2))
    got_total = sum(m * m for m in mean_mag[lo2:hi2 + 1])
    assert abs(got_total - ref_total) / max(ref_total, 1e-9) < 0.20, (got_total, ref_total)
    # band_power() contract: RMS over its own bins == sqrt(total / nbins)
    got_rms = st.band_power(mean_mag, 3.0, 12.0)
    assert abs(got_rms - math.sqrt(got_total / (hi2 - lo2 + 1))) < 1e-9, got_rms


def test_stft_no_numpy_and_fast_enough():
    import time
    import subprocess
    # Ban numpy/scipy IMPORTS (not bare words: the docstring itself says
    # "No numpy/scipy", which a bare-word grep false-positives on).
    out = subprocess.run(["grep", "-rn",
                          r"import numpy\|import scipy\|from numpy\|from scipy",
                          "firmware/common/stft.py"],
                         capture_output=True, text=True).stdout
    assert out.strip() == "", out
    from common.stft import STFTProcessor
    st = STFTProcessor(num_samples=128, frame_len=64, hop=32, fs=100.0)
    t0 = time.perf_counter()
    st.spectrogram(make_sine())
    assert (time.perf_counter() - t0) < 0.050, "host smoke bound 50 ms"


def test_stft_rejects_bad_params():
    from common.stft import STFTProcessor
    for kw in ({"frame_len": 100}, {"hop": 48}, {"frame_len": 256}):
        # Merge over valid defaults (no duplicate keys): each override alone
        # must raise ValueError — non-pow2 frame, non-pow2 hop, frame > window.
        args = {"num_samples": 128, "frame_len": 64, "hop": 32, "fs": 100.0}
        args.update(kw)
        try:
            STFTProcessor(**args)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for %r" % (kw,))
