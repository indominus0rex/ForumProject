"""common/frontend.py — canonical tremor frontend (ported from combo_b7_fit).

Per-axis gravity/DC removal -> dominant-axis projection -> bandpass 3-12 Hz
-> amplitude-smoothed, normalized PLL drive. Normalization keeps loop gain
constant across shakes (see review Blocker 2); raw amplitude is returned
untouched for output scaling.
"""

MEAN_ALPHA = 0.02  # TODO: tune on body — DC (gravity) tracker per axis
ENERGY_ALPHA = 0.02  # TODO: tune on body — axis-energy tracker
AMP_ALPHA = 0.05  # TODO: tune on body — amplitude smoother
NORM_EPS = 0.05  # PLL normalization floor (g)


class AxisFrontend:
    """Single-IMU frontend: xyz -> (pll_in, filt, amp)."""

    def __init__(self, bandpass):
        self._bp = bandpass
        self._mx, self._my, self._mz = 0.0, 0.0, 1.0
        self._ex, self._ey, self._ez = 0.0, 0.0, 0.0
        self._dom = 0
        self._amp_smooth = 0.0

    def step(self, x, y, z):
        self._mx += MEAN_ALPHA * (x - self._mx)
        self._my += MEAN_ALPHA * (y - self._my)
        self._mz += MEAN_ALPHA * (z - self._mz)
        ax, ay, az = x - self._mx, y - self._my, z - self._mz
        self._ex += ENERGY_ALPHA * (ax * ax - self._ex)
        self._ey += ENERGY_ALPHA * (ay * ay - self._ey)
        self._ez += ENERGY_ALPHA * (az * az - self._ez)
        if self._ey > self._ex and self._ey >= self._ez:
            self._dom = 1
        elif self._ez > self._ex and self._ez > self._ey:
            self._dom = 2
        else:
            self._dom = 0
        s = ax if self._dom == 0 else (ay if self._dom == 1 else az)
        filt = self._bp.process_sample(s)
        amp = abs(filt)
        self._amp_smooth += AMP_ALPHA * (amp - self._amp_smooth)
        pll_in = filt / (self._amp_smooth + NORM_EPS)
        return pll_in, filt, amp

    def reset(self):
        self._bp.reset()
        self._mx, self._my, self._mz = 0.0, 0.0, 1.0
        self._ex = self._ey = self._ez = 0.0
        self._dom = 0
        self._amp_smooth = 0.0
