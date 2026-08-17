# sessions/

Raw CSV output from `collect_pilot.py`, one file per capture session.

## Filename convention

```
<label>_s<NN>.csv
```

e.g. `rest_s01.csv`, `kinetic_s03.csv`.

## Row format

```
<LABEL>,ax1,ay1,az1,ax2,ay2,az2,...,ax128,ay128,az128
```

- 1 label field + 128 windows × 3 axes = 385 floats per row
- One row = one 1.28s window at 100 Hz
- ~7 KB per row, ~160 KB per 30s session
- ~23 windows per session

## Capture workflow

1. Edit `LABEL` in `collect_pilot.py` to match task class
2. Flash to ESP32 via Thonny
3. Strap sensor to dorsum of most-affected hand
4. Subject assumes position, run script
5. Copy CSV output from Thonny shell into a new file in this folder
6. Repeat for all 4 classes × 5-10 sessions

## Target counts (per class)

| Class   | Target windows | Sessions × 30s |
|---------|----------------|----------------|
| rest    | ≥ 20           | 1+             |
| postural| ≥ 20           | 1+             |
| kinetic | ≥ 20           | 1+             |
| baseline| ≥ 20           | 1+             |

## Analysis

```bash
python analyze_pilot.py           # reads all CSVs in this folder
python analyze_pilot.py rest_s01.csv kinetic_s01.csv
```
