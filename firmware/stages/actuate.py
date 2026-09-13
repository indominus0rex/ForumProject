"""firmware/stages/actuate.py

Actuation stage: DNN-supervised, PLL-driven LRA output.
Replays the completed window sample-by-sample through an owned SuppressStage
(bandpass -> PLL -> predictor -> anti-phase PWM -> adaptive gain) and writes a
single suppress_duty that HapticStage already prefers. Gated by the state
machine action: only cue_low (postural, scaled) and cue_high (kinetic, full)
produce output. Any gate closure resets PLL state so lock never carries over.
"""
from stages import Frame
from stages.suppress import SuppressStage

CUE_LOW = 'cue_low'
CUE_HIGH = 'cue_high'
MAX_DUTY = 1023

class ActuationStage:
    def __init__(self, fs=100.0, pll_bandwidth=1.0, prediction_ms=15.0,
                 initial_gain=0.5, kinetic_scale=1.0, postural_scale=0.5):
        # Defaults mirror common/config.py — keep in sync manually.
        self.kinetic_scale = kinetic_scale
        self.postural_scale = postural_scale
        self._sup = SuppressStage(fs=fs, pll_bandwidth=pll_bandwidth,
                                  prediction_ms=prediction_ms,
                                  initial_gain=initial_gain)
    def _gate_off(self, frame, reason):
        self._sup.reset()
        frame['suppress_duty'] = 0
        frame['pll_locked'] = False
        frame['actuation_reason'] = 'gated:' + reason
        return frame
    def process(self, frame):
        if not frame.get('quality_ok', True):
            return self._gate_off(frame, frame.get('quality_reason', 'quality'))
        if not frame.get('safe', True):
            return self._gate_off(frame, frame.get('error_msg', 'unsafe'))
        action = frame.get('action', 'none')
        if action == CUE_HIGH:
            scale = self.kinetic_scale
        elif action == CUE_LOW:
            scale = self.postural_scale
        else:
            return self._gate_off(frame, 'action:' + str(action))
        window = frame.get('window')
        if not window:
            return self._gate_off(frame, 'no_window')
        duties = [self._sup.process_sample(r[0], r[1], r[2]) for r in window]
        tail = duties[-32:] if len(duties) >= 32 else duties
        s = sorted(tail)
        med = s[len(s) // 2]
        duty = int(max(0, min(MAX_DUTY, round(med * scale))))
        frame['suppress_duty'] = duty
        frame['pll_locked'] = self._sup.pll.locked
        frame['pll_freq'] = self._sup.pll.freq
        frame['adaptive_gain'] = self._sup.adaptive_gain.get_gain()
        frame['actuation_reason'] = 'actuate:%s:%d' % (frame.get('label', '?'), duty)
        return frame
