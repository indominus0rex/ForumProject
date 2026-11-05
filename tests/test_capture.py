import os, sys, tempfile
sys.path.insert(0, 'host_scripts')
from capture_session import capture_lines
def device_line(label, n_fields, seed=0):
    vals = ','.join('%.4f' % ((i + seed) % 7 * 0.01) for i in range(n_fields))
    return '%s,%s\n' % (label, vals)
def test_capture_splits_train_and_aux():
    import serial
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, 'postural.csv')
        aux = os.path.join(tmp, 'postural_multi.csv')
        lines = [device_line('postural', 384), 'boot message\n',
                 device_line('postural:aux', 1536), device_line('postural', 10),
                 device_line('postural', 384, seed=3)]
        stats = capture_lines(iter(lines), 'postural', out, aux)
        assert stats['train'] == 2, stats
        assert stats['aux'] == 1, stats
        assert stats['skipped'] == 2, stats
        rows = open(out).read().strip().split(chr(10))
        assert rows[0].startswith('# LABEL')
        assert len(rows) == 3, len(rows)
        assert len(rows[1].split(',')) == 385
        arows = open(aux).read().strip().split(chr(10))
        assert len(arows) == 2 and len(arows[1].split(',')) == 1537
def test_capture_live_loopback():
    import serial
    from capture_session import capture_port
    import threading
    ser = serial.serial_for_url('loop://', timeout=1)
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, 'rest.csv')
        def feed():
            ser.write(device_line('rest', 384).encode())
        th = threading.Thread(target=feed); th.start()
        stats = capture_port(ser, 'rest', out, None, max_windows=1)
        th.join()
        assert stats['train'] == 1, stats
    ser.close()
if __name__ == '__main__':
    test_capture_splits_train_and_aux()
    test_capture_live_loopback()
    print('capture tests passed!')
