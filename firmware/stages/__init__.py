"""stages package — Hierarchical Stage Pipeline with typed Stage Protocol.

Every stage implements:
    def process(self, frame: Frame) -> Frame
where Frame is a mutable dict. The main loop never touches stage internals.

Order of execution (default):
  safety -> sensor -> stationarity -> fft -> features -> classify -> haptic -> audit

Adding a new stage is as simple as creating a module and registering it in
embedded_main_hsp.STAGES. No changes to hardware contracts.
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
# Quality gates before classify; state_machine gates haptic.
STAGE_ORDER: List[str] = [
    "safety",
    "sensor",
    "stationarity",
    "quality",
    "fft",
    "features",
    "classify",
    "state_machine",
    "haptic",
    "audit",
]

__all__ = ["STAGE_ORDER", "Stage", "Frame"]