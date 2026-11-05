import sys, types
mach = types.ModuleType('machine')
class _Pin:
    IN = 0; OUT = 1
    def __init__(self, *a, **k): pass
    def value(self, v=None): pass
class _I2C:
    def __init__(self, *a, **k): pass
class _Timer:
    PERIODIC = 0
    def __init__(self, *a, **k): pass
    def init(self, *a, **k): pass
    def deinit(self): pass
mach.Pin = _Pin; mach.I2C = _I2C; mach.Timer = _Timer
sys.modules['machine'] = mach
sys.path.insert(0, 'firmware')
from raw_data_collection import MultiIMUCollector
class FakeIMU:
    def __init__(self, v): self.v = v
    def read_3axis(self): return self.v
def make_collector():
    c = MultiIMUCollector.__new__(MultiIMUCollector)
    c.label = 'postural'; c.samples = 128
    c.sensors = [FakeIMU((0.1 * (i + 1), 0.2 * (i + 1), 1.0)) for i in range(4)]
    c.mux = types.SimpleNamespace(select_channel=lambda ch: None)
    c.allocate_buffer()
    return c
def fill(c):
    for idx in range(128):
        s = c.read_sample()
        assert len(s) == 12, len(s)
        base = idx * 12
        for i, v in enumerate(s):
            c._buffer[base + i] = v
def test_read_sample_keeps_xyz_per_imu():
    c = make_collector()
    s = c.read_sample()
    assert len(s) == 12
    assert abs(s[0] - 0.1) < 1e-9 and abs(s[2] - 1.0) < 1e-9
    assert abs(s[3] - 0.2) < 1e-9 and abs(s[11] - 1.0) < 1e-9
def test_format_output_parse_compatible():
    c = make_collector()
    fill(c)
    lines = c.format_output(c._buffer).strip().split(chr(10))
    train = [ln for ln in lines if not ln.startswith('postural:aux')]
    assert len(train) == 1, len(lines)
    parts = train[0].split(',')
    assert len(parts) == 1 + 128 * 3, len(parts)
    assert parts[0] == 'postural'
    assert abs(float(parts[1]) - 0.1) < 1e-3
    aux = [ln for ln in lines if ln.startswith('postural:aux')]
    assert len(aux) == 1
    assert len(aux[0].split(',')) == 1 + 128 * 12, len(aux[0].split(','))
if __name__ == '__main__':
    test_read_sample_keeps_xyz_per_imu()
    test_format_output_parse_compatible()
    print('multicollector tests passed!')
