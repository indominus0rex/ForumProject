"""firmware/stages/haptic.py

Haptic stage: feedback policy extracted from embedded_main.apply_feedback.
Updates LED and LRA PWM based on frame['label'] and frame['confidence'].
Requires frame to contain hardware objects: led, lra, lra_array, USE_LRA_ARRAY.
"""

from machine import Pin, PWM
from stages import Frame


LRA_DUTY_ON = 512
LRA_DUTY_OFF = 0


class HapticStage:
    def __init__(self):
        pass

    def _set_all_lras(self, led: Pin, lra: PWM, lra_array: list[PWM], duty: int) -> None:
        lra.duty(duty)
        for dev in lra_array:
            dev.duty(duty)

    def process(self, frame: Frame) -> Frame:
        # Confidence/state/quality gated: prefer frame["action"] from state_machine
        action = frame.get("action")
        label = frame.get("label")
        conf = frame.get("confidence", 0.0)
        led = frame.get("led")
        lra = frame.get("lra")
        lra_array = frame.get("lra_array", [])
        use_array = frame.get("use_lra_array", False)

        # Hard gates
        if not frame.get("quality_ok", True) or not frame.get("safe", True):
            if led:
                led.value(0)
            self._set_all_lras(led, lra, lra_array, LRA_DUTY_OFF)
            frame["haptic_reason"] = "gated:{}".format(frame.get("quality_reason", "unsafe"))
            return frame

        # If state machine present, drive from action
        if action is not None:
            import time
            now = time.ticks_ms()
            if action == "none" or action == "observe":
                if led:
                    led.value(0)
                self._set_all_lras(led, lra, lra_array, LRA_DUTY_OFF)
                frame["haptic_reason"] = action
                return frame
            if action == "cue_low":
                phase = (now // 1000) % 2
                if led:
                    led.value(1 if phase == 0 else 0)
                self._set_all_lras(led, lra, lra_array, LRA_DUTY_OFF)
                frame["haptic_reason"] = "cue_low"
                return frame
            if action == "cue_high":
                if led:
                    led.value(1)
                phase = (now // 500) % 2
                duty = LRA_DUTY_ON if phase == 0 else LRA_DUTY_OFF
                self._set_all_lras(led, lra, lra_array, duty)
                frame["haptic_reason"] = "cue_high"
                return frame

        # Fallback: direct label mapping (when state_machine not in pipeline)
        import time
        now = time.ticks_ms()

        if label == "baseline" or label == "rest":
            if led:
                led.value(0)
            self._set_all_lras(led, lra, lra_array, LRA_DUTY_OFF)
            return frame

        if label == "postural":
            phase = (now // 1000) % 2
            if led:
                led.value(1 if phase == 0 else 0)
            self._set_all_lras(led, lra, lra_array, LRA_DUTY_OFF)
            return frame

        if label == "kinetic":
            if led:
                led.value(1)
            phase = (now // 500) % 2
            duty = LRA_DUTY_ON if phase == 0 else LRA_DUTY_OFF
            self._set_all_lras(led, lra, lra_array, duty)
            return frame

        # grasp_guidance or other
        if label == "grasp_guidance" or (use_array and label not in ["baseline", "rest", "postural", "kinetic"]):
            if not use_array:
                if led:
                    led.value(1)
                self._set_all_lras(led, lra, lra_array, LRA_DUTY_ON)
                return frame
            # spatial sequence
            sequence_phase = (now // 333) % 3
            for i, dev in enumerate(lra_array):
                dev.duty(LRA_DUTY_ON if i == sequence_phase else LRA_DUTY_OFF)
            if led:
                led.value(1 if sequence_phase == 0 else 0)
            return frame

        # unknown/default
        if led:
            led.value(0)
        self._set_all_lras(led, lra, lra_array, LRA_DUTY_OFF)
        return frame