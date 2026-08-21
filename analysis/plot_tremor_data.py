"""Plot one example WRIST x/y/z signal per tremor class.

Reads C:/ForumProject/Datasets/Parkinson's/Parkinson's Tremor
Classification Dataset/{train.csv,data/<file>.csv} and produces a PNG
with 5 small panels (one per tremor class).

Usage:
    python plot_tremor_data.py
    python plot_tremor_data.py --out tremor_examples.png

Note: on this box, `python` resolves to the hermes-agent venv (where
matplotlib is installed). `py` resolves to a separate Python 3.14
install without matplotlib, so `py plot_tremor_data.py` will fail with
ModuleNotFoundError. Use `python`, not `py`.
"""

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Resolve dataset root relative to this script so the file is runnable
# from anywhere, not just C:\ForumProject.
SCRIPT_DIR = Path(__file__).resolve().parent
DATASET_DIR = SCRIPT_DIR / "Datasets" / "Parkinson's" / "Parkinson's Tremor Classification Dataset"

CLASS_ORDER = [
    "Postural tremor",
    "Fist",
    "Finger tapping",
    "Kinetic tremor",
    "Pronation and supination of the hand",
]


def pick_examples(train_csv: Path) -> dict[str, dict]:
    """Return one example row per class (the first occurrence of each)."""
    examples: dict[str, dict] = {}
    with train_csv.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            label = row["folder_path"]
            if label in CLASS_ORDER and label not in examples:
                examples[label] = row
    missing = [c for c in CLASS_ORDER if c not in examples]
    if missing:
        raise SystemExit(f"train.csv is missing labels: {missing}")
    return examples


def load_wrist(csv_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (time, wrist_xyz) where wrist_xyz has shape (N, 3)."""
    arr = np.genfromtxt(csv_path, delimiter=",", skip_header=1)
    # Columns: WRIST.x, WRIST.y, WRIST.z, ..., TIME
    wrist = arr[:, 0:3]
    time = arr[:, -1]
    # Normalize time to start at 0 so each panel shares the same x-axis range.
    time = time - time[0]
    return time, wrist


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=SCRIPT_DIR / "tremor_examples.png",
        help="Output PNG path (default: ./tremor_examples.png)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATASET_DIR / "data",
        help="Directory holding raw_data_*.csv files",
    )
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=DATASET_DIR / "train.csv",
        help="Path to train.csv with labels",
    )
    args = parser.parse_args()

    examples = pick_examples(args.train_csv)

    fig, axes = plt.subplots(
        nrows=len(CLASS_ORDER),
        ncols=1,
        figsize=(10, 10),
        sharex=True,
    )
    fig.suptitle("Parkinson Tremor Classification — one WRIST example per class", fontsize=13)

    axis_labels = ("WRIST.x", "WRIST.y", "WRIST.z")
    colors = ("#1f77b4", "#ff7f0e", "#2ca02c")

    for ax, label in zip(axes, CLASS_ORDER):
        row = examples[label]
        csv_path = args.data_dir / row["data_file_name"]
        time, wrist = load_wrist(csv_path)
        for i, (component, color) in enumerate(zip(axis_labels, colors)):
            ax.plot(time, wrist[:, i], color=color, linewidth=1.0, label=component)
        ax.set_ylabel(label, fontsize=10, rotation=0, ha="right", va="center", labelpad=8)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right", fontsize=8, ncol=3)

    axes[-1].set_xlabel("time (s)")

    fig.tight_layout(rect=(0, 0, 1, 0.97))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=120)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
