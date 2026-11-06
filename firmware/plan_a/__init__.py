"""plan_a — full Hierarchical Stage Pipeline (HSP) for tremor suppression.

Plan A is the full pipeline: 12 stages in firmware/stages/, wired by
firmware/embedded_main_hsp.py via STAGE_ORDER, sharing DSP math in
firmware/common/. Use Plan A when the board has RAM/CPU headroom and you
want classification-supervised actuation. Use firmware/plan_b combos when
you need a smaller fit (e.g. b7_fit on stock ESP32-S3-Kaluga-1).

Entry: firmware/embedded_main_hsp.py (flash support files first, see README).
Stages: safety -> sensor -> stationarity -> quality -> bandpass -> fft
  -> features -> classify (DNN) -> state_machine -> actuate -> haptic -> audit.
Frame: plain dict passed through every stage (see firmware/stages/__init__.py).
"""

NAME = "plan_a_full_hsp"
DESCRIPTION = "full 12-stage HSP: quality/bandpass/FFT/features/DNN/state-machine/PLL actuation"
ENTRY = "embedded_main_hsp.py"

__all__ = ["NAME", "DESCRIPTION", "ENTRY"]
