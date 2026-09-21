"""firmware/stages/haptic.py

Haptic stage: feedback policy extracted from embedded_main.apply_feedback.
Updates LED and TB6612FNG motor driver based on frame['label'] and frame['confidence'].
Requires frame to contain hardware objects: led, tb6612 (dict with ain1, ain2, pwma, stby).
"""

from stages import Frame


class HapticStage:
    def __init__(self):
        pass

    def _set_motor(self, tb6612: dict, duty: int) -> None:
        """Set TB6612FNG channel A PWM duty. 0 = off, 1023 = full speed."""
        pwma = tb6612.get("pwma")
        if pwma:
            pwma.duty(duty)

    def _motor_off(self, tb6612: dict) -> None:
        """Turn motor off via TB6612FNG."""
        self._set_motor(tb6612, 0)

    def process(self, frame: Frame) -> Frame:
        # Confidence/state/quality gated: prefer frame["suppress_duty"] from suppress stage
        suppress_duty = frame.get("suppress_duty")
        label = frame.get("label")
        conf = frame.get("confidence", 0.0)
        led = frame.get("led")
        tb6612 = frame.get("tb6612", {})

        # Hard gates
        if not frame.get("quality_ok", True) or not frame.get("safe", True):
            if led:
                led.value(0)
            self._motor_off(tb6612)
            frame["haptic_reason"] = "gated:{}".format(frame.get("quality_reason", "unsafe"))
            return frame

        # If suppress stage present, drive from suppress_duty
        if suppress_duty is not None:
            if led:
                led.value(1 if suppress_duty > 0 else 0)
            self._set_motor(tb6612, suppress_duty)
            frame["haptic_reason"] = "suppress:{}".format(suppress_duty)
            return frame

        # Fallback: direct label mapping (when suppress not in pipeline)
        import time
        now = time.ticks_ms()

        if label == "baseline" or label == "rest":
            if led:
                led.value(0)
            self._motor_off(tb6612)
            return frame

        if label == "postural":
            phase = (now // 1000) % 2
            if led:
                led.value(1 if phase == 0 else 0)
            self._motor_off(tb6612)
            return frame

        if label == "kinetic":
            if led:
                led.value(1)
            phase = (now // 500) % 2
            duty = 512 if phase == 0 else 0  # ~50% duty for vibration
            self._set_motor(tb6612, duty)
            return frame

        # grasp_guidance or other — steady vibration
        if label == "grasp_guidance" or label not in ["baseline", "rest", "postural", "kinetic"]:
            if led:
                led.value(1)
            self._set_motor(tb6612, 512)  # ~50% duty steady
            return frame

        # unknown/default
        if led:
            led.value(0)
        self._motor_off(tb6612)
        return frame