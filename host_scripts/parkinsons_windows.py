import csv
import glob
import os
import numpy as np

TASK_TO_LABEL = {
    'Kinetic tremor': 'kinetic',
    'Postural tremor': 'postural',
    'Fist': 'rest',
    'Finger tapping': 'baseline',
    'Pronation and supination of the hand': 'baseline',
}

N = 128
OUT_HZ = 100.0

def load_file(path):
    t, xyz = [], []
    with open(path, newline='') as fh:
        for row in csv.reader(fh):
            if not row or row[0].startswith('WRIST'):
                continue
            try:
                x, y, z = float(row[0]), float(row[1]), float(row[2])
                tt = float(row[-1])
            except (ValueError, IndexError):
                continue
            t.append(tt); xyz.append((x, y, z))
    return np.array(t), np.array(xyz, dtype=np.float64)

def resample_to_100hz(t, xyz, out_hz=OUT_HZ):
    if len(t) < 8:
        return np.zeros((0, 3))
    t = t - t[0]
    dur = t[-1]
    if dur <= 0:
        return np.zeros((0, 3))
    grid = np.arange(0.0, dur, 1.0 / out_hz)
    if len(grid) < N:
        return np.zeros((0, 3))
    out = np.stack([np.interp(grid, t, xyz[:, j]) for j in range(3)], axis=1)
    return out

def build_windows(data_dir, train_csv, limit=None, in_hz=22.07):
    del in_hz  # rate comes from TIME stamps via interp, kept for API/tests
    Xs, ys, fs = [], [], []
    skipped = []
    with open(train_csv, newline='') as fh:
        rows = list(csv.DictReader(fh))
    if limit is not None:
        rows = rows[:limit]
    for row in rows:
        task = row['folder_path']
        if task not in TASK_TO_LABEL:
            skipped.append((row['data_file_name'], task))
            continue
        label = TASK_TO_LABEL[task]
        path = os.path.join(data_dir, row['data_file_name'])
        if not os.path.exists(path):
            skipped.append((row['data_file_name'], 'missing file'))
            continue
        t, xyz = load_file(path)
        sig = resample_to_100hz(t, xyz)
        for s in range(0, len(sig) - N + 1, N):
            w = sig[s:s + N]
            if np.isnan(w).any() or np.var(w) <= 0:
                continue
            Xs.append(w.astype(np.float32)); ys.append(label); fs.append(row['data_file_name'])
    if skipped:
        print('skipped %d rows, e.g. %s' % (len(skipped), skipped[:3]))
    X = np.array(Xs, dtype=np.float32).reshape(-1, N, 3) if Xs else np.zeros((0, N, 3), dtype=np.float32)
    return X, np.array(ys), np.array(fs)

def save_cache(X, y, files, path):
    np.savez_compressed(path, X=X, y=y, files=files)
    print('cached %d windows -> %s' % (len(y), path))

def load_cache(path):
    d = np.load(path, allow_pickle=True)
    return d['X'], np.array([str(v) for v in d['y']]), np.array([str(v) for v in d['files']])

def main():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                         'Datasets', "Parkinson's",
                         "Parkinson's Tremor Classification Dataset")
    X, y, files = build_windows(os.path.join(base, 'data'), os.path.join(base, 'train.csv'))
    uniq, counts = np.unique(y, return_counts=True)
    for u, c in zip(uniq, counts):
        print('  %s: %d' % (u, c))
    print('total windows: %d' % len(y))
    save_cache(X, y, files, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        'parkinsons_windows.npz'))
    return 0 if len(y) > 5000 else 2

if __name__ == '__main__':
    import sys
    sys.exit(main())
