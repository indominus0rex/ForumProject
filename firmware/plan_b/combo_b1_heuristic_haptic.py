"""B1 safe — P0 heuristic perception + S0 threshold haptic. No weights needed."""
import math

NAME = "b1_safe"
DESCRIPTION = "heuristic 3-12Hz peak + fixed-duty haptic; runs with no baked weights"
PERCEPTION = "P0_heuristic"
SUPPRESSION = "S0_threshold_haptic"
GATE_OK = True

HEURISTIC_LO_HZ = 3.0
HEURISTIC_HI_HZ = 12.0
HEURISTIC_MAG_THRESHOLD = 1.2
LRA_DUTY_ON = 512
LRA_DUTY_OFF = 0


class Combo:
    def __init__(self, fs: float = 100.0):
        from common.fft import FFTProcessor
        self.fs = fs
        self._fft = FFTProcessor(num_samples=128)

    def _heuristic(self, window):
        signal = [0.0] * len(window)
        for i, row in enumerate(window):
            signal[i] = math.sqrt(row[0] ** 2 + row[1] ** 2 + row[2] ** 2)
        freq, mag = self._fft.process_data(signal, self.fs)
        if HEURISTIC_LO_HZ <= freq <= HEURISTIC_HI_HZ and mag > HEURISTIC_MAG_THRESHOLD:
            return "kinetic", min(1.0, mag / (HEURISTIC_MAG_THRESHOLD * 2.0))
        return "rest", 1.0

    def process(self, frame: dict) -> dict:
        window = frame.get("window") or [[0.0, 0.0, 1.0]] * 128
        label, conf = self._heuristic(window)
        duty = LRA_DUTY_ON if label != "rest" else LRA_DUTY_OFF
        frame["label"] = label
        frame["confidence"] = conf
        frame["suppress_duty"] = duty
        frame["plan_b"] = NAME
        return frame

    def process_sample(self, x: float, y: float, z: float) -> int:
        mag = math.sqrt(x * x + y * y + z * z) - 1.0
        return LRA_DUTY_ON if mag > 0.2 else LRA_DUTY_OFF
