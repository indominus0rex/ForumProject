import os
import sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train_classifier import extract_features, fmt_list
from parkinsons_windows import load_cache

HIDDEN = 16
GATE_MIN_CV = 0.40

def main(cache=None):
    if cache is None:
        cache = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'parkinsons_windows.npz')
    Xw, y, files = load_cache(cache)
    print('windows: %d classes: %s' % (len(y), sorted(set(y.tolist()))))
    X = np.array([extract_features(w) for w in Xw], dtype=np.float64)
    y = np.array(y)
    scaler = StandardScaler().fit(X)
    Xs = scaler.transform(X)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
    logreg = LogisticRegression(max_iter=500, C=1.0, solver='lbfgs')
    s_lr = cross_val_score(logreg, Xs, y, cv=cv)
    print('logreg CV: %.3f +/- %.3f' % (s_lr.mean(), s_lr.std()))
    mlp = MLPClassifier(hidden_layer_sizes=(HIDDEN,), activation='relu',
                        max_iter=2000, random_state=0)
    s_dnn = cross_val_score(mlp, Xs, y, cv=cv)
    print('dnn CV: %.3f +/- %.3f' % (s_dnn.mean(), s_dnn.std()))
    ok = s_dnn.mean() > GATE_MIN_CV and s_dnn.mean() > s_lr.mean()
    print('GATE %s: dnn %.3f vs logreg %.3f (min %.2f)' % (
        'PASS' if ok else 'FAIL', s_dnn.mean(), s_lr.mean(), GATE_MIN_CV))
    if not ok:
        return 2
    mlp.fit(Xs, y)
    print('train acc: %.3f' % float((mlp.predict(Xs) == y).mean()))
    print('')
    print('# === paste into model_dnn.py ===')
    print('CLASSES = %s' % [str(c) for c in mlp.classes_])
    print('FEATURE_MEAN = %s' % fmt_list(scaler.mean_))
    print('FEATURE_STD  = %s' % fmt_list(scaler.scale_))
    print('W1 = [')
    for row in mlp.coefs_[0].T:
        print('    ' + fmt_list(row) + ',')
    print(']')
    print('B1 = %s' % fmt_list(mlp.intercepts_[0]))
    print('W2 = [')
    for row in mlp.coefs_[1].T:
        print('    ' + fmt_list(row) + ',')
    print(']')
    print('B2 = %s' % fmt_list(mlp.intercepts_[1]))
    print('# === end ===')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
