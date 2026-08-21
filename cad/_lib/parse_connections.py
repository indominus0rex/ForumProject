"""Parse connections.csv into structured dicts for FreeCAD scripts."""
import csv
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent / "connections.csv"


def load_connections():
    """Return list of dicts with keys: net, from_component, from_pin, to_component, to_pin, color, notes."""
    rows = []
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k.strip(): (v.strip() if v else "") for k, v in row.items()})
    return rows


def nets_by_color(connections):
    """Group connections by wire color."""
    out = {}
    for c in connections:
        out.setdefault(c["color"], []).append(c)
    return out


if __name__ == "__main__":
    cs = load_connections()
    print(f"Loaded {len(cs)} connections")
    by_color = nets_by_color(cs)
    for color, items in by_color.items():
        print(f"  {color}: {len(items)} wires")
