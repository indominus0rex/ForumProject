"""Generate a quick time-series plot for every raw CSV in the diagnosis folders.

Assumes you have already run sort_by_diagnosis.py and have a tree like:
    C:/ForumProject/
        data_by_diagnosis/
            0/
                raw_data_****.csv
                ...
            1/
                ...
            ...

For each CSV it plots WRIST.x, WRIST.y, WRIST.z vs TIME (normalized to start at 0)
and saves the figure as:
    data_by_diagnosis/<diag>/diagnosis<diag>_<file-stem>.png

Usage:
    python plot_all_by_diagnosis.py
    python plot_all_by_diagnosis.py --data-by-diag <path>   # override folder
    python plot_all_by_diagnosis.py --copy                # if you copied instead of symlinked
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_DIAG_ROOT = SCRIPT_DIR / "data_by_diagnosis"


def load_wrist(csv_path: Path):
    """Return (time_sec, wrist_xyz) where wrist_xyz is (N,3)."""
    data = np.genfromtxt(csv_path, delimiter=",", skip_header=1)
    # columns: WRIST.x, WRIST.y, WRIST.z, ..., TIME
    wrist = data[:, 0:3]
    time = data[:, -1]
    time = time - time[0]  # normalize to zero start
    return time, wrist


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-by-diag",
        type=Path,
        default=DEFAULT_DIAG_ROOT,
        help="Root folder containing diagnosis subfolders (default ./data_by_diagnosis)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=120,
        help="Output image DPI",
    )
    args = parser.parse_args()

    if not args.data_by_diag.is_dir():
        raise SystemExit(f"Diagnosis root not found: {args.data_by_diag}")

    diag_folders = sorted([p for p in args.data_by_diag.iterdir() if p.is_dir() and p.name.isdigit()],
                          key=lambda p: int(p.name))
    if not diag_folders:
        raise SystemExit(f"No diagnosis subfolders found under {args.data_by_diag}")

    total_plots = 0
    for diag_folder in diag_folders:
        diag = diag_folder.name
        csv_files = sorted(diag_folder.glob("raw_data_*.csv"))
        print(f"[{diag}] found {len(csv_files)} CSVs")
        for csv_path in csv_files:
            try:
                time, wrist = load_wrist(csv_path)
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(time, wrist[:, 0], label="WRIST.x", color="#1f77b4")
                ax.plot(time, wrist[:, 1], label="WRIST.y", color="#ff7f0e")
                ax.plot(time, wrist[:, 2], label="WRIST.z", color="#2ca02c")
                ax.set_xlabel("time (s)")
                ax.set_ylabel("position (a.u.)")
                ax.set_title(f"Diagnosis {diag} – {csv_path.name}")
                ax.grid(True, alpha=0.3)
                ax.legend(loc="upper right", fontsize=9)
                fig.tight_layout()
                out_name = f"diagnosis{diag}_{csv_path.stem}.png"
                out_path = diag_folder / out_name
                fig.savefig(out_path, dpi=args.dpi)
                plt.close(fig)
                total_plots += 1
            except Exception as e:
                print(f"  !! failed {csv_path.name}: {e}")

    print(f"\nFinished. Generated {total_plots} PNG files under {args.data_by_diag}")


if __name__ == "__main__":
    main()