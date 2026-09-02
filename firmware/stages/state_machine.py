"""firmware/stages/state_machine.py — Context state machine + confidence-gated haptic policy.

Implements the edge-tremor-coach policy from docs/SYSTEM_ARCHITECTURE_IMPROVEMENTS.md:

  idle -> observing -> tremor_candidate -> confirmed_tremor -> feedback -> cooldown

- Debounces predictions across 2-3 windows (reduces false LRA fires)
- Gates feedback by confidence, signal quality, and cooldown
- Emits frame["state"], frame["action"] in {none, observe, cue_low, cue_high}
- Logs last transition for audit / event stream
"""

from stages import Frame
import time

# State names
IDLE = "idle"
OBSERVING = "observing"
CANDIDATE = "tremor_candidate"
CONFIRMED = "confirmed_tremor"
FEEDBACK = "feedback"
COOLDOWN = "cooldown"

# Actions consumed by haptic stage
ACTION_NONE = "none"
ACTION_OBSERVE = "observe"
ACTION_CUE_LOW = "cue_low"   # postural — gentle cue
ACTION_CUE_HIGH = "cue_high" # kinetic — stronger pulse

TREMOR_LABELS = ("kinetic", "postural")


class TremorStateMachine:
    def __init__(
        self,
        confirm_windows: int = 2,
        cooldown_windows: int = 2,
        conf_thresh_kinetic: float = 0.55,
        conf_thresh_postural: float = 0.50,
        max_tremor_before_cooldown: int = 4,
    ):
        self.state = IDLE
        self.confirm_windows = confirm_windows
        self.cooldown_windows = cooldown_windows
        self.conf_thresh_kinetic = conf_thresh_kinetic
        self.conf_thresh_postural = conf_thresh_postural
        self.max_tremor_before_cooldown = max_tremor_before_cooldown

        self._candidate_count = 0
        self._cooldown_remaining = 0
        self._feedback_count = 0
        self._last_label = None

    def _is_tremor(self, label: str, conf: float) -> bool:
        if label == "kinetic":
            return conf >= self.conf_thresh_kinetic
        if label == "postural":
            return conf >= self.conf_thresh_postural
        return False

    def _label_to_action(self, label: str) -> str:
        if label == "kinetic":
            return ACTION_CUE_HIGH
        if label == "postural":
            return ACTION_CUE_LOW
        return ACTION_NONE

    def process(self, frame: Frame) -> Frame:
        label = frame.get("label", "rest")
        conf = frame.get("confidence", 0.0)
        quality_ok = frame.get("quality_ok", True)
        safe = frame.get("safe", True)

        # Hard gate: never act on bad signal or unsafe
        if not safe or not quality_ok:
            # stay or revert to idle, but keep cooldown ticking
            if self.state == COOLDOWN and self._cooldown_remaining > 0:
                self._cooldown_remaining -= 1
                frame["state"] = COOLDOWN
                frame["action"] = ACTION_NONE
                frame["state_reason"] = frame.get("quality_reason", "unsafe")
                return frame
            self.state = IDLE
            self._candidate_count = 0
            frame["state"] = self.state
            frame["action"] = ACTION_NONE
            frame["state_reason"] = "quality_gate" if not quality_ok else "unsafe"
            return frame

        # Cooldown: suppress feedback for N windows after a burst
        if self.state == COOLDOWN:
            self._cooldown_remaining -= 1
            if self._cooldown_remaining <= 0:
                self.state = IDLE
                self._candidate_count = 0
            frame["state"] = self.state
            frame["action"] = ACTION_NONE
            frame["state_reason"] = "cooldown:{}".format(self._cooldown_remaining)
            return frame

        is_tremor = self._is_tremor(label, conf)

        # State transitions
        if self.state == IDLE:
            if is_tremor:
                self.state = CANDIDATE
                self._candidate_count = 1
                self._last_label = label
                frame["state_reason"] = "candidate:{}".format(label)
            else:
                # baseline/rest => stay idle but mark observing briefly for telemetry
                self.state = OBSERVING
                frame["state_reason"] = "observing:{}".format(label)
            frame["state"] = self.state
            frame["action"] = ACTION_NONE
            return frame

        if self.state == OBSERVING:
            if is_tremor:
                self.state = CANDIDATE
                self._candidate_count = 1
                self._last_label = label
            elif label in ("baseline", "rest"):
                self.state = IDLE
                self._candidate_count = 0
            frame["state"] = self.state
            frame["action"] = ACTION_NONE
            frame["state_reason"] = "obs->{}".format(self.state)
            return frame

        if self.state == CANDIDATE:
            # Need consecutive tremor windows of same type (or any tremor)
            if is_tremor:
                # allow label drift kinetic<->postural as same tremor family
                self._candidate_count += 1
                self._last_label = label
                if self._candidate_count >= self.confirm_windows:
                    self.state = CONFIRMED
                    frame["state_reason"] = "confirmed:{}x".format(self._candidate_count)
                else:
                    frame["state_reason"] = "candidate:{}/{}".format(self._candidate_count, self.confirm_windows)
            else:
                # broken streak
                self.state = IDLE
                self._candidate_count = 0
                frame["state_reason"] = "break:{}".format(label)
            frame["state"] = self.state
            # only act once confirmed
            frame["action"] = ACTION_NONE if self.state != CONFIRMED else self._label_to_action(self._last_label or label)
            # move to feedback on next window if still tremor
            if self.state == CONFIRMED:
                self.state = FEEDBACK
                self._feedback_count = 0
            return frame

        if self.state == FEEDBACK:
            if is_tremor:
                self._feedback_count += 1
                frame["action"] = self._label_to_action(label)
                frame["state_reason"] = "feedback:{}".format(self._feedback_count)
                if self._feedback_count >= self.max_tremor_before_cooldown:
                    self.state = COOLDOWN
                    self._cooldown_remaining = self.cooldown_windows
                    frame["state_reason"] = "enter_cooldown"
            else:
                # tremor ended
                self.state = IDLE
                self._candidate_count = 0
                frame["action"] = ACTION_NONE
                frame["state_reason"] = "tremor_end"
            frame["state"] = self.state if self.state != COOLDOWN else COOLDOWN
            return frame

        # fallback
        frame["state"] = self.state
        frame["action"] = ACTION_NONE
        frame["state_reason"] = "fallback"
        return frame

    def reset(self):
        self.state = IDLE
        self._candidate_count = 0
        self._cooldown_remaining = 0
        self._feedback_count = 0
        self._last_label = None
