"""stages package — Hierarchical Stage Pipeline with typed Stage Protocol.

Every stage implements:
    def process(self, frame: Frame) -> Frame
where Frame is a mutable dict. The main loop never touches stage internals.

Order of execution (default):
  safety -> sensor -> stationarity -> quality -> bandpass -> fft
  -> features -> audit

classify / state_machine / actuate / haptic removed from pipeline:
  - DNN weights not yet trained for Option A+ET placement
  - ERM (TB6612FNG) output controlled separately, not via classify→state_machine→actuate→haptic
  - Add back after retraining + baking weights into model_dnn.py
"""

from typing import Protocol, Dict, Any, List

# Type alias for the frame dictionary passed through the pipeline
Frame = Dict[str, Any]

# Stage Protocol - defines the contract for all pipeline stages
class Stage(Protocol):
    def process(self, frame: Frame) -> Frame:
        """Process the frame and return the (potentially modified) frame."""
        ...

# Ordered stage names mirroring the folder order used by the refactor.
# Quality gates before suppress; suppress drives haptic.
STAGE_ORDER: List[str] = [
    "safety",
    "sensor",
    "stationarity",
    "quality",
    "bandpass",
    "fft",
    "features",
    "audit",
]

__all__ = ["STAGE_ORDER", "Stage", "Frame"]