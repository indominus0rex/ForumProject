# -*- coding: utf-8 -*-
"""
generate_test_data.py — Utility to generate synthetic tremor data for testing suppression analysis.

Creates CSV files with controllable tremor amplitude to validate suppression metrics.
"""

import numpy as np
import os
import argparse

FS = 100.0
SAMPLES = 128

def generate_tremor_window(tremor_amplitude=0.1, noise_level=0.02, tremor_freq=5.0, class_label="postural"):
    """Generate a 128x3 window with simulated tremor."""
    t = np.linspace(0, SAMPLES/FS, SAMPLES, endpoint=False)
    
    # Simulate tremor as sinusoidal oscillation in X-axis (most common)
    tremor_signal = tremor_amplitude * np.sin(2 * np.pi * tremor_freq * t)
    
    # Add noise
    noise_x = np.random.normal(0, noise_level, SAMPLES)
    noise_y = np.random.normal(0, noise_level, SAMPLES)
    noise_z = np.random.normal(0, noise_level, SAMPLES)
    
    # Combine signal and noise
    x = tremor_signal + noise_x
    y = noise_y  # Assume tremor primarily in X
    z = noise_z
    
    # Add small gravity offset to Z (simulating sensor orientation)
    z += 0.98
    
    # Stack into window format
    window = np.column_stack([x, y, z])  # [128, 3]
    return window, class_label

def save_to_csv(filename, window, label):
    """Save window to CSV row format."""
    flattened = window.flatten()
    with open(filename, 'w') as f:
        # Write header comment
        f.write("# LABEL,ax1,ay1,az1,...,ax128,ay128,az128\n")
        # Write data row
        row = [str(label)] + [str(val) for val in flattened]
        f.write(','.join(row) + '\n')

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic tremor test data")
    parser.add_argument("--pre-amplitude", type=float, default=0.15, 
                        help="Tremor amplitude for pre-intervention data (g)")
    parser.add_argument("--post-amplitude", type=float, default=0.05,
                        help="Tremor amplitude for post-intervention data (g)")
    parser.add_argument("--windows-per-file", type=int, default=10,
                        help="Number of windows per CSV file")
    parser.add_argument("--pre-files", type=int, default=3,
                        help="Number of pre-intervention files to generate")
    parser.add_argument("--post-files", type=int, default=3,
                        help="Number of post-intervention files to generate")
    parser.add_argument("--output-dir", default="sessions",
                        help="Directory to save generated CSV files")
    parser.add_argument("--class", dest="class_label", default="postural",
                        help="Class label for generated data")
    parser.add_argument("--noise", type=float, default=0.02,
                        help="Noise level (std dev of Gaussian noise)")
    parser.add_argument("--tremor-freq", type=float, default=5.0,
                        help="Tremor frequency in Hz")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Generating test data in {args.output_dir}/")
    print(f"Pre-amplitude: {args.pre_amplitude}g, Post-amplitude: {args.post_amplitude}g")
    print(f"Expected suppression: {(1-args.post_amplitude/args.pre_amplitude)*100:.1f}%")
    
    # Generate pre-intervention files
    for i in range(args.pre_files):
        filename = os.path.join(args.output_dir, f"pre_{args.class_label}_s{i+1:02d}.csv")
        with open(filename, 'w') as f:
            f.write("# LABEL,ax1,ay1,az1,...,ax128,ay128,az128\n")
            
        for w in range(args.windows_per_file):
            window, label = generate_tremor_window(
                tremor_amplitude=args.pre_amplitude,
                noise_level=args.noise,
                tremor_freq=args.tremor_freq,
                class_label=args.class_label
            )
            save_to_csv(filename, window, label)
            # Append to file (rewrite approach for simplicity)
            with open(filename, 'r') as f:
                content = f.read()
            lines = content.strip().split('\n')
            header = lines[0] if lines else "# LABEL,ax1,ay1,az1,...,ax128,ay128,az128"
            # Generate new row
            flattened = window.flatten()
            row = [str(label)] + [str(val) for val in flattened]
            new_line = ','.join(row)
            # Write back
            with open(filename, 'w') as f:
                f.write(header + '\n')
                for line in lines[1:]:  # existing data lines
                    if line.strip():
                        f.write(line + '\n')
                f.write(new_line + '\n')
    
    # Generate post-intervention files
    for i in range(args.post_files):
        filename = os.path.join(args.output_dir, f"post_{args.class_label}_s{i+1:02d}.csv")
        with open(filename, 'w') as f:
            f.write("# LABEL,ax1,ay1,az1,...,ax128,ay128,az128\n")
            
        for w in range(args.windows_per_file):
            window, label = generate_tremor_window(
                tremor_amplitude=args.post_amplitude,
                noise_level=args.noise,
                tremor_freq=args.tremor_freq,
                class_label=args.class_label
            )
            save_to_csv(filename, window, label)
            # Append to file
            with open(filename, 'r') as f:
                content = f.read()
            lines = content.strip().split('\n')
            header = lines[0] if lines else "# LABEL,ax1,ay1,az1,...,ax128,ay128,az128"
            # Generate new row
            flattened = window.flatten()
            row = [str(label)] + [str(val) for val in flattened]
            new_line = ','.join(row)
            # Write back
            with open(filename, 'w') as f:
                f.write(header + '\n')
                for line in lines[1:]:  # existing data lines
                    if line.strip():
                        f.write(line + '\n')
                f.write(new_line + '\n')
    
    print(f"Generated {args.pre_files} pre-files and {args.post_files} post-files")
    print(f"Each file contains {args.windows_per_file} windows")
    print("Test data generation complete!")

if __name__ == "__main__":
    main()