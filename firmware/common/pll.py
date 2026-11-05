"""common/pll.py — Software Phase-Locked Loop (PLL) for tremor phase tracking.

Tracks the phase and frequency of quasi-periodic tremor oscillations (3-12 Hz)
in real-time. Adapts to frequency drift without retraining.

Architecture:
    input → phase_detector → loop_filter → NCO → output
              ↑                                    │
              └────────────────────────────────────┘
"""

import math
from typing import Tuple


class PLL:
    """Software Phase-Locked Loop for tremor tracking.

    Tracks phase and frequency of a quasi-periodic input signal.
    Uses a numerically controlled oscillator (NCO) as the internal reference.
    """

    def __init__(self, fs: float = 100.0, center_freq: float = 6.0,
                 bandwidth: float = 1.0, damping: float = 0.707):  # bw matches common/config.py PLL_BANDWIDTH_HZ
        """Initialize PLL.

        Args:
            fs: Sampling frequency in Hz.
            center_freq: Initial frequency estimate in Hz (typically 6 Hz for tremor).
            bandwidth: Loop bandwidth in Hz (0.5 = slow but stable, 2.0 = fast but noisy).
            damping: Damping factor (0.707 = Butterworth, critical damping).
        """
        self.fs = fs
        self.center_freq = center_freq
        self.bandwidth = bandwidth
        self.damping = damping

        # NCO state
        self.phase = 0.0  # Current phase (radians, 0 to 2*pi)
        self.freq = center_freq  # Current frequency estimate (Hz)

        # Loop filter coefficients (PI controller)
        # Natural frequency from bandwidth
        wn = 2.0 * math.pi * bandwidth / damping
        # PI gains
        self.kp = 2.0 * damping * wn / fs
        self.ki = wn * wn / (fs * fs)
        # Crest-factor compensation: the level tracker below follows peaks
        # (fast attack), so normalized detector gain is lower by ~pi/2 for
        # sine input; restore the design loop gain explicitly.
        self.kp *= 1.57
        self.ki *= 1.57

        # Loop filter integrator state
        self.integrator = 0.0

        # Phase detector state (low-pass filter of phase error)
        self.phase_error_filtered = 0.0
        self.alpha_lpf = 0.1  # LPF smoothing factor

        # Output tracking
        self.locked = False
        self.lock_count = 0
        self.lock_threshold = 50  # samples before declaring lock

        # G2 coarse estimator (zero-crossing rate, ported from prototype/loop_v2.py).
        # Scale-invariant: crossings detected on RMS-normalized input so it
        # works for raw sines (~1.0) and bandpassed tremor (~0.15) alike.
        # Seeded from center_freq (the best prior; also a warm start after
        # ActuationStage resets between tremor episodes).
        self._rms = 1.0
        self._crate = max(3.0, min(12.0, center_freq))
        self._cslow = max(3.0, min(12.0, center_freq))
        # Unclamped twin of _cslow: same leak, but fed the raw crossing rate
        # so out-of-band tones (2/15 Hz) stay distinguishable from rail tones
        # (3/12 Hz) after the [3, 12] clamp saturates. Rail-lock veto only.
        self._craw = max(3.0, min(12.0, center_freq))
        self._armed = False
        self._cross_n = 0
        self._unlocked_n = 0

        # B1 disagreement counter (ported from prototype/loop_v2.py).
        self._disagree_n = 0

    def update(self, sample: float) -> Tuple[float, float, float]:
        """Update PLL with new sample.

        Args:
            sample: Input signal sample (filtered accelerometer magnitude).

        Returns:
            Tuple of (phase, frequency, nco_output) where:
                phase: Current tracked phase (radians, 0 to 2*pi)
                frequency: Current tracked frequency (Hz)
                nco_output: NCO output (sin of phase, for monitoring)
        """
        # Coarse frequency estimate: leaky count of hysteresis-gated rising
        # crossings over a ~1 s window. crate ~= crossings-per-100-samples = Hz.
        # Seeded from center_freq (the best prior; also a warm start after
        # ActuationStage resets between tremor episodes). Early transient
        # dip (leak outrunning sparse pre-fill crossings) stays inside the
        # 0.5 Hz disagree band, so it cannot veto center lock; FLL/recenter
        # below additionally wait for estimator maturity.
        # Level tracker with fast attack / slow release (classic AGC for
        # loop leveling): upward steps re-scale within ~10 samples (a 4x
        # jump must not ring past the ~100-sample recovery budget), while
        # steady-state ripple stays small so the lock band below keeps its
        # margins. Slow release is the safe direction (fade = sluggish loop,
        # and output is amplitude-gated downstream anyway).
        a = abs(sample)
        self._rms += (0.3 if a > self._rms else 0.005) * (a - self._rms)
        xn = sample / (self._rms + 1e-6)
        H = 0.3  # hysteresis on normalized input (scale-invariant)
        if xn < -H:
            self._armed = True
        self._crate *= 0.99
        if self._armed and xn > H:
            self._armed = False
            self._crate += 1.0
            self._cross_n += 1
        fest = max(3.0, min(12.0, self._crate))
        self._cslow += 0.02 * (fest - self._cslow)
        # Faster leak than _cslow on purpose: a slow unclamped tracker would
        # slew through the agree band during 2 Hz pull-in long enough (>50
        # samples) to false-lock; at 0.05 the pass-through stays <50 while
        # steady-state ripple stays inside the 0.75 rail veto band.
        self._craw += 0.05 * (self._crate - self._craw)

        # NCO outputs (in-phase and quadrature)
        nco_sin = math.sin(self.phase)
        nco_cos = math.cos(self.phase)

        # Phase detector: multiply input by quadrature NCO
        # sin(ωt+φ_in) * cos(ωt+φ_nco) = 0.5[sin(φ_in-φ_nco) + sin(2ωt+...)]
        # After LPF: 0.5*sin(φ_in-φ_nco) ≈ 0.5*(φ_in-φ_nco) for small error
        phase_error = sample * nco_cos

        # Amplitude-invariant loop drive: normalize by input level so loop
        # dynamics (and the lock band below) are identical for raw sines
        # (~1.0) and bandpassed tremor (~0.15). The 0.05 floor bounds gain
        # for weak signals (same role as NORM_EPS in plan_b/combo_b7_fit.py).
        phase_error = phase_error / (self._rms + 0.05)

        # Low-pass filter the phase error (removes 2x frequency component)
        self.phase_error_filtered += self.alpha_lpf * (phase_error - self.phase_error_filtered)

        # Agreement veto (B1 core, ported from prototype/loop_v2.py): coarse
        # zero-crossing estimate vs NCO frequency. A slow beat keeps perr
        # small while the two disagree; 30 consecutive disagreements veto
        # lock. Scale-free (unlike raw error magnitude), so it holds for
        # raw sines and bandpassed tremor alike.
        agree = True
        if self._cross_n >= 3:
            fcoarse = min(12.0, max(3.0, self._cslow))
            if abs(fcoarse - self.freq) < 0.5:
                self._disagree_n = 0
            else:
                self._disagree_n += 1
                agree = self._disagree_n < 30
        else:
            self._disagree_n = 0

        # Loop filter (PI controller)
        self.integrator += self.ki * self.phase_error_filtered
        freq_adjust = self.kp * self.phase_error_filtered + self.integrator

        # Update NCO frequency
        self.freq = self.center_freq + freq_adjust

        # Clamp frequency to tremor band, with integrator anti-windup: if
        # clamped, roll back this sample's integration so the integrator
        # cannot wind up against the rail and freeze a phase offset in.
        # (Without this, edge tones park at the rail with ferr ~0.5 forever.)
        raw_freq = self.freq
        self.freq = max(3.0, min(12.0, self.freq))
        if self.freq != raw_freq:
            self.integrator -= self.ki * self.phase_error_filtered

        # FLL assist (acquisition only — cut on lock so PI owns tracking;
        # gated on estimator maturity so it never chases a transient).
        # Early pull is ~zero near truth, so fast center lock is
        # undisturbed; off-center, pull starts on converged evidence.
        # Feed the coarse-vs-NCO gap into the integrator so a zero-mean
        # beat cannot stalemate pull-in. Closes ~0.5 Hz gaps in ~50 samples;
        # integration smooths coarse jitter; also unwinds rail deadlock by
        # pulling off the rail. On drift-out, unlock re-engages.
        if self._cross_n >= 8 and not self.locked:
            fc_now = max(3.0, min(12.0, self._cslow))
            self.integrator += 0.02 * (fc_now - self.freq)

        # Update NCO phase
        self.phase += 2.0 * math.pi * self.freq / self.fs

        # Wrap phase to [0, 2*pi)
        while self.phase >= 2.0 * math.pi:
            self.phase -= 2.0 * math.pi
        while self.phase < 0.0:
            self.phase += 2.0 * math.pi

        # Lock detection: absolute band (as before) AND coarse agreement.
        # Rail-edge addendum (Task 4): at the clamp rails a steady-state
        # phase offset freezes in (|perr| parks ~0.3-0.6, never < 0.1 — worse
        # at 3 Hz where the 2f image leaks through the LPF), so the absolute
        # band alone never fires there. When the NCO sits at a rail AND the
        # coarse estimator agrees (clamped band) AND the *unclamped* rate
        # agrees (rejects 2/15 Hz, which also park at rails with small perr),
        # a wider perr band declares honest rail lock. The perr term does NOT
        # guard offband tones — the unclamped veto does. The B1 disagree veto
        # above stays authoritative everywhere else.
        fcoarse_rail = min(12.0, max(3.0, self._cslow))
        at_rail = self.freq <= 3.15 or self.freq >= 11.85
        rail_ok = (self._cross_n >= 3
                   and abs(fcoarse_rail - self.freq) < 0.5
                   and abs(self._craw - self.freq) < 0.75)
        rail_hold = at_rail and rail_ok and abs(self.phase_error_filtered) < 0.7
        if (abs(self.phase_error_filtered) < 0.1 and agree) or rail_hold:
            self.lock_count += 1
            if self.lock_count >= self.lock_threshold:
                self.locked = True
        elif abs(self.phase_error_filtered) > 0.2 or self._disagree_n >= 30:
            self.lock_count = 0
            self.locked = False

        # G2 pull-in: sustained coarse-vs-NCO disagreement (>1 s unlocked
        # AND 30 consecutive disagreeing samples) jumps center to the coarse
        # estimate and restarts the integrator (which holds beat windup).
        # The >0.3 Hz guard stops refiring once centered; the PI loop plus
        # FLL assist below own the residual.
        if not self.locked:
            self._unlocked_n += 1
            if self._unlocked_n > 100 and self._disagree_n >= 30:
                fc = max(3.0, min(12.0, self._cslow))
                if abs(fc - self.center_freq) > 0.3:
                    self.center_freq = fc
                    self.integrator = 0.0
                    self._unlocked_n = 0
                    self._disagree_n = 0
        else:
            self._unlocked_n = 0

        return self.phase, self.freq, nco_sin

    def reset(self):
        """Reset PLL to initial state."""
        self.phase = 0.0
        self.freq = self.center_freq
        self.integrator = 0.0
        self.phase_error_filtered = 0.0
        self.locked = False
        self.lock_count = 0
        self._rms = 1.0
        self._crate = max(3.0, min(12.0, self.center_freq))
        self._cslow = max(3.0, min(12.0, self.center_freq))
        self._craw = max(3.0, min(12.0, self.center_freq))
        self._armed = False
        self._cross_n = 0
        self._unlocked_n = 0
        self._disagree_n = 0

    def get_phase_degrees(self) -> float:
        """Return current phase in degrees (0-360)."""
        return math.degrees(self.phase)

    def get_period_samples(self) -> float:
        """Return current period in samples."""
        if self.freq > 0:
            return self.fs / self.freq
        return 0.0
