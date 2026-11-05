import sys, math
sys.path.insert(0, 'firmware')
from stages.actuate import ActuationStage
def make_window(freq_hz=6.0, amp=0.5, n=128, fs=100.0):
    return [[amp * math.sin(2 * math.pi * freq_hz * i / fs), 0.0, 1.0] for i in range(n)]
def enabled_frame(action='cue_high', conf=0.9):
    return {'window': make_window(), 'action': action, 'confidence': conf,
            'label': 'kinetic', 'quality_ok': True, 'safe': True}
def test_enabled_produces_bounded_duty():
    st = ActuationStage()
    out = st.process(enabled_frame())
    assert isinstance(out['suppress_duty'], int), type(out['suppress_duty'])
    assert 0 <= out['suppress_duty'] <= 1023, out['suppress_duty']
    assert 'pll_locked' in out and 'actuation_reason' in out
def test_gated_outputs_zero_and_resets():
    st = ActuationStage()
    st.process(enabled_frame())
    out = st.process({'window': make_window(), 'action': 'none', 'confidence': 0.1,
                      'label': 'rest', 'quality_ok': True, 'safe': True})
    assert out['suppress_duty'] == 0
    assert st._sup.pll.locked is False
    assert st._sup.pll.lock_count == 0
def test_postural_scales_below_kinetic():
    d_hi = ActuationStage().process(enabled_frame(action='cue_high'))['suppress_duty']
    d_lo = ActuationStage().process(enabled_frame(action='cue_low'))['suppress_duty']
    assert d_lo <= d_hi, (d_lo, d_hi)
def test_replay_real_postural_window():
    sys.path.insert(0, 'host_scripts')
    from train_classifier import parse_file
    from stages.quality import QualityStage
    from stages.bandpass import BandpassStage
    from stages.fft import FFTStage
    from stages.features import FeaturesStage
    from stages.classify import ClassifyStage
    from stages.state_machine import TremorStateMachine
    labels, arr = parse_file('host_scripts/sessions/pre_postural_s01.csv')
    assert len(labels) > 0
    q, bp, ff, fe, cl, sm, ac = (QualityStage(), BandpassStage(fs=100.0),
        FFTStage(samples=128, fs=100.0), FeaturesStage(fs=100.0),
        ClassifyStage(samples=128, fs=100.0), TremorStateMachine(), ActuationStage())
    out = None
    for rep in range(3):
        w = arr[rep % len(arr)]
        rows = [[float(w[i, 0]), float(w[i, 1]), float(w[i, 2])] for i in range(w.shape[0])]
        frame = {'window': rows, 'x': rows[-1][0], 'y': rows[-1][1], 'z': rows[-1][2]}
        for st in (q, bp, ff, fe, cl, sm, ac):
            frame = st.process(frame)
        out = frame
        print('replay win%d: true=%s label=%s conf=%.2f action=%s duty=%d reason=%s' % (
            rep, labels[rep % len(labels)], out.get('label'), out.get('confidence', 0.0),
            out.get('action'), out['suppress_duty'], out.get('actuation_reason')))
    assert 0 <= out['suppress_duty'] <= 1023
    assert out.get('action') in ('cue_low', 'cue_high'), out.get('action')
if __name__ == '__main__':
    test_enabled_produces_bounded_duty()
    test_gated_outputs_zero_and_resets()
    test_postural_scales_below_kinetic()
    test_replay_real_postural_window()
    print('actuate tests passed!')
