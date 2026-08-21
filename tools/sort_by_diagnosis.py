"""Sort raw tremor CSVs into folders named by doctor_diagnosis_0_5.

Reads C:/ForumProject/Datasets/Parkinson's/Parkinson's Tremor
Classification Dataset/train.csv and copies each listed
raw_data_*.csv into ./data_by_diagnosis/<N>/ where <N> is the
diagnosis value (0-5).

- Test.csv rows are NOT copied (they aren't in train.csv).
- Files on disk under data/ that are NOT listed in train.csv are
  skipped with a warning.
- Diagnosis values outside 0-5 are skipped with a warning (none exist
  in this dataset, but the guard is cheap).
- Duplicates in train.csv (same file listed twice with different
  diagnosis) are flagged and the first one wins.

Usage:
    python sort_by_diagnosis.py
    python sort_by_diagnosis.py --copy   # default is symlink, --copy
                                    # actually copies bytes instead
"""

import argparse
import csv
import shutil
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATASET_DIR = SCRIPT_DIR / "Datasets" / "Parkinson's" / "Parkinson's Tremor Classification Dataset"
DEFAULT_OUT = SCRIPT_DIR / "data_by_diagnosis"


def load_train(train_csv: Path) -> tuple[dict[str, str], list[tuple[str, str, list[str]]]]:
    """Return (file->diagnosis, duplicates).

    duplicates is a list of (filename, kept_diagnosis, [other_diagnoses]).
    """
    file_to_diag: dict[str, str] = {}
    diag_history: dict[str, list[str]] = defaultdict(list)
    with train_csv.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            file_to_diag.setdefault(row["data_file_name"], row["doctor_diagnosis_0_5"])
            diag_history[row["data_file_name"]].append(row["doctor_diagnosis_0_5"])
    duplicates = [
        (name, file_to_diag[name], others)
        for name, all_diags in diag_history.items()
        for others in [sorted(set(all_diags) - {file_to_diag[name]})]
        if others
    ]
    return file_to_diag, duplicates


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output root (default: ./data_by_diagnosis)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATASET_DIR / "data",
        help="Source directory holding raw_data_*.csv",
    )
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=DATASET_DIR / "train.csv",
        help="train.csv with labels",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Actually copy bytes (default: symlink — faster, no disk use)",
    )
    args = parser.parse_args()

    file_to_diag, duplicates = load_train(args.train_csv)
    print(f"train.csv: {len(file_to_diag)} unique files")

    if duplicates:
        print(f"  {len(duplicates)} files appear multiple times with different diagnoses "
              f"(keeping the first):")
        for name, kept, others in duplicates[:10]:
            print(f"    {name}: kept {kept}, also saw {others}")
        if len(duplicates) > 10:
            print(f"    ... and {len(duplicates) - 10} more")

    placed: Counter[str] = Counter()
    skipped_missing: list[str] = []
    skipped_bad_diag: list[tuple[str, str]] = []

    for filename, diag in file_to_diag.items():
        if not diag.isdigit() or not (0 <= int(diag) <= 5):
            skipped_bad_diag.append((filename, diag))
            continue
        src = args.data_dir / filename
        if not src.is_file():
            skipped_missing.append(filename)
            continue
        dst_dir = args.out / diag
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / filename
        if dst.exists() or dst.is_symlink():
            dst.unlink()
        if args.copy:
            shutil.copy2(src, dst)
        else:
            dst.symlink_to(src)
        placed[diag] += 1

    print()
    print("placed per diagnosis folder:")
    for diag in sorted(placed):
        print(f"  data_by_diagnosis/{diag}/  -> {placed[diag]} files")
    print(f"  total placed: {sum(placed.values())}")

    if skipped_missing:
        print(f"\nwarning: {len(skipped_missing)} listed files were not found on disk "
              f"(first 5):")
        for name in skipped_missing[:5]:
            print(f"    {name}")
    if skipped_bad_diag:
        print(f"\nwarning: {len(skipped_bad_diag)} rows had a bad diagnosis value:")
        for name, diag in skipped_bad_diag:
            print(f"    {name}: {diag!r}")

    print(f"\noutput: {args.out}")


if __name__ == "__main__":
    main()
