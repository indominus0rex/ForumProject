import sys
import numpy as np
sys.path.insert(0, 'host_scripts')
from parkinsons_windows import build_windows, TASK_TO_LABEL
DATA = "Datasets/Parkinson's/Parkinson's Tremor Classification Dataset"
def test_task_map_covers_train_tasks():
    import csv
    tasks = set()
    with open(DATA + '/train.csv', newline='') as fh:
        for row in csv.DictReader(fh):
            tasks.add(row['folder_path'])
    missing = tasks - set(TASK_TO_LABEL)
    assert not missing, missing
def test_build_windows_subset_shape_and_labels():
    X, y, files = build_windows(DATA + '/data', DATA + '/train.csv', limit=10, in_hz=22.07)
    assert X.ndim == 3 and X.shape[1:] == (128, 3), X.shape
    assert X.shape[0] >= 100, X.shape[0]
    assert set(np.unique(y)) <= {'kinetic', 'postural', 'rest', 'baseline'}, set(np.unique(y))
    assert not np.isnan(X).any()
    assert len(y) == len(files) == X.shape[0]
if __name__ == '__main__':
    test_task_map_covers_train_tasks()
    test_build_windows_subset_shape_and_labels()
    print('parkinsons windows tests passed!')
