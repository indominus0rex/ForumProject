"""Train a baseline classifier on the Parkinson tremor dataset format.

This is separate from train_classifier.py, which expects the embedded pilot CSV
format: LABEL,ax1,ay1,az1,...,ax128,ay128,az128.

Dataset expected here:
    Datasets/Parkinson's/Parkinson's Tremor Classification Dataset/train.csv
    Datasets/Parkinson's/Parkinson's Tremor Classification Dataset/data/raw_data_*.csv

Target:
    folder_path activity label from train.csv.

Run from repo root:
    uv run python host_scripts/train_parkinsons_dataset.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression


ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "Datasets" / "Parkinson's" / "Parkinson's Tremor Classification Dataset"
TRAIN_CSV = DATASET_DIR / "train.csv"
DATA_DIR = DATASET_DIR / "data"
REPORT_PATH = ROOT / "analysis" / "parkinsons_training_report.md"


def _read_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return next(csv.reader(f))


def _joint_bases(header: list[str]) -> list[str]:
    bases = set()
    for col in header:
        if col.upper() == "TIME" or "." not in col:
            continue
        bases.add(col.rsplit(".", 1)[0])
    return sorted(bases)


def _safe_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def extract_features(raw_path: Path) -> np.ndarray:
    """Extract simple motion features from all joint xyz time series."""
    header = _read_header(raw_path)
    arr = np.genfromtxt(raw_path, delimiter=",", skip_header=1, dtype=np.float32)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    if arr.shape[0] < 2:
        raise ValueError("not enough samples")

    col_idx = {name: i for i, name in enumerate(header)}
    features: list[float] = []

    time_col = col_idx.get("TIME")
    if time_col is not None:
        t = arr[:, time_col]
        dt = np.diff(t)
        dt = dt[np.isfinite(dt) & (dt > 0)]
        fs = float(1.0 / np.median(dt)) if len(dt) else 30.0
        duration = float(t[-1] - t[0]) if len(t) else 0.0
    else:
        fs = 30.0
        duration = 0.0
    features.extend([fs, duration, float(arr.shape[0])])

    for base in _joint_bases(header):
        try:
            xyz = np.column_stack([
                arr[:, col_idx[f"{base}.x"]],
                arr[:, col_idx[f"{base}.y"]],
                arr[:, col_idx[f"{base}.z"]],
            ])
        except KeyError:
            continue

        centered = xyz - np.nanmean(xyz, axis=0, keepdims=True)
        mag = np.sqrt(np.nansum(centered * centered, axis=1))
        vel = np.diff(xyz, axis=0) * fs if xyz.shape[0] > 1 else np.zeros_like(xyz)
        vel_mag = np.sqrt(np.nansum(vel * vel, axis=1)) if len(vel) else np.array([0.0])

        features.extend([
            float(np.nanmean(mag)),
            float(np.nanstd(mag)),
            float(np.nanmax(mag) - np.nanmin(mag)),
            float(np.sqrt(np.nanmean(mag * mag))),
            float(np.nanmean(vel_mag)),
            float(np.nanstd(vel_mag)),
            float(np.nanpercentile(mag, 95)),
        ])

    return np.array(features, dtype=np.float32)


def load_dataset() -> tuple[np.ndarray, np.ndarray, list[str]]:
    rows = []
    with TRAIN_CSV.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    X, y, skipped = [], [], []
    for row in rows:
        raw_path = DATA_DIR / row["data_file_name"]
        if not raw_path.exists():
            skipped.append(row["data_file_name"])
            continue
        try:
            feats = extract_features(raw_path)
        except Exception as exc:  # keep training robust for malformed raw files
            skipped.append(f"{row['data_file_name']} ({exc})")
            continue

        age = _safe_float(row.get("age"), 0.0)
        gender = 1.0 if str(row.get("gender", "")).lower().startswith("m") else 0.0
        off_on = 1.0 if str(row.get("patient_off_on", "")).lower() == "on" else 0.0
        diagnosis = _safe_float(row.get("doctor_diagnosis_0_5"), 0.0)
        feats = np.concatenate([feats, np.array([age, gender, off_on, diagnosis], dtype=np.float32)])

        X.append(feats)
        y.append(row["folder_path"])

    if not X:
        raise SystemExit("No usable training rows found")

    # All current raw files have the same schema; pad defensively if needed.
    max_len = max(len(v) for v in X)
    X_pad = np.full((len(X), max_len), np.nan, dtype=np.float32)
    for i, v in enumerate(X):
        X_pad[i, :len(v)] = v
    return X_pad, np.array(y), skipped


def main() -> int:
    X, y, skipped = load_dataset()
    classes, counts = np.unique(y, return_counts=True)

    print(f"Loaded {len(y)} usable rows, {len(classes)} classes")
    for cls, count in zip(classes, counts):
        print(f"  {cls}: {count}")
    if skipped:
        print(f"Skipped {len(skipped)} rows/files")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    logreg = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(max_iter=1000, class_weight="balanced"),
    )
    rf = make_pipeline(
        SimpleImputer(strategy="median"),
        RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced"),
    )

    results = []
    for name, clf in [("LogisticRegression", logreg), ("RandomForest", rf)]:
        scores = cross_val_score(clf, X, y, cv=cv, scoring="accuracy")
        print(f"{name} CV accuracy: {scores.mean():.3f} +/- {scores.std():.3f}")
        results.append((name, clf, scores))

    best_name, best_clf, best_scores = max(results, key=lambda item: item[2].mean())
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    best_clf.fit(X_train, y_train)
    pred = best_clf.predict(X_val)
    holdout_acc = accuracy_score(y_val, pred)

    print(f"Best model: {best_name}")
    print(f"Holdout accuracy: {holdout_acc:.3f}")
    print(classification_report(y_val, pred, zero_division=0))

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8") as f:
        f.write("# Parkinson Dataset Training Report\n\n")
        f.write(f"Dataset: `{DATASET_DIR}`\n\n")
        f.write(f"Usable rows: {len(y)}\n\n")
        f.write("## Class counts\n\n")
        for cls, count in zip(classes, counts):
            f.write(f"- {cls}: {int(count)}\n")
        f.write("\n## Cross-validation\n\n")
        for name, _, scores in results:
            f.write(f"- {name}: {scores.mean():.3f} +/- {scores.std():.3f}\n")
        f.write(f"\nBest model: **{best_name}**\n\n")
        f.write(f"Holdout accuracy: **{holdout_acc:.3f}**\n\n")
        f.write("## Holdout classification report\n\n")
        f.write("```text\n")
        f.write(classification_report(y_val, pred, zero_division=0))
        f.write("```\n\n")
        f.write("## Confusion matrix\n\n")
        f.write("Rows=true, columns=predicted.\n\n")
        f.write("```text\n")
        f.write(str(confusion_matrix(y_val, pred, labels=list(classes))))
        f.write("\n```\n")
        if skipped:
            f.write(f"\nSkipped rows/files: {len(skipped)}\n")

    print(f"Wrote {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
