"""Build full assembly: place parts + route wires per connections.csv.

Run inside FreeCAD:
    freecadcmd build_assembly.py

Reads connections.csv, places components at predefined positions on the perfboard,
and draws wires as 3D splines between pin endpoints.
"""
import sys
from pathlib import Path

import FreeCAD as App
import Part
import Import
import Draft

sys.path.insert(0, str(Path(__file__).parent))
from _lib.parse_connections import load_connections

OUT_DIR = Path(__file__).parent / "assembly"
OUT_DIR.mkdir(exist_ok=True)

# Color hex per net type
COLORS_HEX = {
    "red": 0xFF0000,
    "black": 0x000000,
    "yellow": 0xFFFF00,
    "blue": 0x0000FF,
}

# Component placement on perfboard (x, y, z) in mm, rotation in degrees around Z
# Perfboard: origin at center, X = columns direction, Y = rows direction
# 30 cols x 15 rows, pitch 2.54mm => board 73.66 x 35.56 mm
# Layout: ESP32 left, GY-521 top-right, perfboard center, components around

COMPONENT_POSITIONS = {
    "ESP32-S3-Kaluga-1": {
        "pos": (-25, -8, 1.6),   # raised 1.6mm on standoffs
        "rot_z": 0,
        "step": "parts/_vendor/ESP32-S3-Kaluga-1.step",  # vendor STEP required
        "color": (0.0, 0.4, 0.7),
        "note": "Vendor STEP required",
    },
    "GY-521": {
        "pos": (22, 8, 1.6),
        "rot_z": 0,
        "step": "parts/_vendor/GY-521.step",
        "color": (0.1, 0.5, 0.1),
        "note": "Vendor STEP required",
    },
    "perfboard": {
        "pos": (0, 0, 0),
        "rot_z": 0,
        "step": "parts/perfboard.step",
        "color": (0.0, 0.4, 0.0),
    },
    "RES_220": {
        "pos": (-10, -10, 1.6),
        "rot_z": 30,
        "step": "parts/RES_220.step",
        "color": (0.85, 0.75, 0.55),
    },
    "RES_10K": {
        "pos": (-5, 10, 1.6),
        "rot_z": 60,
        "step": "parts/RES_10K.step",
        "color": (0.85, 0.75, 0.55),
    },
    "LED_5MM": {
        "pos": (-15, 12, 1.6),
        "rot_z": 90,
        "step": "parts/LED_5MM.step",
        "color": (1.0, 0.0, 0.0),
    },
    "2N7000": {
        "pos": (8, -5, 1.6),
        "rot_z": 0,
        "step": "parts/2N7000.step",
        "color": (0.1, 0.1, 0.1),
    },
    "1N4148": {
        "pos": (5, 5, 1.6),
        "rot_z": 45,
        "step": "parts/1N4148.step",
        "color": (0.95, 0.95, 0.95),
    },
    "LRA_COIN": {
        "pos": (15, -10, 1.6),
        "rot_z": 0,
        "step": "parts/LRA_COIN.step",
        "color": (0.7, 0.7, 0.72),
    },
}

# Pin anchor points per component (x, y, z) RELATIVE to component center, in mm
# Heights are typical lead/pad heights above the part body
PIN_ANCHORS = {
    "ESP32-S3-Kaluga-1": {
        "3V3": (15, -8, 5),
        "GND": (15, 8, 5),
        "GPIO2": (5, -8, 5),
        "GPIO21": (-15, -8, 5),
        "GPIO22": (-15, 0, 5),
        "GPIO25": (-15, 8, 5),
    },
    "GY-521": {
        "VCC": (-10, 8, 3),
        "GND": (-10, -8, 3),
        "SDA": (10, -8, 3),
        "SCL": (10, 8, 3),
    },
    "perfboard": {
        "RAIL_3V3": (0, -15, 1.6),
        "RAIL_GND": (0, 15, 1.6),
    },
    "RES_220": {
        "top": (3, 0, 0.3),
        "bottom": (-3, 0, 0.3),
    },
    "RES_10K": {
        "top": (3, 0, 0.3),
        "bottom": (-3, 0, 0.3),
        "mid": (3, -1.27, 0.3),
    },
    "LED_5MM": {
        "anode": (-1.27, 0, -7),
        "cathode": (1.27, 0, -7),
    },
    "2N7000": {
        "gate": (-1.27, 0, -7),
        "source": (0, 0, -7),
        "drain": (1.27, 0, -7),
    },
    "1N4148": {
        "anode": (-15, 0, 0),
        "cathode": (15, 0, 0),
    },
    "LRA_COIN": {
        "POS": (-3, 0, 4),
        "NEG": (3, 0, 4),
    },
}


def pin_world_pos(component, pin):
    """Compute world position of a pin given component placement + pin anchor."""
    if component not in COMPONENT_POSITIONS:
        raise ValueError(f"Unknown component: {component}")
    if component not in PIN_ANCHORS:
        raise ValueError(f"No pin anchors defined for {component}")
    if pin not in PIN_ANCHORS[component]:
        raise ValueError(f"Pin {pin} not defined for {component}")
    cp = COMPONENT_POSITIONS[component]
    anchor = PIN_ANCHORS[component][pin]
    return App.Vector(
        cp["pos"][0] + anchor[0],
        cp["pos"][1] + anchor[1],
        cp["pos"][2] + anchor[2],
    )


def place_part(doc, name):
    """Insert a STEP file into the assembly at the predefined position."""
    info = COMPONENT_POSITIONS[name]
    step_path = Path(__file__).parent / info["step"]
    if not step_path.exists():
        print(f"  [SKIP] {name}: STEP not found at {step_path}")
        return None
    shape = Part.Shape()
    shape.read(str(step_path))
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    obj.Placement = App.Placement(
        App.Vector(*info["pos"]),
        App.Rotation(App.Vector(0, 0, 1), info["rot_z"]),
    )
    if "color" in info:
        obj.ViewObject.ShapeColor = info["color"]
    return obj


def route_wire(doc, conn, idx):
    """Draw a 3D spline wire between two pin endpoints."""
    start = pin_world_pos(conn["from_component"], conn["from_pin"])
    end = pin_world_pos(conn["to_component"], conn["to_pin"])

    # Add a midpoint for natural sag (slightly below midpoint)
    mid = App.Vector(
        (start.x + end.x) / 2,
        (start.y + end.y) / 2,
        min(start.z, end.z) + 2,
    )

    # Build a wire by sweeping a small circle along a spline
    # Use Draft.makeWire (BSpline) and then Part.makePipe
    import Draft
    wire_feature = Draft.make_wire([start, mid, end], closed=False)
    wire_feature.Label = f"Wire_{idx}_{conn['net']}"
    wire_feature.ViewObject.LineColor = COLORS_HEX.get(conn["color"], 0x888888)
    wire_feature.ViewObject.LineWidth = 2

    # Make it visible as a thick wire via pipe sweep
    profile = doc.addObject("Part::Cylinder", f"WireProfile_{idx}")
    profile.Radius = 0.3
    profile.Height = 1
    profile.Placement = App.Placement(start, App.Rotation(App.Vector(1, 0, 0), 90))

    # Actually simpler: use Draft.makeWire and set DrawStyle to thick line
    # For 3D thickness, we'd need to sweep - skip for simplicity, lines work
    doc.removeObject(profile.Name)

    return wire_feature


def main():
    print("Loading connections.csv...")
    conns = load_connections()
    print(f"  {len(conns)} wires")

    doc = App.newDocument("tremor_assembly")

    # Place all parts
    print("\nPlacing parts...")
    for name in COMPONENT_POSITIONS:
        place_part(doc, name)

    # Route wires
    print("\nRouting wires...")
    for i, conn in enumerate(conns):
        try:
            route_wire(doc, conn, i)
            print(f"  [{conn['color']:6}] {conn['from_component']}.{conn['from_pin']} -> {conn['to_component']}.{conn['to_pin']}")
        except Exception as e:
            print(f"  [FAIL] {conn}: {e}")

    doc.recompute()

    out = OUT_DIR / "tremor_assembly.FCStd"
    doc.saveAs(str(out))
    print(f"\nSaved: {out}")

    # Also export as STEP for sharing
    Import.export([doc.Objects[-1]], str(OUT_DIR / "tremor_assembly.step"))
    print(f"STEP: {OUT_DIR / 'tremor_assembly.step'}")


if __name__ == "__main__":
    main()
