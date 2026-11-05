"""bench_plan_b.py — score plan_b combos on cached windows (host only).

Usage:
    python host_scripts/bench_plan_b.py
    python host_scripts/bench_plan_b.py --cache host_scripts/parkinsons_windows.npz
"""
import argparse, os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from train_classifier import extract_features, fmt_list  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "parkinsons_windows.npz"))
    args = ap.parse_args()
    if not os.path.exists(args.cache):
        print("no cache at %s; run parkinsons_windows.py first" % args.cache)
        return 2
    z = np.load(args.cache, allow_pickle=True)
    Xw, y = z["Xw"], z["y"]
    print("combos: b1_heuristic b2_logreg b3_dnn b4_naive_pll_proxy b5_gated b6_cnn_proxy")
    print("windows: %d classes: %s" % (len(y), sorted(set(y.tolist()))))
    X = np.array([extract_features(w) for w in Xw])
    print("feat_mean[0:3] = %s" % fmt_list(X.mean(axis=0)[:3]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
