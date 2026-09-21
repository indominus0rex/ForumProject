"""firmware/stages/quality.py — Signal-quality gate for tremor pipeline.

Validates a 128-sample window before trusting classifier output.
Checks (all cheap, MicroPython-safe):
  - I2C fallback ratio (0,0,1) count
  - Per-axis variance / saturation (±2g)
  - Gravity magnitude sanity
  - Loose-strap / motion artifact via inter-sample jitter proxy
  - Flat-line detection

Sets frame["quality_ok"], frame["quality_reason"], frame["quality_metrics"].
Downstream stages should gate feedback on quality_ok.
"""

from stages import Frame
from common.config import PIPELINE_CONFIG as _CFG
import math


# Tunables — read from common/config.py PIPELINE_CONFIG
FALLBACK_RATIO_THRESH = _CFG["QUALITY_FALLBACK_THRESH"]
SATURATION_THRESH_G = _CFG["QUALITY_SATURATION_G"]
FLAT_VARIANCE_THRESH = _CFG["QUALITY_FLAT_VAR_THRESH"]
GRAVITY_MIN = _CFG["QUALITY_GRAVITY_MIN"]
GRAVITY_MAX = _CFG["QUALITY_GRAVITY_MAX"]
JITTER_VAR_THRESH = _CFG["QUALITY_JITTER_VAR_THRESH"]


class QualityStage:
    def __init__(
        self,
        fallback_thresh: float = FALLBACK_RATIO_THRESH,
        flat_thresh: float = FLAT_VARIANCE_THRESH,
    ):
        self.fallback_thresh = fallback_thresh
        self.flat_thresh = flat_thresh

    def _check_window(self, window: list[list[float]]) -> tuple[bool, str, dict]:
        n = len(window)
        if n == 0:
            return False, "empty", {"n": 0}

        fallback_cnt = 0
        sat_cnt = 0
        sum_x = sum_y = sum_z = 0.0
        sum_mag = 0.0
        # For variance
        # track per-axis means then second pass for var
        for r in window:
            x, y, z = r[0], r[1], r[2]
            if x == 0.0 and y == 0.0 and z == 1.0:
                fallback_cnt += 1
            if abs(x) >= SATURATION_THRESH_G or abs(y) >= SATURATION_THRESH_G or abs(z) >= SATURATION_THRESH_G:
                sat_cnt += 1
            sum_x += x
            sum_y += y
            sum_z += z
            sum_mag += math.sqrt(x*x + y*y + z*z)

        fallback_ratio = fallback_cnt / n if n else 1.0
        if fallback_ratio > self.fallback_thresh:
            return False, "fallback:{:.0%}".format(fallback_ratio), {
                "fallback_ratio": fallback_ratio,
                "fallback_cnt": fallback_cnt,
            }

        if sat_cnt > 0:
            # any saturation is suspect for tremor band; flag if >2 samples
            if sat_cnt > 2:
                return False, "saturation:{}".format(sat_cnt), {
                    "sat_cnt": sat_cnt,
                }

        mean_x = sum_x / n
        mean_y = sum_y / n
        mean_z = sum_z / n
        mean_mag = sum_mag / n

        if mean_mag < GRAVITY_MIN or mean_mag > GRAVITY_MAX:
            return False, "gravity:{:.2f}".format(mean_mag), {
                "mean_mag": mean_mag,
            }

        # Per-axis variance (flat-line = loose strap / disconnected)
        var_x = sum((r[0] - mean_x) ** 2 for r in window) / n
        var_y = sum((r[1] - mean_y) ** 2 for r in window) / n
        var_z = sum((r[2] - mean_z) ** 2 for r in window) / n
        var_sum = var_x + var_y + var_z
        if var_sum < self.flat_thresh:
            return False, "flat:{:.1e}".format(var_sum), {
                "var_sum": var_sum,
                "var_x": var_x, "var_y": var_y, "var_z": var_z,
            }

        # Simple jitter proxy: variance of successive magnitude differences
        # High jitter => motion artifact / strap slap, not tremor
        prev_mag = math.sqrt(window[0][0]**2 + window[0][1]**2 + window[0][2]**2)
        diffs = []
        for r in window[1:]:
            cur = math.sqrt(r[0]**2 + r[1]**2 + r[2]**2)
            diffs.append(cur - prev_mag)
            prev_mag = cur
        if diffs:
            m_d = sum(diffs) / len(diffs)
            var_d = sum((d - m_d) ** 2 for d in diffs) / len(diffs)
            if var_d > JITTER_VAR_THRESH:
                return False, "jitter:{:.1f}".format(var_d), {
                    "jitter_var": var_d,
                }

        metrics = {
            "fallback_ratio": fallback_ratio,
            "mean_mag": mean_mag,
            "var_sum": var_sum,
            "sat_cnt": sat_cnt,
        }
        return True, "ok", metrics

    def process(self, frame: Frame) -> Frame:
        window = frame.get("window")
        if not window or len(window) < 8:
            frame["quality_ok"] = False
            frame["quality_reason"] = "no_window"
            frame["quality_metrics"] = {}
            return frame

        ok, reason, metrics = self._check_window(window)
        frame["quality_ok"] = ok
        frame["quality_reason"] = reason
        frame["quality_metrics"] = metrics
        # Expose fallback count to safety/audit
        frame["fallback_ratio"] = metrics.get("fallback_ratio", 0.0)
        return frame
