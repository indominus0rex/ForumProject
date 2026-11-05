import argparse, os, sys, time
TRAIN_FIELDS = 1 + 128 * 3
AUX_FIELDS = 1 + 128 * 12
HEADER = '# LABEL,' + ','.join('a%d' % i for i in range(128 * 3))
def _valid_floats(parts):
    try:
        [float(p) for p in parts[1:]]
        return True
    except ValueError:
        return False
def capture_lines(line_iter, label, out_path, aux_path, max_windows=None, verbose=True):
    stats = {'train': 0, 'aux': 0, 'skipped': 0}
    aux_label = label + ':aux'
    out_f = open(out_path, 'w')
    out_f.write(HEADER + chr(10))
    aux_f = open(aux_path, 'w') if aux_path else None
    if aux_f: aux_f.write('# ' + aux_label + chr(10))
    try:
        for raw in line_iter:
            line = raw.strip() if isinstance(raw, str) else raw.decode('utf-8', 'replace').strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith(aux_label + ','):
                parts = line.split(',')
                if len(parts) == AUX_FIELDS and _valid_floats(parts) and aux_f:
                    aux_f.write(line + chr(10)); stats['aux'] += 1
                else:
                    stats['skipped'] += 1
            elif line.startswith(label + ','):
                parts = line.split(',')
                if len(parts) == TRAIN_FIELDS and _valid_floats(parts):
                    out_f.write(line + chr(10)); stats['train'] += 1
                    if verbose and stats['train'] % 10 == 0:
                        print('  windows: %d' % stats['train'])
                else:
                    stats['skipped'] += 1
            else:
                stats['skipped'] += 1
            if max_windows and stats['train'] >= max_windows:
                break
    finally:
        out_f.close()
        if aux_f: aux_f.close()
    return stats
def _port_lines(ser):
    while True:
        chunk = ser.readline()
        if chunk:
            yield chunk
        else:
            time.sleep(0.01)
def capture_port(ser, label, out_path, aux_path, max_windows=None):
    print('capturing label=%s -> %s (Ctrl-C to stop)' % (label, out_path))
    try:
        stats = capture_lines(_port_lines(ser), label, out_path, aux_path, max_windows)
    except KeyboardInterrupt:
        stats = {'train': -1, 'aux': -1, 'skipped': -1}
        print('stopped by user')
    print('done: train=%d aux=%d skipped=%d' % (stats['train'], stats['aux'], stats['skipped']))
    return stats
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', required=True)
    ap.add_argument('--label', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--aux', default=None)
    ap.add_argument('--baud', type=int, default=115200)
    ap.add_argument('--max-windows', type=int, default=None)
    a = ap.parse_args()
    import serial
    ser = serial.Serial(a.port, a.baud, timeout=1)
    try:
        capture_port(ser, a.label, a.out, a.aux, a.max_windows)
    finally:
        ser.close()
if __name__ == '__main__':
    main()
