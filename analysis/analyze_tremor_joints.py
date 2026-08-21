"""Analyze tremor differences across diagnoses for each joint/sensor
to recommend optimal LRA placement on the hand.

Assumes data_by_diagnosis/<diag>/ contains raw_data_*.csv symlinks/copies
from sort_by_diagnosis.py.

For each CSV:
  - Load all columns (WRIST.x, WRIST.y, WRIST.z, THUMB_CMC.x, ... , TIME)
  - For each joint (group of .x,.y,.z columns) compute 3D magnitude over time
  - Detrend (subtract mean) and compute RMS (root-mean-square) as tremor magnitude proxy
  - Optionally compute power in 4-12 Hz band via FFT (requires sampling frequency)
    We'll estimate fs from median delta of TIME column.

Aggregate per diagnosis: mean and std of the metric across files.
Compute effect size (Cohen's d) between each pair of diagnoses or vs. diagnosis 0 (healthy?).
Report joint with highest average effect size across diagnoses.

Outputs:
  - Console summary
  - CSV file joint_effect_sizes.csv for further inspection
"""

import numpy as np
import pandas as pd
from pathlib import Path
import itertools
import csv

SCRIPT_DIR = Path(__file__).resolve().parent
DIAG_ROOT = SCRIPT_DIR / "data_by_diagnosis"

# List of joint base names as they appear in CSV columns (before .x,.y,.z)
# We'll infer from columns of a sample file.
def get_joint_bases(sample_path):
    df = pd.read_csv(sample_path, nrows=0)
    cols = df.columns.tolist()
    # Remove TIME
    cols = [c for c in cols if not c.upper() == 'TIME']
    # Split on '.' and take prefix before last dot
    bases = set()
    for c in cols:
        if '.' in c:
            prefix = c.rsplit('.', 1)[0]
            bases.add(prefix)
    return sorted(bases)

def compute_metrics_for_file(csv_path):
    """Return dict joint_base -> metric (RMS magnitude)."""
    # Load data
    data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    # Last column is TIME
    time = data[:, -1]
    # Estimate sampling frequency (Hz)
    if len(time) > 1:
        dt = np.diff(time)
        fs = 1.0 / np.median(dt) if np.median(dt) > 0 else 100.0
    else:
        fs = 100.0
    # Sensor data (exclude TIME)
    sensor = data[:, :-1]
    # Get column names from header
    with open(csv_path, 'r') as f:
        header = f.readline().strip().split(',')
    # Remove TIME header
    sensor_header = [h for h in header if h.upper() != 'TIME']
    # Map column to index
    col_idx = {name: i for i, name in enumerate(sensor_header)}
    
    # Determine joint bases from header
    joint_bases = set()
    for name in sensor_header:
        if '.' in name:
            joint_bases.add(name.rsplit('.', 1)[0])
    joint_bases = sorted(joint_bases)
    
    metrics = {}
    for base in joint_bases:
        # Extract x,y,z columns
        try:
            x = sensor[:, col_idx[f'{base}.x']]
            y = sensor[:, col_idx[f'{base}.y']]
            z = sensor[:, col_idx[f'{base}.z']]
        except KeyError:
            continue
        # Compute 3D magnitude
        mag = np.sqrt(x**2 + y**2 + z**2)
        # Detrend (remove mean)
        mag_detrended = mag - np.mean(mag)
        # RMS as tremor magnitude proxy
        rms = np.sqrt(np.mean(mag_detrended**2))
        metrics[base] = rms
    return metrics, fs

def main():
    # Find a sample file to get joint list
    sample_file = None
    for diag_dir in DIAG_ROOT.iterdir():
        if diag_dir.is_dir():
            for f in diag_dir.iterdir():
                if f.suffix == '.csv':
                    sample_file = f
                    break
            if sample_file:
                break
    if sample_file is None:
        print("No CSV files found in data_by_diagnosis")
        return
    joint_bases = get_joint_bases(sample_file)
    print(f"Detected {len(joint_bases)} joints: {joint_bases}")
    
    # Prepare storage: dict diagnosis -> dict joint -> list of metrics
    diag_metrics = {d: {j: [] for j in joint_bases} for d in map(str, range(0,6))}
    
    # Iterate over diagnosis folders
    for diag_dir in DIAG_ROOT.iterdir():
        if not diag_dir.is_dir():
            continue
        diag = diag_dir.name
        if not diag.isdigit():
            continue
        print(f"Processing diagnosis {diag}...")
        for csv_path in diag_dir.glob('raw_data_*.csv'):
            try:
                metrics, _ = compute_metrics_for_file(csv_path)
                for base in joint_bases:
                    if base in metrics:
                        diag_metrics[diag][base].append(metrics[base])
            except Exception as e:
                print(f"  Error processing {csv_path.name}: {e}")
    
    # Compute summary statistics
    summary_rows = []
    for diag in sorted(diag_metrics.keys(), key=int):
        for base in joint_bases:
            vals = diag_metrics[diag][base]
            if len(vals) == 0:
                continue
            arr = np.array(vals)
            mean = np.mean(arr)
            std = np.std(arr, ddof=1)
            summary_rows.append({
                'diagnosis': diag,
                'joint': base,
                'n': len(vals),
                'mean_rms': mean,
                'std_rms': std
            })
    summary_df = pd.DataFrame(summary_rows)
    
    # Compute effect size vs diagnosis 0 (assuming 0 is healthy/lowest tremor)
    ref_diag = '0'
    effect_rows = []
    for base in joint_bases:
        ref_vals = np.array(diag_metrics[ref_diag][base])
        if len(ref_vals) == 0:
            continue
        ref_mean = np.mean(ref_vals)
        ref_std = np.std(ref_vals, ddof=1)
        for diag in sorted(diag_metrics.keys(), key=int):
            if diag == ref_diag:
                continue
            vals = np.array(diag_metrics[diag][base])
            if len(vals) == 0:
                continue
            mean = np.mean(vals)
            std = np.std(vals, ddof=1)
            # Cohen's d
            pooled_std = np.sqrt((ref_std**2 + std**2) / 2.0)
            if pooled_std == 0:
                d = 0.0
            else:
                d = abs(mean - ref_mean) / pooled_std
            effect_rows.append({
                'joint': base,
                'diagnosis': diag,
                'effect_size_vs_0': d,
                'mean_diff': mean - ref_mean
            })
    effect_df = pd.DataFrame(effect_rows)
    
    # Average effect size across diagnoses (excluding 0) per joint
    avg_effect = effect_df.groupby('joint')['effect_size_vs_0'].mean().reset_index()
    avg_effect = avg_effect.rename(columns={'effect_size_vs_0': 'avg_effect_size_vs_0'})
    avg_effect = avg_effect.sort_values('avg_effect_size_vs_0', ascending=False)
    
    print("\n=== Average effect size (Cohen's d) vs diagnosis 0 ===")
    print(avg_effect.to_string(index=False))
    
    # Recommend joint with highest average effect size
    if not avg_effect.empty:
        best_joint = avg_effect.iloc[0]['joint']
        best_score = avg_effect.iloc[0]['avg_effect_size_vs_0']
        print(f"\nRecommended LRA placement joint: {best_joint} (avg effect size = {best_score:.3f})")
        print("Rationale: This joint shows the largest average tremor magnitude difference "
              "between diagnosis 0 and other diagnoses across the dataset.")
    else:
        print("\nCould not compute effect sizes.")
    
    # Save summaries
    out_dir = SCRIPT_DIR
    summary_df.to_csv(out_dir / 'joint_diagnosis_summary.csv', index=False)
    effect_df.to_csv(out_dir / 'joint_effect_sizes.csv', index=False)
    avg_effect.to_csv(out_dir / 'joint_avg_effect_vs_0.csv', index=False)
    print(f"\nSaved summaries to {out_dir}")

if __name__ == '__main__':
    main()