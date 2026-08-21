"""Plot WRIST x/y/z signals from a single specific CSV file.

Usage:
    python plot_tremor_data.py --file "C:/path/to/raw_data.csv"
    python plot_tremor_data.py --file "C:/path/to/raw_data.csv" --out "my_plot.png"
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load_wrist(csv_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (time, wrist_xyz) where wrist_xyz has shape (N, 3)."""
    arr = np.genfromtxt(csv_path, delimiter=",", skip_header=1)
    # Columns: WRIST.x, WRIST.y, WRIST.z, ..., TIME
    wrist = arr[:, 0:3]
    time = arr[:, -1]
    # Normalize time to start at 0
    time = time - time[0]
    return time, wrist


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-f", "--file",
        type=Path,
        required=True,
        help="Path to the specific raw_data_*.csv file you want to plot",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("single_tremor_plot.png"),
        help="Output PNG path (default: ./single_tremor_plot.png)",
    )
    args = parser.parse_args()

    if not args.file.exists():
        raise SystemExit(f"Error: Could not find file at {args.file}")

    # Load the data from the specific file
    time, wrist = load_wrist(args.file)

    # Set up a single plot panel
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.suptitle(f"Tremor Data: {args.file.name}", fontsize=13)

    axis_labels = ("WRIST.x", "WRIST.y", "WRIST.z")
    colors = ("#1f77b4", "#ff7f0e", "#2ca02c")

    # Plot X, Y, and Z lines
    for i, (component, color) in enumerate(zip(axis_labels, colors)):
        ax.plot(time, wrist[:, i], color=color, linewidth=1.0, label=component)
    
    ax.set_ylabel("Amplitude", fontsize=10)
    ax.set_xlabel("time (s)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=8, ncol=3)

    fig.tight_layout()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=120)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()